
# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping Arastirmasi
Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), GOLD sembolu
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi
okumaz/kullanmaz. Sadece ham OHLCV/tick veri MT5'ten cekilir.
"""
import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timedelta
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
print("SYMBOL INFO point:", info.point, "digits:", info.digits, "contract_size:", info.trade_contract_size)

now = datetime.now()

# ---- M1 verisi (maksimum kadar geriye, MT5 sinirlari geregi 99999) ----
m1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 99999)
m5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 99999)

print("M1 bar sayisi:", len(m1) if m1 is not None else None)
print("M5 bar sayisi:", len(m5) if m5 is not None else None)

if m1 is not None and len(m1) > 0:
    t0 = datetime.utcfromtimestamp(m1[0]['time'])
    t1 = datetime.utcfromtimestamp(m1[-1]['time'])
    print("M1 araligi (sunucu saati/epoch):", t0, "->", t1)

if m5 is not None and len(m5) > 0:
    t0 = datetime.utcfromtimestamp(m5[0]['time'])
    t1 = datetime.utcfromtimestamp(m5[-1]['time'])
    print("M5 araligi (sunucu saati/epoch):", t0, "->", t1)

# spread field mevcut mu?
print("M1 dtype fields:", m1.dtype.names)

results = {}

def hourly_stats(rates, tf_name):
    hours = np.array([datetime.utcfromtimestamp(r['time']).hour for r in rates])
    ranges_points = (rates['high'] - rates['low']) / info.point
    spreads = rates['spread']  # points
    out = {}
    for h in range(24):
        mask = hours == h
        n = int(mask.sum())
        if n == 0:
            continue
        out[h] = {
            "n": n,
            "range_mean_pts": round(float(ranges_points[mask].mean()), 2),
            "range_median_pts": round(float(np.median(ranges_points[mask])), 2),
            "range_p90_pts": round(float(np.percentile(ranges_points[mask], 90)), 2),
            "spread_mean_pts": round(float(spreads[mask].mean()), 2),
            "spread_median_pts": round(float(np.median(spreads[mask])), 2),
            "spread_max_pts": int(spreads[mask].max()),
        }
    results[tf_name + "_hourly"] = out
    return out

h1 = hourly_stats(m1, "M1")
h5 = hourly_stats(m5, "M5")

# ---- Gun ici toplam ATR benzeri (M5, tum gun ortalama range) ----
def overall_stats(rates, tf_name):
    ranges_points = (rates['high'] - rates['low']) / info.point
    body_points = np.abs(rates['close'] - rates['open']) / info.point
    results[tf_name + "_overall"] = {
        "n": len(rates),
        "range_mean_pts": round(float(ranges_points.mean()), 2),
        "range_median_pts": round(float(np.median(ranges_points)), 2),
        "range_std_pts": round(float(ranges_points.std()), 2),
        "body_mean_pts": round(float(body_points.mean()), 2),
        "spread_mean_pts": round(float(rates['spread'].mean()), 2),
        "spread_median_pts": round(float(np.median(rates['spread'])), 2),
    }

overall_stats(m1, "M1")
overall_stats(m5, "M5")

# ---- Bar yon devamliligi (continuation) - M1 ve M5, genel istatistik ----
def continuation_stats(rates, tf_name):
    closes = rates['close']
    opens = rates['open']
    direction = np.sign(closes - opens)  # +1 yukari, -1 asagi, 0 doji
    nonzero_mask = direction != 0
    d = direction[nonzero_mask]
    if len(d) < 3:
        return
    same_as_prev = (d[1:] == d[:-1])
    cont_rate = float(same_as_prev.mean())

    # N ardisik ayni yonlu bardan sonraki barin yonu (streak length 2,3,4,5)
    streak_results = {}
    for streak_len in [2, 3, 4, 5]:
        idx_hits = []
        cur = 1
        for i in range(1, len(d)):
            if d[i] == d[i-1]:
                cur += 1
            else:
                cur = 1
            if cur == streak_len and i+1 < len(d):
                idx_hits.append(i+1)
        if idx_hits:
            nxt = d[idx_hits]
            prev_dir = d[np.array(idx_hits) - 1]
            same = float((nxt == prev_dir).mean())
            streak_results[streak_len] = {"n": len(idx_hits), "sonraki_bar_ayni_yon_orani": round(same, 3)}

    results[tf_name + "_continuation"] = {
        "genel_ardisik_ayni_yon_orani": round(cont_rate, 3),
        "streak_sonrasi": streak_results,
        "n_bar_yonlu": int(len(d)),
    }

continuation_stats(m1, "M1")
continuation_stats(m5, "M5")

# ---- Buyuk range (breakout) sonrasi davranis - M5 ----
def breakout_followthrough(rates, tf_name, mult=1.5):
    ranges = rates['high'] - rates['low']
    mean_r = ranges.mean()
    opens = rates['open']; closes = rates['close']; highs = rates['high']; lows = rates['low']
    direction = np.sign(closes - opens)
    big_idx = np.where(ranges > mult * mean_r)[0]
    big_idx = big_idx[(big_idx > 0) & (big_idx < len(rates)-1)]
    if len(big_idx) == 0:
        return
    same_dir_next = 0
    opp_dir_next = 0
    for i in big_idx:
        if direction[i] == 0:
            continue
        nd = np.sign(closes[i+1] - opens[i+1])
        if nd == direction[i]:
            same_dir_next += 1
        elif nd == -direction[i]:
            opp_dir_next += 1
    total = same_dir_next + opp_dir_next
    results[tf_name + "_breakout_followthrough"] = {
        "esik_carpani": mult,
        "buyuk_bar_sayisi": int(len(big_idx)),
        "sonraki_bar_ayni_yon_sayisi": same_dir_next,
        "sonraki_bar_ters_yon_sayisi": opp_dir_next,
        "ayni_yon_orani": round(same_dir_next/total, 3) if total else None,
    }

breakout_followthrough(m5, "M5")
breakout_followthrough(m1, "M1")

# ---- Ortalamaya donus (mean reversion) - fiyatin N-bar SMA'dan sapmasi sonrasi davranis (M5) ----
def mean_reversion_stats(rates, tf_name, window=20, dev_mult=2.0):
    closes = rates['close'].astype(float)
    if len(closes) < window + 5:
        return
    sma = np.convolve(closes, np.ones(window)/window, mode='valid')
    aligned_closes = closes[window-1:]
    std = np.array([closes[max(0,i-window+1):i+1].std() for i in range(window-1, len(closes))])
    dev = (aligned_closes - sma)
    upper_hits = np.where(dev > dev_mult*std)[0]
    lower_hits = np.where(dev < -dev_mult*std)[0]
    def forward_return(hits, horizon=5):
        rets = []
        for i in hits:
            real_i = i + window - 1
            if real_i + horizon < len(closes):
                rets.append(closes[real_i+horizon] - closes[real_i])
        return rets
    up_fwd = forward_return(upper_hits)
    low_fwd = forward_return(lower_hits)
    results[tf_name + "_mean_reversion"] = {
        "window": window, "dev_mult": dev_mult,
        "ust_sapma_sayisi": len(upper_hits),
        "ust_sapma_5bar_sonra_ort_getiri_pts": round(float(np.mean(up_fwd)/info.point), 2) if up_fwd else None,
        "alt_sapma_sayisi": len(lower_hits),
        "alt_sapma_5bar_sonra_ort_getiri_pts": round(float(np.mean(low_fwd)/info.point), 2) if low_fwd else None,
    }

mean_reversion_stats(m5, "M5")
mean_reversion_stats(m1, "M1")

# ---- Guncel spread / min-max (canli) ----
tick = mt5.symbol_info_tick(SYMBOL)
results["canli_spread_pts"] = int(round((tick.ask - tick.bid)/info.point))
results["point"] = info.point
results["digits"] = info.digits
results["contract_size"] = info.trade_contract_size

with open(r"C:\MilaYatirim\Justin\research_scalping_output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(json.dumps(results, ensure_ascii=False, indent=2))

mt5.shutdown()
