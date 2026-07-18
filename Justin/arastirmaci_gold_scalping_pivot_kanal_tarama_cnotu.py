# -*- coding: utf-8 -*-
"""
EK (C-NOTU) - Kanal kirilimi sonrasi gozlemsel not.
Ana script (arastirmaci_gold_scalping_pivot_kanal_tarama.py) ile AYNI algoritma/parametreler
tekrar calistirilir (yeniden-uretilebilirlik), sadece break_idx sonrasi bir gozlem eklenir.
Ayri hipotez/model KURULMAZ - sadece gozlemsel not (gorev Madde 5).
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

TFS = {"H1": (mt5.TIMEFRAME_H1, 60), "M30": (mt5.TIMEFRAME_M30, 30)}
raw = {}
for tf_name, (tf_const, bar_min) in TFS.items():
    raw[tf_name] = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)


def ema(values, span):
    return pd.Series(values).ewm(span=span, adjust=False).mean().values


def macd(values, fast=12, slow=26, signal=9):
    macd_line = ema(values, fast) - ema(values, slow)
    signal_line = pd.Series(macd_line).ewm(span=signal, adjust=False).mean().values
    return macd_line, signal_line


def atr_series_pts(rates, window=14):
    highs = rates['high'].astype(float); lows = rates['low'].astype(float); closes = rates['close'].astype(float)
    prev_close = np.roll(closes, 1); prev_close[0] = closes[0]
    tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
    return pd.Series(tr).rolling(window, min_periods=window).mean().values / point


def find_swings(rates, n=5):
    highs = rates['high'].astype(float); lows = rates['low'].astype(float)
    m = len(highs)
    swing_high = np.zeros(m, dtype=bool); swing_low = np.zeros(m, dtype=bool)
    for i in range(n, m - n):
        if highs[i] == highs[i - n:i + n + 1].max():
            swing_high[i] = True
        if lows[i] == lows[i - n:i + n + 1].min():
            swing_low[i] = True
    return swing_high, swing_low


ATR = {tf: atr_series_pts(raw[tf]) for tf in TFS}
EMA50 = {tf: ema(raw[tf]['close'].astype(float), 50) for tf in TFS}
EMA200 = {tf: ema(raw[tf]['close'].astype(float), 200) for tf in TFS}
MACD_LINE = {}; MACD_SIG = {}
for tf in TFS:
    ml, sl = macd(raw[tf]['close'].astype(float), 12, 26, 9)
    MACD_LINE[tf] = ml; MACD_SIG[tf] = sl
SWINGS = {}
for tf in TFS:
    sh, sl = find_swings(raw[tf], n=5)
    SWINGS[tf] = {"swing_high": sh, "swing_low": sl}

CAP_MINUTES = 300 * 24 * 60


def detect_channels(tf_name, direction, min_touches=3, touch_k=0.5):
    rates = raw[tf_name]; bar_min = TFS[tf_name][1]
    closes = rates['close'].astype(float); highs = rates['high'].astype(float); lows = rates['low'].astype(float)
    times = rates['time'].astype(np.int64)
    atr = ATR[tf_name]; ema50 = EMA50[tf_name]; ema200 = EMA200[tf_name]
    macd_l = MACD_LINE[tf_name]; macd_s = MACD_SIG[tf_name]
    if direction == "up":
        sign = 1; swing_mask = SWINGS[tf_name]["swing_low"]; price_arr = lows
    else:
        sign = -1; swing_mask = SWINGS[tf_name]["swing_high"]; price_arr = highs
    swing_idx = np.where(swing_mask)[0]
    cap_bars = CAP_MINUTES // bar_min
    m = len(swing_idx); n_total = len(closes)
    channels = []
    pos = 0
    while pos < m - 2:
        anchor = swing_idx[pos]
        if np.isnan(atr[anchor]):
            pos += 1; continue
        anchor_price = price_arr[anchor]; anchor_time = times[anchor]
        j = pos + 1; second = None
        while j < m:
            c = swing_idx[j]
            if times[c] - anchor_time > cap_bars * bar_min * 60:
                break
            if np.isnan(atr[c]):
                j += 1; continue
            delta = price_arr[c] - anchor_price
            if sign * delta > 0:
                second = c; break
            j += 1
        if second is None:
            pos += 1; continue
        slope = (price_arr[second] - anchor_price) / (second - anchor)
        touches = [anchor, second]; confirm_idx = None
        k = j + 1
        while k < m:
            c = swing_idx[k]
            if times[c] - anchor_time > cap_bars * bar_min * 60:
                break
            if np.isnan(atr[c]):
                k += 1; continue
            projected = anchor_price + slope * (c - anchor)
            tol = touch_k * atr[c]
            diff = price_arr[c] - projected
            if sign * diff < -tol:
                break
            elif abs(diff) <= tol:
                touches.append(c)
                if len(touches) >= min_touches and confirm_idx is None:
                    confirm_idx = c
            k += 1
        if confirm_idx is None:
            pos += 1; continue
        if direction == "up":
            ema_ok = ema50[confirm_idx] > ema200[confirm_idx]; macd_ok = macd_l[confirm_idx] > macd_s[confirm_idx]
        else:
            ema_ok = ema50[confirm_idx] < ema200[confirm_idx]; macd_ok = macd_l[confirm_idx] < macd_s[confirm_idx]
        if not (ema_ok and macd_ok):
            pos += 1; continue
        break_idx = None
        limit_idx = min(n_total - 1, anchor + cap_bars)
        for i in range(confirm_idx + 1, limit_idx + 1):
            projected = anchor_price + slope * (i - anchor)
            tol = touch_k * atr[i] if not np.isnan(atr[i]) else touch_k * np.nanmedian(atr)
            diff = closes[i] - projected
            if sign * diff < -tol:
                break_idx = i; break
        censored = False
        if break_idx is None:
            break_idx = limit_idx; censored = True
        channels.append({"anchor_idx": int(anchor), "confirm_idx": int(confirm_idx),
                          "break_idx": int(break_idx), "censored": censored})
        next_pos = np.searchsorted(swing_idx, break_idx, side="right")
        pos = max(next_pos, pos + 1)
    return channels


out = {}
for tf_name in ("H1", "M30"):
    bar_min = TFS[tf_name][1]
    closes = raw[tf_name]['close'].astype(float)
    n_total = len(closes)
    horizons_days = [1, 3, 7]
    tf_out = {}
    for direction in ("up", "down"):
        sign = 1 if direction == "up" else -1
        chs = detect_channels(tf_name, direction)
        non_censored = [c for c in chs if not c["censored"]]
        h_out = {}
        for d in horizons_days:
            N = int(d * 24 * 60 / bar_min)
            reversal = []
            continuation = []
            for c in non_censored:
                bi = c["break_idx"]
                if bi + N >= n_total:
                    continue
                p0 = closes[bi]
                p1 = closes[bi + N]
                move = sign * (p1 - p0)  # pozitif ise TREND YONUNDE devam (kirilime ragmen), negatif ise TERSINE-DONUS (reversal, trend aleyhine)
                if move < 0:
                    reversal.append(1)
                else:
                    reversal.append(0)
            if reversal:
                h_out[f"{d}_gun_sonrasi"] = {
                    "n": len(reversal),
                    "kirilim_sonrasi_tersine_donus_orani": round(float(np.mean(reversal)), 4),
                }
        tf_out[direction] = {"n_kirilim_censored_olmayan": len(non_censored), "kirilim_sonrasi": h_out}
    out[tf_name] = tf_out

with open(r"C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_cnotu_output.json",
          "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1))
mt5.shutdown()
