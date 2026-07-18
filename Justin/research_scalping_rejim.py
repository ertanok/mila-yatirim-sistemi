# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping Arastirmasi - REJIM-SEGMENTLI EK ANALIZ
(Stratejist raporu stratejici_raporu_justin_gold_scalping_20260712.md, Bolum 6 talebi)

Amac: Hipotez 3 (Rejim-Farkinda Hibrit) icin ON-KOSUL - mevcut research_scalping.py'nin
BULGU 3 (ardisik bar yon devami) ve BULGU 4 (buyuk-bar sonrasi yon) olcumlerini
trend/range rejimine gore ALT-ORNEKLEMLERE bolerek yeniden hesaplar + her alt-orneklem
icin binom/ki-kare istatistiksel anlamlilik testi uygular (Risk Analisti'nin Hipotez 2'de
uyguladigi yontemle AYNI: scipy.stats.binomtest(iki-yonlu, H0: p=0.5) + ki-kare uygunluk
testi df=1, alpha=0.05).

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Sadece ham OHLCV veri MT5'ten (dogrudan MetaTrader5 kutuphanesi) cekilir. Yeni veri kaynagi
ARANMADI - ayni GOLD M1/M5 serisi, ayni pencere/esik (99999 bar, 1.5x mult) korunmustur.

Rejim etiketleme (nedensel/ileri-bakissiz - yalniz GECMIS veri kullanilir):
  - Label VOL  (volatilite genisligi): ATR(14), bar i'de bar(i-13..i) kullanilarak hesaplanir
    (causal). Bar i'nin ATR(14) degeri, KENDI trailing 100-bar penceresinin (bar i-99..i,
    yine yalniz gecmis+kendisi) medyaniyla kiyaslanir -> "genis" (ATR14[i] > trailing medyan)
    veya "dar" (<=).
  - Label TREND (Kaufman Efficiency Ratio, 20-bar): ER20[i] = |close[i]-close[i-20]| /
    sum(|close[j]-close[j-1]|, j=i-19..i) - net yer degistirme / kat edilen toplam yol.
    1'e yakin = guclu tek yonlu hareket (trend), 0'a yakin = fiyatin ileri-geri gidip
    net yer degistirmedigi (range/choppy). ER20[i], KENDI trailing 100-bar penceresinin
    (i-99..i) medyaniyla kiyaslanir -> "trend" (>medyan) veya "range" (<=medyan).
  - Her iki esik de (ATR trailing medyan, ER trailing medyan) o ana kadarki GECMIS veriden
    turetilir - hicbir noktada ileri-bakis (gelecek bar) kullanilmaz. Esik sabit/global bir
    deger degil, kendi trailing penceresidir (bkz. SINIR bolumu, rapor).

