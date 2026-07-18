# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping, Strateji Ailesi Plani ADIM 0 - ON-TARAMA
Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), GOLD sembolu, sunucu saati (GMT+3).
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz.
Sadece ham OHLCV veri MT5'ten cekilir. Onceki Justin scriptleriyle (research_scalping.py)
ayni genel kod-yapisi (ayni proje ici, izolasyon ihlali degil) kullanilmistir.

Kapsam: A-Taramasi (otokorelasyon, varyans-orani, N-bar devam orani, MA-durum devam
dogrulugu, breakout-notu, S1 maliyet-orani) + J-Taramasi (saat/gun getiri profili,
coklu-test duzeltmeli).
"""
import MetaTrader5 as mt5
import numpy as np
from datetime import datetime
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
point = info.point

TFS = {
    "M15": (mt5.TIMEFRAME_M15, 15),
    "H1": (mt5.TIMEFRAME_H1, 60),
    "H4": (mt5.TIMEFRAME_H4, 240),
}

results = {"symbol_info": {"point": point, "digits": info.digits,
                            "contract_size": info.trade_contract_size}}

raw = {}
for tf_name, (tf_const, bar_min) in TFS.items():
    rates = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)
    raw[tf_name] = rates
    t0 = datetime.utcfromtimestamp(rates[0]['time'])
    t1 = datetime.utcfromtimestamp(rates[-1]['time'])
    results.setdefault("veri_araligi", {})[tf_name] = {
        "n_bar": int(len(rates)), "baslangic": str(t0), "bitis": str(t1)
    }
    print(tf_name, "n=", len(rates), t0, "->", t1)

# ============================================================
# A-TARAMASI
# ============================================================

def autocorr_lag(x, lag):
    a = x[:-lag]
    b = x[lag:]
    if len(a) < 30:
        return None
    c = np.corrcoef(a, b)[0, 1]
    n = len(a)
    se = 1.0 / np.sqrt(n)
    z = c / se
    return {"lag": lag, "n": int(n), "coef": round(float(c), 4),
            "se_approx": round(float(se), 4), "z_approx": round(float(z), 2),
            "anlamli_2sigma": bool(abs(z) > 1.96)}


def variance_ratio(returns, q):
    n = len(returns)
    n_blocks = n // q
    if n_blocks < 50:
        return None
    trimmed = returns[:n_blocks * q]
    block_sums = trimmed.reshape(n_blocks, q).sum(axis=1)
    var_q = block_sums.var(ddof=1)
    var_1 = returns.var(ddof=1)
    vr = var_q / (q * var_1)
    se = np.sqrt(2 * (2 * q - 1) * (q - 1) / (3 * q * n))
    z = (vr - 1) / se
    return {"q": q, "n_return_obs": int(n), "n_blocks": int(n_blocks),
            "VR": round(float(vr), 4), "se_approx": round(float(se), 4),
            "z_approx": round(float(z), 2), "anlamli_2sigma": bool(abs(z) > 1.96)}


def direction_series(rates):
    d = np.sign(rates['close'] - rates['open'])
    return d


def streak_continuation(rates, streak_lens=(2, 3, 4, 5, 8), fwd_list=(1, 2, 3)):
    d = direction_series(rates)
    nz_mask = d != 0
    d = d[nz_mask]
    n_total = len(d)
    p_up = float((d == 1).sum()) / n_total if n_total else None
    null_same = p_up ** 2 + (1 - p_up) ** 2 if p_up is not None else None
    out = {"n_bar_yonlu": int(n_total), "p_up_empirik": round(p_up, 4) if p_up else None,
           "null_ayni_yon_orani_bagimsizlik": round(null_same, 4) if null_same else None,
           "streak_sonrasi": {}}
    for L in streak_lens:
        # streak sonu indeksleri (d dizisinde) - son L bar ayni yonde
        streak_end_idx = []
        cur = 1
        for i in range(1, n_total):
            if d[i] == d[i - 1]:
                cur += 1
            else:
                cur = 1
            if cur == L:
                streak_end_idx.append(i)
        streak_end_idx = np.array(streak_end_idx, dtype=int)
        entry = {"n_streak_olay": int(len(streak_end_idx))}
        for M in fwd_list:
            valid = streak_end_idx[streak_end_idx + M < n_total]
            if len(valid) == 0:
                entry[f"sonraki_{M}_bar_ayni_yon_orani"] = None
                continue
            streak_dir = d[valid]
            fwd_dir = d[valid + M]
            same = float((fwd_dir == streak_dir).mean())
            entry[f"sonraki_{M}_bar_ayni_yon_orani"] = round(same, 4)
            entry[f"sonraki_{M}_bar_n"] = int(len(valid))
        out["streak_sonrasi"][L] = entry
    return out


def ma_state_forward_accuracy(rates, fast=10, slow=30, fwd_list=(1, 2, 4, 8)):
    closes = rates['close'].astype(float)
    n = len(closes)
    if n < slow + max(fwd_list) + 10:
        return None

    def sma(x, w):
        c = np.cumsum(np.insert(x, 0, 0))
        s = (c[w:] - c[:-w]) / w
        return np.concatenate([np.full(w - 1, np.nan), s])

    fast_ma = sma(closes, fast)
    slow_ma = sma(closes, slow)
    bull = fast_ma > slow_ma
    bear = fast_ma < slow_ma
    valid = ~np.isnan(fast_ma) & ~np.isnan(slow_ma)

    p_up_overall = {}
    out = {"fast": fast, "slow": slow, "fwd": {}}
    for M in fwd_list:
        idx = np.where(valid)[0]
        idx = idx[idx + M < n]
        fwd_up = (closes[idx + M] - closes[idx]) > 0
        fwd_down = (closes[idx + M] - closes[idx]) < 0
        is_bull = bull[idx]
        is_bear = bear[idx]
        # bull durumunda ileri M bar sonra fiyat yukarida mi
        bull_n = int(is_bull.sum())
        bull_acc = float(fwd_up[is_bull].mean()) if bull_n > 0 else None
        bear_n = int(is_bear.sum())
        bear_acc = float(fwd_down[is_bear].mean()) if bear_n > 0 else None
        overall_up_rate = float(fwd_up.mean())
        out["fwd"][M] = {
            "bull_durum_n": bull_n,
            "bull_durum_ileri_yukari_orani": round(bull_acc, 4) if bull_acc is not None else None,
            "bear_durum_n": bear_n,
            "bear_durum_ileri_asagi_orani": round(bear_acc, 4) if bear_acc is not None else None,
            "kosulsuz_ileri_yukari_orani_karsilastirma": round(overall_up_rate, 4),
        }
    return out


def donchian_breakout_note(rates, window=20, fwd_list=(1, 2, 4)):
    closes = rates['close'].astype(float)
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    n = len(closes)
    if n < window + max(fwd_list) + 10:
        return None
    roll_max = np.array([highs[max(0, i - window):i].max() if i >= window else np.nan
                          for i in range(n)])
    roll_min = np.array([lows[max(0, i - window):i].min() if i >= window else np.nan
                          for i in range(n)])
    up_break = closes > roll_max
    down_break = closes < roll_min
    out = {"window": window, "fwd": {}}
    for M in fwd_list:
        idx_up = np.where(up_break)[0]
        idx_up = idx_up[idx_up + M < n]
        idx_dn = np.where(down_break)[0]
        idx_dn = idx_dn[idx_dn + M < n]
        up_cont = float(((closes[idx_up + M] - closes[idx_up]) > 0).mean()) if len(idx_up) else None
        dn_cont = float(((closes[idx_dn + M] - closes[idx_dn]) < 0).mean()) if len(idx_dn) else None
        out["fwd"][M] = {
            "yukari_kirilim_n": int(len(idx_up)), "yukari_kirilim_devam_orani": round(up_cont, 4) if up_cont else None,
            "asagi_kirilim_n": int(len(idx_dn)), "asagi_kirilim_devam_orani": round(dn_cont, 4) if dn_cont else None,
        }
    return out


def atr_points(rates, window=14):
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    closes = rates['close'].astype(float)
    prev_close = np.roll(closes, 1)
    prev_close[0] = closes[0]
    tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
    atr = np.convolve(tr, np.ones(window) / window, mode='valid')
    return atr / point  # points


def s1_cost_check(rates, tf_name, bar_min, n_list=(1, 2, 4, 8, 16, 32)):
    closes = rates['close'].astype(float)
    spread_pts = rates['spread'].astype(float)
    atr_pts = atr_points(rates, 14)
    atr_median = float(np.median(atr_pts))
    spread_median = float(np.median(spread_pts))
    slippage_est = 0.037 * atr_median  # S1 standardi kalibrasyon notu (Justin'in kendi H2 kesitinden)
    cost_pts = spread_median + slippage_est
    cost_pct_of_atr = cost_pts / atr_median * 100 if atr_median else None

    n = len(closes)
    horizon_table = {}
    for N in n_list:
        if N >= n:
            continue
        fwd_move = np.abs(closes[N:] - closes[:-N]) / point
        med = float(np.median(fwd_move))
        p75 = float(np.percentile(fwd_move, 75))
        ratio_med = med / cost_pts if cost_pts else None
        ratio_p75 = p75 / cost_pts if cost_pts else None
        horizon_table[N] = {
            "gercek_sure_dk": N * bar_min,
            "ileri_hareket_median_pts": round(med, 1),
            "ileri_hareket_p75_pts": round(p75, 1),
            "oran_median_hedef_maliyet": round(ratio_med, 2) if ratio_med else None,
            "oran_p75_hedef_maliyet": round(ratio_p75, 2) if ratio_p75 else None,
        }
    return {
        "spread_median_pts": round(spread_median, 2),
        "atr14_median_pts": round(atr_median, 2),
        "slippage_tahmini_pts (atr*0.037)": round(slippage_est, 2),
        "toplam_maliyet_pts": round(cost_pts, 2),
        "maliyet_pct_of_atr": round(cost_pct_of_atr, 2) if cost_pct_of_atr else None,
        "ufuk_tablosu": horizon_table,
    }


for tf_name, (tf_const, bar_min) in TFS.items():
    rates = raw[tf_name]
    closes = rates['close'].astype(float)
    log_ret = np.diff(np.log(closes))

    ac = {}
    for lag in range(1, 11):
        r = autocorr_lag(log_ret, lag)
        if r:
            ac[lag] = r
    results.setdefault("otokorelasyon", {})[tf_name] = ac

    vr = {}
    for q in (2, 4, 8, 16):
        r = variance_ratio(log_ret, q)
        if r:
            vr[q] = r
    results.setdefault("varyans_orani", {})[tf_name] = vr

    results.setdefault("n_bar_devam_orani", {})[tf_name] = streak_continuation(rates)
    results.setdefault("ma_durum_ileri_dogruluk", {})[tf_name] = ma_state_forward_accuracy(rates)
    results.setdefault("donchian_kirilim_notu", {})[tf_name] = donchian_breakout_note(rates)
    results.setdefault("s1_maliyet_kontrolu", {})[tf_name] = s1_cost_check(rates, tf_name, bar_min)

# ============================================================
# J-TARAMASI (saat / gun-ici, coklu-test duzeltmeli) - H1 verisi kullanilir
# ============================================================
h1 = raw["H1"]
h1_closes = h1['close'].astype(float)
h1_opens = h1['open'].astype(float)
h1_times = h1['time']
h1_logret_bar = np.log(h1_closes / h1_opens)  # bar-ici getiri (open->close), saat etiketi bar'in kendi saati

hours = np.array([datetime.utcfromtimestamp(t).hour for t in h1_times])
weekdays = np.array([datetime.utcfromtimestamp(t).weekday() for t in h1_times])  # 0=Pazartesi

def one_sample_t(x):
    n = len(x)
    if n < 30:
        return None
    mean = float(np.mean(x))
    std = float(np.std(x, ddof=1))
    se = std / np.sqrt(n)
    t = mean / se if se > 0 else 0.0
    # normal yaklasimla p-deger (n buyuk oldugu icin)
    from scipy import stats
    p = float(2 * (1 - stats.norm.cdf(abs(t))))
    return {"n": int(n), "mean_logret": mean, "t_approx": round(t, 3), "p_ham": p}

hour_tests = {}
for h in range(24):
    mask = hours == h
    r = one_sample_t(h1_logret_bar[mask])
    if r:
        hour_tests[h] = r
n_hour_tests = len(hour_tests)
alpha_hour = 0.05 / n_hour_tests if n_hour_tests else None
for h, r in hour_tests.items():
    r["p_bonferroni_esik"] = round(alpha_hour, 5)
    r["anlamli_duzeltme_sonrasi"] = bool(r["p_ham"] < alpha_hour)

day_tests = {}
day_names = {0: "Pazartesi", 1: "Sali", 2: "Carsamba", 3: "Persembe", 4: "Cuma", 5: "Cumartesi", 6: "Pazar"}
for wd in range(7):
    mask = weekdays == wd
    if mask.sum() < 30:
        continue
    r = one_sample_t(h1_logret_bar[mask])
    if r:
        day_tests[day_names[wd]] = r
n_day_tests = len(day_tests)
alpha_day = 0.05 / n_day_tests if n_day_tests else None
for d, r in day_tests.items():
    r["p_bonferroni_esik"] = round(alpha_day, 5)
    r["anlamli_duzeltme_sonrasi"] = bool(r["p_ham"] < alpha_day)

# Session (yaklasik, sunucu saati GMT+3 - DST dogrulamasi bu asamada YAPILMADI, bkz. sinirlamalar)
SESSIONS = {
    "Asya (yaklasik 03-10)": range(3, 10),
    "Avrupa (yaklasik 10-16)": range(10, 16),
    "ABD (yaklasik 16-23)": range(16, 23),
    "Dusuk-likidite/rollover (23-03)": list(range(23, 24)) + list(range(0, 3)),
}
session_tests = {}
for sname, hrs in SESSIONS.items():
    mask = np.isin(hours, list(hrs))
    r = one_sample_t(h1_logret_bar[mask])
    if r:
        session_tests[sname] = r
n_session_tests = len(session_tests)
alpha_session = 0.05 / n_session_tests if n_session_tests else None
for s, r in session_tests.items():
    r["p_bonferroni_esik"] = round(alpha_session, 5)
    r["anlamli_duzeltme_sonrasi"] = bool(r["p_ham"] < alpha_session)

results["j_taramasi"] = {
    "saat_bazinda": hour_tests,
    "gun_bazinda": day_tests,
    "session_bazinda": session_tests,
    "coklu_test_notu": {
        "saat_ailesi_n_test": n_hour_tests, "saat_ailesi_bonferroni_alpha": round(alpha_hour, 5) if alpha_hour else None,
        "gun_ailesi_n_test": n_day_tests, "gun_ailesi_bonferroni_alpha": round(alpha_day, 5) if alpha_day else None,
        "session_ailesi_n_test": n_session_tests, "session_ailesi_bonferroni_alpha": round(alpha_session, 5) if alpha_session else None,
    }
}

with open(r"C:\MilaYatirim\Justin\arastirmaci_gold_scalping_adim0_tarama_output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI. JSON yazildi.")
mt5.shutdown()
