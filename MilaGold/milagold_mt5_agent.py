import MetaTrader5 as mt5
import time
import json
import os
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from config import LOGIN, SERVER, PASSWORD, MT5_PATH, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# --- AYARLAR ---
SYMBOL    = "GOLD"
LOT_SIZE  = 0.01
LOG_FILE         = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_mt5_log.txt"
SIGNAL_FILE      = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\signal.json"
MANUAL_SIGNAL_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\manuel_signal.json"
MANUAL_SIGNAL_NO = "MANUEL"  # signal_no bu degerse EMA/Streak filtreleri atlanir
PERFORMANCE_FILE      = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_trades.json"
CONTROL_FILE          = "C:\\MilaYatirim\\mila-yatirim-sistemi\\data\\milagold_control.json"
POSITIONS_STATUS_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\positions_status.json"
PRICE_OFFSET     = 0.0

SL_DISTANCE  = 5.0
TP1_DISTANCE = 3.0
TP2_DISTANCE = 5.0
TP3_DISTANCE = 8.0

ENTRY_CHANGE_THRESHOLD = 0.5

DEAL_FILLING_MODES = [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]

DRAWDOWN_LIMIT   = 0.15
MT5_CALL_TIMEOUT = 10   # saniye - MT5 API cagrilari icin max bekleme suresi

