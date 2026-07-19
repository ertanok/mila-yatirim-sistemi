# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - A Ailesi (Tur 2, Adim 2) - HIPOTEZ H5
"Kanal-Disi Kirilim Girisi" - ADIM 1 (ON-KONTROL) + ADIM 2 (LOOK-AHEAD) + ADIM 3 (ANA TEST)

Onkosul: Bu script SADECE ADIM 0 (backtest_H5_adim0_ontarama.py) "devam et" kararindan SONRA
calistirilir. ADIM 0 sonucu: M15'te toplam 748 tasma olayi (4 HTF/yon kombinasyonunun HER
BIRINDE 100-251 arasi, tek haneli DEGIL) -> devam kararı verildi (bkz. backtest_muhendisi_
raporu_..._H5_20260719.md, "On-Tarama Sonucu" bolumu).

KAYNAK DOSYA EKSIKLIGI (tekrar, ADIM 0 scriptindeki ayni uyari): stratejici_raporu_justin_
gold_scalping_A_ailesi_tur2_adim1_20260719.md bulunamadi. Bu script Orkestrator cagrisinin
ADIM 1/2/3 tanimina ve Tam Tur 1 + H2/H3'un ortak metodolojisine (kanal tanimi, DST-kontrolu,
S1 maliyet-orani, train/val/test purge/embargo, walk-forward SL/TP secimi) dayanmaktadir.
Kanal genisligi/DIS SINIR tanimi ADIM 0 scriptiyle AYNI (bu script tarafindan tasarlandi,
Stratejist onayina sunulur - bkz. rapor).

