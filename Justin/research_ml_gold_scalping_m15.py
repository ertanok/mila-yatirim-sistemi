# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping ML/Feature-Tabanli Arastirma (M15+)
Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), GOLD sembolu, M15 OHLCV+tick_volume+spread.
H1/H4 barlari M15 ham verisinden nedensel/hizalanmis yeniden-ornekleme (resampling) ile turetilir
(gorev tanimi geregi, ayri bir MT5 cagrisi ile degil).
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Sadece ham OHLCV/spread/tick_volume verisi MT5'ten cekilir. Kutuphane kisiti: bu ortamda
pandas/lightgbm/xgboost/scikit-learn KURULU DEGIL; bu script yalniz numpy/scipy kullanir,
gercek model egitimi bu asamada YAPILMAMISTIR (bkz. rapor, Riskler/Sinirlamalar).
"""
import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timezone
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point

m15 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 99999)
assert m15 is not None and len(m15) > 0, "M15 veri cekilemedi"

results = {}
results["meta"] = {
    "symbol": SYMBOL,
    "point": POINT,
    "digits": info.digits,
    "contract_size": info.trade_contract_size,
    "m15_n": int(len(m15)),
    "m15_start": datetime.fromtimestamp(int(m15[0]['time']), tz=timezone.utc).isoformat(),
    "m15_end": datetime.fromtimestamp(int(m15[-1]['time']), tz=timezone.utc).isoformat(),
}

t = m15['time'].astype(np.int64)
o = m15['open'].astype(float)
h = m15['high'].astype(float)
l = m15['low'].astype(float)
c = m15['close'].astype(float)
vol = m15['tick_volume'].astype(float)
spread = m15['spread'].astype(float)

# ---------------------------------------------------------------
# YARDIMCI: nedensel (causal) rolling fonksiyonlar (yalniz gecmis+kendisi)
# ---------------------------------------------------------------

def rolling_mean_causal(x, window):
    out = np.full(len(x), np.nan)
    csum = np.cumsum(np.insert(x, 0, 0.0))
    for i in range(window - 1, len(x)):
        out[i] = (csum[i + 1] - csum[i + 1 - window]) / window
    return out


def rolling_median_causal(x, window):
    out = np.full(len(x), np.nan)
    for i in range(window - 1, len(x)):
        out[i] = np.median(x[i - window + 1:i + 1])
    return out


# ---------------------------------------------------------------
# 1) True Range / ATR(14), nedensel
# ---------------------------------------------------------------
prev_c = np.roll(c, 1)
prev_c[0] = c[0]
tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
tr_pts = tr / POINT
ATR_N = 14
atr14 = rolling_mean_causal(tr_pts, ATR_N)

# ATR14'un kendi trailing-100 medyanina gore genis/dar rejimi (BULGU 3'teki onceki calisma
# metodolojisiyle AYNI yapi, farkli TF)
TRAIL_W = 100
atr_trail_med = rolling_median_causal(np.nan_to_num(atr14, nan=0.0), TRAIL_W)
valid_regime = ~np.isnan(atr14)
valid_regime[:ATR_N - 1 + TRAIL_W - 1] = False

# ---------------------------------------------------------------
# 2) Saat / Oturum / Gun-ici konum (UTC epoch -> saat; sunucu saati GMT+3 varsayimi,
#    onceki rapordaki ayni SINIR/varsayim gecerlidir, DST ayrica dogrulanmadi)
# ---------------------------------------------------------------
dt_utc = [datetime.fromtimestamp(int(x), tz=timezone.utc) for x in t]
hours = np.array([d.hour for d in dt_utc])
dows = np.array([d.weekday() for d in dt_utc])  # 0=Pazartesi

# Genel/kamuya-acik seans tanimlari (server-saat/UTC epoch dogrudan okunmus, GMT+3 varsayimi):
# Asya ~ 1-8, Londra ~ 9-16, New York ~ 15-23 (Londra/NY orustugu bant 15-16 iki sette de var)
SESSION_ASIA = set(range(1, 9))
SESSION_LONDON = set(range(9, 17))
SESSION_NY = set(range(15, 24))


def in_session(hr, s):
    return hr in s


results["m15_hourly_atr_spread_volume"] = {}
for hr in range(24):
    mask = (hours == hr) & valid_regime
    n = int(mask.sum())
    if n == 0:
        continue
    results["m15_hourly_atr_spread_volume"][hr] = {
        "n": n,
        "atr14_mean_pts": round(float(np.nanmean(atr14[mask])), 2),
        "atr14_median_pts": round(float(np.nanmedian(atr14[mask])), 2),
        "atr14_p90_pts": round(float(np.nanpercentile(atr14[mask], 90)), 2),
        "spread_mean_pts": round(float(spread[mask].mean()), 2),
        "spread_median_pts": round(float(np.median(spread[mask])), 2),
        "tick_volume_mean": round(float(vol[mask].mean()), 1),
        "tick_volume_median": round(float(np.median(vol[mask])), 1),
    }

# ---------------------------------------------------------------
# 3) ATR genisleme/daralma rejim dagilimi + rejim-bazli sonraki-4-bar mutlak getiri
# ---------------------------------------------------------------
wide_mask = valid_regime & (atr14 > atr_trail_med)
narrow_mask = valid_regime & (atr14 <= atr_trail_med)

fwd_h = 4  # M15 icin 4 bar = 1 saat ileri ufuk


def fwd_abs_return_pts(mask, horizon):
    idx = np.where(mask)[0]
    idx = idx[idx + horizon < len(c)]
    if len(idx) == 0:
        return None, 0
    rets = np.abs(c[idx + horizon] - c[idx]) / POINT
    return float(np.mean(rets)), len(idx)


wide_fwd, wide_n = fwd_abs_return_pts(wide_mask, fwd_h)
narrow_fwd, narrow_n = fwd_abs_return_pts(narrow_mask, fwd_h)

results["atr_regime"] = {
    "trail_window": TRAIL_W,
    "genis_n": int(wide_mask.sum()),
    "dar_n": int(narrow_mask.sum()),
    "genis_sonraki_4bar_mutlak_getiri_pts_ort": round(wide_fwd, 2) if wide_fwd else None,
    "genis_sonraki_4bar_n": wide_n,
    "dar_sonraki_4bar_mutlak_getiri_pts_ort": round(narrow_fwd, 2) if narrow_fwd else None,
    "dar_sonraki_4bar_n": narrow_n,
}

# ---------------------------------------------------------------
# 4) Coklu-zaman-dilimi (M15/H1/H4) trend confluence
#    Trend tanimi: close[i] > SMA20[i] (kendi TF'inde) -> +1 (yukari), <= -> -1 (asagi)
#    H1/H4 barlari M15'ten nedensel/hizalanmis resample: epoch // 3600 (H1), epoch // 14400 (H4)
# ---------------------------------------------------------------

def resample_ohlc(t, o, h, l, c, v, bucket_seconds):
    key = (t // bucket_seconds)
    # gruplari sirali tut (t zaten artan)
    uniq_key, first_idx, counts = np.unique(key, return_index=True, return_counts=True)
    order = np.argsort(first_idx)
    uniq_key = uniq_key[order]
    first_idx = first_idx[order]
    counts = counts[order]
    n = len(uniq_key)
    r_o = np.empty(n); r_h = np.empty(n); r_l = np.empty(n); r_c = np.empty(n); r_v = np.empty(n)
    r_t = np.empty(n, dtype=np.int64)
    pos = 0
    for i in range(n):
        seg = slice(pos, pos + counts[i])
        r_o[i] = o[seg][0]
        r_h[i] = h[seg].max()
        r_l[i] = l[seg].min()
        r_c[i] = c[seg][-1]
        r_v[i] = v[seg].sum()
        r_t[i] = uniq_key[i] * bucket_seconds
        pos += counts[i]
    return r_t, r_o, r_h, r_l, r_c, r_v


h1_t, h1_o, h1_h, h1_l, h1_c, h1_v = resample_ohlc(t, o, h, l, c, vol, 3600)
h4_t, h4_o, h4_h, h4_l, h4_c, h4_v = resample_ohlc(t, o, h, l, c, vol, 14400)

results["resample_check"] = {
    "h1_bar_sayisi": int(len(h1_t)),
    "h4_bar_sayisi": int(len(h4_t)),
    "h1_ilk_son": [int(h1_t[0]), int(h1_t[-1])],
    "h4_ilk_son": [int(h4_t[0]), int(h4_t[-1])],
}


def sma_trend(close_arr, window=20):
    sma = rolling_mean_causal(close_arr, window)
    trend = np.full(len(close_arr), np.nan)
    valid = ~np.isnan(sma)
    trend[valid] = np.sign(close_arr[valid] - sma[valid])
    return trend, valid


m15_trend, m15_trend_valid = sma_trend(c, 20)
h1_trend, h1_trend_valid = sma_trend(h1_c, 20)
h4_trend, h4_trend_valid = sma_trend(h4_c, 20)

# Her M15 barina, o anda gecerli (henuz kapanmamis olabilecek) en son TAMAMLANMIS H1/H4 barinin
# trend etiketini nedensel olarak esle (bar i zamaninda, kendinden ONCEKI kapanmis H1/H4 bari)
h1_bucket_of_m15 = (t // 3600)
h4_bucket_of_m15 = (t // 14400)
h1_key_to_idx = {int(k): i for i, k in enumerate(h1_t // 3600)}
h4_key_to_idx = {int(k): i for i, k in enumerate(h4_t // 14400)}

n = len(t)
m15_h1_trend_aligned = np.full(n, np.nan)
m15_h4_trend_aligned = np.full(n, np.nan)
for i in range(n):
    hb = int(h1_bucket_of_m15[i])
    h1_idx = h1_key_to_idx.get(hb)
    # nedensellik: sadece bar i'den ONCE kapanmis H1 barini kullan (bir onceki H1 bucket)
    if h1_idx is not None and h1_idx - 1 >= 0 and h1_trend_valid[h1_idx - 1]:
        m15_h1_trend_aligned[i] = h1_trend[h1_idx - 1]
    hb4 = int(h4_bucket_of_m15[i])
    h4_idx = h4_key_to_idx.get(hb4)
    if h4_idx is not None and h4_idx - 1 >= 0 and h4_trend_valid[h4_idx - 1]:
        m15_h4_trend_aligned[i] = h4_trend[h4_idx - 1]

conf_valid = m15_trend_valid & ~np.isnan(m15_h1_trend_aligned) & ~np.isnan(m15_h4_trend_aligned)
all_bull = conf_valid & (m15_trend == 1) & (m15_h1_trend_aligned == 1) & (m15_h4_trend_aligned == 1)
all_bear = conf_valid & (m15_trend == -1) & (m15_h1_trend_aligned == -1) & (m15_h4_trend_aligned == -1)
no_confluence = conf_valid & ~all_bull & ~all_bear


def fwd_signed_return(mask, horizon, direction):
    idx = np.where(mask)[0]
    idx = idx[idx + horizon < len(c)]
    if len(idx) == 0:
        return None, 0
    rets = (c[idx + horizon] - c[idx]) / POINT * direction
    return float(np.mean(rets)), len(idx)


bull_fwd, bull_n = fwd_signed_return(all_bull, 8, 1)
bear_fwd, bear_n = fwd_signed_return(all_bear, 8, -1)
none_fwd_bull_side, none_n = fwd_signed_return(no_confluence, 8, 1)

results["mtf_confluence"] = {
    "tanim": "trend = sign(close - SMA20), kendi TF'inde; H1/H4 nedensel-hizalanmis (bar i'den once kapanmis son H1/H4 bari kullanilir)",
    "toplam_gecerli_m15_bar": int(conf_valid.sum()),
    "tum_yon_yukari_n": int(all_bull.sum()),
    "tum_yon_asagi_n": int(all_bear.sum()),
    "confluence_yok_n": int(no_confluence.sum()),
    "confluence_orani": round(float((all_bull.sum() + all_bear.sum()) / conf_valid.sum()), 4) if conf_valid.sum() else None,
    "8bar_ileri_yon_hizali_getiri_pts_ort_yukari_confluence": round(bull_fwd, 2) if bull_fwd else None,
    "8bar_ileri_n_yukari_confluence": bull_n,
    "8bar_ileri_yon_hizali_getiri_pts_ort_asagi_confluence": round(bear_fwd, 2) if bear_fwd else None,
    "8bar_ileri_n_asagi_confluence": bear_n,
    "8bar_ileri_getiri_pts_ort_confluence_yok": round(none_fwd_bull_side, 2) if none_fwd_bull_side else None,
    "8bar_ileri_n_confluence_yok": none_n,
}

# ---------------------------------------------------------------
# 5) RSI(14) M15 + MACD(12,26,9) histogram sign persistence
# ---------------------------------------------------------------

def rsi(close_arr, period=14):
    delta = np.diff(close_arr, prepend=close_arr[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = rolling_mean_causal(gain, period)
    avg_loss = rolling_mean_causal(loss, period)
    rs = np.divide(avg_gain, avg_loss, out=np.full_like(avg_gain, np.nan), where=avg_loss != 0)
    rsi_val = 100 - (100 / (1 + rs))
    rsi_val[avg_loss == 0] = 100.0
    return rsi_val


def ema_causal(x, span):
    alpha = 2.0 / (span + 1)
    out = np.full(len(x), np.nan)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


rsi14 = rsi(c, 14)
ema12 = ema_causal(c, 12)
ema26 = ema_causal(c, 26)
macd_line = ema12 - ema26
macd_signal = ema_causal(macd_line, 9)
macd_hist = macd_line - macd_signal

hist_sign = np.sign(macd_hist)
hist_sign_valid = ~np.isnan(hist_sign) & (hist_sign != 0)
hs = hist_sign[hist_sign_valid]
same_next = (hs[1:] == hs[:-1])
macd_persistence = float(same_next.mean()) if len(same_next) else None

results["momentum_features"] = {
    "rsi14_mean": round(float(np.nanmean(rsi14)), 2),
    "rsi14_median": round(float(np.nanmedian(rsi14)), 2),
    "rsi14_p10_p90": [round(float(np.nanpercentile(rsi14, 10)), 2), round(float(np.nanpercentile(rsi14, 90)), 2)],
    "rsi14_gt70_orani": round(float(np.nanmean(rsi14 > 70)), 4),
    "rsi14_lt30_orani": round(float(np.nanmean(rsi14 < 30)), 4),
    "macd_hist_ayni_isaret_sonraki_bar_orani": round(macd_persistence, 4) if macd_persistence else None,
    "macd_hist_n": int(len(hs)),
}

# HH/LL ardisiklik (M15): higher-high = high[i] > high[i-1], lower-low = low[i] < low[i-1]
hh = h[1:] > h[:-1]
ll = l[1:] < l[:-1]


def max_streak_stats(bool_arr):
    streaks = []
    cur = 0
    for b in bool_arr:
        if b:
            cur += 1
        else:
            if cur > 0:
                streaks.append(cur)
            cur = 0
    if cur > 0:
        streaks.append(cur)
    if not streaks:
        return None
    streaks = np.array(streaks)
    return {
        "adet": int(len(streaks)),
        "ortalama_uzunluk": round(float(streaks.mean()), 2),
        "p90_uzunluk": int(np.percentile(streaks, 90)),
        "maksimum_uzunluk": int(streaks.max()),
    }


results["structure_features"] = {
    "higher_high_orani": round(float(hh.mean()), 4),
    "lower_low_orani": round(float(ll.mean()), 4),
    "hh_streak": max_streak_stats(hh),
    "ll_streak": max_streak_stats(ll),
}

# ---------------------------------------------------------------
# 6) Hacim (tick_volume) anomali -> sonraki bar range iliskisi
# ---------------------------------------------------------------
vol_trail_med = rolling_median_causal(vol, TRAIL_W)
vol_valid = ~np.isnan(vol_trail_med)
vol_anomaly = vol_valid & (vol > 2 * vol_trail_med)

range_pts = (h - l) / POINT
idx_anom = np.where(vol_anomaly)[0]
idx_anom = idx_anom[idx_anom + 1 < len(range_pts)]
idx_normal = np.where(vol_valid & ~vol_anomaly)[0]
idx_normal = idx_normal[idx_normal + 1 < len(range_pts)]

results["volume_features"] = {
    "trail_window": TRAIL_W,
    "anomali_esigi": "tick_volume > 2x trailing_median(100)",
    "anomali_bar_sayisi": int(vol_anomaly.sum()),
    "anomali_sonrasi_bar_ort_range_pts": round(float(range_pts[idx_anom + 1].mean()), 2) if len(idx_anom) else None,
    "normal_sonrasi_bar_ort_range_pts": round(float(range_pts[idx_normal + 1].mean()), 2) if len(idx_normal) else None,
    "tick_volume_ortalama": round(float(vol.mean()), 1),
    "tick_volume_medyan": round(float(np.median(vol)), 1),
}

# ---------------------------------------------------------------
# 7) Gun-ici oturum ozeti (Asya/Londra/NY) + haftanin gunu
# ---------------------------------------------------------------
results["session_summary"] = {}
for name, sess in [("ASYA", SESSION_ASIA), ("LONDRA", SESSION_LONDON), ("NY", SESSION_NY)]:
    mask = np.isin(hours, list(sess)) & valid_regime
    n = int(mask.sum())
    if n == 0:
        continue
    results["session_summary"][name] = {
        "n": n,
        "atr14_median_pts": round(float(np.nanmedian(atr14[mask])), 2),
        "spread_median_pts": round(float(np.median(spread[mask])), 2),
        "tick_volume_medyan": round(float(np.median(vol[mask])), 1),
    }

results["dow_summary"] = {}
gun_isimleri = ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"]
for d in range(7):
    mask = (dows == d) & valid_regime
    n = int(mask.sum())
    if n == 0:
        continue
    results["dow_summary"][gun_isimleri[d]] = {
        "n": n,
        "range_mean_pts": round(float(np.mean(range_pts[mask])), 2),
        "atr14_median_pts": round(float(np.nanmedian(atr14[mask])), 2),
    }

# ---------------------------------------------------------------
# 8) Triple-Barrier on-simulasyon (label tasarimi icin taban dagilim)
#    N-bar ileri ufuk, barrier = k x ATR14 (giris barindaki ATR14)
# ---------------------------------------------------------------
results["triple_barrier"] = {}
for N in [4, 8, 16]:
    for k in [1.0, 1.5, 2.0]:
        tp_first = 0
        sl_first = 0
        neither = 0
        considered = 0
        idx_pool = np.where(valid_regime)[0]
        idx_pool = idx_pool[idx_pool + N < len(c)]
        for i in idx_pool:
            entry = c[i]
            atr_i = atr14[i]
            if np.isnan(atr_i) or atr_i <= 0:
                continue
            tp_up = entry + k * atr_i * POINT
            sl_down = entry - k * atr_i * POINT
            path_h = h[i + 1:i + 1 + N]
            path_l = l[i + 1:i + 1 + N]
            hit_tp_idx = np.argmax(path_h >= tp_up) if np.any(path_h >= tp_up) else None
            hit_sl_idx = np.argmax(path_l <= sl_down) if np.any(path_l <= sl_down) else None
            considered += 1
            if hit_tp_idx is None and hit_sl_idx is None:
                neither += 1
            elif hit_tp_idx is None:
                sl_first += 1
            elif hit_sl_idx is None:
                tp_first += 1
            else:
                if hit_tp_idx <= hit_sl_idx:
                    tp_first += 1
                else:
                    sl_first += 1
        if considered > 0:
            results["triple_barrier"][f"N{N}_k{k}"] = {
                "considered_n": considered,
                "tp_first_orani": round(tp_first / considered, 4),
                "sl_first_orani": round(sl_first / considered, 4),
                "neither_orani": round(neither / considered, 4),
            }

# ---------------------------------------------------------------
# 9) Maliyet-orani on-tahmini (S1 On-Kontrol icin kaba veri)
# ---------------------------------------------------------------
median_atr = float(np.nanmedian(atr14))
median_spread = float(np.median(spread))
results["cost_ratio_precheck"] = {
    "atr14_m15_medyan_pts": round(median_atr, 2),
    "spread_m15_medyan_pts": round(median_spread, 2),
    "atr_over_spread_orani": round(median_atr / median_spread, 2) if median_spread else None,
}
for k in [1.0, 1.5, 2.0]:
    target_pts = k * median_atr
    results["cost_ratio_precheck"][f"k{k}_hedef_pts_over_spread_orani"] = round(target_pts / median_spread, 2) if median_spread else None

# Canli spread
tick = mt5.symbol_info_tick(SYMBOL)
results["canli_spread_pts"] = int(round((tick.ask - tick.bid) / POINT))

with open(r"C:\MilaYatirim\Justin\research_ml_gold_scalping_m15_output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("TAMAMLANDI")
print(json.dumps({k: v for k, v in results.items() if k != "m15_hourly_atr_spread_volume"}, ensure_ascii=False, indent=2))

mt5.shutdown()
