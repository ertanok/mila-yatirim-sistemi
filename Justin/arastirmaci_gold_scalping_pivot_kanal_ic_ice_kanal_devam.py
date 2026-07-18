# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping, Strateji Ailesi Plani ADIM 0 EK - IC-ICE KANAL METODOLOJI SORUSU
Gorev: gorev_arastirmaci_justin_gold_scalping_pivot_kanal_ic_ice_kanal_devam_20260716.md

Kapsam: Tam Yol1 pipeline turu DEGIL. Arastirmaci-duzeyi, dar kapsamli METODOLOJI EK olcumu.
Hipotez/model uretilmemistir, Stratejist'e devir yoktur.

Soru: 14 Temmuz raporundaki "onay-sonrasi trend-yonunde-devam orani" (fiyatin 1/3/7/14 gun
sonra hala trend yonunde ileride olup olmadigi) tutarsiz (%13-80) cikti. Bu tutarsizligin bir
nedeni, olcumun H1/M30 kanalinin ICINDEKI M15/M5-seviyesi dogal alt-kanallari/kisa ters-yon
hareketlerini "basarisizlik" olarak yanlislikla sayiyor olabilir mi?

Bu script:
  1. Ayni pivot/kanal formulunu (N=5 fraktal, >=3 dokunus, EMA50/EMA200+MACD 12/26/9, 0.5xATR14)
     DEGISTIRMEDEN H1/M30 (ana/parent kanal, GENEL veri) ve M15/M5 (alt-kanal, SADECE bir
     parent kanalin onay->kirilim aktif penceresi ICINDE) seviyesinde uygular.
  2. ESKI "devam" tanimini (fiyat konumu, 1/3/7/14 gun) yeniden hesaplar.
  3. YENI "devam" tanimini (ana kanal kirildi mi/kirilmadi mi, 1/3/7/14 gun ufkunda) hesaplar.
  4. Ic-ice alt-kanal sikligini (M15/M5, ayni yon + zit yon) parent kanal penceresi icinde olcer.

Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), GOLD, sunucu saati (GMT+3).
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Kod-iskeleti (MT5 baglanti, pivot/kanal algoritmasi) BILEREK ayni-proje-ici
arastirmaci_gold_scalping_pivot_kanal_tarama.py ile TUTARLI tutulmustur (karsilastirilabilirlik
amacli - izolasyon kurali yalniz BASKA projelerin dosya/format referansini yasaklar).
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
# ORTAK YARDIMCI FONKSIYONLAR (14 Temmuz scriptiyle AYNI)
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

# 14 Temmuz scriptinde sadece H1/M30 icin swing hesaplaniyordu; bu turde M15/M5 alt-kanal
# taramasi icin M15/M5 swingleri de GEREKLI (formul AYNI, sadece kapsam genisletildi).
SWINGS = {}
for tf in ("H1", "M30", "M15", "M5"):
    sh, sl = find_swings(raw[tf], n=5)
    SWINGS[tf] = {"swing_high": sh, "swing_low": sl}
    print(tf, "swing_high n=", sh.sum(), "swing_low n=", sl.sum())

CAP_MINUTES = 300 * 24 * 60  # ~300 gun gercek-zaman arama penceresi siniri (14 Temmuz ile AYNI)


# ============================================================
# GENEL PIVOT/KANAL TESPIT FONKSIYONU (parametrik pencere ile)
# Formul TAM OLARAK 14 Temmuz scriptiyle AYNI (arastirmaci_gold_scalping_pivot_kanal_tarama.py,
# detect_channels). Tek fark: swing havuzu ve arama/kirilim ust siniri artik bir [lo, hi)
# penceresiyle kisitlanabiliyor (parent=tum veri: lo=0, hi=n_total; alt-kanal=parent kanalin
# aktif penceresiyle kesisen M15/M5 bar araligi).
# ============================================================

def detect_channels_windowed(tf_name, direction, lo, hi, min_touches=3, touch_k=0.5):
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

    full_swing_idx = np.where(swing_mask)[0]
    swing_idx = full_swing_idx[(full_swing_idx >= lo) & (full_swing_idx < hi)]
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

        # tam kirilim noktasi: TUM barlar (sadece swingler degil), cizgi DONDURULMUS,
        # pencerenin ustu (hi-1) veya 300-gun capi, hangisi once gelirse
        break_idx = None
        limit_idx = min(hi - 1, anchor + cap_bars)
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
            "censored": bool(censored),
        })

        next_pos = np.searchsorted(swing_idx, break_idx, side="right")
        pos = max(next_pos, pos + 1)

    return channels


