# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping ML/Feature-Tabanli Arastirma (M15+), TUR 2 (v2)
Amac: Tam Tur 1'de KULLANILMAMIS feature ailelerini (rejim/ADX, gorece fiyat yapisi/pivot-S-R,
mikro-yapi/tick-kural-tabanli proxy, capraz-piyasa/DXY) ve alternatif etiket tanimlarini (3-sinif,
regresyon-hedef) olcmek. Veri kaynagi: XM/MT5, dogrudan MetaTrader5 kutuphanesi.
Izolasyon notu: MilaGold/Lisa/Signal GPT'ye ait hicbir dosya okunmadi/kullanilmadi. Yalniz XM/MT5
sembolleri (GOLD, USDX-SEP26) kullanildi.
Kutuphaneler: bu ortamda artik pandas/numpy/lightgbm/scikit-learn KURULU (v1'deki kisit ortadan
kalkti, ayrica dogrulandi) - bu script pandas/numpy kullanir, gercek model egitimi YAPMAZ (bu hala
Backtest Muhendisi'nin isi), sadece nedensel feature/label dagilim olcumu yapar.
"""
import json
import time
import datetime as dt

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point

results = {}
results["meta"] = {
    "symbol": SYMBOL,
    "point": POINT,
    "digits": info.digits,
    "contract_size": info.trade_contract_size,
}

# =====================================================================================
# 0) GOLD M15 tam gecmis (nedensel hesaplamalarin tabani)
# =====================================================================================
m15_raw = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 99999)
assert m15_raw is not None and len(m15_raw) > 0, "M15 veri cekilemedi"

df = pd.DataFrame(m15_raw)
df["dt"] = pd.to_datetime(df["time"], unit="s")  # NOT: epoch dogrudan UTC gibi okunuyor
# (sunucu saati GMT+3 varsayimi, DST bagimsiz ayrica dogrulanmadi - v1 ile AYNI SINIR/varsayim)
df = df.sort_values("time").reset_index(drop=True)

results["meta"]["m15_n"] = int(len(df))
results["meta"]["m15_start"] = df["dt"].iloc[0].isoformat()
results["meta"]["m15_end"] = df["dt"].iloc[-1].isoformat()

o = df["open"].to_numpy(float)
h = df["high"].to_numpy(float)
l = df["low"].to_numpy(float)
c = df["close"].to_numpy(float)
vol = df["tick_volume"].to_numpy(float)
spread = df["spread"].to_numpy(float)
n = len(df)

prev_c = np.roll(c, 1)
prev_c[0] = c[0]
tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
tr_pts = tr / POINT


def wilder_smooth(x, period):
    """Wilder's smoothing, nedensel (i. deger sadece 0..i kullanir)."""
    out = np.full(len(x), np.nan)
    if len(x) < period:
        return out
    first = np.nansum(x[:period])
    out[period - 1] = first
    for i in range(period, len(x)):
        out[i] = out[i - 1] - (out[i - 1] / period) + x[i]
    return out


# =====================================================================================
# 1) YENI FEATURE AILESI - REJIM/ADX (Tam Tur 1'de KULLANILMADI)
# =====================================================================================
ADX_N = 14
up_move = h - np.roll(h, 1)
down_move = np.roll(l, 1) - l
up_move[0] = 0.0
down_move[0] = 0.0
plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

tr_smooth = wilder_smooth(tr_pts, ADX_N)
plus_dm_smooth = wilder_smooth(plus_dm / POINT, ADX_N)
minus_dm_smooth = wilder_smooth(minus_dm / POINT, ADX_N)

with np.errstate(divide="ignore", invalid="ignore"):
    plus_di = 100.0 * plus_dm_smooth / tr_smooth
    minus_di = 100.0 * minus_dm_smooth / tr_smooth
    dx = 100.0 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
dx = np.nan_to_num(dx, nan=0.0)

# ADX = DX'in kendisinin Wilder-smoothed ortalamasi (ilk deger = ilk ADX_N DX'in ortalamasi,
# sonrasi Wilder rekursiyonu) - standart tanim, nedensel.
adx = np.full(n, np.nan)
first_valid = ADX_N - 1 + ADX_N  # DX, ADX_N-1'den itibaren gecerli; ADX icin bir ADX_N daha gerek
if n > first_valid:
    adx[first_valid] = np.mean(dx[ADX_N - 1: first_valid + 1])
    for i in range(first_valid + 1, n):
        adx[i] = (adx[i - 1] * (ADX_N - 1) + dx[i]) / ADX_N

TREND_TH = 25.0
RANGE_TH = 20.0
regime = np.full(n, "gecis", dtype=object)  # transitional/gecis (20<=ADX<=25 veya NaN)
regime[np.nan_to_num(adx, nan=-1) > TREND_TH] = "trend"
regime[(np.nan_to_num(adx, nan=-1) < RANGE_TH) & (~np.isnan(adx))] = "range"
regime[np.isnan(adx)] = "nan"

valid_adx = ~np.isnan(adx)
adx_valid = adx[valid_adx]
regime_valid = regime[valid_adx]

# Rejim gecis mesafesi (son rejim degisiminden bu yana gecen bar sayisi), nedensel
bars_since_change = np.full(n, np.nan)
last_regime = None
counter = 0
for i in range(n):
    if regime[i] == "nan":
        continue
    if last_regime is None or regime[i] != last_regime:
        counter = 0
        last_regime = regime[i]
    else:
        counter += 1
    bars_since_change[i] = counter

trend_n = int(np.sum(regime_valid == "trend"))
range_n = int(np.sum(regime_valid == "range"))
gecis_n = int(np.sum(regime_valid == "gecis"))

# Rejime gore sonraki-8-bar (2 saat) MUTLAK getiri (ATR-benzeri buyukluk olcumu, BULGU4/v1 ile
# ayni yapida ama ADX-tabanli rejimle, hacim/ATR-trailing degil)
FWD_N = 8
fwd_abs_ret = np.full(n, np.nan)
for i in range(n - FWD_N):
    fwd_abs_ret[i] = abs(c[i + FWD_N] - c[i]) / POINT

mask_trend = valid_adx & (regime == "trend") & ~np.isnan(fwd_abs_ret)
mask_range = valid_adx & (regime == "range") & ~np.isnan(fwd_abs_ret)
mask_gecis = valid_adx & (regime == "gecis") & ~np.isnan(fwd_abs_ret)

# Rejime gore yon-tutarliligi: mevcut bar kapanis yonu (c[i]-c[i-1]) ile sonraki 8-bar getiri
# ayni yonde mi (trend-devam) oranı
sign_now = np.sign(c - prev_c)
sign_fwd = np.full(n, np.nan)
for i in range(n - FWD_N):
    sign_fwd[i] = np.sign(c[i + FWD_N] - c[i])

def continuation_rate(mask):
    idx = mask & (sign_now != 0) & ~np.isnan(sign_fwd) & (sign_fwd != 0)
    if idx.sum() == 0:
        return None, 0
    rate = float(np.mean(sign_now[idx] == sign_fwd[idx]))
    return rate, int(idx.sum())

cont_trend, cont_trend_n = continuation_rate(mask_trend)
cont_range, cont_range_n = continuation_rate(mask_range)
cont_gecis, cont_gecis_n = continuation_rate(mask_gecis)

results["regim_adx"] = {
    "adx_period": ADX_N,
    "trend_threshold": TREND_TH,
    "range_threshold": RANGE_TH,
    "n_valid": int(valid_adx.sum()),
    "trend_n": trend_n,
    "range_n": range_n,
    "gecis_n": gecis_n,
    "trend_oran": trend_n / valid_adx.sum(),
    "range_oran": range_n / valid_adx.sum(),
    "gecis_oran": gecis_n / valid_adx.sum(),
    "adx_medyan": float(np.median(adx_valid)),
    "adx_p10_p90": [float(np.percentile(adx_valid, 10)), float(np.percentile(adx_valid, 90))],
    "bars_since_change_medyan": float(np.nanmedian(bars_since_change)),
    "bars_since_change_p90": float(np.nanpercentile(bars_since_change, 90)),
    "fwd8bar_abs_ret_trend_medyan": float(np.nanmedian(fwd_abs_ret[mask_trend])) if mask_trend.sum() else None,
    "fwd8bar_abs_ret_range_medyan": float(np.nanmedian(fwd_abs_ret[mask_range])) if mask_range.sum() else None,
    "fwd8bar_abs_ret_gecis_medyan": float(np.nanmedian(fwd_abs_ret[mask_gecis])) if mask_gecis.sum() else None,
    "fwd8bar_abs_ret_trend_n": int(mask_trend.sum()),
    "fwd8bar_abs_ret_range_n": int(mask_range.sum()),
    "fwd8bar_abs_ret_gecis_n": int(mask_gecis.sum()),
    "continuation_rate_trend": cont_trend,
    "continuation_rate_trend_n": cont_trend_n,
    "continuation_rate_range": cont_range,
    "continuation_rate_range_n": cont_range_n,
    "continuation_rate_gecis": cont_gecis,
    "continuation_rate_gecis_n": cont_gecis_n,
}

print("REJIM/ADX tamam", flush=True)

# =====================================================================================
# 2) YENI FEATURE AILESI - GORECE FIYAT YAPISI (Gunluk/Haftalik Pivot, N-gun S/R)
#    Tam Tur 1'de YOKTU. Tumu nedensel: sadece ONCEKI TAMAMLANMIS gun/hafta OHLC kullanilir.
# =====================================================================================
df["date"] = df["dt"].dt.date
daily = df.groupby("date").agg(d_open=("open", "first"), d_high=("high", "max"),
                                d_low=("low", "min"), d_close=("close", "last")).reset_index()
daily["pivot"] = (daily["d_high"] + daily["d_low"] + daily["d_close"]) / 3.0
daily["r1"] = 2 * daily["pivot"] - daily["d_low"]
daily["s1"] = 2 * daily["pivot"] - daily["d_high"]
# ONCEKI gunun pivot/r1/s1'i BUGUNE atanir (nedensel, shift(1))
daily["pivot_for_next_day"] = daily["pivot"].shift(1)
daily["r1_for_next_day"] = daily["r1"].shift(1)
daily["s1_for_next_day"] = daily["s1"].shift(1)
# 20-gunluk (onceki tamamlanmis gunler) rolling high/low, bugune (shift(1) sonrasi) atanir
daily["roll20_high"] = daily["d_high"].rolling(20).max().shift(1)
daily["roll20_low"] = daily["d_low"].rolling(20).min().shift(1)

date_map = daily.set_index("date")[["pivot_for_next_day", "r1_for_next_day", "s1_for_next_day",
                                     "roll20_high", "roll20_low"]]
df = df.merge(date_map, left_on="date", right_index=True, how="left")

dist_pivot_pts = (c - df["pivot_for_next_day"].to_numpy(float)) / POINT
dist_r1_pts = (c - df["r1_for_next_day"].to_numpy(float)) / POINT
dist_s1_pts = (c - df["s1_for_next_day"].to_numpy(float)) / POINT
dist_roll20_high_pts = (df["roll20_high"].to_numpy(float) - c) / POINT
dist_roll20_low_pts = (c - df["roll20_low"].to_numpy(float)) / POINT

valid_pivot = ~np.isnan(dist_pivot_pts)
valid_roll20 = ~np.isnan(dist_roll20_high_pts)

# Weekly pivot (ISO hafta), ayni mantik
df["iso_year"] = df["dt"].dt.isocalendar().year
df["iso_week"] = df["dt"].dt.isocalendar().week
weekly = df.groupby(["iso_year", "iso_week"]).agg(
    w_high=("high", "max"), w_low=("low", "min"), w_close=("close", "last")).reset_index()
weekly = weekly.sort_values(["iso_year", "iso_week"]).reset_index(drop=True)
weekly["w_pivot"] = (weekly["w_high"] + weekly["w_low"] + weekly["w_close"]) / 3.0
weekly["w_pivot_for_next_week"] = weekly["w_pivot"].shift(1)
wk_map = weekly.set_index(["iso_year", "iso_week"])[["w_pivot_for_next_week"]]
df = df.merge(wk_map, left_on=["iso_year", "iso_week"], right_index=True, how="left")
dist_wpivot_pts = (c - df["w_pivot_for_next_week"].to_numpy(float)) / POINT
valid_wpivot = ~np.isnan(dist_wpivot_pts)

# BULGU: bu mesafelerin sonraki-8-bar yon-hizali getiriyle iliskisi (pivot ustunde/altinda mi
# ayrimi -> sonraki hareket farkli mi)
above_pivot = valid_pivot & (dist_pivot_pts > 0) & ~np.isnan(fwd_abs_ret)
below_pivot = valid_pivot & (dist_pivot_pts < 0) & ~np.isnan(fwd_abs_ret)
fwd_signed_ret = np.full(n, np.nan)
for i in range(n - FWD_N):
    fwd_signed_ret[i] = (c[i + FWD_N] - c[i]) / POINT

results["gorece_fiyat_yapisi"] = {
    "n_valid_daily_pivot": int(valid_pivot.sum()),
    "n_valid_weekly_pivot": int(valid_wpivot.sum()),
    "n_valid_roll20_sr": int(valid_roll20.sum()),
    "dist_pivot_pts_medyan_abs": float(np.nanmedian(np.abs(dist_pivot_pts))),
    "dist_r1_pts_medyan_abs": float(np.nanmedian(np.abs(dist_r1_pts))),
    "dist_s1_pts_medyan_abs": float(np.nanmedian(np.abs(dist_s1_pts))),
    "dist_wpivot_pts_medyan_abs": float(np.nanmedian(np.abs(dist_wpivot_pts))),
    "dist_roll20_high_pts_medyan": float(np.nanmedian(dist_roll20_high_pts)),
    "dist_roll20_low_pts_medyan": float(np.nanmedian(dist_roll20_low_pts)),
    "above_pivot_fwd8_signed_ret_medyan": float(np.nanmedian(fwd_signed_ret[above_pivot])) if above_pivot.sum() else None,
    "above_pivot_n": int(above_pivot.sum()),
    "below_pivot_fwd8_signed_ret_medyan": float(np.nanmedian(fwd_signed_ret[below_pivot])) if below_pivot.sum() else None,
    "below_pivot_n": int(below_pivot.sum()),
    # Roll20 high/low'a yakinlik (en yakin %10'luk dilim) sonrasi davranis
}

# roll20 high/low'a yakin barlarda (ust/alt bandin en yakin %10'u) sonraki 8-bar signed getiri
near_high_th = np.nanpercentile(dist_roll20_high_pts[valid_roll20], 10)
near_low_th = np.nanpercentile(dist_roll20_low_pts[valid_roll20], 10)
near_high_mask = valid_roll20 & (dist_roll20_high_pts <= near_high_th) & ~np.isnan(fwd_signed_ret)
near_low_mask = valid_roll20 & (dist_roll20_low_pts <= near_low_th) & ~np.isnan(fwd_signed_ret)
results["gorece_fiyat_yapisi"]["near_roll20_high_fwd8_signed_ret_medyan"] = float(np.nanmedian(fwd_signed_ret[near_high_mask])) if near_high_mask.sum() else None
results["gorece_fiyat_yapisi"]["near_roll20_high_n"] = int(near_high_mask.sum())
results["gorece_fiyat_yapisi"]["near_roll20_low_fwd8_signed_ret_medyan"] = float(np.nanmedian(fwd_signed_ret[near_low_mask])) if near_low_mask.sum() else None
results["gorece_fiyat_yapisi"]["near_roll20_low_n"] = int(near_low_mask.sum())

print("GORECE FIYAT YAPISI tamam", flush=True)

# =====================================================================================
# 3) ETIKET ALTERNATIFLERI - 3 SINIF (deadzone) ve REGRESYON HEDEFI (N=8 bar, 2 saat)
# =====================================================================================
atr14_pts = pd.Series(tr_pts).rolling(14).mean().to_numpy()  # basit (Wilder degil) ATR, sadece
# etiket deadzone esigi icin referans buyukluk - nedensel (rolling, ileri bakis yok)

DEADZONE_K = 0.3  # +-0.3xATR14 icinde "notr"
label3 = np.full(n, np.nan)
valid_label = ~np.isnan(fwd_signed_ret) & ~np.isnan(atr14_pts)
th = DEADZONE_K * atr14_pts
label3_arr = np.where(fwd_signed_ret > th, 1, np.where(fwd_signed_ret < -th, -1, 0))
label3_arr = label3_arr.astype(float)
label3_arr[~valid_label] = np.nan

up_n = int(np.sum(label3_arr == 1))
down_n = int(np.sum(label3_arr == -1))
neutral_n = int(np.sum(label3_arr == 0))
tot_label = up_n + down_n + neutral_n

reg_target = fwd_signed_ret[valid_label]
reg_target_atr_norm = (fwd_signed_ret / atr14_pts)[valid_label]

results["etiket_alternatifleri"] = {
    "n_valid": int(tot_label),
    "deadzone_k": DEADZONE_K,
    "3sinif_yukari_n": up_n,
    "3sinif_asagi_n": down_n,
    "3sinif_notr_n": neutral_n,
    "3sinif_yukari_oran": up_n / tot_label if tot_label else None,
    "3sinif_asagi_oran": down_n / tot_label if tot_label else None,
    "3sinif_notr_oran": neutral_n / tot_label if tot_label else None,
    "regresyon_hedef_pts_ortalama": float(np.mean(reg_target)),
    "regresyon_hedef_pts_std": float(np.std(reg_target)),
    "regresyon_hedef_pts_p10_p90": [float(np.percentile(reg_target, 10)), float(np.percentile(reg_target, 90))],
    "regresyon_hedef_atr_norm_ortalama": float(np.mean(reg_target_atr_norm)),
    "regresyon_hedef_atr_norm_std": float(np.std(reg_target_atr_norm)),
    "regresyon_hedef_atr_norm_p10_p90": [float(np.percentile(reg_target_atr_norm, 10)), float(np.percentile(reg_target_atr_norm, 90))],
}

# Alternatif deadzone (0.15xATR, daha dar) - hassasiyet check
for dz in [0.15, 0.5]:
    th2 = dz * atr14_pts
    l3 = np.where(fwd_signed_ret > th2, 1, np.where(fwd_signed_ret < -th2, -1, 0)).astype(float)
    l3[~valid_label] = np.nan
    u_n = int(np.sum(l3 == 1)); d_n = int(np.sum(l3 == -1)); ntr_n = int(np.sum(l3 == 0))
    tot = u_n + d_n + ntr_n
    results["etiket_alternatifleri"][f"deadzone_{dz}_yukari_oran"] = u_n / tot if tot else None
    results["etiket_alternatifleri"][f"deadzone_{dz}_asagi_oran"] = d_n / tot if tot else None
    results["etiket_alternatifleri"][f"deadzone_{dz}_notr_oran"] = ntr_n / tot if tot else None

print("ETIKET ALTERNATIFLERI tamam", flush=True)

# =====================================================================================
# 4) CAPRAZ-PIYASA / DXY (USDX-SEP26 futures proxy) - VERI ERISIMI KISITLI (kisa gecmis)
# =====================================================================================
dxy_section = {"veri_erisimi": None}
dxy_symbol = "USDX-SEP26"
if mt5.symbol_select(dxy_symbol, True):
    dxy_raw = mt5.copy_rates_from_pos(dxy_symbol, mt5.TIMEFRAME_M15, 0, 99999)
    if dxy_raw is not None and len(dxy_raw) > 0:
        dxy_df = pd.DataFrame(dxy_raw)
        dxy_df["dt"] = pd.to_datetime(dxy_df["time"], unit="s")
        dxy_df = dxy_df.sort_values("time").reset_index(drop=True)
        dxy_section["veri_erisimi"] = "kismi (futures kontrat, kisa gecmis)"
        dxy_section["n"] = int(len(dxy_df))
        dxy_section["start"] = dxy_df["dt"].iloc[0].isoformat()
        dxy_section["end"] = dxy_df["dt"].iloc[-1].isoformat()

        # GOLD barlarini ayni epoch-time uzerinden birlestir (M15 grid'leri ayni epoch tabanina
        # hizali olmali, exact merge dene; olmazsa merge_asof nedensel/causal kullan)
        gold_small = df[["time", "dt", "close"]].rename(columns={"close": "gold_close"})
        dxy_small = dxy_df[["time", "dt", "close"]].rename(columns={"close": "dxy_close"})
        merged_exact = pd.merge(gold_small, dxy_small, on="time", how="inner")
        dxy_section["exact_merge_n"] = int(len(merged_exact))

        if len(merged_exact) > 50:
            g_ret = merged_exact["gold_close"].pct_change()
            d_ret = merged_exact["dxy_close"].pct_change()
            valid = g_ret.notna() & d_ret.notna()
            corr_all = float(g_ret[valid].corr(d_ret[valid]))
            dxy_section["m15_return_correlation_tam_ortusme"] = corr_all
            dxy_section["m15_return_correlation_n"] = int(valid.sum())

            # 20-bar rolling korelasyon dagilimi (nedensel pencere, backward-looking - bir onceki
            # 20 M15-bar'in getiri korelasyonu, ileri bakis yok)
            roll_corr = g_ret.rolling(20).corr(d_ret)
            dxy_section["rolling20_corr_medyan"] = float(roll_corr.median())
            dxy_section["rolling20_corr_p10_p90"] = [float(roll_corr.quantile(0.10)), float(roll_corr.quantile(0.90))]

            # GOLD'un sonraki-8-bar getirisi ile ONCEKI 8-bar DXY getirisi arasindaki iliski
            # (nedensel: DXY gecmisi -> GOLD gelecegi, capraz-piyasa "momentum-uyum" testi)
            merged_exact = merged_exact.reset_index(drop=True)
            g_close = merged_exact["gold_close"].to_numpy(float)
            d_close = merged_exact["dxy_close"].to_numpy(float)
            m = len(merged_exact)
            dxy_past8_ret = np.full(m, np.nan)
            gold_fwd8_ret = np.full(m, np.nan)
            for i in range(8, m - 8):
                dxy_past8_ret[i] = (d_close[i] - d_close[i - 8]) / d_close[i - 8]
                gold_fwd8_ret[i] = (g_close[i + 8] - g_close[i]) / g_close[i]
            v2 = ~np.isnan(dxy_past8_ret) & ~np.isnan(gold_fwd8_ret)
            if v2.sum() > 30:
                dxy_section["dxy_past8_vs_gold_fwd8_corr"] = float(np.corrcoef(dxy_past8_ret[v2], gold_fwd8_ret[v2])[0, 1])
                dxy_section["dxy_past8_vs_gold_fwd8_n"] = int(v2.sum())
    else:
        dxy_section["veri_erisimi"] = "yok (symbol_select basarili ama veri donmedi)"
else:
    dxy_section["veri_erisimi"] = "yok (symbol_select basarisiz)"

results["capraz_piyasa_dxy"] = dxy_section
print("DXY tamam:", dxy_section.get("veri_erisimi"), flush=True)

# =====================================================================================
# 5) MIKRO-YAPI (TICK-KURAL-TABANLI PROXY) - SINIRLI PENCERE (son ~20 islem gunu)
#    Gercek order-flow/trade-side verisi YOK (bu feed quote-tick: bid/ask, volume=0, last=0) -
#    bu nedenle "tick-rule" bid/ask ORTA-FIYAT (mid) hareketine dayali bir PROXY'dir, gercek
#    alici/satici baskisi degil.
# =====================================================================================
TICK_DAYS = 20
end_date = df["dt"].iloc[-1].normalize() + pd.Timedelta(days=1)
day_list = [end_date - pd.Timedelta(days=k) for k in range(1, TICK_DAYS + 1)]

bucket_records = []
t0 = time.time()
for day_end in day_list:
    day_start = day_end - pd.Timedelta(days=1)
    ticks = mt5.copy_ticks_range(SYMBOL, day_start.to_pydatetime(), day_end.to_pydatetime(), mt5.COPY_TICKS_ALL)
    if ticks is None or len(ticks) == 0:
        continue
    tdf = pd.DataFrame(ticks)
    tdf = tdf[(tdf["bid"] > 0) & (tdf["ask"] > 0)]
    if len(tdf) == 0:
        continue
    tdf["mid"] = (tdf["bid"] + tdf["ask"]) / 2.0
    tdf["spr"] = tdf["ask"] - tdf["bid"]
    tdf["bucket"] = (tdf["time"] // 900) * 900
    mid_diff = tdf["mid"].diff()
    sign = np.sign(mid_diff)
    sign = sign.replace(0, np.nan).ffill().fillna(0)
    tdf["sign"] = sign
    tdf["mid_ret"] = tdf["mid"].pct_change()

    grp = tdf.groupby("bucket").agg(
        tick_count=("mid", "size"),
        sign_sum=("sign", "sum"),
        spr_mean=("spr", "mean"),
        mid_ret_std=("mid_ret", "std"),
    ).reset_index()
    grp["imbalance"] = grp["sign_sum"] / grp["tick_count"]
    bucket_records.append(grp)

fetch_seconds = time.time() - t0
if bucket_records:
    all_buckets = pd.concat(bucket_records, ignore_index=True)
    micro_df = df[["time", "close"]].rename(columns={"time": "bucket", "close": "gold_close"}).merge(
        all_buckets, on="bucket", how="inner")
    micro_df = micro_df.sort_values("bucket").reset_index(drop=True)
    mg_close = micro_df["gold_close"].to_numpy(float)
    mfwd = np.full(len(micro_df), np.nan)
    for i in range(len(micro_df) - FWD_N):
        mfwd[i] = (mg_close[i + FWD_N] - mg_close[i]) / POINT
    micro_df["fwd8_signed_ret_pts"] = mfwd

    imb = micro_df["imbalance"].to_numpy(float)
    valid_imb = ~np.isnan(imb) & ~np.isnan(mfwd)
    imb_q80 = np.nanpercentile(imb[valid_imb], 80) if valid_imb.sum() else None
    imb_q20 = np.nanpercentile(imb[valid_imb], 20) if valid_imb.sum() else None
    high_imb_mask = valid_imb & (imb >= imb_q80) if imb_q80 is not None else np.zeros(len(imb), bool)
    low_imb_mask = valid_imb & (imb <= imb_q20) if imb_q20 is not None else np.zeros(len(imb), bool)

    micro_results = {
        "pencere_gun": TICK_DAYS,
        "pencere_baslangic": str(day_list[-1].date()),
        "pencere_bitis": str(day_list[0].date()),
        "toplam_m15_bucket_n": int(len(micro_df)),
        "fetch_sure_sn": round(fetch_seconds, 1),
        "tick_count_medyan": float(micro_df["tick_count"].median()),
        "imbalance_medyan": float(np.nanmedian(imb)),
        "imbalance_p10_p90": [float(np.nanpercentile(imb, 10)), float(np.nanpercentile(imb, 90))],
        "yuksek_imbalance_fwd8_medyan_pts": float(np.nanmedian(mfwd[high_imb_mask])) if high_imb_mask.sum() else None,
        "yuksek_imbalance_n": int(high_imb_mask.sum()),
        "dusuk_imbalance_fwd8_medyan_pts": float(np.nanmedian(mfwd[low_imb_mask])) if low_imb_mask.sum() else None,
        "dusuk_imbalance_n": int(low_imb_mask.sum()),
        "mid_ret_std_medyan": float(micro_df["mid_ret_std"].median()),
        "spr_mean_medyan_pts": float(micro_df["spr_mean"].median()) ,
        "imbalance_vs_fwd8_korelasyon": float(np.corrcoef(imb[valid_imb], mfwd[valid_imb])[0, 1]) if valid_imb.sum() > 30 else None,
        "mid_ret_std_vs_fwd8_abs_korelasyon": None,
    }
    absfwd = np.abs(mfwd)
    v3 = ~np.isnan(micro_df["mid_ret_std"].to_numpy(float)) & ~np.isnan(absfwd)
    if v3.sum() > 30:
        micro_results["mid_ret_std_vs_fwd8_abs_korelasyon"] = float(
            np.corrcoef(micro_df["mid_ret_std"].to_numpy(float)[v3], absfwd[v3])[0, 1])
    results["mikro_yapi_tick_proxy"] = micro_results
else:
    results["mikro_yapi_tick_proxy"] = {"veri_erisimi": "yok/bos - tick cekimi basarisiz"}

print("MIKRO-YAPI tamam", flush=True)

# =====================================================================================
# Cikti
# =====================================================================================
with open("research_ml_gold_scalping_m15_v2_output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI")
print(json.dumps({k: (v if k != "meta" else v) for k, v in results.items()}, ensure_ascii=False, indent=2, default=str)[:3000])