Kapsam (FAZ'lar):
  FAZ 0: MT5 veri
  FAZ 1: ON-KONTROL Madde 1 - DST/saat-esleme BAGIMSIZ dogrulama
  FAZ 2: Kanal tespiti + DIS sinir (ADIM 0 ile birebir ayni algoritma)
  FAZ 3: M15 (birincil) tasma-olayi aday-giris tespiti (LOOK-AHEAD-SAFE) + M5 (ikincil/capraz)
  FAZ 4: N-bar-ileri medyan hareket olcumu (TP kalibrasyonu icin baglam, TRAIN-only)
  FAZ 5: ON-KONTROL Madde 2 - S1 maliyet-orani (GERCEK SL/TP mesafeleriyle)
  FAZ 6: Train/Validation/Test ayrimi (purged/embargolu)
  FAZ 7: Trade simulasyonu (giris=kirilim barinin KENDI kapanisi; cikis: SL-false-breakout /
         TP-ATR-dinamik / kanala-geri-donus-erken-cikis)
  FAZ 8: Walk-forward SL/TP kalibrasyonu (Train->Validation sec, Test TEK KEZ)
  FAZ 9: False-breakout sikligi + islem frekansi + kirilim analizi + JSON/CSV kaydi

Izolasyon: Yalniz C:\\MilaYatirim\\Justin\\ icinde calisilmistir, veri dogrudan MT5 GOLD'dan.
MilaGold/Lisa/Signal GPT'ye ait hicbir dosya/deger/format referans alinmamistir.
"""
import json
import math
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_H5_main_output.json"
CSV_PATH = r"C:\MilaYatirim\Justin\backtest_H5_islem_logu_tam.csv"

# ============================================================
# SABITLER
# ============================================================
SYMBOL = "GOLD"
MIN_TOUCHES = 3
TOUCH_K = 0.5
SWING_N = 5
LOOKAHEAD_LAG_BARS = 5
CAP_DAYS = 300
EMA_FAST, EMA_SLOW = 50, 200
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9

TASMA_ESIK_ATR_MULT = 0.5   # ADIM 0 ile ayni tanim - kanal aktifken giris icin de bu esik kullanilir

# H5'e ozel grid'ler (Orkestrator cagrisi: SL ~0,3-0,5xATR14; TP grid asagida FAZ4 olcumune gore)
SL_MULT_GRID = [0.3, 0.4, 0.5]
TP_MULT_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
MFE_HORIZONS_BARS = [4, 8, 16, 24, 48]   # 1/2/4/6/12 saat (M15) - N-bar-ileri olcum icin

KASA_USD = 2000.0
RISK_PCT_UST_SINIR = 0.01
TABAN_LOT = 0.01
LOT_STEP_USD = 0.01

EMBARGO_DAYS = 45
TRAIN_FRAC, VAL_FRAC = 0.50, 0.25
MIN_TRADES_FOR_SELECTION = 30

DST_TRANSITIONS = ["2025-03-30", "2025-10-26", "2026-03-29"]

print("=" * 70)
print("FAZ 0: MT5 BAGLANTI + HAM VERI")
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
    "hipotez_adi": "A Ailesi H5 - Kanal-Disi Kirilim Girisi (ADIM 1-3)",
    "kaynak_dosya_eksik_uyarisi": (
        "stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md BULUNAMADI - "
        "bu script Orkestrator cagrisinin ADIM1-3 tanimina ve Tam Tur 1/H2-H3 metodolojisine "
        "dayanmaktadir. Kanal genisligi/DIS SINIR tanimi bu gorevde ozel tasarlanmistir."
    ),
    "min_touches": MIN_TOUCHES, "touch_k": TOUCH_K, "swing_n": SWING_N,
    "lookahead_lag_bars": LOOKAHEAD_LAG_BARS, "cap_days": CAP_DAYS,
    "tasma_esik_atr_mult": TASMA_ESIK_ATR_MULT,
    "sl_mult_grid": SL_MULT_GRID, "tp_mult_grid": TP_MULT_GRID,
    "kasa_usd": KASA_USD, "risk_pct_ust_sinir": RISK_PCT_UST_SINIR, "taban_lot": TABAN_LOT,
    "embargo_days": EMBARGO_DAYS,
}}
results["veri_araligi"] = {tf: {"n_bar": int(len(raw[tf])),
                                 "baslangic": str(datetime.fromtimestamp(int(raw[tf][0]['time']), tz=timezone.utc)),
                                 "bitis": str(datetime.fromtimestamp(int(raw[tf][-1]['time']), tz=timezone.utc))}
                           for tf in TFS}

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
print("H1 DST kontrolu:", dst_h1["dst_kontrolu"])
print("M15 DST kontrolu:", dst_m15["dst_kontrolu"])

results["faz1_on_kontrol_dst"] = {
    "canli_capraz_kontrol": {"epoch_utc_okuma": str(epoch_as_utc), "vps_yerel_simdi": str(vps_local_now),
                              "fark_saniye": diff_seconds},
    "H1": dst_h1, "M15": dst_m15,
    "sonuc_notu": ("H5 icin BAGIMSIZ olarak (H2/H3'ten devralinmadan) yeniden kosturuldu. "
                   "H2/H3'teki 5. bagimsiz teyitle TUTARLI olup olmadigi asagidaki H1/M15 "
                   "kayma sonuclarindan okunmalidir."),
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

# ============================================================
# FAZ 2: KANAL TESPITI + DIS SINIR (ADIM 0 ile BIREBIR AYNI)
# ============================================================
print("=" * 70)
print("FAZ 2: PIVOT/KANAL TESPITI + DIS SINIR (KANAL GENISLIGI)")
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
        opposite_arr = highs
    else:
        sign = -1
        swing_mask = SWINGS[tf_name]["swing_high"]
        price_arr = highs
        opposite_arr = lows

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
            "genislik_price": genislik,
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
        print(tf_name, direction, "onaylanmis kanal sayisi:", len(chs))

results["faz2_kanal_sayilari"] = {
    tf: {d: len(channels_all[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")
}

# ============================================================
# FAZ 3: M15 (BIRINCIL) + M5 (IKINCIL) TASMA-OLAYI ADAY-GIRIS TESPITI
#   LOOK-AHEAD-SAFE: genislik anchor..confirm_idx_ham'dan (confirmed_active_idx'ten ONCE
#   bilinen veri) turetiliyor; tasma taramasi confirmed_active_time'dan BASLIYOR. Giris,
#   kirilim barinin KENDI kapanisinda (TEK bar tetigi) - bu, kirilim tespitinin kendisinin
#   GERCEK ZAMANLI oldugu anlamina gelir (5-bar-gecikme SADECE kanalin/genisligin
#   BILINIRLIGINE aittir, kirilim ANINA degil - bkz. rapor "Look-Ahead Bias Dogrulamasi").
# ============================================================
print("=" * 70)
print("FAZ 3: TASMA-OLAYI ADAY-GIRIS TESPITI (M15 birincil, M5 ikincil)")
print("=" * 70)


def find_breakout_candidates(channels_htf, ltf_name):
    ltf_times = raw[ltf_name]['time'].astype(np.int64)
    ltf_closes = raw[ltf_name]['close'].astype(float)
    ltf_atr = ATR[ltf_name]
    n_ltf = len(ltf_closes)
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    candidates = []
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

        sign = 1 if c["direction"] == "up" else -1
        anchor_price = c["anchor_price"]
        anchor_time = c["anchor_time"]
        bar_min_htf = TFS[c["tf"]][1]
        slope_per_sec = c["slope_price_per_bar"] / (bar_min_htf * 60)
        genislik = c["genislik_price"]

        was_tasma = False
        for i in range(lo, hi):
            if np.isnan(ltf_atr[i]):
                was_tasma = False
                continue
            t_i = int(ltf_times[i])
            trendline_i = anchor_price + slope_per_sec * (t_i - anchor_time)
            outer_boundary_i = trendline_i + sign * genislik
            esik = TASMA_ESIK_ATR_MULT * ltf_atr[i] * POINT
            disari_mesafe = sign * (ltf_closes[i] - outer_boundary_i)
            is_tasma = disari_mesafe >= esik
            if is_tasma and not was_tasma:
                candidates.append({
                    "exec_idx": i, "direction": c["direction"],
                    "atr_at_signal": float(ltf_atr[i]),
                    "outer_boundary_at_entry": float(outer_boundary_i),
                    "channel": c, "ltf": ltf_name,
                })
            was_tasma = is_tasma

    return candidates


m15_candidates_by_combo = {}
all_m15_candidates = []
for tf_name in ("H1", "M30"):
    for direction in ("up", "down"):
        cands = find_breakout_candidates(channels_all[tf_name][direction], "M15")
        m15_candidates_by_combo[f"{tf_name}_{direction}"] = len(cands)
        all_m15_candidates.extend(cands)
all_m15_candidates.sort(key=lambda x: x["exec_idx"])
print("M15 (birincil) toplam aday-giris:", len(all_m15_candidates), m15_candidates_by_combo)

m5_candidates_by_combo = {}
all_m5_candidates = []
for tf_name in ("H1", "M30"):
    for direction in ("up", "down"):
        cands = find_breakout_candidates(channels_all[tf_name][direction], "M5")
        m5_candidates_by_combo[f"{tf_name}_{direction}"] = len(cands)
        all_m5_candidates.extend(cands)
all_m5_candidates.sort(key=lambda x: x["exec_idx"])
print("M5 (ikincil/capraz-kontrol) toplam aday-giris:", len(all_m5_candidates), m5_candidates_by_combo)

results["faz3_aday_giris_sayilari"] = {
    "M15_birincil": {"kombinasyon_bazinda": m15_candidates_by_combo, "toplam": len(all_m15_candidates)},
    "M5_ikincil_capraz_kontrol": {"kombinasyon_bazinda": m5_candidates_by_combo, "toplam": len(all_m5_candidates)},
}
print("FAZ 3 tamamlandi.")

# ============================================================
# ORTAK: LTF (M15/M5) dizileri (trade simulasyonu icin)
# ============================================================
m15_times = raw["M15"]['time'].astype(np.int64)
m15_closes = raw["M15"]['close'].astype(float)
m15_highs = raw["M15"]['high'].astype(float)
m15_lows = raw["M15"]['low'].astype(float)
m15_atr = ATR["M15"]
m15_spread = raw["M15"]['spread'].astype(float)
N_M15 = len(m15_closes)

# ============================================================
# FAZ 4: N-BAR-ILERI MEDYAN HAREKET OLCUMU (TP baglami - TRAIN split ile sinirli, asagida
#   split sinirlari hesaplandiktan SONRA calisir - bu yuzden FAZ 6'nin ARDINDAN cagrilacak,
#   burada sadece fonksiyon tanimlaniyor)
# ============================================================


def measure_mfe(cands, horizons=MFE_HORIZONS_BARS):
    """Her aday icin, giris barindan itibaren N bar ileri, TREND YONUNDE maksimum lehte
    hareketi (MFE) ATR-birim cinsinden olcer. Sadece BAGLAM/kalibrasyon amaclidir (TRAIN
    split ile sinirlanarak cagrilmalidir - asagida FAZ 6 sonrasi TRAIN adaylariyla cagrilir)."""
    out = {h: [] for h in horizons}
    for cand in cands:
        i0 = cand["exec_idx"]
        sign = 1 if cand["direction"] == "up" else -1
        atr0 = cand["atr_at_signal"]
        if np.isnan(atr0) or atr0 <= 0:
            continue
        entry_price = m15_closes[i0]
        for h in horizons:
            i1 = min(N_M15 - 1, i0 + h)
            if i1 <= i0:
                continue
            seg_highs = m15_highs[i0 + 1:i1 + 1]
            seg_lows = m15_lows[i0 + 1:i1 + 1]
            if len(seg_highs) == 0:
                continue
            if sign == 1:
                mfe_pts = (seg_highs.max() - entry_price) / POINT
            else:
                mfe_pts = (entry_price - seg_lows.min()) / POINT
            out[h].append(mfe_pts / atr0)
    return {h: {"n": len(v), "medyan_atr_mult": round(float(np.median(v)), 3) if v else None}
            for h, v in out.items()}


# ============================================================
# FAZ 5: ON-KONTROL MADDE 2 - S1 MALIYET-ORANI (fonksiyon, split sonrasi cagrilacak)
# ============================================================
atr_m15_median = float(np.nanmedian(m15_atr))
spread_m15_median = float(np.median(m15_spread))
slippage_est_m15 = 0.037 * atr_m15_median   # H2/H3 ile ayni kalibrasyon referansi (izolasyon: ayni-proje-ici)
cost_pts_total = spread_m15_median + slippage_est_m15
print(f"M15: spread_median={spread_m15_median:.2f}, ATR14_median={atr_m15_median:.2f}, "
      f"slippage_est={slippage_est_m15:.2f}, TOPLAM_MALIYET={cost_pts_total:.2f} pts")

precheck_rows = []
for tp_m in TP_MULT_GRID:
    tp_pts_repr = tp_m * atr_m15_median
    ratio = tp_pts_repr / cost_pts_total
    precheck_rows.append({
        "tp_mult_atr": tp_m, "temsili_tp_pts": round(tp_pts_repr, 1),
        "maliyet_orani": round(ratio, 2),
        "gecti_mi_15x": bool(ratio >= 15.0), "gecti_mi_20x": bool(ratio >= 20.0),
    })
    print(f"  TP={tp_m}xATR ({tp_pts_repr:.1f}pts) -> oran={ratio:.2f}x "
          f"[15x:{'GECTI' if ratio>=15 else 'KALDI'} / 20x:{'GECTI' if ratio>=20 else 'KALDI'}]")

TP_MULT_SURVIVED = [r["tp_mult_atr"] for r in precheck_rows if r["gecti_mi_15x"]]
print("On-kontrolu (>=15x) GECEN TP carpanlari:", TP_MULT_SURVIVED)

results["faz5_on_kontrol_maliyet_orani"] = {
    "spread_median_pts": round(spread_m15_median, 2),
    "atr14_median_pts": round(atr_m15_median, 2),
    "slippage_tahmini_pts": round(slippage_est_m15, 2),
    "toplam_maliyet_pts": round(cost_pts_total, 2),
    "sl_mult_grid": SL_MULT_GRID, "tp_mult_grid": TP_MULT_GRID,
    "hucre_bazinda_sonuc": precheck_rows,
    "on_kontrolu_gecen_tp_mult": TP_MULT_SURVIVED,
    "karar": "ANA_TESTE_GECILEBILIR" if TP_MULT_SURVIVED else "RED_ON_KONTROLDE_KAPANDI",
}
print("FAZ 5 tamamlandi. Karar:", results["faz5_on_kontrol_maliyet_orani"]["karar"])
assert TP_MULT_SURVIVED, "H5 on-kontrolde elendi (S1 >=15x hicbir TP carpaninda saglanamiyor)."

# ============================================================
# FAZ 6: TRAIN / VALIDATION / TEST AYRIMI (purged/embargolu, zaman-bazli)
# ============================================================
print("=" * 70)
print("FAZ 6: TRAIN / VALIDATION / TEST AYRIMI")
print("=" * 70)

m15_t0, m15_t1 = int(m15_times[0]), int(m15_times[-1])
total_days = (m15_t1 - m15_t0) / 86400.0
train_end_t = m15_t0 + int(total_days * TRAIN_FRAC * 86400)
val_start_t = train_end_t + EMBARGO_DAYS * 86400
val_end_t = val_start_t + int(total_days * VAL_FRAC * 86400)
test_start_t = val_end_t + EMBARGO_DAYS * 86400
test_end_t = m15_t1

split_bounds = {
    "train": (m15_t0, train_end_t),
    "validation": (val_start_t, val_end_t),
    "test": (test_start_t, test_end_t),
}
for k, (a, b) in split_bounds.items():
    print(f"  {k}: {datetime.fromtimestamp(a, tz=timezone.utc)} -> {datetime.fromtimestamp(b, tz=timezone.utc)} "
          f"({(b - a) / 86400.0:.0f} gun)")

results["faz6_split_sinirlari"] = {
    k: {"baslangic": str(datetime.fromtimestamp(a, tz=timezone.utc)),
        "bitis": str(datetime.fromtimestamp(b, tz=timezone.utc)),
        "gun": round((b - a) / 86400.0, 1)}
    for k, (a, b) in split_bounds.items()
}


def split_of_time(t):
    for k, (a, b) in split_bounds.items():
        if a <= t <= b:
            return k
    return "embargo"


for cand in all_m15_candidates:
    cand["split"] = split_of_time(int(m15_times[cand["exec_idx"]]))

split_counts = {k: sum(1 for c in all_m15_candidates if c["split"] == k) for k in ("train", "validation", "test", "embargo")}
print("M15 aday-giris split dagilimi:", split_counts)
results["faz6_aday_giris_split_dagilimi"] = split_counts

# --- FAZ 4'un TRAIN-only cagrisi (veri sizintisi olmadan TP baglam olcumu) ---
train_cands_for_mfe = [c for c in all_m15_candidates if c["split"] == "train"]
mfe_stats = measure_mfe(train_cands_for_mfe)
print("N-bar-ileri medyan hareket (ATR-birim, TRAIN-only):", mfe_stats)
results["faz4_n_bar_ileri_medyan_hareket_train_only"] = mfe_stats
print("FAZ 4/6 tamamlandi.")

# ============================================================
# FAZ 7: TRADE SIMULASYONU
#   Giris: kirilim barinin KENDI kapanisinda (exec_idx bari kapanisi = entry_price)
#   Cikis (entry_idx+1'den itibaren taranir), HER barda SIRAYLA:
#     1) SL (false-breakout hizli cikis): kirilan sinirin GERISINE ~SLxATR14(giris)
#     2) TP: ATR14(giris)-bazli dinamik hedef
#     3) Kanala-geri-donus erken cikis: bar KAPANISI outer_boundary(t)'nin GERISINE donerse
#   Ayni barda SL+TP ARALIGINA girilirse (high/low) MUHAFAZAKAR varsayimla SL kazanir.
# ============================================================
print("=" * 70)
print("FAZ 7: TRADE SIMULASYONU FONKSIYONU")
print("=" * 70)


def floor_lot(x, step=LOT_STEP_USD):
    return math.floor(x / step) * step


def simulate_trades(candidates_subset, sl_mult, tp_mult, kasa=KASA_USD):
    trades = []
    pos_open_until_idx = -1
    n_overlap_skipped = 0

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

        entry_price = float(m15_closes[entry_idx])
        outer_boundary_entry = cand["outer_boundary_at_entry"]
        c = cand["channel"]
        anchor_price, anchor_time = c["anchor_price"], c["anchor_time"]
        bar_min_htf = TFS[c["tf"]][1]
        slope_per_sec = c["slope_price_per_bar"] / (bar_min_htf * 60)
        genislik = c["genislik_price"]

        sl_dist_pts = sl_mult * atr_sig
        tp_dist_pts = tp_mult * atr_sig
        # SL: kirilan sinirin (outer_boundary, giris anindaki degeriyle SABIT) GERISINE
        sl_price = outer_boundary_entry - sign * sl_dist_pts * POINT
        tp_price = entry_price + sign * tp_dist_pts * POINT

        exit_idx = None
        exit_reason = None
        exit_price = None
        j = entry_idx + 1
        while j < N_M15:
            hi, lo, close_j = float(m15_highs[j]), float(m15_lows[j]), float(m15_closes[j])
            if sign == 1:
                sl_hit = lo <= sl_price
                tp_hit = hi >= tp_price
            else:
                sl_hit = hi >= sl_price
                tp_hit = lo <= tp_price

            if sl_hit:
                exit_idx, exit_reason, exit_price = j, "SL_FALSE_BREAKOUT", sl_price
                break
            if tp_hit:
                exit_idx, exit_reason, exit_price = j, "TP", tp_price
                break

            # Kanala-geri-donus erken cikis: bar KAPANISI, o anki outer_boundary'nin GERISINE donerse
            t_j = int(m15_times[j])
            trendline_j = anchor_price + slope_per_sec * (t_j - anchor_time)
            outer_boundary_j = trendline_j + sign * genislik
            if sign * (close_j - outer_boundary_j) < 0:
                exit_idx, exit_reason, exit_price = j, "KANALA_GERI_DONUS_ERKEN_CIKIS", close_j
                break
            j += 1
        if exit_idx is None:
            exit_idx = N_M15 - 1
            exit_reason = "VERI_SONU_ACIK"
            exit_price = float(m15_closes[exit_idx])

        gross_pnl_pts = sign * (exit_price - entry_price) / POINT
        net_pnl_pts = gross_pnl_pts - cost_pts_total

        lot = max(TABAN_LOT, floor_lot((kasa * RISK_PCT_UST_SINIR) / sl_dist_pts))
        pnl_usd = net_pnl_pts * USD_PER_POINT_PER_LOT * lot

        hold_bars = exit_idx - entry_idx
        trades.append({
            "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
            "entry_time": str(datetime.fromtimestamp(int(m15_times[entry_idx]), tz=timezone.utc)),
            "exit_time": str(datetime.fromtimestamp(int(m15_times[exit_idx]), tz=timezone.utc)),
            "direction": direction, "tf_source": c["tf"],
            "sl_pts": round(sl_dist_pts, 1), "tp_pts": round(tp_dist_pts, 1),
            "exit_reason": exit_reason,
            "gross_pnl_pts": round(gross_pnl_pts, 2), "net_pnl_pts": round(net_pnl_pts, 2),
            "lot": round(lot, 2), "pnl_usd": round(pnl_usd, 4),
            "hold_bars_m15": int(hold_bars), "hold_hours": round(hold_bars * 15 / 60.0, 3),
            "split": cand["split"],
        })
        pos_open_until_idx = exit_idx

    return trades, n_overlap_skipped


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
    n_sl = exit_reasons.get("SL_FALSE_BREAKOUT", 0)

    return {
        "n_trades": len(trades),
        "win_rate": round(float(np.mean(wins)), 4),
        "profit_factor": round(pf, 4) if pf is not None and pf != float('inf') else pf,
        "net_profit_usd": round(float(pnl_usd.sum()), 2),
        "net_profit_pts": round(float(net_pts.sum()), 1),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "medyan_tutma_suresi_saat": round(float(np.median(hold_hours)), 2),
        "ortalama_tutma_suresi_saat": round(float(np.mean(hold_hours)), 2),
        "cikis_nedeni_dagilimi": exit_reasons,
        "false_breakout_sikligi": round(n_sl / len(trades), 4),
    }


print("FAZ 7 fonksiyonlari tanimlandi.")

# ============================================================
# FAZ 8: WALK-FORWARD SL/TP KALIBRASYONU
# ============================================================
print("=" * 70)
print("FAZ 8: WALK-FORWARD SL/TP KALIBRASYONU")
print("=" * 70)

train_cands = [c for c in all_m15_candidates if c["split"] == "train"]
val_cands = [c for c in all_m15_candidates if c["split"] == "validation"]
test_cands = [c for c in all_m15_candidates if c["split"] == "test"]
print(f"Ham aday sayilari: train={len(train_cands)}, validation={len(val_cands)}, test={len(test_cands)}")

grid_results = []
for sl_m in SL_MULT_GRID:
    for tp_m in TP_MULT_SURVIVED:
        tr_trades, tr_ov = simulate_trades(train_cands, sl_m, tp_m)
        va_trades, va_ov = simulate_trades(val_cands, sl_m, tp_m)
        tr_sum = summarize_trades(tr_trades)
        va_sum = summarize_trades(va_trades)
        grid_results.append({
            "sl_mult": sl_m, "tp_mult": tp_m,
            "train": tr_sum, "validation": va_sum,
            "train_overlap_skipped": tr_ov, "validation_overlap_skipped": va_ov,
        })
        pf_tr, pf_va = tr_sum.get("profit_factor"), va_sum.get("profit_factor")
        print(f"  SL={sl_m}xATR TP={tp_m}xATR -> Train(n={tr_sum.get('n_trades')}, PF={pf_tr}) | "
              f"Validation(n={va_sum.get('n_trades')}, PF={pf_va})")

results["faz8_grid_tarama"] = grid_results

eligible = [g for g in grid_results if g["validation"].get("n_trades", 0) >= MIN_TRADES_FOR_SELECTION
            and g["validation"].get("profit_factor") is not None]
if eligible:
    best = max(eligible, key=lambda g: g["validation"]["profit_factor"])
    secim_notu = f"Validation'da PF'ye gore secildi (n>={MIN_TRADES_FOR_SELECTION} sarti saglayan {len(eligible)} hucre arasindan)."
else:
    candidates_by_n = [g for g in grid_results if g["validation"].get("n_trades", 0) > 0]
    if candidates_by_n:
        best = max(candidates_by_n, key=lambda g: g["validation"].get("n_trades", 0))
        secim_notu = (f"HICBIR hucre Validation'da n>={MIN_TRADES_FOR_SELECTION} esigini GECMEDI - "
                      f"en fazla islem sayisina sahip hucre secildi (n={best['validation']['n_trades']}), "
                      f"bu secim ZAYIF/dusuk-guvenilirlikli olarak isaretlenmelidir.")
    else:
        best = grid_results[0]
        secim_notu = "Validation'da HICBIR hucrede islem olusmadi - ilk grid hucresi varsayilan olarak kullanildi (guvenilmez)."

SELECTED_SL_MULT = best["sl_mult"]
SELECTED_TP_MULT = best["tp_mult"]
print(f"SECILEN KOMBINASYON: SL={SELECTED_SL_MULT}xATR14_M15(giris), TP={SELECTED_TP_MULT}xATR14_M15(giris)")
print(secim_notu)

results["faz8_secim"] = {
    "secilen_sl_mult": SELECTED_SL_MULT, "secilen_tp_mult": SELECTED_TP_MULT,
    "secim_notu": secim_notu, "min_trades_esigi": MIN_TRADES_FOR_SELECTION,
}

test_trades, test_ov = simulate_trades(test_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
test_summary = summarize_trades(test_trades)
print("TEST SONUCU (tek kez):", test_summary)

train_trades_final, train_ov_final = simulate_trades(train_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
val_trades_final, val_ov_final = simulate_trades(val_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
train_summary_final = summarize_trades(train_trades_final)
val_summary_final = summarize_trades(val_trades_final)

all_cands_sorted = sorted(all_m15_candidates, key=lambda x: x["exec_idx"])
full_trades, full_ov = simulate_trades(all_cands_sorted, SELECTED_SL_MULT, SELECTED_TP_MULT)
full_summary = summarize_trades(full_trades)
print("TAM DONEM (train+val+test birlikte, tek-pozisyon TUM eksende) SONUCU:", full_summary)

results["faz8_final_sonuclar"] = {
    "train": train_summary_final, "validation": val_summary_final, "test": test_summary,
    "tam_donem_birlesik": full_summary,
    "overlap_skipped": {"train": train_ov_final, "validation": val_ov_final, "test": test_ov, "tam_donem": full_ov},
}
print("FAZ 8 tamamlandi.")

# ============================================================
# FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + KAYIT
# ============================================================
print("=" * 70)
print("FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + JSON/CSV")
print("=" * 70)

if full_trades:
    entry_dates = [datetime.fromisoformat(t["entry_time"]).date() for t in full_trades]
    n_months = max(1, (entry_dates[-1].year - entry_dates[0].year) * 12 + (entry_dates[-1].month - entry_dates[0].month) + 1)
    n_years = (entry_dates[-1] - entry_dates[0]).days / 365.25 if len(entry_dates) > 1 else 1.0
    trades_per_month = len(full_trades) / n_months
    trades_per_year = len(full_trades) / n_years if n_years > 0 else None
else:
    trades_per_month, trades_per_year = None, None
print(f"Islem/ay (tam donem): {trades_per_month}, Islem/yil: {trades_per_year}")

kirilim_tf, kirilim_yon = {}, {}
for t in full_trades:
    kirilim_tf.setdefault(t["tf_source"], []).append(t["net_pnl_pts"])
    kirilim_yon.setdefault(t["direction"], []).append(t["net_pnl_pts"])


def group_summary(d):
    out = {}
    for k, v in d.items():
        arr = np.array(v)
        wins = arr > 0
        gp = arr[arr > 0].sum()
        gl = -arr[arr < 0].sum()
        out[k] = {"n": len(arr), "win_rate": round(float(np.mean(wins)), 4),
                  "profit_factor_pts_bazli": round(float(gp / gl), 4) if gl > 0 else None,
                  "net_pts": round(float(arr.sum()), 1)}
    return out


results["faz9_islem_frekansi"] = {
    "islem_ay_sayisi_tam_donem": round(trades_per_month, 2) if trades_per_month else None,
    "islem_yil_sayisi_tam_donem": round(trades_per_year, 2) if trades_per_year else None,
    "toplam_islem_tam_donem": len(full_trades),
}
results["faz9_kirilim_tf_kaynagi"] = group_summary(kirilim_tf)
results["faz9_kirilim_yon"] = group_summary(kirilim_yon)
results["islem_logu_ornek"] = full_trades[:20] + (full_trades[-20:] if len(full_trades) > 20 else [])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)

if full_trades:
    pd.DataFrame(full_trades).to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print("Tam islem logu CSV yazildi.")

mt5.shutdown()
print("BITTI.")
