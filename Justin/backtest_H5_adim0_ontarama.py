# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - A Ailesi (Tur 2, Adim 2) - HIPOTEZ H5
"Kanal-Disi Kirilim Girisi" - ADIM 0: ZORUNLU ON-TARAMA (olay-sayimi)

Kaynak gorev: Orkestrator cagrisi (19 Temmuz 2026, 09:20).
ONEMLI NOT (izolasyon/kaynak seffafligi icin acikca belirtilmeli): Bu gorevin "dogrudan
kaynagi" olarak belirtilen dosya - stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_
adim1_20260719.md ("HIPOTEZ H5 bolumu + BACKTEST MUHENDISI ICIN NOTLAR 1-10") - bu calisma
dizininde (C:\\MilaYatirim\\Justin\\) BULUNAMADI (dosya sistemi kontrol edildi, mevcut degil).
Bu script SADECE Orkestrator cagrisinin kendi icindeki ADIM 0 tanimina dayanmaktadir (bu
tanim, olay tasma esigi, HTF/LTF/yon kombinasyonlari, ATR14 M15 esigi dahil, cagrida
tam olarak verilmisti). Kanal (pivot/swing/dokunus/EMA-MACD) tanimi Tam Tur 1'den
(stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md) ve H2/H3 backtest
scriptlerinden (metodolojik olarak) degistirilmeden alinmistir - bu, ayni-proje-ici
tutarlilik amaclidir, izolasyon ihlali degildir.

YENI TASARIM UNSURU (Stratejist tarafindan tanimlanmamis, kaynak dosya eksik oldugu icin
bu script tarafindan ACIKCA tasarlanmistir - asagida "KANAL GENISLIGI / DIS SINIR TANIMI"
bolumunde belgelenmistir): H2/H3 kanal algoritmasi yalniz TEK bir cizgi (trend cizgisi -
yukselen kanalda alt/destek cizgisi, alcalan kanalda ust/direnc cizgisi) uretir. H5,
kanalin TREND-YONUNDEKI DIS SINIRINI (yukselen kanalda UST, alcalan kanalda ALT) gerektirir
- bu, orijinal H2/H3 algoritmasinda mevcut degildi. Bu script bu disi siniri, kanalin
OLUSUM penceresinde (anchor->3.dokunus/onay bari) ZIT yondeki fiyat uc noktalarinin
(yukselen kanalda high, alcalan kanalda low) trend cizgisine olan MAKSIMUM dikey
uzakligi olarak tanimlar ve bunu onay sonrasi sabit genislik olarak projekte eder. Bu
bir VARSAYIMdir, Stratejist onayina sunulmalidir (asagida uyarilar bolumunde tekrarlanir).

