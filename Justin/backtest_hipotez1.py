# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - HIPOTEZ 1 dogrulama
Seans-Filtreli Asimetrik Ortalamaya-Donus (Mean-Reversion), M5, GOLD

Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi
okumaz/kullanmaz (signal.json, milagold_trades.json, lisa_performance.json,
positions_status.json, stratejici_gold_gecmis_calisma.md vb.). Yalniz
MT5'ten dogrudan cekilen ham GOLD M5 verisi kullanilir. MilaGold'un sabit
5$/3$/5$/8$ SL/TP yapisi veya lot kurallari HICBIR SEKILDE kullanilmadi;
SL/TP tamamen ATR-bazli/dinamik olarak Stratejist'in tasarimina gore
uygulanmistir.

Kapsam: Stratejist raporu, HIPOTEZ 1 (satir 38-88) + Backtest Muhendisi
icin Notlar (satir 182-206).
"""
import json
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timezone

# ---------------------------------------------------------------------
# SABITLER (Stratejist'in belirledigi degerler - degistirilmedi)
# ---------------------------------------------------------------------
SYMBOL = "GOLD"
WINDOW = 20            # SMA/rolling-std penceresi, BULGU5 ile tutarli
K_BASELINE = 2.0        # sapma esigi carpani (baslangic)
K_SCAN = [1.5, 2.0, 2.5]  # Stratejist'in izin verdigi dar tarama araligi
ATR_PERIOD = 14         # ATR(14, M5)
RR_RATIO = 1.0          # TP:SL = 1:1 (baslangic orani, Stratejist notu)
N_BARS_BASELINE = 5     # zaman-bazli cikis, BULGU5 ile tutarli
SESSION_PRIMARY = set(range(15, 19))              # sunucu saati 15-18
SESSION_SECONDARY = set(range(15, 19)) | {3, 4}    # + ikincil 3-4 bandi
DETREND_WINDOW = 100    # rolling lineer trend penceresi (muhendislik karari,
                         # asagida GEREKCE bolumunde aciklanir)
IS_FRACTION = 0.70       # klasik IS/OOS ayrimi
WF_FOLDS = 6             # walk-forward rolling pencere sayisi
MAX_HOLD_BARS_ATR_ONLY = 50   # yalniz-ATR exit varyanti icin muhendislik
                              # ust siniri (Stratejist N belirtmedigi icin;
                              # sinirsiz tutma gerceci degildir)

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_hipotez1_output.json"

# ---------------------------------------------------------------------
# MT5 BAGLANTISI VE HAM VERI
# ---------------------------------------------------------------------
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size  # 100 oz -> 1 puan = 0.01 USD/oz -> 1.0 lot basina 1 USD/puan

rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 99999)
n = len(rates)
t = rates['time'].astype(np.int64)
o = rates['open'].astype(float)
h = rates['high'].astype(float)
l = rates['low'].astype(float)
c = rates['close'].astype(float)
spr = rates['spread'].astype(float)  # broker'in bar-kapanisinda rapor ettigi puan-cinsi spread

hours = np.array([datetime.fromtimestamp(x, tz=timezone.utc).hour for x in t])
dates = np.array([datetime.fromtimestamp(x, tz=timezone.utc).date() for x in t])

results = {}
results["veri_ozeti"] = {
    "sembol": SYMBOL,
    "toplam_bar_M5": int(n),
    "baslangic": str(datetime.fromtimestamp(int(t[0]), tz=timezone.utc)),
    "bitis": str(datetime.fromtimestamp(int(t[-1]), tz=timezone.utc)),
    "point": POINT,
    "contract_size": CONTRACT_SIZE,
}

# ---------------------------------------------------------------------
# 1) SAAT ESLEME DOGRULAMASI (Acik Soru 1 / Muhendis Notu 3)
# ---------------------------------------------------------------------
# (a) Canli-an capraz kontrolu: MT5 epoch'unu UTC gibi okuyup VPS yerel
#     saatiyle (CLAUDE.md: VPS saat dilimi GMT+3) karsilastir.
tick = mt5.symbol_info_tick(SYMBOL)
epoch_as_utc = datetime.fromtimestamp(tick.time, tz=timezone.utc).replace(tzinfo=None)
vps_local_now = datetime.now()
diff_seconds = abs((epoch_as_utc - vps_local_now).total_seconds())

# (b) Hafta sonu geciş noktalarinda (Cuma kapanis / Pazar acilis) saat
#     kaymasi var mi? EU/Cyprus DST gecis tarihleri veri araliginda 3 kez
#     gerceklesiyor: 2025-03-30 (ileri), 2025-10-26 (geri), 2026-03-29 (ileri).
#     Eger sunucu GMT+3 SABIT calisiyorsa bu tarihler civarinda Cuma-kapanis
#     saatinde kayma OLMAMALI. Kayma varsa, sunucu EU DST'sini takip ediyor
#     demektir (yani GMT+3 sadece yaz aylarinda, kis aylarinda GMT+2) - bu
#     durumda mevcut saat-bazli filtreler kis aylarinda 1 saat kaymis olur.
gap_threshold_sec = 23 * 3600  # 23 saatten uzun bar-arasi bosluk = hafta sonu
gaps = []
for i in range(1, n):
    dt = t[i] - t[i-1]
    if dt > gap_threshold_sec:
        gaps.append({
            "friday_close_utc_epoch_hour": int(hours[i-1]),
            "friday_close_date": str(dates[i-1]),
            "sunday_open_utc_epoch_hour": int(hours[i]),
            "sunday_open_date": str(dates[i]),
        })

dst_transitions = ["2025-03-30", "2025-10-26", "2026-03-29"]

def hour_mode_window(gaps_list, center_date_str, days=21, key="friday_close_utc_epoch_hour", date_key="friday_close_date"):
    from datetime import date as _date
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
        "oncesi_tekil_deger_mi": len(set(before)) <= 1 if before else None,
        "sonrasi_tekil_deger_mi": len(set(after)) <= 1 if after else None,
        "kayma_tespit_edildi_mi": (
            bool(before) and bool(after) and
            (max(set(before), key=before.count) != max(set(after), key=after.count))
        ),
    })

results["saat_esleme_dogrulama"] = {
    "canli_capraz_kontrol": {
        "aciklama": "MT5 tick.time UTC-gibi okundugunda VPS yerel saatine (GMT+3, CLAUDE.md) ne kadar yakin?",
        "epoch_utc_okuma": str(epoch_as_utc),
        "vps_yerel_simdi": str(vps_local_now),
        "fark_saniye": diff_seconds,
        "yorum": "Fark birkac saniye/dakika mertebesindeyse (network/islem gecikmesi), su anki (Temmuz 2026, yaz) offset = GMT+3 dogrulanir.",
    },
    "hafta_sonu_gecis_DST_kontrolu": dst_check,
    "toplam_hafta_sonu_gecis_sayisi": len(gaps),
    "genel_sonuc": (
        "DST gecis tarihlerinin hicbirinde Cuma-kapanis saatinde kayma tespit edilmediyse (asagidaki "
        "'kayma_tespit_edildi_mi' hepsinde False ise), sunucu sabit bir offset kullaniyor demektir - "
        "GMT+3 varsayimi yil boyunca tutarlidir. Kayma tespit edilirse (True), sunucu EU/Cyprus DST'sini "
        "takip ediyor demektir ve GMT+3 varsayimi yalniz yaz aylarinda (Mart sonu-Ekim sonu) gecerlidir; "
        "kis aylarinda saat-bazli filtreler (15-18, 0-2, 22-23) 1 saat kaydirilarak yeniden degerlendirilmelidir."
    ),
}

print("Saat esleme kontrolu tamamlandi, hafta sonu gecis sayisi:", len(gaps))
for d in dst_check:
    print(d)

# ---------------------------------------------------------------------
# 2) TEMEL SERILER: SMA20/std20 (ham fiyat), ATR14 (ham fiyat)
# ---------------------------------------------------------------------
def rolling_sma_std(closes, window):
    sma = np.full(len(closes), np.nan)
    std = np.full(len(closes), np.nan)
    csum = np.cumsum(np.insert(closes, 0, 0.0))
    for i in range(window - 1, len(closes)):
        seg = closes[i-window+1:i+1]
        sma[i] = seg.mean()
        std[i] = seg.std()
    return sma, std

sma20, std20 = rolling_sma_std(c, WINDOW)

def compute_atr(h, l, c, period):
    tr = np.full(len(c), np.nan)
    tr[0] = h[0] - l[0]
    for i in range(1, len(c)):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i-1]), abs(l[i] - c[i-1]))
    atr = np.full(len(c), np.nan)
    for i in range(period - 1, len(c)):
        atr[i] = tr[i-period+1:i+1].mean()
    return atr

atr14 = compute_atr(h, l, c, ATR_PERIOD)

# ---------------------------------------------------------------------
# 3) DETREND SERISI: rolling lineer trend cikarma (nedensel/causal)
#    GEREKCE: Stratejist "rolling lineer trend" istedi, pencere belirtmedi.
#    DETREND_WINDOW=100 bar (~8.3 saat, M5) secildi - BULGU6'daki uzun-vadeli
#    (17 aylik) yon-onyargisini (drift) baskilayacak kadar uzun, ama
#    WINDOW=20'lik sinyal penceresini bozacak kadar kisa DEGIL. Yalniz o ana
#    kadarki (i-DETREND_WINDOW+1 .. i) verilerle hesaplanir - ileri-bakis yok.
# ---------------------------------------------------------------------
def rolling_linear_detrend(closes, window):
    nloc = len(closes)
    trend = np.full(nloc, np.nan)
    x = np.arange(window, dtype=float)
    sx = x.sum()
    sxx = (x * x).sum()
    denom = window * sxx - sx * sx
    csum_y = np.cumsum(np.insert(closes, 0, 0.0))
    idx_all = np.arange(nloc, dtype=float)
    csum_iy = np.cumsum(np.insert(idx_all * closes, 0, 0.0))
    for i in range(window - 1, nloc):
        start = i - window + 1
        sy = csum_y[i+1] - csum_y[start]
        # sum(local_x * y) = sum(j*y) - start*sum(y),  j=global index
        s_jy = csum_iy[i+1] - csum_iy[start]
        sxy = s_jy - start * sy
        slope = (window * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / window
        trend[i] = intercept + slope * (window - 1)  # trend degeri bar i'de (x=window-1)
    return trend

trend100 = rolling_linear_detrend(c, DETREND_WINDOW)
detrended = c - trend100  # NaN ilk DETREND_WINDOW-1 barda

sma20_dt, std20_dt = rolling_sma_std(np.nan_to_num(detrended, nan=0.0), WINDOW)
# detrended serideki NaN bölgesini maskeler icin ayrica gecerlilik maskesi:
dt_valid_from = DETREND_WINDOW - 1

print("Temel seriler (SMA/std/ATR/detrend) hesaplandi.")

# ---------------------------------------------------------------------
# 4) SINYAL URETIMI (alt-sapma / long) - ham VE detrended seri icin
# ---------------------------------------------------------------------
def gen_signals(price_close, sma, std, k, valid_from=WINDOW-1, upper_too=False):
    """close < sma - k*std -> long sinyali (alt-sapma).
       upper_too=True ise ayrica close > sma + k*std -> short sinyali (simetrik, yalniz detrend testi icin)."""
    long_idx = []
    short_idx = []
    for i in range(valid_from, len(price_close)):
        if np.isnan(sma[i]) or np.isnan(std[i]) or std[i] == 0:
            continue
        dev = price_close[i] - sma[i]
        if dev < -k * std[i]:
            long_idx.append(i)
        elif upper_too and dev > k * std[i]:
            short_idx.append(i)
    return long_idx, short_idx

print("Sinyal uretimi baslatiliyor...")

# ---------------------------------------------------------------------
# 5) TEK BiR ISLEMI SIMULE ETME (nedensel, look-ahead yok)
# ---------------------------------------------------------------------
def simulate_trade(signal_idx, direction, entry_mode, exit_mode, n_bars, rr_ratio):
    """direction: +1 long, -1 short.
       entry_mode: 'close' (sinyal barinin kapanisinda) | 'next_open' (bir sonraki bar acilisinda)
       exit_mode: 'time' | 'atr' | 'combined'
       Donus: dict veya None (yetersiz veri/atr yok ise)."""
    if entry_mode == 'close':
        entry_idx = signal_idx
        entry_price = c[signal_idx]
        scan_start = signal_idx + 1
    else:  # next_open
        entry_idx = signal_idx + 1
        if entry_idx >= n:
            return None
        entry_price = o[entry_idx]
        scan_start = entry_idx

    atr_at_signal = atr14[signal_idx]
    if np.isnan(atr_at_signal) or atr_at_signal <= 0:
        return None

    tp_dist = rr_ratio * atr_at_signal  # RR_RATIO=1.0 -> TP=SL=1xATR
    sl_dist = 1.0 * atr_at_signal
    if direction == 1:
        tp_price = entry_price + tp_dist
        sl_price = entry_price - sl_dist
    else:
        tp_price = entry_price - tp_dist
        sl_price = entry_price + sl_dist

    time_exit_idx = entry_idx + n_bars
    if time_exit_idx >= n:
        return None

    exit_idx = None
    exit_price = None
    exit_reason = None

    if exit_mode == 'time':
        exit_idx = time_exit_idx
        exit_price = c[exit_idx]
        exit_reason = "zaman"
    else:
        scan_end = time_exit_idx if exit_mode == 'combined' else min(entry_idx + MAX_HOLD_BARS_ATR_ONLY, n - 1)
        for j in range(scan_start, scan_end + 1):
            hit_tp = (h[j] >= tp_price) if direction == 1 else (l[j] <= tp_price)
            hit_sl = (l[j] <= sl_price) if direction == 1 else (h[j] >= sl_price)
            if hit_tp and hit_sl:
                # ayni barda ikisi de - muhafazakar varsayim: SL vuruldu say
                exit_idx, exit_price, exit_reason = j, sl_price, "SL(ayni-bar-oncelik)"
                break
            elif hit_sl:
                exit_idx, exit_price, exit_reason = j, sl_price, "SL"
                break
            elif hit_tp:
                exit_idx, exit_price, exit_reason = j, tp_price, "TP"
                break
        if exit_idx is None:
            if exit_mode == 'combined':
                exit_idx = time_exit_idx
                exit_price = c[exit_idx]
                exit_reason = "zaman(TP/SL_tetiklenmedi)"
            else:
                exit_idx = scan_end
                exit_price = c[exit_idx]
                exit_reason = "max_hold(TP/SL_tetiklenmedi)"

    spread_cost_pts = spr[entry_idx]  # yuvarlak-tur maliyet: girisin gerceklestigi bardaki broker spread'i
    raw_pts = (exit_price - entry_price) / POINT if direction == 1 else (entry_price - exit_price) / POINT
    net_pts = raw_pts - spread_cost_pts

    return {
        "signal_idx": int(signal_idx),
        "entry_idx": int(entry_idx),
        "exit_idx": int(exit_idx),
        "entry_hour": int(hours[signal_idx]),
        "direction": direction,
        "entry_price": float(entry_price),
        "exit_price": float(exit_price),
        "exit_reason": exit_reason,
        "atr_at_entry_pts": float(atr_at_signal / POINT),
        "spread_cost_pts": float(spread_cost_pts),
        "raw_pts": float(raw_pts),
        "net_pts": float(net_pts),
        "net_usd_per_lot": float(net_pts * POINT * CONTRACT_SIZE),  # 1.0 standart lot varsayimiyla, kiyaslama amacli
    }

# ---------------------------------------------------------------------
# 6) BiR SENARYOYU KOSTUR: sinyal uret + non-overlapping trade simulasyonu
# ---------------------------------------------------------------------
def run_scenario(k, entry_mode, exit_mode, n_bars, rr_ratio, session_filter, use_detrended, allow_short=False):
    if use_detrended:
        long_idx, short_idx = gen_signals(detrended, sma20_dt, std20_dt, k, valid_from=max(WINDOW-1, dt_valid_from), upper_too=allow_short)
    else:
        long_idx, short_idx = gen_signals(c, sma20, std20, k, valid_from=WINDOW-1, upper_too=allow_short)

    all_signals = [(i, 1) for i in long_idx] + ([(i, -1) for i in short_idx] if allow_short else [])
    all_signals.sort(key=lambda x: x[0])

    trades = []
    skipped_overlap = 0
    skipped_session = 0
    skipped_insuff = 0
    open_until = -1  # bir pozisyon acikken yeni sinyal alinmaz (non-overlapping, tek pozisyon)

    for sig_idx, direction in all_signals:
        if sig_idx <= open_until:
            skipped_overlap += 1
            continue
        if session_filter is not None and hours[sig_idx] not in session_filter:
            skipped_session += 1
            continue
        tr = simulate_trade(sig_idx, direction, entry_mode, exit_mode, n_bars, rr_ratio)
        if tr is None:
            skipped_insuff += 1
            continue
        trades.append(tr)
        open_until = tr["exit_idx"]

    return trades, {"skipped_overlap": skipped_overlap, "skipped_session": skipped_session, "skipped_insuff_data": skipped_insuff,
                     "toplam_ham_sinyal": len(all_signals)}

def summarize(trades):
    if not trades:
        return {"toplam_islem": 0, "win_rate": None, "profit_factor": None, "net_profit_pts": 0.0,
                "net_profit_usd_per_lot": 0.0, "max_drawdown_pts": None, "ortalama_net_pts": None}
    net = np.array([t["net_pts"] for t in trades])
    wins = net[net > 0]
    losses = net[net <= 0]
    win_rate = len(wins) / len(net)
    gross_profit = wins.sum() if len(wins) else 0.0
    gross_loss = -losses.sum() if len(losses) else 0.0
    pf = (gross_profit / gross_loss) if gross_loss > 0 else (None if gross_profit == 0 else float("inf"))
    cum = np.cumsum(net)
    running_max = np.maximum.accumulate(cum)
    dd = cum - running_max
    max_dd = dd.min() if len(dd) else 0.0
    return {
        "toplam_islem": int(len(net)),
        "win_rate": round(float(win_rate), 4),
        "profit_factor": (round(float(pf), 3) if pf not in (None, float("inf")) else pf),
        "net_profit_pts": round(float(net.sum()), 2),
        "net_profit_usd_per_lot": round(float(net.sum() * POINT * CONTRACT_SIZE), 2),
        "ortalama_net_pts": round(float(net.mean()), 3),
        "max_drawdown_pts": round(float(max_dd), 2),
        "ortalama_atr_entry_pts": round(float(np.mean([t["atr_at_entry_pts"] for t in trades])), 2),
        "ortalama_spread_entry_pts": round(float(np.mean([t["spread_cost_pts"] for t in trades])), 2),
        "spread_TP_orani_medyan": round(float(np.median([t["spread_cost_pts"] / t["atr_at_entry_pts"] for t in trades if t["atr_at_entry_pts"] > 0])), 3),
    }

def split_is_oos(trades):
    if not trades:
        return [], []
    cutoff = int(n * IS_FRACTION)
    is_trades = [t for t in trades if t["signal_idx"] < cutoff]
    oos_trades = [t for t in trades if t["signal_idx"] >= cutoff]
    return is_trades, oos_trades

def walk_forward_folds(trades, folds=WF_FOLDS):
    if not trades:
        return []
    edges = np.linspace(0, n, folds + 1).astype(int)
    out = []
    for f in range(folds):
        lo, hi = edges[f], edges[f+1]
        sub = [t for t in trades if lo <= t["signal_idx"] < hi]
        out.append({"fold": f + 1, "bar_araligi": [int(lo), int(hi)],
                     "tarih_araligi": [str(dates[lo]), str(dates[min(hi, n-1)])],
                     **summarize(sub)})
    return out

print("Senaryolar kosturuluyor...")

# ---------------------------------------------------------------------
# 7) SENARYOLAR
# ---------------------------------------------------------------------
scenarios = {}

# --- 7.1 ANA/BASELINE KONFIGURASYON ---
# k=2.0, entry=next_open (gerceklenebilir/look-ahead-siz), exit=combined,
# N=5, RR=1:1, seans filtresi = birincil (15-18), ham (detrend edilmemis) veri
baseline_trades, baseline_meta = run_scenario(
    k=K_BASELINE, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
    rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=False, allow_short=False)
baseline_is, baseline_oos = split_is_oos(baseline_trades)
scenarios["ANA_KONFIGURASYON"] = {
    "parametreler": {"k": K_BASELINE, "entry_mode": "next_open", "exit_mode": "combined",
                      "n_bars": N_BARS_BASELINE, "rr_ratio": RR_RATIO, "seans_filtresi": "15-18"},
    "meta": baseline_meta,
    "tum_donem": summarize(baseline_trades),
    "IS_ilk_%70": summarize(baseline_is),
    "OOS_son_%30": summarize(baseline_oos),
    "walk_forward": walk_forward_folds(baseline_trades),
}

# --- 7.2 GIRIS YONTEMI KARSILASTIRMASI: close vs next_open ---
close_trades, close_meta = run_scenario(
    k=K_BASELINE, entry_mode='close', exit_mode='combined', n_bars=N_BARS_BASELINE,
    rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=False, allow_short=False)
close_is, close_oos = split_is_oos(close_trades)
scenarios["GIRIS_YONTEMI_KARSILASTIRMA"] = {
    "next_open_bar_acilisinda": {"tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos)},
    "close_kirilma_barinin_kapanisinda": {"tum_donem": summarize(close_trades), "IS": summarize(close_is), "OOS": summarize(close_oos), "meta": close_meta},
}

# --- 7.3 CIKIS YONTEMI KARSILASTIRMASI: time-only / atr-only / combined ---
time_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='time', n_bars=N_BARS_BASELINE,
                               rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=False)
atr_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='atr', n_bars=N_BARS_BASELINE,
                              rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=False)
time_is, time_oos = split_is_oos(time_trades)
atr_is, atr_oos = split_is_oos(atr_trades)
scenarios["CIKIS_YONTEMI_KARSILASTIRMA"] = {
    "yalniz_N_bar_zaman": {"tum_donem": summarize(time_trades), "IS": summarize(time_is), "OOS": summarize(time_oos)},
    "yalniz_ATR_TP_SL": {"tum_donem": summarize(atr_trades), "IS": summarize(atr_is), "OOS": summarize(atr_oos),
                          "not": f"ATR TP/SL {MAX_HOLD_BARS_ATR_ONLY} barda tetiklenmezse zorla kapatilir (muhendislik siniri)"},
    "birlikte_combined": {"tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos)},
}

# --- 7.4 K DUYARLILIK TARAMASI (dar aralik, ince ayar YOK) ---
k_scan_results = {}
for kv in K_SCAN:
    kt, _ = run_scenario(k=kv, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
                          rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=False)
    kt_is, kt_oos = split_is_oos(kt)
    k_scan_results[str(kv)] = {"tum_donem": summarize(kt), "IS": summarize(kt_is), "OOS": summarize(kt_oos)}
scenarios["K_DUYARLILIK_TARAMASI"] = {
    "not": "k secimi OOS sonuclarina bakilarak yapilmadi/optimize edilmedi; sadece raporlama amaciyla 3 deger de gosteriliyor.",
    "sonuclar": k_scan_results,
}

# --- 7.5 SEANS FiLTRESi: VAR (birincil) / VAR (birincil+ikincil) / YOK ---
nofilter_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
                                   rr_ratio=RR_RATIO, session_filter=None, use_detrended=False)
secondary_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
                                    rr_ratio=RR_RATIO, session_filter=SESSION_SECONDARY, use_detrended=False)
nf_is, nf_oos = split_is_oos(nofilter_trades)
sec_is, sec_oos = split_is_oos(secondary_trades)
scenarios["SEANS_FiLTRESi_KARSILASTIRMA"] = {
    "filtresiz_tum_saatler": {"tum_donem": summarize(nofilter_trades), "IS": summarize(nf_is), "OOS": summarize(nf_oos)},
    "birincil_15_18": {"tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos)},
    "birincil_ve_ikincil_15_18_ve_3_4": {"tum_donem": summarize(secondary_trades), "IS": summarize(sec_is), "OOS": summarize(sec_oos)},
}

# --- 7.6 DETREND TESTI (ZORUNLU) ---
detrend_long_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
                                       rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=True, allow_short=False)
detrend_symmetric_trades, _ = run_scenario(k=K_BASELINE, entry_mode='next_open', exit_mode='combined', n_bars=N_BARS_BASELINE,
                                            rr_ratio=RR_RATIO, session_filter=SESSION_PRIMARY, use_detrended=True, allow_short=True)
dl_is, dl_oos = split_is_oos(detrend_long_trades)
ds_is, ds_oos = split_is_oos(detrend_symmetric_trades)
# detrend_symmetric icindeki long/short ayrimi
ds_long = [x for x in detrend_symmetric_trades if x["direction"] == 1]
ds_short = [x for x in detrend_symmetric_trades if x["direction"] == -1]
scenarios["DETREND_TESTi_ZORUNLU"] = {
    "gerekce": f"Rolling lineer trend (pencere={DETREND_WINDOW} bar) fiyattan cikarilip ayni SMA20/std20 sapma "
               f"mantigi detrended seri uzerinde kosturuldu. Sinyal ZAMANLAMASI detrended seriden, GERCEK islem "
               f"P&L'i ise ham (gercek) fiyattan hesaplandi - cunku piyasada yalniz gercek fiyat islem gorur.",
    "ham_fiyat_long_only_baseline": {"tum_donem": summarize(baseline_trades), "IS": summarize(baseline_is), "OOS": summarize(baseline_oos)},
    "detrended_long_only": {"tum_donem": summarize(detrend_long_trades), "IS": summarize(dl_is), "OOS": summarize(dl_oos)},
    "detrended_simetrik_long_ve_short": {
        "birlikte": {"tum_donem": summarize(detrend_symmetric_trades), "IS": summarize(ds_is), "OOS": summarize(ds_oos)},
        "yalniz_long_bacagi": summarize(ds_long),
        "yalniz_short_bacagi": summarize(ds_short),
    },
}

# ---------------------------------------------------------------------
# 8) ISLEM LOGU (ornek - ilk 50 ve son 50 islem, tam log JSON'da mevcut degil,
#    dosya boyutu icin ozet tutuluyor; ana konfigurasyon)
# ---------------------------------------------------------------------
def trade_log_sample(trades, n_head=25, n_tail=25):
    def fmt(t):
        return {"tarih": str(dates[t["signal_idx"]]), "saat": t["entry_hour"], "yon": "LONG" if t["direction"] == 1 else "SHORT",
                "giris": t["entry_price"], "cikis": t["exit_price"], "sebep": t["exit_reason"],
                "net_pts": t["net_pts"], "net_usd_per_lot": t["net_usd_per_lot"]}
    return [fmt(x) for x in trades[:n_head]] + (["...".format()] if len(trades) > n_head + n_tail else []) + [fmt(x) for x in trades[-n_tail:] if len(trades) > n_head]

scenarios["ANA_KONFIGURASYON"]["islem_logu_ornek"] = trade_log_sample(baseline_trades)

results["senaryolar"] = scenarios
results["sabitler"] = {
    "WINDOW": WINDOW, "K_BASELINE": K_BASELINE, "K_SCAN": K_SCAN, "ATR_PERIOD": ATR_PERIOD,
    "RR_RATIO": RR_RATIO, "N_BARS_BASELINE": N_BARS_BASELINE, "SESSION_PRIMARY": sorted(SESSION_PRIMARY),
    "SESSION_SECONDARY": sorted(SESSION_SECONDARY), "DETREND_WINDOW": DETREND_WINDOW,
    "IS_FRACTION": IS_FRACTION, "WF_FOLDS": WF_FOLDS, "MAX_HOLD_BARS_ATR_ONLY": MAX_HOLD_BARS_ATR_ONLY,
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI ->", OUT_PATH)
print(json.dumps(scenarios["ANA_KONFIGURASYON"]["tum_donem"], ensure_ascii=False, indent=2))
print(json.dumps(scenarios["ANA_KONFIGURASYON"]["OOS_son_%30"], ensure_ascii=False, indent=2))

mt5.shutdown()
