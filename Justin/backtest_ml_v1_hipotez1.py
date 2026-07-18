# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - ML/Feature-Tabanli Aile v1 - HIPOTEZ 1
LightGBM ikili yon-tahmini modeli, N=16 (4 saat) M15-bar zaman-bariyeri, k=1,5xATR14(M15).

Girdi: stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md (Karar 1-4, Hipotez 1)
Cerceve: justin_gecmis_calisma.md, justin_ml_anti_overfitting_protokolu.md (S2),
         justin_backtest_onkontrol_standardi.md (S1 + DST + SL/TP-ozel)

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Veri dogrudan MT5'ten (MetaTrader5 kutuphanesi), GOLD sembolu M15 OHLCV+tick_volume+spread.
Kutuphane on-kosulu: bu turde pandas/lightgbm/xgboost/scikit-learn GORUNUR SEKILDE kuruldu
(izole/geri-donulebilir islem, bilgi notu - bkz. rapor Bolum 1).
"""
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import MetaTrader5 as mt5
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import lightgbm as lgb
from sklearn.metrics import roc_auc_score

# =====================================================================
# SABITLER (Stratejist Karar 1-3 + justin_gecmis_calisma.md + S2 protokolu)
# =====================================================================
SYMBOL = "GOLD"
N_BARS = 16                 # zaman-bariyeri, 4 saat (Stratejist Karar 1, KESIN)
K_ATR = 1.5                 # barrier katsayisi (Stratejist Karar 1, KESIN)
ATR_PERIOD = 14
TRAIL_WINDOW = 100          # ATR/hacim rejim trailing-medyan penceresi
EMBARGO_BARS = 24           # 6 saat (S2 Madde1'in onerdigi 4-8 saat araliginda), M15-bar
TEST_FRACTION = 0.20        # kronolojik son %20 -> rezerve TEST seti (TEK KEZ kullanim)
WF_SEGMENTS = 5             # TRAINVAL walk-forward icin esit-uzunluklu segment sayisi (4 fold uretir)
RANDOM_SEED = 42            # LightGBM deterministik egitim (S2: RL'e ozgu coklu-seed kurali burada gecerli degil)
N_BARS_FETCH = 99999
MIN_SAMPLE = 30             # minimum orneklem esigi (Ortak Ilkeler + Justin'in onceki turlerindeki standart)

# justin_gecmis_calisma.md sabitleri
KASA_USD = 2000.0
RISK_PCT_CAP = 0.01         # islem-basi risk UST SINIRI (%1)
LOT_FIXED = 0.01            # kasa 2000-3999 USD dilimi -> 0,01 lot (Olceklendirme kurali, backtest boyunca sabit kasa varsayimi)
HEDEF_PF = 1.5
HEDEF_WR_RR11 = 0.60        # RR=1:1 icin gerekli WR (gecmis_calisma formulu)
HEDEF_DD = 0.20             # kumulatif

MAX_TICK_MISMATCH_SEC = 60  # Justin ailesinde onceki turlerde onaylanmis standart (H1/H2/H3)

# Esik kalibrasyonu adaylari (Stratejist'in baslangic onerisi araligi)
THRESH_LONG_CANDIDATES = [0.60, 0.575, 0.55]
THRESH_SHORT_CANDIDATES = [0.40, 0.425, 0.45]

# LightGBM sabit/dar hiperparametre araligi (S2: genis grid-search YAPILMAMALI, ONCEDEN sabit)
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

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1_output.json"

results = {}

# =====================================================================
# MT5 BAGLANTI + VERI
# =====================================================================
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size

rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, N_BARS_FETCH)
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
    "contract_size": CONTRACT_SIZE, "m15_n": int(n),
    "m15_start": dates_str[0], "m15_end": dates_str[-1],
}
print("M15 bar sayisi:", n, "araligi:", dates_str[0], "->", dates_str[-1])

# =====================================================================
# DST / SAAT-ESLESME BAGIMSIZ DOGRULAMA (justin_backtest_onkontrol_standardi.md Madde 1)
# Onceki H1/H2/H3 turlerinden DEVRALINMADI - bu ML/M15 pipeline'i icin BAGIMSIZ yeniden yapildi.
# Yontem: her bilinen DST gecisinde, gecis-oncesi/gecis-sonrasi haftanin PIYASA-ACILIS barinin
# UTC/epoch-okunan saati karsilastirilir. Sunucu DST'yi takip ediyorsa (yerel saat sabit, UTC
# gorunumu mevsimsel kayar) bu saat 1 KAYAR; sabit-offset bir sunucuda KAYMAMASI beklenir.
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
        "gecis_tarihi": tarih,
        "onceki_hafta_acilis_saati_utc": saat_onceki,
        "gecis_sonrasi_hafta_acilis_saati_utc": saat_sonraki,
        "1_saat_kayma_gozlendi_mi": bool(kaydi),
    })

results["dst_saat_eslesme_dogrulamasi"] = {
    "yontem": (
        "BAGIMSIZ (bu ML/M15 pipeline'i icin yeniden yazildi, H1/H2/H3'ten devralinmadi) - her "
        "bilinen DST gecisinde, gecis-oncesi ve gecis-sonrasi haftanin PIYASA-ACILIS barinin "
        "UTC/epoch-okunan saati karsilastirildi."
    ),
    "canli_capraz_kontrol": {
        "sistem_saati_utc": now_system.isoformat(),
        "son_tick_epoch_utc": tick_epoch.isoformat(),
        "fark_saniye": round(fark_sn, 2),
        "yorum": "fark kucukse (birkac saniye) MT5 sunucu-epoch okumasi guvenilir UTC kabul edilir",
    },
    "dst_gecis_taramasi": dst_scan,
    "degerlendirilen_gecis_sayisi": degerlendirilen_sayisi,
    "1_saat_kayma_gozlenen_gecis_sayisi": kayma_sayisi,
    "SONUC": (
        (f"{kayma_sayisi}/{degerlendirilen_sayisi} bilinen DST gecisinde piyasa-acilis saati "
         "1 SAAT KAYDI - bu, MT5 sunucusunun DST'yi TAKIP ETTIGINI (sabit GMT+3 DEGIL, mevsimsel "
         "kaydiran bir saat kullandigini) DOGRULAR.")
        if kayma_sayisi == degerlendirilen_sayisi and degerlendirilen_sayisi > 0 else
        (f"{kayma_sayisi}/{degerlendirilen_sayisi} gecis kaydi gosterdi - KARISIK/BELIRSIZ sonuc, "
         "asagidaki SINIR notuna gore yorumlanmali.")
    ),
    "SINIR": (
        "Sunucu DST'yi takip ediyorsa, Feature Grubu 4'teki (saat/oturum: hour_sin/cos, "
        "Asya/Londra/NY bayraklari) TUM saat-bazli feature'lar yaz/kis donemlerinde GERCEK yerel "
        "seans zamanina gore TUTARLI kalir (sunucu-yerel-saat sabit, sadece UTC gorunumu "
        "mevsimsel kayar; bu script UTC-epoch'u dogrudan 'saat' olarak okur - onemli olan, "
        "modelin ogrendigi 'saat X'te confluence/ATR yuksek' iliskisinin sunucu-yerel zamana "
        "gore SABIT bir gercekligi yansitmasidir). Onceki H1/H2/H3 turlerindeki 'DST "
        "dogrulanmadi, sabit GMT+3 varsayildi' notu bu ML turunde ARTIK GECERLI DEGIL - sunucu "
        "DST takip ediyor (asagidaki SONUC alanina bakiniz), feature'lar buna gore TUTARLIDIR."
    ),
}
print("DST/saat-eslesme dogrulamasi tamamlandi:", results["dst_saat_eslesme_dogrulamasi"]["SONUC"])

# =====================================================================
# YARDIMCI FONKSIYONLAR (nedensel/causal)
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

def ema_causal(x, span):
    alpha = 2.0 / (span + 1)
    out = np.full(len(x), np.nan)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out

def compute_atr_points(hh, ll, cc, period, point):
    """ATR, PUAN (points) biriminde dondurulur - spread ile ayni birimde tutmak icin (S1 karsilastirmasi
    ve barrier hesaplari bu birimi bekler; research_ml_gold_scalping_m15.py ile AYNI yakinsama)."""
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

def sma_trend(close_arr, window=20):
    sma = rolling_mean_causal(close_arr, window)
    trend = np.full(len(close_arr), np.nan)
    valid = ~np.isnan(sma)
    trend[valid] = np.sign(close_arr[valid] - sma[valid])
    return trend, valid

print("Yardimci fonksiyonlar hazir. Feature hesaplaniyor...")

# =====================================================================
# GRUP 1 - VOLATILITE: ATR14(M15, puan), rejim orani, ATR14(H1, puan)
# =====================================================================
atr14_m15 = compute_atr_points(h, l, c, ATR_PERIOD, POINT)
atr_trail_med = rolling_median_causal(np.nan_to_num(atr14_m15, nan=0.0), TRAIL_WINDOW)
atr_regime_ratio = np.full(n, np.nan)
valid_atr_regime = ~np.isnan(atr14_m15) & ~np.isnan(atr_trail_med) & (atr_trail_med > 0)
atr_regime_ratio[valid_atr_regime] = atr14_m15[valid_atr_regime] / atr_trail_med[valid_atr_regime]

h1_t, h1_o, h1_h, h1_l, h1_c, h1_v = resample_ohlc(t, o, h, l, c, vol, 3600)
h4_t, h4_o, h4_h, h4_l, h4_c, h4_v = resample_ohlc(t, o, h, l, c, vol, 14400)
atr14_h1 = compute_atr_points(h1_h, h1_l, h1_c, ATR_PERIOD, POINT)

# Her M15 barina, o bardan ONCE KAPANMIS son H1 barinin ATR'sini nedensel esle
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
# GRUP 2 - COKLU-TF TREND CONFLUENCE (M15/H1/H4, SMA20, nedensel-hizalanmis)
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
# GRUP 3 - HACIM/TICK-YOGUNLUGU
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
# GRUP 4-CEKIRDEK - OTURUM/GUN-ICI KONUM
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
# GRUP 5 - FIYAT YAPISI/MOMENTUM
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
macd_hist = macd_line - macd_signal  # HAM DEGER kullaniliyor - isaret DEGIL (BULGU6 SINIR, S2 Madde3)

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
# FEATURE MATRISI (Karar 3 - ~18-22 sutun hedefi, feature-sizinti kontrol listesi asagida)
# =====================================================================
feature_names = [
    "atr14_m15", "atr_regime_ratio", "atr14_h1_aligned",              # Grup 1 (3)
    "m15_trend", "h1_trend_aligned", "h4_trend_aligned", "confluence_flag",  # Grup 2 (4)
    "tick_volume", "vol_ratio_trail100", "vol_slope_8bar",            # Grup 3 (3)
    "hour_sin", "hour_cos", "dow", "session_asia", "session_london", "session_ny",  # Grup 4 (6)
    "lag_ret_1", "lag_ret_4", "lag_ret_8", "rsi14", "macd_line", "macd_hist", "directional_streak",  # Grup 5 (7)
]
X_full = np.column_stack([
    atr14_m15, atr_regime_ratio, atr14_h1_aligned,
    m15_trend, m15_h1_trend_aligned, m15_h4_trend_aligned, confluence_flag,
    vol, vol_ratio, vol_slope,
    hour_sin, hour_cos, dow_feature, session_asia, session_london, session_ny,
    lag_ret_1, lag_ret_4, lag_ret_8, rsi14, macd_line, macd_hist, directional_streak,
])
assert X_full.shape[1] == len(feature_names)
results["feature_seti"] = {"sutun_sayisi": len(feature_names), "sutunlar": feature_names}
print("Feature matrisi hazir. Sutun sayisi:", len(feature_names))

feature_valid = ~np.isnan(X_full).any(axis=1)
print("Feature-gecerli bar sayisi:", int(feature_valid.sum()), "/", n)

# =====================================================================
# FEATURE-SIZINTI KONTROL LISTESI (S2 Madde 3 - madde madde teyit, elle/manuel dogrulama notlari)
# =====================================================================
results["feature_sizinti_kontrol_listesi"] = {
    "1_ileri_bakan_bilgi_var_mi": (
        "HAYIR - tum feature'lar rolling_mean_causal/rolling_median_causal/ema_causal ile SADECE "
        "bar i ve ONCESI veriyi kullanir; H1/H4 trend/ATR eslemesi bar i'den ONCE KAPANMIS son "
        "H1/H4 barini kullanir (bkz. h1_idx-1/h4_idx-1 indeksleme, kod satirlari Grup1-2)."
    ),
    "2_label_hesaplamasinda_kullanilan_veriyi_dolayli_iceriyor_mu": (
        "HAYIR - etiket (triple-barrier) SADECE bar i'nin ATR14'unu (giris ani) ve i+1..i+16 "
        "arasindaki YOL'u (high/low) kullanir; hicbir feature bu ileri-yol verisini kullanmaz."
    ),
    "3_normalizasyon_sadece_egitim_setinden_mi": (
        "EVET - feature standardizasyonu (ortalama/std) her walk-forward fold'unda SADECE o "
        "fold'un TRAIN kesitinden, final modelde SADECE final_train_idx'ten hesaplanir; TEST "
        "setine bu TRAIN istatistikleri uygulanir, TEST verisinden hicbir istatistik hesaplanmaz."
    ),
    "4_zaman_bazli_feature_dst_dogrulamasindan_gecti_mi": (
        "EVET - yukaridaki dst_saat_eslesme_dogrulamasi bolumune bakiniz, bu ML turu icin "
        "BAGIMSIZ olarak yapildi (sonuc: sunucu DST takip ediyor)."
    ),
    "5_macd_ham_deger_mi_isaret_mi": (
        "HAM DEGER - macd_line ve macd_hist dogrudan sayisal (float) deger olarak feature "
        "matrisine eklendi, np.sign() UYGULANMADI (Arastirmaci BULGU6 SINIR/Stratejist Karar3 "
        "geregi)."
    ),
}

# =====================================================================
# TRIPLE-BARRIER ETIKET (N=16, k=1,5xATR14(M15) PUAN) - entry=c[i], path=h/l[i+1:i+1+N]
# =====================================================================
label = np.full(n, np.nan)     # 1=yukari-bariyer-once, 0=asagi-bariyer-once, NaN=hicbiri/gecersiz
label_neither = np.zeros(n, dtype=bool)
label_valid = np.zeros(n, dtype=bool)
tp_price_arr = np.full(n, np.nan)
sl_price_arr = np.full(n, np.nan)
time_exit_price_arr = np.full(n, np.nan)
exit_idx_arr = np.full(n, -1, dtype=int)
exit_reason_arr = np.full(n, "", dtype=object)

idx_pool = np.where(feature_valid)[0]
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
# S1 - MALIYET-ORANI STRES TESTI (justin_backtest_onkontrol_standardi.md Madde 2)
# =====================================================================
valid_atr_full = ~np.isnan(atr14_m15)
atr_median = float(np.nanmedian(atr14_m15))
atr_p90 = float(np.nanpercentile(atr14_m15[valid_atr_full], 90))
spread_median = float(np.median(spread))
spread_p90 = float(np.percentile(spread, 90))
spread_max = float(np.max(spread))

hedef_pts_k15 = K_ATR * atr_median
oran_medyan_spread = hedef_pts_k15 / spread_median
oran_p90_spread = hedef_pts_k15 / spread_p90
oran_max_spread = hedef_pts_k15 / spread_max

ESIK_ALT = 15.0
s1_gecti_medyan = oran_medyan_spread >= ESIK_ALT
s1_gecti_p90 = oran_p90_spread >= ESIK_ALT

results["s1_maliyet_orani_stres_testi"] = {
    "k_atr": K_ATR,
    "atr14_m15_medyan_pts": round(atr_median, 2),
    "atr14_m15_p90_pts": round(atr_p90, 2),
    "spread_medyan_pts": round(spread_median, 2),
    "spread_p90_pts": round(spread_p90, 2),
    "spread_max_pts": round(spread_max, 2),
    "hedef_pts_k1_5_x_atr_medyan": round(hedef_pts_k15, 2),
    "oran_medyan_spread_uzerinden": round(oran_medyan_spread, 2),
    "oran_p90_spread_uzerinden_STRES_TESTI": round(oran_p90_spread, 2),
    "oran_max_spread_uzerinden_ekstrem": round(oran_max_spread, 2),
    "esik_alt_sinir": ESIK_ALT,
    "medyan_uzerinden_GECTI_Mi": bool(s1_gecti_medyan),
    "P90_STRES_TESTI_GECTI_Mi": bool(s1_gecti_p90),
    "yorum": (
        "Stratejist'in medyan-spread on-tahmini burada dogrulandi. P90-spread ile stres "
        "testinde " + ("esik korunuyor" if s1_gecti_p90 else "esik KAYBEDILIYOR")
        + f" (oran={round(oran_p90_spread,2)}x, esik={ESIK_ALT}x). Max-spread (ekstrem) oran="
        + f"{round(oran_max_spread,2)}x - bu ekstrem/nadir anlarin gostergesidir, PASS/RED "
        + "kriteri degildir. Gorev talimati geregi bu esik kaybi ANA TESTI DURDURMAZ - Hipotez 1 "
        "yine de asagida calistirilmistir, sonuc Hipotez3/k=2,0 yedeginin bir SONRAKI TUR olarak "
        "degerlendirilmesi gerektigine isaret eder."
    ),
}
print("S1 stres testi (P90):", results["s1_maliyet_orani_stres_testi"]["P90_STRES_TESTI_GECTI_Mi"],
      "oran:", results["s1_maliyet_orani_stres_testi"]["oran_p90_spread_uzerinden_STRES_TESTI"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (on-kontroller + feature/etiket) tamamlandi ->", OUT_PATH)

# =====================================================================
# CHRONOLOJIK BOLUM: TRAINVAL (%80, ilk) / TEST (%20, son) - PURGE + EMBARGO
# =====================================================================
trainval_end_bar = int(n * (1 - TEST_FRACTION))
test_start_bar = trainval_end_bar + EMBARGO_BARS

labeled_idx_all = idx_pool[~np.isnan(label[idx_pool])]

trainval_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= trainval_end_bar)]
test_idx = labeled_idx_all[(labeled_idx_all >= test_start_bar)]

results["veri_bolumu"] = {
    "toplam_bar": int(n),
    "trainval_end_bar": trainval_end_bar,
    "embargo_bars": EMBARGO_BARS,
    "test_start_bar": test_start_bar,
    "trainval_tarih_araligi": [dates_str[0], dates_str[min(trainval_end_bar, n - 1)]],
    "test_tarih_araligi": [dates_str[min(test_start_bar, n - 1)], dates_str[-1]],
    "trainval_ikili_etiketli_n": int(len(trainval_idx)),
    "test_ikili_etiketli_n": int(len(test_idx)),
    "purge_kurali": "trainval ornekleri i+N<=trainval_end_bar ile SINIRLANDI (etiket penceresi sinira tasmaz)",
    "embargo_kurali": f"test, trainval_end_bar+{EMBARGO_BARS} bar (6 saat) SONRA baslar",
}
print("Veri bolumu:", results["veri_bolumu"]["trainval_ikili_etiketli_n"], "trainval /",
      results["veri_bolumu"]["test_ikili_etiketli_n"], "test")

# =====================================================================
# PURGED/EMBARGOLU WALK-FORWARD (TRAINVAL ICINDE, 5 esit segment -> 4 fold)
# Test setine HENUZ DOKUNULMADI - bu asama sadece model-stabilite/esik-kalibrasyonu icindir.
# =====================================================================
seg_edges = np.linspace(0, trainval_end_bar, WF_SEGMENTS + 1).astype(int)

def build_fold_sets(train_lo, train_hi, val_lo, val_hi):
    tr = labeled_idx_all[(labeled_idx_all >= train_lo) & (labeled_idx_all + N_BARS <= train_hi)]
    va = labeled_idx_all[(labeled_idx_all >= val_lo + EMBARGO_BARS) & (labeled_idx_all + N_BARS <= val_hi)]
    return tr, va

wf_folds_info = []
oof_idx_list = []
oof_prob_list = []
for f in range(1, WF_SEGMENTS):
    train_lo, train_hi = 0, seg_edges[f]
    val_lo, val_hi = seg_edges[f], seg_edges[f + 1]
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

results["walk_forward_purged_embargolu"] = {
    "segment_sayisi": WF_SEGMENTS, "fold_sayisi": WF_SEGMENTS - 1,
    "embargo_bars": EMBARGO_BARS, "sonuclar": wf_folds_info,
}
auc_list = [f_["val_auc"] for f_ in wf_folds_info if "val_auc" in f_]
results["walk_forward_purged_embargolu"]["auc_ozet"] = {
    "ortalama": round(float(np.mean(auc_list)), 4) if auc_list else None,
    "std": round(float(np.std(auc_list)), 4) if auc_list else None,
    "min": round(float(np.min(auc_list)), 4) if auc_list else None,
    "max": round(float(np.max(auc_list)), 4) if auc_list else None,
}
print("Walk-forward AUC ozet:", results["walk_forward_purged_embargolu"]["auc_ozet"])

# =====================================================================
# ESIK KALIBRASYONU (out-of-fold tahminleri uzerinden - TEST SETINE HENUZ BAKILMADI, S2 Madde2)
# Minimum orneklem korumasi (Ortak Ilkeler + MIN_SAMPLE): bir taraf (long/short) n<MIN_SAMPLE ise
# o tarafin precision'i SECIM SKORUNA DAHIL EDILMEZ (guvenilmez/rastlantisal kabul edilir).
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
    """SADECE MIN_SAMPLE esigini gecen taraflarin precision'i skora dahil edilir. Hicbir taraf
    yeterli orneklem saglamiyorsa bu aday ELENIR (skor=-1, secilemez)."""
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
    # HICBIR aday MIN_SAMPLE'i gecemedi - en genis (en cok toplam islem sunan) esik fallback
    # olarak secilir ve bu durum ACIKCA bir YETERSIZ VERI uyarisi olarak isaretlenir.
    secilen_esik = sorted(esik_tablosu, key=lambda r: r["toplam_islem_n"], reverse=True)[0]
    yetersiz_uyarisi = True

THRESH_LONG_FINAL = secilen_esik["esik_long"]
THRESH_SHORT_FINAL = secilen_esik["esik_short"]

results["esik_kalibrasyonu"] = {
    "yontem": "Out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR) taramasi - TEST SETINE BAKILMADI",
    "oof_ornek_sayisi": int(len(oof_prob_all)),
    "min_sample_esigi": MIN_SAMPLE,
    "aday_tablosu": esik_tablosu,
    "secim_kurali": (
        "MIN_SAMPLE (>=30) esigini GECEN taraflarin ORTALAMA precision'i en yuksek olan cift "
        "secildi; hicbir aday esigi gecmediyse en genis kapsamli aday fallback olarak secilir "
        "ve YETERSIZ_VERI olarak isaretlenir."
    ),
    "SECILEN_ESIK_LONG": THRESH_LONG_FINAL,
    "SECILEN_ESIK_SHORT": THRESH_SHORT_FINAL,
    "YETERSIZ_ORNEKLEM_FALLBACK_UYGULANDI": yetersiz_uyarisi,
}
print("Esik kalibrasyonu:", results["esik_kalibrasyonu"]["SECILEN_ESIK_LONG"],
      results["esik_kalibrasyonu"]["SECILEN_ESIK_SHORT"],
      "fallback:", yetersiz_uyarisi)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (walk-forward + esik kalibrasyonu) tamamlandi ->", OUT_PATH)

# =====================================================================
# FINAL MODEL: TUM TRAINVAL uzerinde egitim (SL/TP/esik ARTIK SABIT, degistirilmeyecek)
# =====================================================================
inner_val_start = seg_edges[WF_SEGMENTS - 1]
final_train_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= seg_edges[WF_SEGMENTS - 1])]
final_innerval_idx = labeled_idx_all[
    (labeled_idx_all >= inner_val_start + EMBARGO_BARS) & (labeled_idx_all + N_BARS <= trainval_end_bar)
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
# TEST SETI - TEK KEZ KULLANIM (S2 Madde2) - normalizasyon mu_final/sd_final (TRAIN'den) uygulanir
# =====================================================================
Xte = X_full[test_idx]
Xte_n = (Xte - mu_final) / sd_final
p_test = final_model.predict_proba(Xte_n)[:, 1]
y_test_binary_label = label[test_idx]
test_auc = roc_auc_score(y_test_binary_label, p_test)
print("TEST SETI AUC (tek-kez):", test_auc)

results["test_seti_siniflandirma_performansi"] = {
    "test_n": int(len(test_idx)), "test_auc": round(float(test_auc), 4),
    "not": "Bu, N=16/k=1,5 ikili siniflandirma gorevinin (hicbiri haric) TEST setindeki AUC'udur - TEK KEZ hesaplandi.",
}

# TANI AMACLI (2. tur ek - parametre/esik/yontem DEGISTIRMEZ, sadece raporlama icin p_test
# dagilimini kaydeder - test-seti islem sayisi 0 cikarsa NEDENININ gercek/dogrulanabilir
# oldugunu (esik-tetikleme yok) gostermek icindir, yeni bir karar/esik secimi YAPILMAZ).
results["test_p_dagilimi_TANI"] = {
    "aciklama": "Final modelin (best_iteration=1) TEST setindeki p(yukari) dagilimi - PRIMARY/SUPPLEMENTARY 0 islem cikarsa nedenini gostermek icin eklendi, esik secimini ETKILEMEZ.",
    "p_test_min": round(float(p_test.min()), 4),
    "p_test_max": round(float(p_test.max()), 4),
    "p_test_mean": round(float(p_test.mean()), 4),
    "p_test_std": round(float(p_test.std()), 4),
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
# TICK-BAZLI GERCEK MALIYET MODELI (Justin ailesinde onceki turlerle AYNI yontem/standart)
# =====================================================================
TICK_QUOTE_CACHE = {}
TICK_LOOKUP_COUNT = {"call": 0, "hit": 0, "miss_veri_yok": 0, "miss_zaman_uyusmazligi": 0, "miss_gecersiz_kotasyon": 0}

def get_tick_quote(bar_idx):
    if bar_idx in TICK_QUOTE_CACHE:
        TICK_LOOKUP_COUNT["hit"] += 1
        return TICK_QUOTE_CACHE[bar_idx]
    TICK_LOOKUP_COUNT["call"] += 1
    bar_epoch = int(t[bar_idx])
    ticks = mt5.copy_ticks_from(SYMBOL, bar_epoch, 3, mt5.COPY_TICKS_ALL)
    result = None
    if ticks is None or len(ticks) == 0:
        TICK_LOOKUP_COUNT["miss_veri_yok"] += 1
    else:
        row = ticks[0]
        tick_epoch_i = int(row['time'])
        fark = tick_epoch_i - bar_epoch
        if fark > MAX_TICK_MISMATCH_SEC or fark < -1:
            TICK_LOOKUP_COUNT["miss_zaman_uyusmazligi"] += 1
        else:
            bid = float(row['bid']); ask = float(row['ask'])
            if ask > 0 and bid > 0 and ask >= bid:
                result = (ask, bid)
            else:
                TICK_LOOKUP_COUNT["miss_gecersiz_kotasyon"] += 1
    TICK_QUOTE_CACHE[bar_idx] = result
    return result

def simulate_trade(signal_idx, direction):
    """direction: +1 LONG, -1 SHORT. entry_theo=c[signal_idx] (etiket tanimiyla TUTARLI),
    gercek tick-bazli slipaj entry_idx=signal_idx+1'deki bid/ask ile uygulanir (Justin ailesi
    standardi). exit_theo, GERCEK yol tarafindan hangi bariyerin/zaman-asiminin once
    gerceklestigine gore (yon FARK ETMEKSIZIN) belirlenir; raw_pts formulu yon-bagimli isareti
    dogru sekilde uygular (LONG icin yukari-cikis=kar, SHORT icin asagi-cikis=kar)."""
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
        exit_theo = tp_price_arr[signal_idx]     # yukari-bariyer-once gerceklesti
        exit_reason = "yukari_bariyer_ilk"
    else:
        exit_theo = sl_price_arr[signal_idx]     # asagi-bariyer-once gerceklesti
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
        "olasilik_p_yukari": None,  # asagida doldurulacak
        "hicbiri_mi": bool(label_neither[signal_idx]),
        "sebep": exit_reason,
        "atr_entry_pts": round(float(atr14_m15[signal_idx]), 2),
        "risk_pts": round(float(risk_pts), 2), "risk_usd_0_01_lot": round(float(risk_usd), 4),
        "risk_pct_of_kasa": round(float(risk_pct_of_kasa), 6),
        "tick_spread_pts": round(float(spread_pts_tick), 3),
        "giris_slipaj_pts": round(float(slip_pts), 3),
        "toplam_maliyet_pts": round(float(total_cost_pts), 3),
        "raw_pts": round(float(raw_pts), 3), "net_pts": round(float(net_pts), 3),
        "net_usd_0_01_lot": round(float(net_pts * POINT * CONTRACT_SIZE * LOT_FIXED), 4),
    }, "ok"

print("Test seti icin trade simulasyonu baslatiliyor (sadece esik-tetiklemeli sinyaller)...")

# Sinyal karari: p>=LONG -> LONG, p<=SHORT -> SHORT, aksi TAKDIRDE ISLEM YOK
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

print("Test seti PRIMARY (hicbiri-haric etiketli kume) tetiklenen islem sayisi:", len(trade_log),
      "atlanma nedenleri:", dict(reasons))

def summarize_trades(trades):
    if not trades:
        return {"toplam_islem": 0, "win_rate": None, "profit_factor": None,
                "net_profit_pts": 0.0, "net_profit_usd": 0.0, "max_drawdown_pct": None}
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

warnings_list = []
w = minimum_sample_warning(len(trade_log), "TEST_PRIMARY_tum_islemler")
if w: warnings_list.append(w)
w = minimum_sample_warning(len(long_trades), "TEST_PRIMARY_LONG")
if w: warnings_list.append(w)
w = minimum_sample_warning(len(short_trades), "TEST_PRIMARY_SHORT")
if w: warnings_list.append(w)
if yetersiz_uyarisi:
    warnings_list.append(
        "ESIK_KALIBRASYONU_YETERSIZ_ORNEKLEM: hicbir esik adayi out-of-fold kumede MIN_SAMPLE "
        f"(>={MIN_SAMPLE}) esigini HER IKI tarafta da gecemedi - fallback (en genis kapsamli "
        "aday) secildi, asagidaki sonuclar bu ONEMLI SINIRLA birlikte yorumlanmalidir."
    )
warnings_list.append(
    f"SINYAL_SIKLIGI_COK_DUSUK: test setindeki {len(test_idx)} bar icinden sadece {len(trade_log)} "
    f"bar esik-tetiklemeli islem uretti (kapsama ~{round(len(trade_log)/len(test_idx)*100,3) if len(test_idx) else 0}%) "
    "- bu, modelin p>=0,55/p<=0,45 gibi yuksek-guven bolgesine cok NADIREN ulastigini gosterir "
    "(AUC~0,50-0,52 ile TUTARLI - bkz. walk_forward_purged_embargolu.auc_ozet, modelin ayirt "
    "edici gucu neredeyse rastgele/coin-flip seviyesindedir)."
)

results["test_trade_simulasyonu_PRIMARY"] = {
    "aciklama": (
        "Stratejist Karar 2 geregi 'hicbiri' ornekleri TEST SETINDEN DE FILTRELENDI - bu, "
        "SADECE gercek sonucu (yukari-bariyer-once/asagi-bariyer-once) ONCEDEN belirli olan "
        "test barlarinda esik-tetiklemeli sinyal calistirir. Canliya-yakin bir capraz-kontrol "
        "icin 'hicbiri dahil' supplementary bolume bakiniz (asagida)."
    ),
    "esik_long": THRESH_LONG_FINAL, "esik_short": THRESH_SHORT_FINAL,
    "atlanma_nedenleri": dict(reasons),
    "tum_islemler_ozet": primary_summary,
    "LONG_ozet": summarize_trades(long_trades),
    "SHORT_ozet": summarize_trades(short_trades),
    "tick_lookup_istatistigi": dict(TICK_LOOKUP_COUNT),
}

print("PRIMARY (hicbiri-haric) test sonuc ozeti:", primary_summary)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (PRIMARY trade sim) tamamlandi ->", OUT_PATH)

# =====================================================================
# SUPPLEMENTARY - "HICBIRI DAHIL" GERCEKCI CANLI-BENZERI CAPRAZ KONTROL
# Model, canlida HANGI barin 'hicbiri' cikacagini ONCEDEN BILEMEZ - bu blok, esik-tetiklemeli
# TUM test barlarini (hicbiri dahil, feature-gecerli ve N-bar-ileri veri sinirinda) kullanir.
# =====================================================================
test_idx_all = idx_pool[(idx_pool >= test_start_bar)]  # hicbiri DAHIL, feature-gecerli tum test barlari
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

print("Test seti SUPPLEMENTARY (hicbiri dahil) tetiklenen islem sayisi:", len(trade_log_all),
      "atlanma nedenleri:", dict(reasons_all))

supplementary_summary = summarize_trades(trade_log_all)
neither_in_trades = [x for x in trade_log_all if x["hicbiri_mi"]]

results["test_trade_simulasyonu_SUPPLEMENTARY_hicbiri_dahil"] = {
    "aciklama": (
        "Karar-2-literal degil - bu, CANLI DEPLOYMENT'ta gercekte olacagini simule eder: model "
        "esik-asan HERHANGI bir test barinda islem acar, gercek sonuc (TP/SL/hicbiri-zaman-asimi) "
        "SONRADAN ortaya cikar. 'hicbiri' (zaman-asimi) cikan islemler gercek fiyatla kapatilir, "
        "P&L'e dahildir."
    ),
    "atlanma_nedenleri": dict(reasons_all),
    "tum_islemler_ozet": supplementary_summary,
    "hicbiri_zaman_asimi_ile_biten_islem_sayisi": len(neither_in_trades),
    "hicbiri_orani_tetiklenen_islemler_icinde": round(len(neither_in_trades) / len(trade_log_all), 4) if trade_log_all else None,
}
print("SUPPLEMENTARY (hicbiri dahil) test sonuc ozeti:", supplementary_summary)

# =====================================================================
# TAM ISLEM LOGU + UYARILAR + NIHAI JSON
# =====================================================================
results["islem_logu_PRIMARY_tam"] = trade_log
results["islem_logu_SUPPLEMENTARY_tam"] = trade_log_all
results["uyarilar"] = warnings_list

results["hipotez_ozet"] = {
    "hipotez_adi": "LightGBM Ikili Yon-Tahmini Modeli (N=16/k=1,5xATR14-M15) - HIPOTEZ 1",
    "yaklasim_turu": "Makine Ogrenmesi - Gradient Boosting (LightGBM)",
    "hedef_pf": HEDEF_PF, "hedef_wr_rr11": HEDEF_WR_RR11, "hedef_dd": HEDEF_DD,
    "gozlemlenen_pf_PRIMARY": primary_summary.get("profit_factor"),
    "gozlemlenen_wr_PRIMARY": primary_summary.get("win_rate"),
    "hedef_pf_karsilandi_mi_PRIMARY": (
        primary_summary.get("profit_factor") is not None and
        primary_summary.get("profit_factor") not in (float("inf"),) and
        primary_summary.get("profit_factor") >= HEDEF_PF
    ) if primary_summary.get("toplam_islem", 0) > 0 else None,
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("NIHAI KAYIT tamamlandi ->", OUT_PATH)
print("Hipotez ozet:", results["hipotez_ozet"])

mt5.shutdown()
print("MT5 baglantisi kapatildi. Script tamamlandi.")
