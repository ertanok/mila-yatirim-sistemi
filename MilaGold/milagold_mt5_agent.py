import MetaTrader5 as mt5
import time
import json
import os
import requests
from datetime import datetime
from config import LOGIN, SERVER, PASSWORD, MT5_PATH, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# --- AYARLAR ---
SYMBOL    = "GOLD"
LOT_SIZE  = 0.01
LOG_FILE         = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_mt5_log.txt"
SIGNAL_FILE      = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\signal.json"
PERFORMANCE_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_trades.json"
PRICE_OFFSET     = 0.0

# SL/TP mesafeleri (sabit) - orphan adoption icin de kullanilir
SL_DISTANCE  = 5.0
TP1_DISTANCE = 3.0
TP2_DISTANCE = 5.0
TP3_DISTANCE = 8.0

# Oncelik 1: dolu pozisyon varken yeni sinyal geldiginde
# entry/yon farkinin "farkli sinyal" sayilmasi icin esik
ENTRY_CHANGE_THRESHOLD = 0.5

# Piyasadan kapatma (TRADE_ACTION_DEAL) icin denenecek filling modlari, sirayla.
# Bu broker/sembolde RETURN, TRADE_ACTION_DEAL icin reddediliyor (10030 - Unsupported
# filling mode); IOC/FOK market emirlerinde daha yaygin desteklenir.
DEAL_FILLING_MODES = [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]

# --- TELEGRAM ---
DRAWDOWN_LIMIT = 0.20  # %20 kasa dusunce dur


