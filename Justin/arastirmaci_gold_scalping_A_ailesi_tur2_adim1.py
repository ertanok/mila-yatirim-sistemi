# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping, A Ailesi TUR 2 / ADIM 1 GIRISI (19 Temmuz 2026)
Tetikleyici: gorev_arastirmaci_justin_gold_scalping_A_ailesi_tur2_adim1_giris_20260719.md

Kapsam: Tam Yol1 pipeline turunun Arastirmaci adimi. Hipotez URETILMEZ.
1) M1 giris-zamanlama testi (baseline tetik: dokunus + bir-sonraki-barin-trend-yonunde-
   kapanmasi) - H1/M30 kanal FILTRESI (14 Temmuz formulu, DEGISTIRILMEDEN) icinde, M1'e
   projeksiyon.
2) Alternatif giris-tetigi tanimlari (M1/M5/M15 seviyelerinde, H1/M30 kanal FILTRESI SABIT):
   a) Coklu-teyit tetigi (N=2, N=3 ardisik bar, hepsi trend yonunde)
   b) Momentum-esikli tetik (govde/ATR14 >= 0.5x ve >= 1.0x, teyit barinda)
   Orijinal (dokunus+hemen-devam) tetikle YAN YANA karsilastirma.

Veri kaynagi: XM/MT5, dogrudan MetaTrader5 kutuphanesi, sembol GOLD, sunucu saati (GMT+3,
DST bu turde de bagimsiz dogrulanmadi).
Pivot/kanal formulu (H1/M30 tespiti) `arastirmaci_gold_scalping_pivot_kanal_tarama.py`
scriptinden HICBIR PARAMETRE DEGISTIRILMEDEN alinmistir (detect_channels fonksiyonu birebir
ayni).
Izolasyon: yalniz C:\\MilaYatirim\\mila-yatirim-sistemi\\Justin\\ altinda calisilir, tek veri
kaynagi MT5/GOLD.
"""
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime, timezone
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
point = info.point

TFS = {
    "M1": (mt5.TIMEFRAME_M1, 1),
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
    t0 = datetime.fromtimestamp(int(rates[0]['time']), tz=timezone.utc)
    t1 = datetime.fromtimestamp(int(rates[-1]['time']), tz=timezone.utc)
    results.setdefault("veri_araligi", {})[tf_name] = {
        "n_bar": int(len(rates)), "baslangic": str(t0), "bitis": str(t1)
    }
    print(tf_name, "n=", len(rates), t0, "->", t1)

# ============================================================
# M1 VERI DERINLIGI TESTI (m5_donem_dogrulama_raporu.md ile AYNI yontem)
# ============================================================
m1_derinlik = {}
p2 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 99999, 99999)
m1_derinlik["pos_99999_count_99999_n_bar"] = int(len(p2)) if p2 is not None else None
if p2 is not None and len(p2) > 0:
    m1_derinlik["pos_99999_ilk_bar"] = str(datetime.fromtimestamp(int(p2[0]['time']), tz=timezone.utc))
    m1_derinlik["pos_99999_son_bar"] = str(datetime.fromtimestamp(int(p2[-1]['time']), tz=timezone.utc))
p3 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 100000, 100)
m1_derinlik["pos_100000_count_100"] = None if p3 is None else int(len(p3))
m1_derinlik["pos_100000_last_error"] = str(mt5.last_error())
results["m1_veri_derinligi_testi"] = m1_derinlik
print("M1 derinlik testi:", m1_derinlik)

# ============================================================
# ORTAK YARDIMCI FONKSIYONLAR (14 Temmuz scriptiyle BIREBIR AYNI)
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
    return atr / point


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
# PIVOT/KANAL TESPITI - 14 Temmuz formulu, BIREBIR AYNI (degistirilmedi)
# ============================================================

CAP_MINUTES = 300 * 24 * 60


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
            pos += 1
            continue

        if direction == "up":
            ema_ok = ema50[confirm_idx] > ema200[confirm_idx]
            macd_ok = macd_l[confirm_idx] > macd_s[confirm_idx]
        else:
            ema_ok = ema50[confirm_idx] < ema200[confirm_idx]
            macd_ok = macd_l[confirm_idx] < macd_s[confirm_idx]

        if not (ema_ok and macd_ok):
            pos += 1
            continue

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
            "anchor_time": str(datetime.fromtimestamp(int(anchor_time), tz=timezone.utc)),
            "confirm_time": str(datetime.fromtimestamp(int(times[confirm_idx]), tz=timezone.utc)),
            "break_time": str(datetime.fromtimestamp(int(times[break_idx]), tz=timezone.utc)),
            "anchor_price": float(anchor_price), "confirm_price": float(closes[confirm_idx]),
            "break_price": float(closes[break_idx]),
            "duration_bars_anchor_to_break": int(break_idx - anchor),
            "duration_bars_confirm_to_break": int(break_idx - confirm_idx),
            "censored_veri_sonu": bool(censored),
        })

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

results["h1_m30_yapisal_kanal_ozet_bu_tur_n_kanal"] = {
    tf: {d: len(channel_results[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")
}

# ============================================================
# S1 GLOBAL MALIYET (M1/M5/M15)
# ============================================================


def s1_cost_global(tf_name):
    rates = raw[tf_name]
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
    }


S1_GLOBAL = {tf: s1_cost_global(tf) for tf in ("M1", "M5", "M15")}
results["s1_global_maliyet"] = {tf: {k: v for k, v in d.items() if k != "cost_pts_raw"}
                                 for tf, d in S1_GLOBAL.items()}

# ============================================================
# ORTAK: KANAL-PENCERE / DOKUNUS TESPITI (vektorize, tum tetik varyantlari icin
# paylasilan "dokunus" kumesi - dokunus tanimi HICBIR VARYANTTA DEGISMEZ)
# ============================================================


def get_touches_per_channel(htf_name, ltf_name, channels_htf, direction, touch_k=0.5):
    """Her ortusen kanal icin (lo, hi, dokunus_idx_array) dondurur. Dokunus tanimi
    14 Temmuz formuluyle BIREBIR AYNI: |kapanis - projeksiyon| <= 0.5*ATR14(ltf bar)."""
    htf_bar_min = TFS[htf_name][1]
    ltf_rates = raw[ltf_name]
    ltf_times = ltf_rates['time'].astype(np.int64)
    ltf_closes = ltf_rates['close'].astype(float)
    ltf_atr = ATR[ltf_name]
    sign = 1 if direction == "up" else -1
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    per_channel = []
    n_overlap = 0
    for c in channels_htf:
        confirm_t = int(datetime.strptime(c["confirm_time"], "%Y-%m-%d %H:%M:%S+00:00").timestamp())
        break_t = int(datetime.strptime(c["break_time"], "%Y-%m-%d %H:%M:%S+00:00").timestamp())
        if break_t < ltf_t0 or confirm_t > ltf_t1:
            continue
        n_overlap += 1
        win_start = max(confirm_t, ltf_t0)
        win_end = min(break_t, ltf_t1)
        lo = np.searchsorted(ltf_times, win_start, side="left")
        hi = np.searchsorted(ltf_times, win_end, side="right")
        if hi - lo < 3:
            continue

        anchor_price = c["anchor_price"]
        anchor_time = int(datetime.strptime(c["anchor_time"], "%Y-%m-%d %H:%M:%S+00:00").timestamp())
        slope_per_bar = c["slope_per_bar_pts"] * point
        slope_per_sec = slope_per_bar / (htf_bar_min * 60)

        idx = np.arange(lo, hi - 1)
        if len(idx) == 0:
            continue
        t_i = ltf_times[idx].astype(np.int64)
        atr_i = ltf_atr[idx]
        valid = ~np.isnan(atr_i)
        projected = anchor_price + slope_per_sec * (t_i - anchor_time)
        tol = touch_k * atr_i
        diff = ltf_closes[idx] - projected
        touch_mask = valid & (np.abs(diff) <= tol)
        touch_idx = idx[touch_mask]
        per_channel.append({"lo": int(lo), "hi": int(hi), "touch_idx": touch_idx})

    return per_channel, n_overlap


# ============================================================
# TETIK VARYANTLARI (dokunus kumesi ayni, sadece "teyit" farkli)
# ============================================================

def entries_baseline(ltf_name, per_channel, sign):
    closes = raw[ltf_name]['close'].astype(float)
    all_entries = []
    for ch in per_channel:
        ti = ch["touch_idx"]
        ti = ti[ti + 1 < ch["hi"]]
        if len(ti) == 0:
            continue
        cond = sign * (closes[ti + 1] - closes[ti]) > 0
        all_entries.extend((ti[cond] + 1).tolist())
    return sorted(set(all_entries))


def entries_multiconfirm(ltf_name, per_channel, sign, n_confirm):
    closes = raw[ltf_name]['close'].astype(float)
    all_entries = []
    for ch in per_channel:
        ti = ch["touch_idx"]
        ti = ti[ti + n_confirm < ch["hi"]]
        if len(ti) == 0:
            continue
        mask = np.ones(len(ti), dtype=bool)
        for k in range(n_confirm):
            a = closes[ti + k]
            b = closes[ti + k + 1]
            mask &= (sign * (b - a) > 0)
        all_entries.extend((ti[mask] + n_confirm).tolist())
    return sorted(set(all_entries))


def entries_momentum(ltf_name, per_channel, sign, k_atr):
    closes = raw[ltf_name]['close'].astype(float)
    opens = raw[ltf_name]['open'].astype(float)
    atr = ATR[ltf_name]
    all_entries = []
    for ch in per_channel:
        ti = ch["touch_idx"]
        ti = ti[ti + 1 < ch["hi"]]
        if len(ti) == 0:
            continue
        conf = ti + 1
        atr_conf = atr[conf]
        valid = ~np.isnan(atr_conf)
        body = np.abs(closes[conf] - opens[conf]) / point  # points cinsine cevir (ATR de points)
        dircond = sign * (closes[conf] - closes[ti]) > 0
        momcond = valid & (body >= k_atr * atr_conf)
        cond = dircond & momcond
        all_entries.extend((conf[cond]).tolist())
    return sorted(set(all_entries))


def entry_forward_test(ltf_name, entries, n_list_bars, cost_pts):
    closes = raw[ltf_name]['close'].astype(float)
    bar_min = TFS[ltf_name][1]
    n_total = len(closes)
    entries = np.array(entries, dtype=int)
    table = {}
    for N in n_list_bars:
        if len(entries) == 0:
            table[N] = None
            continue
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


def interpolate_threshold_minutes(tbl, threshold):
    points = sorted([(v["gercek_sure_dk"], v["oran_median_hedef_maliyet"])
                      for v in tbl.values() if v and v["oran_median_hedef_maliyet"] is not None],
                     key=lambda x: x[0])
    if not points:
        return None
    if points[0][1] >= threshold:
        return points[0][0]
    for idx in range(len(points) - 1):
        (t0, r0), (t1, r1) = points[idx], points[idx + 1]
        if r0 < threshold <= r1:
            frac = (threshold - r0) / (r1 - r0) if r1 != r0 else 0.0
            return t0 + frac * (t1 - t0)
    return None  # esik test edilen ufuklar icinde gecilmedi


N_LIST = {
    "M1": (1, 2, 4, 8, 16, 32, 64, 128, 256, 480),
    "M5": (1, 2, 4, 8, 16, 32, 64, 128),
    "M15": (1, 2, 4, 8, 16, 32, 64),
}

# ============================================================
# 1) M1 BASELINE GIRIS-ZAMANLAMA TESTI (H1/M30 -> M1)
# ============================================================

giris_testi_m1_baseline = {}
for htf in ("H1", "M30"):
    giris_testi_m1_baseline[htf] = {}
    for direction in ("up", "down"):
        sign = 1 if direction == "up" else -1
        per_channel, n_overlap = get_touches_per_channel(htf, "M1", channel_results[htf][direction], direction)
        entries = entries_baseline("M1", per_channel, sign)
        tbl = entry_forward_test("M1", entries, N_LIST["M1"], S1_GLOBAL["M1"]["cost_pts_raw"])
        giris_testi_m1_baseline[htf][direction] = {
            "n_htf_kanal_ortusen": n_overlap,
            "n_giris_tetigi": len(entries),
            "ufuk_tablosu": tbl,
            "esik_15x_dk": interpolate_threshold_minutes(tbl, 15.0),
            "esik_20x_dk": interpolate_threshold_minutes(tbl, 20.0),
        }
        print(f"M1 baseline {htf} {direction}: n_overlap={n_overlap} n_giris={len(entries)}")

results["giris_testi_m1_baseline"] = giris_testi_m1_baseline

# ============================================================
# 2) ALTERNATIF GIRIS-TETIGI TANIMLARI (M1/M5/M15, H1/M30 SABIT)
# ============================================================

alternatif = {"coklu_teyit_N2": {}, "coklu_teyit_N3": {},
              "momentum_k05": {}, "momentum_k10": {},
              "baseline_karsilastirma": {}}

for ltf in ("M1", "M5", "M15"):
    for key in alternatif:
        alternatif[key][ltf] = {}
    for htf in ("H1", "M30"):
        for key in alternatif:
            alternatif[key][ltf][htf] = {}
        for direction in ("up", "down"):
            sign = 1 if direction == "up" else -1
            per_channel, n_overlap = get_touches_per_channel(htf, ltf, channel_results[htf][direction], direction)
            cost_raw = S1_GLOBAL[ltf]["cost_pts_raw"]

            # baseline (orijinal, karsilastirma icin bu turde YENIDEN hesaplandi - ayni formul)
            e_base = entries_baseline(ltf, per_channel, sign)
            tbl_base = entry_forward_test(ltf, e_base, N_LIST[ltf], cost_raw)
            alternatif["baseline_karsilastirma"][ltf][htf][direction] = {
                "n_htf_kanal_ortusen": n_overlap, "n_giris_tetigi": len(e_base),
                "ufuk_tablosu": tbl_base,
                "esik_15x_dk": interpolate_threshold_minutes(tbl_base, 15.0),
                "esik_20x_dk": interpolate_threshold_minutes(tbl_base, 20.0),
            }

            # coklu-teyit N=2, N=3
            for n_confirm, key in ((2, "coklu_teyit_N2"), (3, "coklu_teyit_N3")):
                e = entries_multiconfirm(ltf, per_channel, sign, n_confirm)
                tbl = entry_forward_test(ltf, e, N_LIST[ltf], cost_raw)
                alternatif[key][ltf][htf][direction] = {
                    "n_htf_kanal_ortusen": n_overlap, "n_giris_tetigi": len(e),
                    "ufuk_tablosu": tbl,
                    "esik_15x_dk": interpolate_threshold_minutes(tbl, 15.0),
                    "esik_20x_dk": interpolate_threshold_minutes(tbl, 20.0),
                }

            # momentum-esikli k=0.5, k=1.0
            for k_atr, key in ((0.5, "momentum_k05"), (1.0, "momentum_k10")):
                e = entries_momentum(ltf, per_channel, sign, k_atr)
                tbl = entry_forward_test(ltf, e, N_LIST[ltf], cost_raw)
                alternatif[key][ltf][htf][direction] = {
                    "n_htf_kanal_ortusen": n_overlap, "n_giris_tetigi": len(e),
                    "ufuk_tablosu": tbl,
                    "esik_15x_dk": interpolate_threshold_minutes(tbl, 15.0),
                    "esik_20x_dk": interpolate_threshold_minutes(tbl, 20.0),
                }

            print(f"alternatif {ltf} {htf} {direction} tamamlandi "
                  f"(n_overlap={n_overlap}, baseline_n={len(e_base)})")

results["alternatif_giris_tetigi"] = alternatif

with open(r"C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_A_ailesi_tur2_adim1_output.json",
          "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI. JSON yazildi.")
mt5.shutdown()
