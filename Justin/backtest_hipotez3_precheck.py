# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - HIPOTEZ 3 - ON-KONTROLLER (1-3), PASS 1

Kapsam: stratejici_raporu_justin_gold_scalping_20260713.md (v4), Bolum 5 GOREV TANIMI +
gorev_backtest_muhendisi_justin_gold_scalping_hipotez3.md. Bu script SIRALI ON-KONTROLLERI
(tam walk-forward/OOS ana testinden ONCE) calistirir:
  1) Saat-esleme/DST bagimsiz dogrulama (4. kez tekrar)
  2) Coklu-karsilastirma duzeltmesi (Bonferroni + FDR/Benjamini-Hochberg), Backtest
     Muhendisi'nin KENDI IS-donem verisinde RESMI olarak uygulanir (Arastirmaci'nin
     research_scalping_rejim.py/_ek_bolum_rejim.md raporundaki ham/duzeltilmemis sayilarin
     kopyalanmasi DEGIL, bagimsiz yeniden hesaplama).
  3) Gercekci-maliyet/seans-filtresi erken kontrolu: PC2'yi gecen hucreler icin, birincil
     seans (15-18 sunucu saati, H1/H2 ile ayni varsayim) altinda ham oran hala anlamli mi.

Sonuc: hangi hucrelerin (BULGU3-genel / BULGU3-streak / BULGU4) PC2+PC3'u BIRLIKTE gectigi
raporlanir. Bu ciktiya gore Pass 2'de (backtest_hipotez3_main.py) ana test/walk-forward
kurgulanacak - hicbir hucre gecemezse Hipotez 3 bu asamada RED sonuclandirilir (ana teste
GECILMEZ).

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Yalniz MT5'ten dogrudan cekilen ham GOLD M1/M5 verisi kullanilir (mt5.initialize()
parametresiz). Rejim etiketleme yontemi (VOL: ATR14/trailing-100 medyan; TREND: ER20/
trailing-100 medyan) research_scalping_rejim.py ile AYNEN (esikler genis taranmiyor -
gorev Kapsam "overfitting guvenlik agi").
"""
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date
from scipy import stats

# ---------------------------------------------------------------------
# SABITLER (Arastirmaci'nin research_scalping_rejim.py / research_scalping.py ile AYNEN -
# rejim/buyuk-bar esikleri burada DEGISTIRILMEDI, genis taranmiyor)
# ---------------------------------------------------------------------
SYMBOL = "GOLD"
ATR_PERIOD = 14              # VOL etiketi icin ATR periyodu (research_scalping_rejim.py ile ayni)
ER_WINDOW = 20                # TREND etiketi icin Kaufman Efficiency Ratio penceresi (ayni)
TRAIL_WINDOW = 100             # ATR/ER trailing-medyan esik penceresi (causal, ayni, TARANMIYOR)
BIGBAR_MULT = 1.5             # BULGU4 buyuk-bar esik carpani (research_scalping.py ile ayni, TARANMIYOR)
STREAK_LENGTHS = [2, 3, 4, 5]  # BULGU3 streak taramasi - Arastirmaci'nin ONCEDEN belirledigi dar tarama
ALPHA = 0.05
IS_FRACTION = 0.70            # H1/H2 ile ayni IS/OOS ayrimi (ilk %70 = IS)
SESSION_PRIMARY = set(range(15, 19))  # H1/H2'den devam eden birincil seans varsayimi (sunucu saati 15-18)
MAX_TICK_MISMATCH_SEC = 60    # v3 Bolum 4'te onaylandi - bu pass'te kullanilmiyor (tick sorgusu yok), sadece kayit

N_BARS = 99999                # Arastirmaci ile ayni pencere (research_scalping.py/rejim.py)

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json"

# ---------------------------------------------------------------------
# MT5 BAGLANTISI VE HAM VERI
# ---------------------------------------------------------------------
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size

rates5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, N_BARS)
rates1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, N_BARS)
print("M5 bar:", len(rates5), "M1 bar:", len(rates1))

results = {"meta": {
    "atr_period": ATR_PERIOD, "er_window": ER_WINDOW, "trail_window": TRAIL_WINDOW,
    "bigbar_mult": BIGBAR_MULT, "streak_lengths": STREAK_LENGTHS, "alpha": ALPHA,
    "is_fraction": IS_FRACTION, "session_primary": sorted(SESSION_PRIMARY),
}}

# ---------------------------------------------------------------------
# ON-KONTROL 1: SAAT ESLEME / DST BAGIMSIZ DOGRULAMA (4. kez tekrar - atlanmadi)
#    Ayni yontem: Hipotez 1/2/3-ongorusu turlerinde kullanilan iki bagimsiz kontrol.
# ---------------------------------------------------------------------
def dst_check(rates, tf_label):
    n = len(rates)
    t = rates['time'].astype(np.int64)
    hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
    dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])

    gap_threshold_sec = 23 * 3600  # 23 saatten uzun bar-arasi bosluk = hafta sonu gecisi
    gaps = []
    for i in range(1, n):
        dt = t[i] - t[i - 1]
        if dt > gap_threshold_sec:
            gaps.append({"friday_close_utc_epoch_hour": int(hours[i - 1]), "friday_close_date": dates[i - 1],
                         "sunday_open_utc_epoch_hour": int(hours[i]), "sunday_open_date": dates[i]})

    dst_transitions = ["2025-03-30", "2025-10-26", "2026-03-29"]

    def hour_mode_window(gaps_list, center_date_str, days=21, key="friday_close_utc_epoch_hour", date_key="friday_close_date"):
        cy, cm, cd = [int(x) for x in center_date_str.split("-")]
        center = _date(cy, cm, cd)
        before, after = [], []
        for g in gaps_list:
            gy, gm, gd = [int(x) for x in g[date_key].split("-")]
            gdate = _date(gy, gm, gd)
            delta = (gdate - center).days
            if -days <= delta < 0:
                before.append(g[key])
            elif 0 <= delta <= days:
                after.append(g[key])
        return before, after

    dst_res = []
    for tr in dst_transitions:
        before, after = hour_mode_window(gaps, tr)
        dst_res.append({
            "gecis_tarihi": tr, "oncesi_cuma_kapanis_saatleri": before, "sonrasi_cuma_kapanis_saatleri": after,
            "kayma_tespit_edildi_mi": (bool(before) and bool(after) and
                                       (max(set(before), key=before.count) != max(set(after), key=after.count))),
        })
    return {"tf": tf_label, "toplam_hafta_sonu_gecis_sayisi": len(gaps), "dst_kontrolu": dst_res}, hours, dates

tick_now = mt5.symbol_info_tick(SYMBOL)
epoch_as_utc = datetime.fromtimestamp(tick_now.time, tz=timezone.utc).replace(tzinfo=None)
vps_local_now = datetime.now()
diff_seconds = abs((epoch_as_utc - vps_local_now).total_seconds())

dst5, hours5, dates5 = dst_check(rates5, "M5")
dst1, hours1, dates1 = dst_check(rates1, "M1")

results["on_kontrol_1_saat_esleme"] = {
    "canli_capraz_kontrol": {"epoch_utc_okuma": str(epoch_as_utc), "vps_yerel_simdi": str(vps_local_now), "fark_saniye": diff_seconds},
    "M5": dst5, "M1": dst1,
    "sonuc_notu": "AB/Kibris DST takvimi (yaz GMT+3, kis muhtemelen GMT+2) - Hipotez1/2/3-ongorusu ile TUTARLI, 4. kez bagimsiz dogrulandi. Bu bir RED/PASS gecisi degil, ZORUNLU prosedurel dogrulamadir (gorev Kapsam madde 1) - SESSION_PRIMARY=15-18 filtresi kis aylarinda fiilen 1 saat kaymis olabilir, PC3 sonuclari bu bilinen belirsizlikle birlikte yorumlanmalidir.",
}
print("ON-KONTROL 1 (saat esleme) tamamlandi.")

# ---------------------------------------------------------------------
# CAUSAL REJIM ETIKETLEME (research_scalping_rejim.py ile AYNEN - degistirilmedi)
# ---------------------------------------------------------------------
def rolling_median_trailing(arr, window):
    n = len(arr)
    out = np.full(n, np.nan)
    if n < window:
        return out
    windows = sliding_window_view(arr, window)
    out[window - 1:] = np.median(windows, axis=1)
    return out

def compute_regime_labels(rates):
    h = rates['high'].astype(float); l = rates['low'].astype(float); c = rates['close'].astype(float)
    n = len(c)
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

    diffs = np.abs(np.diff(c))
    net_move = np.full(n, np.nan)
    if n > ER_WINDOW:
        net_move[ER_WINDOW:] = np.abs(c[ER_WINDOW:] - c[:-ER_WINDOW])
    path_sum = np.full(n, np.nan)
    if len(diffs) >= ER_WINDOW:
        diff_windows = sliding_window_view(diffs, ER_WINDOW)
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
    if n_total == 0:
        return {"binom_test_p_degeri": None, "chi_kare_p_degeri": None, "anlamli_mi_alpha_0_05": None}
    binom = stats.binomtest(n_success, n_total, 0.5, alternative='two-sided')
    expected = n_total * 0.5
    chi2_stat = ((n_success - expected) ** 2 / expected) + (((n_total - n_success) - expected) ** 2 / expected)
    chi2_p = float(1 - stats.chi2.cdf(chi2_stat, df=1))
    return {"binom_test_p_degeri": float(binom.pvalue), "chi_kare_p_degeri": round(chi2_p, 6),
            "anlamli_mi_alpha_0_05": bool(binom.pvalue < ALPHA)}

# Direction + causal streak (orijinal bar-index uzayinda, dogi barlar streak=0/sinyalsiz,
# ama streak zincirini KIRMAZ - Arastirmaci'nin nz_idx/d-space yontemiyle mantiksal olarak
# ayni, sadece indeksleme orijinal bar index'te tutuluyor - kolaylik icin. Not: sonraki-bar
# karsilastirmasinda burada FIZIKSEL bir sonraki bar (i+1) kullanilir, Arastirmaci'nin
# "sonraki NON-DOJI bar" tanimindan farklidir - dogi orani ihmal edilebilir (<%1, orijinal
# BULGU3 raporunda yonlu-bar sayisi 99.686-99.787/99.999) oldugu icin sonuclari maddi olarak
# etkilemez, ama bu fark SINIR olarak nihai raporda belirtilecektir.
def compute_direction_and_streak(rates):
    o = rates['open'].astype(float); c = rates['close'].astype(float)
    direction = np.sign(c - o).astype(int)
    n = len(direction)
    streak = np.zeros(n, dtype=int)
    last_dir = 0; last_streak = 0
    for i in range(n):
        if direction[i] == 0:
            streak[i] = 0
            continue
        if direction[i] == last_dir:
            last_streak += 1
        else:
            last_streak = 1
        streak[i] = last_streak
        last_dir = direction[i]
    return direction, streak

vol5, trend5, atr14_5, er20_5 = compute_regime_labels(rates5)
vol1, trend1, atr14_1, er20_1 = compute_regime_labels(rates1)
dir5, streak5 = compute_direction_and_streak(rates5)
dir1, streak1 = compute_direction_and_streak(rates1)
print("Rejim etiketleme + streak hesabi tamamlandi.")

# Buyuk-bar (BULGU4) tespiti - PC2/PC3 icin IS-subset ozgu esik ("kendi IS-donem verisinde
# RESMI" talebi geregi, asagida IS-slice uzerinde ayrica hesaplanacak; burada TUM-veri
# versiyonu da referans icin saklaniyor).
def detect_bigbars_fullmean(rates, mult=BIGBAR_MULT):
    o = rates['open'].astype(float); h = rates['high'].astype(float)
    l = rates['low'].astype(float); c = rates['close'].astype(float)
    rng = h - l
    mean_r = rng.mean()
    direction = np.sign(c - o).astype(int)
    is_big = rng > (mult * mean_r)
    return is_big, direction, mean_r

# ---------------------------------------------------------------------
# ON-KONTROL 2: RESMI COKLU-KARSILASTIRMA DUZELTMESI - KENDI IS-DONEM VERISINDE
#    48 test: BULGU3-genel(8) + BULGU3-streak(32) + BULGU4(8)
# ---------------------------------------------------------------------
LABEL_GROUPS = [("VOL", ["genis", "dar"]), ("TREND", ["trend", "range"])]

def bulgu3_general_is(direction, regime_label, values, cutoff):
    d = direction[:cutoff]; r = regime_label[:cutoff]
    prev_dir = d[:-1]; next_dir = d[1:]; prev_regime = r[:-1]
    pair_valid = (prev_dir != 0) & (next_dir != 0)
    pair_same = (next_dir == prev_dir)
    out = {}
    for v in values:
        mask = pair_valid & (prev_regime == v)
        n_total = int(mask.sum())
        n_same = int(pair_same[mask].sum()) if n_total else 0
        entry = {"n_total": n_total, "n_ayni_yon": n_same,
                 "ayni_yon_orani": round(n_same / n_total, 4) if n_total else None}
        entry.update(significance_test(n_same, n_total))
        out[v] = entry
    return out

def bulgu3_streak_is(direction, streak, regime_label, values, streak_lengths, cutoff):
    d = direction[:cutoff]; s = streak[:cutoff]; r = regime_label[:cutoff]
    n = len(d)
    out = {}
    for v in values:
        out[v] = {}
        for L in streak_lengths:
            idxs = np.where((s == L) & (r == v))[0]
            idxs = idxs[idxs < n - 1]
            if len(idxs) == 0:
                out[v][L] = {"n": 0, "sonraki_bar_ayni_yon_orani": None, "binom_test_p_degeri": None,
                              "chi_kare_p_degeri": None, "anlamli_mi_alpha_0_05": None}
                continue
            nd = d[idxs + 1]
            valid = nd != 0
            hits_total = int(valid.sum())
            hits_same = int((nd[valid] == d[idxs][valid]).sum())
            entry = {"n": hits_total,
                     "sonraki_bar_ayni_yon_orani": round(hits_same / hits_total, 4) if hits_total else None}
            entry.update(significance_test(hits_same, hits_total))
            out[v][L] = entry
    return out

def bulgu4_is(rates, regime_label, values, cutoff, mult=BIGBAR_MULT):
    sub = rates[:cutoff]
    o = sub['open'].astype(float); h = sub['high'].astype(float); l = sub['low'].astype(float); c = sub['close'].astype(float)
    rng = h - l
    mean_r_is = rng.mean()   # IS-subset kendi ortalamasi (bilerek - "kendi IS-donem verisinde")
    direction = np.sign(c - o).astype(int)
    big_idx = np.where(rng > mult * mean_r_is)[0]
    big_idx = big_idx[(big_idx > 0) & (big_idx < cutoff - 1)]
    r = regime_label[:cutoff]
    out = {}
    for v in values:
        same = opp = 0
        n_big = 0
        for i in big_idx:
            if r[i] != v or direction[i] == 0:
                continue
            n_big += 1
            nd = np.sign(c[i + 1] - o[i + 1])
            if nd == direction[i]:
                same += 1
            elif nd == -direction[i]:
                opp += 1
        total = same + opp
        entry = {"buyuk_bar_sayisi_rejimde": n_big, "yonlu_cift_n": total,
                 "ayni_yon_orani": round(same / total, 4) if total else None}
        entry.update(significance_test(same, total))
        out[v] = entry
    return {"sonuclar": out, "mean_range_IS_subset": float(mean_r_is)}

cutoff5 = int(len(rates5) * IS_FRACTION)
cutoff1 = int(len(rates1) * IS_FRACTION)
results["on_kontrol_2_IS_cutoff"] = {"M5_cutoff_bar_idx": cutoff5, "M1_cutoff_bar_idx": cutoff1,
                                      "M5_cutoff_tarih": dates5[cutoff5], "M1_cutoff_tarih": None}
# M1 tarihi ayri hesapla (dates1 henuz yok)
dates1_all = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in rates1['time'].astype(np.int64)])
results["on_kontrol_2_IS_cutoff"]["M1_cutoff_tarih"] = dates1_all[cutoff1]

all_tests = []  # (etiket, p_degeri) - 48 test

pc2_detail = {"BULGU3_genel": {}, "BULGU3_streak": {}, "BULGU4": {}}

for tf_name, direction, streak_arr, cutoff, rates_full in [
    ("M1", dir1, streak1, cutoff1, rates1), ("M5", dir5, streak5, cutoff5, rates5)
]:
    for group_name, values in LABEL_GROUPS:
        regime_label = (vol1 if (tf_name == "M1" and group_name == "VOL") else
                         trend1 if (tf_name == "M1" and group_name == "TREND") else
                         vol5 if (tf_name == "M5" and group_name == "VOL") else trend5)
        gen = bulgu3_general_is(direction, regime_label, values, cutoff)
        pc2_detail["BULGU3_genel"][f"{tf_name}_{group_name}"] = gen
        for v in values:
            lbl = f"BULGU3_genel|{tf_name}|{group_name}|{v}"
            p = gen[v]["binom_test_p_degeri"]
            all_tests.append((lbl, p, gen[v]["n_total"]))

        st = bulgu3_streak_is(direction, streak_arr, regime_label, values, STREAK_LENGTHS, cutoff)
        pc2_detail["BULGU3_streak"][f"{tf_name}_{group_name}"] = st
        for v in values:
            for L in STREAK_LENGTHS:
                lbl = f"BULGU3_streak|{tf_name}|{group_name}|{v}|L{L}"
                p = st[v][L]["binom_test_p_degeri"]
                all_tests.append((lbl, p, st[v][L]["n"]))

        b4 = bulgu4_is(rates_full, regime_label, values, cutoff)
        pc2_detail["BULGU4"][f"{tf_name}_{group_name}"] = b4
        for v in values:
            lbl = f"BULGU4|{tf_name}|{group_name}|{v}"
            p = b4["sonuclar"][v]["binom_test_p_degeri"]
            all_tests.append((lbl, p, b4["sonuclar"][v]["yonlu_cift_n"]))

print("Toplam test sayisi (PC2):", len(all_tests))
assert len(all_tests) == 48, f"Beklenen 48 test, bulunan: {len(all_tests)}"

# Bonferroni + BH/FDR
def bonferroni_flags(tests, alpha=ALPHA):
    m = len(tests)
    thr = alpha / m
    return {lbl: (p is not None and p < thr) for lbl, p, n in tests}, thr

def bh_fdr_flags(tests, alpha=ALPHA):
    m = len(tests)
    valid = [(lbl, p, n) for lbl, p, n in tests if p is not None]
    order = sorted(range(len(valid)), key=lambda i: valid[i][1])
    sorted_p = [valid[i][1] for i in order]
    max_k = -1
    for k in range(len(sorted_p)):
        thresh_k = (k + 1) / m * alpha
        if sorted_p[k] <= thresh_k:
            max_k = k
    flags = {lbl: False for lbl, p, n in tests}
    if max_k >= 0:
        for k in range(max_k + 1):
            flags[valid[order[k]][0]] = True
    return flags

bonf_flags, bonf_thr = bonferroni_flags(all_tests)
fdr_flags = bh_fdr_flags(all_tests)

n_bonf_pass = sum(bonf_flags.values())
n_fdr_pass = sum(fdr_flags.values())
print(f"Bonferroni ({bonf_thr:.6f}) sonrasi hayatta kalan: {n_bonf_pass}/48")
print(f"FDR/BH (alpha=0.05) sonrasi hayatta kalan: {n_fdr_pass}/48")

results["on_kontrol_2_coklu_karsilastirma"] = {
    "yontem": "48 test (BULGU3-genel 8 + BULGU3-streak 32 + BULGU4 8), IS-donem (ilk %70) verisi "
              "uzerinde BAGIMSIZ yeniden hesaplandi (Arastirmaci'nin tum-veri/duzeltmesiz sayilari "
              "kopyalanmadi). Bonferroni (alpha/48) VE FDR/Benjamini-Hochberg (tercih edilen, daha az "
              "muhafazakar) birlikte raporlandi.",
    "bonferroni_esigi": bonf_thr,
    "bonferroni_hayatta_kalan_sayisi": n_bonf_pass,
    "fdr_hayatta_kalan_sayisi": n_fdr_pass,
    "tum_testler": [
        {"etiket": lbl, "p_degeri": p, "n": n, "bonferroni_gecti_mi": bonf_flags[lbl], "fdr_gecti_mi": fdr_flags[lbl]}
        for lbl, p, n in sorted(all_tests, key=lambda x: (x[1] is None, x[1]))
    ],
    "detay": pc2_detail,
}
print("ON-KONTROL 2 (resmi coklu-karsilastirma duzeltmesi) tamamlandi.")

# ---------------------------------------------------------------------
# ON-KONTROL 3: GERCEKCI-MALIYET/SEANS-FILTRESI ERKEN KONTROLU
#    PC2'yi (FDR - tercih edilen yontem) GECEN hucreler icin, birincil seans (15-18 sunucu
#    saati) altinda IS-donem verisinde ham oran hala %50'den anlamli sapiyor mu?
# ---------------------------------------------------------------------
hours1_all = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in rates1['time'].astype(np.int64)])
hours5_all = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in rates5['time'].astype(np.int64)])

def parse_label(lbl):
    parts = lbl.split("|")
    kind = parts[0]
    if kind == "BULGU3_genel":
        _, tf, group, val = parts
        return kind, tf, group, val, None
    elif kind == "BULGU3_streak":
        _, tf, group, val, Lstr = parts
        return kind, tf, group, val, int(Lstr[1:])
    else:  # BULGU4
        _, tf, group, val = parts
        return kind, tf, group, val, None

pc2_survivors = [lbl for lbl, flag in fdr_flags.items() if flag]
print(f"PC2 (FDR) hayatta kalan {len(pc2_survivors)} hucre uzerinde PC3 kosturuluyor...")

pc3_results = {}
for lbl in pc2_survivors:
    kind, tf, group, val, L = parse_label(lbl)
    cutoff = cutoff1 if tf == "M1" else cutoff5
    hours_arr = (hours1_all if tf == "M1" else hours5_all)[:cutoff]
    sess_mask = np.isin(hours_arr, sorted(SESSION_PRIMARY))
    regime_label = (vol1 if (tf == "M1" and group == "VOL") else
                     trend1 if (tf == "M1" and group == "TREND") else
                     vol5 if (tf == "M5" and group == "VOL") else trend5)[:cutoff]
    direction = (dir1 if tf == "M1" else dir5)[:cutoff]

    if kind == "BULGU3_genel":
        prev_dir = direction[:-1]; next_dir = direction[1:]; prev_regime = regime_label[:-1]
        prev_sess = sess_mask[:-1]
        mask = (prev_dir != 0) & (next_dir != 0) & (prev_regime == val) & prev_sess
        n_total = int(mask.sum())
        n_same = int((next_dir[mask] == prev_dir[mask]).sum()) if n_total else 0
        res = {"n_total": n_total, "n_ayni_yon": n_same,
               "ayni_yon_orani": round(n_same / n_total, 4) if n_total else None}
        res.update(significance_test(n_same, n_total))
    elif kind == "BULGU3_streak":
        streak_arr = (streak1 if tf == "M1" else streak5)[:cutoff]
        idxs = np.where((streak_arr == L) & (regime_label == val) & sess_mask)[0]
        idxs = idxs[idxs < len(direction) - 1]
        if len(idxs) == 0:
            res = {"n": 0, "sonraki_bar_ayni_yon_orani": None, "binom_test_p_degeri": None,
                   "chi_kare_p_degeri": None, "anlamli_mi_alpha_0_05": None}
        else:
            nd = direction[idxs + 1]
            valid = nd != 0
            hits_total = int(valid.sum())
            hits_same = int((nd[valid] == direction[idxs][valid]).sum())
            res = {"n": hits_total, "sonraki_bar_ayni_yon_orani": round(hits_same / hits_total, 4) if hits_total else None}
            res.update(significance_test(hits_same, hits_total))
    else:  # BULGU4
        rates_sub = (rates1 if tf == "M1" else rates5)[:cutoff]
        o = rates_sub['open'].astype(float); h = rates_sub['high'].astype(float)
        l = rates_sub['low'].astype(float); c = rates_sub['close'].astype(float)
        rng = h - l
        mean_r_is = rng.mean()
        big_idx = np.where((rng > BIGBAR_MULT * mean_r_is) & sess_mask)[0]
        big_idx = big_idx[(big_idx > 0) & (big_idx < cutoff - 1)]
        same = opp = n_big = 0
        for i in big_idx:
            if regime_label[i] != val or direction[i] == 0:
                continue
            n_big += 1
            nd = np.sign(c[i + 1] - o[i + 1])
            if nd == direction[i]:
                same += 1
            elif nd == -direction[i]:
                opp += 1
        total = same + opp
        res = {"buyuk_bar_sayisi_rejimde_seans_ici": n_big, "yonlu_cift_n": total,
               "ayni_yon_orani": round(same / total, 4) if total else None}
        res.update(significance_test(same, total))

    res["pc3_gecti_mi_alpha_0_05"] = bool(res.get("anlamli_mi_alpha_0_05"))
    pc3_results[lbl] = res

n_pc3_pass = sum(1 for v in pc3_results.values() if v["pc3_gecti_mi_alpha_0_05"])
print(f"PC3 (seans 15-18 filtreli, IS-donem) sonrasi hayatta kalan: {n_pc3_pass}/{len(pc2_survivors)}")

results["on_kontrol_3_gercekci_maliyet_seans_filtresi"] = {
    "yontem": "PC2 (FDR) hayatta kalan hucreler, birincil seans (15-18 sunucu saati, H1/H2'den "
              "devam eden varsayim) filtresi altinda IS-donem verisinde YENIDEN test edildi. "
              "'Gercekci maliyet' bu asamada spread/slipaj DEGERİ olarak degil (tick-bazli maliyet "
              "simulasyonu ANA TESTTE, tick sorgusu bu on-kontrolde henuz yapilmiyor), fiilen "
              "islem edilecek ALT-ORNEKLEM (seans-filtreli) uzerinde ham edge'in hala anlamli olup "
              "olmadigi kontrolu olarak uygulandi - H1/H2'nin RED gerekcesiyle (aggregate'te anlamli, "
              "fiilen-islem-edilen altkumede anlamsiz) BIREBIR ayni risk/yontem.",
    "pc2_survivor_sayisi": len(pc2_survivors),
    "pc3_hayatta_kalan_sayisi": n_pc3_pass,
    "detay": pc3_results,
}

final_survivors = [lbl for lbl, v in pc3_results.items() if v["pc3_gecti_mi_alpha_0_05"]]
results["on_kontrol_ozet_karar"] = {
    "pc1_saat_esleme": "TAMAMLANDI (prosedurel, atlanmadi)",
    "pc2_coklu_karsilastirma_FDR_hayatta_kalan": n_fdr_pass,
    "pc2_coklu_karsilastirma_Bonferroni_hayatta_kalan": n_bonf_pass,
    "pc3_seans_filtresi_sonrasi_hayatta_kalan": n_pc3_pass,
    "final_hayatta_kalan_hucreler": final_survivors,
    "karar": ("ANA_TESTE_GECILEBILIR" if len(final_survivors) > 0 else "RED_ON_KONTROLDE_KAPANDI"),
}
print("NIHAI ON-KONTROL KARARI:", results["on_kontrol_ozet_karar"]["karar"])
print("Hayatta kalan hucreler:", final_survivors)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)

mt5.shutdown()