def telegram(msg):
    """Telegram mesaji gonder."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        log(f"Telegram hatasi: {e}")


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def connect_mt5():
    # MT5 zaten acik ve giris yapilmis olmali (Windows baslangicindan otomatik baslayacak sekilde ayarli).
    # Parametre vermeden initialize() cagrilarak calisan terminal ornegine baglanilir.
    if not mt5.initialize():
        log(f"MT5 baglanma hatasi: {mt5.last_error()}")
        return False
    log(f"MT5 baglandi. Bakiye: {mt5.account_info().balance} USD")
    return True


def get_current_price(direction):
    tick = mt5.symbol_info_tick(SYMBOL)
    return tick.bid if direction == "SELL" else tick.ask


def open_trade(direction, entry, sl, tp1, tp2, tp3):
    entry = round(entry + PRICE_OFFSET, 2)
    sl    = round(sl + PRICE_OFFSET, 2)
    tp3   = round(tp3 + PRICE_OFFSET, 2)
    mt5.symbol_select(SYMBOL, True)
    tick = mt5.symbol_info_tick(SYMBOL)

    if direction == "SELL":
        current_price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL_STOP if current_price > entry else mt5.ORDER_TYPE_SELL_LIMIT
    else:
        current_price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY_STOP if current_price < entry else mt5.ORDER_TYPE_BUY_LIMIT

    request = {
        "action":       mt5.TRADE_ACTION_PENDING,
        "symbol":       SYMBOL,
        "volume":       LOT_SIZE,
        "type":         order_type,
        "price":        entry,
        "sl":           sl,
        "tp":           tp3,
        "deviation":    20,
        "magic":        999999,
        "comment":      "Mila",
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"Islem acildi: {result.order} | {direction} @ {entry} | SL:{sl} | TP1:{tp1} TP2:{tp2} TP3:{tp3}")
        return result.order
    else:
        log(f"Islem acilamadi: {result.retcode} - {result.comment}")
        return None


def close_position_at_market(ticket, direction):
    """Acik pozisyonu piyasa fiyatindan kapat.

    Oncelik 1: Yeni sinyal geldiginde (Lisa'nin entry'si degisti, dolayisiyla
    Lisa eski pozisyonunu kapattigi anlasildi) bizim pozisyonumuzu da
    piyasadan kapatip Lisa'nin "temiz cikis" davranisini izlemek icin kullanilir.

    Donus degerleri:
      "closed_by_us"   -> pozisyon acikti, biz kapattik (forced_close=True icin kullanilir)
      "already_closed" -> pozisyon zaten kapanmisti (dogal SL/TP - bizim aksiyonumuz degil)
      "failed"         -> pozisyon acik ama kapatma emri reddedildi, tekrar denenmeli
    """
    positions = mt5.positions_get(ticket=ticket)
    if not positions:
        log(f"Pozisyon zaten kapali (kapatma denenmeden once): ticket={ticket}")
        return "already_closed"

    position = positions[0]
    tick = mt5.symbol_info_tick(SYMBOL)

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

    # TRADE_ACTION_DEAL (piyasadan kapatma) icin filling mode'u sirayla dene.
    # Bu broker/sembolde RETURN reddediliyor (10030 - Unsupported filling mode);
    # market emirlerinde IOC/FOK genelde desteklenir. Ilk basariliyi/farkli-hatayi
    # verende dur.
    result = None
    for filling_mode in DEAL_FILLING_MODES:
        request["type_filling"] = filling_mode
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"Pozisyon piyasadan kapatildi: ticket={ticket} @ {price} (filling={filling_mode})")
            return "closed_by_us"
        if result.retcode != mt5.TRADE_RETCODE_INVALID_FILL:
            # Reddedilme nedeni filling mode degil - baska filling modlari denemeye
            # gerek yok, asagidaki "zaten kapanmis mi" kontroluyle devam et.
            break

    # Kapatma reddedildi - bu sirada pozisyon zaten kapanmis olabilir mi?
    if not mt5.positions_get(ticket=ticket):
        log(f"Pozisyon kapatma denemesi reddedildi ama zaten kapanmis: ticket={ticket} "
            f"({result.retcode} - {result.comment})")
        return "already_closed"

    log(f"Pozisyon kapatilamadi: ticket={ticket} | {result.retcode} - {result.comment}")
    return "failed"


def update_sl(ticket, new_sl):
    new_sl = round(new_sl, 2)
    positions = mt5.positions_get(ticket=ticket)
    if positions:
        position = positions[0]
        request = {
            "action":   mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl":       new_sl,
            "tp":       position.tp,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"SL guncellendi: ticket={ticket} yeni SL={new_sl}")
        else:
            log(f"SL guncellenemedi: {result.retcode} - {result.comment}")
    else:
        orders = mt5.orders_get(ticket=ticket)
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
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"Bekleyen emir SL guncellendi: ticket={ticket} yeni SL={new_sl}")
            else:
                log(f"Bekleyen emir SL guncellenemedi: {result.comment}")


def save_performance(record):
    """Performance kaydini JSON dosyasina ekle."""
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


def get_deal_info(ticket):
    """Kapanan islemin deal bilgilerini MT5'ten al."""
    try:
        deals = mt5.history_deals_get(position=ticket)
        if deals and len(deals) >= 2:
            close_deal = deals[-1]
            return {
                "close_price": close_deal.price,
                "close_time":  datetime.fromtimestamp(close_deal.time).strftime("%Y-%m-%d %H:%M:%S"),
                "profit":      close_deal.profit,
            }
    except:
        pass
    return None


def determine_result(active, close_price, forced_close=False):
    """Kapanış sonucunu sl_level'a gore belirle (fiyat esitsizligine guvenme - slippage payi var).

    forced_close=True: Oncelik 1 - yeni sinyal geldigi icin bizim piyasadan
    kapattigimiz erken cikis. Bu durumda sl_level==0 ve TP3'e ulasilmamissa
    sonuc "SL" degil "Exit" olarak kaydedilir (Lisa'nin kucuk kar/zararla
    erken cikis tanimina denk gelir). sl_level>=1 ise (TP1/TP2 zaten gecilmis,
    kar kilitlenmis) etiket aynen TP1/Entry kalir - bu zaten dogru bilgi.
    """
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
        # SL, girise tasinmisti (TP2 goruldu) -> basabas (Entry) ile kapandi
        return "Entry", pip
    elif forced_close:
        # TP2'ye ulasilmadan, yeni sinyal nedeniyle erken kapatildi -> Exit
        return "Exit", pip
    else:
        # SL hic tasinmadi, dogal kapanis -> orijinal SL ile kapandi
        return "SL", pip


