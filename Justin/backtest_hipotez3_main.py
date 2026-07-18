# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - HIPOTEZ 3 - ANA TEST, PASS 2

On-kontroller 1-3 (backtest_hipotez3_precheck.py, backtest_hipotez3_precheck_output.json)
GECILDI: 11/48 hucre PC2 (FDR/BH resmi duzeltme, kendi IS-donem verisinde) + PC3 (seans
15-18 filtresi, IS-donem) BIRLIKTE gecti - TAMAMI M1 (gorev Kapsam "M1 birincil" beklentisiyle
tutarli, M5'te hicbir hucre hayatta kalmadi -> M5 ana testte KURULMUYOR, exploratory bile
degil, cunku pre-check'i gecen hicbir M5 hucre yok).

Hayatta kalan hucreler (PC3 IS-donem, seans-filtreli):
  BULGU3_genel: M1-VOL-genis, M1-VOL-dar, M1-TREND-trend, M1-TREND-range  (yani VOL/TREND'in
    HER IKI kategorisi de hayatta kaliyor - Stratejist'in Bolum-1 bulgusuyla tutarli: sinyal
    rejimden BAGIMSIZ/uniform, tek bir rejime ozgu degil)
  BULGU3_streak: M1-VOL-genis-L5, M1-TREND-trend-L4, M1-TREND-trend-L5 (32 hucreden yalniz 3'u,
    kucuk n - 195-208 IS-donem/seans-filtreli)
  BULGU4: M1-VOL-genis, M1-VOL-dar, M1-TREND-trend, M1-TREND-range (BULGU3-genel ile ayni
    "uniform" patern)

ANA TEST TASARIMI (rejim = IKINCIL FILTRE, birincil sinyal degil - gorev Kapsam geregi):
  3 sinyal ailesi kuruldu (M1, seans 15-18 birincil/tek populasyon - PC3'un dogruladigi
  alt-orneklem, ayni tutarlilikla):
    1) GENEL-FADE   : BULGU3-genel'in tradeable hali - HER dogu-olmayan barin yonune fade,
                       bir sonraki bar acilisinda giris (t+1, teyitsiz).
    2) STREAK-FADE  : BULGU3-streak'in tradeable hali - N ardisik ayni-yonlu bar (N=2,3,4,5,
                       Arastirmaci'nin ONCEDEN belirledigi dar tarama, esik GENISLETILMEDI)
                       sonrasi fade, t+1 giris.
    3) BIGBAR-FADE  : BULGU4'un tradeable hali - buyuk bar (range > 1,5x causal-rolling-20-bar
                       ortalama, backtest_hipotez2.py'deki CAUSAL yontemle AYNI - PC2/PC3'teki
                       resmi-duzeltme-testi icin kullanilan tam-veri/IS-subset ortalamasi
                       FARKLIDIR ve sadece istatistiksel testte kullanildi, gercek islem
                       simulasyonunda ASLA kullanilmaz - look-ahead yasak) sonrasi fade,
                       t+1 giris.

  HER sinyal ailesi icin TEK bir pozisyon-yonetimli (cakisan sinyal atlanir) simulasyon
  kosturulur (rejim etiketi/sinyal turu ne olursa olsun ayni giris/cikis/maliyet mantigi).
  Rejim filtresi sonradan (post-hoc) bu SAME trade seti uzerinde uygulanir: her islemin
  SINYAL ANINDAKI VOL/TREND etiketi kaydedilir, sonra alt-kumelere (VOL=genis/dar,
  TREND=trend/range) bolunerek PF karsilastirilir. Bu, "rejim ayri bir simulasyon degil
  AYNI islem setinin ikincil bir filtresi/dogrulayicisi" ilkesini (gorev Kapsam) birebir
  uygular ve gereksiz/celiskili pozisyon-yonetimi farkliliklarini (farkli simulasyonlarda
  farkli cakisma/pozisyon sonuclari) onler - metodolojik tercih, asagida raporda ayrica not
  dusulmustur.

SL/TP semasi: ATR(14,M1, causal) x 0,5 (ATR_FRACTION), RR=1:1 - H1/H2'den DEVAM EDEN
muhendislik semasi (Stratejist Hipotez 3 icin yeni bir deger belirtmedi; "parametreleri
degistirme" ilkesi geregi rastgele YENI bir deger secmek yerine onceki turlerde zaten
kullanilmis/rapor edilmis semayi tasimak tercih edildi - bu bir muhendislik karari olarak
ayrica isaretlenmistir, Stratejist onayi gerektirir).

