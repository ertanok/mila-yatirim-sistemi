# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping, Strateji Ailesi Plani ADIM 0 - EK TARAMA (Pivot/Kanal)
Tetikleyici: Ertan'in Adim 0 raporuna Soru 2 + Soru 3 geri bildirimi
(orkestrator_yanit_3soru_justin_20260714.md, Bolum 2).

Kapsam: bar-bar otokorelasyondan (Adim 0, A-Taramasi) FARKLI bir mekanizma -
pivot/dokunus-sayimi tabanli yapisal trend/kanal (>=3 dokunus) + EMA/MACD teyidi.
Ana trend tespiti: H1 ve M30 (H4 bu turde KULLANILMIYOR, Ertan'in acik talimati).
Giris zamanlamasi: M15 ve M5 (H1/M30 kanali icinde AYRICA test edilir).

Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), GOLD sembolu, sunucu saati (GMT+3).
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Sadece ham OHLCV veri MT5'ten cekilir. Ayni proje ici onceki script (adim0_tarama.py) ile
genel kod-iskeleti (MT5 baglanti/veri-cekme kalibi) ve S1 maliyet-orani yontemi PAYLASILIR
(karsilastirilabilirlik icin metodoloji bilerek tutarli tutulmustur) - izolasyon ihlali
DEGILDIR (kural yalniz BASKA projelerin dosya/format referansini yasaklar).
"""
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
point = info.point

TFS = {
    "M5": (mt5.TIMEFRAME_M5, 5),
    "M15": (mt5.TIMEFRAME_M15, 15),
    "M30": (mt5.TIMEFRAME_M30, 30),
    "H1": (mt5.TIMEFRAME_H1, 60),
}

results = {"symbol_info": {"point": point, "digits": info.digits,
                            "contract_size": info.trade_contract_size}}

raw = {}
for tf_name, (tf_const, bar_min) in TFS.items():
    rates = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)
    raw[tf_name] = rates
    t0 = datetime.utcfromtimestamp(int(rates[0]['time']))
    t1 = datetime.utcfromtimestamp(int(rates[-1]['time']))
    results.setdefault("veri_araligi", {})[tf_name] = {
        "n_bar": int(len(rates)), "baslangic": str(t0), "bitis": str(t1)
    }
    print(tf_name, "n=", len(rates), t0, "->", t1)

# ============================================================
# ORTAK YARDIMCI FONKSIYONLAR
# ============================================================

def ema(values, span):
    return pd.Series(values).ewm(span=span, adjust=False).mean().values


def macd(values, fast=12, slow=26, signal=9):
    macd_line = ema(values, fast) - ema(values, slow)
    signal_line = pd.Series(macd_line).ewm(span=signal, adjust=False).mean().values
    return macd_line, signal_line


def atr_series_pts(rates, window=14, point=point):
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    closes = rates['close'].astype(float)
    prev_close = np.roll(closes, 1)
    prev_close[0] = closes[0]
    tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
    atr = pd.Series(tr).rolling(window, min_periods=window).mean().values
    return atr / point  # aligned, index i = ATR14 using bars i-13..i, NaN for i<13


def find_swings(rates, n=5):
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


def atr_points_all(rates_dict):
    return {tf: atr_series_pts(raw[tf]) for tf in rates_dict}


ATR = {tf: atr_series_pts(raw[tf]) for tf in TFS}
EMA50 = {tf: ema(raw[tf]['close'].astype(float), 50) for tf in TFS}
EMA200 = {tf: ema(raw[tf]['close'].astype(float), 200) for tf in TFS}
MACD_LINE = {}
MACD_SIG = {}
for tf in TFS:
    ml, sl = macd(raw[tf]['close'].astype(float), 12, 26, 9)
    MACD_LINE[tf] = ml
    MACD_SIG[tf] = sl

SWINGS = {}
for tf in ("H1", "M30"):
    sh, sl = find_swings(raw[tf], n=5)
    SWINGS[tf] = {"swing_high": sh, "swing_low": sl}
    print(tf, "swing_high n=", sh.sum(), "swing_low n=", sl.sum())

# ============================================================
# PIVOT/KANAL TESPITI
# ============================================================
# Formul (bu tur icin sabitlenmis, standart/optimize-edilmemis baslangic degerleri):
#  - Pivot (swing) tanimi: fraktal, N=5 -> bar i, high[i] = max(high[i-5:i+6]) ise swing high;
#    low[i] = min(low[i-5:i+6]) ise swing low (5 bar sol + 5 bar sag).
#  - Kanal cizgisi: anchor (1. swing) + 2. swing noktasindan gecen DOGRUSAL cizgi (2-nokta,
#    refit YOK - deterministik, sabit egim).
#  - Dokunus toleransi: tol(i) = 0.5 x ATR14(i) (o bardaki ATR14, points cinsinden).
#  - Ek swing noktasi "dokunus" sayilir eger |fiyat - projeksiyon| <= tol(i).
#  - "Kirilim" (break): bir swing (veya sonradan herhangi bir bar KAPANISI) projeksiyonu
#    trend-aleyhine tol(i)'den fazla asarsa (yukselen kanal icin close < projeksiyon - tol;
#    alcalan kanal icin close > projeksiyon + tol).
#  - Gecerlilik esigi: >=3 dokunus (anchor + en az 2 ek dokunus). 3. dokunusun olustugu bar
#    "onay (confirm) bari" sayilir.
#  - EMA/MACD teyidi (onay barinda kontrol edilir): yukselen kanal icin EMA50>EMA200 VE
#    MACD_line>MACD_signal; alcalan kanal icin ters yon. Saglanmazsa aday ELENIR (kanal
#    olarak SAYILMAZ).
#  - Arama penceresi sinirlamasi (hesaplama pratikligi icin, optimizasyon degil): anchor'dan
#    itibaren ~300 gun (432.000 dk) gercek-zaman penceresi asilirsa aday terk edilir.
#  - Onaylanan kanalin tam kirilim noktasi, onay barindan itibaren TUM barlar (sadece
#    swing'ler degil) taranarak bulunur (cizgi onay barindaki 2-nokta egimiyle DONDURULMUS
#    olarak kullanilir, sonradan yeniden fit edilmez).

CAP_MINUTES = 300 * 24 * 60  # ~300 gun gercek-zaman arama penceresi siniri


def detect_channels(tf_name, direction, min_touches=3, touch_k=0.5):
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
    macd_s = MACD_SIG[tf_name]

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
    n_total = len(closes)

    channels = []
    pos = 0
    while pos < m - 2:
        anchor = swing_idx[pos]
        if np.isnan(atr[anchor]):
            pos += 1
            continue
        anchor_price = price_arr[anchor]
        anchor_time = times[anchor]

        # 2. nokta ara (slope tanimlayan)
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
        broke_in_swings = False
        k = j + 1
        while k < m:
            c = swing_idx[k]
            if times[c] - anchor_time > cap_bars * bar_min * 60:
                break
            if np.isnan(atr[c]):
                k += 1
                continue
            projected = anchor_price + slope * (c - anchor)
            tol = touch_k * atr[c]
            diff = price_arr[c] - projected
            if sign * diff < -tol:
                broke_in_swings = True
                break
            elif abs(diff) <= tol:
                touches.append(c)
                if len(touches) >= min_touches and confirm_idx is None:
                    confirm_idx = c
            k += 1

        if confirm_idx is None:
            # yeterli dokunus olusmadan bitti (kirildi ya da pencere doldu) -> aday gecersiz
            pos += 1
            continue

        # EMA/MACD teyidi - onay barinda
        if direction == "up":
            ema_ok = ema50[confirm_idx] > ema200[confirm_idx]
            macd_ok = macd_l[confirm_idx] > macd_s[confirm_idx]
        else:
            ema_ok = ema50[confirm_idx] < ema200[confirm_idx]
            macd_ok = macd_l[confirm_idx] < macd_s[confirm_idx]

        if not (ema_ok and macd_ok):
            # geometrik olarak gecerli ama EMA/MACD teyidi yok -> SAYILMAZ
            # bir sonraki anchor'a gec (bu bolgeyi tekrar denemeye izin ver, gecmedik)
            pos += 1
            continue

        # tam kirilim noktasini TUM barlarla bul (onay barindan itibaren, cizgi dondurulmus)
        break_idx = None
        limit_idx = min(n_total - 1, anchor + cap_bars)
        for i in range(confirm_idx + 1, limit_idx + 1):
            projected = anchor_price + slope * (i - anchor)
            tol = touch_k * atr[i] if not np.isnan(atr[i]) else touch_k * np.nanmedian(atr)
            diff = closes[i] - projected
            if sign * diff < -tol:
                break_idx = i
                break
        censored = False
        if break_idx is None:
            break_idx = limit_idx
            censored = True

        channels.append({
            "anchor_idx": int(anchor), "second_idx": int(second),
            "confirm_idx": int(confirm_idx), "break_idx": int(break_idx),
            "n_touches_total": int(len(touches)), "slope_per_bar_pts": float(slope / point),
            "anchor_time": str(datetime.utcfromtimestamp(int(anchor_time))),
            "confirm_time": str(datetime.utcfromtimestamp(int(times[confirm_idx]))),
            "break_time": str(datetime.utcfromtimestamp(int(times[break_idx]))),
            "anchor_price": float(anchor_price), "confirm_price": float(closes[confirm_idx]),
            "break_price": float(closes[break_idx]),
            "duration_bars_anchor_to_break": int(break_idx - anchor),
            "duration_bars_confirm_to_break": int(break_idx - confirm_idx),
            "censored_veri_sonu": bool(censored),
        })

        # non-overlapping ilerleme: break/sinir sonrasi ilk swing'e atla
        next_pos = np.searchsorted(swing_idx, break_idx, side="right")
        pos = max(next_pos, pos + 1)

    return channels


channel_results = {}
for tf_name in ("H1", "M30"):
    channel_results[tf_name] = {}
    for direction in ("up", "down"):
        chs = detect_channels(tf_name, direction)
        channel_results[tf_name][direction] = chs
        print(tf_name, direction, "confirmed kanal sayisi:", len(chs))

# ============================================================
# H1/M30 KANAL OZET ISTATISTIKLERI (siklik, sure, devam-orani)
# ============================================================

def summarize_channels(tf_name, direction, chs):
    bar_min = TFS[tf_name][1]
    n_total_bars = len(raw[tf_name])
    closes = raw[tf_name]['close'].astype(float)
    sign = 1 if direction == "up" else -1

    if not chs:
        return {"n_kanal": 0}

    dur_anchor_break = np.array([c["duration_bars_anchor_to_break"] for c in chs])
    dur_confirm_break = np.array([c["duration_bars_confirm_to_break"] for c in chs])

    # gorece siklik: kanal basina dusen ortalama bar sayisi (n_total_bars / n_kanal)
    freq_bars_per_channel = n_total_bars / len(chs)
    freq_per_year = len(chs) / (n_total_bars * bar_min / (60 * 24 * 365.25))

    # devam-orani: onay barindan N bar sonra fiyat hala trend yonunde ileride mi
    # (Adim 0 A.4 ile karsilastirilabilir format)
    days_horizons = [1, 3, 7, 14]
    devam = {}
    for d in days_horizons:
        N = int(d * 24 * 60 / bar_min)
        same_dir = []
        move_pts = []
        for c in chs:
            ci = c["confirm_idx"]
            if ci + N < n_total_bars:
                p0 = closes[ci]
                p1 = closes[ci + N]
                same_dir.append(1 if sign * (p1 - p0) > 0 else 0)
                move_pts.append(sign * (p1 - p0) / point)
        if same_dir:
            devam[f"{d}_gun"] = {
                "n": len(same_dir),
                "trend_yonunde_devam_orani": round(float(np.mean(same_dir)), 4),
                "medyan_hareket_pts_trend_yonunde": round(float(np.median(move_pts)), 1),
            }
        else:
            devam[f"{d}_gun"] = None

    return {
        "n_kanal": len(chs),
        "toplam_bar": n_total_bars,
        "kanal_basina_ortalama_bar": round(freq_bars_per_channel, 1),
        "yillik_kanal_sayisi_yaklasik": round(freq_per_year, 2),
        "sure_anchor_to_break_bar": {
            "medyan": round(float(np.median(dur_anchor_break)), 1),
            "ortalama": round(float(np.mean(dur_anchor_break)), 1),
            "medyan_saat": round(float(np.median(dur_anchor_break) * bar_min / 60), 1),
            "medyan_gun": round(float(np.median(dur_anchor_break) * bar_min / (60 * 24)), 2),
        },
        "sure_confirm_to_break_bar": {
            "medyan": round(float(np.median(dur_confirm_break)), 1),
            "ortalama": round(float(np.mean(dur_confirm_break)), 1),
            "medyan_saat": round(float(np.median(dur_confirm_break) * bar_min / 60), 1),
            "medyan_gun": round(float(np.median(dur_confirm_break) * bar_min / (60 * 24)), 2),
        },
        "censored_orani_veri_sonunda_hala_aktif": round(
            float(np.mean([c["censored_veri_sonu"] for c in chs])), 3),
        "trend_yonunde_devam_orani_onay_sonrasi": devam,
    }


channel_summary = {}
for tf_name in ("H1", "M30"):
    channel_summary[tf_name] = {}
    for direction in ("up", "down"):
        channel_summary[tf_name][direction] = summarize_channels(
            tf_name, direction, channel_results[tf_name][direction])

results["h1_m30_yapisal_kanal_ozet"] = channel_summary

# ============================================================
# M15/M5 GIRIS-ZAMANLAMA TESTI (H1/M30 kanali icinde)
# ============================================================

def s1_cost_global(tf_name, n_list_bars):
    rates = raw[tf_name]
    bar_min = TFS[tf_name][1]
    closes = rates['close'].astype(float)
    spread_pts = rates['spread'].astype(float)
    atr_pts_arr = ATR[tf_name]
    atr_median = float(np.nanmedian(atr_pts_arr))
    spread_median = float(np.median(spread_pts))
    slippage_est = 0.037 * atr_median
    cost_pts = spread_median + slippage_est
    return {
        "spread_median_pts": round(spread_median, 2),
        "atr14_median_pts": round(atr_median, 2),
        "slippage_tahmini_pts": round(slippage_est, 2),
        "toplam_maliyet_pts": round(cost_pts, 2),
        "cost_pts_raw": cost_pts,
        "atr_median_raw": atr_median,
    }


S1_GLOBAL = {tf: s1_cost_global(tf, None) for tf in ("M15", "M5")}
results["s1_global_maliyet"] = {tf: {k: v for k, v in d.items() if k not in ("cost_pts_raw", "atr_median_raw")}
                                  for tf, d in S1_GLOBAL.items()}


def project_and_find_entries(htf_name, ltf_name, channels_htf, direction, touch_k=0.5):
    htf_bar_min = TFS[htf_name][1]
    ltf_rates = raw[ltf_name]
    ltf_times = ltf_rates['time'].astype(np.int64)
    ltf_closes = ltf_rates['close'].astype(float)
    ltf_atr = ATR[ltf_name]
    sign = 1 if direction == "up" else -1

    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    all_entries = []  # list of ltf bar indices (entry = bar after touch, confirming continuation)
    n_channels_in_overlap = 0

    for c in channels_htf:
        confirm_t = int(datetime.strptime(c["confirm_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        break_t = int(datetime.strptime(c["break_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        # yalniz LTF veri araligiyla ORTUSEN kanal pencereleri kullanilir
        if break_t < ltf_t0 or confirm_t > ltf_t1:
            continue
        n_channels_in_overlap += 1
        win_start = max(confirm_t, ltf_t0)
        win_end = min(break_t, ltf_t1)
        lo = np.searchsorted(ltf_times, win_start, side="left")
        hi = np.searchsorted(ltf_times, win_end, side="right")
        if hi - lo < 3:
            continue

        anchor_price = c["anchor_price"]
        anchor_time = int(datetime.strptime(c["anchor_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        slope_per_bar = c["slope_per_bar_pts"] * point
        slope_per_sec = slope_per_bar / (htf_bar_min * 60)

        for i in range(lo, hi - 1):
            if np.isnan(ltf_atr[i]):
                continue
            t_i = int(ltf_times[i])
            projected = anchor_price + slope_per_sec * (t_i - anchor_time)
            tol = touch_k * ltf_atr[i]
            diff = ltf_closes[i] - projected
            if abs(diff) <= tol:
                # dokunus - bir sonraki barin trend yonunde kapanmasi giris tetigi
                if sign * (ltf_closes[i + 1] - ltf_closes[i]) > 0:
                    all_entries.append(i + 1)

    return sorted(set(all_entries)), n_channels_in_overlap


def entry_forward_test(ltf_name, entries, n_list_bars, cost_pts):
    closes = raw[ltf_name]['close'].astype(float)
    bar_min = TFS[ltf_name][1]
    n_total = len(closes)
    entries = np.array(entries, dtype=int)
    table = {}
    for N in n_list_bars:
        valid = entries[entries + N < n_total]
        if len(valid) == 0:
            table[N] = None
            continue
        fwd = np.abs(closes[valid + N] - closes[valid]) / point
        med = float(np.median(fwd))
        ratio = med / cost_pts if cost_pts else None
        table[N] = {
            "gercek_sure_dk": N * bar_min,
            "n_giris": int(len(valid)),
            "ileri_hareket_median_pts": round(med, 1),
            "oran_median_hedef_maliyet": round(ratio, 2) if ratio else None,
        }
    return table


N_LIST = {"M15": (1, 2, 4, 8, 16, 32, 64), "M5": (1, 2, 4, 8, 16, 32, 64, 128)}

giris_testi = {}
for htf in ("H1", "M30"):
    for ltf in ("M15", "M5"):
        combo = f"{htf}_to_{ltf}"
        giris_testi[combo] = {}
        for direction in ("up", "down"):
            entries, n_overlap = project_and_find_entries(
                htf, ltf, channel_results[htf][direction], direction)
            tbl = entry_forward_test(ltf, entries, N_LIST[ltf], S1_GLOBAL[ltf]["cost_pts_raw"])
            giris_testi[combo][direction] = {
                "n_htf_kanal_ortusen": n_overlap,
                "n_giris_tetigi": len(entries),
                "ufuk_tablosu": tbl,
            }
        print(combo, "tamamlandi")

results["giris_testi_m15_m5"] = giris_testi

with open(r"C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_output.json",
          "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI. JSON yazildi.")
mt5.shutdown()
