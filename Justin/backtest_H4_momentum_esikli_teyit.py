# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - A Ailesi (Momentum/Trend-Following) - TUR 2
HIPOTEZ H4 - "Momentum-Esikli Teyit"

Kaynak gorev: Orkestrator cagrisi 19 Temmuz 2026 09:20 (bu gorevin YAZILI cagri metni, Backtest
Muhendisi sistem promptunun aldigi girdi olarak ayni klasorde bulunan gorev notunda saklidir).
Girdi: stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md, HIPOTEZ H4 bolumu.

Mekanizma (Tam Tur 1 H2'den TEK fark - giris tetiginde): dokunus barindan (i) SONRAKI barin (i+1,
"teyit bari") hem trend yonunde kapanmasi HEM DE govde/ATR14(i+1) >= k olmasi. Giris, teyit barindan
bir SONRAKI barin (i+2) ACILISINDA gerceklesir. Rejim/kanal filtresi, dokunus tanimi, cikis uc-
kosullu cercevesi (SL/TP/kirilim-erken-cikis) Tam Tur 1/H2 ile AYNI - degisen SADECE teyit kriteri.

Kapsam (tek script, FAZ 0-9, H2'nin yapisal iskeletiyle tutarli - karsilastirilabilirlik amacli):
  FAZ 0: MT5 baglanti + ham veri (H1/M30/M15/M5) - BAGIMSIZ CEKME (Tam Tur 1/H2'den devralinmadi)
  FAZ 1: On-kontrol Madde 1 - DST/saat-esleme BAGIMSIZ dogrulama (H1, M15, M5)
  FAZ 2: Pivot/kanal tespiti (H1/M30, up/down) - LOOK-AHEAD DUZELTMESI ile (5-bar gecikmeli confirm)
  FAZ 3: Dokunus tespiti (M15 VE M5, H1/M30 icin) - AYNI dokunus tanimi (|kapanis-projeksiyon|<=0.5xATR)
  FAZ 4: Momentum-esikli aday-giris uretimi (k=1.0 VE k=0.5, M15 VE M5) + On-kontrol Madde 2
         (S1 maliyet-orani, GERCEK/olay-kosullu ATR ile, gecmeyen kombinasyon ana teste GECMEZ)
  FAZ 5: Train/Validation/Test ayrimi (purged/embargolu, zaman-bazli) - her kombinasyon icin ayri
  FAZ 6: Trade simulasyonu (tek-pozisyon, uc-kosullu cikis: SL/TP/kirilim-bazli-erken-cikis)
  FAZ 7: Walk-forward SL/TP kalibrasyonu (Train'de tara, Validation'da sec, Test'te TEK KEZ) - HER
         kombinasyon KENDI verisinde BAGIMSIZ kalibre edilir, hicbir katsayi otomatik tasinmaz
  FAZ 8: Kirilim-bazli-erken-cikis dogrulama ornekleri
  FAZ 9: Islem frekansi + kirilim analizi + JSON/CSV kaydi

Izolasyon: Yalniz C:\\MilaYatirim\\mila-yatirim-sistemi\\Justin\\ icinde calisilmistir. Veri
dogrudan MT5'ten (GOLD). MilaGold/Lisa/Signal GPT'ye ait hicbir dosya/deger/format referans
alinmamistir. Kanal tespiti algoritmasi ve genel iskelet, ayni proje icindeki
backtest_A_ailesi_H2.py ile METODOLOJIK OLARAK tutarli tutulmustur (karsilastirilabilirlik amacli,
izolasyon ihlali degil - kural yalniz BASKA proje dosyalarini yasaklar); SL/TP katsayilari ve
teyit-kriteri KENDINE OZGUDUR, otomatik tasinmamistir (bkz. justin_backtest_onkontrol_standardi.md
Madde 3).
"""
import json
import math
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date

OUT_PATH = r"C:\MilaYatirim\mila-yatirim-sistemi\Justin\backtest_H4_momentum_esikli_teyit_output.json"

# ============================================================
# SABITLER
# ============================================================
SYMBOL = "GOLD"
MIN_TOUCHES = 3            # kanal gecerlilik esigi (Stratejist tasarimi - Tam Tur 1'den DEGISMEDI)
TOUCH_K = 0.5               # dokunus toleransi: 0.5 x ATR14 (Stratejist/Arastirmaci tanimi - AYNI)
SWING_N = 5                 # fraktal pivot penceresi (N=5, sol+sag)
LOOKAHEAD_LAG_BARS = 5      # swing bir bar'in "swing" oldugu ancak N=5 bar SONRA kesinlesir
CAP_DAYS = 300               # kanal arama penceresi sinirlamasi (muhendislik pratikligi)
EMA_FAST, EMA_SLOW = 50, 200
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9

KASA_USD = 2000.0            # justin_gecmis_calisma.md
RISK_PCT_UST_SINIR = 0.01    # islem-basi risk UST SINIRI (kasa x %1)
TABAN_LOT = 0.01
LOT_STEP_USD = 0.01          # lot yuvarlama adimi

EMBARGO_DAYS = 45            # train/val/test arasi purge/embargo (H2 ile AYNI yapisal sabit)
TRAIN_FRAC, VAL_FRAC = 0.50, 0.25  # kalan Test'e (~%25)

DST_TRANSITIONS = ["2025-03-30", "2025-10-26", "2026-03-29"]

# H4'e OZEL: teyit/momentum grid'i - Stratejist'in birincil (k=1.0) + duyarlilik (k=0.5) tanimi
K_GRID = [1.0, 0.5]

# SL/TP arama-uzayi (grid) - H1/H2/H3 ile AYNI YAPIDA (metodolojik tutarlilik icin), ancak
# SECILEN katsayilar asagida H4'un KENDI Train/Validation verisinde BAGIMSIZ belirlenir - hicbir
# deger otomatik TASINMAZ (bkz. justin_backtest_onkontrol_standardi.md Madde 3).
SL_MULT_GRID = [0.5, 0.75, 1.0]
TP_MULT_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
MIN_TRADES_FOR_SELECTION = 30

print("=" * 70)
print("FAZ 0: MT5 BAGLANTI + HAM VERI (BAGIMSIZ CEKME)")
print("=" * 70)
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size
USD_PER_POINT_PER_LOT = CONTRACT_SIZE * POINT
print(f"point={POINT}, contract_size={CONTRACT_SIZE}, USD/puan/1.0-lot={USD_PER_POINT_PER_LOT}")

TFS = {
    "M5": (mt5.TIMEFRAME_M5, 5),
    "M15": (mt5.TIMEFRAME_M15, 15),
    "M30": (mt5.TIMEFRAME_M30, 30),
    "H1": (mt5.TIMEFRAME_H1, 60),
}
raw = {}
for tf_name, (tf_const, bar_min) in TFS.items():
    rates = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)
    raw[tf_name] = rates
    t0 = datetime.fromtimestamp(int(rates[0]['time']), tz=timezone.utc)
    t1 = datetime.fromtimestamp(int(rates[-1]['time']), tz=timezone.utc)
    print(tf_name, "n=", len(rates), t0, "->", t1)

results = {"meta": {
    "hipotez_adi": "A Ailesi H4 - Momentum-Esikli Teyit",
    "min_touches": MIN_TOUCHES, "touch_k": TOUCH_K, "swing_n": SWING_N,
    "lookahead_lag_bars": LOOKAHEAD_LAG_BARS, "cap_days": CAP_DAYS,
    "ema_fast": EMA_FAST, "ema_slow": EMA_SLOW, "macd": [MACD_FAST, MACD_SLOW, MACD_SIG],
    "kasa_usd": KASA_USD, "risk_pct_ust_sinir": RISK_PCT_UST_SINIR, "taban_lot": TABAN_LOT,
    "embargo_days": EMBARGO_DAYS, "k_grid": K_GRID,
}}
results["veri_araligi"] = {tf: {"n_bar": int(len(raw[tf])),
                                 "baslangic": str(datetime.fromtimestamp(int(raw[tf][0]['time']), tz=timezone.utc)),
                                 "bitis": str(datetime.fromtimestamp(int(raw[tf][-1]['time']), tz=timezone.utc))}
                           for tf in TFS}
# M5 veri derinligi uyarisi - broker/terminal M5 gecmisi diger TF'lerden cok daha kisa
m5_gun = (int(raw["M5"][-1]['time']) - int(raw["M5"][0]['time'])) / 86400.0
m15_gun = (int(raw["M15"][-1]['time']) - int(raw["M15"][0]['time'])) / 86400.0
results["m5_veri_derinligi_uyarisi"] = (
    f"M5 verisi {m5_gun:.0f} gun kapsiyor (terminal/broker limiti, 99999 bar), M15 ise {m15_gun:.0f} "
    f"gun kapsiyor - M5 cross-check testi M15'e gore COK DAHA KISA bir donemi temsil eder, bu "
    f"Stratejist'in 'M5 sonucu daha kirilgan kabul edilmeli' uyarisina EK bir kirilganlik "
    f"kaynagidir (kanal sayisi kirilganligina bagimsiz veri-uzunlugu kirilganligi)."
)
print(results["m5_veri_derinligi_uyarisi"])

# ============================================================
# FAZ 1: ON-KONTROL MADDE 1 - DST / SAAT-ESLEME BAGIMSIZ DOGRULAMA
# ============================================================
print("=" * 70)
print("FAZ 1: DST / SAAT-ESLEME BAGIMSIZ DOGRULAMA")
print("=" * 70)


def dst_check(rates, tf_label):
    n = len(rates)
    t = rates['time'].astype(np.int64)
    hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
    dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])
    gap_threshold_sec = 23 * 3600
    gaps = []
    for i in range(1, n):
        dt = t[i] - t[i - 1]
        if dt > gap_threshold_sec:
            gaps.append({"friday_close_utc_hour": int(hours[i - 1]), "friday_close_date": dates[i - 1],
                         "sunday_open_utc_hour": int(hours[i]), "sunday_open_date": dates[i]})

    def hour_mode_window(gaps_list, center_date_str, days=21):
        cy, cm, cd = [int(x) for x in center_date_str.split("-")]
        center = _date(cy, cm, cd)
        before, after = [], []
        for g in gaps_list:
            gy, gm, gd = [int(x) for x in g["friday_close_date"].split("-")]
            gdate = _date(gy, gm, gd)
            delta = (gdate - center).days
            if -days <= delta < 0:
                before.append(g["friday_close_utc_hour"])
            elif 0 <= delta <= days:
                after.append(g["friday_close_utc_hour"])
        return before, after

    dst_res = []
    for tr in DST_TRANSITIONS:
        before, after = hour_mode_window(gaps, tr)
        kayma = (bool(before) and bool(after) and
                 (max(set(before), key=before.count) != max(set(after), key=after.count)))
        dst_res.append({"gecis_tarihi": tr, "oncesi_cuma_kapanis_saatleri": before,
                         "sonrasi_cuma_kapanis_saatleri": after, "kayma_tespit_edildi_mi": bool(kayma)})
    return {"tf": tf_label, "toplam_hafta_sonu_gecis_sayisi": len(gaps), "dst_kontrolu": dst_res}


tick_now = mt5.symbol_info_tick(SYMBOL)
epoch_as_utc = datetime.fromtimestamp(tick_now.time, tz=timezone.utc).replace(tzinfo=None)
vps_local_now = datetime.now()
diff_seconds = abs((epoch_as_utc - vps_local_now).total_seconds())
print(f"canli capraz kontrol: epoch_utc={epoch_as_utc}, vps_yerel={vps_local_now}, fark_sn={diff_seconds:.2f}")

dst_h1 = dst_check(raw["H1"], "H1")
dst_m15 = dst_check(raw["M15"], "M15")
dst_m5 = dst_check(raw["M5"], "M5")
print("H1 DST kontrolu:", dst_h1["dst_kontrolu"])
print("M15 DST kontrolu:", dst_m15["dst_kontrolu"])
print("M5 DST kontrolu:", dst_m5["dst_kontrolu"])

results["faz1_on_kontrol_dst"] = {
    "canli_capraz_kontrol": {"epoch_utc_okuma": str(epoch_as_utc), "vps_yerel_simdi": str(vps_local_now),
                              "fark_saniye": diff_seconds},
    "H1": dst_h1, "M15": dst_m15, "M5": dst_m5,
    "sonuc_notu": ("H4 icin BAGIMSIZ olarak (H2/Tam Tur 1'den devralinmadan) yeniden kosturuldu, H1/M15 "
                   "VE M5 uzerinde. Beklenen: MT5/XM sunucusu AB/Kibris DST takvimini izliyor (yaz GMT+3, "
                   "kis GMT+2) - onceki turlerde (H1/H2/H3) tekrarlanan bulguyla TUTARLI olup olmadigi "
                   "asagidaki kayma sonuclarindan okunmalidir."),
}
print("FAZ 1 tamamlandi.")

# ============================================================
# ORTAK YARDIMCI FONKSIYONLAR
# ============================================================


def ema(values, span):
    return pd.Series(values).ewm(span=span, adjust=False).mean().values


def macd(values, fast=MACD_FAST, slow=MACD_SLOW, sig=MACD_SIG):
    macd_line = ema(values, fast) - ema(values, slow)
    signal_line = pd.Series(macd_line).ewm(span=sig, adjust=False).mean().values
    return macd_line, signal_line


def atr_series_pts(rates, window=14, point=POINT):
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    closes = rates['close'].astype(float)
    prev_close = np.roll(closes, 1)
    prev_close[0] = closes[0]
    tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
    atr = pd.Series(tr).rolling(window, min_periods=window).mean().values
    return atr / point


def find_swings(rates, n=SWING_N):
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    m = len(highs)
    swing_high = np.zeros(m, dtype=bool)
    swing_low = np.zeros(m, dtype=bool)
    for i in range(n, m - n):
        wh = highs[i - n:i + n + 1]
        wl = lows[i - n:i + n + 1]
        if highs[i] == wh.max():
            swing_high[i] = True
        if lows[i] == wl.min():
            swing_low[i] = True
    return swing_high, swing_low


CLOSES = {tf: raw[tf]['close'].astype(float) for tf in TFS}
OPENS = {tf: raw[tf]['open'].astype(float) for tf in TFS}
HIGHS = {tf: raw[tf]['high'].astype(float) for tf in TFS}
LOWS = {tf: raw[tf]['low'].astype(float) for tf in TFS}
TIMES = {tf: raw[tf]['time'].astype(np.int64) for tf in TFS}
SPREADS = {tf: raw[tf]['spread'].astype(float) for tf in TFS}
ATR = {tf: atr_series_pts(raw[tf]) for tf in TFS}
EMA50 = {tf: ema(CLOSES[tf], EMA_FAST) for tf in TFS}
EMA200 = {tf: ema(CLOSES[tf], EMA_SLOW) for tf in TFS}
MACD_LINE, MACD_SIG_ARR = {}, {}
for tf in TFS:
    ml, sl_ = macd(CLOSES[tf])
    MACD_LINE[tf] = ml
    MACD_SIG_ARR[tf] = sl_

SWINGS = {}
for tf in ("H1", "M30"):
    sh, sl_ = find_swings(raw[tf])
    SWINGS[tf] = {"swing_high": sh, "swing_low": sl_}
    print(tf, "swing_high n=", int(sh.sum()), "swing_low n=", int(sl_.sum()))

# ============================================================
# FAZ 2: PIVOT/KANAL TESPITI - LOOK-AHEAD DUZELTMESI ILE (H2 ile BIREBIR AYNI mantik)
# ============================================================
print("=" * 70)
print("FAZ 2: PIVOT/KANAL TESPITI (LOOK-AHEAD DUZELTMESI ILE)")
print("=" * 70)

CAP_MINUTES = CAP_DAYS * 24 * 60


def detect_channels(tf_name, direction):
    rates = raw[tf_name]
    bar_min = TFS[tf_name][1]
    closes = CLOSES[tf_name]
    highs = HIGHS[tf_name]
    lows = LOWS[tf_name]
    times = TIMES[tf_name]
    atr = ATR[tf_name]
    ema50 = EMA50[tf_name]
    ema200 = EMA200[tf_name]
    macd_l = MACD_LINE[tf_name]
    macd_s = MACD_SIG_ARR[tf_name]
    n_total = len(closes)

    if direction == "up":
        sign = 1
        swing_mask = SWINGS[tf_name]["swing_low"]
        price_arr = lows
    else:
        sign = -1
        swing_mask = SWINGS[tf_name]["swing_high"]
        price_arr = highs

    swing_idx = np.where(swing_mask)[0]
    cap_bars = CAP_MINUTES // bar_min
    m = len(swing_idx)

    channels = []
    pos = 0
    while pos < m - 2:
        anchor = swing_idx[pos]
        if np.isnan(atr[anchor]):
            pos += 1
            continue
        anchor_price = price_arr[anchor]
        anchor_time = times[anchor]

        j = pos + 1
        second = None
        while j < m:
            c = swing_idx[j]
            if times[c] - anchor_time > cap_bars * bar_min * 60:
                break
            if np.isnan(atr[c]):
                j += 1
                continue
            delta = price_arr[c] - anchor_price
            if sign * delta > 0:
                second = c
                break
            j += 1
        if second is None:
            pos += 1
            continue

        slope = (price_arr[second] - anchor_price) / (second - anchor)
        touches = [anchor, second]
        confirm_idx = None
        k = j + 1
        while k < m:
            c = swing_idx[k]
            if times[c] - anchor_time > cap_bars * bar_min * 60:
                break
            if np.isnan(atr[c]):
                k += 1
                continue
            projected = anchor_price + slope * (c - anchor)
            tol = TOUCH_K * atr[c]
            diff = price_arr[c] - projected
            if sign * diff < -tol:
                break  # kirildi (dokunus sayilmadan)
            elif abs(diff) <= tol:
                touches.append(c)
                if len(touches) >= MIN_TOUCHES and confirm_idx is None:
                    confirm_idx = c
            k += 1

        if confirm_idx is None:
            pos += 1
            continue

        # --- LOOK-AHEAD DUZELTMESI: kanal ancak confirm_idx + 5 barda "bilinir" ---
        confirmed_active_idx = confirm_idx + LOOKAHEAD_LAG_BARS
        if confirmed_active_idx >= n_total:
            pos += 1
            continue

        if direction == "up":
            ema_ok = ema50[confirmed_active_idx] > ema200[confirmed_active_idx]
            macd_ok = macd_l[confirmed_active_idx] > macd_s[confirmed_active_idx]
        else:
            ema_ok = ema50[confirmed_active_idx] < ema200[confirmed_active_idx]
            macd_ok = macd_l[confirmed_active_idx] < macd_s[confirmed_active_idx]

        if not (ema_ok and macd_ok):
            pos += 1
            continue

        break_idx = None
        limit_idx = min(n_total - 1, anchor + cap_bars)
        for i in range(confirmed_active_idx + 1, limit_idx + 1):
            projected = anchor_price + slope * (i - anchor)
            tol = TOUCH_K * atr[i] if not np.isnan(atr[i]) else TOUCH_K * np.nanmedian(atr)
            diff = closes[i] - projected
            if sign * diff < -tol:
                break_idx = i
                break
        censored = False
        if break_idx is None:
            break_idx = limit_idx
            censored = True

        break_known_time = int(times[break_idx]) + bar_min * 60

        channels.append({
            "tf": tf_name, "direction": direction,
            "anchor_idx": int(anchor), "second_idx": int(second),
            "confirm_idx_ham": int(confirm_idx),
            "confirmed_active_idx": int(confirmed_active_idx),
            "break_idx": int(break_idx),
            "n_touches_total": int(len(touches)), "slope_per_bar_pts": float(slope / POINT),
            "anchor_time": int(anchor_time),
            "confirmed_active_time": int(times[confirmed_active_idx]),
            "break_time": int(times[break_idx]),
            "break_known_time": int(break_known_time),
            "anchor_price": float(anchor_price),
            "duration_bars_confirmed_to_break": int(break_idx - confirmed_active_idx),
            "lag_bars_confirm_ham_to_active": int(confirmed_active_idx - confirm_idx),
            "censored_veri_sonu": bool(censored),
        })

        next_pos = np.searchsorted(swing_idx, break_idx, side="right")
        pos = max(next_pos, pos + 1)

    return channels


channels_all = {}
for tf_name in ("H1", "M30"):
    channels_all[tf_name] = {}
    for direction in ("up", "down"):
        chs = detect_channels(tf_name, direction)
        channels_all[tf_name][direction] = chs
        print(tf_name, direction, "confirmed kanal sayisi (look-ahead-duzeltilmis):", len(chs))

results["faz2_kanal_sayilari"] = {
    tf: {d: len(channels_all[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")
}

# ============================================================
# LOOK-AHEAD BIAS DOGRULAMASI (AYRI/ACIK BOLUM - Stratejist'in KRITIK maddesi)
# ============================================================
all_lags = []
for tf_name in ("H1", "M30"):
    for direction in ("up", "down"):
        for c in channels_all[tf_name][direction]:
            all_lags.append(c["lag_bars_confirm_ham_to_active"])
all_lags = np.array(all_lags)
results["look_ahead_bias_dogrulamasi"] = {
    "tanim": ("Kanal/pivot tanimi (N=5 sag-pencereli fraktal swing) Tam Tur 1'den DEGISMEDI. Bir "
              "swing noktasi, ancak kendisinden N=5 bar SONRASI gerceklestiginde geometrik olarak "
              "'swing' oldugu belli olur (fraktal tanimi sag pencereye bakar) - bu nedenle "
              "confirm_idx_ham (3. dokunusun swing olarak GEOMETRIK olustugu bar) DOGRUDAN "
              "kullanilirsa look-ahead bias olusur."),
    "duzeltme": ("Tum asagidaki dokunus/tetik/giris hesaplamalari confirmed_active_idx = "
                 "confirm_idx_ham + 5 (LOOKAHEAD_LAG_BARS) kullanir - yani kanal, gercek-zamanli "
                 "sistemde ancak bu bar'da 'bilinir/kullanilabilir' varsayilir. confirm_idx_ham hicbir "
                 "yerde dogrudan dokunus/giris hesaplamasinda KULLANILMAZ, sadece FAZ2 kanal tespit "
                 "kaydinda referans olarak saklanir."),
    "dogrulama_istatistigi": {
        "toplam_kanal_sayisi": int(len(all_lags)),
        "lag_bars_sabit_mi_5": bool(np.all(all_lags == LOOKAHEAD_LAG_BARS)) if len(all_lags) else None,
        "lag_bars_min_max": [int(all_lags.min()), int(all_lags.max())] if len(all_lags) else None,
    },
    "not": ("lag_bars_sabit_mi_5 = True olmasi beklenir (LOOKAHEAD_LAG_BARS sabit 5 olarak "
            "confirmed_active_idx hesaplamasina eklendigi icin) - bu, duzeltmenin HER kanalda "
            "tutarli uygulandiginin basit bir ic-tutarlilik kaniti olarak raporlanir."),
}
print("Look-ahead bias dogrulamasi:", results["look_ahead_bias_dogrulamasi"]["dogrulama_istatistigi"])
print("FAZ 2 tamamlandi.")

# ============================================================
# FAZ 3: DOKUNUS TESPITI (M15 VE M5, H1/M30 icin) - LOOK-AHEAD-SAFE, VEKTORIZE
# ============================================================
print("=" * 70)
print("FAZ 3: DOKUNUS TESPITI (M15 / M5)")
print("=" * 70)


def get_touches_per_channel(ltf_name, channels_htf):
    """Her ortusen kanal icin (touch_idx array, hi sinirlari) dondurur. Dokunus tanimi H2/Tam
    Tur 1 ile BIREBIR AYNI: |kapanis - projeksiyon| <= 0.5*ATR14(ltf bar). Pencere confirmed_active_
    time -> break_known_time (LOOK-AHEAD-SAFE, FAZ2'nin duzeltilmis alanlari kullanilir)."""
    ltf_times = TIMES[ltf_name]
    ltf_closes = CLOSES[ltf_name]
    ltf_atr = ATR[ltf_name]
    n_total = len(ltf_closes)
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    per_channel = []
    n_overlap = 0
    for c in channels_htf:
        conf_t = c["confirmed_active_time"]
        brk_known_t = c["break_known_time"]
        if brk_known_t < ltf_t0 or conf_t > ltf_t1:
            continue
        n_overlap += 1
        win_start = max(conf_t, ltf_t0)
        win_end = min(brk_known_t, ltf_t1)
        lo = np.searchsorted(ltf_times, win_start, side="left")
        hi = np.searchsorted(ltf_times, win_end, side="right")
        if hi - lo < 3 or lo >= hi - 2:
            continue

        sign = 1 if c["direction"] == "up" else -1
        anchor_price = c["anchor_price"]
        anchor_time = c["anchor_time"]
        bar_min_htf = TFS[c["tf"]][1]
        slope_per_bar = c["slope_per_bar_pts"] * POINT
        slope_per_sec = slope_per_bar / (bar_min_htf * 60)

        idx = np.arange(lo, hi - 2)  # touch=i, teyit=i+1, giris=i+2 - ucu de hi/n_total icinde olmali
        idx = idx[idx + 2 < n_total]
        if len(idx) == 0:
            continue
        t_i = ltf_times[idx]
        atr_i = ltf_atr[idx]
        valid = ~np.isnan(atr_i)
        projected = anchor_price + slope_per_sec * (t_i - anchor_time)
        tol = TOUCH_K * atr_i
        diff = ltf_closes[idx] - projected
        touch_mask = valid & (np.abs(diff) <= tol)
        touch_idx = idx[touch_mask]
        if len(touch_idx) == 0:
            continue
        per_channel.append({"touch_idx": touch_idx, "channel": c, "hi": int(hi)})

    return per_channel, n_overlap


TOUCHES_CACHE = {}
touch_overlap_report = {}
for ltf_name in ("M15", "M5"):
    for htf_name in ("H1", "M30"):
        for direction in ("up", "down"):
            per_ch, n_ov = get_touches_per_channel(ltf_name, channels_all[htf_name][direction])
            TOUCHES_CACHE[(ltf_name, htf_name, direction)] = per_ch
            n_touch_total = int(sum(len(x["touch_idx"]) for x in per_ch))
            touch_overlap_report[f"{ltf_name}_{htf_name}_{direction}"] = {
                "ortusen_kanal": n_ov, "toplam_dokunus": n_touch_total,
            }
            print(f"{ltf_name} <- {htf_name} {direction}: ortusen kanal={n_ov}, toplam dokunus={n_touch_total}")

results["faz3_dokunus_ozet"] = touch_overlap_report
print("FAZ 3 tamamlandi.")

# ============================================================
# FAZ 4: MOMENTUM-ESIKLI ADAY-GIRIS URETIMI + ON-KONTROL MADDE 2 (S1)
# ============================================================
print("=" * 70)
print("FAZ 4: MOMENTUM-ESIKLI ADAY-GIRIS URETIMI + ON-KONTROL MADDE 2")
print("=" * 70)


def build_momentum_candidates(ltf_name, htf_name, direction, k):
    closes = CLOSES[ltf_name]
    opens = OPENS[ltf_name]
    atr = ATR[ltf_name]
    times = TIMES[ltf_name]
    n_total = len(closes)
    sign = 1 if direction == "up" else -1
    per_channel = TOUCHES_CACHE[(ltf_name, htf_name, direction)]

    cands = []
    for ch in per_channel:
        ti = ch["touch_idx"]
        c = ch["channel"]
        hi = ch["hi"]
        mask_bound = (ti + 2 < hi) & (ti + 2 < n_total)
        ti = ti[mask_bound]
        if len(ti) == 0:
            continue
        trig = ti + 1
        ex = ti + 2
        atr_trig = atr[trig]
        valid = ~np.isnan(atr_trig)
        body = np.abs(closes[trig] - opens[trig]) / POINT
        dircond = sign * (closes[trig] - closes[ti]) > 0
        momcond = valid & (body >= k * atr_trig)
        cond = dircond & momcond
        ti_f, trig_f, ex_f, atr_f = ti[cond], trig[cond], ex[cond], atr_trig[cond]

        brk_known_t = c["break_known_time"]
        ex_times = times[ex_f]
        keep = ex_times < brk_known_t
        ti_f, trig_f, ex_f, atr_f = ti_f[keep], trig_f[keep], ex_f[keep], atr_f[keep]

        for jx in range(len(ex_f)):
            cands.append({
                "exec_idx": int(ex_f[jx]), "direction": direction, "tf_source": htf_name,
                "atr_at_signal": float(atr_f[jx]), "touch_idx": int(ti_f[jx]),
                "trigger_idx": int(trig_f[jx]), "channel_break_known_time": int(brk_known_t),
            })
    return cands


def s1_precheck(ltf_name, all_cands, label):
    """On-kontrol Madde 2: S1 maliyet-orani, bu OLAY KUMESININ (momentum-filtreli) kendi ATR-at-
    signal medyanina gore. Spread global-medyan (LTF genelinde) kullanilir - olay-kosullu spread
    varyasyonu ATR kadar buyuk olmadigi icin bu basitlestirme yeterli kabul edilmistir (asagida
    acikca not edilir)."""
    spread_median = float(np.median(SPREADS[ltf_name]))
    if len(all_cands) == 0:
        return {
            "label": label, "n_olay": 0, "karar": "RED_ON_KONTROLDE_KAPANDI",
            "not": "Bu kombinasyonda HIC aday-giris olusmadi - on-kontrol degerlendirilemez, otomatik RED.",
        }
    atr_event_median = float(np.median([c["atr_at_signal"] for c in all_cands]))
    slippage_est = 0.037 * atr_event_median  # H2/Tam-Tur-1 ile AYNI slippage/ATR referans-orani (kalibrasyon kaynagi: justin_backtest_onkontrol_standardi.md Madde 2)
    cost_pts_total = spread_median + slippage_est

    rows = []
    for tp_m in TP_MULT_GRID:
        tp_pts_repr = tp_m * atr_event_median
        ratio = tp_pts_repr / cost_pts_total if cost_pts_total > 0 else None
        rows.append({
            "tp_mult_atr": tp_m, "temsili_tp_pts": round(tp_pts_repr, 1),
            "maliyet_orani": round(ratio, 2) if ratio is not None else None,
            "gecti_mi_15x": bool(ratio is not None and ratio >= 15.0),
            "gecti_mi_20x": bool(ratio is not None and ratio >= 20.0),
        })
    survived = [r["tp_mult_atr"] for r in rows if r["gecti_mi_15x"]]
    karar = "ANA_TESTE_GECILEBILIR" if survived else "RED_ON_KONTROLDE_KAPANDI"
    print(f"[{label}] n_olay={len(all_cands)} spread_med={spread_median:.2f} atr_event_med={atr_event_median:.2f} "
          f"maliyet={cost_pts_total:.2f} karar={karar} gecen_tp={survived}")
    return {
        "label": label, "n_olay": len(all_cands),
        "spread_median_pts": round(spread_median, 2),
        "atr_event_median_pts": round(atr_event_median, 2),
        "slippage_tahmini_pts": round(slippage_est, 2),
        "toplam_maliyet_pts": round(cost_pts_total, 2),
        "hucre_bazinda_sonuc": rows, "on_kontrolu_gecen_tp_mult": survived,
        "karar": karar, "cost_pts_total_raw": cost_pts_total,
    }


COMBOS = [
    {"key": "M15_k10", "ltf": "M15", "k": 1.0, "label": "BIRINCIL: M15 giris, k=1.0x ATR14"},
    {"key": "M15_k05", "ltf": "M15", "k": 0.5, "label": "DUYARLILIK: M15 giris, k=0.5x ATR14"},
    {"key": "M5_k10", "ltf": "M5", "k": 1.0, "label": "IKINCIL/CAPRAZ-KONTROL: M5 giris, k=1.0x ATR14"},
]

combo_candidates = {}
combo_precheck = {}
for combo in COMBOS:
    ltf_name, k, key = combo["ltf"], combo["k"], combo["key"]
    all_cands = []
    per_htf_dir_counts = {}
    for htf_name in ("H1", "M30"):
        for direction in ("up", "down"):
            cs = build_momentum_candidates(ltf_name, htf_name, direction, k)
            all_cands.extend(cs)
            per_htf_dir_counts[f"{htf_name}_{direction}"] = len(cs)
    all_cands.sort(key=lambda x: x["exec_idx"])
    combo_candidates[key] = all_cands
    pre = s1_precheck(ltf_name, all_cands, combo["label"])
    pre["kombinasyon_bazinda_aday_sayisi"] = per_htf_dir_counts
    combo_precheck[key] = pre

results["faz4_aday_giris_ve_on_kontrol"] = {k: {kk: vv for kk, vv in v.items() if kk != "cost_pts_total_raw"}
                                             for k, v in combo_precheck.items()}
print("FAZ 4 tamamlandi.")

# ============================================================
# FAZ 6 (fonksiyon tanimlari - FAZ 5 split ile birlikte kombinasyon-basi kullanilacak)
# ============================================================


def floor_lot(x, step=LOT_STEP_USD):
    return math.floor(x / step) * step


def simulate_trades(ltf_name, candidates_subset, sl_mult, tp_mult, cost_pts_total, kasa=KASA_USD):
    """Tek-pozisyon sirali simulasyon (H2 ile BIREBIR AYNI mantik). candidates_subset exec_idx'e
    gore SIRALI olmali."""
    closes = CLOSES[ltf_name]
    opens = OPENS[ltf_name]
    highs = HIGHS[ltf_name]
    lows = LOWS[ltf_name]
    times = TIMES[ltf_name]
    n_total = len(closes)

    trades = []
    pos_open_until_idx = -1
    n_overlap_skipped = 0
    n_break_before_open = 0

    for cand in candidates_subset:
        entry_idx = cand["exec_idx"]
        if entry_idx <= pos_open_until_idx:
            n_overlap_skipped += 1
            continue

        direction = cand["direction"]
        sign = 1 if direction == "up" else -1
        atr_sig = cand["atr_at_signal"]
        if np.isnan(atr_sig) or atr_sig <= 0:
            continue
        sl_pts = sl_mult * atr_sig
        tp_pts = tp_mult * atr_sig
        entry_price = float(opens[entry_idx])
        break_known_t = cand["channel_break_known_time"]

        if int(times[entry_idx]) >= break_known_t:
            n_break_before_open += 1
            continue

        if sign == 1:
            sl_price = entry_price - sl_pts * POINT
            tp_price = entry_price + tp_pts * POINT
        else:
            sl_price = entry_price + sl_pts * POINT
            tp_price = entry_price - tp_pts * POINT

        exit_idx = None
        exit_reason = None
        exit_price = None
        j = entry_idx
        while j < n_total:
            t_j = int(times[j])
            bar_open_after_break = t_j >= break_known_t
            hi_, lo_ = float(highs[j]), float(lows[j])
            if sign == 1:
                sl_hit = lo_ <= sl_price
                tp_hit = hi_ >= tp_price
            else:
                sl_hit = hi_ >= sl_price
                tp_hit = lo_ <= tp_price

            if sl_hit:  # muhafazakar varsayim: ayni barda SL+TP varsa SL kazanir
                exit_idx, exit_reason, exit_price = j, "SL", sl_price
                break
            if tp_hit:
                exit_idx, exit_reason, exit_price = j, "TP", tp_price
                break
            if bar_open_after_break:
                exit_idx, exit_reason, exit_price = j, "KIRILIM_ERKEN_CIKIS", float(closes[j])
                break
            j += 1
        if exit_idx is None:
            exit_idx = n_total - 1
            exit_reason = "VERI_SONU_ACIK"
            exit_price = float(closes[exit_idx])

        gross_pnl_pts = sign * (exit_price - entry_price) / POINT
        net_pnl_pts = gross_pnl_pts - cost_pts_total

        lot = max(TABAN_LOT, floor_lot((kasa * RISK_PCT_UST_SINIR) / sl_pts))
        pnl_usd = net_pnl_pts * USD_PER_POINT_PER_LOT * lot

        hold_bars = exit_idx - entry_idx
        bar_min = TFS[ltf_name][1]
        trades.append({
            "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
            "entry_time": str(datetime.fromtimestamp(int(times[entry_idx]), tz=timezone.utc)),
            "exit_time": str(datetime.fromtimestamp(int(times[exit_idx]), tz=timezone.utc)),
            "direction": direction, "tf_source": cand["tf_source"],
            "sl_pts": round(sl_pts, 1), "tp_pts": round(tp_pts, 1),
            "exit_reason": exit_reason,
            "gross_pnl_pts": round(gross_pnl_pts, 2), "net_pnl_pts": round(net_pnl_pts, 2),
            "lot": round(lot, 2), "pnl_usd": round(pnl_usd, 4),
            "hold_bars": int(hold_bars), "hold_hours": round(hold_bars * bar_min / 60.0, 3),
            "split": cand.get("split"),
        })
        pos_open_until_idx = exit_idx

    return trades, n_overlap_skipped, n_break_before_open


def summarize_trades(trades):
    if not trades:
        return {"n_trades": 0}
    net_pts = np.array([t["net_pnl_pts"] for t in trades])
    pnl_usd = np.array([t["pnl_usd"] for t in trades])
    wins = net_pts > 0
    gross_profit = pnl_usd[pnl_usd > 0].sum()
    gross_loss = -pnl_usd[pnl_usd < 0].sum()
    pf = float(gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else None)

    equity = KASA_USD + np.cumsum(pnl_usd)
    running_max = np.maximum.accumulate(np.concatenate(([KASA_USD], equity)))[1:]
    drawdown = (running_max - equity) / running_max
    max_dd_pct = float(np.max(drawdown)) * 100 if len(drawdown) else 0.0

    hold_hours = np.array([t["hold_hours"] for t in trades])
    exit_reasons = {}
    for t in trades:
        exit_reasons[t["exit_reason"]] = exit_reasons.get(t["exit_reason"], 0) + 1

    # basit binom guven araligi (Wilson) win_rate icin - n kucukken genis araligi gorunur kilmak icin
    n = len(trades)
    p = float(np.mean(wins))
    z = 1.96
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    halfwidth = (z * math.sqrt((p * (1 - p) / n) + (z ** 2 / (4 * n ** 2)))) / denom
    wilson_lo, wilson_hi = max(0.0, center - halfwidth), min(1.0, center + halfwidth)

    return {
        "n_trades": n,
        "win_rate": round(p, 4),
        "win_rate_wilson_95ci": [round(wilson_lo, 4), round(wilson_hi, 4)],
        "profit_factor": round(pf, 4) if pf is not None and pf != float('inf') else pf,
        "net_profit_usd": round(float(pnl_usd.sum()), 2),
        "net_profit_pts": round(float(net_pts.sum()), 1),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "medyan_tutma_suresi_saat": round(float(np.median(hold_hours)), 2),
        "ortalama_tutma_suresi_saat": round(float(np.mean(hold_hours)), 2),
        "p10_p90_tutma_suresi_saat": [round(float(np.percentile(hold_hours, 10)), 2),
                                        round(float(np.percentile(hold_hours, 90)), 2)],
        "cikis_nedeni_dagilimi": exit_reasons,
    }


print("FAZ 6 fonksiyonlari tanimlandi.")

# ============================================================
# FAZ 5 + 7 + 8 + 9: HER KOMBINASYON ICIN AYRI AYRI YURUT
# ============================================================
kombinasyon_sonuclari = {}

for combo in COMBOS:
    key, ltf_name, k = combo["key"], combo["ltf"], combo["k"]
    print("=" * 70)
    print(f"KOMBINASYON: {combo['label']} ({key})")
    print("=" * 70)

    pre = combo_precheck[key]
    combo_out = {"label": combo["label"], "ltf": ltf_name, "k": k, "on_kontrol_madde2": {
        kk: vv for kk, vv in pre.items() if kk != "cost_pts_total_raw"}}

    if pre["karar"] != "ANA_TESTE_GECILEBILIR":
        combo_out["durum"] = "ELENDI_ON_KONTROLDE (Madde 2 - S1 maliyet-orani >=15x saglanamadi)"
        combo_out["ana_test_yapildi_mi"] = False
        kombinasyon_sonuclari[key] = combo_out
        print(f"[{key}] ON-KONTROLDE ELENDI - ana teste GECILMEDI.")
        continue

    cost_pts_total = pre["cost_pts_total_raw"]
    all_cands = combo_candidates[key]

    # ---- FAZ 5: split ----
    ltf_times = TIMES[ltf_name]
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])
    total_days = (ltf_t1 - ltf_t0) / 86400.0
    train_end_t = ltf_t0 + int(total_days * TRAIN_FRAC * 86400)
    val_start_t = train_end_t + EMBARGO_DAYS * 86400
    val_end_t = val_start_t + int(total_days * VAL_FRAC * 86400)
    test_start_t = val_end_t + EMBARGO_DAYS * 86400
    test_end_t = ltf_t1

    split_bounds = {
        "train": (ltf_t0, train_end_t),
        "validation": (val_start_t, val_end_t),
        "test": (test_start_t, test_end_t),
    }
    split_info = {}
    for kk, (a, b) in split_bounds.items():
        split_info[kk] = {"baslangic": str(datetime.fromtimestamp(a, tz=timezone.utc)),
                           "bitis": str(datetime.fromtimestamp(b, tz=timezone.utc)),
                           "gun": round((b - a) / 86400.0, 1)}
        print(f"  {kk}: {split_info[kk]['baslangic']} -> {split_info[kk]['bitis']} ({split_info[kk]['gun']} gun)")
    combo_out["faz5_split_sinirlari"] = split_info

    def split_of_time(t):
        for kk, (a, b) in split_bounds.items():
            if a <= t <= b:
                return kk
        return "embargo"

    for cand in all_cands:
        cand["split"] = split_of_time(int(ltf_times[cand["exec_idx"]]))
    split_counts = {kk: sum(1 for c in all_cands if c["split"] == kk) for kk in ("train", "validation", "test", "embargo")}
    combo_out["faz5_aday_giris_split_dagilimi"] = split_counts
    print(f"  aday-giris split dagilimi: {split_counts}")

    train_cands = [c for c in all_cands if c["split"] == "train"]
    val_cands = [c for c in all_cands if c["split"] == "validation"]
    test_cands = [c for c in all_cands if c["split"] == "test"]

    # ---- FAZ 7: walk-forward SL/TP kalibrasyonu ----
    survived_tp = pre["on_kontrolu_gecen_tp_mult"]
    grid_results = []
    for sl_m in SL_MULT_GRID:
        for tp_m in survived_tp:
            tr_trades, _, _ = simulate_trades(ltf_name, train_cands, sl_m, tp_m, cost_pts_total)
            va_trades, _, _ = simulate_trades(ltf_name, val_cands, sl_m, tp_m, cost_pts_total)
            tr_sum = summarize_trades(tr_trades)
            va_sum = summarize_trades(va_trades)
            grid_results.append({"sl_mult": sl_m, "tp_mult": tp_m, "train": tr_sum, "validation": va_sum})
            print(f"  SL={sl_m}xATR TP={tp_m}xATR -> Train(n={tr_sum.get('n_trades')}, "
                  f"PF={tr_sum.get('profit_factor')}) | Validation(n={va_sum.get('n_trades')}, "
                  f"PF={va_sum.get('profit_factor')})")
    combo_out["faz7_grid_tarama"] = grid_results

    eligible = [g for g in grid_results if g["validation"].get("n_trades", 0) >= MIN_TRADES_FOR_SELECTION
                and g["validation"].get("profit_factor") is not None]
    if eligible:
        best = max(eligible, key=lambda g: g["validation"]["profit_factor"])
        secim_notu = (f"Validation'da PF'ye gore secildi (n>={MIN_TRADES_FOR_SELECTION} sarti "
                      f"saglayan {len(eligible)} hucre arasindan).")
    else:
        candidates_by_n = [g for g in grid_results if g["validation"].get("n_trades", 0) > 0]
        if candidates_by_n:
            best = max(candidates_by_n, key=lambda g: g["validation"].get("n_trades", 0))
            secim_notu = (f"HICBIR hucre Validation'da n>={MIN_TRADES_FOR_SELECTION} esigini GECMEDI - "
                          f"en fazla islem sayisina sahip hucre secildi (n={best['validation']['n_trades']}), "
                          f"bu secim ZAYIF/dusuk-guvenilirlikli olarak isaretlenmelidir.")
        elif grid_results:
            best = grid_results[0]
            secim_notu = "Validation'da HICBIR hucrede islem olusmadi - ilk grid hucresi varsayilan olarak kullanildi (guvenilmez)."
        else:
            best = None
            secim_notu = "Grid tarama HICBIR hucre uretmedi (survived_tp bos) - beklenmeyen durum."

    if best is None:
        combo_out["faz7_secim"] = {"secim_notu": secim_notu}
        combo_out["durum"] = "GRID_BOS_HATA"
        kombinasyon_sonuclari[key] = combo_out
        continue

    SELECTED_SL_MULT, SELECTED_TP_MULT = best["sl_mult"], best["tp_mult"]
    print(f"  SECILEN: SL={SELECTED_SL_MULT}xATR14({ltf_name}), TP={SELECTED_TP_MULT}xATR14({ltf_name}) - {secim_notu}")
    combo_out["faz7_secim"] = {
        "secilen_sl_mult": SELECTED_SL_MULT, "secilen_tp_mult": SELECTED_TP_MULT,
        "secim_notu": secim_notu, "min_trades_esigi": MIN_TRADES_FOR_SELECTION,
    }

    test_trades, test_ov, test_brk = simulate_trades(ltf_name, test_cands, SELECTED_SL_MULT, SELECTED_TP_MULT, cost_pts_total)
    test_summary = summarize_trades(test_trades)

    train_trades_final, train_ov_f, train_brk_f = simulate_trades(ltf_name, train_cands, SELECTED_SL_MULT, SELECTED_TP_MULT, cost_pts_total)
    val_trades_final, val_ov_f, val_brk_f = simulate_trades(ltf_name, val_cands, SELECTED_SL_MULT, SELECTED_TP_MULT, cost_pts_total)
    train_summary_final = summarize_trades(train_trades_final)
    val_summary_final = summarize_trades(val_trades_final)

    all_cands_sorted = sorted(all_cands, key=lambda x: x["exec_idx"])
    full_trades, full_ov, full_brk = simulate_trades(ltf_name, all_cands_sorted, SELECTED_SL_MULT, SELECTED_TP_MULT, cost_pts_total)
    full_summary = summarize_trades(full_trades)
    print(f"  TEST: {test_summary}")
    print(f"  TAM DONEM: {full_summary}")

    combo_out["faz7_final_sonuclar"] = {
        "train": train_summary_final, "validation": val_summary_final, "test": test_summary,
        "tam_donem_birlesik": full_summary,
        "overlap_skipped": {"train": train_ov_f, "validation": val_ov_f, "test": test_ov, "tam_donem": full_ov},
        "kanal_kirilmis_giris_reddi": {"train": train_brk_f, "validation": val_brk_f, "test": test_brk, "tam_donem": full_brk},
    }

    # overfitting kontrolu: Train vs Test PF farki
    pf_train = train_summary_final.get("profit_factor")
    pf_test = test_summary.get("profit_factor")
    overfitting_flag = None
    if pf_train is not None and pf_test is not None:
        overfitting_flag = bool(abs(pf_train - pf_test) >= 0.3)
    combo_out["overfitting_kontrolu"] = {
        "pf_train": pf_train, "pf_test": pf_test,
        "OVERFITTING_RISKI": overfitting_flag,
        "not": "Fark >=0.3 PF birimi ise OVERFITTING_RISKI=True flag'lenir (basit esik, mutlak kanit degil).",
    }

    # ---- FAZ 8: kirilim-bazli-erken-cikis dogrulama ornekleri ----
    break_exit_trades = [t for t in full_trades if t["exit_reason"] == "KIRILIM_ERKEN_CIKIS"]
    combo_out["faz8_kirilim_erken_cikis_dogrulama"] = {
        "toplam_kirilim_cikisi": len(break_exit_trades), "toplam_islem_tam_donem": len(full_trades),
        "oran": round(len(break_exit_trades) / len(full_trades), 4) if full_trades else None,
        "ornek_islemler": [{"entry_time": t["entry_time"], "exit_time": t["exit_time"],
                             "direction": t["direction"], "tf_source": t["tf_source"],
                             "hold_hours": t["hold_hours"], "net_pnl_pts": t["net_pnl_pts"]}
                            for t in break_exit_trades[:5]],
    }

    # ---- FAZ 9: islem frekansi + kirilim analizi ----
    if full_trades:
        entry_dates = [datetime.fromisoformat(t["entry_time"]).date() for t in full_trades]
        n_months = max(1, (entry_dates[-1].year - entry_dates[0].year) * 12 +
                       (entry_dates[-1].month - entry_dates[0].month) + 1)
        n_years = (entry_dates[-1] - entry_dates[0]).days / 365.25 if len(entry_dates) > 1 else 1.0
        trades_per_month = len(full_trades) / n_months
        trades_per_year = len(full_trades) / n_years if n_years > 0 else None
    else:
        trades_per_month, trades_per_year = None, None

    kirilim_tf, kirilim_yon = {}, {}
    for t in full_trades:
        kirilim_tf.setdefault(t["tf_source"], []).append(t["net_pnl_pts"])
        kirilim_yon.setdefault(t["direction"], []).append(t["net_pnl_pts"])

    def group_summary(d):
        out = {}
        for kk, v in d.items():
            arr = np.array(v)
            wins = arr > 0
            gp = arr[arr > 0].sum()
            gl = -arr[arr < 0].sum()
            out[kk] = {"n": len(arr), "win_rate": round(float(np.mean(wins)), 4),
                       "profit_factor_pts_bazli": round(float(gp / gl), 4) if gl > 0 else None,
                       "net_pts": round(float(arr.sum()), 1)}
        return out

    combo_out["faz9_islem_frekansi"] = {
        "islem_ay_sayisi_tam_donem": round(trades_per_month, 2) if trades_per_month else None,
        "islem_yil_sayisi_tam_donem": round(trades_per_year, 2) if trades_per_year else None,
        "toplam_islem_tam_donem": len(full_trades),
    }
    combo_out["faz9_kirilim_tf_kaynagi"] = group_summary(kirilim_tf)
    combo_out["faz9_kirilim_yon"] = group_summary(kirilim_yon)
    combo_out["islem_logu_ornek"] = full_trades[:15] + (full_trades[-15:] if len(full_trades) > 15 else [])
    combo_out["ana_test_yapildi_mi"] = True
    combo_out["durum"] = "TAMAMLANDI"

    kombinasyon_sonuclari[key] = combo_out

    if full_trades:
        pd.DataFrame(full_trades).to_csv(
            rf"C:\MilaYatirim\mila-yatirim-sistemi\Justin\backtest_H4_{key}_islem_logu_tam.csv",
            index=False, encoding="utf-8-sig")
        print(f"  [{key}] Tam islem logu CSV yazildi.")

results["kombinasyon_sonuclari"] = kombinasyon_sonuclari

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)

mt5.shutdown()
print("BITTI.")