def detect_channels(tf_name, direction, min_touches=3, touch_k=0.5):
    """Parent (H1/M30) kanal tespiti - GENEL veri, tam pencere (14 Temmuz ile AYNI cagri)."""
    return detect_channels_windowed(tf_name, direction, 0, len(raw[tf_name]), min_touches, touch_k)


# ============================================================
# 1) PARENT (H1/M30) KANAL TESPITI
# ============================================================

channel_results = {}
for tf_name in ("H1", "M30"):
    channel_results[tf_name] = {}
    for direction in ("up", "down"):
        chs = detect_channels(tf_name, direction)
        channel_results[tf_name][direction] = chs
        print(tf_name, direction, "confirmed parent kanal sayisi:", len(chs))

results["parent_kanal_sayisi"] = {
    tf: {d: len(channel_results[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")
}

# ============================================================
# 2) ESKI "DEVAM" TANIMI (fiyat konumu, 1/3/7/14 gun) - 14 Temmuz ile AYNI YONTEM
# ============================================================

DAY_HORIZONS = [1, 3, 7, 14]


def eski_devam_tanimi(tf_name, direction, chs):
    bar_min = TFS[tf_name][1]
    n_total_bars = len(raw[tf_name])
    closes = raw[tf_name]['close'].astype(float)
    sign = 1 if direction == "up" else -1

    devam = {}
    for d in DAY_HORIZONS:
        N = int(d * 24 * 60 / bar_min)
        same_dir = []
        for c in chs:
            ci = c["confirm_idx"]
            if ci + N < n_total_bars:
                p0 = closes[ci]
                p1 = closes[ci + N]
                same_dir.append(1 if sign * (p1 - p0) > 0 else 0)
        if same_dir:
            devam[f"{d}_gun"] = {
                "n": len(same_dir),
                "trend_yonunde_devam_orani": round(float(np.mean(same_dir)), 4),
            }
        else:
            devam[f"{d}_gun"] = {"n": 0, "trend_yonunde_devam_orani": None}
    return devam


# ============================================================
# 3) YENI "DEVAM" TANIMI (ana kanal kirildi mi/kirilmadi mi, 1/3/7/14 gun ufku)
#    - censored VEYA gercek kirilim suresi >= ufuk gunu ise "kirilmadi" (1)
#    - gercek kirilim suresi < ufuk gunu ise "kirildi" (0)
#    - censored VE censored-suresi < ufuk gunu ise BELIRSIZ -> orneklemden CIKARILIR
#      (veri/pencere o ufka kadar uzanmiyor, bilinemez)
# ============================================================

def yeni_devam_tanimi(tf_name, chs):
    bar_min = TFS[tf_name][1]
    devam = {}
    for d in DAY_HORIZONS:
        kirilmadi = []
        belirsiz_sayisi = 0
        for c in chs:
            dur_days = c["duration_bars_confirm_to_break"] * bar_min / (60 * 24)
            if dur_days >= d:
                kirilmadi.append(1)  # ana kanal en az d gun boyunca kirilmadi (bilinen)
            else:
                if c["censored"]:
                    belirsiz_sayisi += 1  # veri/pencere o ufka ulasmadan bitti -> bilinemez
                    continue
                else:
                    kirilmadi.append(0)  # d gunden ONCE gercekten kirildi (bilinen)
        if kirilmadi:
            devam[f"{d}_gun"] = {
                "n": len(kirilmadi),
                "n_belirsiz_disarida_birakildi": belirsiz_sayisi,
                "ana_kanal_kirilmadi_orani": round(float(np.mean(kirilmadi)), 4),
            }
        else:
            devam[f"{d}_gun"] = {"n": 0, "n_belirsiz_disarida_birakildi": belirsiz_sayisi,
                                  "ana_kanal_kirilmadi_orani": None}
    return devam


devam_karsilastirma = {}
for tf_name in ("H1", "M30"):
    devam_karsilastirma[tf_name] = {}
    for direction in ("up", "down"):
        chs = channel_results[tf_name][direction]
        devam_karsilastirma[tf_name][direction] = {
            "n_kanal_toplam": len(chs),
            "eski_tanim_fiyat_konumu": eski_devam_tanimi(tf_name, direction, chs),
            "yeni_tanim_ana_kanal_kirilma_bazli": yeni_devam_tanimi(tf_name, chs),
        }

results["devam_tanimi_karsilastirma"] = devam_karsilastirma

# ============================================================
# 4) IC-ICE ALT-KANAL SIKLIGI (M15/M5, parent kanal aktif penceresi icinde)
#    - "n_overlap" sayimi 14 Temmuz scriptindeki project_and_find_entries ile AYNI kriter:
#      break_t < ltf_t0 veya confirm_t > ltf_t1 ise atla; sonra hi-lo < 3 ise atla.
# ============================================================

def alt_kanal_sikligi(htf_name, ltf_name, channels_htf, htf_direction):
    ltf_rates = raw[ltf_name]
    ltf_times = ltf_rates['time'].astype(np.int64)
    ltf_t0, ltf_t1 = int(ltf_times[0]), int(ltf_times[-1])

    per_window_counts = []  # her ortusen parent-pencere icin (ayni_yon_sayisi, zit_yon_sayisi)
    n_overlap = 0

    for c in channels_htf:
        confirm_t = int(datetime.strptime(c["confirm_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        break_t = int(datetime.strptime(c["break_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        if break_t < ltf_t0 or confirm_t > ltf_t1:
            continue
        win_start = max(confirm_t, ltf_t0)
        win_end = min(break_t, ltf_t1)
        lo = int(np.searchsorted(ltf_times, win_start, side="left"))
        hi = int(np.searchsorted(ltf_times, win_end, side="right"))
        if hi - lo < 3:
            continue
        n_overlap += 1

        ayni_yon = detect_channels_windowed(ltf_name, htf_direction, lo, hi)
        zit_yon_dir = "down" if htf_direction == "up" else "up"
        zit_yon = detect_channels_windowed(ltf_name, zit_yon_dir, lo, hi)

        per_window_counts.append({
            "confirm_time": c["confirm_time"], "break_time": c["break_time"],
            "n_ltf_bar_pencerede": int(hi - lo),
            "ayni_yon_alt_kanal_sayisi": len(ayni_yon),
            "zit_yon_alt_kanal_sayisi": len(zit_yon),
        })

    if n_overlap == 0:
        return {
            "n_overlap_parent_kanal": 0,
            "ortalama_ayni_yon_alt_kanal": None,
            "ortalama_zit_yon_alt_kanal": None,
            "ortalama_toplam_alt_kanal": None,
            "detay": [],
        }

    ayni = [w["ayni_yon_alt_kanal_sayisi"] for w in per_window_counts]
    zit = [w["zit_yon_alt_kanal_sayisi"] for w in per_window_counts]
    toplam = [a + z for a, z in zip(ayni, zit)]

    return {
        "n_overlap_parent_kanal": n_overlap,
        "ortalama_ayni_yon_alt_kanal": round(float(np.mean(ayni)), 2),
        "ortalama_zit_yon_alt_kanal": round(float(np.mean(zit)), 2),
        "ortalama_toplam_alt_kanal": round(float(np.mean(toplam)), 2),
        "medyan_toplam_alt_kanal": round(float(np.median(toplam)), 2),
        "min_maks_toplam_alt_kanal": [int(np.min(toplam)), int(np.max(toplam))],
        "detay": per_window_counts,
    }


ic_ice_sikligi = {}
for htf in ("H1", "M30"):
    for ltf in ("M15", "M5"):
        combo = f"{htf}_to_{ltf}"
        ic_ice_sikligi[combo] = {}
        for direction in ("up", "down"):
            print("ic-ice tarama basliyor:", combo, direction)
            ic_ice_sikligi[combo][direction] = alt_kanal_sikligi(
                htf, ltf, channel_results[htf][direction], direction)
            print("  ->", combo, direction, "n_overlap=",
                  ic_ice_sikligi[combo][direction]["n_overlap_parent_kanal"],
                  "ort_toplam=", ic_ice_sikligi[combo][direction]["ortalama_toplam_alt_kanal"])

results["ic_ice_alt_kanal_sikligi"] = ic_ice_sikligi

with open(r"C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam_output.json",
          "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI. JSON yazildi.")
mt5.shutdown()