Kapsam: SADECE ADIM 0 (olay-sayimi/S1-proxy on-tarama). ADIM 1-3 (on-kontrol/ana test)
bu on-tarama sonucu "yeterli" cikarsa AYRI bir script/gorevde yapilir.
"""
import json
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timezone

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_H5_adim0_ontarama_output.json"

# ============================================================
# SABITLER (Tam Tur 1 / H2-H3 ile AYNI - kanal tanimi degistirilmedi)
# ============================================================
SYMBOL = "GOLD"
MIN_TOUCHES = 3            # kanal gecerlilik esigi
TOUCH_K = 0.5               # dokunus toleransi: 0.5 x ATR14
SWING_N = 5                 # fraktal pivot penceresi (N=5 sag-pencereli)
LOOKAHEAD_LAG_BARS = 5      # swing, olustugu bardan 5 bar SONRA "bilinir" (look-ahead duzeltmesi)
CAP_DAYS = 300              # kanal arama penceresi sinirlamasi
EMA_FAST, EMA_SLOW = 50, 200
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9

# H5'E OZEL (Orkestrator cagrisinda ACIKCA verilen ADIM 0 esigi):
TASMA_ESIK_ATR_MULT = 0.5   # kirilim barinin kapanisi, DIS sinirin en az 0,5xATR14(LTF) DISINDA olmali

print("=" * 70)
print("FAZ 0: MT5 BAGLANTI + HAM VERI (H1, M30, M15, M5)")
print("=" * 70)
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point

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

results = {
    "meta": {
        "hipotez_adi": "A Ailesi H5 - Kanal-Disi Kirilim Girisi - ADIM 0 ON-TARAMA",
        "kaynak_dosya_eksik_uyarisi": (
            "stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md dosyasi "
            "C:\\MilaYatirim\\Justin\\ icinde BULUNAMADI - bu script yalniz Orkestrator "
            "cagrisinin ADIM 0 tanimina ve Tam Tur 1/H2-H3'un kanal tanimina dayanmaktadir."
        ),
        "min_touches": MIN_TOUCHES, "touch_k": TOUCH_K, "swing_n": SWING_N,
        "lookahead_lag_bars": LOOKAHEAD_LAG_BARS, "cap_days": CAP_DAYS,
        "tasma_esik_atr_mult": TASMA_ESIK_ATR_MULT,
    },
    "veri_araligi": {tf: {"n_bar": int(len(raw[tf])),
                           "baslangic": str(datetime.fromtimestamp(int(raw[tf][0]['time']), tz=timezone.utc)),
                           "bitis": str(datetime.fromtimestamp(int(raw[tf][-1]['time']), tz=timezone.utc))}
                     for tf in TFS}
}


# ============================================================
# ORTAK YARDIMCI FONKSIYONLAR (H2/H3 ile ayni)
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


ATR = {tf: atr_series_pts(raw[tf]) for tf in TFS}
EMA50 = {tf: ema(raw[tf]['close'].astype(float), EMA_FAST) for tf in TFS}
EMA200 = {tf: ema(raw[tf]['close'].astype(float), EMA_SLOW) for tf in TFS}
MACD_LINE, MACD_SIG_ARR = {}, {}
for tf in TFS:
    ml, sl_ = macd(raw[tf]['close'].astype(float))
    MACD_LINE[tf] = ml
    MACD_SIG_ARR[tf] = sl_

SWINGS = {}
for tf in ("H1", "M30"):
    sh, sl_ = find_swings(raw[tf])
    SWINGS[tf] = {"swing_high": sh, "swing_low": sl_}
    print(tf, "swing_high n=", int(sh.sum()), "swing_low n=", int(sl_.sum()))

# ============================================================
# FAZ 2: PIVOT/KANAL TESPITI (H2/H3 ile BIREBIR AYNI ALGORITMA)
#   + KANAL GENISLIGI / DIS SINIR HESABI (YENI, bu scripte ozel - bkz. ust yorum)
# ============================================================
print("=" * 70)
print("FAZ 2: PIVOT/KANAL TESPITI + DIS SINIR (KANAL GENISLIGI) HESABI")
print("=" * 70)

CAP_MINUTES = CAP_DAYS * 24 * 60


def detect_channels(tf_name, direction):
    rates = raw[tf_name]
    bar_min = TFS[tf_name][1]
    closes = rates['close'].astype(float)
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    times = rates['time'].astype(np.int64)
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
        opposite_arr = highs   # DIS sinir (ust) icin karsi-uc: high
    else:
        sign = -1
        swing_mask = SWINGS[tf_name]["swing_high"]
        price_arr = highs
        opposite_arr = lows    # DIS sinir (alt) icin karsi-uc: low

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
                break
            elif abs(diff) <= tol:
                touches.append(c)
                if len(touches) >= MIN_TOUCHES and confirm_idx is None:
                    confirm_idx = c
            k += 1

        if confirm_idx is None:
            pos += 1
            continue

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

        # --- YENI: KANAL GENISLIGI / DIS SINIR (bkz. ust dosya-basi yorumu) ---
        # Olusum penceresi: anchor -> confirm_idx_ham (ham 3.dokunus bari), bu ana kadarki
        # veriyle hesaplanir (confirmed_active_idx'ten ONCESI, look-ahead YARATMAZ - genislik
        # zaten confirmed_active_idx'te "bilinir" durumda olacak sekilde anchor..confirm_idx_ham
        # araligindan turetiliyor).
        form_lo, form_hi = anchor, confirm_idx
        seg = np.arange(form_lo, form_hi + 1)
        proj_seg = anchor_price + slope * (seg - anchor)
        opp_seg = opposite_arr[form_lo:form_hi + 1]
        width_candidates = sign * (opp_seg - proj_seg)
        genislik = float(max(0.0, np.nanmax(width_candidates))) if len(width_candidates) else 0.0

        channels.append({
            "tf": tf_name, "direction": direction,
            "anchor_idx": int(anchor), "second_idx": int(second),
            "confirm_idx_ham": int(confirm_idx),
            "confirmed_active_idx": int(confirmed_active_idx),
            "break_idx": int(break_idx),
            "n_touches_total": int(len(touches)), "slope_price_per_bar": float(slope),
            "anchor_time": int(anchor_time),
            "confirmed_active_time": int(times[confirmed_active_idx]),
            "break_time": int(times[break_idx]),
            "break_known_time": int(break_known_time),
            "anchor_price": float(anchor_price),
            "genislik_price": genislik,               # DIS sinir - trend cizgisi mesafesi (fiyat birimi)
            "genislik_pts": round(genislik / POINT, 1),
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
        print(tf_name, direction, "onaylanmis kanal sayisi:", len(chs),
              "| medyan genislik (pts):",
              round(float(np.median([c["genislik_pts"] for c in chs])), 1) if chs else None)

results["faz2_kanal_sayilari"] = {
    tf: {d: len(channels_all[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")
}
results["faz2_kanal_genislik_ozet_pts"] = {
    tf: {d: {
        "n": len(channels_all[tf][d]),
        "medyan": round(float(np.median([c["genislik_pts"] for c in channels_all[tf][d]])), 1) if channels_all[tf][d] else None,
        "min": round(float(np.min([c["genislik_pts"] for c in channels_all[tf][d]])), 1) if channels_all[tf][d] else None,
        "maks": round(float(np.max([c["genislik_pts"] for c in channels_all[tf][d]])), 1) if channels_all[tf][d] else None,
    } for d in ("up", "down")} for tf in ("H1", "M30")
}

# ============================================================
# ADIM 0: TASMA OLAYI SAYIMI (HTF x LTF x yon kombinasyonu)
#   LTF birincil: M15 (Orkestrator cagrisinda acikca M15 belirtilmis)
#   LTF ikincil/capraz-kontrol: M5 (ADIM 3 tanimindaki M5 rolune tutarli, bilgi amacli)
# ============================================================
print("=" * 70)
print("ADIM 0: TASMA OLAYI SAYIMI")
print("=" * 70)


def count_tasma_events(channels_htf, ltf_name):
    ltf_times = raw[ltf_name]['time'].astype(np.int64)
    ltf_closes = raw[ltf_name]['close'].astype(float)
    ltf_atr = ATR[ltf_name]
    n_ltf = len(ltf_closes)
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    total_events = 0
    n_channels_with_overlap = 0
    n_channels_with_event = 0
    per_channel_detail = []

    for c in channels_htf:
        conf_t = c["confirmed_active_time"]
        brk_t = c["break_known_time"]
        if brk_t < ltf_t0 or conf_t > ltf_t1 or c["genislik_price"] <= 0:
            continue
        win_start = max(conf_t, ltf_t0)
        win_end = min(brk_t, ltf_t1)
        lo = np.searchsorted(ltf_times, win_start, side="left")
        hi = np.searchsorted(ltf_times, win_end, side="right")
        if hi - lo < 2:
            continue
        n_channels_with_overlap += 1

        sign = 1 if c["direction"] == "up" else -1
        anchor_price = c["anchor_price"]
        anchor_time = c["anchor_time"]
        bar_min_htf = TFS[c["tf"]][1]
        slope_per_sec = c["slope_price_per_bar"] / (bar_min_htf * 60)
        genislik = c["genislik_price"]

        was_tasma = False
        n_events_this_channel = 0
        for i in range(lo, hi):
            if np.isnan(ltf_atr[i]):
                was_tasma = False
                continue
            t_i = int(ltf_times[i])
            trendline_i = anchor_price + slope_per_sec * (t_i - anchor_time)
            outer_boundary_i = trendline_i + sign * genislik
            esik = TASMA_ESIK_ATR_MULT * ltf_atr[i] * POINT
            disari_mesafe = sign * (ltf_closes[i] - outer_boundary_i)  # pozitifse DIS sinirin disinda (trend yonunde)
            is_tasma = disari_mesafe >= esik
            if is_tasma and not was_tasma:
                n_events_this_channel += 1
            was_tasma = is_tasma

        total_events += n_events_this_channel
        if n_events_this_channel > 0:
            n_channels_with_event += 1
        per_channel_detail.append({
            "anchor_time_utc": str(datetime.fromtimestamp(c["anchor_time"], tz=timezone.utc)),
            "confirmed_active_time_utc": str(datetime.fromtimestamp(conf_t, tz=timezone.utc)),
            "break_known_time_utc": str(datetime.fromtimestamp(brk_t, tz=timezone.utc)),
            "genislik_pts": c["genislik_pts"],
            "n_tasma_olayi": n_events_this_channel,
            "censored": c["censored_veri_sonu"],
        })

    return {
        "toplam_tasma_olayi": total_events,
        "kanal_sayisi_ltf_ile_ortusen": n_channels_with_overlap,
        "kanal_sayisi_en_az_1_olayli": n_channels_with_event,
        "detay": per_channel_detail,
    }


adim0_ozet = {}
toplam_genel_m15 = 0
for tf_name in ("H1", "M30"):
    for direction in ("up", "down"):
        for ltf_name in ("M15", "M5"):
            key = f"{tf_name}_{direction}_{ltf_name}"
            res = count_tasma_events(channels_all[tf_name][direction], ltf_name)
            adim0_ozet[key] = res
            if ltf_name == "M15":
                toplam_genel_m15 += res["toplam_tasma_olayi"]
            print(f"{tf_name} {direction} -> {ltf_name}: kanal(ortusen)={res['kanal_sayisi_ltf_ile_ortusen']}, "
                  f"kanal(>=1 olay)={res['kanal_sayisi_en_az_1_olayli']}, TOPLAM OLAY={res['toplam_tasma_olayi']}")

results["adim0_tasma_olayi_sayimi"] = adim0_ozet
results["adim0_toplam_olay_m15_tum_kombinasyonlar"] = toplam_genel_m15
toplam_genel_m5 = sum(v["toplam_tasma_olayi"] for k, v in adim0_ozet.items() if k.endswith("_M5"))
results["adim0_toplam_olay_m5_tum_kombinasyonlar"] = toplam_genel_m5

print("=" * 70)
print(f"TOPLAM TASMA OLAYI (M15, tum HTF/yon kombinasyonlari toplami): {toplam_genel_m15}")
print(f"TOPLAM TASMA OLAYI (M5, tum HTF/yon kombinasyonlari toplami): {toplam_genel_m5}")
print("=" * 70)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)

mt5.shutdown()
print("BITTI.")