_mt5_pool = ThreadPoolExecutor(max_workers=1)


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_timing(tag, direction, entry, aciklama):
    """Gecikme olcumu icin milisaniye hassasiyetli log satiri (T1-T5 tanı amacli).
    Mevcut log() fonksiyonu saniye hassasiyetinde oldugu icin ayri tutuluyor."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"{timestamp} | {tag} | {direction}@{entry} | {aciklama}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        log(f"Telegram hatasi: {e}")


def mt5_call(fn, *args, timeout=MT5_CALL_TIMEOUT, **kwargs):
    """MT5 fonksiyonunu ayri thread'de calistir, timeout'ta RuntimeError firlatir.
    Timeout olusmasi durumunda executor yenilenir; arka planda MT5 yeniden baglanti denenir."""
    global _mt5_pool
    future = _mt5_pool.submit(fn, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeout:
        msg = f"MT5 TIMEOUT: {fn.__name__} {timeout}sn icinde yanit vermedi"
        log(msg)
        # Eski pool'u birak (takili thread daemon olarak calisir, process kapaninca olur)
        _mt5_pool.shutdown(wait=False)
        _mt5_pool = ThreadPoolExecutor(max_workers=1)
        # Yeniden baglanti denemesini arka planda yap - bloke etme
        def _reconnect():
            try:
                mt5.shutdown()
                time.sleep(2)
                if mt5.initialize():
                    log("MT5 yeniden baglandi.")
                else:
                    log(f"MT5 yeniden baglanti basarisiz: {mt5.last_error()}")
            except Exception as e:
                log(f"MT5 reconnect hatasi: {e}")
        threading.Thread(target=_reconnect, daemon=True).start()
        raise RuntimeError(msg)


def connect_mt5():
    if not mt5_call(mt5.initialize):
        log(f"MT5 baglanma hatasi: {mt5.last_error()}")
        return False
    info = mt5_call(mt5.account_info)
    log(f"MT5 baglandi. Bakiye: {info.balance if info else '?'} USD")
    return True


def get_current_price(direction):
    tick = mt5_call(mt5.symbol_info_tick, SYMBOL)
    if tick is None:
        raise RuntimeError("symbol_info_tick None dondu")
    return tick.bid if direction == "SELL" else tick.ask


def ema_filtresi_gecti_mi(direction):
    """M5 EMA20 filtresi: fiyat, sinyal yonunun tersi tarafta kalirsa sinyal atlanir.
    SELL: fiyat EMA20 uzerindeyse ATLANIR (yukari momentum).
    BUY:  fiyat EMA20 altindaysa ATLANIR (asagi momentum) — SELL ile simetrik.
    MT5'ten son 25 M5 mumu cekerek gercek EMA20 hesaplar (k=2/21).
    Hata durumunda True döner (filtre devre dışı kalır, islem açılır)."""
    try:
        rates = mt5_call(mt5.copy_rates_from_pos, SYMBOL, mt5.TIMEFRAME_M5, 0, 25)
        if rates is None or len(rates) < 20:
            log("EMA filtresi: M5 verisi alinamadi, filtre atlanıyor.")
            return True
        closes = [r[4] for r in rates]  # close fiyatlari
        # Gercek EMA20 hesapla (k = 2/(20+1))
        k = 2 / (20 + 1)
        ema20 = sum(closes[:5]) / 5  # ilk 5 bar ile baslatma (warmup)
        for c in closes[5:]:
            ema20 = c * k + ema20 * (1 - k)
        guncel_fiyat = closes[-1]
        if direction == "SELL":
            if guncel_fiyat > ema20:
                log(f"EMA filtresi: SELL ATLANDI — fiyat={guncel_fiyat:.2f} > EMA20={ema20:.2f} (yukari momentum)")
                return False
            else:
                log(f"EMA filtresi: SELL ONAYLANDI — fiyat={guncel_fiyat:.2f} <= EMA20={ema20:.2f}")
                return True
        else:
            if guncel_fiyat < ema20:
                log(f"EMA filtresi: BUY ATLANDI — fiyat={guncel_fiyat:.2f} < EMA20={ema20:.2f} (asagi momentum)")
                return False
            else:
                log(f"EMA filtresi: BUY ONAYLANDI — fiyat={guncel_fiyat:.2f} >= EMA20={ema20:.2f}")
                return True
    except Exception as e:
        log(f"EMA filtresi hatasi: {e} — filtre atlanıyor.")
        return True


def streak_filtresi_gecti_mi(direction):
    """EMA100 streak filtresi: fiyatin sinyal yonunde EMA100'e gore kaldigi
    ardisik M5 mum sayisi >= 13 olmali.
    SELL: fiyat EMA100 altinda. BUY: fiyat EMA100 ustunde — SELL ile simetrik.
    Hata durumunda True doner (filtre atlanir)."""
    try:
        rates = mt5_call(mt5.copy_rates_from_pos, SYMBOL, mt5.TIMEFRAME_M5, 0, 250)
        if rates is None or len(rates) < 110:
            log("Streak filtresi: M5 verisi yetersiz, filtre atlanıyor.")
            return True
        closes = [r[4] for r in rates]
        k = 2 / 101
        ema = sum(closes[:10]) / 10
        ema_list = [None] * 10
        for c in closes[10:]:
            ema = c * k + ema * (1 - k)
            ema_list.append(ema)
        streak = 0
        for i in range(len(closes) - 1, 9, -1):
            uygun = (closes[i] < ema_list[i]) if direction == "SELL" else (closes[i] > ema_list[i])
            if uygun:
                streak += 1
            else:
                break
        if streak < 13:
            log(f"Streak filtresi: {direction} ATLANDI — EMA100 streak={streak} < 13 (trend yeterince guclu degil)")
            return False
        else:
            log(f"Streak filtresi: {direction} ONAYLANDI — EMA100 streak={streak} >= 13")
            return True
    except Exception as e:
        log(f"Streak filtresi hatasi: {e} — filtre atlanıyor.")
        return True


def open_trade(direction, entry, sl, tp1, tp2, tp3):
    entry = round(entry + PRICE_OFFSET, 2)
    sl    = round(sl + PRICE_OFFSET, 2)
    tp3   = round(tp3 + PRICE_OFFSET, 2)
    mt5_call(mt5.symbol_select, SYMBOL, True)
    tick = mt5_call(mt5.symbol_info_tick, SYMBOL)
    if tick is None:
        log("open_trade: tick alinamadi")
        return None

    if direction == "SELL":
        current_price = tick.bid
        if current_price <= entry:
            order_type = mt5.ORDER_TYPE_SELL_LIMIT
            log(f"Emir turu: SELL_LIMIT (fiyat={current_price} <= entry={entry})")
        else:
            order_type = mt5.ORDER_TYPE_SELL_STOP
            log(f"Emir turu: SELL_STOP (fiyat={current_price} > entry={entry})")
    else:
        current_price = tick.ask
        if current_price >= entry:
            order_type = mt5.ORDER_TYPE_BUY_LIMIT
            log(f"Emir turu: BUY_LIMIT (fiyat={current_price} >= entry={entry})")
        else:
            order_type = mt5.ORDER_TYPE_BUY_STOP
            log(f"Emir turu: BUY_STOP (fiyat={current_price} < entry={entry})")

    # Ayni entry'de zaten bekleyen emir var mi kontrol et
    mevcut_emirler = mt5_call(mt5.orders_get, symbol=SYMBOL)
    if mevcut_emirler:
        for emir in mevcut_emirler:
            if emir.magic == 999999 and abs(emir.price_open - entry) < 0.1:
                log(f"open_trade: Ayni entry ({entry}) ile zaten bekleyen emir var "
                    f"(ticket={emir.ticket}), yeni emir acilmiyor.")
                return "SKIP"

    request = {
        "action":       mt5.TRADE_ACTION_PENDING,
        "symbol":       SYMBOL,
        "volume":       LOT_SIZE,
        "type":         order_type,
        "price":        entry,
        "sl":           sl,
        "magic":        999999,
        "comment":      "Mila",
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    log_timing("T4", direction, entry, "order_send cagrilacak")
    result = mt5.order_send(request)
    log_timing("T5", direction, entry,
               f"order_send sonucu: {'basarili' if result and result.retcode == mt5.TRADE_RETCODE_DONE else 'basarisiz'}")
    if result is None:
        last_err = mt5.last_error()
        log(f"open_trade: order_send None dondu | last_error={last_err}")
        return None
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"Islem acildi: {result.order} | {direction} @ {entry} | SL:{sl} | TP1:{tp1} TP2:{tp2} TP3:{tp3}")
        return result.order
    else:
        log(f"Islem acilamadi: {result.retcode} - {result.comment}")
        return None


def close_position_at_market(ticket, direction):
    """Acik pozisyonu piyasa fiyatindan kapat.
    Donus: "closed_by_us" | "already_closed" | "failed"
    """
    positions = mt5_call(mt5.positions_get, ticket=ticket)
    if not positions:
        log(f"Pozisyon zaten kapali (kapatma denenmeden once): ticket={ticket}")
        return "already_closed"

    position = positions[0]
    tick = mt5_call(mt5.symbol_info_tick, SYMBOL)
    if tick is None:
        log(f"close_position: tick alinamadi, ticket={ticket}")
        return "failed"

    if direction == "SELL":
        close_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        close_type = mt5.ORDER_TYPE_SELL
        price = tick.bid

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       SYMBOL,
        "volume":       position.volume,
        "type":         close_type,
        "position":     ticket,
        "price":        price,
        "deviation":    20,
        "magic":        999999,
        "comment":      "Mila-NewSignal",
    }

    result = None
    for filling_mode in DEAL_FILLING_MODES:
        request["type_filling"] = filling_mode
        result = mt5.order_send(request)
        if result is None:
            last_err = mt5.last_error()
            log(f"close_position: order_send None | last_error={last_err} | ticket={ticket}")
            check = mt5_call(mt5.positions_get, ticket=ticket)
            if check is not None and not check:
                log(f"Timeout sonrasi pozisyon zaten kapanmis: ticket={ticket}")
                return "already_closed"
            return "failed"
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"Pozisyon piyasadan kapatildi: ticket={ticket} @ {price} (filling={filling_mode})")
            return "closed_by_us"
        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            break

    check = mt5_call(mt5.positions_get, ticket=ticket)
    if check is not None and not check:
        log(f"Pozisyon kapatma denemesi reddedildi ama zaten kapanmis: ticket={ticket} "
            f"({result.retcode if result else '?'} - {result.comment if result else '?'})")
        return "already_closed"

    log(f"Pozisyon kapatilamadi: ticket={ticket} | "
        f"{result.retcode if result else '?'} - {result.comment if result else '?'}")
    return "failed"


def update_sl(ticket, new_sl):
    new_sl = round(new_sl, 2)
    positions = mt5_call(mt5.positions_get, ticket=ticket)
    if positions:
        position = positions[0]
        request = {
            "action":   mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl":       new_sl,
            "tp":       position.tp,
        }
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"SL guncellendi: ticket={ticket} yeni SL={new_sl}")
        else:
            code    = result.retcode if result else "timeout"
            comment = result.comment if result else ""
            log(f"SL guncellenemedi: {code} - {comment}")
    else:
        orders = mt5_call(mt5.orders_get, ticket=ticket)
        if orders:
            order = orders[0]
            request = {
                "action":       mt5.TRADE_ACTION_MODIFY,
                "order":        ticket,
                "price":        order.price_open,
                "sl":           new_sl,
                "tp":           order.tp,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"Bekleyen emir SL guncellendi: ticket={ticket} yeni SL={new_sl}")
            else:
                comment = result.comment if result else "timeout"
                log(f"Bekleyen emir SL guncellenemedi: {comment}")


def save_performance(record):
    try:
        if os.path.exists(PERFORMANCE_FILE):
            with open(PERFORMANCE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(record)
        with open(PERFORMANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log(f"Performans kaydedildi: {record['sonuc']} | {record['pip']} pip")
    except Exception as e:
        log(f"Performans kayit hatasi: {e}")


def write_positions_status(active_trades):
    try:
        data = {
            "acik_pozisyon_var": len(active_trades) > 0,
            "guncelleme": datetime.now().isoformat(timespec="seconds")
        }
        with open(POSITIONS_STATUS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log(f"positions_status.json yazma hatasi: {e}")


def get_deal_info(ticket):
    try:
        deals = mt5_call(mt5.history_deals_get, position=ticket)
        if deals and len(deals) >= 2:
            close_deal = deals[-1]
            return {
                "close_price": close_deal.price,
                "close_time":  datetime.utcfromtimestamp(close_deal.time).strftime("%Y-%m-%d %H:%M:%S"),
                "profit":      close_deal.profit,
            }
    except Exception:
        pass
    return None


def determine_result(active, close_price, forced_close=False):
    """Kapanis sonucunu sl_level'a gore belirle."""
    direction = active["direction"]
    entry     = active["entry"]
    tp3       = active["tp3"]
    sl_level  = active["sl_level"]

    if direction == "SELL":
        pip = round(entry - close_price, 2)
        ulasti_tp3 = close_price <= tp3
    else:
        pip = round(close_price - entry, 2)
        ulasti_tp3 = close_price >= tp3

    if ulasti_tp3:
        return "TP3", pip
    elif sl_level >= 1:
        return "Entry", pip
    elif forced_close:
        return "Exit", pip
    else:
        return "SL", pip