def build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3):
    """Yeni acilan islem icin active sozlugu olustur."""
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
    """Kapanan islem icin performance kaydi olustur ve kaydet. (sonuc, pip, profit) doner."""
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


def handle_closed_position_and_open_new(active, signal_no, direction, entry, sl, tp1, tp2, tp3, forced_close):
    """Eski islem (active) artik MT5'te yok - dogal kapanmis veya biz piyasadan
    kapatmisiz. Kapanis bilgisini al, performansa kaydet, Telegram'a bildir,
    ardindan yeni sinyali ac. Yeni active sozlugunu (veya acilamadiysa None) doner.

    forced_close=True  -> Oncelik 1: biz piyasadan kapattik (close_position_at_market basarili)
    forced_close=False -> dogal kapanis (Lisa'nin sinyali degisirken bizim SL/TP'imiz de
                           tetiklenmis olabilir, veya kapatma denemeden once zaten kapanmisti)
    """
    deal = None
    for _ in range(5):
        deal = get_deal_info(active["ticket"])
        if deal:
            break
        time.sleep(0.3)

    if deal:
        sonuc, pip, profit = record_close(active, deal["close_price"], deal, forced_close=forced_close)
        telegram(f"[MilaGold] 🔄 Eski islem kapandi: {sonuc} {pip:+.2f} pip ({profit:+.2f} USD) | "
                 f"Yeni sinyal: #{signal_no} {direction} @ {entry}")
    else:
        log(f"Uyari: kapanis bilgisi alinamadi, performans kaydedilemedi: ticket={active['ticket']}")
        telegram(f"[MilaGold] ⚠️ Eski islem (ticket={active['ticket']}) kapandi ama kapanis bilgisi "
                 f"okunamadi. Yeni sinyal: #{signal_no} {direction} @ {entry}")

    log(f"Yeni sinyal aciliyor: #{signal_no} {direction} @ {entry}")
    ticket = open_trade(direction, entry, sl, tp1, tp2, tp3)
    if ticket:
        return build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3)
    return None


def read_signal():
    try:
        if not os.path.exists(SIGNAL_FILE):
            return None
        with open(SIGNAL_FILE, "r") as f:
            return json.load(f)
    except:
        return None


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
    """Mevcut SL pozisyonundan sl_level tahmin et.
    MT5 pozisyonundan okunur - entry ve sl bilgisi zaten var.

    sl_level=0: SL orijinal yerde (entry'den SL_DISTANCE uzakta)
    sl_level=1: SL girise tasinmis (TP2 goruldu)
    """
    entry = position.price_open
    sl    = position.sl

    if position.type == mt5.ORDER_TYPE_SELL:
        original_sl = entry + sl_dist
        entry_sl    = entry
        tp1         = entry - tp1_dist
    else:
        original_sl = entry - sl_dist
        entry_sl    = entry
        tp1         = entry + tp1_dist

    dist_original = abs(sl - original_sl)
    dist_entry    = abs(sl - entry_sl)
    dist_tp1      = abs(sl - tp1)

    if dist_entry < 0.6:
        return 1
    else:
        return 0


def adopt_orphans():
    """Restart sonrasi MT5'teki magic=999999 pozisyon/emirleri tara,
    active_trades listesine yukle (orphan adoption).
    Yeni bir liste doner."""
    adopted = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Acik pozisyonlar
    positions = mt5.positions_get(symbol=SYMBOL)
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
            rec["open_time"] = now_str  # gercek open_time bilinmiyor
            adopted.append(rec)
            log(f"Orphan pozisyon alindi: ticket={pos.ticket} {direction} @ {entry} sl_level={sl_level}")

    # Bekleyen emirler
    orders = mt5.orders_get(symbol=SYMBOL)
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
        telegram(f"[MilaGold] 🔄 {len(adopted)} orphan pozisyon/emir devralindi. "
                 f"Takip basladi.")
    return adopted


