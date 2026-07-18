# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - ML/Feature-Tabanli Aile v2 (ML Tam Tur 2) - HIPOTEZ 3
OLCEKLENEBILIRLIK PILOTU (DUSUK ONCELIK) - Grup D (mikro-yapi/tick-proxy) feature'lari, SADECE
SON 90 ISLEM GUNU penceresinde, Hipotez 1'in feature seti (Grup 1-5 + Grup B) + EK Grup D ile.

Bu, ana Hipotez 1/2'nin 4,2 yillik egitim/test setinden TAMAMEN AYRI, kucuk-olcekli bir
alt-deneydir (Stratejist Karar 4). Sonucu ne olursa olsun (KABUL/RED) tam-tarihsel
olceklendirme sorusu (Grup D'nin 4,2 yillik veriye nasil tasinacagi) bu script/raporla
COZULMEZ - bu bir ilk/dar-kapsamli gozlemdir, TEK BASINA Tur 2'nin nihai karar dayanagi DEGILDIR.

Girdi: stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md (Karar 4, Hipotez 3)
Cerceve: justin_gecmis_calisma.md, justin_ml_anti_overfitting_protokolu.md (S2),
         justin_backtest_onkontrol_standardi.md (S1 + DST + SL/TP-ozel)
Yapi/kutuphane-kullanimi referansi: backtest_ml_v2_hipotez1.py (Justin'in KENDI onceki turu -
         izolasyon kurali MilaGold/Lisa/Signal GPT'ye ait dosyalar icin gecerlidir, bu KAPSAM DISI).

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Veri dogrudan MT5'ten (MetaTrader5 kutuphanesi), GOLD sembolu M15 OHLCV+tick_volume+spread + tick
(bid/ask) verisi (copy_ticks_range).
"""
import json
import time
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import MetaTrader5 as mt5
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import lightgbm as lgb
from sklearn.metrics import roc_auc_score

# =====================================================================
# SABITLER
# =====================================================================
SYMBOL = "GOLD"
N_BARS = 16                 # zaman-bariyeri, 4 saat (Hipotez1 ile BIREBIR AYNI - Stratejist SL/TP notu)
K_ATR = 1.5                 # barrier katsayisi (Hipotez1 ile BIREBIR AYNI)
ATR_PERIOD = 14
TRAIL_WINDOW = 100          # ATR/hacim rejim trailing-medyan penceresi (Hipotez1 ile AYNI)
RANDOM_SEED = 42
MIN_SAMPLE = 30
ROLL_SR_WINDOW = 20         # Grup B - 20 GUNLUK rolling high/low penceresi (Hipotez1 ile AYNI)
NEAR_ATR_MULT = 0.5         # Grup B yakinlik-bayragi esigi (Hipotez1 ile AYNI)

# --- PILOT PENCERE (Karar 4 / Hipotez 3'e OZEL - YENI) ---
N_BARS_FETCH_PILOT = 14000  # M15 bar cekme miktari (>=115 islem gunu icin bol marjli, asagida dogrulanir)
WINDOW_TRADING_DAYS = 90    # Stratejist araligi 60-90; UST SINIR secildi (daha genis orneklem, dusuk-guc
                            # riskini kismen azaltmak icin) - ampirik tick-cekme suresi (asagida olculdu,
                            # ~2-10 saniye) bu secimi PRATIK olarak destekliyor, ek maliyet onemsiz.
WARMUP_TRADING_DAYS = 25    # pencere BASLANGICINDAN ONCEKI, SADECE nedensel feature warmup icin (ROLL_SR_
                            # WINDOW=20 gun + 5 gun guvenlik payi) - bu gunler TRAIN/TEST/ORNEKLEM SAYISINA
                            # DAHIL DEGILDIR, sadece rolling hesaplarin ilk pencereyi doldurmasi icin kullanilir.
TEST_FRACTION = 0.20        # pencere icinde kronolojik son %20 -> TEST (TEK KEZ kullanim)
WF_SEGMENTS = 5             # TRAINVAL walk-forward icin esit-uzunluklu segment sayisi (4 fold uretir) -
                            # Hipotez1 ile AYNI SAYIDA segment (S2 protokolu ayni sekilde uygulanir); pencere
                            # kucuk oldugu icin fold-basi n dusecektir, bu asagida ACIKCA raporlanir.
EMBARGO_TRADING_DAYS_PILOT = 1  # Stratejist'in ONERISI: "N=16-bar + 1 gunluk embargo" (Hipotez1/2'nin
                            # tam-tarihsel 24-bar/6-saat sabit embargosu DEGIL - kucuk pencereye ORANTILI
                            # kucultulmus, gun-bazli bir embargo). Purge zaten idx+N_BARS<=sinir kurali ile
                            # AYRICA/EK olarak uygulanir (asagida) - embargo bunun USTUNE eklenir.

KASA_USD = 2000.0
RISK_PCT_CAP = 0.01
LOT_FIXED = 0.01
HEDEF_PF = 1.5
HEDEF_WR_RR11 = 0.60
HEDEF_DD = 0.20

MAX_TICK_MISMATCH_SEC = 60  # Justin ailesinde onaylanmis standart (H1/H2/H3/ML v1/v2)

THRESH_LONG_CANDIDATES = [0.60, 0.575, 0.55]
THRESH_SHORT_CANDIDATES = [0.40, 0.425, 0.45]

LGB_PARAMS = dict(
    objective="binary",
    num_leaves=31,
    max_depth=6,
    learning_rate=0.05,
    n_estimators=500,
    min_child_samples=50,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    random_state=RANDOM_SEED,
    verbosity=-1,
)

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_ml_v2_hipotez3_output.json"

results = {}
results["hipotez_cercevesi"] = {
    "oncelik": "3-Dusuk (Stratejist raporu) - bu sonuc Tur 2'nin nihai KABUL/RED kararinin TEK BASINA "
               "dayanagi OLAMAZ, Hipotez 1/2 birincil, bu hipotez tamamlayici/on-gozlem niteligindedir.",
    "cerceveleme_ZORUNLU": (
        "Kucuk orneklem (tahmini 3.780-5.670 M15-bucket, Stratejist onerisi) nedeniyle istatistiksel guc "
        "SINIRLIDIR. Sonuc 'KESIN RED/KABUL' olarak SUNULMAZ - 'bu olcekte ilk gozlem, tam-tarihsel "
        "olceklendirme HALA cozulmemis' seklinde cercevelenir (asagida SONUC bolumunde tekrarlanacaktir)."
    ),
    "olceklenebilirlik_durumu": "COZULMEDI - bu hipotez BASARILI cikSa bile Grup D'nin 4,2 yillik tam "
                                 "egitim setine nasil tasinacagi ayri bir tasarim/muhendislik sorusudur.",
}

# =====================================================================
# MT5 BAGLANTI + M15 VERI (pencere + warmup icin bol marjli tek seferlik cekim)
# =====================================================================
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size

rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, N_BARS_FETCH_PILOT)
assert rates is not None and len(rates) > 0, "M15 veri cekilemedi"
n = len(rates)
t = rates['time'].astype(np.int64)
o = rates['open'].astype(float)
h = rates['high'].astype(float)
l = rates['low'].astype(float)
c = rates['close'].astype(float)
vol = rates['tick_volume'].astype(float)
spread = rates['spread'].astype(float)

dt_utc = [datetime.fromtimestamp(int(x), tz=timezone.utc) for x in t]
hours = np.array([d.hour for d in dt_utc])
dows = np.array([d.weekday() for d in dt_utc])
dates_str = np.array([str(d.date()) for d in dt_utc])

results["meta"] = {
    "symbol": SYMBOL, "point": POINT, "digits": info.digits,
    "contract_size": CONTRACT_SIZE, "m15_n_toplam_cekilen": int(n),
    "m15_start_toplam": dates_str[0], "m15_end_toplam": dates_str[-1],
    "not": "Bu toplam cekim (warmup+pencere) - asagida SADECE son 90 islem gunu (PENCERE) egitim/test icin kullanilir.",
}
print("M15 toplam bar sayisi:", n, "araligi:", dates_str[0], "->", dates_str[-1])

# =====================================================================
# PILOT PENCERE TANIMI (Karar 4 - YENI, Hipotez1/2'nin 4,2 yillik setinden TAMAMEN AYRI)
# =====================================================================
uniq_dates_all, first_idx_all = np.unique(dates_str, return_index=True)
order_u = np.argsort(first_idx_all)
uniq_dates_all = uniq_dates_all[order_u]
toplam_islem_gunu = len(uniq_dates_all)
assert toplam_islem_gunu >= WINDOW_TRADING_DAYS + WARMUP_TRADING_DAYS + 5, (
    f"HATA: cekilen veri sadece {toplam_islem_gunu} islem gunu iceriyor - pencere({WINDOW_TRADING_DAYS})+"
    f"warmup({WARMUP_TRADING_DAYS})+guvenlik-payi(5) icin yetersiz, N_BARS_FETCH_PILOT artirilmali."
)

window_start_date = uniq_dates_all[-WINDOW_TRADING_DAYS]
window_end_date = uniq_dates_all[-1]
window_mask = dates_str >= window_start_date
window_indices = np.where(window_mask)[0]              # kronolojik, artan sirali
warmup_mask = ~window_mask                              # SADECE feature-warmup icin, ornekleme DAHIL DEGIL

results["pilot_pencere_tanimi"] = {
    "window_trading_days_hedef": WINDOW_TRADING_DAYS,
    "warmup_trading_days": WARMUP_TRADING_DAYS,
    "toplam_cekilen_islem_gunu": int(toplam_islem_gunu),
    "pencere_baslangic_tarihi": window_start_date,
    "pencere_bitis_tarihi": window_end_date,
    "pencere_bar_sayisi": int(len(window_indices)),
    "warmup_bar_sayisi": int(warmup_mask.sum()),
    "not": (
        "Warmup bolgesi (pencere ONCESI) SADECE nedensel rolling feature'larin (ROLL_SR_WINDOW=20 gun, "
        "TRAIL_WINDOW=100 bar, MTF SMA20) ilk degerlerini doldurmak icin kullanilir - bu barlar egitim/"
        "test/ornek SAYISINA KATILMAZ, ana Hipotez1/2'nin 4,2 yillik setiyle KARISTIRILMAZ."
    ),
}
print("Pilot pencere:", window_start_date, "->", window_end_date, "bar sayisi:", len(window_indices))

# =====================================================================
# DST / SAAT-ESLESME BAGIMSIZ DOGRULAMA (justin_backtest_onkontrol_standardi.md Madde 1) -
# onceki turden DEVRALINMAZ, bu turde de BAGIMSIZ calistirilir (Grup B gun/hafta-siniri + Grup D
# tick-bucket-siniri GMT+3/DST varsayimina dayandigi icin)
# =====================================================================
now_system = datetime.now(timezone.utc)
tick_now = mt5.symbol_info_tick(SYMBOL)
tick_epoch = datetime.fromtimestamp(int(tick_now.time), tz=timezone.utc)
fark_sn = (now_system - tick_epoch).total_seconds()

DST_TRANSITIONS = [
    "2022-10-30", "2023-03-26", "2023-10-29", "2024-03-31", "2024-10-27",
    "2025-03-30", "2025-10-26", "2026-03-29",
]
dst_scan = []
kayma_sayisi = 0
degerlendirilen_sayisi = 0
for tarih in DST_TRANSITIONS:
    tdate = datetime.strptime(tarih, "%Y-%m-%d").date()
    if str(tdate) < dates_str[0] or str(tdate) > dates_str[-1]:
        dst_scan.append({"gecis_tarihi": tarih, "durum": "veri_araliginda_yok"})
        continue
    sonraki_mask = (dates_str >= str(tdate)) & (dates_str <= str(tdate + timedelta(days=2)))
    onceki_tdate = tdate - timedelta(days=7)
    onceki_mask = (dates_str >= str(onceki_tdate)) & (dates_str <= str(onceki_tdate + timedelta(days=2)))
    idx_sonraki = np.where(sonraki_mask)[0]
    idx_onceki = np.where(onceki_mask)[0]
    if len(idx_sonraki) == 0 or len(idx_onceki) == 0:
        dst_scan.append({"gecis_tarihi": tarih, "durum": "veri_araliginda_yetersiz_hafta"})
        continue
    saat_onceki = int(hours[idx_onceki[0]])
    saat_sonraki = int(hours[idx_sonraki[0]])
    kaydi = (saat_onceki != saat_sonraki)
    degerlendirilen_sayisi += 1
    if kaydi:
        kayma_sayisi += 1
    dst_scan.append({
        "gecis_tarihi": tarih, "onceki_hafta_acilis_saati_utc": saat_onceki,
        "gecis_sonrasi_hafta_acilis_saati_utc": saat_sonraki, "1_saat_kayma_gozlendi_mi": bool(kaydi),
    })

results["dst_saat_eslesme_dogrulamasi"] = {
    "yontem": "BAGIMSIZ (bu Hipotez3/pilot calismasi icin YENIDEN calistirildi) - PILOT PENCEREYI de "
              "kapsayan toplam cekilen veri icinde bilinen DST gecisleri taranir.",
    "canli_capraz_kontrol": {
        "sistem_saati_utc": now_system.isoformat(), "son_tick_epoch_utc": tick_epoch.isoformat(),
        "fark_saniye": round(fark_sn, 2),
    },
    "dst_gecis_taramasi": dst_scan,
    "degerlendirilen_gecis_sayisi": degerlendirilen_sayisi,
    "1_saat_kayma_gozlenen_gecis_sayisi": kayma_sayisi,
    "SONUC": (
        f"{kayma_sayisi}/{degerlendirilen_sayisi} bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI "
        "- MT5 sunucusu DST'yi TAKIP EDIYOR (Hipotez1/2 ile AYNI sonuc, BAGIMSIZ tekrar-uretildi)."
        if kayma_sayisi == degerlendirilen_sayisi and degerlendirilen_sayisi > 0 else
        f"{kayma_sayisi}/{degerlendirilen_sayisi} gecis kaydi gosterdi - KARISIK/BELIRSIZ, DIKKAT."
    ),
}
print("DST/saat-eslesme dogrulamasi:", results["dst_saat_eslesme_dogrulamasi"]["SONUC"])

# =====================================================================
# YARDIMCI FONKSIYONLAR (Hipotez1/backtest_ml_v2_hipotez1.py ile AYNI - Justin'in KENDI onceki
# turu, izolasyon kapsami DISINDA - MilaGold/Lisa'ya ait degil)
# =====================================================================
def rolling_mean_causal(x, window):
    out = np.full(len(x), np.nan)
    csum = np.cumsum(np.insert(x, 0, 0.0))
    for i in range(window - 1, len(x)):
        out[i] = (csum[i + 1] - csum[i + 1 - window]) / window
    return out

def rolling_median_causal(x, window):
    nn = len(x)
    out = np.full(nn, np.nan)
    if nn < window:
        return out
    windows = sliding_window_view(x, window)
    out[window - 1:] = np.median(windows, axis=1)
    return out

def rolling_max_causal(x, window):
    nn = len(x)
    out = np.full(nn, np.nan)
    if nn < window:
        return out
    windows = sliding_window_view(x, window)
    out[window - 1:] = np.max(windows, axis=1)
    return out

def rolling_min_causal(x, window):
    nn = len(x)
    out = np.full(nn, np.nan)
    if nn < window:
        return out
    windows = sliding_window_view(x, window)
    out[window - 1:] = np.min(windows, axis=1)
    return out

def ema_causal(x, span):
    alpha = 2.0 / (span + 1)
    out = np.full(len(x), np.nan)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out

def compute_atr_points(hh, ll, cc, period, point):
    nn = len(cc)
    tr = np.empty(nn)
    tr[0] = hh[0] - ll[0]
    tr[1:] = np.maximum(np.maximum(hh[1:] - ll[1:], np.abs(hh[1:] - cc[:-1])), np.abs(ll[1:] - cc[:-1]))
    tr_pts = tr / point
    atr = rolling_mean_causal(tr_pts, period)
    return atr

def resample_ohlc(tt, oo, hh, ll, cc, vv, bucket_seconds):
    key = tt // bucket_seconds
    uniq_key, first_idx, counts = np.unique(key, return_index=True, return_counts=True)
    order = np.argsort(first_idx)
    uniq_key = uniq_key[order]; first_idx = first_idx[order]; counts = counts[order]
    nn = len(uniq_key)
    r_o = np.empty(nn); r_h = np.empty(nn); r_l = np.empty(nn); r_c = np.empty(nn); r_v = np.empty(nn)
    r_t = np.empty(nn, dtype=np.int64)
    pos = 0
    for i in range(nn):
        seg = slice(pos, pos + counts[i])
        r_o[i] = oo[seg][0]; r_h[i] = hh[seg].max(); r_l[i] = ll[seg].min()
        r_c[i] = cc[seg][-1]; r_v[i] = vv[seg].sum(); r_t[i] = uniq_key[i] * bucket_seconds
        pos += counts[i]
    return r_t, r_o, r_h, r_l, r_c, r_v

def aggregate_by_key(key_arr, hh, ll, cc):
    uniq_k, first_idx, counts = np.unique(key_arr, return_index=True, return_counts=True)
    order = np.argsort(first_idx)
    uniq_k = uniq_k[order]; first_idx = first_idx[order]; counts = counts[order]
    m = len(uniq_k)
    agg_high = np.empty(m); agg_low = np.empty(m); agg_close = np.empty(m)
    pos = 0
    for i in range(m):
        seg = slice(pos, pos + counts[i])
        agg_high[i] = hh[seg].max(); agg_low[i] = ll[seg].min(); agg_close[i] = cc[seg][-1]
        pos += counts[i]
    return uniq_k, agg_high, agg_low, agg_close, counts

def sma_trend(close_arr, window=20):
    sma = rolling_mean_causal(close_arr, window)
    trend = np.full(len(close_arr), np.nan)
    valid = ~np.isnan(sma)
    trend[valid] = np.sign(close_arr[valid] - sma[valid])
    return trend, valid

print("Yardimci fonksiyonlar hazir. Feature hesaplaniyor (Grup 1-5 + Grup B, TOPLAM cekilen veri "
      "uzerinde - nedensel, warmup DAHIL, pencere ile ornekleme asamasinda kisitlanacak)...")

# =====================================================================
# GRUP 1 - VOLATILITE (Hipotez1 ile AYNI)
# =====================================================================
atr14_m15 = compute_atr_points(h, l, c, ATR_PERIOD, POINT)
atr_trail_med = rolling_median_causal(np.nan_to_num(atr14_m15, nan=0.0), TRAIL_WINDOW)
atr_regime_ratio = np.full(n, np.nan)
valid_atr_regime = ~np.isnan(atr14_m15) & ~np.isnan(atr_trail_med) & (atr_trail_med > 0)
atr_regime_ratio[valid_atr_regime] = atr14_m15[valid_atr_regime] / atr_trail_med[valid_atr_regime]

h1_t, h1_o, h1_h, h1_l, h1_c, h1_v = resample_ohlc(t, o, h, l, c, vol, 3600)
h4_t, h4_o, h4_h, h4_l, h4_c, h4_v = resample_ohlc(t, o, h, l, c, vol, 14400)
atr14_h1 = compute_atr_points(h1_h, h1_l, h1_c, ATR_PERIOD, POINT)

h1_bucket_of_m15 = t // 3600
h1_key_to_idx = {int(k): i for i, k in enumerate(h1_t // 3600)}
atr14_h1_aligned = np.full(n, np.nan)
for i in range(n):
    hb = int(h1_bucket_of_m15[i])
    h1_idx = h1_key_to_idx.get(hb)
    if h1_idx is not None and h1_idx - 1 >= 0 and not np.isnan(atr14_h1[h1_idx - 1]):
        atr14_h1_aligned[i] = atr14_h1[h1_idx - 1]
print("Grup 1 (volatilite) hazir.")

# =====================================================================
# GRUP 2 - COKLU-TF TREND CONFLUENCE (Hipotez1 ile AYNI)
# =====================================================================
m15_trend, m15_trend_valid = sma_trend(c, 20)
h1_trend, h1_trend_valid = sma_trend(h1_c, 20)
h4_trend, h4_trend_valid = sma_trend(h4_c, 20)

h4_bucket_of_m15 = t // 14400
h4_key_to_idx = {int(k): i for i, k in enumerate(h4_t // 14400)}
m15_h1_trend_aligned = np.full(n, np.nan)
m15_h4_trend_aligned = np.full(n, np.nan)
for i in range(n):
    hb = int(h1_bucket_of_m15[i])
    h1_idx = h1_key_to_idx.get(hb)
    if h1_idx is not None and h1_idx - 1 >= 0 and h1_trend_valid[h1_idx - 1]:
        m15_h1_trend_aligned[i] = h1_trend[h1_idx - 1]
    hb4 = int(h4_bucket_of_m15[i])
    h4_idx = h4_key_to_idx.get(hb4)
    if h4_idx is not None and h4_idx - 1 >= 0 and h4_trend_valid[h4_idx - 1]:
        m15_h4_trend_aligned[i] = h4_trend[h4_idx - 1]

conf_valid = m15_trend_valid & ~np.isnan(m15_h1_trend_aligned) & ~np.isnan(m15_h4_trend_aligned)
confluence_flag = np.zeros(n)
confluence_flag[conf_valid] = (
    (m15_trend[conf_valid] == m15_h1_trend_aligned[conf_valid]) &
    (m15_trend[conf_valid] == m15_h4_trend_aligned[conf_valid])
).astype(float)
print("Grup 2 (MTF confluence) hazir.")

# =====================================================================
# GRUP 3 - HACIM/TICK-YOGUNLUGU (BAR-seviyesi, Hipotez1 ile AYNI)
# =====================================================================
vol_trail_med = rolling_median_causal(vol, TRAIL_WINDOW)
vol_ratio = np.full(n, np.nan)
valid_vol_ratio = ~np.isnan(vol_trail_med) & (vol_trail_med > 0)
vol_ratio[valid_vol_ratio] = vol[valid_vol_ratio] / vol_trail_med[valid_vol_ratio]

VOL_SLOPE_W = 8
vol_slope = np.full(n, np.nan)
denom = np.where(vol[:-VOL_SLOPE_W] > 0, vol[:-VOL_SLOPE_W], np.nan)
vol_slope[VOL_SLOPE_W:] = (vol[VOL_SLOPE_W:] - vol[:-VOL_SLOPE_W]) / denom
print("Grup 3 (hacim) hazir.")

# =====================================================================
# GRUP 4 - OTURUM/GUN-ICI KONUM (Hipotez1 ile AYNI)
# =====================================================================
hour_sin = np.sin(2 * np.pi * hours / 24.0)
hour_cos = np.cos(2 * np.pi * hours / 24.0)
SESSION_ASIA = set(range(1, 9)); SESSION_LONDON = set(range(9, 17)); SESSION_NY = set(range(15, 24))
session_asia = np.isin(hours, list(SESSION_ASIA)).astype(float)
session_london = np.isin(hours, list(SESSION_LONDON)).astype(float)
session_ny = np.isin(hours, list(SESSION_NY)).astype(float)
dow_feature = dows.astype(float)
print("Grup 4 (oturum/gun-ici) hazir.")

# =====================================================================
# GRUP 5 - FIYAT YAPISI/MOMENTUM (Hipotez1 ile AYNI)
# =====================================================================
def lag_return(cc, lag, point):
    out = np.full(len(cc), np.nan)
    out[lag:] = (cc[lag:] - cc[:-lag]) / point
    return out

lag_ret_1 = lag_return(c, 1, POINT)
lag_ret_4 = lag_return(c, 4, POINT)
lag_ret_8 = lag_return(c, 8, POINT)

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

rsi14 = rsi(c, 14)
ema12 = ema_causal(c, 12); ema26 = ema_causal(c, 26)
macd_line = ema12 - ema26
macd_signal = ema_causal(macd_line, 9)
macd_hist = macd_line - macd_signal

hh_bool = np.zeros(n, dtype=bool); ll_bool = np.zeros(n, dtype=bool)
hh_bool[1:] = h[1:] > h[:-1]
ll_bool[1:] = l[1:] < l[:-1]
directional_streak = np.zeros(n)
_cur = 0
for i in range(1, n):
    if hh_bool[i] and not ll_bool[i]:
        _cur = _cur + 1 if _cur >= 0 else 1
    elif ll_bool[i] and not hh_bool[i]:
        _cur = _cur - 1 if _cur <= 0 else -1
    else:
        _cur = 0
    directional_streak[i] = _cur
print("Grup 5 (fiyat yapisi/momentum) hazir.")

# =====================================================================
# GRUP B - GORECE FIYAT YAPISI (Hipotez1 ile AYNI - gunluk/haftalik pivot + 20-gunluk rolling S/R)
# =====================================================================
daily_keys, d_high, d_low, d_close, daily_counts = aggregate_by_key(dates_str, h, l, c)
daily_pivot = (d_high + d_low + d_close) / 3.0
daily_pivot_prev = np.concatenate(([np.nan], daily_pivot[:-1]))
roll20_high_incl = rolling_max_causal(d_high, ROLL_SR_WINDOW)
roll20_low_incl = rolling_min_causal(d_low, ROLL_SR_WINDOW)
roll20_high_prev = np.concatenate(([np.nan], roll20_high_incl[:-1]))
roll20_low_prev = np.concatenate(([np.nan], roll20_low_incl[:-1]))

date_to_daily_idx = {k: i for i, k in enumerate(daily_keys)}
dist_daily_pivot_pts = np.full(n, np.nan)
dist_roll20_high_pts = np.full(n, np.nan)
dist_roll20_low_pts = np.full(n, np.nan)
for i in range(n):
    di = date_to_daily_idx[dates_str[i]]
    if not np.isnan(daily_pivot_prev[di]):
        dist_daily_pivot_pts[i] = (c[i] - daily_pivot_prev[di]) / POINT
    if not np.isnan(roll20_high_prev[di]):
        dist_roll20_high_pts[i] = (roll20_high_prev[di] - c[i]) / POINT
    if not np.isnan(roll20_low_prev[di]):
        dist_roll20_low_pts[i] = (c[i] - roll20_low_prev[di]) / POINT

iso_year = np.array([d.isocalendar()[0] for d in dt_utc])
iso_week = np.array([d.isocalendar()[1] for d in dt_utc])
week_key = np.array([f"{y}-W{w:02d}" for y, w in zip(iso_year, iso_week)])
weekly_keys, w_high, w_low, w_close, weekly_counts = aggregate_by_key(week_key, h, l, c)
weekly_pivot = (w_high + w_low + w_close) / 3.0
weekly_pivot_prev = np.concatenate(([np.nan], weekly_pivot[:-1]))

week_to_idx = {k: i for i, k in enumerate(weekly_keys)}
dist_weekly_pivot_pts = np.full(n, np.nan)
for i in range(n):
    wi = week_to_idx[week_key[i]]
    if not np.isnan(weekly_pivot_prev[wi]):
        dist_weekly_pivot_pts[i] = (c[i] - weekly_pivot_prev[wi]) / POINT

near_roll20_high_flag = np.zeros(n)
near_roll20_low_flag = np.zeros(n)
valid_near_high = ~np.isnan(dist_roll20_high_pts) & ~np.isnan(atr14_m15)
near_roll20_high_flag[valid_near_high] = (
    dist_roll20_high_pts[valid_near_high] <= NEAR_ATR_MULT * atr14_m15[valid_near_high]
).astype(float)
valid_near_low = ~np.isnan(dist_roll20_low_pts) & ~np.isnan(atr14_m15)
near_roll20_low_flag[valid_near_low] = (
    dist_roll20_low_pts[valid_near_low] <= NEAR_ATR_MULT * atr14_m15[valid_near_low]
).astype(float)
print("Grup B (pivot/rolling S-R) hazir.")

# =====================================================================
# GRUP D (YENI - Hipotez3'e OZEL) - TICK-KURAL-TABANLI MIKRO-YAPI, SADECE PILOT PENCERE
# (imbalance orani, tick-sayisi, tick-ici mikro-volatilite/mid_ret_std, tick-seviyesi ortalama
# spread - Arastirmaci BULGU 7-9 yontemi, BAGIMSIZ olarak buradan yeniden uygulanmistir)
# =====================================================================
window_start_bar_idx = window_indices[0]
tick_fetch_start = datetime.fromtimestamp(int(t[window_start_bar_idx]), tz=timezone.utc)
tick_fetch_end = datetime.fromtimestamp(int(t[-1]) + 900, tz=timezone.utc)

print(f"Grup D icin tick verisi cekiliyor: {tick_fetch_start} -> {tick_fetch_end} (SADECE pilot pencere)...")
_t0 = time.time()
ticks = mt5.copy_ticks_range(SYMBOL, tick_fetch_start, tick_fetch_end, mt5.COPY_TICKS_ALL)
_t1 = time.time()
assert ticks is not None and len(ticks) > 0, "Grup D icin tick verisi cekilemedi"
tick_fetch_seconds = round(_t1 - _t0, 3)
print(f"Tick cekme suresi: {tick_fetch_seconds} sn, tick sayisi: {len(ticks)}")

tk_time = ticks['time'].astype(np.int64)
tk_bid = ticks['bid'].astype(float)
tk_ask = ticks['ask'].astype(float)
del ticks  # bellek - digger alanlara (last, volume, flags) ihtiyac yok

# Gecerli kotasyon filtresi (ask>=bid>0) - Justin ailesi standardi (Hipotez1/2 simulate_trade ile AYNI ilke)
valid_q = (tk_bid > 0) & (tk_ask > 0) & (tk_ask >= tk_bid)
tk_time = tk_time[valid_q]; tk_bid = tk_bid[valid_q]; tk_ask = tk_ask[valid_q]
# Kronolojik siralama garantisi (MT5 ticks zaten sirali doner, yine de BAGIMSIZ dogrulaniyor)
assert np.all(np.diff(tk_time) >= 0), "HATA: tick verisi kronolojik sirali degil!"

tk_mid = (tk_bid + tk_ask) / 2.0
tk_key = tk_time // 900  # M15-bucket anahtari (bar epoch/900 ile AYNI birim - hizalama dogrulanacak)

# --- Tick-kural (tick-rule) isaret: yukari=+1, asagi=-1, degisim-yoksa ONCEKI ISARETI TASI ---
diff_mid = np.diff(tk_mid, prepend=tk_mid[0])
raw_sign = np.sign(diff_mid)
nz_mask = raw_sign != 0
carry_idx = np.where(nz_mask, np.arange(len(raw_sign)), 0)
carry_idx = np.maximum.accumulate(carry_idx)
tick_direction = np.where(nz_mask, raw_sign, raw_sign[carry_idx])  # ilk tick icin nz yoksa 0 kalir

# --- Tick-ici getiri (mid pct_change, GLOBAL/surekli - bucket siniri ihmal edilebilir, ilk eleman haric) ---
mid_ret = np.diff(tk_mid, prepend=tk_mid[0]) / np.concatenate(([tk_mid[0]], tk_mid[:-1]))
mid_ret[0] = 0.0  # ilk tick icin onceki yok, ihmal edilebilir tek-nokta etkisi (sadece ilk bucket'i etkiler)

tk_spread_pts = (tk_ask - tk_bid) / POINT

# --- Bucket sinirlari: veri KRONOLOJIK ve tk_key AZALMAYAN oldugu icin diff-tabanli sinir tespiti
#     (np.unique'in tam siralamasindan DAHA HIZLI, 30+ milyon tick icin onemli) ---
change_points = np.nonzero(np.diff(tk_key))[0] + 1
bucket_starts = np.concatenate(([0], change_points))
bucket_ends = np.concatenate((change_points, [len(tk_key)]))
bucket_keys_uniq = tk_key[bucket_starts]
bucket_counts = bucket_ends - bucket_starts

sum_dir = np.add.reduceat(tick_direction, bucket_starts)
mean_dir = sum_dir / bucket_counts
sum_spread = np.add.reduceat(tk_spread_pts, bucket_starts)
mean_spread = sum_spread / bucket_counts
sum_r = np.add.reduceat(mid_ret, bucket_starts)
sumsq_r = np.add.reduceat(mid_ret ** 2, bucket_starts)
mean_r = sum_r / bucket_counts
var_r = np.maximum(sumsq_r / bucket_counts - mean_r ** 2, 0.0)
std_r = np.sqrt(var_r)
std_r[bucket_counts < 2] = np.nan  # tek-tick bucket'ta std tanimsiz

bucket_key_to_pos = {int(k): i for i, k in enumerate(bucket_keys_uniq)}

# =====================================================================
# GRUP D - BAGIMSIZ NEDENSELLIK/ILERI-BAKIS KONTROLU (Stratejist'in ozel talebi: Arastirmaci'nin
# kendi iddiasi YETERLI SAYILMAZ, BAGIMSIZ tekrar kontrol edilmeli)
# =====================================================================
grup_d_dogrulama = {}

# (1) Her bucket'taki TUM ticklerin epoch'u [bucket_key*900, bucket_key*900+900) araliginda mi -
#     yani bucket'a "ait" ticklerin GERCEKTEN o M15 barinin KENDI zaman araligindan geldigi, ILERI
#     bir bardan SIZMADIGI (rastgele 200 bucket spot-check + tam taramada sinir-disi sayaci)
rng_check_positions = np.linspace(0, len(bucket_keys_uniq) - 1, min(200, len(bucket_keys_uniq))).astype(int)
sinir_disi_sayisi = 0
ornek_sinir_kontrolu = []
for pos_ in rng_check_positions:
    s, e = bucket_starts[pos_], bucket_ends[pos_]
    k_ = bucket_keys_uniq[pos_]
    seg_times = tk_time[s:e]
    alt = k_ * 900
    ust = alt + 900
    disinda = int(np.sum((seg_times < alt) | (seg_times >= ust)))
    sinir_disi_sayisi += disinda
    if len(ornek_sinir_kontrolu) < 5:
        ornek_sinir_kontrolu.append({
            "bucket_key": int(k_), "bucket_epoch_baslangic": int(alt), "bucket_epoch_bitis": int(ust),
            "tick_sayisi": int(e - s), "ilk_tick_epoch": int(seg_times[0]), "son_tick_epoch": int(seg_times[-1]),
            "tum_ticklerin_araliginda_mi": disinda == 0,
        })
grup_d_dogrulama["bucket_siniri_spot_check_200_bucket"] = {
    "kontrol_edilen_bucket_sayisi": int(len(rng_check_positions)),
    "sinir_disi_tick_sayisi": int(sinir_disi_sayisi),
    "ornekler": ornek_sinir_kontrolu,
    "SONUC": "GECTI - hicbir bucket'ta sinir-disi tick YOK (ileri-bakis/karisma yok)" if sinir_disi_sayisi == 0
             else f"DIKKAT - {sinir_disi_sayisi} tick yanlis bucket'a atanmis olabilir",
}
assert sinir_disi_sayisi == 0, "HATA: Grup D bucket sinirlari ihlal edildi - ileri-bakis riski!"

# (2) Bar-epoch ile tick-bucket-epoch birimi AYNI mi - 3 ornek barda elle karsilastirma
ornek_bar_pos = [window_indices[len(window_indices) // 4], window_indices[len(window_indices) // 2],
                  window_indices[(3 * len(window_indices)) // 4]]
spot_check_bar_bucket = []
for bp in ornek_bar_pos:
    bar_key = int(t[bp] // 900)
    beklenen_baslangic = bar_key * 900
    eslesme = int(t[bp]) == beklenen_baslangic
    spot_check_bar_bucket.append({
        "bar_idx": int(bp), "bar_epoch": int(t[bp]), "bar_key_x900": int(beklenen_baslangic),
        "bar_epoch_multiple_of_900_mu": eslesme,
    })
grup_d_dogrulama["bar_tick_bucket_birim_uyumu"] = spot_check_bar_bucket
assert all(row["bar_epoch_multiple_of_900_mu"] for row in spot_check_bar_bucket), (
    "HATA: bar epoch'u 900 saniyenin kati degil - tick-bucket eslemesi guvenilmez!"
)

# (3) Ileri-bakis ozel kontrolu: bir bar'in Grup D degeri, SADECE o barin KENDI [t_i, t_i+900)
#     araliginin ticklerinden mi geliyor (bir SONRAKI barin ticklerinden DEGIL) - bucket_key
#     eslemesi zaten (1)'de dogrulandi; burada AYRICA "bar i icin kullanilan deger, bar i+1'in
#     ilk tick'ini ICERMIYOR" seklinde 3 ornekte elle teyit edilir.
ileri_bakis_ek_kontrol = []
for bp in ornek_bar_pos:
    bar_key = int(t[bp] // 900)
    pos_in_bucket = bucket_key_to_pos.get(bar_key)
    if pos_in_bucket is None:
        continue
    s, e = bucket_starts[pos_in_bucket], bucket_ends[pos_in_bucket]
    son_tick_epoch = int(tk_time[e - 1])
    bar_bitis_epoch = bar_key * 900 + 900
    ileri_bakis_ek_kontrol.append({
        "bar_idx": int(bp), "bucket_son_tick_epoch": son_tick_epoch, "bar_bitis_epoch": bar_bitis_epoch,
        "son_tick_bar_bitisinden_ONCE_mi": son_tick_epoch < bar_bitis_epoch,
    })
grup_d_dogrulama["ileri_bakis_ek_spot_check"] = ileri_bakis_ek_kontrol
assert all(row["son_tick_bar_bitisinden_ONCE_mi"] for row in ileri_bakis_ek_kontrol), (
    "HATA: bucket icinde bir SONRAKI barin tick'i bulunmus - ileri-bakis riski!"
)

grup_d_dogrulama["yontem_notu"] = (
    "Imbalance = tick-kural (tick-rule) isaretinin (yukari=+1/asagi=-1/degisim-yoksa-onceki-isaret) "
    "bucket-ici ORTALAMASI. mid_ret_std = tick-bazli mid-fiyat getirisinin (GLOBAL/surekli hesaplanip "
    "bucket'a gore gruplanmis) bucket-ici standart sapmasi - bucket sinirini gecen TEK bir getiri "
    "noktasi (onceki bucket'in son tick'inden bu bucket'in ilk tick'ine) metodolojik bir YAKLASIKLIK "
    "olarak kabul edilmistir (Arastirmaci'nin BULGU 8 tanimiyla AYNI ruhta, birebir ayni kod DEGIL - "
    "bu SINIR acikca belirtilir). avg_spread_tick_pts = bucket icindeki TUM tick'lerin (ask-bid)/POINT "
    "ortalamasi (Arastirmaci BULGU 9 ile AYNI tanim)."
)
grup_d_dogrulama["SONUC"] = (
    "GECTI - Grup D'nin tick-agregasyonlarinin M15-bucket icinde NEDENSEL/ileri-bakissiz oldugu "
    "BAGIMSIZ olarak (Arastirmaci'nin kendi ic-mantik iddiasina DAYANILMADAN) 3 ayri kontrolle "
    "(bucket-sinir spot-check 200 ornek, bar-bucket birim uyumu, bucket-son-tick<bar-bitis kontrolu) "
    "dogrulandi - hicbir ihlal bulunmadi."
)
results["grup_d_nedensellik_dogrulamasi_BAGIMSIZ"] = grup_d_dogrulama
print("Grup D nedensellik dogrulamasi:", grup_d_dogrulama["SONUC"])

# --- Bar-seviyesine esleme (bar i -> Grup D degerleri, key=t[i]//900) ---
tick_imbalance_ratio = np.full(n, np.nan)
tick_count_bucket = np.full(n, np.nan)
tick_mid_ret_std = np.full(n, np.nan)
tick_avg_spread_pts = np.full(n, np.nan)
for i in window_indices:  # SADECE pilot pencere barlari icin (Grup D tick verisi zaten sadece bu araligi kapsiyor)
    key_ = int(t[i] // 900)
    pos_ = bucket_key_to_pos.get(key_)
    if pos_ is None:
        continue
    tick_imbalance_ratio[i] = mean_dir[pos_]
    tick_count_bucket[i] = bucket_counts[pos_]
    tick_mid_ret_std[i] = std_r[pos_]
    tick_avg_spread_pts[i] = mean_spread[pos_]

eslesen_bar_sayisi = int(np.sum(~np.isnan(tick_imbalance_ratio[window_indices])))
results["grup_d_ozet_istatistikler"] = {
    "tick_cekme_suresi_sn": tick_fetch_seconds,
    "tick_toplam_sayisi_gecerli_kotasyon": int(len(tk_time)),
    "toplam_bucket_sayisi": int(len(bucket_keys_uniq)),
    "pencere_bar_sayisi": int(len(window_indices)),
    "grup_d_ile_eslesen_bar_sayisi": eslesen_bar_sayisi,
    "eslesme_orani": round(eslesen_bar_sayisi / len(window_indices), 4) if len(window_indices) else None,
    "bucket_basi_medyan_tick_sayisi": round(float(np.median(bucket_counts)), 1),
    "imbalance_medyan": round(float(np.nanmedian(tick_imbalance_ratio[window_indices])), 4),
    "imbalance_p10_p90": [
        round(float(np.nanpercentile(tick_imbalance_ratio[window_indices], 10)), 4),
        round(float(np.nanpercentile(tick_imbalance_ratio[window_indices], 90)), 4),
    ],
    "avg_spread_tick_medyan_pts": round(float(np.nanmedian(tick_avg_spread_pts[window_indices])), 2),
    "mid_ret_std_medyan": float(np.nanmedian(tick_mid_ret_std[window_indices])),
    "not": "BULGU 7-9 ile KARSILASTIRMA AMACLI BENZER olcumler - farkli pencere/uzunluk (90 gun vs 20 "
           "gun) nedeniyle sayilar DOGRUDAN eslesmeyebilir, bu BEKLENEN bir farktir (CLAUDE.md sayisal-"
           "tutarlilik ilkesi geregi burada ACIKCA belirtilir).",
}
print("Grup D ozet:", results["grup_d_ozet_istatistikler"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (Grup D + on-kontroller) tamamlandi ->", OUT_PATH)

# =====================================================================
# FEATURE MATRISI (Hipotez1'in 29 sutunu + Grup D'nin 4 YENI sutunu = 33 sutun toplam)
# =====================================================================
feature_names = [
    "atr14_m15", "atr_regime_ratio", "atr14_h1_aligned",
    "m15_trend", "h1_trend_aligned", "h4_trend_aligned", "confluence_flag",
    "tick_volume", "vol_ratio_trail100", "vol_slope_8bar",
    "hour_sin", "hour_cos", "dow", "session_asia", "session_london", "session_ny",
    "lag_ret_1", "lag_ret_4", "lag_ret_8", "rsi14", "macd_line", "macd_hist", "directional_streak",
    "dist_daily_pivot_pts", "dist_weekly_pivot_pts",
    "dist_roll20_high_pts", "dist_roll20_low_pts",
    "near_roll20_high_flag", "near_roll20_low_flag",
    "tick_imbalance_ratio", "tick_count_bucket", "tick_mid_ret_std", "tick_avg_spread_pts",  # Grup D - YENI
]
X_full = np.column_stack([
    atr14_m15, atr_regime_ratio, atr14_h1_aligned,
    m15_trend, m15_h1_trend_aligned, m15_h4_trend_aligned, confluence_flag,
    vol, vol_ratio, vol_slope,
    hour_sin, hour_cos, dow_feature, session_asia, session_london, session_ny,
    lag_ret_1, lag_ret_4, lag_ret_8, rsi14, macd_line, macd_hist, directional_streak,
    dist_daily_pivot_pts, dist_weekly_pivot_pts,
    dist_roll20_high_pts, dist_roll20_low_pts,
    near_roll20_high_flag, near_roll20_low_flag,
    tick_imbalance_ratio, tick_count_bucket, tick_mid_ret_std, tick_avg_spread_pts,
])
assert X_full.shape[1] == len(feature_names)
results["feature_seti"] = {
    "sutun_sayisi": len(feature_names), "sutunlar": feature_names,
    "hipotez1_sutun_sayisi": 29, "grup_d_yeni_sutun_sayisi": 4,
    "not": "Hipotez1 ile BIREBIR AYNI Grup 1-5 + Grup B (29 sutun) + Grup D (4 sutun: tick_imbalance_"
           "ratio, tick_count_bucket, tick_mid_ret_std, tick_avg_spread_pts) = 33 sutun toplam.",
}
print("Feature matrisi hazir. Sutun sayisi:", len(feature_names))

# Ornekleme SADECE pilot pencere barlariyla SINIRLANDIRILIR (Grup D disinda NaN olan warmup barlari
# feature_valid ile zaten otomatik elenir, ama ACIKCA window_mask ile de kisitliyoruz - cift-guvence)
feature_valid = ~np.isnan(X_full).any(axis=1)
feature_valid_in_window = feature_valid & window_mask
print("Feature-gecerli bar sayisi (pencere icinde):", int(feature_valid_in_window.sum()), "/", len(window_indices))

# =====================================================================
# FEATURE-SIZINTI KONTROL LISTESI (S2 Madde 3)
# =====================================================================
results["feature_sizinti_kontrol_listesi"] = {
    "1_ileri_bakan_bilgi_var_mi": (
        "HAYIR - Grup 1-5/B Hipotez1 ile AYNI (rolling_*_causal, H1/H4 ONCEKI-kapanan-bar hizalamasi). "
        "Grup D icin AYRICA yukarida grup_d_nedensellik_dogrulamasi_BAGIMSIZ bolumunde 3 bagimsiz "
        "kontrolle (bucket-sinir, bar-bucket-birim, son-tick<bar-bitis) dogrulandi."
    ),
    "2_label_hesaplamasinda_kullanilan_veriyi_dolayli_iceriyor_mu": (
        "HAYIR - etiket (triple-barrier) SADECE bar i'nin ATR14'unu ve i+1..i+16 YOL'unu kullanir; "
        "Grup D feature'lari SADECE bar i'nin KENDI [t_i, t_i+900) araligindaki tick'lerden turetilir, "
        "bu bar i+1 ve sonrasindaki fiyat yoluyla (etiketin kendisiyle) CAKISMAZ."
    ),
    "3_normalizasyon_sadece_egitim_setinden_mi": (
        "EVET - asagida final_train_idx/fold train kesitlerinden hesaplanan mu/sd, TEST/val'e uygulanir. "
        "Grup D feature'lari da HICBIR global/test-icerikli istatistikle olceklendirilmedi (ham puan/oran "
        "degerleri, normalizasyon egitim-setinden)."
    ),
    "4_zaman_bazli_feature_dst_dogrulamasindan_gecti_mi": (
        "EVET - dst_saat_eslesme_dogrulamasi bu turde BAGIMSIZ tekrar calistirildi (yukarida)."
    ),
    "5_macd_ham_deger_mi_isaret_mi": "HAM DEGER (Hipotez1 ile AYNI, degismedi).",
    "6_grup_d_nedensellik_bagimsiz_kontrol": (
        "EVET - grup_d_nedensellik_dogrulamasi_BAGIMSIZ bolumunde detaylandirildi; Arastirmaci'nin "
        "kendi ic-mantik iddiasina (BULGU 7-9) DAYANILMADAN sifirdan/bagimsiz kod-incelemesi+assert+"
        "spot-check yapildi (Stratejist'in ozel talebi geregi, Grup B'nin Hipotez1'deki dogrulama "
        "yontemiyle AYNI TITIZLIKTE)."
    ),
    "7_pilot_pencere_warmup_sizintisi_var_mi": (
        "HAYIR - warmup bolgesi (pencere ONCESI) sadece rolling feature'larin ilk degerlerini "
        "doldurmak icin kullanilir, TRAIN/TEST/WF orneklerine (idx_pool) hicbir warmup bari DAHIL "
        "EDILMEZ (feature_valid_in_window = feature_valid & window_mask ile CIFT-GUVENCELI kisitlama)."
    ),
}

# =====================================================================
# TRIPLE-BARRIER ETIKET (N=16, k=1,5xATR14(M15) PUAN) - Hipotez1 ile BIREBIR AYNI yontem
# =====================================================================
label = np.full(n, np.nan)
label_neither = np.zeros(n, dtype=bool)
label_valid = np.zeros(n, dtype=bool)
tp_price_arr = np.full(n, np.nan)
sl_price_arr = np.full(n, np.nan)
time_exit_price_arr = np.full(n, np.nan)
exit_idx_arr = np.full(n, -1, dtype=int)
exit_reason_arr = np.full(n, "", dtype=object)

idx_pool = np.where(feature_valid_in_window)[0]
idx_pool = idx_pool[idx_pool + N_BARS < n]
for i in idx_pool:
    atr_i = atr14_m15[i]
    if np.isnan(atr_i) or atr_i <= 0:
        continue
    entry = c[i]
    tp_up = entry + K_ATR * atr_i * POINT
    sl_down = entry - K_ATR * atr_i * POINT
    path_h = h[i + 1:i + 1 + N_BARS]
    path_l = l[i + 1:i + 1 + N_BARS]
    hit_tp_idx = np.argmax(path_h >= tp_up) if np.any(path_h >= tp_up) else None
    hit_sl_idx = np.argmax(path_l <= sl_down) if np.any(path_l <= sl_down) else None
    tp_price_arr[i] = tp_up; sl_price_arr[i] = sl_down
    time_exit_price_arr[i] = c[i + N_BARS]
    label_valid[i] = True
    if hit_tp_idx is None and hit_sl_idx is None:
        label_neither[i] = True
        exit_idx_arr[i] = i + N_BARS
        exit_reason_arr[i] = "zaman_asimi"
    elif hit_tp_idx is None:
        label[i] = 0.0
        exit_idx_arr[i] = i + 1 + hit_sl_idx
        exit_reason_arr[i] = "SL"
    elif hit_sl_idx is None:
        label[i] = 1.0
        exit_idx_arr[i] = i + 1 + hit_tp_idx
        exit_reason_arr[i] = "TP"
    else:
        if hit_tp_idx <= hit_sl_idx:
            label[i] = 1.0
            exit_idx_arr[i] = i + 1 + hit_tp_idx if hit_tp_idx < hit_sl_idx else i + 1 + hit_sl_idx
            exit_reason_arr[i] = "TP" if hit_tp_idx < hit_sl_idx else "SL(ayni-bar-oncelik)"
        else:
            label[i] = 0.0
            exit_idx_arr[i] = i + 1 + hit_sl_idx
            exit_reason_arr[i] = "SL"

print("Triple-barrier etiket hesaplandi. Gecerli:", int(label_valid.sum()),
      "hicbiri:", int(label_neither.sum()), "ikili-etiketli:", int((~np.isnan(label)).sum()))

results["etiket_dagilimi"] = {
    "gecerli_bar": int(label_valid.sum()),
    "yukari_bariyer_once": int(np.nansum(label == 1.0)),
    "asagi_bariyer_once": int(np.nansum(label == 0.0)),
    "hicbiri": int(label_neither.sum()),
    "hicbiri_orani": round(float(label_neither.sum() / label_valid.sum()), 4) if label_valid.sum() else None,
}

# =====================================================================
# S1 - MALIYET-ORANI STRES TESTI (justin_backtest_onkontrol_standardi.md Madde 2) - k_risk=1,5xATR14
# ZORUNLU DEGIL (Stratejist Notu Madde1 - Hipotez1'den DEVIR MUMKUN) ama PENCEREYE OZEL OPSIYONEL
# TEYIT olarak burada AYRICA hesaplanmistir (Stratejist'in acikca izin verdigi ek saglamlik kontrolu)
# =====================================================================
spread_window = spread[window_indices]
atr_window = atr14_m15[window_indices]
valid_atr_window = ~np.isnan(atr_window)
atr_median_w = float(np.nanmedian(atr_window))
atr_p90_w = float(np.nanpercentile(atr_window[valid_atr_window], 90))
spread_median_w = float(np.median(spread_window))
spread_p90_w = float(np.percentile(spread_window, 90))
spread_max_w = float(np.max(spread_window))
tick_spread_median_w = float(np.nanmedian(tick_avg_spread_pts[window_indices]))

hedef_pts_k15_w = K_ATR * atr_median_w
oran_medyan_spread_w = hedef_pts_k15_w / spread_median_w
oran_p90_spread_w = hedef_pts_k15_w / spread_p90_w
oran_max_spread_w = hedef_pts_k15_w / spread_max_w
oran_medyan_tickspread_w = hedef_pts_k15_w / tick_spread_median_w

ESIK_ALT = 15.0
s1_gecti_medyan_w = oran_medyan_spread_w >= ESIK_ALT
s1_gecti_p90_w = oran_p90_spread_w >= ESIK_ALT

results["s1_maliyet_orani_stres_testi_PENCEREYE_OZEL"] = {
    "yontem_notu": (
        "ZORUNLU DEGIL (Stratejist Notu Madde1, k_risk=1,5 Hipotez1'den DEVIR yeterliydi) - Stratejist'in "
        "acikca izin verdigi OPSIYONEL ek saglamlik kontrolu olarak, bu 90-gunluk kisitli PENCERENIN "
        "KENDI spread/ATR degerleriyle AYRICA hesaplandi (Hipotez1'in tam-tarihsel degerleriyle "
        "KARISTIRILMAMALIDIR - farkli veri araligi, CLAUDE.md sayisal-tutarlilik ilkesi)."
    ),
    "k_atr": K_ATR, "pencere_bar_sayisi": int(len(window_indices)),
    "atr14_m15_medyan_pts": round(atr_median_w, 2), "atr14_m15_p90_pts": round(atr_p90_w, 2),
    "bar_kapanis_spread_medyan_pts": round(spread_median_w, 2),
    "bar_kapanis_spread_p90_pts": round(spread_p90_w, 2),
    "bar_kapanis_spread_max_pts": round(spread_max_w, 2),
    "tick_seviyesi_ORTALAMA_spread_medyan_pts": round(tick_spread_median_w, 2),
    "hedef_pts_k1_5_x_atr_medyan": round(hedef_pts_k15_w, 2),
    "oran_medyan_bar_kapanis_spread": round(oran_medyan_spread_w, 2),
    "oran_p90_bar_kapanis_spread_STRES_TESTI": round(oran_p90_spread_w, 2),
    "oran_max_bar_kapanis_spread_ekstrem": round(oran_max_spread_w, 2),
    "oran_medyan_TICK_SEVIYESI_spread_EK_TEYIT": round(oran_medyan_tickspread_w, 2),
    "esik_alt_sinir": ESIK_ALT,
    "medyan_bar_kapanis_spread_uzerinden_GECTI_Mi": bool(s1_gecti_medyan_w),
    "P90_bar_kapanis_spread_STRES_TESTI_GECTI_Mi": bool(s1_gecti_p90_w),
    "hipotez1_tam_tarihsel_referans": {"oran_medyan_spread": 15.97, "oran_p90_spread": 11.91},
    "yorum": (
        "Bu pencereye ozel oran, Hipotez1'in tam-tarihsel (4,2 yil) oranindan (15,97x/11,91x) FARKLI "
        "cikabilir - bu bir hata degil, farkli/daha kisa/daha yakin-tarihli bir veri araligini yansitir "
        "(DOGRUDAN KARSILASTIRILAMAZ, sadece bu pencerenin KENDI icinde tutarliligini gosterir)."
    ),
}
print("S1 (pencereye ozel) P90 stres testi:",
      results["s1_maliyet_orani_stres_testi_PENCEREYE_OZEL"]["P90_bar_kapanis_spread_STRES_TESTI_GECTI_Mi"],
      "oran:", results["s1_maliyet_orani_stres_testi_PENCEREYE_OZEL"]["oran_p90_bar_kapanis_spread_STRES_TESTI"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (feature/etiket/S1) tamamlandi ->", OUT_PATH)

# =====================================================================
# PENCERE-ICI KRONOLOJIK BOLUM: TRAINVAL (%80) / TEST (%20) - PURGE (idx+N<=sinir) + EMBARGO
# (Karar 4 / Stratejist onerisi: "N=16-bar + 1 GUNLUK embargo" - Hipotez1/2'nin tam-tarihsel
# 24-bar/6-saat SABIT embargosundan FARKLI, pencereye ORANTILI kucultulmus/gun-bazli bir deger)
# =====================================================================
bars_per_day_median = float(np.median(daily_counts[daily_counts >= 50]))  # tam/aktif islem gunu tipik bar sayisi
EMBARGO_BARS_PILOT = int(round(bars_per_day_median * EMBARGO_TRADING_DAYS_PILOT))

trainval_count_target = int(len(window_indices) * (1 - TEST_FRACTION))
trainval_end_bar = int(window_indices[trainval_count_target - 1])
test_start_bar = trainval_end_bar + EMBARGO_BARS_PILOT

labeled_idx_all = idx_pool[~np.isnan(label[idx_pool])]

trainval_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= trainval_end_bar)]
test_idx = labeled_idx_all[(labeled_idx_all >= test_start_bar)]

results["veri_bolumu_PENCERE_ICI"] = {
    "not": "Bu bolum SADECE 90-gunluk pilot pencere icindir - Hipotez1/2'nin 4,2 yillik TRAINVAL/TEST "
           "bolumuyle KARISTIRILMAMALIDIR (Karar 4, tamamen ayri alt-deney).",
    "pencere_bar_sayisi": int(len(window_indices)),
    "bars_per_day_median_pencere": bars_per_day_median,
    "embargo_gun_sayisi": EMBARGO_TRADING_DAYS_PILOT, "embargo_bar_sayisi": EMBARGO_BARS_PILOT,
    "purge_kurali": "trainval ornekleri i+N_BARS<=trainval_end_bar ile SINIRLANDI (Hipotez1/2 ile AYNI ilke)",
    "trainval_end_bar": trainval_end_bar, "test_start_bar": test_start_bar,
    "trainval_tarih_araligi": [dates_str[window_indices[0]], dates_str[min(trainval_end_bar, n - 1)]],
    "test_tarih_araligi": [dates_str[min(test_start_bar, n - 1)], dates_str[-1]],
    "trainval_ikili_etiketli_n": int(len(trainval_idx)),
    "test_ikili_etiketli_n": int(len(test_idx)),
}
print("Pencere-ici veri bolumu:", results["veri_bolumu_PENCERE_ICI"]["trainval_ikili_etiketli_n"],
      "trainval /", results["veri_bolumu_PENCERE_ICI"]["test_ikili_etiketli_n"], "test",
      "| embargo_bar:", EMBARGO_BARS_PILOT)

# =====================================================================
# PURGED/EMBARGOLU WALK-FORWARD (TRAINVAL ICINDE, pencereye ORANTILI kucultulmus embargo ile)
# =====================================================================
seg_edges = np.linspace(window_indices[0], trainval_end_bar, WF_SEGMENTS + 1).astype(int)

def build_fold_sets(train_lo, train_hi, val_lo, val_hi):
    tr = labeled_idx_all[(labeled_idx_all >= train_lo) & (labeled_idx_all + N_BARS <= train_hi)]
    va = labeled_idx_all[(labeled_idx_all >= val_lo + EMBARGO_BARS_PILOT) & (labeled_idx_all + N_BARS <= val_hi)]
    return tr, va

wf_folds_info = []
oof_idx_list = []
oof_prob_list = []
for f in range(1, WF_SEGMENTS):
    train_lo, train_hi = int(window_indices[0]), int(seg_edges[f])
    val_lo, val_hi = int(seg_edges[f]), int(seg_edges[f + 1])
    tr_idx, va_idx = build_fold_sets(train_lo, train_hi, val_lo, val_hi)
    if len(tr_idx) < 200 or len(va_idx) < 50:
        wf_folds_info.append({"fold": f, "durum": "yetersiz_ornek_atlandi",
                               "train_n": int(len(tr_idx)), "val_n": int(len(va_idx))})
        continue
    Xtr = X_full[tr_idx]; ytr = label[tr_idx]
    Xva = X_full[va_idx]; yva = label[va_idx]
    mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    Xtr_n = (Xtr - mu) / sd
    Xva_n = (Xva - mu) / sd
    model_f = lgb.LGBMClassifier(**LGB_PARAMS)
    model_f.fit(Xtr_n, ytr, eval_set=[(Xva_n, yva)],
                callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)])
    p_va = model_f.predict_proba(Xva_n)[:, 1]
    auc = roc_auc_score(yva, p_va)
    wf_folds_info.append({
        "fold": f, "train_lo_bar": int(train_lo), "train_hi_bar": int(train_hi),
        "val_lo_bar": int(val_lo), "val_hi_bar": int(val_hi),
        "train_n": int(len(tr_idx)), "val_n": int(len(va_idx)),
        "val_auc": round(float(auc), 4),
        "best_iteration": int(model_f.best_iteration_) if model_f.best_iteration_ else LGB_PARAMS["n_estimators"],
    })
    oof_idx_list.append(va_idx)
    oof_prob_list.append(p_va)
    print(f"WF fold {f}: train_n={len(tr_idx)} val_n={len(va_idx)} AUC={auc:.4f}")

results["walk_forward_purged_embargolu_PENCERE_ICI"] = {
    "segment_sayisi": WF_SEGMENTS, "fold_sayisi": WF_SEGMENTS - 1,
    "embargo_bars": EMBARGO_BARS_PILOT, "sonuclar": wf_folds_info,
}
auc_list = [f_["val_auc"] for f_ in wf_folds_info if "val_auc" in f_]
results["walk_forward_purged_embargolu_PENCERE_ICI"]["auc_ozet"] = {
    "ortalama": round(float(np.mean(auc_list)), 4) if auc_list else None,
    "std": round(float(np.std(auc_list)), 4) if auc_list else None,
    "min": round(float(np.min(auc_list)), 4) if auc_list else None,
    "max": round(float(np.max(auc_list)), 4) if auc_list else None,
    "gecerli_fold_sayisi": len(auc_list),
}
print("Walk-forward AUC ozet:", results["walk_forward_purged_embargolu_PENCERE_ICI"]["auc_ozet"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (veri bolumu + walk-forward) tamamlandi ->", OUT_PATH)

# =====================================================================
# ESIK KALIBRASYONU (out-of-fold tahminleri uzerinden - TEST SETINE HENUZ BAKILMADI, S2 Madde2)
# =====================================================================
oof_idx_all = np.concatenate(oof_idx_list) if oof_idx_list else np.array([], dtype=int)
oof_prob_all = np.concatenate(oof_prob_list) if oof_prob_list else np.array([])
oof_label_all = label[oof_idx_all] if len(oof_idx_all) else np.array([])

esik_tablosu = []
for t_long, t_short in zip(THRESH_LONG_CANDIDATES, THRESH_SHORT_CANDIDATES):
    long_mask = oof_prob_all >= t_long
    short_mask = oof_prob_all <= t_short
    long_n = int(long_mask.sum()); short_n = int(short_mask.sum())
    long_prec = float((oof_label_all[long_mask] == 1.0).mean()) if long_n else None
    short_prec = float((oof_label_all[short_mask] == 0.0).mean()) if short_n else None
    toplam_n = long_n + short_n
    kapsama = round(toplam_n / len(oof_prob_all), 4) if len(oof_prob_all) else None
    esik_tablosu.append({
        "esik_long": t_long, "esik_short": t_short,
        "long_n": long_n, "long_precision_proxy_WR": round(long_prec, 4) if long_prec is not None else None,
        "long_yeterli_orneklem": long_n >= MIN_SAMPLE,
        "short_n": short_n, "short_precision_proxy_WR": round(short_prec, 4) if short_prec is not None else None,
        "short_yeterli_orneklem": short_n >= MIN_SAMPLE,
        "toplam_islem_n": toplam_n, "kapsama_orani": kapsama,
    })

def esik_skor(row):
    vals = []
    if row["long_yeterli_orneklem"] and row["long_precision_proxy_WR"] is not None:
        vals.append(row["long_precision_proxy_WR"])
    if row["short_yeterli_orneklem"] and row["short_precision_proxy_WR"] is not None:
        vals.append(row["short_precision_proxy_WR"])
    return np.mean(vals) if vals else -1

esik_tablosu_sirali = sorted(esik_tablosu, key=esik_skor, reverse=True)
gecerli_adaylar = [row for row in esik_tablosu_sirali if esik_skor(row) > -1]
yetersiz_uyarisi = False
if gecerli_adaylar:
    secilen_esik = gecerli_adaylar[0]
else:
    secilen_esik = sorted(esik_tablosu, key=lambda r: r["toplam_islem_n"], reverse=True)[0]
    yetersiz_uyarisi = True

THRESH_LONG_FINAL = secilen_esik["esik_long"]
THRESH_SHORT_FINAL = secilen_esik["esik_short"]

results["esik_kalibrasyonu"] = {
    "yontem": "Out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR) taramasi - TEST SETINE BAKILMADI",
    "oof_ornek_sayisi": int(len(oof_prob_all)),
    "min_sample_esigi": MIN_SAMPLE,
    "aday_tablosu": esik_tablosu,
    "SECILEN_ESIK_LONG": THRESH_LONG_FINAL,
    "SECILEN_ESIK_SHORT": THRESH_SHORT_FINAL,
    "YETERSIZ_ORNEKLEM_FALLBACK_UYGULANDI": yetersiz_uyarisi,
}
print("Esik kalibrasyonu:", results["esik_kalibrasyonu"]["SECILEN_ESIK_LONG"],
      results["esik_kalibrasyonu"]["SECILEN_ESIK_SHORT"], "fallback:", yetersiz_uyarisi)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (esik kalibrasyonu) tamamlandi ->", OUT_PATH)

# =====================================================================
# FINAL MODEL: TUM TRAINVAL uzerinde egitim (SL/TP/esik ARTIK SABIT)
# =====================================================================
inner_val_start = int(seg_edges[WF_SEGMENTS - 1])
final_train_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= inner_val_start)]
final_innerval_idx = labeled_idx_all[
    (labeled_idx_all >= inner_val_start + EMBARGO_BARS_PILOT) & (labeled_idx_all + N_BARS <= trainval_end_bar)
]
print("Final egitim n:", len(final_train_idx), "ic-validasyon n:", len(final_innerval_idx))

Xtr_final = X_full[final_train_idx]; ytr_final = label[final_train_idx]
Xiv_final = X_full[final_innerval_idx]; yiv_final = label[final_innerval_idx]

mu_final = Xtr_final.mean(axis=0); sd_final = Xtr_final.std(axis=0); sd_final[sd_final == 0] = 1.0
Xtr_final_n = (Xtr_final - mu_final) / sd_final
Xiv_final_n = (Xiv_final - mu_final) / sd_final

final_model = lgb.LGBMClassifier(**LGB_PARAMS)
final_model.fit(Xtr_final_n, ytr_final, eval_set=[(Xiv_final_n, yiv_final)],
                 callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)])
final_iv_auc = roc_auc_score(yiv_final, final_model.predict_proba(Xiv_final_n)[:, 1])
print("Final model ic-validasyon AUC:", final_iv_auc, "best_iter:", final_model.best_iteration_)

feat_importance = dict(zip(feature_names, [int(x) for x in final_model.feature_importances_]))
results["final_model_egitimi"] = {
    "egitim_n": int(len(final_train_idx)),
    "ic_validasyon_n": int(len(final_innerval_idx)),
    "ic_validasyon_auc": round(float(final_iv_auc), 4),
    "best_iteration": int(final_model.best_iteration_) if final_model.best_iteration_ else LGB_PARAMS["n_estimators"],
    "hiperparametreler_SABIT": LGB_PARAMS,
    "feature_importance_gain_split": feat_importance,
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (final model) tamamlandi ->", OUT_PATH)

# =====================================================================
# TEST SETI - TEK KEZ KULLANIM (S2 Madde2)
# =====================================================================
Xte = X_full[test_idx]
Xte_n = (Xte - mu_final) / sd_final
p_test = final_model.predict_proba(Xte_n)[:, 1]
y_test_binary_label = label[test_idx]
test_auc = roc_auc_score(y_test_binary_label, p_test) if len(np.unique(y_test_binary_label)) > 1 else None
print("TEST SETI AUC (tek-kez):", test_auc)

results["test_seti_siniflandirma_performansi"] = {
    "test_n": int(len(test_idx)),
    "test_auc": round(float(test_auc), 4) if test_auc is not None else None,
}

results["test_p_dagilimi_TANI"] = {
    "p_test_min": round(float(p_test.min()), 4), "p_test_max": round(float(p_test.max()), 4),
    "p_test_mean": round(float(p_test.mean()), 4), "p_test_std": round(float(p_test.std()), 4),
    "p_test_percentileler": {
        str(pc): round(float(np.percentile(p_test, pc)), 4) for pc in [1, 5, 25, 50, 75, 95, 99]
    },
    "esik_long_asan_bar_sayisi": int((p_test >= THRESH_LONG_FINAL).sum()),
    "esik_short_asan_bar_sayisi": int((p_test <= THRESH_SHORT_FINAL).sum()),
}
print("TANI - p_test min/max/mean/std:", results["test_p_dagilimi_TANI"]["p_test_min"],
      results["test_p_dagilimi_TANI"]["p_test_max"], results["test_p_dagilimi_TANI"]["p_test_mean"],
      results["test_p_dagilimi_TANI"]["p_test_std"])

# =====================================================================
# TICK-BAZLI GERCEK MALIYET MODELI - onceden yuklenmis Grup D tick dizileri KULLANILIR (ayrica MT5
# copy_ticks_from cagrisi YAPILMAZ - ayni veri kaynagindan tutarlilik + performans)
# =====================================================================
TICK_LOOKUP_COUNT = {"call": 0, "hit": 0, "miss_bucket_yok": 0, "miss_zaman_uyusmazligi": 0, "miss_gecersiz_kotasyon": 0}

def get_tick_quote(bar_idx):
    """Bar_idx+1'in (giris barinin) KENDI bucket'indaki ILK tick'in ask/bid'i - onceden yuklenmis
    Grup D tick dizilerinden (bucket_starts/tk_ask/tk_bid) okunur, YENI bir MT5 cagrisi YAPILMAZ."""
    TICK_LOOKUP_COUNT["call"] += 1
    bar_epoch = int(t[bar_idx])
    key_ = bar_epoch // 900
    pos_ = bucket_key_to_pos.get(key_)
    if pos_ is None:
        TICK_LOOKUP_COUNT["miss_bucket_yok"] += 1
        return None
    s = bucket_starts[pos_]
    tick_epoch_i = int(tk_time[s])
    fark = tick_epoch_i - bar_epoch
    if fark > MAX_TICK_MISMATCH_SEC or fark < -1:
        TICK_LOOKUP_COUNT["miss_zaman_uyusmazligi"] += 1
        return None
    ask = float(tk_ask[s]); bid = float(tk_bid[s])
    if ask <= 0 or bid <= 0 or ask < bid:
        TICK_LOOKUP_COUNT["miss_gecersiz_kotasyon"] += 1
        return None
    TICK_LOOKUP_COUNT["hit"] += 1
    return (ask, bid)

def simulate_trade(signal_idx, direction):
    entry_idx = signal_idx + 1
    if entry_idx >= n:
        return None, "veri_sinirinda"
    entry_theo = c[signal_idx]
    exit_idx = exit_idx_arr[signal_idx]
    if exit_idx < 0:
        return None, "etiket_gecersiz"
    if label_neither[signal_idx]:
        exit_theo = time_exit_price_arr[signal_idx]
        exit_reason = "zaman_asimi"
    elif label[signal_idx] == 1.0:
        exit_theo = tp_price_arr[signal_idx]
        exit_reason = "yukari_bariyer_ilk"
    else:
        exit_theo = sl_price_arr[signal_idx]
        exit_reason = "asagi_bariyer_ilk"

    raw_pts = (exit_theo - entry_theo) / POINT if direction == 1 else (entry_theo - exit_theo) / POINT

    quote = get_tick_quote(entry_idx)
    if quote is None:
        return None, "tick_verisi_yok"
    ask, bid = quote
    spread_pts_tick = (ask - bid) / POINT
    if direction == 1:
        entry_real = ask; slip_pts = (entry_real - entry_theo) / POINT
    else:
        entry_real = bid; slip_pts = (entry_theo - entry_real) / POINT
    total_cost_pts = slip_pts + spread_pts_tick / 2.0
    net_pts = raw_pts - total_cost_pts

    risk_pts = K_ATR * atr14_m15[signal_idx]
    risk_usd = risk_pts * POINT * CONTRACT_SIZE * LOT_FIXED
    risk_pct_of_kasa = risk_usd / KASA_USD

    return {
        "signal_idx": int(signal_idx), "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
        "tarih": dates_str[signal_idx], "saat_sinyal": int(hours[signal_idx]),
        "yon": "LONG" if direction == 1 else "SHORT",
        "olasilik_p_yukari": None,
        "hicbiri_mi": bool(label_neither[signal_idx]), "sebep": exit_reason,
        "atr_entry_pts": round(float(atr14_m15[signal_idx]), 2),
        "risk_pts": round(float(risk_pts), 2), "risk_usd_0_01_lot": round(float(risk_usd), 4),
        "risk_pct_of_kasa": round(float(risk_pct_of_kasa), 6),
        "tick_spread_pts": round(float(spread_pts_tick), 3),
        "giris_slipaj_pts": round(float(slip_pts), 3),
        "toplam_maliyet_pts": round(float(total_cost_pts), 3),
        "raw_pts": round(float(raw_pts), 3), "net_pts": round(float(net_pts), 3),
        "net_usd_0_01_lot": round(float(net_pts * POINT * CONTRACT_SIZE * LOT_FIXED), 4),
    }, "ok"

print("Test seti icin trade simulasyonu baslatiliyor...")

signal_dir = np.zeros(len(test_idx), dtype=int)
signal_dir[p_test >= THRESH_LONG_FINAL] = 1
signal_dir[p_test <= THRESH_SHORT_FINAL] = -1

trade_log = []
reasons = defaultdict(int)
open_until = -1
for pos_in_test, i in enumerate(test_idx):
    if signal_dir[pos_in_test] == 0:
        continue
    if i <= open_until:
        reasons["cakisma_atlandi"] += 1
        continue
    res, status = simulate_trade(i, int(signal_dir[pos_in_test]))
    if res is None:
        reasons[status] += 1
        continue
    res["olasilik_p_yukari"] = round(float(p_test[pos_in_test]), 4)
    trade_log.append(res)
    open_until = res["exit_idx"]

print("Test seti PRIMARY (hicbiri-haric) tetiklenen islem sayisi:", len(trade_log), "atlanma:", dict(reasons))

def summarize_trades(trades):
    if not trades:
        return {"toplam_islem": 0, "win_rate": None, "profit_factor": None,
                "net_profit_pts": 0.0, "net_profit_usd_0_01_lot": 0.0, "max_drawdown_pct_kasa2000": None}
    net = np.array([x["net_pts"] for x in trades])
    net_usd = np.array([x["net_usd_0_01_lot"] for x in trades])
    wins = net[net > 0]; losses = net[net <= 0]
    win_rate = len(wins) / len(net)
    gross_profit = wins.sum() if len(wins) else 0.0
    gross_loss = -losses.sum() if len(losses) else 0.0
    pf = (gross_profit / gross_loss) if gross_loss > 0 else (None if gross_profit == 0 else float("inf"))
    cum_usd = np.cumsum(net_usd)
    running_max = np.maximum.accumulate(np.concatenate(([0.0], cum_usd)))[1:]
    dd_usd = cum_usd - running_max
    max_dd_pct = float(dd_usd.min() / KASA_USD * 100) if len(dd_usd) else 0.0
    return {
        "toplam_islem": int(len(net)), "win_rate": round(float(win_rate), 4),
        "profit_factor": (round(float(pf), 3) if pf not in (None, float("inf")) else pf),
        "net_profit_pts": round(float(net.sum()), 2),
        "net_profit_usd_0_01_lot": round(float(net_usd.sum()), 2),
        "max_drawdown_pct_kasa2000": round(max_dd_pct, 3),
        "ortalama_risk_pct_of_kasa": round(float(np.mean([x["risk_pct_of_kasa"] for x in trades])), 5),
        "ortalama_toplam_maliyet_pts": round(float(np.mean([x["toplam_maliyet_pts"] for x in trades])), 3),
        "ortalama_atr_entry_pts": round(float(np.mean([x["atr_entry_pts"] for x in trades])), 2),
    }

def minimum_sample_warning(count, label_str, threshold=MIN_SAMPLE):
    if count == 0:
        return f"{label_str}: ISLEM YOK (n=0)."
    if count < threshold:
        return f"{label_str}: YETERSIZ ORNEKLEM (n={count} < {threshold}) - sonuc yorumlanabilir ama tek basina karar dayanagi OLAMAZ."
    return None

primary_summary = summarize_trades(trade_log)
long_trades = [x for x in trade_log if x["yon"] == "LONG"]
short_trades = [x for x in trade_log if x["yon"] == "SHORT"]

warnings_list = [
    "ISTATISTIKSEL_GUC_SINIRLI (Stratejist'in ZORUNLU cerceveleme talebi): bu hipotezin kucuk "
    "orneklem boyutu (asagidaki gercek pencere_bar_sayisi/test_n) nedeniyle istatistiksel guc "
    "SINIRLIDIR - sonuc 'KESIN RED/KABUL' DEGIL, 'bu olcekte ilk gozlem, tam-tarihsel olceklendirme "
    "HALA cozulmemis' seklinde yorumlanmalidir.",
]
w = minimum_sample_warning(len(trade_log), "TEST_PRIMARY_tum_islemler")
if w: warnings_list.append(w)
w = minimum_sample_warning(len(long_trades), "TEST_PRIMARY_LONG")
if w: warnings_list.append(w)
w = minimum_sample_warning(len(short_trades), "TEST_PRIMARY_SHORT")
if w: warnings_list.append(w)
if yetersiz_uyarisi:
    warnings_list.append(
        "ESIK_KALIBRASYONU_YETERSIZ_ORNEKLEM: hicbir esik adayi out-of-fold kumede MIN_SAMPLE "
        f"(>={MIN_SAMPLE}) esigini HER IKI tarafta da gecemedi - fallback secildi."
    )
warnings_list.append(
    f"SINYAL_SIKLIGI: test setindeki {len(test_idx)} bar icinden {len(trade_log)} bar esik-tetiklemeli "
    f"islem uretti (kapsama ~{round(len(trade_log)/len(test_idx)*100,3) if len(test_idx) else 0}%)."
)

results["test_trade_simulasyonu_PRIMARY"] = {
    "esik_long": THRESH_LONG_FINAL, "esik_short": THRESH_SHORT_FINAL,
    "atlanma_nedenleri": dict(reasons),
    "tum_islemler_ozet": primary_summary,
    "LONG_ozet": summarize_trades(long_trades),
    "SHORT_ozet": summarize_trades(short_trades),
    "tick_lookup_istatistigi": dict(TICK_LOOKUP_COUNT),
}
print("PRIMARY test sonuc ozeti:", primary_summary)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (PRIMARY trade sim) tamamlandi ->", OUT_PATH)

# =====================================================================
# SUPPLEMENTARY - "HICBIRI DAHIL" GERCEKCI CANLI-BENZERI CAPRAZ KONTROL
# =====================================================================
test_idx_all = idx_pool[(idx_pool >= test_start_bar)]
Xte_all = X_full[test_idx_all]
Xte_all_n = (Xte_all - mu_final) / sd_final
p_test_all = final_model.predict_proba(Xte_all_n)[:, 1]

signal_dir_all = np.zeros(len(test_idx_all), dtype=int)
signal_dir_all[p_test_all >= THRESH_LONG_FINAL] = 1
signal_dir_all[p_test_all <= THRESH_SHORT_FINAL] = -1

trade_log_all = []
reasons_all = defaultdict(int)
open_until2 = -1
for pos_in_test, i in enumerate(test_idx_all):
    if signal_dir_all[pos_in_test] == 0:
        continue
    if i <= open_until2:
        reasons_all["cakisma_atlandi"] += 1
        continue
    res, status = simulate_trade(i, int(signal_dir_all[pos_in_test]))
    if res is None:
        reasons_all[status] += 1
        continue
    res["olasilik_p_yukari"] = round(float(p_test_all[pos_in_test]), 4)
    trade_log_all.append(res)
    open_until2 = res["exit_idx"]

print("SUPPLEMENTARY (hicbiri dahil) tetiklenen islem sayisi:", len(trade_log_all), "atlanma:", dict(reasons_all))

supplementary_summary = summarize_trades(trade_log_all)
neither_in_trades = [x for x in trade_log_all if x["hicbiri_mi"]]

results["test_trade_simulasyonu_SUPPLEMENTARY_hicbiri_dahil"] = {
    "atlanma_nedenleri": dict(reasons_all),
    "tum_islemler_ozet": supplementary_summary,
    "hicbiri_zaman_asimi_ile_biten_islem_sayisi": len(neither_in_trades),
    "hicbiri_orani_tetiklenen_islemler_icinde": round(len(neither_in_trades) / len(trade_log_all), 4) if trade_log_all else None,
}
print("SUPPLEMENTARY test sonuc ozeti:", supplementary_summary)

# =====================================================================
# TAM ISLEM LOGU + UYARILAR + NIHAI JSON
# =====================================================================
results["islem_logu_PRIMARY_tam"] = trade_log
results["islem_logu_SUPPLEMENTARY_tam"] = trade_log_all
results["uyarilar"] = warnings_list

results["hipotez1_karsilastirma_referansi"] = {
    "not": "Hipotez1 (v2/Tur2) raporundan/ham JSON'undan AYNEN alinan referans degerler - BU turde "
           "YENIDEN HESAPLANMADI, FARKLI veri araligi/olcek (4,2 yil vs 90 gun) oldugu icin DOGRUDAN "
           "KARSILASTIRILAMAZ, sadece BAGLAM icin buraya kopyalandi (CLAUDE.md sayisal-tutarlilik ilkesi).",
    "veri_araligi": "2022-04-18 -> 2026-07-10 (4,2 yil, tam-tarihsel)",
    "walk_forward_auc_ortalama": 0.5075, "walk_forward_auc_std": 0.0122,
    "final_ic_validasyon_auc": 0.4990, "test_auc": 0.5170,
    "esik_long": 0.55, "esik_short": 0.45,
    "primary_toplam_islem": 0, "supplementary_toplam_islem": 0,
}

results["hedef_karsilastirma_ve_karar"] = {
    "hedef_pf": HEDEF_PF, "hedef_wr_rr11": HEDEF_WR_RR11, "hedef_dd": HEDEF_DD,
    "gozlemlenen_pf_PRIMARY": primary_summary.get("profit_factor"),
    "gozlemlenen_wr_PRIMARY": primary_summary.get("win_rate"),
    "gozlemlenen_dd_PRIMARY": primary_summary.get("max_drawdown_pct_kasa2000"),
    "gozlemlenen_pf_SUPPLEMENTARY": supplementary_summary.get("profit_factor"),
    "gozlemlenen_wr_SUPPLEMENTARY": supplementary_summary.get("win_rate"),
}

pf_ok = (
    primary_summary.get("toplam_islem", 0) > 0 and
    primary_summary.get("profit_factor") not in (None, float("inf")) and
    primary_summary.get("profit_factor") >= HEDEF_PF
)
wr_ok = (
    primary_summary.get("toplam_islem", 0) > 0 and
    primary_summary.get("win_rate") is not None and
    primary_summary.get("win_rate") >= HEDEF_WR_RR11
)
dd_ok = (
    primary_summary.get("toplam_islem", 0) > 0 and
    primary_summary.get("max_drawdown_pct_kasa2000") is not None and
    abs(primary_summary.get("max_drawdown_pct_kasa2000")) <= HEDEF_DD * 100
)
if primary_summary.get("toplam_islem", 0) == 0:
    karar = "RED"
    karar_gerekce = "PRIMARY test setinde 0 islem tetiklendi - Ortak Ilkeler'deki minimum orneklem uyarisi geregi hicbir hedefin karsilandigi iddia edilemez (S2 Madde4)."
elif pf_ok and wr_ok and dd_ok:
    karar = "KABUL (KISITLI/PILOT - TEK BASINA NIHAI KARAR DAYANAGI DEGIL)"
    karar_gerekce = "HEDEF_PF/HEDEF_WR/HEDEF_DD kriterlerinin UCU DE bu kisitli 90-gunluk pencerede karsilandi - ANCAK istatistiksel guc SINIRLIDIR, bu Tur 2'nin nihai kararinin TEK BASINA dayanagi OLAMAZ (Stratejist Karar4/Oncelik-3)."
else:
    karar = "RED"
    karar_gerekce = f"HEDEF kriterlerinden en az biri karsilanmadi (PF_ok={pf_ok}, WR_ok={wr_ok}, DD_ok={dd_ok})."

results["hedef_karsilastirma_ve_karar"]["KARAR"] = karar
results["hedef_karsilastirma_ve_karar"]["gerekce"] = karar_gerekce
print("KARAR:", karar, "-", karar_gerekce)

results["hipotez_ozet"] = {
    "hipotez_adi": "LightGBM Ikili Yon-Tahmini + Grup 1-5/B/D (mikro-yapi) - 90 GUNLUK KISITLI/PILOT PENCERE - HIPOTEZ 3 (v2/Tur2)",
    "yaklasim_turu": "Makine Ogrenmesi - Gradient Boosting (LightGBM) + kural-tabanli tick-agregasyon (Grup D girdisi)",
    "oncelik": "3-Dusuk (on-gozlem)",
    "olceklenebilirlik_durumu": "COZULMEDI - bu rapor Grup D'nin 4,2 yillik tam veriye tasinma yontemini COZMEZ",
    "hedef_pf": HEDEF_PF, "hedef_wr_rr11": HEDEF_WR_RR11, "hedef_dd": HEDEF_DD,
    "KARAR": karar,
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("NIHAI KAYIT tamamlandi ->", OUT_PATH)
print("Hipotez ozet:", results["hipotez_ozet"])

mt5.shutdown()
print("MT5 baglantisi kapatildi. Script tamamlandi.")