def build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3):
    return {
        "ticket":    ticket,
        "signal_no": signal_no,
        "direction": direction,
        "entry":     entry,
        "tp1":       tp1,
        "tp2":       tp2,
        "tp3":       tp3,
        "sl":        sl,
        "sl_level":  0,
        "tp1_hit":   False,
        "open_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def record_close(active, close_price, deal, forced_close=False):
    sonuc, pip = determine_result(active, close_price, forced_close=forced_close)
    record = {
        "signal_no":   active["signal_no"],
        "direction":   active["direction"],
        "entry":       active["entry"],
        "sl":          active["sl"],
        "tp1":         active["tp1"],
        "tp2":         active["tp2"],
        "tp3":         active["tp3"],
        "close_price": close_price,
        "open_time":   active["open_time"],
        "close_time":  deal["close_time"],
        "sonuc":       sonuc,
        "pip":         pip,
        "profit_usd":  deal["profit"],
    }
    save_performance(record)
    return sonuc, pip, deal["profit"]


def read_signal():
    try:
        if not os.path.exists(SIGNAL_FILE):
            return None
        with open(SIGNAL_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def read_manual_signal():
    try:
        if not os.path.exists(MANUAL_SIGNAL_FILE):
            return None
        with open(MANUAL_SIGNAL_FILE, "r") as f:
            return json.load(f)
    except:
        return None


def clear_manual_signal():
    try:
        if os.path.exists(MANUAL_SIGNAL_FILE):
            with open(MANUAL_SIGNAL_FILE, "r") as f:
                data = json.load(f)
            data["processed"] = True
            with open(MANUAL_SIGNAL_FILE, "w") as f:
                json.dump(data, f)
    except:
        pass


def clear_active_signal(signal_dict):
    """Hangi kaynaktan (manuel/OCR) gelen sinyal isleniyorsa o dosyayi
    processed=True yapar - islem yolunun tek clear_signal() cagrisi
    her iki kaynak icin de dogru dosyaya yazsin diye."""
    if signal_dict and signal_dict.get("signal_no") == MANUAL_SIGNAL_NO:
        clear_manual_signal()
    else:
        clear_signal()


def manuel_sinyali_tam_sinyale_cevir(manuel):
    """manuel_signal.json'daki minimal alanlari (direction, entry) OCR
    sinyaliyle ayni sekle cevirir - sl/tp1/tp2/tp3, mevcut SL/TP mesafe
    sabitleriyle (SL_DISTANCE vb.) hesaplanir, boylece ayni isleme
    fonksiyonuna OCR sinyaliyle birebir ayni sekilde girer. signal_no
    MANUAL_SIGNAL_NO olarak isaretlenir - EMA/Streak filtreleri bu
    isaretle atlanir (asagida)."""
    direction = manuel["direction"]
    entry = manuel["entry"]
    if direction == "SELL":
        sl  = round(entry + SL_DISTANCE,  2)
        tp1 = round(entry - TP1_DISTANCE, 2)
        tp2 = round(entry - TP2_DISTANCE, 2)
        tp3 = round(entry - TP3_DISTANCE, 2)
    else:
        sl  = round(entry - SL_DISTANCE,  2)
        tp1 = round(entry + TP1_DISTANCE, 2)
        tp2 = round(entry + TP2_DISTANCE, 2)
        tp3 = round(entry + TP3_DISTANCE, 2)
    return {
        "signal_no": MANUAL_SIGNAL_NO,
        "direction": direction,
        "entry":     entry,
        "sl":        sl,
        "tp1":       tp1,
        "tp2":       tp2,
        "tp3":       tp3,
        "status":    "RUNNING",
        "time":      manuel.get("time"),
        "processed": manuel.get("processed", False),
        "confirmed": True,
        "cancel":    manuel.get("cancel", False),
    }


def read_control():
    try:
        if not os.path.exists(CONTROL_FILE):
            return {"pause": False}
        with open(CONTROL_FILE, "r") as f:
            return json.load(f)
    except:
        return {"pause": False}


def clear_signal():
    try:
        if os.path.exists(SIGNAL_FILE):
            with open(SIGNAL_FILE, "r") as f:
                data = json.load(f)
            data["processed"] = True
            with open(SIGNAL_FILE, "w") as f:
                json.dump(data, f)
    except:
        pass


def guess_sl_level(position, tp1_dist=TP1_DISTANCE, tp2_dist=TP2_DISTANCE, sl_dist=SL_DISTANCE):
    entry = position.price_open
    sl    = position.sl

    if position.type == mt5.ORDER_TYPE_SELL:
        entry_sl = entry
    else:
        entry_sl = entry

    dist_entry = abs(sl - entry_sl)
    if dist_entry < 0.6:
        return 1
    return 0


def adopt_orphans():
    adopted = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    positions = mt5_call(mt5.positions_get, symbol=SYMBOL)
    if positions:
        for pos in positions:
            if pos.magic != 999999:
                continue
            direction = "SELL" if pos.type == mt5.ORDER_TYPE_SELL else "BUY"
            entry     = pos.price_open
            sl_level  = guess_sl_level(pos)

            if direction == "SELL":
                sl  = round(entry + SL_DISTANCE,  2)
                tp1 = round(entry - TP1_DISTANCE, 2)
                tp2 = round(entry - TP2_DISTANCE, 2)
                tp3 = round(entry - TP3_DISTANCE, 2)
            else:
                sl  = round(entry - SL_DISTANCE,  2)
                tp1 = round(entry + TP1_DISTANCE, 2)
                tp2 = round(entry + TP2_DISTANCE, 2)
                tp3 = round(entry + TP3_DISTANCE, 2)

            rec = build_active(pos.ticket, "orphan", direction, entry, sl, tp1, tp2, tp3)
            rec["sl_level"]  = sl_level
            rec["open_time"] = now_str
            adopted.append(rec)
            log(f"Orphan pozisyon alindi: ticket={pos.ticket} {direction} @ {entry} sl_level={sl_level}")

    orders = mt5_call(mt5.orders_get, symbol=SYMBOL)
    if orders:
        for ord_ in orders:
            if ord_.magic != 999999:
                continue
            direction = "SELL" if ord_.type in (
                mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_SELL_LIMIT) else "BUY"
            entry = ord_.price_open

            if direction == "SELL":
                sl  = round(entry + SL_DISTANCE,  2)
                tp1 = round(entry - TP1_DISTANCE, 2)
                tp2 = round(entry - TP2_DISTANCE, 2)
                tp3 = round(entry - TP3_DISTANCE, 2)
            else:
                sl  = round(entry - SL_DISTANCE,  2)
                tp1 = round(entry + TP1_DISTANCE, 2)
                tp2 = round(entry + TP2_DISTANCE, 2)
                tp3 = round(entry + TP3_DISTANCE, 2)

            rec = build_active(ord_.ticket, "orphan", direction, entry, sl, tp1, tp2, tp3)
            rec["open_time"] = now_str
            adopted.append(rec)
            log(f"Orphan bekleyen emir alindi: ticket={ord_.ticket} {direction} @ {entry}")

    if adopted:
        telegram(f"[MilaGold] 🔄 {len(adopted)} orphan pozisyon/emir devralindi. Takip basladi.")
    return adopted


def main():
    log("MilaGold MT5 Agent basliyor...")
    if not connect_mt5():
        return

    active_trades = adopt_orphans()

    try:
        if os.path.exists(SIGNAL_FILE):
            with open(SIGNAL_FILE, "r") as f:
                startup_signal = json.load(f)
            if not startup_signal.get("confirmed", True) or startup_signal.get("cancel", False):
                startup_signal["processed"] = True
                with open(SIGNAL_FILE, "w") as f:
                    json.dump(startup_signal, f, indent=2)
                log("Baslatma: yarim/iptal sinyal temizlendi (processed=True yapildi).")
    except Exception as e:
        log(f"Baslatma sinyal temizleme hatasi: {e}")

    info = mt5_call(mt5.account_info)
    baslangic_bakiye = info.balance if info else 0
    drawdown_durdur  = False
    log(f"Baslangic bakiyesi: {baslangic_bakiye} USD")
    log(f"Hazir. {len(active_trades)} aktif islem devralindi. signal.json bekleniyor...")
    telegram(f"[MilaGold] ✅ MilaGold MT5 Agent basladi. Bakiye: {baslangic_bakiye} USD | "
             f"Devralınan: {len(active_trades)} islem")

    last_heartbeat = time.time()
    HEARTBEAT_INTERVAL = 30  # saniye
    last_skipped_signal = None  # SL/Entry kapanisinda yeniden denenecek sinyal
    sistem_duraklatildi_prev = False
    last_t3_key = None  # T3 dedup: (signal_no, time, direction, entry) - ayni sinyalin retry'inde tekrar loglanmasin

    while True:
        try:
            # Heartbeat - watchdog icin periyodik log
            now_ts = time.time()
            if now_ts - last_heartbeat >= HEARTBEAT_INTERVAL:
                hb_info = mt5_call(mt5.account_info)
                bakiye_str = f"{hb_info.balance:.2f}" if hb_info else "?"
                log(f"Heartbeat: {len(active_trades)} aktif islem | Bakiye: {bakiye_str} USD")
                last_heartbeat = now_ts

            ocr_signal = read_signal()
            manuel_ham = read_manual_signal()
            manuel_bekliyor = bool(manuel_ham) and not manuel_ham.get("processed") \
                and not manuel_ham.get("cancel")
            if manuel_bekliyor:
                signal = manuel_sinyali_tam_sinyale_cevir(manuel_ham)
            else:
                signal = ocr_signal

            # Gunluk sifirlama
            simdi = datetime.now()
            if simdi.hour == 0 and simdi.minute == 0 and simdi.second < 5:
                reset_info = mt5_call(mt5.account_info)
                yeni_bakiye = reset_info.balance if reset_info else baslangic_bakiye
                if yeni_bakiye != baslangic_bakiye:
                    log(f"Gunluk sifirlama: yeni baslangic bakiyesi = {yeni_bakiye} USD")
                    telegram(f"[MilaGold] 🔄 Yeni gun. Baslangic bakiyesi: {yeni_bakiye} USD")
                    baslangic_bakiye = yeni_bakiye
                    drawdown_durdur = False

            # Drawdown kontrolu
            dd_info = mt5_call(mt5.account_info)
            if dd_info:
                guncel_bakiye = dd_info.balance
                dusus = (baslangic_bakiye - guncel_bakiye) / baslangic_bakiye if baslangic_bakiye else 0
                if dusus >= DRAWDOWN_LIMIT and not drawdown_durdur:
                    mesaj = (f"[MilaGold] ⚠️ EMNiYET STOPU! Kasa %{dusus*100:.1f} dusus. "
                             f"Islem alma durduruldu. Bakiye: {guncel_bakiye} USD")
                    log(mesaj)
                    telegram(mesaj)
                    drawdown_durdur = True

            if drawdown_durdur:
                time.sleep(5)
                continue

            # --- KONTROL DOSYASI ---
            control = read_control()
            sistem_duraklatildi = control.get("pause", False)
            if sistem_duraklatildi != sistem_duraklatildi_prev:
                if sistem_duraklatildi:
                    log("Sistem duraklatildi — yeni emir alinmiyor")
                else:
                    log("Sistem aktif — yeni emir alinmaya devam ediyor")
                sistem_duraklatildi_prev = sistem_duraklatildi

            # --- PIYASA KAPANIS KURALLARI ---
            simdi_k = datetime.now()
            kapanis_saati = simdi_k.hour == 23 and simdi_k.minute >= 45

            # 23:55'te acik pozisyon varsa kapat, bekleyen (henuz dolmamis) emir
            # varsa iptal et (gap riski - 17/07/2026 oncesi sadece acik pozisyonlar
            # kapsaniyordu, bekleyen sell-stop/buy-stop emirleri gece boyunca acik
            # kalip gapten etkilenebiliyordu)
            if simdi_k.hour == 23 and simdi_k.minute >= 55:
                if active_trades:
                    log("23:55 gap koruma: tum acik pozisyonlar ve bekleyen emirler kapatiliyor.")
                    telegram("[MilaGold] ⚠️ 23:55 gap koruma: pozisyonlar/bekleyen emirler kapatiliyor.")
                    for trade in list(active_trades):
                        ticket = trade["ticket"]
                        if mt5_call(mt5.positions_get, ticket=ticket):
                            close_position_at_market(ticket, trade["direction"])
                        elif mt5_call(mt5.orders_get, ticket=ticket):
                            cancel_result = mt5.order_send({
                                "action": mt5.TRADE_ACTION_REMOVE,
                                "order": ticket,
                            })
                            if cancel_result and cancel_result.retcode == mt5.TRADE_RETCODE_DONE:
                                log(f"23:55 gap koruma: bekleyen emir iptal edildi: ticket={ticket}")
                            else:
                                code = cancel_result.retcode if cancel_result else "timeout"
                                log(f"23:55 gap koruma: bekleyen emir iptal edilemedi: ticket={ticket} | {code}")
                    active_trades = []
                time.sleep(5)
                continue

            # --- CANCEL KONTROLU ---
            if signal and signal.get("cancel") and not signal.get("processed"):
                log("signal.json cancel=True alindi. Bekleyen emir iptal ediliyor...")
                bekleyenler = [t for t in active_trades
                               if mt5_call(mt5.orders_get, ticket=t["ticket"])]
                for bekleyen in bekleyenler:
                    cancel_result = mt5.order_send({
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order":  bekleyen["ticket"],
                    })
                    if cancel_result and cancel_result.retcode == mt5.TRADE_RETCODE_DONE:
                        log(f"Dogrulama basarisiz - emir iptal edildi: ticket={bekleyen['ticket']}")
                        active_trades = [t for t in active_trades
                                         if t["ticket"] != bekleyen["ticket"]]
                    else:
                        code    = cancel_result.retcode if cancel_result else "timeout"
                        comment = cancel_result.comment if cancel_result else ""
                        log(f"Emir iptal edilemedi (zaten dolmus olabilir): "
                            f"ticket={bekleyen['ticket']} | {code} - {comment}")

            # --- YENI SiNYAL iSLEME ---
            # 23:45'ten sonra yeni islem alma
            if kapanis_saati and signal and not signal.get("processed"):
                log("23:45 sonrasi yeni islem alinmiyor, sinyal atlandi.")
                clear_active_signal(signal)
                time.sleep(5)
                continue

            if not sistem_duraklatildi and signal and not signal.get("processed") \
                    and signal.get("status") in ("RUNNING", "WAITING") \
                    and not signal.get("cancel", False):
                direction = signal["direction"]
                entry     = signal["entry"]
                sl        = signal["sl"]
                tp1       = signal["tp1"]
                tp2       = signal["tp2"]
                tp3       = signal["tp3"]
                signal_no = signal.get("signal_no", "?")

                t3_key = (signal_no, signal.get("time"), direction, entry)
                if t3_key != last_t3_key:
                    log_timing("T3", direction, entry, "signal.json okundu (MT5 agent)")
                    last_t3_key = t3_key

                ana = next((t for t in active_trades
                            if mt5_call(mt5.positions_get, ticket=t["ticket"])), None)

                if ana is None:
                    bekleyenler = [t for t in active_trades
                                   if mt5_call(mt5.orders_get, ticket=t["ticket"])]

                    manuel_bekleyen_var = any(
                        b.get("signal_no") == MANUAL_SIGNAL_NO for b in bekleyenler)
                    if manuel_bekleyen_var and signal_no != MANUAL_SIGNAL_NO:
                        log(f"OCR sinyali atlandi (manuel emir aktif): #{signal_no} {direction} @ {entry}")
                        telegram(f"[MilaGold] Sinyal atlandi — {direction} @ {entry} (manuel emir aktif)")
                        clear_active_signal(signal)
                        continue

                    for bekleyen in bekleyenler:
                        log(f"Yeni sinyal geldi, bekleyen emir iptal ediliyor: "
                            f"ticket={bekleyen['ticket']} ({bekleyen['direction']} @ {bekleyen['entry']})")
                        cancel_result = mt5.order_send({
                            "action": mt5.TRADE_ACTION_REMOVE,
                            "order":  bekleyen["ticket"],
                        })
                        if cancel_result and cancel_result.retcode == mt5.TRADE_RETCODE_DONE:
                            log(f"Bekleyen emir iptal edildi: ticket={bekleyen['ticket']}")
                            active_trades = [t for t in active_trades
                                             if t["ticket"] != bekleyen["ticket"]]
                        else:
                            code = cancel_result.retcode if cancel_result else "timeout"
                            log(f"Emir iptal edilemedi: ticket={bekleyen['ticket']} | {code}")

                    log(f"Yeni sinyal alindi: #{signal_no} {direction} @ {entry}")
                    if signal_no == MANUAL_SIGNAL_NO:
                        log(f"Manuel emir: EMA/Streak filtreleri atlaniyor — {direction} @ {entry}")
                    else:
                        if not ema_filtresi_gecti_mi(direction):
                            log(f"EMA filtresi: sinyal atlandi #{signal_no} {direction} @ {entry}")
                            telegram(f"[MilaGold] EMA filtresi: sinyal atlandi — {direction} @ {entry} (yukari momentum)")
                            clear_active_signal(signal)
                            continue
                        if not streak_filtresi_gecti_mi(direction):
                            log(f"Streak filtresi: sinyal atlandi #{signal_no} {direction} @ {entry}")
                            telegram(f"[MilaGold] Streak filtresi: sinyal atlandi — {direction} @ {entry} (EMA100 streak yetersiz)")
                            clear_active_signal(signal)
                            continue
                    ticket = open_trade(direction, entry, sl, tp1, tp2, tp3)
                    if isinstance(ticket, int):
                        active_trades.append(
                            build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3))
                        clear_active_signal(signal)
                    elif ticket == "SKIP":
                        clear_active_signal(signal)
                    else:  # None - MT5 yanit vermedi
                        alarm = (f"[MilaGold] UYARI: Emir gonderilemedi (order_send None): "
                                 f"{direction} @ {entry}. Sonraki dongude tekrar denenecek.")
                        log(alarm)
                        telegram(alarm)

                else:
                    yon_degisti   = (direction != ana["direction"])
                    fark          = entry - ana["entry"]

                    if ana["direction"] == "SELL":
                        yeni_daha_iyi = fark > ENTRY_CHANGE_THRESHOLD
                    else:
                        yeni_daha_iyi = fark < -ENTRY_CHANGE_THRESHOLD

                    entry_degisti = abs(fark) > ENTRY_CHANGE_THRESHOLD

                    if not entry_degisti and not yon_degisti:
                        log(f"Ayni sinyal tekrar geldi, islem yapilmiyor: #{signal_no}")
                        clear_active_signal(signal)

                    elif yon_degisti or yeni_daha_iyi:
                        neden = "yon degisti" if yon_degisti else "yeni entry daha iyi"
                        log(f"Yeni sinyal ({neden}): "
                            f"{ana['direction']}@{ana['entry']} -> {direction}@{entry}. "
                            f"Kapatiliyor: ticket={ana['ticket']}")

                        close_status = close_position_at_market(ana["ticket"], ana["direction"])

                        if close_status == "failed":
                            log("Pozisyon kapatilamadi - sonraki dongude tekrar denenecek.")
                        else:
                            forced = (close_status == "closed_by_us")
                            deal = None
                            for _ in range(5):
                                deal = get_deal_info(ana["ticket"])
                                if deal:
                                    break
                                time.sleep(0.3)
                            if deal:
                                sonuc, pip, profit = record_close(
                                    ana, deal["close_price"], deal, forced_close=forced)
                                telegram(f"[MilaGold] 🔄 Eski pozisyon kapandi: "
                                         f"{sonuc} {pip:+.2f} pip ({profit:+.2f} USD) | "
                                         f"Yeni: #{signal_no} {direction} @ {entry}")
                            else:
                                log(f"Kapanis bilgisi alinamadi: ticket={ana['ticket']}")

                            active_trades = [t for t in active_trades
                                             if t["ticket"] != ana["ticket"]]
                            ticket = open_trade(direction, entry, sl, tp1, tp2, tp3)
                            if isinstance(ticket, int):
                                active_trades.append(
                                    build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3))
                                clear_active_signal(signal)
                            elif ticket == "SKIP":
                                clear_active_signal(signal)
                            else:  # None - MT5 yanit vermedi
                                alarm = (f"[MilaGold] UYARI: Eski pozisyon kapandi ama yeni emir gonderilemedi "
                                         f"(order_send None): {direction} @ {entry}. Sonraki dongude tekrar denenecek.")
                                log(alarm)
                                telegram(alarm)

                    else:
                        if ana["sl_level"] == 0:
                            log(f"Yeni sinyal daha kotu entry, sl_level=0. "
                                f"Eski pozisyon tutuldu, sinyal hafizaya alindi: #{signal_no}@{entry}")
                            telegram(f"[MilaGold] ℹ️ Sinyal hafizaya alindi (kotu entry, sl_level=0): "
                                     f"{ana['direction']}@{ana['entry']} devam | Atlanan: #{signal_no}@{entry}")
                            last_skipped_signal = {
                                "direction": direction,
                                "entry":     entry,
                                "sl":        sl,
                                "tp1":       tp1,
                                "tp2":       tp2,
                                "tp3":       tp3,
                                "signal_no": signal_no,
                            }
                            clear_active_signal(signal)
                        else:
                            if len(active_trades) >= 2:
                                log(f"Yeni sinyal daha kotu entry, sl_level={ana['sl_level']}. "
                                    f"Ama zaten 2 pozisyon var, sinyal atildi: #{signal_no}")
                                telegram(f"[MilaGold] Sinyal atildi (max 2 pozisyon): #{signal_no}@{entry}")
                                clear_active_signal(signal)
                            else:
                                log(f"Yeni sinyal daha kotu entry, sl_level={ana['sl_level']}. "
                                    f"2. pozisyon aciliyor: #{signal_no} @ {entry}")
                                ticket2 = open_trade(direction, entry, sl, tp1, tp2, tp3)
                                if isinstance(ticket2, int):
                                    active_trades.append(
                                        build_active(ticket2, signal_no, direction, entry, sl, tp1, tp2, tp3))
                                    telegram(f"[MilaGold] 2. pozisyon acildi: "
                                             f"#{signal_no} {direction} @ {entry} | ticket={ticket2}")
                                    clear_active_signal(signal)
                                elif ticket2 == "SKIP":
                                    clear_active_signal(signal)
                                else:  # None - MT5 yanit vermedi
                                    alarm = (f"[MilaGold] UYARI: 2. emir gonderilemedi "
                                             f"(order_send None): {direction} @ {entry}. Sonraki dongude tekrar denenecek.")
                                    log(alarm)
                                    telegram(alarm)
                                    # clear_signal cagirilmiyor - sonraki dongude tekrar denenir

            # --- AKTiF iSLEMLERi TAKiP ET ---
            kapanan_tickets = []
            for trade in active_trades:
                ticket    = trade["ticket"]
                direction = trade["direction"]
                tp1       = trade["tp1"]
                tp2       = trade["tp2"]
                current   = get_current_price(direction)

                positions = mt5_call(mt5.positions_get, ticket=ticket)
                orders    = mt5_call(mt5.orders_get, ticket=ticket)

                if not positions and not orders:
                    log(f"Islem kapandi: ticket={ticket}")
                    deal = get_deal_info(ticket)
                    sonuc = None
                    if deal:
                        sonuc, pip, profit = record_close(trade, deal["close_price"], deal, forced_close=False)
                    kapanan_tickets.append(ticket)

                    # SL veya Entry kapanisinda last_skipped_signal varsa yeniden dene
                    if sonuc in ("SL", "Entry") and last_skipped_signal:
                        sk = last_skipped_signal
                        current_price = get_current_price(sk["direction"])
                        # Fiyat hala uygun mu kontrol et
                        price_ok = (sk["direction"] == "SELL" and current_price > sk["entry"]) or \
                                   (sk["direction"] == "BUY"  and current_price < sk["entry"])
                        if price_ok:
                            log(f"Kapanis sonrasi hafizadaki sinyal deneniyor: "
                                f"#{sk['signal_no']} {sk['direction']} @ {sk['entry']}")
                            if sk.get("signal_no") == MANUAL_SIGNAL_NO:
                                log(f"Manuel emir (hafizadaki): EMA/Streak filtreleri atlaniyor — {sk['direction']} @ {sk['entry']}")
                            else:
                                if not ema_filtresi_gecti_mi(sk["direction"]):
                                    log(f"EMA filtresi: hafizadaki sinyal da atlandi — {sk['direction']} @ {sk['entry']}")
                                    telegram(f"[MilaGold] EMA filtresi: hafizadaki sinyal atlandi — {sk['direction']} @ {sk['entry']}")
                                    last_skipped_signal = None
                                    continue
                                if not streak_filtresi_gecti_mi(sk["direction"]):
                                    log(f"Streak filtresi: hafizadaki sinyal da atlandi — {sk['direction']} @ {sk['entry']}")
                                    telegram(f"[MilaGold] Streak filtresi: hafizadaki sinyal atlandi — {sk['direction']} @ {sk['entry']}")
                                    last_skipped_signal = None
                                    continue
                            ticket2 = open_trade(sk["direction"], sk["entry"],
                                                 sk["sl"], sk["tp1"], sk["tp2"], sk["tp3"])
                            if isinstance(ticket2, int):
                                active_trades.append(
                                    build_active(ticket2, sk["signal_no"], sk["direction"],
                                                 sk["entry"], sk["sl"], sk["tp1"], sk["tp2"], sk["tp3"]))
                                telegram(f"[MilaGold] ♻️ Hafizadaki sinyal girildi: "
                                         f"#{sk['signal_no']} {sk['direction']} @ {sk['entry']} | ticket={ticket2}")
                                log(f"Hafizadaki sinyal girildi: ticket={ticket2}")
                            elif ticket2 == "SKIP":
                                log("Hafizadaki sinyal: fiyat artik uygun degil (SKIP).")
                            else:
                                log("Hafizadaki sinyal: order_send basarisiz.")
                        else:
                            log(f"Hafizadaki sinyal artik gecersiz (fiyat uzaklasti): "
                                f"{sk['direction']}@{sk['entry']} | guncel={current_price:.2f}")
                        last_skipped_signal = None

                    elif sonuc == "TP3" and last_skipped_signal:
                        log(f"TP3 kapanisi, hafizadaki sinyal temizlendi: "
                            f"#{last_skipped_signal['signal_no']}")
                        last_skipped_signal = None

                    continue

                if not positions:
                    continue

                if not trade["tp1_hit"]:
                    if (direction == "SELL" and current <= tp1) or \
                       (direction == "BUY"  and current >= tp1):
                        log(f"TP1 gecildi: ticket={ticket} fiyat={current} TP1={tp1} -> SL -2 ye tasiniyor")
                        yeni_sl = round(trade["entry"] + 2.0, 2) if direction == "SELL" else round(trade["entry"] - 2.0, 2)
                        update_sl(ticket, yeni_sl)
                        trade["tp1_hit"] = True

                if trade["sl_level"] < 1:
                    if (direction == "SELL" and current <= tp2) or \
                       (direction == "BUY"  and current >= tp2):
                        log(f"TP2 gecildi: ticket={ticket} fiyat={current} TP2={tp2} -> SL girise tasiniyor, trailing basliyor")
                        update_sl(ticket, trade["entry"])
                        trade["sl_level"] = 1

                # --- TRAILING STOP (TP2 sonrasi) ---
                if trade["sl_level"] >= 1:
                    entry = trade["entry"]
                    # Kar mesafesini hesapla (entry'den itibaren)
                    if direction == "SELL":
                        kar = round(entry - current, 2)
                    else:
                        kar = round(current - entry, 2)

                    # Tablodan trailing mesafesi belirle
                    if kar >= 9.0:
                        trailing = 2.0
                    elif kar >= 8.0:   # TP3 seviyesi — trailing devam eder, kapatmaz
                        trailing = 2.0
                    elif kar >= 7.0:
                        trailing = 3.0
                    elif kar >= 6.0:
                        trailing = 4.0
                    else:              # 5-6 arasi (TP2 sonrasi)
                        trailing = 5.0

                    # Yeni SL hesapla
                    if direction == "SELL":
                        yeni_sl = round(current + trailing, 2)
                    else:
                        yeni_sl = round(current - trailing, 2)

                    # Mevcut SL'i al
                    pos_list = mt5_call(mt5.positions_get, ticket=ticket)
                    if pos_list:
                        mevcut_sl = pos_list[0].sl
                        # Sadece SL lehte ilerliyorsa taşı (SELL: yeni_sl < mevcut_sl, BUY: yeni_sl > mevcut_sl)
                        if direction == "SELL" and yeni_sl < mevcut_sl - 0.05:
                            log(f"Trailing SL: ticket={ticket} kar={kar:.2f} trailing={trailing} | {mevcut_sl} -> {yeni_sl}")
                            update_sl(ticket, yeni_sl)
                        elif direction == "BUY" and yeni_sl > mevcut_sl + 0.05:
                            log(f"Trailing SL: ticket={ticket} kar={kar:.2f} trailing={trailing} | {mevcut_sl} -> {yeni_sl}")
                            update_sl(ticket, yeni_sl)

            active_trades = [t for t in active_trades if t["ticket"] not in kapanan_tickets]

            write_positions_status(active_trades)
            time.sleep(1)

        except KeyboardInterrupt:
            log("Agent durduruldu.")
            break
        except Exception as e:
            log(f"Hata: {e}")
            time.sleep(5)

    mt5.shutdown()


if __name__ == "__main__":
    main()