Cikis: "combined" (ATR TP/SL VEYA N=1 bar zaman-asimi, hangisi once) - H1/H2 ana
konfigurasyonuyla AYNI.

Maliyet: tick-bazli gercek bid/ask (giris) + giris-spread'inin yarisi (cikis, H1/H2 ile
ayni sinir/varsayim), MAX_TICK_MISMATCH_SEC=60 (v3 Bolum 4 onaylandi, degismedi).

Izolasyon notu: MilaGold/Lisa/Signal GPT'ye ait hicbir dosya kullanilmadi; veri dogrudan
MT5'ten (MetaTrader5 kutuphanesi).
"""
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import MetaTrader5 as mt5
from datetime import datetime, timezone
from collections import defaultdict
from scipy import stats

# ---------------------------------------------------------------------
# SABITLER
# ---------------------------------------------------------------------
SYMBOL = "GOLD"
ATR_PERIOD = 14
ATR_FRACTION = 0.5          # H1/H2 semasi - DEVAM ETTIRILDI (Stratejist'e ayrica bildirilecek)
RR_RATIO = 1.0
N_BARS_TIME = 1             # "combined" exit icin zaman-asimi ufku - H1/H2 ile ayni
BIGBAR_MULT = 1.5           # BULGU4 esigi - FIXED, TARANMIYOR
RANGE_WINDOW = 20           # BULGU4 causal rolling-ortalama penceresi - H2 ile ayni, FIXED
STREAK_LENGTHS = [2, 3, 4, 5]
SESSION_PRIMARY = set(range(15, 19))  # PC3'un dogruladigi TEK populasyon (ana test bu ALT-ORNEKLEM uzerinde)
MAX_TICK_MISMATCH_SEC = 60   # v3 Bolum 4 onaylandi
IS_FRACTION = 0.70
WF_FOLDS = 6
ALPHA = 0.05
N_BARS = 99999

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_hipotez3_output.json"

# ---------------------------------------------------------------------
# MT5 BAGLANTISI + VERI (M1 birincil - M5'te pre-check'i gecen hucre YOK, M5 kurulmuyor)
# ---------------------------------------------------------------------
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size

rates1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, N_BARS)
n = len(rates1)
t = rates1['time'].astype(np.int64)
o = rates1['open'].astype(float)
h = rates1['high'].astype(float)
l = rates1['low'].astype(float)
c = rates1['close'].astype(float)
hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])
print("M1 bar sayisi:", n, "araligi:", dates[0], "->", dates[-1])

# ---------------------------------------------------------------------
# CAUSAL OZELLIKLER: ATR(14), rejim etiketleri (VOL/TREND), yon+streak, buyuk-bar (causal)
#    Rejim etiketleme research_scalping_rejim.py ile AYNEN (esikler degistirilmedi)
# ---------------------------------------------------------------------
ATR_PERIOD_REGIME = 14
ER_WINDOW = 20
TRAIL_WINDOW = 100

def rolling_median_trailing(arr, window):
    nn = len(arr)
    out = np.full(nn, np.nan)
    if nn < window:
        return out
    windows = sliding_window_view(arr, window)
    out[window - 1:] = np.median(windows, axis=1)
    return out

def compute_atr(hh, ll, cc, period):
    nn = len(cc)
    tr = np.empty(nn)
    tr[0] = hh[0] - ll[0]
    tr[1:] = np.maximum(np.maximum(hh[1:] - ll[1:], np.abs(hh[1:] - cc[:-1])), np.abs(ll[1:] - cc[:-1]))
    atr = np.full(nn, np.nan)
    if nn >= period:
        atr_windows = sliding_window_view(tr, period)
        atr[period - 1:] = atr_windows.mean(axis=1)
    return atr, tr

atr14, tr_arr = compute_atr(h, l, c, ATR_PERIOD)
print("ATR14 (M1, causal) hesaplandi.")

def compute_regime_labels(hh, ll, cc):
    nn = len(cc)
    atr_r, _ = compute_atr(hh, ll, cc, ATR_PERIOD_REGIME)
    atr_trail_med = rolling_median_trailing(atr_r, TRAIL_WINDOW)
    label_vol = np.full(nn, None, dtype=object)
    valid_vol = ~np.isnan(atr_trail_med) & ~np.isnan(atr_r)
    label_vol[valid_vol & (atr_r > atr_trail_med)] = "genis"
    label_vol[valid_vol & (atr_r <= atr_trail_med)] = "dar"

    diffs = np.abs(np.diff(cc))
    net_move = np.full(nn, np.nan)
    if nn > ER_WINDOW:
        net_move[ER_WINDOW:] = np.abs(cc[ER_WINDOW:] - cc[:-ER_WINDOW])
    path_sum = np.full(nn, np.nan)
    if len(diffs) >= ER_WINDOW:
        diff_windows = sliding_window_view(diffs, ER_WINDOW)
        path_sum[ER_WINDOW:] = diff_windows.sum(axis=1)
    er20 = np.full(nn, np.nan)
    valid_path = ~np.isnan(path_sum) & (path_sum > 0)
    er20[valid_path] = net_move[valid_path] / path_sum[valid_path]
    er_trail_med = rolling_median_trailing(er20, TRAIL_WINDOW)
    label_trend = np.full(nn, None, dtype=object)
    valid_trend = ~np.isnan(er_trail_med) & ~np.isnan(er20)
    label_trend[valid_trend & (er20 > er_trail_med)] = "trend"
    label_trend[valid_trend & (er20 <= er_trail_med)] = "range"
    return label_vol, label_trend

vol_label, trend_label = compute_regime_labels(h, l, c)
print("Rejim etiketleri (VOL/TREND, causal, research_scalping_rejim.py ile AYNI) hesaplandi.")

direction = np.sign(c - o).astype(int)
streak = np.zeros(n, dtype=int)
_last_dir = 0; _last_streak = 0
for i in range(n):
    if direction[i] == 0:
        streak[i] = 0
        continue
    if direction[i] == _last_dir:
        _last_streak += 1
    else:
        _last_streak = 1
    streak[i] = _last_streak
    _last_dir = direction[i]
print("Yon + streak (causal) hesaplandi.")

# Buyuk-bar tespiti - CAUSAL (H2/backtest_hipotez2.py'deki detect_bigbars ile AYNI yontem -
# onceki RANGE_WINDOW barin ortalama range'i, bar'in KENDISI HARIC). PC2/PC3'teki IS-subset/
# tam-veri ORTALAMASI (non-causal, sadece istatistik/anlamlilik testi icin) BURADA
# KULLANILMAZ - gercek islem simulasyonunda look-ahead kesinlikle yasak.
def detect_bigbars_causal(oo, hh, ll, cc, window, mult):
    nn = len(cc)
    rng = hh - ll
    avg_rng = np.full(nn, np.nan)
    cum = np.cumsum(np.insert(rng, 0, 0.0))
    for i in range(window, nn):
        avg_rng[i] = (cum[i] - cum[i - window]) / window
    is_big = np.zeros(nn, dtype=bool)
    fade_dir = np.zeros(nn, dtype=int)
    for i in range(window, nn):
        if np.isnan(avg_rng[i]) or avg_rng[i] <= 0:
            continue
        if rng[i] > mult * avg_rng[i]:
            if cc[i] > oo[i]:
                is_big[i] = True; fade_dir[i] = -1
            elif cc[i] < oo[i]:
                is_big[i] = True; fade_dir[i] = 1
    return is_big, fade_dir

is_big, bigbar_fade_dir = detect_bigbars_causal(o, h, l, c, RANGE_WINDOW, BIGBAR_MULT)
print("Buyuk-bar (causal, BULGU4) tespiti tamamlandi. Toplam:", int(is_big.sum()))

# ---------------------------------------------------------------------
# TICK-BAZLI GERCEK MALIYET MODELI (H1/H2 ile AYNI yontem + AYNI kok-neden duzeltmesi)
# ---------------------------------------------------------------------
TICK_QUOTE_CACHE = {}
TICK_LOOKUP_COUNT = {"call": 0, "hit": 0, "miss_veri_yok": 0, "miss_zaman_uyusmazligi": 0, "miss_gecersiz_kotasyon": 0}
TICK_TIME_MISMATCH_LOG = []

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
        fark = tick_epoch - bar_epoch
        if fark > MAX_TICK_MISMATCH_SEC or fark < -1:
            TICK_LOOKUP_COUNT["miss_zaman_uyusmazligi"] += 1
            TICK_TIME_MISMATCH_LOG.append({"bar_idx": int(bar_idx), "fark_saniye": int(fark)})
        else:
            bid = float(row['bid']); ask = float(row['ask'])
            if ask > 0 and bid > 0 and ask >= bid:
                result = (ask, bid)
            else:
                TICK_LOOKUP_COUNT["miss_gecersiz_kotasyon"] += 1
    TICK_QUOTE_CACHE[bar_idx] = result
    return result

# ---------------------------------------------------------------------
# TEK ISLEM SIMULASYONU (t+1 giris, teyitsiz - BULGU3/4'un olctugu ufuk, look-ahead yok)
# ---------------------------------------------------------------------
def simulate_trade(signal_idx, fade_dir_val, session_filter):
    if session_filter is not None and hours[signal_idx] not in session_filter:
        return None, "seans_disi"
    entry_idx = signal_idx + 1
    if entry_idx >= n:
        return None, "veri_sinirinda"
    atr_sig = atr14[signal_idx]
    if np.isnan(atr_sig) or atr_sig <= 0:
        return None, "atr_yok"

    direction_trade = fade_dir_val
    entry_theo = o[entry_idx]
    tp_dist = RR_RATIO * ATR_FRACTION * atr_sig
    sl_dist = ATR_FRACTION * atr_sig
    if direction_trade == 1:
        tp_price = entry_theo + tp_dist; sl_price = entry_theo - sl_dist
    else:
        tp_price = entry_theo - tp_dist; sl_price = entry_theo + sl_dist

    time_exit_idx = entry_idx + N_BARS_TIME
    if time_exit_idx >= n:
        return None, "yetersiz_veri"

    exit_idx = exit_theo = exit_reason = None
    for j in range(entry_idx, time_exit_idx + 1):
        hit_tp = (h[j] >= tp_price) if direction_trade == 1 else (l[j] <= tp_price)
        hit_sl = (l[j] <= sl_price) if direction_trade == 1 else (h[j] >= sl_price)
        if hit_tp and hit_sl:
            exit_idx, exit_theo, exit_reason = j, sl_price, "SL(ayni-bar-oncelik)"; break
        elif hit_sl:
            exit_idx, exit_theo, exit_reason = j, sl_price, "SL"; break
        elif hit_tp:
            exit_idx, exit_theo, exit_reason = j, tp_price, "TP"; break
    if exit_idx is None:
        exit_idx = time_exit_idx; exit_theo = c[exit_idx]; exit_reason = "zaman(TP/SL_tetiklenmedi)"

    raw_pts = (exit_theo - entry_theo) / POINT if direction_trade == 1 else (entry_theo - exit_theo) / POINT

    quote = get_tick_quote(entry_idx)
    if quote is None:
        return None, "tick_verisi_yok"
    ask, bid = quote
    spread_pts_tick = (ask - bid) / POINT
    if direction_trade == 1:
        entry_real = ask; slip_pts = (entry_real - entry_theo) / POINT
    else:
        entry_real = bid; slip_pts = (entry_theo - entry_real) / POINT
    total_cost_pts = slip_pts + spread_pts_tick / 2.0
    net_pts = raw_pts - total_cost_pts

    return {
        "signal_idx": int(signal_idx), "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
        "tarih": dates[signal_idx], "saat_sinyal": int(hours[signal_idx]),
        "yon": "LONG" if direction_trade == 1 else "SHORT", "sebep": exit_reason,
        "vol_label": vol_label[signal_idx], "trend_label": trend_label[signal_idx],
        "atr_entry_pts": float(atr_sig / POINT),
        "tick_spread_pts": round(float(spread_pts_tick), 3),
        "giris_slipaj_pts": round(float(slip_pts), 3),
        "toplam_maliyet_pts": round(float(total_cost_pts), 3),
        "raw_pts": round(float(raw_pts), 3), "net_pts": round(float(net_pts), 3),
        "net_usd_per_lot": round(float(net_pts * POINT * CONTRACT_SIZE), 2),
    }, "ok"

def run_scenario(signal_mask, fade_dir_arr, session_filter=SESSION_PRIMARY):
    trades = []
    reasons = defaultdict(int)
    open_until = -1
    idxs = np.where(signal_mask)[0]
    for i in idxs:
        if i <= open_until:
            reasons["cakisma_atlandi"] += 1
            continue
        res, status = simulate_trade(i, fade_dir_arr[i], session_filter)
        if res is None:
            reasons[status] += 1
            continue
        trades.append(res)
        open_until = res["exit_idx"]
    return trades, dict(reasons)

# ---------------------------------------------------------------------
# OZETLEME / IS-OOS / WALK-FORWARD (H1/H2 ile ayni yontem)
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
        "toplam_islem": int(len(net)), "win_rate": round(float(win_rate), 4),
        "profit_factor": (round(float(pf), 3) if pf not in (None, float("inf")) else pf),
        "net_profit_pts": round(float(net.sum()), 2),
        "net_profit_usd_per_lot": round(float(net.sum() * POINT * CONTRACT_SIZE), 2),
        "ortalama_net_pts": round(float(net.mean()), 3), "medyan_net_pts": round(float(np.median(net)), 3),
        "max_drawdown_pts": round(float(dd.min()), 2) if len(dd) else 0.0,
        "ortalama_atr_entry_pts": round(float(np.mean([x["atr_entry_pts"] for x in trades])), 2),
        "ortalama_toplam_maliyet_pts": round(float(np.mean([x["toplam_maliyet_pts"] for x in trades])), 3),
    }

def split_is_oos(trades):
    if not trades:
        return [], []
    cutoff = int(n * IS_FRACTION)
    return [x for x in trades if x["signal_idx"] < cutoff], [x for x in trades if x["signal_idx"] >= cutoff]

def walk_forward_folds(trades, folds=WF_FOLDS):
    if not trades:
        return []
    edges = np.linspace(0, n, folds + 1).astype(int)
    out = []
    for f in range(folds):
        lo, hi = edges[f], edges[f + 1]
        sub = [x for x in trades if lo <= x["signal_idx"] < hi]
        out.append({"fold": f + 1, "tarih_araligi": [dates[lo], dates[min(hi, n - 1)]], **summarize(sub)})
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

def monthly_breakdown(trades):
    agg = defaultdict(list)
    for x in trades:
        agg[x["tarih"][:7]].append(x["net_pts"])
    out = {}
    for k in sorted(agg.keys()):
        arr = np.array(agg[k])
        out[k] = {"islem": int(len(arr)), "net_pts": round(float(arr.sum()), 2), "win_rate": round(float((arr > 0).mean()), 4)}
    return out

def regime_slice(trades, key, value):
    return [x for x in trades if x[key] == value]

def regime_breakdown(trades):
    out = {}
    for val in ["genis", "dar"]:
        out[f"VOL_{val}"] = summarize(regime_slice(trades, "vol_label", val))
    for val in ["trend", "range"]:
        out[f"TREND_{val}"] = summarize(regime_slice(trades, "trend_label", val))
    return out

def minimum_sample_warning(count, label, threshold=30):
    if count == 0:
        return f"{label}: ISLEM YOK (n=0)."
    if count < threshold:
        return f"{label}: YETERSIZ ORNEKLEM (n={count} < {threshold}) - sonuc yorumlanabilir ama tek basina karar dayanagi OLAMAZ."
    return None

print("Yardimci fonksiyonlar hazir. Senaryolar kosturuluyor...")

# ---------------------------------------------------------------------
# SENARYO 1: GENEL-FADE (BULGU3-genel'in tradeable hali - her dogu-olmayan bar)
# ---------------------------------------------------------------------
genel_mask = direction != 0
genel_fade_dir = -direction  # fade: streak/bar yonunun tersi
genel_trades, genel_reasons = run_scenario(genel_mask, genel_fade_dir, SESSION_PRIMARY)
print("GENEL-FADE tamamlandi. Islem:", len(genel_trades), "tick lookup:", TICK_LOOKUP_COUNT)

genel_is, genel_oos = split_is_oos(genel_trades)
genel_result = {
    "meta_atlanma_nedenleri": genel_reasons,
    "tum_donem": summarize(genel_trades),
    "IS_ilk_%70": summarize(genel_is), "OOS_son_%30": summarize(genel_oos),
    "walk_forward": walk_forward_folds(genel_trades),
    "ardisik_seriler": consecutive_streaks(genel_trades),
    "aylik_kirilim": monthly_breakdown(genel_trades),
    "rejim_kirilimi_POST_HOC": regime_breakdown(genel_trades),
}

# ---------------------------------------------------------------------
# SENARYO 2: STREAK-FADE (BULGU3-streak'in tradeable hali), N=2,3,4,5
# ---------------------------------------------------------------------
streak_results = {}
for L in STREAK_LENGTHS:
    mask = (streak == L)
    fade_dir_arr = -direction
    tr, rs = run_scenario(mask, fade_dir_arr, SESSION_PRIMARY)
    tr_is, tr_oos = split_is_oos(tr)
    streak_results[f"L{L}"] = {
        "meta_atlanma_nedenleri": rs,
        "tum_donem": summarize(tr), "IS_ilk_%70": summarize(tr_is), "OOS_son_%30": summarize(tr_oos),
        "walk_forward": walk_forward_folds(tr),
        "ardisik_seriler": consecutive_streaks(tr),
        "rejim_kirilimi_POST_HOC": regime_breakdown(tr),
        "islem_logu_tam": tr,  # ilk gecisteki tam islem listesi dogrudan saklandi (ORKESTRATOR BULGUSU
                                # duzeltmesi - ikinci/tekrar run_scenario cagrisi GEREKSIZDI, silindi)
    }
    print(f"STREAK-FADE L={L} tamamlandi. Islem:", len(tr), "tick lookup:", TICK_LOOKUP_COUNT)

# ---------------------------------------------------------------------
# SENARYO 3: BIGBAR-FADE (BULGU4'un tradeable hali, causal esik)
# ---------------------------------------------------------------------
bigbar_trades, bigbar_reasons = run_scenario(is_big, bigbar_fade_dir, SESSION_PRIMARY)
bigbar_is, bigbar_oos = split_is_oos(bigbar_trades)
bigbar_result = {
    "meta_atlanma_nedenleri": bigbar_reasons,
    "tum_donem": summarize(bigbar_trades),
    "IS_ilk_%70": summarize(bigbar_is), "OOS_son_%30": summarize(bigbar_oos),
    "walk_forward": walk_forward_folds(bigbar_trades),
    "ardisik_seriler": consecutive_streaks(bigbar_trades),
    "aylik_kirilim": monthly_breakdown(bigbar_trades),
    "rejim_kirilimi_POST_HOC": regime_breakdown(bigbar_trades),
}
print("BIGBAR-FADE tamamlandi. Islem:", len(bigbar_trades), "tick lookup:", TICK_LOOKUP_COUNT)

# ---------------------------------------------------------------------
# MINIMUM ORNEKLEM UYARILARI
# ---------------------------------------------------------------------
warnings = []
for label, trs in [("GENEL-FADE tum-donem", genel_trades), ("GENEL-FADE OOS", genel_oos),
                    ("BIGBAR-FADE tum-donem", bigbar_trades), ("BIGBAR-FADE OOS", bigbar_oos)]:
    w = minimum_sample_warning(len(trs), label)
    if w:
        warnings.append(w)
for L in STREAK_LENGTHS:
    tr_all = streak_results[f"L{L}"]["tum_donem"]["toplam_islem"]
    w = minimum_sample_warning(tr_all, f"STREAK-FADE L={L} tum-donem")
    if w:
        warnings.append(w)
    oos_n = streak_results[f"L{L}"]["OOS_son_%30"]["toplam_islem"]
    w2 = minimum_sample_warning(oos_n, f"STREAK-FADE L={L} OOS")
    if w2:
        warnings.append(w2)

# ---------------------------------------------------------------------
# TAM ISLEM LOGU (H1/H2 standardi - Risk Analisti'nin bagimsiz dogrulamasi icin TAMAMI)
# ---------------------------------------------------------------------
results = {
    "on_kontrol_referansi": r"C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json",
    "sabitler": {
        "ATR_PERIOD": ATR_PERIOD, "ATR_FRACTION": ATR_FRACTION, "RR_RATIO": RR_RATIO,
        "N_BARS_TIME": N_BARS_TIME, "BIGBAR_MULT": BIGBAR_MULT, "RANGE_WINDOW": RANGE_WINDOW,
        "STREAK_LENGTHS": STREAK_LENGTHS, "SESSION_PRIMARY": sorted(SESSION_PRIMARY),
        "MAX_TICK_MISMATCH_SEC": MAX_TICK_MISMATCH_SEC, "IS_FRACTION": IS_FRACTION, "WF_FOLDS": WF_FOLDS,
    },
    "veri_ozeti": {"toplam_bar": int(n), "baslangic": dates[0], "bitis": dates[-1]},
    "senaryolar": {
        "GENEL_FADE": {**genel_result, "islem_logu_tam": genel_trades},
        "STREAK_FADE": streak_results,
        "BIGBAR_FADE": {**bigbar_result, "islem_logu_tam": bigbar_trades},
    },
    "minimum_orneklem_uyarilari": warnings,
    "tick_lookup_istatistigi": TICK_LOOKUP_COUNT,
    "tick_zaman_eslesme_reddedilen_sayisi": len(TICK_TIME_MISMATCH_LOG),
}
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)
print("Toplam tick lookup:", TICK_LOOKUP_COUNT)
print("Uyarilar:", warnings)

mt5.shutdown()
