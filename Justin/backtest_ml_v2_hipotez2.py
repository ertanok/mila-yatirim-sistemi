# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - ML/Feature-Tabanli Aile v2 (ML Tam Tur 2) - HIPOTEZ 2
LightGBM MULTICLASS (3-sinif, deadzone) yon-tahmini modeli - ETIKET-IZOLE, Hipotez 1 (v2) ile
PARALEL calisir (Stratejist Karar 2: feature seti Hipotez 1 ile BIREBIR AYNI - Grup B eklenmis -
SADECE etiket semasi degisir: ikili barrier-touch yerine 3-sinifli sabit-ufuk deadzone).

Girdi: stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md (Karar 1-5, HIPOTEZ 2)
Cerceve: justin_gecmis_calisma.md, justin_ml_anti_overfitting_protokolu.md (S2),
         justin_backtest_onkontrol_standardi.md (S1 + DST + SL/TP-ozel)
Yapi referansi (kopyalama degil, ayni egitim/test/embargo/tick-maliyet iskeletinin yeniden
kullanimi - Justin'in KENDI onceki turleri, izolasyon disi, MilaGold DEGIL):
         backtest_ml_v1_hipotez1.py, backtest_ml_v1_hipotez2.py,
         research_ml_gold_scalping_m15_v2.py (Grup B / etiket-alternatifleri olcum mantigi)

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Veri dogrudan MT5'ten (MetaTrader5 kutuphanesi), GOLD sembolu M15 OHLCV+tick_volume+spread.
Kutuphane on-kosulu: pandas/lightgbm/scikit-learn Hipotez 1 (v2) ile PAYLASILIR - versiyon
teyidi asagida yapilir, ayri kurulum GEREKMEDI (Orkestrator gorev talimati Madde 1).

*** IKI FARKLI k - KOD DUZEYINDE AYRI DEGISKENLER (Stratejist'in ozel uyarisi, Karar 2) ***
  - K_LABEL_ATR_MULT : SADECE 3-sinifli egitim etiketini (yukari/asagi/notr) belirlemek icindir.
  - K_RISK_ATR_MULT  : GERCEK SL/TP mesafesidir (Hipotez 1 ile AYNI, 1,5xATR14) - pozisyon
    acildiginda risk yonetimi HER ZAMAN bununla yapilir, k_label'dan TAMAMEN BAGIMSIZDIR.
Bu iki degisken hicbir yerde ayni isimle/degerle karistirilmamistir - asagidaki kod boyunca
degisken adlari bu ayrimi acikca yansitir.
"""
import json
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
import MetaTrader5 as mt5
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import lightgbm as lgb
import sklearn
from sklearn.metrics import log_loss, confusion_matrix, accuracy_score

# =====================================================================
# SABITLER
# =====================================================================
SYMBOL = "GOLD"
N_BARS = 16                     # zaman-bariyeri/sabit-ufuk, 4 saat (Stratejist Karar 3, KESIN - Hipotez 1 ile AYNI)
K_RISK_ATR_MULT = 1.5           # GERCEK SL/TP mesafesi (Stratejist Karar 2/3, Hipotez 1 ile AYNI) - k_label'dan BAGIMSIZ
K_LABEL_ATR_MULT_BASLANGIC = 0.3  # SADECE 3-sinif egitim etiketi/deadzone esigi - BASLANGIC noktasi (BULGU10'dan devralinan oran)
K_LABEL_SEARCH_GRID = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]  # S2 Madde4: egitimden ONCE, TEST'e bakmadan ayarlanabilir aralik
NOTR_ORANI_UST_SINIR = 0.40     # bu sinirin USTUNDE "cok dengesiz" kabul edilir (Stratejist gorev talimati)
NOTR_ORANI_ALT_SINIR = 0.05     # bu sinirin ALTINDA "cok dengesiz" kabul edilir
ATR_PERIOD = 14
TRAIL_WINDOW = 100              # ATR/hacim rejim trailing-medyan penceresi
EMBARGO_BARS = 24               # 6 saat (S2 Madde1 onerisi), M15-bar
TEST_FRACTION = 0.20            # kronolojik son %20 -> rezerve TEST seti (TEK KEZ kullanim)
WF_SEGMENTS = 5                 # TRAINVAL walk-forward icin esit-uzunluklu segment sayisi (4 fold uretir)
RANDOM_SEED = 42
N_BARS_FETCH = 99999
MIN_SAMPLE = 30                 # minimum orneklem esigi
ROLL20_GUN = 20                 # 20-gunluk rolling S/R penceresi (Grup B, Arastirmaci BULGU5 ile AYNI)
NUM_CLASS = 3                   # 0=asagi, 1=notr, 2=yukari

# justin_gecmis_calisma.md sabitleri
KASA_USD = 2000.0
RISK_PCT_CAP = 0.01
LOT_FIXED = 0.01
HEDEF_PF = 1.5
HEDEF_WR_RR11 = 0.60
HEDEF_DD = 0.20

MAX_TICK_MISMATCH_SEC = 60

# Esik kalibrasyonu adaylari (Stratejist'in baslangic onerisi: P_yukari>=0,45, simetrik P_asagi>=0,45)
THRESH_YUKARI_CANDIDATES = [0.40, 0.45, 0.50, 0.55]
THRESH_ASAGI_CANDIDATES = [0.40, 0.45, 0.50, 0.55]

# LightGBM MULTICLASS - dar hiperparametre araligi (S2: multiclass'a gecisin kendisi karmasiklik
# artisi oldugu icin arama AYRICA genisletilmedi - Hipotez 1 (v2) ile AYNI karmasiklik duzeyi)
LGB_PARAMS = dict(
    objective="multiclass",
    num_class=NUM_CLASS,
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

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_ml_v2_hipotez2_output.json"

results = {}
results["kutuphane_versiyon_teyidi"] = {
    "pandas": pd.__version__, "lightgbm": lgb.__version__, "scikit_learn": sklearn.__version__,
    "not": "Hipotez 1 (v2) ile PAYLASILAN kurulum - Orkestrator Madde 1 geregi ayri kurulum yapilmadi, sadece versiyon teyidi.",
}
print("Kutuphane versiyonlari:", results["kutuphane_versiyon_teyidi"])

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
# DST / SAAT-ESLESME DOGRULAMASI
# Gorev talimati: "Hipotez 1 (v2)'nin DST sonucu DEVRALINABILIR (ayni ML/v2 ailesi ici paylasim)".
# BU RUN ANINDA Hipotez 1 (v2) paralel gorevi HENUZ TAMAMLANMAMISTI (dosya sisteminde ciktisi
# yoktu) - bu yuzden "devralindi" diye KOPYALAMA YAPILMADI, feature-uretim kodu (hour/session/dow
# bloklari) v1/Hipotez1 (M15 ML ailesinin ilk turu) ile BIREBIR AYNI oldugu icin BAGIMSIZ olarak
# BURADA YENIDEN calistirildi (ucretsiz/hizli bir kontrol, atlanmadi). Sonuc, ayni mekanizma/veri
# kullanildigi icin paralel Hipotez 1 (v2) turunde de AYNI cikmasi BEKLENIR - bu, Backtest
# Muhendisi'nin kendi bagimsiz teyididir, varsayimsal bir devralma DEGILDIR.
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
    "durum": "BU_TURDE_BAGIMSIZ_YENIDEN_CALISTIRILDI_HIPOTEZ1_V2_CIKTISI_RUN_ANINDA_MEVCUT_DEGILDI",
    "gerekce": (
        "Gorev talimati Hipotez 1 (v2)'den devralmaya izin veriyordu (ayni ML/v2 ailesi, ayni "
        "feature-uretim kodu) - ancak bu calisma anında Hipotez 1 (v2)'nin ciktisi dosya "
        "sisteminde YOKTU (paralel calisiyor). Kopyalama yerine, AYNI kod (hour_sin/cos, "
        "session_asia/london/ny, dow bloklari, v1/Hipotez1 ML ailesiyle BIREBIR AYNI) burada "
        "BAGIMSIZ yeniden calistirildi - ek maliyeti ihmal edilebilir duzeydedir."
    ),
    "canli_capraz_kontrol": {
        "sistem_saati_utc": now_system.isoformat(),
        "son_tick_epoch_utc": tick_epoch.isoformat(),
        "fark_saniye": round(fark_sn, 2),
    },
    "dst_gecis_taramasi": dst_scan,
    "degerlendirilen_gecis_sayisi": degerlendirilen_sayisi,
    "1_saat_kayma_gozlenen_gecis_sayisi": kayma_sayisi,
    "SONUC": (
        (f"{kayma_sayisi}/{degerlendirilen_sayisi} bilinen DST gecisinde piyasa-acilis saati "
         "1 SAAT KAYDI - MT5 sunucusu DST'yi TAKIP EDIYOR (sabit GMT+3 DEGIL). v1/Hipotez1(v2) "
         "ile TUTARLI sonuc.")
        if kayma_sayisi == degerlendirilen_sayisi and degerlendirilen_sayisi > 0 else
        (f"{kayma_sayisi}/{degerlendirilen_sayisi} gecis kaydi gosterdi - KARISIK/BELIRSIZ sonuc.")
    ),
}
print("DST/saat-eslesme (bagimsiz yeniden-calistirma):", results["dst_saat_eslesme_dogrulamasi"]["SONUC"])

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

def true_range_points(hh, ll, cc, point):
    nn = len(cc)
    tr = np.empty(nn)
    tr[0] = hh[0] - ll[0]
    tr[1:] = np.maximum(np.maximum(hh[1:] - ll[1:], np.abs(hh[1:] - cc[:-1])), np.abs(ll[1:] - cc[:-1]))
    return tr / point

def compute_atr_points_simple(hh, ll, cc, period, point):
    """BASIT (Wilder DEGIL) rolling-ortalama ATR, puan biriminde. Grup1 feature'i VE k_risk (SL/TP)
    icin kullanilir - v1/Hipotez1(v2) ile BIREBIR AYNI mekanizma (compute_atr_points fonksiyonunun
    aynisi, isim degistirildi - 'simple' ekinin nedeni asagidaki wilder varyantindan AYIRT ETMEK)."""
    tr_pts = true_range_points(hh, ll, cc, point)
    return rolling_mean_causal(tr_pts, period)

def compute_atr_points_wilder(hh, ll, cc, period, point):
    """WILDER-SMOOTHED ATR, puan biriminde - SADECE k_label (3-sinif deadzone esigi) icin kullanilir.
    ONEMLI TUTARSIZLIK NOTU (rapor Bolum 'k_label Yeniden-Hesaplama'da tekrar aciklanir): Stratejist
    notu 'Wilder-smoothed, v1/Tur1 ile TUTARLI olmasi icin' diyor, ANCAK v1/Hipotez1(v1/v2)'nin FIILI
    kodu (compute_atr_points_simple/compute_atr_points) BASIT rolling-ortalama kullanir, Wilder
    DEGIL - bu script bu tutarsizligi SESSIZCE COZMEDI: k_risk (SL/TP) icin Hipotez1 ile birebir
    ayni SL/TP mesafesini uretmesi ZORUNLU oldugundan BASIT ATR (compute_atr_points_simple)
    kullanilmaya devam edildi; k_label icin ise Stratejist'in acik/yazili talimati (Wilder) harfiyen
    uygulandi - iki ayri ATR degiskeni (atr14_m15_simple, atr14_m15_wilder) KOD DUZEYINDE AYRI
    tutuldu, hicbir yerde birbirinin yerine KULLANILMADI."""
    tr_pts = true_range_points(hh, ll, cc, point)
    nn = len(tr_pts)
    out = np.full(nn, np.nan)
    if nn < period:
        return out
    out[period - 1] = np.mean(tr_pts[:period])
    for i in range(period, nn):
        out[i] = (out[i - 1] * (period - 1) + tr_pts[i]) / period
    return out

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
# GRUP 1 - VOLATILITE: ATR14(M15, puan, BASIT), rejim orani, ATR14(H1, puan)
# =====================================================================
atr14_m15_simple = compute_atr_points_simple(h, l, c, ATR_PERIOD, POINT)
atr14_m15_wilder = compute_atr_points_wilder(h, l, c, ATR_PERIOD, POINT)  # SADECE k_label icin
atr_trail_med = rolling_median_causal(np.nan_to_num(atr14_m15_simple, nan=0.0), TRAIL_WINDOW)
atr_regime_ratio = np.full(n, np.nan)
valid_atr_regime = ~np.isnan(atr14_m15_simple) & ~np.isnan(atr_trail_med) & (atr_trail_med > 0)
atr_regime_ratio[valid_atr_regime] = atr14_m15_simple[valid_atr_regime] / atr_trail_med[valid_atr_regime]

h1_t, h1_o, h1_h, h1_l, h1_c, h1_v = resample_ohlc(t, o, h, l, c, vol, 3600)
h4_t, h4_o, h4_h, h4_l, h4_c, h4_v = resample_ohlc(t, o, h, l, c, vol, 14400)
atr14_h1 = compute_atr_points_simple(h1_h, h1_l, h1_c, ATR_PERIOD, POINT)

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
macd_hist = macd_line - macd_signal  # HAM DEGER - isaret DEGIL (BULGU6 SINIR/Karar3 geregi, v1 ile AYNI)

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
# GRUP B (YENI, ZORUNLU, Stratejist Karar 1) - GORECE FIYAT YAPISI/PIVOT-S-R
# Tumu NEDENSEL: gunluk/haftalik pivot ONCEKI TAMAMLANMIS gun/haftadan shift(1) ile turetilir;
# 20-gunluk rolling-high/low SADECE t-oncesi 20 TAMAMLANMIS gunu kullanir (shift(1) sonrasi).
# Yontem research_ml_gold_scalping_m15_v2.py Bolum 2 ile AYNI (Justin'in kendi Arastirmaci
# ciktisi - izolasyon disi), burada dogrudan M15 feature matrisine entegre edildi.
# =====================================================================
df_b = pd.DataFrame({"time": t, "high": h, "low": l, "close": c})
df_b["dt"] = pd.to_datetime(df_b["time"], unit="s")
df_b["date"] = df_b["dt"].dt.date

daily = df_b.groupby("date").agg(d_high=("high", "max"), d_low=("low", "min"), d_close=("close", "last")).reset_index()
daily["pivot"] = (daily["d_high"] + daily["d_low"] + daily["d_close"]) / 3.0
daily["pivot_for_next_day"] = daily["pivot"].shift(1)          # ONCEKI gunun pivotu BUGUNE atanir
daily["roll20_high"] = daily["d_high"].rolling(ROLL20_GUN).max().shift(1)
daily["roll20_low"] = daily["d_low"].rolling(ROLL20_GUN).min().shift(1)
date_map = daily.set_index("date")[["pivot_for_next_day", "roll20_high", "roll20_low"]]
df_b = df_b.merge(date_map, left_on="date", right_index=True, how="left")

df_b["iso_year"] = df_b["dt"].dt.isocalendar().year
df_b["iso_week"] = df_b["dt"].dt.isocalendar().week
weekly = df_b.groupby(["iso_year", "iso_week"]).agg(
    w_high=("high", "max"), w_low=("low", "min"), w_close=("close", "last")).reset_index()
weekly = weekly.sort_values(["iso_year", "iso_week"]).reset_index(drop=True)
weekly["w_pivot"] = (weekly["w_high"] + weekly["w_low"] + weekly["w_close"]) / 3.0
weekly["w_pivot_for_next_week"] = weekly["w_pivot"].shift(1)   # ONCEKI haftanin pivotu BU HAFTAYA
wk_map = weekly.set_index(["iso_year", "iso_week"])[["w_pivot_for_next_week"]]
df_b = df_b.merge(wk_map, left_on=["iso_year", "iso_week"], right_index=True, how="left")

assert len(df_b) == n, "Grup B merge sonrasi bar sayisi degisti - beklenmeyen cogaltma/kayip"

dist_daily_pivot_pts = (c - df_b["pivot_for_next_day"].to_numpy(float)) / POINT
dist_weekly_pivot_pts = (c - df_b["w_pivot_for_next_week"].to_numpy(float)) / POINT
dist_roll20_high_pts = (df_b["roll20_high"].to_numpy(float) - c) / POINT
dist_roll20_low_pts = (c - df_b["roll20_low"].to_numpy(float)) / POINT
print("Grup B (pivot/S-R, YENI) hazir.")

# =====================================================================
# FEATURE MATRISI (Stratejist Karar 1: Grup 1-5 + Grup B ZORUNLU, ~22-28 sutun -> burada 27)
# =====================================================================
feature_names = [
    "atr14_m15", "atr_regime_ratio", "atr14_h1_aligned",                          # Grup 1 (3)
    "m15_trend", "h1_trend_aligned", "h4_trend_aligned", "confluence_flag",       # Grup 2 (4)
    "tick_volume", "vol_ratio_trail100", "vol_slope_8bar",                       # Grup 3 (3)
    "hour_sin", "hour_cos", "dow", "session_asia", "session_london", "session_ny",  # Grup 4 (6)
    "lag_ret_1", "lag_ret_4", "lag_ret_8", "rsi14", "macd_line", "macd_hist", "directional_streak",  # Grup 5 (7)
    "dist_daily_pivot_pts", "dist_weekly_pivot_pts", "dist_roll20_high_pts", "dist_roll20_low_pts",  # Grup B (4, YENI)
]
X_full = np.column_stack([
    atr14_m15_simple, atr_regime_ratio, atr14_h1_aligned,
    m15_trend, m15_h1_trend_aligned, m15_h4_trend_aligned, confluence_flag,
    vol, vol_ratio, vol_slope,
    hour_sin, hour_cos, dow_feature, session_asia, session_london, session_ny,
    lag_ret_1, lag_ret_4, lag_ret_8, rsi14, macd_line, macd_hist, directional_streak,
    dist_daily_pivot_pts, dist_weekly_pivot_pts, dist_roll20_high_pts, dist_roll20_low_pts,
])
assert X_full.shape[1] == len(feature_names)
results["feature_seti"] = {
    "sutun_sayisi": len(feature_names), "sutunlar": feature_names,
    "not": "Grup 1-5 v1/Hipotez1(v2) ile BIREBIR AYNI (23 sutun); Grup B (4 sutun, YENI) Stratejist Karar 1 geregi eklendi. Toplam 27 - Stratejist'in ~22-28 tahmin araligi icinde.",
}
print("Feature matrisi hazir. Sutun sayisi:", len(feature_names))

feature_valid = ~np.isnan(X_full).any(axis=1)
print("Feature-gecerli bar sayisi:", int(feature_valid.sum()), "/", n)

# =====================================================================
# FEATURE-SIZINTI KONTROL LISTESI (S2 Madde 3) - Grup B icin OZEL teyit dahil
# =====================================================================
results["feature_sizinti_kontrol_listesi"] = {
    "1_ileri_bakan_bilgi_var_mi": (
        "HAYIR - Grup 1-5 tum feature'lar rolling_mean_causal/rolling_median_causal/ema_causal ile "
        "SADECE bar i ve ONCESI veriyi kullanir; H1/H4 trend/ATR eslemesi bar i'den ONCE KAPANMIS "
        "son H1/H4 barini kullanir (h1_idx-1/h4_idx-1 indeksleme)."
    ),
    "2_label_hesaplamasinda_kullanilan_veriyi_dolayli_iceriyor_mu": (
        "HAYIR - k_label (3-sinif deadzone) SADECE bar i'nin Wilder-ATR14'unu (giris ani) ve "
        "i+16'daki KAPANIS fiyatini kullanir; k_risk (SL/TP barrier) SADECE bar i'nin basit-ATR14'unu "
        "ve i+1..i+16 arasindaki YOL'u (high/low) kullanir. Hicbir feature bu ileri-yol/ileri-kapanis "
        "verisini KULLANMAZ."
    ),
    "3_normalizasyon_sadece_egitim_setinden_mi": (
        "EVET - feature standardizasyonu (ortalama/std) her walk-forward fold'unda SADECE o "
        "fold'un TRAIN kesitinden, final modelde SADECE final_train_idx'ten hesaplanir; TEST "
        "setine bu TRAIN istatistikleri uygulanir."
    ),
    "4_zaman_bazli_feature_dst_dogrulamasindan_gecti_mi": (
        "EVET - yukaridaki dst_saat_eslesme_dogrulamasi bolumune bakiniz (bu turde BAGIMSIZ "
        "yeniden calistirildi, Hipotez1(v2) ciktisi run aninda mevcut degildi)."
    ),
    "5_macd_ham_deger_mi_isaret_mi": (
        "HAM DEGER - macd_line ve macd_hist dogrudan sayisal (float) deger olarak feature "
        "matrisine eklendi, np.sign() UYGULANMADI."
    ),
    "6_GRUP_B_gunluk_haftalik_pivot_onceki_tamamlanmis_periyottan_mi": (
        "EVET - daily/weekly gruplarinda pivot degeri .shift(1) ile bir SONRAKI gune/haftaya "
        "atanir (bkz. 'pivot_for_next_day'/'w_pivot_for_next_week' kolonlari); bugunun/bu haftanin "
        "KENDI (henuz tamamlanmamis) OHLC'si ASLA kullanilmaz."
    ),
    "7_GRUP_B_roll20_high_low_ileri_bakis_icermiyor_mu": (
        "EVET - roll20_high/low, GUNLUK d_high/d_low serisi uzerinde .rolling(20).shift(1) ile "
        "hesaplanir; bu, bugunden ONCEKI 20 TAMAMLANMIS gunu kullanir, bugunku/gelecekteki hicbir "
        "gunu icermez. Merge sonrasi bar sayisinin degismedigi (assert len(df_b)==n) ayrica "
        "dogrulandi (cogaltma/kayip riskine karsi)."
    ),
}
print("Feature-sizinti kontrol listesi teyit edildi (Grup B dahil).")

# =====================================================================
# K_LABEL YENIDEN-HESAPLAMA (N=16) - Stratejist Karar 2/gorev talimati Madde 4, KRITIK
# N=8 (BULGU10, %43,9/%40,5/%15,6) ile BIREBIR KARSILASTIRMA YAPILMAZ - bu bir YENIDEN-OLCUMdur.
# Dagilim SADECE TRAINVAL (chronolojik ilk (1-TEST_FRACTION)) kesitinde olculur - TEST SETINE
# bu asamada KESINLIKLE BAKILMAZ (S2 Madde 2/4 - k_label egitimden ONCE, test'e bakmadan sabitlenir).
# =====================================================================
fwd_signed_ret_pts = np.full(n, np.nan)
fwd_signed_ret_pts[:-N_BARS] = (c[N_BARS:] - c[:-N_BARS]) / POINT

trainval_end_bar_probe = int(n * (1 - TEST_FRACTION))  # k_label aramasi icin ON-TAHMINI sinir (asagida resmi olarak da kullanilacak)

def label3_for_k(k_label):
    th = k_label * atr14_m15_wilder
    lab = np.where(fwd_signed_ret_pts > th, 1, np.where(fwd_signed_ret_pts < -th, -1, 0)).astype(float)
    valid = ~np.isnan(fwd_signed_ret_pts) & ~np.isnan(atr14_m15_wilder) & feature_valid
    lab[~valid] = np.nan
    return lab, valid

def trainval_dagilim(k_label):
    lab, valid = label3_for_k(k_label)
    mask = valid & (np.arange(n) < trainval_end_bar_probe)
    vals = lab[mask]
    tot = len(vals)
    if tot == 0:
        return None
    up = int(np.sum(vals == 1)); down = int(np.sum(vals == -1)); neu = int(np.sum(vals == 0))
    return {"k_label": k_label, "n": tot,
            "yukari_oran": round(up / tot, 4), "asagi_oran": round(down / tot, 4), "notr_oran": round(neu / tot, 4)}

baseline_stats = trainval_dagilim(K_LABEL_ATR_MULT_BASLANGIC)
print("K_LABEL baslangic (0,3xATR14-Wilder, N=16) TRAINVAL dagilimi:", baseline_stats)

k_label_arama_tablosu = [baseline_stats]
dengesiz_mi = (baseline_stats["notr_oran"] > NOTR_ORANI_UST_SINIR) or (baseline_stats["notr_oran"] < NOTR_ORANI_ALT_SINIR)

if dengesiz_mi:
    for k_cand in K_LABEL_SEARCH_GRID:
        if k_cand == K_LABEL_ATR_MULT_BASLANGIC:
            continue
        stat = trainval_dagilim(k_cand)
        if stat is not None:
            k_label_arama_tablosu.append(stat)
    # dengeli araligin (notr [0,05;0,40]) icindeki adaylar arasindan baslangica EN YAKIN olani sec
    dengeli_adaylar = [s for s in k_label_arama_tablosu if NOTR_ORANI_ALT_SINIR <= s["notr_oran"] <= NOTR_ORANI_UST_SINIR]
    if dengeli_adaylar:
        secilen = sorted(dengeli_adaylar, key=lambda s: abs(s["k_label"] - K_LABEL_ATR_MULT_BASLANGIC))[0]
    else:
        # HICBIR aday dengeli araliga girmedi - notr oranina EN YAKIN (0,225, aralik ortasi) olani fallback sec
        secilen = sorted(k_label_arama_tablosu, key=lambda s: abs(s["notr_oran"] - 0.225))[0]
    K_LABEL_ATR_MULT_FINAL = secilen["k_label"]
else:
    K_LABEL_ATR_MULT_FINAL = K_LABEL_ATR_MULT_BASLANGIC
    secilen = baseline_stats

results["k_label_yeniden_hesaplama"] = {
    "aciklama": (
        "N=8 (BULGU10, %43,9/%40,5/%15,6) ile BIREBIR KARSILASTIRMA YAPILMADI - bu N=16 icin "
        "YENIDEN-OLCUMdur (Stratejist Karar 2/gorev talimati Madde 4 geregi). Dagilim SADECE "
        "TRAINVAL kesitinde (test setine BAKILMADAN) olculdu."
    ),
    "wilder_smoothed_atr_kullanildi": True,
    "k_label_baslangic": K_LABEL_ATR_MULT_BASLANGIC,
    "baslangic_trainval_dagilimi": baseline_stats,
    "notr_orani_ust_sinir": NOTR_ORANI_UST_SINIR, "notr_orani_alt_sinir": NOTR_ORANI_ALT_SINIR,
    "dengesiz_bulundu_mu": bool(dengesiz_mi),
    "arama_tablosu_TRAINVAL_SADECE": k_label_arama_tablosu,
    "K_LABEL_ATR_MULT_FINAL": K_LABEL_ATR_MULT_FINAL,
    "final_secim_gerekcesi": (
        "Baslangic (0,3) zaten dengeli araliktaydi (notr [0,05;0,40] icinde), degistirilmedi."
        if not dengesiz_mi else
        f"Baslangic dengesizdi, TRAINVAL-only arama ile k_label={K_LABEL_ATR_MULT_FINAL} secildi (test setine bakilmadan, S2 Madde4)."
    ),
    "ATR_TUTARSIZLIGI_NOTU": (
        "Stratejist notu 'Wilder-smoothed (v1/Tur1 ile TUTARLI)' diyordu, ANCAK v1/Hipotez1'in "
        "fiili kodu (compute_atr_points/rolling_mean_causal) BASIT rolling-ortalama kullanir, "
        "Wilder DEGIL - bu olasi bir terminoloji karisikligidir, Backtest Muhendisi SESSIZCE "
        "COZMEDI: k_risk icin BASIT ATR (Hipotez1 ile birebir ayni SL/TP uretmesi ZORUNLU oldugu "
        "icin), k_label icin Stratejist'in YAZILI talimati geregi WILDER ATR kullanildi - iki "
        "degisken (atr14_m15_simple, atr14_m15_wilder) KOD DUZEYINDE AYRI, hicbir yerde "
        "birbirinin yerine KULLANILMADI. Bu tutarsizlik Risk Analisti'ne ACIKCA bildirilmelidir."
    ),
}
print("K_LABEL_ATR_MULT_FINAL:", K_LABEL_ATR_MULT_FINAL, "gerekce:", results["k_label_yeniden_hesaplama"]["final_secim_gerekcesi"])

# Final 3-sinif etiket (tum veri, sabitlenen K_LABEL_ATR_MULT_FINAL ile) - egitim/test icin TEK sema
label3, label3_valid = label3_for_k(K_LABEL_ATR_MULT_FINAL)
class_idx = np.where(np.isnan(label3), np.nan, label3 + 1.0)  # -1/0/1 -> 0/1/2 (asagi/notr/yukari)

tam_veri_dagilim = trainval_dagilim(K_LABEL_ATR_MULT_FINAL)  # sadece bilgi amacli, trainval kismi
full_valid_mask = label3_valid
full_up = int(np.sum(label3[full_valid_mask] == 1)); full_down = int(np.sum(label3[full_valid_mask] == -1))
full_neu = int(np.sum(label3[full_valid_mask] == 0)); full_tot = full_up + full_down + full_neu
results["k_label_final_dagilim_TUM_VERI_bilgi_amacli"] = {
    "n": full_tot, "yukari_oran": round(full_up / full_tot, 4) if full_tot else None,
    "asagi_oran": round(full_down / full_tot, 4) if full_tot else None,
    "notr_oran": round(full_neu / full_tot, 4) if full_tot else None,
    "not": "Bu TUM VERI (train+test) uzerindeki dagilimdir, SADECE bilgi/raporlama amaclidir - k_label SECIMI yukarida SADECE trainval kullanilarak yapildi.",
}
print("K_LABEL final - TUM VERI dagilimi (bilgi amacli):", results["k_label_final_dagilim_TUM_VERI_bilgi_amacli"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (feature + k_label) tamamlandi ->", OUT_PATH)

# =====================================================================
# K_RISK TRIPLE-BARRIER (SL/TP GERCEK POZISYON YONETIMI) - Hipotez 1 ile BIREBIR AYNI mekanizma
# BASIT atr14_m15_simple ve K_RISK_ATR_MULT=1,5 kullanir - k_label'DAN TAMAMEN BAGIMSIZ.
# =====================================================================
tp_price_arr = np.full(n, np.nan)
sl_price_arr = np.full(n, np.nan)
time_exit_price_arr = np.full(n, np.nan)
exit_idx_arr = np.full(n, -1, dtype=int)
exit_reason_arr = np.full(n, "", dtype=object)
label_neither = np.zeros(n, dtype=bool)   # barrier ANLAMINDA "hicbiri/zaman-asimi" (label3'un "notr"undan FARKLI kavram)
barrier_valid = np.zeros(n, dtype=bool)

idx_pool = np.where(feature_valid)[0]
idx_pool = idx_pool[idx_pool + N_BARS < n]
for i in idx_pool:
    atr_i = atr14_m15_simple[i]
    if np.isnan(atr_i) or atr_i <= 0:
        continue
    entry = c[i]
    tp_up = entry + K_RISK_ATR_MULT * atr_i * POINT
    sl_down = entry - K_RISK_ATR_MULT * atr_i * POINT
    path_h = h[i + 1:i + 1 + N_BARS]
    path_l = l[i + 1:i + 1 + N_BARS]
    hit_tp_idx = np.argmax(path_h >= tp_up) if np.any(path_h >= tp_up) else None
    hit_sl_idx = np.argmax(path_l <= sl_down) if np.any(path_l <= sl_down) else None
    tp_price_arr[i] = tp_up; sl_price_arr[i] = sl_down
    time_exit_price_arr[i] = c[i + N_BARS]
    barrier_valid[i] = True
    if hit_tp_idx is None and hit_sl_idx is None:
        label_neither[i] = True
        exit_idx_arr[i] = i + N_BARS
        exit_reason_arr[i] = "zaman_asimi"
    elif hit_tp_idx is None:
        exit_idx_arr[i] = i + 1 + hit_sl_idx
        exit_reason_arr[i] = "SL"
    elif hit_sl_idx is None:
        exit_idx_arr[i] = i + 1 + hit_tp_idx
        exit_reason_arr[i] = "TP"
    else:
        if hit_tp_idx <= hit_sl_idx:
            exit_idx_arr[i] = i + 1 + hit_tp_idx if hit_tp_idx < hit_sl_idx else i + 1 + hit_sl_idx
            exit_reason_arr[i] = "TP" if hit_tp_idx < hit_sl_idx else "SL(ayni-bar-oncelik)"
        else:
            exit_idx_arr[i] = i + 1 + hit_sl_idx
            exit_reason_arr[i] = "SL"

print("k_risk triple-barrier (SL/TP mekanigi) hesaplandi. Gecerli:", int(barrier_valid.sum()),
      "zaman_asimi:", int(label_neither.sum()))

# =====================================================================
# S1 - MALIYET-ORANI STRES TESTI - k_risk=1,5xATR14 Hipotez1 ile AYNI, model-secimden BAGIMSIZ.
# Gorev talimati geregi Hipotez1 raporundan DEVRALINABILIR - tutarlilik teyidi icin burada da
# (BASIT ATR ile, k_risk mekanizmasiyla AYNI birim) yeniden hesaplandi.
# =====================================================================
valid_atr_full = ~np.isnan(atr14_m15_simple)
atr_median = float(np.nanmedian(atr14_m15_simple))
atr_p90 = float(np.nanpercentile(atr14_m15_simple[valid_atr_full], 90))
spread_median = float(np.median(spread))
spread_p90 = float(np.percentile(spread, 90))
spread_max = float(np.max(spread))

hedef_pts_k_risk = K_RISK_ATR_MULT * atr_median
oran_medyan_spread = hedef_pts_k_risk / spread_median
oran_p90_spread = hedef_pts_k_risk / spread_p90
oran_max_spread = hedef_pts_k_risk / spread_max
ESIK_ALT = 15.0

results["s1_maliyet_orani_stres_testi"] = {
    "durum": "HIPOTEZ_1_ILE_AYNI_K_RISK_BARRIER_TASARIMI_-_DEVRALINABILIR_BU_TURDE_TUTARLILIK_TEYIDI_ICIN_YENIDEN_HESAPLANDI",
    "k_risk_atr_mult": K_RISK_ATR_MULT,
    "atr14_m15_simple_medyan_pts": round(atr_median, 2), "atr14_m15_simple_p90_pts": round(atr_p90, 2),
    "spread_medyan_pts": round(spread_median, 2), "spread_p90_pts": round(spread_p90, 2), "spread_max_pts": round(spread_max, 2),
    "hedef_pts_k_risk_x_atr_medyan": round(hedef_pts_k_risk, 2),
    "oran_medyan_spread_uzerinden": round(oran_medyan_spread, 2),
    "oran_p90_spread_uzerinden_STRES_TESTI": round(oran_p90_spread, 2),
    "oran_max_spread_uzerinden_ekstrem": round(oran_max_spread, 2),
    "esik_alt_sinir": ESIK_ALT,
    "medyan_uzerinden_GECTI_Mi": bool(oran_medyan_spread >= ESIK_ALT),
    "P90_STRES_TESTI_GECTI_Mi": bool(oran_p90_spread >= ESIK_ALT),
    "yorum": (
        "k_risk mekanizmasi (N=16/k=1,5) model mimarisinden/etiket semasindan BAGIMSIZ oldugu "
        "icin Hipotez1(v2) ile AYNI ATR/spread dagilimina dayanir - sonucun v1 Hipotez1 (medyan "
        "15,97x GECTI, P90 11,91x KAYBEDILDI) ile NITELIKSEL OLARAK tutarli olmasi BEKLENIR. "
        "Esik kaybi (varsa) ana testi durdurmaz, gorev talimati geregi Hipotez 2 asagida yine de "
        "calistirilmistir."
    ),
}
print("S1 stres testi (P90):", results["s1_maliyet_orani_stres_testi"]["P90_STRES_TESTI_GECTI_Mi"],
      "oran:", results["s1_maliyet_orani_stres_testi"]["oran_p90_spread_uzerinden_STRES_TESTI"])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (S1 + barrier) tamamlandi ->", OUT_PATH)

# =====================================================================
# CHRONOLOJIK BOLUM: TRAINVAL (%80,ilk) / TEST (%20,son) - PURGE+EMBARGO
# Egitim etiketi ARTIK class_idx (0/1/2) - barrier (exit_idx_arr vb.) SADECE gercek P&L simulasyonu icin.
# =====================================================================
trainval_end_bar = int(n * (1 - TEST_FRACTION))
test_start_bar = trainval_end_bar + EMBARGO_BARS
assert trainval_end_bar == trainval_end_bar_probe, "k_label arama sinirindaki trainval_end_bar_probe resmi sinirla uyusmali"

labeled_idx_all = idx_pool[~np.isnan(class_idx[idx_pool]) & barrier_valid[idx_pool]]

trainval_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= trainval_end_bar)]
test_idx = labeled_idx_all[(labeled_idx_all >= test_start_bar)]

results["veri_bolumu"] = {
    "toplam_bar": int(n), "trainval_end_bar": trainval_end_bar, "embargo_bars": EMBARGO_BARS,
    "test_start_bar": test_start_bar,
    "trainval_tarih_araligi": [dates_str[0], dates_str[min(trainval_end_bar, n - 1)]],
    "test_tarih_araligi": [dates_str[min(test_start_bar, n - 1)], dates_str[-1]],
    "trainval_n": int(len(trainval_idx)), "test_n": int(len(test_idx)),
    "purge_kurali": "trainval ornekleri i+N<=trainval_end_bar ile SINIRLANDI",
    "embargo_kurali": f"test, trainval_end_bar+{EMBARGO_BARS} bar (6 saat) SONRA baslar",
}
print("Veri bolumu:", results["veri_bolumu"]["trainval_n"], "trainval /", results["veri_bolumu"]["test_n"], "test")

if len(trainval_idx) < MIN_SAMPLE or len(test_idx) < MIN_SAMPLE:
    results["uyarilar_erken"] = [f"YETERSIZ VERI: trainval_n={len(trainval_idx)}, test_n={len(test_idx)} - sonuclar anlamsiz olabilir."]
    print("UYARI: yetersiz orneklem, yine de devam ediliyor (raporlama icin).")

# =====================================================================
# PURGED/EMBARGOLU WALK-FORWARD (MULTICLASS)
# =====================================================================
seg_edges = np.linspace(0, trainval_end_bar, WF_SEGMENTS + 1).astype(int)

def build_fold_sets(train_lo, train_hi, val_lo, val_hi):
    tr = labeled_idx_all[(labeled_idx_all >= train_lo) & (labeled_idx_all + N_BARS <= train_hi)]
    va = labeled_idx_all[(labeled_idx_all >= val_lo + EMBARGO_BARS) & (labeled_idx_all + N_BARS <= val_hi)]
    return tr, va

def fit_lgb_multiclass(Xtr_n, ytr, Xva_n, yva):
    model_ = lgb.LGBMClassifier(**LGB_PARAMS)
    model_.fit(Xtr_n, ytr, eval_set=[(Xva_n, yva)],
               callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)])
    return model_

wf_folds_info = []
oof_idx_list = []
oof_prob_list = []
for f in range(1, WF_SEGMENTS):
    train_lo, train_hi = 0, seg_edges[f]
    val_lo, val_hi = seg_edges[f], seg_edges[f + 1]
    tr_idx, va_idx = build_fold_sets(train_lo, train_hi, val_lo, val_hi)
    if len(tr_idx) < 200 or len(va_idx) < 50:
        wf_folds_info.append({"fold": f, "durum": "yetersiz_ornek_atlandi", "train_n": int(len(tr_idx)), "val_n": int(len(va_idx))})
        continue
    Xtr = X_full[tr_idx]; ytr = class_idx[tr_idx].astype(int)
    Xva = X_full[va_idx]; yva = class_idx[va_idx].astype(int)
    mu = Xtr.mean(axis=0); sd = Xtr.std(axis=0); sd[sd == 0] = 1.0
    Xtr_n = (Xtr - mu) / sd
    Xva_n = (Xva - mu) / sd
    model_f = fit_lgb_multiclass(Xtr_n, ytr, Xva_n, yva)
    p_va = model_f.predict_proba(Xva_n)  # (n,3): [P_asagi,P_notr,P_yukari]
    fold_logloss = log_loss(yva, p_va, labels=[0, 1, 2])
    fold_acc = accuracy_score(yva, np.argmax(p_va, axis=1))
    wf_folds_info.append({
        "fold": f, "train_lo_bar": int(train_lo), "train_hi_bar": int(train_hi),
        "val_lo_bar": int(val_lo), "val_hi_bar": int(val_hi),
        "train_n": int(len(tr_idx)), "val_n": int(len(va_idx)),
        "val_multiclass_logloss": round(float(fold_logloss), 4),
        "val_accuracy": round(float(fold_acc), 4),
        "best_iteration": int(model_f.best_iteration_) if model_f.best_iteration_ else LGB_PARAMS["n_estimators"],
    })
    oof_idx_list.append(va_idx)
    oof_prob_list.append(p_va)
    print(f"WF fold {f}: train_n={len(tr_idx)} val_n={len(va_idx)} logloss={fold_logloss:.4f} acc={fold_acc:.4f}")

results["walk_forward_purged_embargolu"] = {
    "segment_sayisi": WF_SEGMENTS, "fold_sayisi": WF_SEGMENTS - 1, "embargo_bars": EMBARGO_BARS,
    "sonuclar": wf_folds_info,
}
ll_list = [f_["val_multiclass_logloss"] for f_ in wf_folds_info if "val_multiclass_logloss" in f_]
acc_list = [f_["val_accuracy"] for f_ in wf_folds_info if "val_accuracy" in f_]
results["walk_forward_purged_embargolu"]["ozet"] = {
    "logloss_ortalama": round(float(np.mean(ll_list)), 4) if ll_list else None,
    "logloss_std": round(float(np.std(ll_list)), 4) if ll_list else None,
    "accuracy_ortalama": round(float(np.mean(acc_list)), 4) if acc_list else None,
    "accuracy_std": round(float(np.std(acc_list)), 4) if acc_list else None,
    "rastgele_taban_cizgisi_bilgi": "3 sinif rastgele tahmin: accuracy~0,333, logloss~ln(3)=1,099 (sinif dagilimina gore degisebilir)",
}
print("Walk-forward ozet:", results["walk_forward_purged_embargolu"]["ozet"])

# =====================================================================
# ESIK KALIBRASYONU (out-of-fold - TEST SETINE HENUZ BAKILMADI)
# Karar kurali: argmax==yukari VE P_yukari>=esik_yukari -> LONG; argmax==asagi VE P_asagi>=esik_asagi -> SHORT
# =====================================================================
oof_idx_all = np.concatenate(oof_idx_list) if oof_idx_list else np.array([], dtype=int)
oof_prob_all = np.concatenate(oof_prob_list, axis=0) if oof_prob_list else np.empty((0, 3))
oof_class_all = class_idx[oof_idx_all].astype(int) if len(oof_idx_all) else np.array([], dtype=int)
oof_argmax_all = np.argmax(oof_prob_all, axis=1) if len(oof_prob_all) else np.array([], dtype=int)

esik_tablosu = []
for t_yukari, t_asagi in zip(THRESH_YUKARI_CANDIDATES, THRESH_ASAGI_CANDIDATES):
    long_mask = (oof_argmax_all == 2) & (oof_prob_all[:, 2] >= t_yukari) if len(oof_prob_all) else np.array([], dtype=bool)
    short_mask = (oof_argmax_all == 0) & (oof_prob_all[:, 0] >= t_asagi) if len(oof_prob_all) else np.array([], dtype=bool)
    long_n = int(long_mask.sum()); short_n = int(short_mask.sum())
    long_prec = float((oof_class_all[long_mask] == 2).mean()) if long_n else None
    short_prec = float((oof_class_all[short_mask] == 0).mean()) if short_n else None
    toplam_n = long_n + short_n
    kapsama = round(toplam_n / len(oof_prob_all), 4) if len(oof_prob_all) else None
    esik_tablosu.append({
        "esik_yukari": t_yukari, "esik_asagi": t_asagi,
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

THRESH_YUKARI_FINAL = secilen_esik["esik_yukari"]
THRESH_ASAGI_FINAL = secilen_esik["esik_asagi"]

results["esik_kalibrasyonu"] = {
    "yontem": "Out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR) taramasi - TEST SETINE BAKILMADI",
    "karar_kurali": "argmax(P)==yukari VE P_yukari>=esik_yukari -> LONG; argmax(P)==asagi VE P_asagi>=esik_asagi -> SHORT; aksi -> ISLEM YOK",
    "oof_ornek_sayisi": int(len(oof_prob_all)), "min_sample_esigi": MIN_SAMPLE,
    "aday_tablosu": esik_tablosu,
    "SECILEN_ESIK_YUKARI": THRESH_YUKARI_FINAL, "SECILEN_ESIK_ASAGI": THRESH_ASAGI_FINAL,
    "YETERSIZ_ORNEKLEM_FALLBACK_UYGULANDI": yetersiz_uyarisi,
}
print("Esik kalibrasyonu:", THRESH_YUKARI_FINAL, THRESH_ASAGI_FINAL, "fallback:", yetersiz_uyarisi)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (walk-forward + esik kalibrasyonu) tamamlandi ->", OUT_PATH)

# =====================================================================
# FINAL MODEL - TUM TRAINVAL (SL/TP/esik/k_label ARTIK SABIT)
# =====================================================================
inner_val_start = seg_edges[WF_SEGMENTS - 1]
final_train_idx = labeled_idx_all[(labeled_idx_all + N_BARS <= seg_edges[WF_SEGMENTS - 1])]
final_innerval_idx = labeled_idx_all[
    (labeled_idx_all >= inner_val_start + EMBARGO_BARS) & (labeled_idx_all + N_BARS <= trainval_end_bar)
]
print("Final egitim n:", len(final_train_idx), "ic-validasyon n:", len(final_innerval_idx))

Xtr_final = X_full[final_train_idx]; ytr_final = class_idx[final_train_idx].astype(int)
Xiv_final = X_full[final_innerval_idx]; yiv_final = class_idx[final_innerval_idx].astype(int)

mu_final = Xtr_final.mean(axis=0); sd_final = Xtr_final.std(axis=0); sd_final[sd_final == 0] = 1.0
Xtr_final_n = (Xtr_final - mu_final) / sd_final
Xiv_final_n = (Xiv_final - mu_final) / sd_final

final_model = fit_lgb_multiclass(Xtr_final_n, ytr_final, Xiv_final_n, yiv_final)
p_iv = final_model.predict_proba(Xiv_final_n)
final_iv_logloss = float(log_loss(yiv_final, p_iv, labels=[0, 1, 2]))
final_iv_acc = float(accuracy_score(yiv_final, np.argmax(p_iv, axis=1)))
final_iv_cm = confusion_matrix(yiv_final, np.argmax(p_iv, axis=1), labels=[0, 1, 2]).tolist()
print("Final model ic-validasyon logloss:", final_iv_logloss, "acc:", final_iv_acc)

feat_importance = dict(zip(feature_names, [int(x) for x in final_model.feature_importances_]))
feat_importance_sirali = dict(sorted(feat_importance.items(), key=lambda kv: kv[1], reverse=True))

results["final_model_egitimi"] = {
    "egitim_n": int(len(final_train_idx)), "ic_validasyon_n": int(len(final_innerval_idx)),
    "ic_validasyon_multiclass_logloss": round(final_iv_logloss, 4),
    "ic_validasyon_accuracy": round(final_iv_acc, 4),
    "ic_validasyon_confusion_matrix_siralari_gercek_sutunlari_tahmin_0asagi_1notr_2yukari": final_iv_cm,
    "best_iteration": int(final_model.best_iteration_) if final_model.best_iteration_ else LGB_PARAMS["n_estimators"],
    "hiperparametreler_SABIT": {k: v for k, v in LGB_PARAMS.items()},
    "feature_importance_split_sayisi_SIRALI": feat_importance_sirali,
    "not_importance_metrigi": "LightGBM feature_importances_ = split-SAYISI (varsayilan) - v1/Hipotez1(v2) ile AYNI metrik, GORELI siralama karsilastirilabilir.",
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("ARA KAYIT (final model) tamamlandi ->", OUT_PATH)

# =====================================================================
# TEST SETI - TEK KEZ KULLANIM (S2 Madde2)
# ZORUNLU EK OLCUMLER: confusion-matrix + multiclass-log-loss (P&L'e donusmeyen ama modelin
# ayirt-ediciligini gosteren olcumler, Orkestrator gorev talimati Madde 7).
# =====================================================================
Xte = X_full[test_idx]
Xte_n = (Xte - mu_final) / sd_final
p_test = final_model.predict_proba(Xte_n)   # (n,3)
y_test_class = class_idx[test_idx].astype(int)
y_test_pred_argmax = np.argmax(p_test, axis=1)

test_multiclass_logloss = float(log_loss(y_test_class, p_test, labels=[0, 1, 2]))
test_accuracy = float(accuracy_score(y_test_class, y_test_pred_argmax))
test_confusion = confusion_matrix(y_test_class, y_test_pred_argmax, labels=[0, 1, 2]).tolist()

print("TEST SETI (tek-kez) multiclass logloss:", test_multiclass_logloss, "accuracy:", test_accuracy)
print("TEST confusion matrix (satir=gercek, sutun=tahmin, sira=[asagi,notr,yukari]):", test_confusion)

results["test_seti_siniflandirma_performansi"] = {
    "test_n": int(len(test_idx)),
    "test_multiclass_logloss": round(test_multiclass_logloss, 4),
    "test_accuracy": round(test_accuracy, 4),
    "test_confusion_matrix_satir_gercek_sutun_tahmin_sira_asagi_notr_yukari": test_confusion,
    "rastgele_taban_cizgisi_bilgi": "3 sinif rastgele tahmin: accuracy~0,333, logloss~ln(3)=1,099",
    "not": (
        "Bu, P&L'e DOGRUDAN donusmeyen bir siniflandirma-ayirt-edicilik olcumudur (Orkestrator "
        "Madde 7 - ZORUNLU). 'notr' sinifinin dogru/yanlis tahmini P&L'i DOGRUDAN ETKILEMEZ "
        "(o barda islem acilmaz), ama modelin GENEL ayirt-edicilik gucunu gosterir."
    ),
}

# TANI AMACLI - p_test dagilimi
results["test_p_dagilimi_TANI"] = {
    "p_yukari_mean": round(float(p_test[:, 2].mean()), 4), "p_yukari_std": round(float(p_test[:, 2].std()), 4),
    "p_asagi_mean": round(float(p_test[:, 0].mean()), 4), "p_asagi_std": round(float(p_test[:, 0].std()), 4),
    "p_notr_mean": round(float(p_test[:, 1].mean()), 4), "p_notr_std": round(float(p_test[:, 1].std()), 4),
    "esik_yukari_asan_VE_argmax_yukari_bar_sayisi": int(((y_test_pred_argmax == 2) & (p_test[:, 2] >= THRESH_YUKARI_FINAL)).sum()),
    "esik_asagi_asan_VE_argmax_asagi_bar_sayisi": int(((y_test_pred_argmax == 0) & (p_test[:, 0] >= THRESH_ASAGI_FINAL)).sum()),
}
print("TANI - p_test ozet:", results["test_p_dagilimi_TANI"])

# =====================================================================
# TICK-BAZLI GERCEK MALIYET MODELI (Justin ailesi standardi, v1 ile AYNI)
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
    """direction: +1 LONG, -1 SHORT. Risk yonetimi HER ZAMAN k_risk (basit ATR, 1,5x) barrier'ina
    gore yapilir - k_label/model-sinifi SADECE giris kararinin (LONG/SHORT/ISLEM-YOK) kaynagidir."""
    entry_idx = signal_idx + 1
    if entry_idx >= n:
        return None, "veri_sinirinda"
    entry_theo = c[signal_idx]
    exit_idx = exit_idx_arr[signal_idx]
    if exit_idx < 0:
        return None, "barrier_gecersiz"
    if label_neither[signal_idx]:
        exit_theo = time_exit_price_arr[signal_idx]
        exit_reason = "zaman_asimi"
    elif exit_reason_arr[signal_idx].startswith("TP"):
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

    risk_pts = K_RISK_ATR_MULT * atr14_m15_simple[signal_idx]
    risk_usd = risk_pts * POINT * CONTRACT_SIZE * LOT_FIXED
    risk_pct_of_kasa = risk_usd / KASA_USD

    return {
        "signal_idx": int(signal_idx), "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
        "tarih": dates_str[signal_idx], "saat_sinyal": int(hours[signal_idx]),
        "yon": "LONG" if direction == 1 else "SHORT",
        "model_sinif_yukari_p": None, "model_sinif_asagi_p": None, "model_sinif_notr_p": None,  # asagida doldurulur
        "gercek_3sinif_etiket": {0: "asagi", 1: "notr", 2: "yukari"}[int(y_class_lookup.get(signal_idx, -1))] if signal_idx in y_class_lookup else None,
        "barrier_zaman_asimi_mi": bool(label_neither[signal_idx]),
        "sebep": exit_reason,
        "atr_entry_pts_basit": round(float(atr14_m15_simple[signal_idx]), 2),
        "risk_pts": round(float(risk_pts), 2), "risk_usd_0_01_lot": round(float(risk_usd), 4),
        "risk_pct_of_kasa": round(float(risk_pct_of_kasa), 6),
        "tick_spread_pts": round(float(spread_pts_tick), 3), "giris_slipaj_pts": round(float(slip_pts), 3),
        "toplam_maliyet_pts": round(float(total_cost_pts), 3),
        "raw_pts": round(float(raw_pts), 3), "net_pts": round(float(net_pts), 3),
        "net_usd_0_01_lot": round(float(net_pts * POINT * CONTRACT_SIZE * LOT_FIXED), 4),
    }, "ok"

y_class_lookup = {int(idx): int(cls) for idx, cls in zip(test_idx, y_test_class)}

print("Test seti icin trade simulasyonu baslatiliyor (sadece esik-tetiklemeli sinyaller)...")

signal_dir = np.zeros(len(test_idx), dtype=int)
signal_dir[(y_test_pred_argmax == 2) & (p_test[:, 2] >= THRESH_YUKARI_FINAL)] = 1
signal_dir[(y_test_pred_argmax == 0) & (p_test[:, 0] >= THRESH_ASAGI_FINAL)] = -1

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
    res["model_sinif_asagi_p"] = round(float(p_test[pos_in_test, 0]), 4)
    res["model_sinif_notr_p"] = round(float(p_test[pos_in_test, 1]), 4)
    res["model_sinif_yukari_p"] = round(float(p_test[pos_in_test, 2]), 4)
    trade_log.append(res)
    open_until = res["exit_idx"]

print("Test seti PRIMARY (zaman-asimi haric barrier-gecerli kume) tetiklenen islem sayisi:", len(trade_log),
      "atlanma nedenleri:", dict(reasons))

def summarize_trades(trades):
    if not trades:
        return {"toplam_islem": 0, "win_rate": None, "profit_factor": None, "net_profit_pts": 0.0,
                "net_profit_usd_0_01_lot": 0.0, "max_drawdown_pct_kasa2000": None}
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
        "ortalama_atr_entry_pts": round(float(np.mean([x["atr_entry_pts_basit"] for x in trades])), 2),
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
for cnt, lbl in [(len(trade_log), "TEST_PRIMARY_tum_islemler"), (len(long_trades), "TEST_PRIMARY_LONG"), (len(short_trades), "TEST_PRIMARY_SHORT")]:
    w = minimum_sample_warning(cnt, lbl)
    if w:
        warnings_list.append(w)
if yetersiz_uyarisi:
    warnings_list.append(
        "ESIK_KALIBRASYONU_YETERSIZ_ORNEKLEM: hicbir esik adayi out-of-fold kumede MIN_SAMPLE "
        f"(>={MIN_SAMPLE}) esigini HER IKI tarafta da gecemedi - fallback (en genis kapsamli aday) secildi."
    )
warnings_list.append(
    f"SINYAL_SIKLIGI_KONTROLU: test setindeki {len(test_idx)} bar icinden {len(trade_log)} bar "
    f"esik-tetiklemeli islem uretti (kapsama ~{round(len(trade_log)/len(test_idx)*100,3) if len(test_idx) else 0}%)."
)
if dengesiz_mi:
    warnings_list.append(
        f"K_LABEL_AYARLANDI: baslangic k_label={K_LABEL_ATR_MULT_BASLANGIC} TRAINVAL'de dengesiz "
        f"bulundu (notr_oran={baseline_stats['notr_oran']}), k_label={K_LABEL_ATR_MULT_FINAL} olarak degistirildi (test setine bakilmadan)."
    )
warnings_list.append(
    "ATR_TUTARSIZLIGI: k_risk (SL/TP) BASIT rolling-ortalama ATR14 kullanir (Hipotez1 ile birebir "
    "ayni), k_label (3-sinif esik) Stratejist talimati geregi WILDER-smoothed ATR14 kullanir - bu "
    "iki farkli ATR tanimi kod duzeyinde AYRI degiskenlerdir (atr14_m15_simple/atr14_m15_wilder), "
    "birbirinin yerine KULLANILMAMISTIR; detay: k_label_yeniden_hesaplama.ATR_TUTARSIZLIGI_NOTU."
)

results["test_trade_simulasyonu_PRIMARY"] = {
    "aciklama": (
        "'Zaman-asimi' (barrier'in N=16 barda TP/SL'ye ulasmadigi) durumlar burada DAHIL EDILMISTIR "
        "- zira k_risk barrier mekanigi Hipotez1 ile AYNIDIR ve zaman-asimi GERCEK bir P&L uretir "
        "(c[i+N] ile kapanir). Bu, Hipotez1(v1/v2)'nin PRIMARY/'hicbiri-haric' ayrimindan FARKLI bir "
        "kavramdir (o ayrim ikili barrier-touch etiketine ozgudur, burada uygulanamaz - k_risk "
        "barrier zaten HER test barinda bir P&L uretir, model sinifindan BAGIMSIZ)."
    ),
    "esik_yukari": THRESH_YUKARI_FINAL, "esik_asagi": THRESH_ASAGI_FINAL,
    "atlanma_nedenleri": dict(reasons),
    "tum_islemler_ozet": primary_summary, "LONG_ozet": summarize_trades(long_trades), "SHORT_ozet": summarize_trades(short_trades),
    "tick_lookup_istatistigi": dict(TICK_LOOKUP_COUNT),
}
print("PRIMARY test sonuc ozeti:", primary_summary)

results["islem_logu_tam"] = trade_log
results["uyarilar"] = warnings_list

results["hipotez_ozet"] = {
    "hipotez_adi": "LightGBM 3-Sinifli (Deadzone) + Grup B Eklenmis Feature Seti - HIPOTEZ 2 (ETIKET-IZOLE, PARALEL)",
    "yaklasim_turu": "Makine Ogrenmesi - Gradient Boosting (LightGBM, multiclass)",
    "k_label_final": K_LABEL_ATR_MULT_FINAL, "k_risk_final": K_RISK_ATR_MULT,
    "hedef_pf": HEDEF_PF, "hedef_wr_rr11": HEDEF_WR_RR11, "hedef_dd": HEDEF_DD,
    "gozlemlenen_pf": primary_summary.get("profit_factor"), "gozlemlenen_wr": primary_summary.get("win_rate"),
    "test_multiclass_logloss": round(test_multiclass_logloss, 4), "test_accuracy": round(test_accuracy, 4),
    "hedef_pf_karsilandi_mi": (
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
