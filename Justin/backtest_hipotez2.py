# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - HIPOTEZ 2 dogrulama
Buyuk-Bar Ters-Yon (Fade) Kisa Vadeli Sinyal, M5 (ana) + M1 (yalniz istatistiksel
anlamlilik bagimsiz dogrulamasi icin), GOLD

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi
okumaz/kullanmaz (signal.json, milagold_trades.json, lisa_performance.json,
positions_status.json, stratejici_gold_gecmis_calisma.md vb.). Yalniz MT5'ten
dogrudan cekilen ham GOLD M5/M1 verisi ve GOLD tick verisi kullanilir.
MilaGold'un sabit 5$/3$/5$/8$ SL/TP yapisi veya 0,01 lot kurallari HICBIR
SEKILDE kullanilmadi; SL/TP tamamen ATR-bazli/dinamik olarak Stratejist'in
HIPOTEZ 2 tasarimina gore uygulanmistir.

Kapsam: Stratejist raporu (20260711 rafine, HIPOTEZ 2 bolumu satir 60-89 +
10 Temmuz orijinal rapor HIPOTEZ 2 bolumu satir 91-130) + Backtest Muhendisi
gorev tanimi (gorev_backtest_muhendisi_justin_gold_scalping_hipotez2.md,
Kapsam maddeleri 1-7).