Regime label bar i'ye atanir; bir sonraki barin (i+1) yonunu tahmin etmek icin
kullanilir (BULGU3/4'un orijinal mantigi ile ayni: "bar i'de bilinen bilgiyle bar i+1
ne yapar" sorusu, sadece burada bar i'nin rejim etiketi de bilgiye ekleniyor).
"""
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from datetime import datetime
from scipy import stats
import MetaTrader5 as mt5

assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)

ATR_PERIOD = 14
ER_WINDOW = 20
TRAIL_WINDOW = 100          # ATR/ER trailing-medyan esik penceresi (causal)
BIGBAR_MULT = 1.5           # BULGU4 ile ayni esik (research_scalping.py, degistirilmedi)
ALPHA = 0.05

m1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 99999)
m5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 99999)

print("M1 bar sayisi:", len(m1) if m1 is not None else None)
print("M5 bar sayisi:", len(m5) if m5 is not None else None)


# ---------------------------------------------------------------------
# 1) REJIM ETIKETLEME (nedensel/ileri-bakissiz)
# ---------------------------------------------------------------------
def rolling_median_trailing(arr, window):
    """arr[i]'yi de iceren, bar i-window+1..i araligindaki trailing medyan.
    Herhangi bir eleman NaN ise (yetersiz gecmis) sonuc NaN (np.median NaN-propagate eder)."""
    n = len(arr)
    out = np.full(n, np.nan)
    if n < window:
        return out
    windows = sliding_window_view(arr, window)
    out[window - 1:] = np.median(windows, axis=1)
    return out


def compute_regime_labels(rates):
    h = rates['high'].astype(float)
    l = rates['low'].astype(float)
    c = rates['close'].astype(float)
    n = len(c)

    # --- ATR(14), causal ---
    tr = np.empty(n)
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(np.maximum(h[1:] - l[1:], np.abs(h[1:] - c[:-1])), np.abs(l[1:] - c[:-1]))
    atr14 = np.full(n, np.nan)
    if n >= ATR_PERIOD:
        atr_windows = sliding_window_view(tr, ATR_PERIOD)
        atr14[ATR_PERIOD - 1:] = atr_windows.mean(axis=1)
    atr_trail_med = rolling_median_trailing(atr14, TRAIL_WINDOW)

    label_vol = np.full(n, None, dtype=object)
    valid_vol = ~np.isnan(atr_trail_med) & ~np.isnan(atr14)
    label_vol[valid_vol & (atr14 > atr_trail_med)] = "genis"
    label_vol[valid_vol & (atr14 <= atr_trail_med)] = "dar"

    # --- Kaufman Efficiency Ratio (20-bar), causal ---
    diffs = np.abs(np.diff(c))  # length n-1, diffs[j] = |c[j+1]-c[j]|
    net_move = np.full(n, np.nan)
    if n > ER_WINDOW:
        net_move[ER_WINDOW:] = np.abs(c[ER_WINDOW:] - c[:-ER_WINDOW])
    path_sum = np.full(n, np.nan)
    if len(diffs) >= ER_WINDOW:
        diff_windows = sliding_window_view(diffs, ER_WINDOW)  # rows = n-1-ER_WINDOW+1 = n-ER_WINDOW
        path_sum[ER_WINDOW:] = diff_windows.sum(axis=1)
    er20 = np.full(n, np.nan)
    valid_path = ~np.isnan(path_sum) & (path_sum > 0)
    er20[valid_path] = net_move[valid_path] / path_sum[valid_path]
    er_trail_med = rolling_median_trailing(er20, TRAIL_WINDOW)

    label_trend = np.full(n, None, dtype=object)
    valid_trend = ~np.isnan(er_trail_med) & ~np.isnan(er20)
    label_trend[valid_trend & (er20 > er_trail_med)] = "trend"
    label_trend[valid_trend & (er20 <= er_trail_med)] = "range"

    return label_vol, label_trend, atr14, er20


def significance_test(n_success, n_total):
    """Risk Analisti'nin Hipotez 2'de uyguladigi yontemle AYNI:
    binom test (iki-yonlu, H0: p=0.5) + ki-kare uygunluk testi (df=1)."""
    if n_total == 0:
        return {
            "binom_test_p_degeri": None,
            "chi_kare_istatistigi": None,
            "chi_kare_p_degeri": None,
            "anlamli_mi_alpha_0_05": None,
        }
    binom = stats.binomtest(n_success, n_total, 0.5, alternative='two-sided')
    expected = n_total * 0.5
    chi2_stat = ((n_success - expected) ** 2 / expected) + (((n_total - n_success) - expected) ** 2 / expected)
    chi2_p = float(1 - stats.chi2.cdf(chi2_stat, df=1))
    return {
        "binom_test_p_degeri": float(binom.pvalue),
        "chi_kare_istatistigi": round(float(chi2_stat), 3),
        "chi_kare_p_degeri": round(chi2_p, 6),
        "anlamli_mi_alpha_0_05": bool(binom.pvalue < ALPHA),
    }


# ---------------------------------------------------------------------
# 2) BULGU 3 (ardisik bar yon devami) - REJIM-SEGMENTLI
# ---------------------------------------------------------------------
def continuation_by_regime(rates, regime_label, label_values):
    opens = rates['open'].astype(float)
    closes = rates['close'].astype(float)
    direction = np.sign(closes - opens)
    n = len(direction)

    out = {}

    # ---- genel ardisik-ikili (pair) devam orani, bar (k-1,k), regime = label[k-1] ----
    prev_dir = direction[:-1]
    next_dir = direction[1:]
    prev_regime = regime_label[:-1]
    pair_valid = (prev_dir != 0) & (next_dir != 0)
    pair_same = (next_dir == prev_dir)

    # ---- streak analizi: d = doji haric yon dizisi, nz_idx = orig index karsiligi ----
    nz_idx = np.where(direction != 0)[0]
    d = direction[nz_idx]

    cur = np.ones(len(d), dtype=int)
    for i in range(1, len(d)):
        cur[i] = cur[i - 1] + 1 if d[i] == d[i - 1] else 1

    for regime_value in label_values:
        mask = pair_valid & (prev_regime == regime_value)
        n_total_pair = int(mask.sum())
        n_same_pair = int(pair_same[mask].sum()) if n_total_pair else 0
        general = {
            "n_total": n_total_pair,
            "n_ayni_yon": n_same_pair,
            "ayni_yon_orani": round(n_same_pair / n_total_pair, 3) if n_total_pair else None,
        }
        general.update(significance_test(n_same_pair, n_total_pair))

        streak_results = {}
        for streak_len in [2, 3, 4, 5]:
            hits_total = 0
            hits_same = 0
            idxs = np.where(cur[:-1] == streak_len)[0]  # cur uses d-space index; exclude last (no i+1)
            for i in idxs:
                orig_i = nz_idx[i]  # bar index (streak'in son bari) - regime buradan okunur (causal)
                if regime_label[orig_i] != regime_value:
                    continue
                hits_total += 1
                if d[i + 1] == d[i]:
                    hits_same += 1
            if hits_total > 0:
                entry = {
                    "n": hits_total,
                    "sonraki_bar_ayni_yon_orani": round(hits_same / hits_total, 3),
                }
                entry.update(significance_test(hits_same, hits_total))
                streak_results[streak_len] = entry

        out[regime_value] = {
            "genel_ardisik_ayni_yon": general,
            "streak_sonrasi": streak_results,
        }
    return out


# ---------------------------------------------------------------------
# 3) BULGU 4 (buyuk-bar sonrasi yon) - REJIM-SEGMENTLI
# ---------------------------------------------------------------------
def breakout_by_regime(rates, regime_label, label_values, mult=BIGBAR_MULT):
    opens = rates['open'].astype(float)
    closes = rates['close'].astype(float)
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    ranges = highs - lows
    mean_r = ranges.mean()  # research_scalping.py ile AYNI esik tanimi (full-sample ortalama)
    direction = np.sign(closes - opens)

    big_idx = np.where(ranges > mult * mean_r)[0]
    big_idx = big_idx[(big_idx > 0) & (big_idx < len(rates) - 1)]

    out = {}
    for regime_value in label_values:
        same_dir_next = 0
        opp_dir_next = 0
        n_big = 0
        for i in big_idx:
            if regime_label[i] != regime_value:
                continue
            if direction[i] == 0:
                continue
            n_big += 1
            nd = np.sign(closes[i + 1] - opens[i + 1])
            if nd == direction[i]:
                same_dir_next += 1
            elif nd == -direction[i]:
                opp_dir_next += 1
        total = same_dir_next + opp_dir_next
        entry = {
            "buyuk_bar_sayisi_rejimde": n_big,
            "yonlu_cift_n": total,
            "sonraki_bar_ayni_yon_sayisi": same_dir_next,
            "sonraki_bar_ters_yon_sayisi": opp_dir_next,
            "ayni_yon_orani": round(same_dir_next / total, 3) if total else None,
        }
        entry.update(significance_test(same_dir_next, total))
        out[regime_value] = entry
    return out


# ---------------------------------------------------------------------
# CALISTIR
# ---------------------------------------------------------------------
results = {
    "meta": {
        "yontem_notu": "Rejim etiketleri (VOL: ATR14 vs trailing-100 medyan; TREND: ER20 vs "
                        "trailing-100 medyan) nedensel/ileri-bakissizdir - yalniz bar i ve "
                        "oncesindeki veri kullanilir. BULGU4 ile ayni 1.5x-ortalama-range esigi "
                        "korunmustur. Istatistiksel anlamlilik: scipy.stats.binomtest (iki-yonlu, "
                        "H0: p=0.5) + ki-kare uygunluk testi (df=1), Risk Analisti Hipotez2 ile ayni "
                        "yontem, alpha=0.05.",
        "atr_period": ATR_PERIOD,
        "er_window": ER_WINDOW,
        "trail_window_regime_esigi": TRAIL_WINDOW,
        "bigbar_mult": BIGBAR_MULT,
        "alpha": ALPHA,
    }
}

for tf_name, rates in [("M1", m1), ("M5", m5)]:
    label_vol, label_trend, atr14, er20 = compute_regime_labels(rates)

    n_vol_valid = int((label_vol != None).sum())
    n_trend_valid = int((label_trend != None).sum())
    n_genis = int((label_vol == "genis").sum())
    n_dar = int((label_vol == "dar").sum())
    n_trend = int((label_trend == "trend").sum())
    n_range = int((label_trend == "range").sum())

    results[tf_name + "_rejim_etiket_dagilimi"] = {
        "toplam_bar": int(len(rates)),
        "VOL_etiketli_bar": n_vol_valid,
        "VOL_genis": n_genis,
        "VOL_dar": n_dar,
        "TREND_etiketli_bar": n_trend_valid,
        "TREND_trend": n_trend,
        "TREND_range": n_range,
    }

    results[tf_name + "_BULGU3_rejim_VOL"] = continuation_by_regime(rates, label_vol, ["genis", "dar"])
    results[tf_name + "_BULGU3_rejim_TREND"] = continuation_by_regime(rates, label_trend, ["trend", "range"])

    results[tf_name + "_BULGU4_rejim_VOL"] = breakout_by_regime(rates, label_vol, ["genis", "dar"])
    results[tf_name + "_BULGU4_rejim_TREND"] = breakout_by_regime(rates, label_trend, ["trend", "range"])

    print(f"--- {tf_name} tamamlandi ---")

with open(r"C:\MilaYatirim\Justin\research_scalping_rejim_output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(json.dumps(results, ensure_ascii=False, indent=2))

mt5.shutdown()