def main():
    log("MilaGold MT5 Agent basliyor...")
    if not connect_mt5():
        return

    # active_trades: tum takip edilen pozisyon/emirlerin listesi
    # (tekil active dict'in yerini aldi - Oncelik 2)
    active_trades = adopt_orphans()

    baslangic_bakiye = mt5.account_info().balance
    drawdown_durdur  = False
    log(f"Baslangic bakiyesi: {baslangic_bakiye} USD")
    log(f"Hazir. {len(active_trades)} aktif islem devralindi. signal.json bekleniyor...")
    telegram(f"[MilaGold] ✅ MilaGold MT5 Agent basladi. Bakiye: {baslangic_bakiye} USD | "
             f"Devralınan: {len(active_trades)} islem")

    while True:
        try:
            signal = read_signal()

            # Gunluk sifirlama
            simdi = datetime.now()
            if simdi.hour == 0 and simdi.minute == 0 and simdi.second < 5:
                yeni_bakiye = mt5.account_info().balance
                if yeni_bakiye != baslangic_bakiye:
                    log(f"Gunluk sifirlama: yeni baslangic bakiyesi = {yeni_bakiye} USD")
                    telegram(f"[MilaGold] 🔄 Yeni gun. Baslangic bakiyesi: {yeni_bakiye} USD")
                    baslangic_bakiye = yeni_bakiye
                    drawdown_durdur = False

            # Drawdown kontrolu
            guncel_bakiye = mt5.account_info().balance
            dusus = (baslangic_bakiye - guncel_bakiye) / baslangic_bakiye
            if dusus >= DRAWDOWN_LIMIT and not drawdown_durdur:
                mesaj = (f"[MilaGold] ⚠️ EMNiYET STOPU! Kasa %{dusus*100:.1f} dusus. "
                         f"Islem alma durduruldu. Bakiye: {guncel_bakiye} USD")
                log(mesaj)
                telegram(mesaj)
                drawdown_durdur = True

            if drawdown_durdur:
                time.sleep(5)
                continue

            # --- YENI SiNYAL iSLEME ---
            if signal and not signal.get("processed") and signal.get("status") in ("RUNNING", "WAITING"):
                direction = signal["direction"]
                entry     = signal["entry"]
                sl        = signal["sl"]
                tp1       = signal["tp1"]
                tp2       = signal["tp2"]
                tp3       = signal["tp3"]
                signal_no = signal.get("signal_no", "?")

                # "Ana" pozisyon: listede ilk pozisyona-donusmus islem
                # (bekleyen emirler sinyal kararinda kullanilmaz, sadece takip edilir)
                ana = next((t for t in active_trades
                            if mt5.positions_get(ticket=t["ticket"])), None)

                if ana is None:
                    # Hicbir aktif pozisyon yok - bekleyen emirler var mi?
                    # Hepsini iptal et (birden fazla olabilir - orn. fiyat uzaklasmis
                    # eski LIMIT emirler listede kalabilir)
                    bekleyenler = [t for t in active_trades
                                   if mt5.orders_get(ticket=t["ticket"])]
                    for bekleyen in bekleyenler:
                        log(f"Yeni sinyal geldi, bekleyen emir iptal ediliyor: "
                            f"ticket={bekleyen['ticket']} ({bekleyen['direction']} @ {bekleyen['entry']})")
                        cancel_result = mt5.order_send({
                            "action": mt5.TRADE_ACTION_REMOVE,
                            "order":  bekleyen["ticket"],
                        })
                        if cancel_result.retcode == mt5.TRADE_RETCODE_DONE:
                            log(f"Bekleyen emir iptal edildi: ticket={bekleyen['ticket']}")
                            active_trades = [t for t in active_trades
                                             if t["ticket"] != bekleyen["ticket"]]
                        else:
                            log(f"Emir iptal edilemedi: ticket={bekleyen['ticket']} | {cancel_result.comment}")

                    log(f"Yeni sinyal alindi: #{signal_no} {direction} @ {entry}")
                    ticket = open_trade(direction, entry, sl, tp1, tp2, tp3)
                    if ticket:
                        active_trades.append(
                            build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3))
                    clear_signal()

                else:
                    # Ana pozisyon var - Exit karar mantigi
                    yon_degisti  = (direction != ana["direction"])
                    fark         = entry - ana["entry"]

                    if ana["direction"] == "SELL":
                        yeni_daha_iyi = fark > ENTRY_CHANGE_THRESHOLD
                    else:
                        yeni_daha_iyi = fark < -ENTRY_CHANGE_THRESHOLD

                    entry_degisti = abs(fark) > ENTRY_CHANGE_THRESHOLD

                    if not entry_degisti and not yon_degisti:
                        log(f"Ayni sinyal tekrar geldi, islem yapilmiyor: #{signal_no}")
                        clear_signal()

                    elif yon_degisti or yeni_daha_iyi:
                        # Kapat ve yeni sinyali ac
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
                            if ticket:
                                active_trades.append(
                                    build_active(ticket, signal_no, direction, entry, sl, tp1, tp2, tp3))
                            clear_signal()

                    else:
                        # Yeni entry daha kotu
                        if ana["sl_level"] == 0:
                            # Durum 3: tam risk var, yeni islemi alma
                            log(f"Yeni sinyal daha kotu entry, sl_level=0. "
                                f"Eski pozisyon tutuldu, sinyal atildi: #{signal_no}")
                            telegram(f"[MilaGold] ℹ️ Sinyal atildi (kotu entry, sl_level=0): "
                                     f"{ana['direction']}@{ana['entry']} devam | Atlanan: #{signal_no}@{entry}")
                            clear_signal()
                        else:
                            # Durum 4: risk kalmadi, yeniyi de ac (max 2 pozisyon)
                            if len(active_trades) >= 2:
                                log(f"Yeni sinyal daha kotu entry, sl_level={ana['sl_level']}. "
                                    f"Ama zaten 2 pozisyon var, sinyal atildi: #{signal_no}")
                                telegram(f"[MilaGold] ℹ️ Sinyal atildi (max 2 pozisyon): #{signal_no}@{entry}")
                            else:
                                log(f"Yeni sinyal daha kotu entry, sl_level={ana['sl_level']}. "
                                    f"2. pozisyon aciliyor: #{signal_no} @ {entry}")
                                ticket2 = open_trade(direction, entry, sl, tp1, tp2, tp3)
                                if ticket2:
                                    active_trades.append(
                                        build_active(ticket2, signal_no, direction, entry, sl, tp1, tp2, tp3))
                                    telegram(f"[MilaGold] 📊 2. pozisyon acildi: "
                                             f"#{signal_no} {direction} @ {entry} | ticket={ticket2}")
                            clear_signal()

            # --- AKTiF iSLEMLERi TAKiP ET ---
            kapanan_tickets = []
            for trade in active_trades:
                ticket    = trade["ticket"]
                direction = trade["direction"]
                tp1       = trade["tp1"]
                tp2       = trade["tp2"]
                current   = get_current_price(direction)

                positions = mt5.positions_get(ticket=ticket)
                orders    = mt5.orders_get(ticket=ticket)

                if not positions and not orders:
                    log(f"Islem kapandi: ticket={ticket}")
                    deal = get_deal_info(ticket)
                    if deal:
                        record_close(trade, deal["close_price"], deal, forced_close=False)
                    kapanan_tickets.append(ticket)
                    continue

                if not positions:
                    # Hala bekleyen emir - TP takibi yapma
                    continue

                # TP1 takibi - sadece log (bir kez), SL tasinmiyor
                if not trade["tp1_hit"]:
                    if (direction == "SELL" and current <= tp1) or \
                       (direction == "BUY"  and current >= tp1):
                        log(f"TP1 gecildi: ticket={ticket} fiyat={current} TP1={tp1} (SL tasinmiyor)")
                        trade["tp1_hit"] = True

                # TP2 takibi - SL girise tas
                if trade["sl_level"] < 1:
                    if (direction == "SELL" and current <= tp2) or \
                       (direction == "BUY"  and current >= tp2):
                        log(f"TP2 gecildi: ticket={ticket} fiyat={current} TP2={tp2} -> SL girise tasiniyor")
                        update_sl(ticket, trade["entry"])
                        trade["sl_level"] = 1

            # Kapananlari listeden cikar
            active_trades = [t for t in active_trades if t["ticket"] not in kapanan_tickets]

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