DUZELTME NOTU (2026-07-11, bu tur): Onceki tur (gorev_id backtest_muhendisi_
20260710_2021) get_tick_quote() fonksiyonunda bir veri-yoklugu artefaktini
"gercek slipaj" olarak yanlis raporluyordu - bkz. get_tick_quote() yorumu ve
nihai rapordaki "Slipaj/Tick-Eslesme Duzeltme Notu" bolumu. Script'in geri
kalani (saat esleme, istatistiksel anlamlilik, ATR, senaryo/tarama yapisi)
onceki turdeki HALIYLE korunmustur - yalniz maliyet-hesaplama katmani (bolum 4)
duzeltildi.
"""
import json
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date
from collections import defaultdict
from scipy import stats

# ---------------------------------------------------------------------
# SABITLER (Stratejist'in belirledigi/onerdigi degerler - degistirilmedi;
# esik carpani ve teyit ufku GENIS TARANMAZ - gorev Kapsam madde 6, ZORUNLU)
# ---------------------------------------------------------------------
SYMBOL = "GOLD"
RANGE_WINDOW = 20          # "buyuk bar" icin ortalama range penceresi (Stratejist: "orn. 20 bar")
BIGBAR_MULT = 1.5          # esik carpani - BULGU4 ile ayni, FIXED (genis taranmiyor)
ATR_PERIOD = 14            # ATR(14, M5) - SL/TP icin
ATR_FRACTION = 0.5         # "dar mesafe" (Stratejist notu) -> TP=SL=0.5 x ATR(14), 1:1 RR
RR_RATIO = 1.0             # TP:SL = 1:1 (Stratejist RR belirtmedi, Hipotez1 baseline ile tutarli)
CONFIRM_HORIZONS = [1, 2, 3]     # teyit ufku: t+1 (teyitsiz) / t+2 (1-bar teyit) / t+3 (2-bar teyit)
TIME_EXIT_SCAN = [1, 2, 3]       # N-bar zaman-cikis dar tarama (gorev Kapsam madde 3)
MAX_HOLD_BARS_ATR_ONLY = 20      # yalniz-ATR exit icin muhendislik ust siniri (scalp sinyali,
                                  # ~100 dk M5'te; Stratejist sinir belirtmedigi icin eklendi,
                                  # ayrica onaylanmali - Hipotez1'deki 50-bar sinirinin ayni
                                  # mantikla kucuk versiyonu, cunku bu daha kisa vadeli bir sinyal)
SESSION_PRIMARY = set(range(15, 19))   # sunucu saati 15-18 (Stratejist onerisi, BULGU2 dar/istikrarli spread)
IS_FRACTION = 0.70          # klasik IS/OOS ayrimi
WF_FOLDS = 6                # walk-forward rolling pencere sayisi (Hipotez1 ile ayni titizlik)

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_hipotez2_output.json"

# ---------------------------------------------------------------------
# MT5 BAGLANTISI VE HAM VERI (M5 ana, M1 yalniz anlamlilik dogrulamasi icin)
# ---------------------------------------------------------------------
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size

rates5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 99999)
n = len(rates5)
t = rates5['time'].astype(np.int64)
o = rates5['open'].astype(float)
h = rates5['high'].astype(float)
l = rates5['low'].astype(float)
c = rates5['close'].astype(float)
spr = rates5['spread'].astype(float)  # yalniz referans/karsilastirma amacli (bar-kapanis spread alani)

hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])

rates1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 99999)
n1 = len(rates1)
t1 = rates1['time'].astype(np.int64)
o1 = rates1['open'].astype(float)
h1 = rates1['high'].astype(float)
l1 = rates1['low'].astype(float)
c1 = rates1['close'].astype(float)

results = {}
results["veri_ozeti"] = {
    "M5": {
        "toplam_bar": int(n),
        "baslangic": str(datetime.fromtimestamp(int(t[0]), tz=timezone.utc)),
        "bitis": str(datetime.fromtimestamp(int(t[-1]), tz=timezone.utc)),
    },
    "M1": {
        "toplam_bar": int(n1),
        "baslangic": str(datetime.fromtimestamp(int(t1[0]), tz=timezone.utc)),
        "bitis": str(datetime.fromtimestamp(int(t1[-1]), tz=timezone.utc)),
    },
    "point": POINT, "contract_size": CONTRACT_SIZE,
}

print("Veri cekildi. M5 bar:", n, "M1 bar:", n1)

# ---------------------------------------------------------------------
# 0) SAAT ESLEME DOGRULAMASI (gorev Kapsam madde 1 - ZORUNLU, ONCE yapilmali)
#    Ayni bagimsiz iki kontrol Hipotez 1 turunde kullanilan yontemle tekrarlaniyor
#    (bu turde ayrica/bagimsiz calistirildi, eski sonuc kopyalanmadi).
# ---------------------------------------------------------------------
tick_now = mt5.symbol_info_tick(SYMBOL)
epoch_as_utc = datetime.fromtimestamp(tick_now.time, tz=timezone.utc).replace(tzinfo=None)
vps_local_now = datetime.now()
diff_seconds = abs((epoch_as_utc - vps_local_now).total_seconds())

gap_threshold_sec = 23 * 3600  # 23 saatten uzun bar-arasi bosluk = hafta sonu geciși
gaps = []
for i in range(1, n):
    dt = t[i] - t[i - 1]
    if dt > gap_threshold_sec:
        gaps.append({
            "friday_close_utc_epoch_hour": int(hours[i - 1]),
            "friday_close_date": dates[i - 1],
            "sunday_open_utc_epoch_hour": int(hours[i]),
            "sunday_open_date": dates[i],
        })

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

dst_check = []
for tr in dst_transitions:
    before, after = hour_mode_window(gaps, tr)
    dst_check.append({
        "gecis_tarihi": tr,
        "oncesi_cuma_kapanis_saatleri": before,
        "sonrasi_cuma_kapanis_saatleri": after,
        "kayma_tespit_edildi_mi": (
            bool(before) and bool(after) and
            (max(set(before), key=before.count) != max(set(after), key=after.count))
        ),
    })

results["saat_esleme_dogrulama"] = {
    "canli_capraz_kontrol": {"epoch_utc_okuma": str(epoch_as_utc), "vps_yerel_simdi": str(vps_local_now), "fark_saniye": diff_seconds},
    "hafta_sonu_gecis_DST_kontrolu": dst_check,
    "toplam_hafta_sonu_gecis_sayisi": len(gaps),
}
print("Saat esleme kontrolu tamamlandi.")
for d in dst_check:
    print(d)

# ---------------------------------------------------------------------
# 1) BUYUK-BAR TESPITI (M5 ve M1, causal/nedensel - ileri-bakis yok)
#    avg_range[i] = onceki RANGE_WINDOW barin (i-RANGE_WINDOW..i-1) ortalama range'i
#    (bar i'nin kendisi HARIC - o anda henuz olusmamis kabul edilir).
# ---------------------------------------------------------------------
def detect_bigbars(oo, hh, ll, cc, window, mult):
    nn = len(cc)
    rng = hh - ll
    avg_rng = np.full(nn, np.nan)
    cum = np.cumsum(np.insert(rng, 0, 0.0))
    for i in range(window, nn):
        avg_rng[i] = (cum[i] - cum[i - window]) / window
    is_big = np.zeros(nn, dtype=bool)
    fade_dir = np.zeros(nn, dtype=int)  # +1: buyuk bar asagi kapandi -> fade LONG ; -1: buyuk bar yukari kapandi -> fade SHORT
    for i in range(window, nn):
        if np.isnan(avg_rng[i]) or avg_rng[i] <= 0:
            continue
        if rng[i] > mult * avg_rng[i]:
            if cc[i] > oo[i]:
                is_big[i] = True
                fade_dir[i] = -1
            elif cc[i] < oo[i]:
                is_big[i] = True
                fade_dir[i] = 1
            # esit (dogi buyuk bar) -> yon belirsiz, sinyal uretilmez
    return is_big, fade_dir, avg_rng

is_big5, fade_dir5, avg_rng5 = detect_bigbars(o, h, l, c, RANGE_WINDOW, BIGBAR_MULT)
is_big1, fade_dir1, avg_rng1 = detect_bigbars(o1, h1, l1, c1, RANGE_WINDOW, BIGBAR_MULT)
print("Buyuk bar tespiti tamamlandi. M5:", int(is_big5.sum()), "M1:", int(is_big1.sum()))

# ---------------------------------------------------------------------
# 2) ISTATISTIKSEL ANLAMLILIK (gorev Kapsam madde 2 - ZORUNLU, ONCE yapilmali)
#    BULGU4'un bagimsiz dogrulamasi: buyuk bar sonrasi bir sonraki barin TERS
#    yonde kapanma orani, binom test + ki-kare uygunluk testi ile 0,50'den
#    anlamli sapiyor mu? (yalniz yonlu ciftler - sonraki bar da doji ise haric)
# ---------------------------------------------------------------------
def reversal_significance(oo, cc, is_big, fade_dir, label):
    nn = len(is_big)
    n_total = 0
    n_reversal = 0
    for i in range(nn - 1):
        if not is_big[i]:
            continue
        j = i + 1
        if cc[j] == oo[j]:
            continue  # sonraki bar doji -> yonlu cift degil, BULGU4 ile tutarli disarida birakildi
        n_total += 1
        next_up = cc[j] > oo[j]
        if fade_dir[i] == 1:      # buyuk bar asagi kapandi -> "ters yon" = sonraki bar YUKARI
            is_reversal = next_up
        else:                      # fade_dir==-1, buyuk bar yukari kapandi -> "ters yon" = sonraki bar ASAGI
            is_reversal = not next_up
        if is_reversal:
            n_reversal += 1
    if n_total == 0:
        return {"label": label, "n_total": 0, "n_reversal": 0, "reversal_orani": None}
    binom = stats.binomtest(n_reversal, n_total, 0.5, alternative='two-sided')
    expected = n_total * 0.5
    chi2_stat = ((n_reversal - expected) ** 2 / expected) + (((n_total - n_reversal) - expected) ** 2 / expected)
    chi2_p = float(1 - stats.chi2.cdf(chi2_stat, df=1))
    return {
        "label": label,
        "n_total_yonlu_cift": int(n_total),
        "n_reversal": int(n_reversal),
        "reversal_orani": round(n_reversal / n_total, 4),
        "binom_test_p_degeri": float(binom.pvalue),
        "chi_kare_istatistigi": round(chi2_stat, 3),
        "chi_kare_p_degeri": round(chi2_p, 6),
        "anlamli_mi_alpha_0_05": bool(binom.pvalue < 0.05),
    }

sig_m5_global = reversal_significance(o, c, is_big5, fade_dir5, "M5_tum_veri_seans_filtresiz")
sig_m1_global = reversal_significance(o1, c1, is_big1, fade_dir1, "M1_tum_veri_seans_filtresiz")

# Ayrica ISLENEN (seans 15-18) alt-orneklemde de anlamlilik ayri raporlaniyor -
# nihai islem edilen populasyon bu oldugu icin, global sonuc kadar onemli.
sess_mask5 = np.isin(hours, sorted(SESSION_PRIMARY))
is_big5_sess = is_big5 & sess_mask5
sig_m5_session = reversal_significance(o, c, is_big5_sess, fade_dir5, "M5_seans_15_18_alt_ornek")

results["istatistiksel_anlamlilik"] = {
    "yontem": "binom test (iki-yonlu, H0: p=0.5) + ki-kare uygunluk testi (df=1), BULGU4'un bagimsiz dogrulamasi",
    "M5_global": sig_m5_global,
    "M1_global": sig_m1_global,
    "M5_seans_15_18_alt_ornek": sig_m5_session,
}
print("Istatistiksel anlamlilik testleri tamamlandi.")
print(sig_m5_global)
print(sig_m1_global)
print(sig_m5_session)

# ---------------------------------------------------------------------
# 3) ATR(14, M5) - SL/TP icin (causal)
# ---------------------------------------------------------------------
def compute_atr(hh, ll, cc, period):
    nn = len(cc)
    tr = np.full(nn, np.nan)
    tr[0] = hh[0] - ll[0]
    for i in range(1, nn):
        tr[i] = max(hh[i] - ll[i], abs(hh[i] - cc[i - 1]), abs(ll[i] - cc[i - 1]))
    atr = np.full(nn, np.nan)
    for i in range(period - 1, nn):
        atr[i] = tr[i - period + 1:i + 1].mean()
    return atr

atr14 = compute_atr(h, l, c, ATR_PERIOD)
print("ATR14 hesaplandi.")

# ---------------------------------------------------------------------
# 4) TICK-BAZLI GERCEKLENEBILIR MALIYET MODELI (gorev Kapsam madde 2 - ZORUNLU)
#    Girisin gerceklestigi barin baslangic zaman damgasindaki GERCEK ilk tick
#    (bid/ask) MT5'ten cekilir. Bu, hem GERCEK spread (ask-bid) hem GIRIS
#    SLIPAJI (tick-fiyati ile teorik bar-acilis fiyati arasindaki fark) icerir.
#    Cikis tarafinda ayni ANDA tick verisi COKALINMIYOR (TP/SL tetiklenme
#    zamanini bar-ici hassasiyette bilmedigimiz icin - Hipotez1 ile ayni
#    hesaplama-uygulanabilirlik kisiti); bunun yerine cikista da benzer
#    genislikte bir spread-payi varsayilir: giris tick'inde olculen spread'in
#    YARISI cikis maliyeti olarak ayrica dusulur (round-trip = giris-yarisi +
#    cikis-yarisi + giris-slipaji). Bu, Hipotez1'in bar-kapanis-spread-alani
#    yaklasimindan daha gercekci (gercek tick verisine dayanir) ama tam
#    cift-tarafli tick simulasyonu DEGILDIR - bu SINIR asagida ayrica
#    UYARILAR'da not dusuluyor.
#
#    DUZELTME (2026-07-11, bu tur - bkz. dosya basi "DUZELTME NOTU" ve nihai
#    raporun "Slipaj/Tick-Eslesme Duzeltme Notu" bolumu): onceki tur, MT5'in
#    copy_ticks_from() cagrisindan DONEN TICK'IN KENDI ZAMAN DAMGASINI hic
#    kontrol etmiyordu. Bu turde eklendi - bkz. get_tick_quote().
# ---------------------------------------------------------------------
TICK_QUOTE_CACHE = {}
TICK_LOOKUP_COUNT = {"call": 0, "hit": 0, "miss_veri_yok": 0, "miss_zaman_uyusmazligi": 0, "miss_gecersiz_kotasyon": 0}

# copy_ticks_from(SYMBOL, bar_epoch, 3, ALL), istenen bar_epoch'tan ITIBAREN ("ileri") tick
# istemesine ragmen, ampirik olarak dogrulandi ki (bkz. rapor) MT5 API'nin tick gecmisi o eski
# tarihe tam senkronize olmadan/hazir olmadan yapilan cagrilarda GUNCEL/FARKLI-DONEMLI bir tick
# donebiliyor (soguk-baslangic artefakti). Bu yuzden donen tick'in KENDI zaman damgasi
# (ticks[0]['time']) bar_epoch ile karsilastirilir; esik disindaysa REDDEDILIR.
MAX_TICK_MISMATCH_SEC = 60   # M5 bar genisliginin (300 sn) beste biri - GOLD aktif piyasada tick
                              # frekansi saniyenin cok altinda oldugundan bu esik gercek bir tick
                              # icin sikistirici degil, ama gozlemlenen artefaktin buyuklugu
                              # (ay/yil mertebesi) karsisinda gercek-vs-artefakt ayrimini kesin yapar
TICK_TIME_MISMATCH_LOG = []   # yalniz REDDEDILEN (esik disi) kayitlar - rapor icin

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
        tick_epoch = int(row['time'])
        fark_saniye = tick_epoch - bar_epoch
        if fark_saniye > MAX_TICK_MISMATCH_SEC or fark_saniye < -1:
            # donen tick'in zaman damgasi istenen bar anindan cok uzak -> veri-yoklugu artefakti,
            # gercek slipaj olarak KULLANILMIYOR
            TICK_LOOKUP_COUNT["miss_zaman_uyusmazligi"] += 1
            TICK_TIME_MISMATCH_LOG.append({
                "bar_idx": int(bar_idx),
                "bar_epoch_utc": str(datetime.fromtimestamp(bar_epoch, tz=timezone.utc)),
                "donen_tick_utc": str(datetime.fromtimestamp(tick_epoch, tz=timezone.utc)),
                "fark_saniye": int(fark_saniye),
                "fark_gun": round(fark_saniye / 86400.0, 2),
            })
        else:
            bid = float(row['bid']); ask = float(row['ask'])
            if ask > 0 and bid > 0 and ask >= bid:
                result = (ask, bid)
            else:
                TICK_LOOKUP_COUNT["miss_gecersiz_kotasyon"] += 1
    TICK_QUOTE_CACHE[bar_idx] = result
    return result

# ---------------------------------------------------------------------
# 5) TEK ISLEM SIMULASYONU (nedensel, look-ahead yok)
# ---------------------------------------------------------------------
def confirmed_reversal_bar(idx, fade_dir_val):
    if c[idx] == o[idx]:
        return False
    if fade_dir_val == 1:
        return c[idx] > o[idx]
    else:
        return c[idx] < o[idx]

def determine_entry_idx(big_idx, fade_dir_val, confirm_horizon):
    if confirm_horizon == 1:
        return big_idx + 1
    elif confirm_horizon == 2:
        c1_idx = big_idx + 1
        if c1_idx >= n or not confirmed_reversal_bar(c1_idx, fade_dir_val):
            return None
        return big_idx + 2
    elif confirm_horizon == 3:
        c1_idx, c2_idx = big_idx + 1, big_idx + 2
        if c2_idx >= n:
            return None
        if not (confirmed_reversal_bar(c1_idx, fade_dir_val) and confirmed_reversal_bar(c2_idx, fade_dir_val)):
            return None
        return big_idx + 3
    raise ValueError("gecersiz confirm_horizon")

def simulate_trade(big_idx, fade_dir_val, confirm_horizon, exit_mode, n_bars_time, session_filter):
    if session_filter is not None and hours[big_idx] not in session_filter:
        return None, "seans_disi"

    entry_idx = determine_entry_idx(big_idx, fade_dir_val, confirm_horizon)
    if entry_idx is None or entry_idx >= n:
        return None, "teyit_saglanmadi_veya_sinir"

    atr_at_signal = atr14[big_idx]
    if np.isnan(atr_at_signal) or atr_at_signal <= 0:
        return None, "atr_yok"

    direction = fade_dir_val
    entry_price_theo = o[entry_idx]
    tp_dist = RR_RATIO * ATR_FRACTION * atr_at_signal
    sl_dist = ATR_FRACTION * atr_at_signal
    if direction == 1:
        tp_price = entry_price_theo + tp_dist
        sl_price = entry_price_theo - sl_dist
    else:
        tp_price = entry_price_theo - tp_dist
        sl_price = entry_price_theo + sl_dist

    time_exit_idx = entry_idx + n_bars_time
    if time_exit_idx >= n:
        return None, "yetersiz_veri"

    exit_idx = exit_price_theo = exit_reason = None
    if exit_mode == 'time':
        exit_idx = time_exit_idx
        exit_price_theo = c[exit_idx]
        exit_reason = "zaman"
    else:
        scan_end = time_exit_idx if exit_mode == 'combined' else min(entry_idx + MAX_HOLD_BARS_ATR_ONLY, n - 1)
        for j in range(entry_idx, scan_end + 1):
            hit_tp = (h[j] >= tp_price) if direction == 1 else (l[j] <= tp_price)
            hit_sl = (l[j] <= sl_price) if direction == 1 else (h[j] >= sl_price)
            if hit_tp and hit_sl:
                exit_idx, exit_price_theo, exit_reason = j, sl_price, "SL(ayni-bar-oncelik)"
                break
            elif hit_sl:
                exit_idx, exit_price_theo, exit_reason = j, sl_price, "SL"
                break
            elif hit_tp:
                exit_idx, exit_price_theo, exit_reason = j, tp_price, "TP"
                break
        if exit_idx is None:
            if exit_mode == 'combined':
                exit_idx = time_exit_idx
                exit_price_theo = c[exit_idx]
                exit_reason = "zaman(TP/SL_tetiklenmedi)"
            else:
                exit_idx = scan_end
                exit_price_theo = c[exit_idx]
                exit_reason = "max_hold(TP/SL_tetiklenmedi)"

    raw_pts = (exit_price_theo - entry_price_theo) / POINT if direction == 1 else (entry_price_theo - exit_price_theo) / POINT

    quote = get_tick_quote(entry_idx)
    if quote is None:
        return None, "tick_verisi_yok"
    ask, bid = quote
    spread_pts_tick = (ask - bid) / POINT
    if direction == 1:
        entry_realistic = ask
        entry_slippage_pts = (entry_realistic - entry_price_theo) / POINT
    else:
        entry_realistic = bid
        entry_slippage_pts = (entry_price_theo - entry_realistic) / POINT
    total_cost_pts = entry_slippage_pts + spread_pts_tick / 2.0
    net_pts = raw_pts - total_cost_pts

    return {
        "big_bar_idx": int(big_idx), "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
        "tarih": dates[big_idx], "saat_buyuk_bar": int(hours[big_idx]),
        "yon": "LONG" if direction == 1 else "SHORT", "confirm_horizon": confirm_horizon,
        "giris_teo": float(entry_price_theo), "cikis_teo": float(exit_price_theo), "sebep": exit_reason,
        "atr_entry_pts": float(atr_at_signal / POINT),
        "tick_spread_pts": round(float(spread_pts_tick), 3),
        "giris_slipaj_pts": round(float(entry_slippage_pts), 3),
        "toplam_maliyet_pts": round(float(total_cost_pts), 3),
        "raw_pts": round(float(raw_pts), 3), "net_pts": round(float(net_pts), 3),
        "net_usd_per_lot": round(float(net_pts * POINT * CONTRACT_SIZE), 2),
    }, "ok"

def run_scenario(confirm_horizon, exit_mode, n_bars_time, session_filter):
    trades = []
    reasons = defaultdict(int)
    open_until = -1
    for i in range(len(is_big5)):
        if not is_big5[i]:
            continue
        if i <= open_until:
            reasons["cakisma_atlandi"] += 1
            continue
        res, status = simulate_trade(i, fade_dir5[i], confirm_horizon, exit_mode, n_bars_time, session_filter)
        if res is None:
            reasons[status] += 1
            continue
        trades.append(res)
        open_until = res["exit_idx"]
    return trades, dict(reasons)

# ---------------------------------------------------------------------
# 6) OZETLEME / IS-OOS / WALK-FORWARD / DAGILIM ISTATISTIKLERI
# ---------------------------------------------------------------------
def summarize(trades):
    if not trades:
        return {"toplam_islem": 0, "win_rate": None, "profit_factor": None, "net_profit_pts": 0.0,
                "net_profit_usd_per_lot": 0.0, "max_drawdown_pts": None}
    net = np.array([x["net_pts"] for x in trades])
    wins = net[net > 0]; losses = net[net <= 0]
    win_rate = len(wins) / len(net)
    gross_profit = wins.sum() if len(wins) else 0.0
    gross_loss = -losses.sum() if len(losses) else 0.0
    pf = (gross_profit / gross_loss) if gross_loss > 0 else (None if gross_profit == 0 else float("inf"))
    cum = np.cumsum(net)
    running_max = np.maximum.accumulate(cum)
    dd = cum - running_max
    return {
        "toplam_islem": int(len(net)),
        "win_rate": round(float(win_rate), 4),
        "profit_factor": (round(float(pf), 3) if pf not in (None, float("inf")) else pf),
        "net_profit_pts": round(float(net.sum()), 2),
        "net_profit_usd_per_lot": round(float(net.sum() * POINT * CONTRACT_SIZE), 2),
        "ortalama_net_pts": round(float(net.mean()), 3),
        "medyan_net_pts": round(float(np.median(net)), 3),
        "max_drawdown_pts": round(float(dd.min()), 2) if len(dd) else 0.0,
        "ortalama_atr_entry_pts": round(float(np.mean([x["atr_entry_pts"] for x in trades])), 2),
        "ortalama_tick_spread_pts": round(float(np.mean([x["tick_spread_pts"] for x in trades])), 3),
        "ortalama_giris_slipaj_pts": round(float(np.mean([x["giris_slipaj_pts"] for x in trades])), 3),
        "ortalama_toplam_maliyet_pts": round(float(np.mean([x["toplam_maliyet_pts"] for x in trades])), 3),
    }

def split_is_oos(trades):
    if not trades:
        return [], []
    cutoff = int(n * IS_FRACTION)
    is_tr = [x for x in trades if x["big_bar_idx"] < cutoff]
    oos_tr = [x for x in trades if x["big_bar_idx"] >= cutoff]
    return is_tr, oos_tr

def walk_forward_folds(trades, folds=WF_FOLDS):
    if not trades:
        return []
    edges = np.linspace(0, n, folds + 1).astype(int)
    out = []
    for f in range(folds):
        lo, hi = edges[f], edges[f + 1]
        sub = [x for x in trades if lo <= x["big_bar_idx"] < hi]
        out.append({"fold": f + 1, "bar_araligi": [int(lo), int(hi)],
                     "tarih_araligi": [dates[lo], dates[min(hi, n - 1)]], **summarize(sub)})
    return out

def consecutive_streaks(trades):
    max_win = max_loss = cur_win = cur_loss = 0
    for x in trades:
        if x["net_pts"] > 0:
            cur_win += 1; cur_loss = 0
        else:
            cur_loss += 1; cur_win = 0
        max_win = max(max_win, cur_win); max_loss = max(max_loss, cur_loss)
    return {"max_ardisik_kazanc": max_win, "max_ardisik_kayip": max_loss}

def profit_concentration(trades, top_n=10):
    nets = sorted([x["net_pts"] for x in trades if x["net_pts"] > 0], reverse=True)
    gross = sum(nets)
    top = sum(nets[:top_n])
    return {"top_n": top_n, "toplam_islem_sayisi_kazanan": len(nets),
            "gross_profit_pts": round(gross, 2), "top_n_profit_pts": round(top, 2),
            "top_n_payi": round(top / gross, 4) if gross > 0 else None}

def monthly_breakdown(trades):
    agg = defaultdict(list)
    for x in trades:
        agg[x["tarih"][:7]].append(x["net_pts"])
    out = {}
    for k in sorted(agg.keys()):
        arr = np.array(agg[k])
        out[k] = {"islem": int(len(arr)), "net_pts": round(float(arr.sum()), 2),
                   "win_rate": round(float((arr > 0).mean()), 4)}
    return out

def net_pts_percentiles(trades):
    net = np.array([x["net_pts"] for x in trades])
    pct = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    return {f"p{p}": round(float(np.percentile(net, p)), 3) for p in pct}

print("Yardimci fonksiyonlar hazir. Senaryolar kosturuluyor...")

# ---------------------------------------------------------------------
# 7) SENARYOLAR
# ---------------------------------------------------------------------
scenarios = {}

# --- 7.1 ANA/BASELINE KONFIGURASYON ---
# confirm_horizon=1 (teyitsiz, BULGU4'un olctugu t+1 ufku), exit=combined
# (ATR TP/SL 0,5xATR VEYA N=1 bar zaman-asimi, hangisi once), seans=15-18
baseline_trades, baseline_reasons = run_scenario(confirm_horizon=1, exit_mode='combined', n_bars_time=1, session_filter=SESSION_PRIMARY)
baseline_is, baseline_oos = split_is_oos(baseline_trades)
scenarios["ANA_KONFIGURASYON"] = {
    "parametreler": {"confirm_horizon": 1, "exit_mode": "combined", "n_bars_time": 1,
                      "atr_fraction": ATR_FRACTION, "rr_ratio": RR_RATIO, "seans_filtresi": "15-18"},
    "meta_atlanma_nedenleri": baseline_reasons,
    "tum_donem": summarize(baseline_trades),
    "IS_ilk_%70": summarize(baseline_is),
    "OOS_son_%30": summarize(baseline_oos),
    "walk_forward": walk_forward_folds(baseline_trades),
    "ardisik_seriler": consecutive_streaks(baseline_trades),
    "kar_konsantrasyonu_top10": profit_concentration(baseline_trades, 10),
    "aylik_kirilim": monthly_breakdown(baseline_trades),
    "net_pts_percentile": net_pts_percentiles(baseline_trades) if baseline_trades else None,
}
print("ANA_KONFIGURASYON tamamlandi. Islem:", len(baseline_trades), "tick lookup:", TICK_LOOKUP_COUNT)

# --- 7.2 TEYIT UFKU (CONFIRM HORIZON) TARAMASI: t+1 / t+2 / t+3 ---
confirm_scan = {}
for hcfg in CONFIRM_HORIZONS:
    tr, rs = run_scenario(confirm_horizon=hcfg, exit_mode='combined', n_bars_time=1, session_filter=SESSION_PRIMARY)
    tr_is, tr_oos = split_is_oos(tr)
    confirm_scan[f"t+{hcfg}"] = {
        "meta_atlanma_nedenleri": rs,
        "tum_donem": summarize(tr), "IS": summarize(tr_is), "OOS": summarize(tr_oos),
        "walk_forward": walk_forward_folds(tr),
    }
    print(f"CONFIRM_HORIZON t+{hcfg} tamamlandi. Islem:", len(tr), "tick lookup:", TICK_LOOKUP_COUNT)
scenarios["TEYIT_UFKU_TARAMASI"] = {
    "not": "Esik carpani (1.5x) SABIT tutuldu, yalniz teyit ufku (t+1/t+2/t+3) dar taramasi yapildi (gorev Kapsam madde 6).",
    "sonuclar": confirm_scan,
}

# --- 7.3 CIKIS YONTEMI TARAMASI: time-only (N=1,2,3) / ATR-only / combined ---
exit_scan = {}
for ncfg in TIME_EXIT_SCAN:
    tr, rs = run_scenario(confirm_horizon=1, exit_mode='time', n_bars_time=ncfg, session_filter=SESSION_PRIMARY)
    tr_is, tr_oos = split_is_oos(tr)
    exit_scan[f"yalniz_zaman_N{ncfg}"] = {
        "meta_atlanma_nedenleri": rs,
        "tum_donem": summarize(tr), "IS": summarize(tr_is), "OOS": summarize(tr_oos),
        "walk_forward": walk_forward_folds(tr),
    }
    print(f"EXIT time N={ncfg} tamamlandi. Islem:", len(tr))

atr_trades, atr_reasons = run_scenario(confirm_horizon=1, exit_mode='atr', n_bars_time=1, session_filter=SESSION_PRIMARY)
atr_is, atr_oos = split_is_oos(atr_trades)
exit_scan["yalniz_ATR_TP_SL"] = {
    "meta_atlanma_nedenleri": atr_reasons,
    "tum_donem": summarize(atr_trades), "IS": summarize(atr_is), "OOS": summarize(atr_oos),
    "walk_forward": walk_forward_folds(atr_trades),
    "not": f"ATR TP/SL {MAX_HOLD_BARS_ATR_ONLY} barda tetiklenmezse zorla kapatilir (muhendislik siniri).",
}
print("EXIT ATR-only tamamlandi. Islem:", len(atr_trades))

exit_scan["combined_ana"] = {
    "tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos),
    "walk_forward": scenarios["ANA_KONFIGURASYON"]["walk_forward"],
}
scenarios["CIKIS_YONTEMI_TARAMASI"] = {
    "not": "N-bar-zaman-cikis (1-3 bar) ATR-bazli TP/SL ile karsilastirildi, her varyantta walk-forward/OOS raporlandi (gorev Kapsam madde 3).",
    "sonuclar": exit_scan,
}
print("CIKIS_YONTEMI_TARAMASI tamamlandi. Toplam tick lookup:", TICK_LOOKUP_COUNT)

# --- 7.4 SEANS FiLTRESi KARSILASTIRMA: filtresiz vs filtreli(15-18) ---
nofilter_trades, nf_reasons = run_scenario(confirm_horizon=1, exit_mode='combined', n_bars_time=1, session_filter=None)
nf_is, nf_oos = split_is_oos(nofilter_trades)
scenarios["SEANS_FiLTRESi_KARSILASTIRMA"] = {
    "filtresiz_tum_saatler": {
        "meta_atlanma_nedenleri": nf_reasons,
        "tum_donem": summarize(nofilter_trades), "IS": summarize(nf_is), "OOS": summarize(nf_oos),
        "walk_forward": walk_forward_folds(nofilter_trades),
    },
    "birincil_15_18": {
        "tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos),
        "walk_forward": scenarios["ANA_KONFIGURASYON"]["walk_forward"],
    },
}
print("SEANS_FiLTRESi_KARSILASTIRMA tamamlandi. Islem (filtresiz):", len(nofilter_trades), "Toplam tick lookup:", TICK_LOOKUP_COUNT)

# ---------------------------------------------------------------------
# 8) TAM ISLEM LOGU (ANA KONFIGURASYON - TAMAMI, ornek degil - Risk Analisti
#    Hipotez1 turunde bu eksikligi bildirmisti, bu turde TEKRARLANMIYOR)
# ---------------------------------------------------------------------
scenarios["ANA_KONFIGURASYON"]["islem_logu_tam"] = baseline_trades

results["senaryolar"] = scenarios
results["sabitler"] = {
    "RANGE_WINDOW": RANGE_WINDOW, "BIGBAR_MULT": BIGBAR_MULT, "ATR_PERIOD": ATR_PERIOD,
    "ATR_FRACTION": ATR_FRACTION, "RR_RATIO": RR_RATIO, "CONFIRM_HORIZONS": CONFIRM_HORIZONS,
    "TIME_EXIT_SCAN": TIME_EXIT_SCAN, "MAX_HOLD_BARS_ATR_ONLY": MAX_HOLD_BARS_ATR_ONLY,
    "SESSION_PRIMARY": sorted(SESSION_PRIMARY), "IS_FRACTION": IS_FRACTION, "WF_FOLDS": WF_FOLDS,
    "MAX_TICK_MISMATCH_SEC": MAX_TICK_MISMATCH_SEC,
}
results["tick_lookup_istatistigi"] = TICK_LOOKUP_COUNT

# ---------------------------------------------------------------------
# 9) TICK ZAMAN-ESLESME DOGRULAMA RAPORU (bu tur eklendi - gorev madde 1)
#    Reddedilen (esik-disi) tum kayitlarin dagilimi + ilk 20 ornek.
# ---------------------------------------------------------------------
if TICK_TIME_MISMATCH_LOG:
    fark_gun_arr = np.array([x["fark_gun"] for x in TICK_TIME_MISMATCH_LOG])
    mismatch_summary = {
        "toplam_reddedilen": len(TICK_TIME_MISMATCH_LOG),
        "fark_gun_min": round(float(fark_gun_arr.min()), 2),
        "fark_gun_max": round(float(fark_gun_arr.max()), 2),
        "fark_gun_ortalama": round(float(fark_gun_arr.mean()), 2),
        "fark_gun_medyan": round(float(np.median(fark_gun_arr)), 2),
    }
else:
    mismatch_summary = {"toplam_reddedilen": 0}

results["tick_zaman_eslesme_dogrulama"] = {
    "esik_saniye": MAX_TICK_MISMATCH_SEC,
    "yontem": "copy_ticks_from() cagrisindan donen ilk tick'in KENDI zaman damgasi (ticks[0]['time']) "
              "istenen bar_epoch ile karsilastirildi; fark esigi asarsa (veya negatifse) tick REDDEDILDI.",
    "ozet": mismatch_summary,
    "reddedilen_ornekler_ilk_20": TICK_TIME_MISMATCH_LOG[:20],
}
print("Tick zaman-eslesme dogrulama ozeti:", mismatch_summary)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI ->", OUT_PATH)
print(json.dumps(scenarios["ANA_KONFIGURASYON"]["tum_donem"], ensure_ascii=False, indent=2))
print(json.dumps(scenarios["ANA_KONFIGURASYON"]["OOS_son_%30"], ensure_ascii=False, indent=2))
print("Tick lookup istatistigi:", TICK_LOOKUP_COUNT)

mt5.shutdown()
