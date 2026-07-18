# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - A Ailesi (Momentum/Trend-Following) - HIPOTEZ H3
"M30-Yukselen Odakli Asimetrik Filtre" (SADECE M30 yukselen kanal + M15 giris + YALNIZCA BUY)

Kaynak gorev: gorev_backtest_muhendisi_justin_gold_scalping_A_ailesi_H3.md
Girdi: stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md (H3 bolumu)

Kapsam (tek script, fazlar halinde):
  FAZ 0: MT5 baglanti + ham veri (M30/M15) - SADECE bu iki TF (H1 bu hipotezde kullanilmiyor)
  FAZ 1: On-kontrol Madde 1 - DST BAGIMSIZ dogrulama ozetinin bu scripte baglanmasi
         (ayrintili/bagimsiz kontrol bt_h3_step0_dst_check.py'de AYRI calistirildi - burada
         SADECE UTC-epoch kullanimimizin DST'den bagisik oldugu gosterilir)
  FAZ 2: M30 pivot/kanal tespiti - SADECE YUKSELEN (up) yon - LOOK-AHEAD DUZELTMESI ile
         (5-bar gecikmeli confirm, H1/H2 ile ayni gerekce/yontem)
  FAZ 2b: Devam-orani (continuation-rate) coklu-blok karsilastirmasi (in-sample vs
          out-of-sample replikasyon testi) - Stratejist'in "n=15-20 kucuk orneklem, tek
          bolunmeye guvenme" talebine yanit - TUM M30-yukselen kanallar (M15 kesisimiyle
          SINIRLI DEGIL) uzerinde, kronolojik 4 esit-zaman bloguna ayrilarak.
  FAZ 3: M15 giris-zamanlama projeksiyonu (SADECE M30-yukselen kanallari icinde) -
         LOOK-AHEAD-SAFE (confirmed kanal + bir-sonraki-bar-acilisi giris), YALNIZCA BUY
  FAZ 4: On-kontrol Madde 2 - S1 maliyet-orani, GERCEK SL/TP mesafeleriyle (H3'e OZEL kalibre,
         H2'den otomatik tasima YOK)
  FAZ 5: COK-FOLD purged/embargolu walk-forward blok sinirlari (H2'nin TEK train/val/test
         bolunmesinden FARKLI - Stratejist'in acik talebi geregi)
  FAZ 6: Trade simulasyonu (tek-pozisyon, uc-kosullu cikis: SL/TP/kirilim-bazli-erken-cikis) -
         H2 ile AYNI mekanik (BUY-only sign=+1 sabit)
  FAZ 7: Her fold icin: Train'de SL/TP grid-tara -> o fold'un Test'inde TEK KEZ uygula
         (expanding-window walk-forward, 3 fold) + fold'lar arasi PF/WR tutarliligi
  FAZ 8: Kirilim-bazli-erken-cikis dogrulama ornekleri
  FAZ 9: Islem frekansi + kirilim analizi + JSON/CSV kaydi

Izolasyon: Yalniz C:\\MilaYatirim\\Justin\\ icinde calisilmistir. Veri dogrudan MT5'ten (GOLD).
MilaGold/Lisa/Signal GPT'ye ait hicbir dosya/deger/format referans alinmamistir. Kanal tespiti
ve trade-simulasyon iskeleti, ayni proje icindeki H2 scriptiyle (backtest_A_ailesi_H2.py)
METODOLOJIK OLARAK BILEREK tutarli tutulmustur (karsilastirilabilirlik amacli - izolasyon kurali
yalniz BASKA proje dosyalarini yasaklar, ayni-proje-ici metodolojik tutarliligi degil) - ancak
DST kontrolu BAGIMSIZ tekrar calistirilmis (bt_h3_step0_dst_check.py), S1/SL-TP kalibrasyonu
H3'e OZEL yapilmis, ve walk-forward semasi H2'nin tek-bolunmesinden BILEREK cok-fold'a
genisletilmistir (Stratejist'in acik talebi, gorev madde 4).
"""
import json
import math
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_A_ailesi_H3_output.json"

# ============================================================
# SABITLER (gorev tanimindan / justin_gecmis_calisma.md'den - degistirilmedi)
# ============================================================
SYMBOL = "GOLD"
MIN_TOUCHES = 3            # kanal gecerlilik esigi (Stratejist tasarimi, H1/H2 ile ayni)
TOUCH_K = 0.5               # dokunus toleransi: 0.5 x ATR14 (Stratejist/Arastirmaci tanimi)
SWING_N = 5                 # fraktal pivot penceresi (N=5, sol+sag)
LOOKAHEAD_LAG_BARS = 5       # swing bir bar'in "swing" oldugu ancak N=5 bar SONRA kesinlesir
CAP_DAYS = 300               # kanal arama penceresi sinirlamasi (muhendislik pratikligi)
EMA_FAST, EMA_SLOW = 50, 200
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9

KASA_USD = 2000.0            # justin_gecmis_calisma.md
RISK_PCT_UST_SINIR = 0.01    # islem-basi risk UST SINIRI (kasa x %1)
TABAN_LOT = 0.01
LOT_STEP_USD = 0.01          # lot yuvarlama adimi

EMBARGO_DAYS = 45            # blok/fold arasi purge/embargo (medyan M30-yukselen kanal omru
                              # ~24,8 gun < 45 - ayni gerekce H2 ile tutarli)
N_BLOCKS = 4                  # cok-fold walk-forward icin kronolojik blok sayisi (M15-kesisim
                              # penceresi ~4,25 yil / 4 = ~13 ay/blok)

DST_TRANSITIONS = ["2025-03-30", "2025-10-26", "2026-03-29"]

print("=" * 70)
print("FAZ 0: MT5 BAGLANTI + HAM VERI (M30 + M15 - H3 SADECE BU IKI TF'i KULLANIR)")
print("=" * 70)
assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
mt5.symbol_select(SYMBOL, True)
info = mt5.symbol_info(SYMBOL)
POINT = info.point
CONTRACT_SIZE = info.trade_contract_size
USD_PER_POINT_PER_LOT = CONTRACT_SIZE * POINT
print(f"point={POINT}, contract_size={CONTRACT_SIZE}, USD/puan/1.0-lot={USD_PER_POINT_PER_LOT}")

TFS = {
    "M15": (mt5.TIMEFRAME_M15, 15),
    "M30": (mt5.TIMEFRAME_M30, 30),
}
raw = {}
for tf_name, (tf_const, bar_min) in TFS.items():
    rates = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)
    raw[tf_name] = rates
    t0 = datetime.fromtimestamp(int(rates[0]['time']), tz=timezone.utc)
    t1 = datetime.fromtimestamp(int(rates[-1]['time']), tz=timezone.utc)
    print(tf_name, "n=", len(rates), t0, "->", t1)

results = {"meta": {
    "hipotez_adi": "A Ailesi H3 - M30-Yukselen Odakli Asimetrik Filtre (YALNIZCA BUY)",
    "yaklasim_turu": "kural-tabanli (yon-asimetrik filtre)",
    "min_touches": MIN_TOUCHES, "touch_k": TOUCH_K, "swing_n": SWING_N,
    "lookahead_lag_bars": LOOKAHEAD_LAG_BARS, "cap_days": CAP_DAYS,
    "ema_fast": EMA_FAST, "ema_slow": EMA_SLOW, "macd": [MACD_FAST, MACD_SLOW, MACD_SIG],
    "kasa_usd": KASA_USD, "risk_pct_ust_sinir": RISK_PCT_UST_SINIR, "taban_lot": TABAN_LOT,
    "embargo_days": EMBARGO_DAYS, "n_blocks_walk_forward": N_BLOCKS,
    "yon": "YALNIZCA BUY/uzun (M30 yukselen kanal disinda SELL/alcalan bu hipotezde YOK)",
}}
results["veri_araligi"] = {tf: {"n_bar": int(len(raw[tf])),
                                 "baslangic": str(datetime.fromtimestamp(int(raw[tf][0]['time']), tz=timezone.utc)),
                                 "bitis": str(datetime.fromtimestamp(int(raw[tf][-1]['time']), tz=timezone.utc))}
                           for tf in TFS}

# ============================================================
# FAZ 1: ON-KONTROL MADDE 1 - DST/SAAT-ESLEME (BAGIMSIZ dogrulama AYRI script'te yapildi)
# ============================================================
print("=" * 70)
print("FAZ 1: DST / SAAT-ESLEME - BAGIMSIZ DOGRULAMA OZETI")
print("=" * 70)

with open(r"C:\MilaYatirim\Justin\bt_h3_step0_dst_check_output.json", encoding="utf-8") as f:
    dst_independent = json.load(f)

results["faz1_on_kontrol_dst"] = {
    "bagimsiz_script": "bt_h3_step0_dst_check.py (bu tur icin AYRI/SIFIRDAN calistirildi, "
                        "H1/H2'den sonuc DEVRALINMADI)",
    "bagimsiz_sonuc_ozeti": dst_independent,
    "bu_scriptteki_projeksiyon_notu": (
        "M30->M15 kanal cizgisi projeksiyonu asagida (FAZ 3) UTC EPOCH SANIYELERI (rates['time'], "
        "mutlak zaman damgasi) uzerinden hesaplanir - saat/DST etiketlemesinden BAGIMSIZDIR. "
        "Bagimsiz kontrol (yukarida) sunucunun hafta-sonu kapanis SAATININ DST gecislerinde "
        "kaydigini (22->23, 23->22) DOGRULADI - bu, insan-okunur saat filtreleri (orn. seans "
        "saati bazli bir filtre) icin onemli olurdu, ama BU hipotezde boyle bir saat-of-day "
        "filtresi YOKTUR; kanal projeksiyonu ve giris tetigi tamamen epoch-farki (saniye) "
        "uzerinden calisir, dolayisiyla DST kaymasindan ETKILENMEZ. Bu ayrim raporda acikca "
        "belirtilecektir (madde 1 'gecti' sayilmasinin GEREKCESI, 'DST yok' anlamina gelmez)."),
}
print("FAZ 1 tamamlandi (bagimsiz kontrol H1/H2 ile TUTARLI: DST kaymasi var, epoch-tabanli "
      "projeksiyon buna bagisik).")

# ============================================================
# ORTAK YARDIMCI FONKSIYONLAR
# ============================================================


def ema(values, span):
    return pd.Series(values).ewm(span=span, adjust=False).mean().values


def macd(values, fast=MACD_FAST, slow=MACD_SLOW, sig=MACD_SIG):
    macd_line = ema(values, fast) - ema(values, slow)
    signal_line = pd.Series(macd_line).ewm(span=sig, adjust=False).mean().values
    return macd_line, signal_line


def atr_series_pts(rates, window=14, point=POINT):
    highs = rates['high'].astype(float)
    lows = rates['low'].astype(float)
    closes = rates['close'].astype(float)
    prev_close = np.roll(closes, 1)
    prev_close[0] = closes[0]
    tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
    atr = pd.Series(tr).rolling(window, min_periods=window).mean().values
    return atr / point


def find_swings(rates, n=SWING_N):
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
EMA50 = {tf: ema(raw[tf]['close'].astype(float), EMA_FAST) for tf in TFS}
EMA200 = {tf: ema(raw[tf]['close'].astype(float), EMA_SLOW) for tf in TFS}
MACD_LINE, MACD_SIG_ARR = {}, {}
for tf in TFS:
    ml, sl_ = macd(raw[tf]['close'].astype(float))
    MACD_LINE[tf] = ml
    MACD_SIG_ARR[tf] = sl_

sh_m30, sl_m30 = find_swings(raw["M30"])
SWINGS = {"M30": {"swing_high": sh_m30, "swing_low": sl_m30}}
print("M30 swing_high n=", int(sh_m30.sum()), "swing_low n=", int(sl_m30.sum()))

# ============================================================
# FAZ 2: M30 PIVOT/KANAL TESPITI - SADECE YUKSELEN (up) - LOOK-AHEAD DUZELTMESI ILE
# ============================================================
print("=" * 70)
print("FAZ 2: M30 PIVOT/KANAL TESPITI - SADECE YUKSELEN YON (LOOK-AHEAD DUZELTMESI ILE)")
print("=" * 70)

CAP_MINUTES = CAP_DAYS * 24 * 60


def detect_channels(tf_name, direction):
    """H2 ile AYNI algoritma (bkz. backtest_A_ailesi_H2.py detect_channels) - bu script SADECE
    tf_name='M30', direction='up' ile cagirir (H3'un tasarim kisiti)."""
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
    macd_s = MACD_SIG_ARR[tf_name]
    n_total = len(closes)

    if direction == "up":
        sign = 1
        swing_mask = SWINGS[tf_name]["swing_low"]
        price_arr = lows
    else:
        sign = -1
        swing_mask = SWINGS[tf_name]["swing_high"]
        price_arr = highs

    swing_idx = np.where(swing_mask)[0]
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
            tol = TOUCH_K * atr[c]
            diff = price_arr[c] - projected
            if sign * diff < -tol:
                break  # kirildi (dokunus sayilmadan)
            elif abs(diff) <= tol:
                touches.append(c)
                if len(touches) >= MIN_TOUCHES and confirm_idx is None:
                    confirm_idx = c
            k += 1

        if confirm_idx is None:
            pos += 1
            continue

        # --- LOOK-AHEAD DUZELTMESI: kanal ancak confirm_idx + 5 barda "bilinir" ---
        confirmed_active_idx = confirm_idx + LOOKAHEAD_LAG_BARS
        if confirmed_active_idx >= n_total:
            pos += 1
            continue

        if direction == "up":
            ema_ok = ema50[confirmed_active_idx] > ema200[confirmed_active_idx]
            macd_ok = macd_l[confirmed_active_idx] > macd_s[confirmed_active_idx]
        else:
            ema_ok = ema50[confirmed_active_idx] < ema200[confirmed_active_idx]
            macd_ok = macd_l[confirmed_active_idx] < macd_s[confirmed_active_idx]

        if not (ema_ok and macd_ok):
            pos += 1
            continue

        break_idx = None
        limit_idx = min(n_total - 1, anchor + cap_bars)
        for i in range(confirmed_active_idx + 1, limit_idx + 1):
            projected = anchor_price + slope * (i - anchor)
            tol = TOUCH_K * atr[i] if not np.isnan(atr[i]) else TOUCH_K * np.nanmedian(atr)
            diff = closes[i] - projected
            if sign * diff < -tol:
                break_idx = i
                break
        censored = False
        if break_idx is None:
            break_idx = limit_idx
            censored = True

        break_known_time = int(times[break_idx]) + bar_min * 60

        channels.append({
            "tf": tf_name, "direction": direction,
            "anchor_idx": int(anchor), "second_idx": int(second),
            "confirm_idx_ham": int(confirm_idx),
            "confirmed_active_idx": int(confirmed_active_idx),
            "break_idx": int(break_idx),
            "n_touches_total": int(len(touches)), "slope_per_bar_pts": float(slope / POINT),
            "anchor_time": int(anchor_time),
            "confirmed_active_time": int(times[confirmed_active_idx]),
            "break_time": int(times[break_idx]),
            "break_known_time": int(break_known_time),
            "anchor_price": float(anchor_price),
            "duration_bars_confirmed_to_break": int(break_idx - confirmed_active_idx),
            "censored_veri_sonu": bool(censored),
        })

        next_pos = np.searchsorted(swing_idx, break_idx, side="right")
        pos = max(next_pos, pos + 1)

    return channels


m30_up_channels = detect_channels("M30", "up")
print("M30 YUKSELEN confirmed kanal sayisi (look-ahead-duzeltilmis):", len(m30_up_channels))

results["faz2_kanal_sayisi_m30_yukselen"] = len(m30_up_channels)
results["faz2_look_ahead_duzeltmesi_notu"] = (
    f"confirm_idx (3. dokunusun swing-olarak GEOMETRIK olustugu bar) ile confirmed_active_idx "
    f"(kanalin gercek-zamanli olarak BILINDIGI/kullanilabildigi bar, confirm_idx+{LOOKAHEAD_LAG_BARS}) "
    f"ARASINDAKI FARK, asagidaki TUM M15 giris testinde confirmed_active_idx kullanilarak "
    f"giderilmistir (H1/H2 ile AYNI gerekce - fraktal pivot N=5 sag-pencereli, ileri-bakisli)."
)
print("FAZ 2 tamamlandi.")

# ============================================================
# FAZ 2b: DEVAM-ORANI (CONTINUATION-RATE) COKLU-BLOK KARSILASTIRMASI
#   Stratejist'in acik talebi (gorev madde 4): M30-yukselen devam-orani (%63-80) bulgusu
#   n=15-20 kucuk orneklemden geliyor - in-sample'da gorunen oranin baska donemlerde
#   TEKRAR EDIP ETMEDIGI, TEK bir bolunmeye guvenmeden, kronolojik COK bloklu karsilastirmayla
#   sinanir. NOT: bu blok M15-kesisimiyle SINIRLI DEGIL - TUM M30-yukselen kanal tarihcesi
#   (~8,5 yillik M30 verisi) kullanilir (daha genis n icin), trade-seviyesi backtest (FAZ 5-7)
#   ise M15 kesisim penceresiyle SINIRLIDIR (ayri bir konu, karistirilmamali).
# ============================================================
print("=" * 70)
print("FAZ 2b: DEVAM-ORANI COKLU-BLOK KARSILASTIRMASI (M30-yukselen, tum tarihce)")
print("=" * 70)

m30_closes = raw["M30"]['close'].astype(float)
m30_n = len(m30_closes)
m30_t0 = int(raw["M30"]['time'][0])
m30_t1 = int(raw["M30"]['time'][-1])

# Kronolojik N_BLOCKS esit-zaman blogu (confirmed_active_time'a gore atama)
block_edges = np.linspace(m30_t0, m30_t1, N_BLOCKS + 1)


def block_of_time(t):
    for bi in range(N_BLOCKS):
        if block_edges[bi] <= t <= block_edges[bi + 1]:
            return bi
    return None


days_horizons = [1, 3, 7, 14]
block_devam = {}
for bi in range(N_BLOCKS):
    chs_in_block = [c for c in m30_up_channels if block_of_time(c["confirmed_active_time"]) == bi]
    devam = {}
    for d in days_horizons:
        N = int(d * 24 * 60 / 30)  # M30 bar sayisi
        same_dir, move_pts = [], []
        for c in chs_in_block:
            ci = c["confirmed_active_idx"]
            if ci + N < m30_n:
                p0 = m30_closes[ci]
                p1 = m30_closes[ci + N]
                same_dir.append(1 if (p1 - p0) > 0 else 0)
                move_pts.append((p1 - p0) / POINT)
        if same_dir:
            devam[f"{d}_gun"] = {"n": len(same_dir),
                                  "devam_orani": round(float(np.mean(same_dir)), 4),
                                  "medyan_hareket_pts": round(float(np.median(move_pts)), 1)}
        else:
            devam[f"{d}_gun"] = {"n": 0, "devam_orani": None, "medyan_hareket_pts": None}
    block_devam[f"blok_{bi+1}"] = {
        "zaman_araligi": [str(datetime.fromtimestamp(int(block_edges[bi]), tz=timezone.utc)),
                          str(datetime.fromtimestamp(int(block_edges[bi + 1]), tz=timezone.utc))],
        "n_kanal": len(chs_in_block),
        "devam_orani_ufuklar": devam,
    }
    print(f"Blok {bi+1}: n_kanal={len(chs_in_block)}, devam_orani(1g)={devam['1_gun']['devam_orani']}, "
          f"(7g)={devam['7_gun']['devam_orani']}, (14g)={devam['14_gun']['devam_orani']}")

# in-sample (Arastirmaci'nin orijinal bulgusu, TUM veri uzerinden hesaplanmisti, n=20) vs
# out-of-sample-benzeri karsilastirma: ilk yari (blok 1-2, "daha eski/discovery-benzeri") vs
# ikinci yari (blok 3-4, "daha yeni") toplu oran
first_half_chs = [c for c in m30_up_channels if block_of_time(c["confirmed_active_time"]) in (0, 1)]
second_half_chs = [c for c in m30_up_channels if block_of_time(c["confirmed_active_time"]) in (2, 3)]


def half_devam(chs):
    out_d = {}
    for d in days_horizons:
        N = int(d * 24 * 60 / 30)
        same_dir = []
        for c in chs:
            ci = c["confirmed_active_idx"]
            if ci + N < m30_n:
                same_dir.append(1 if (m30_closes[ci + N] - m30_closes[ci]) > 0 else 0)
        out_d[f"{d}_gun"] = {"n": len(same_dir),
                             "devam_orani": round(float(np.mean(same_dir)), 4) if same_dir else None}
    return out_d


ilk_yari = half_devam(first_half_chs)
ikinci_yari = half_devam(second_half_chs)
print("Ilk yari (blok1-2) devam-orani:", ilk_yari)
print("Ikinci yari (blok3-4) devam-orani:", ikinci_yari)

results["faz2b_devam_orani_coklu_blok"] = {
    "yontem_notu": ("TUM M30-yukselen kanal tarihcesi (n={}) kronolojik {} esit-zaman blogunda "
                     "AYRI AYRI devam-orani hesaplandi (Arastirmaci'nin TEK bir n=20 toplu "
                     "sonucuna guvenmek yerine). Ayrica ilk-yari (blok1-2) vs ikinci-yari "
                     "(blok3-4) TOPLU karsilastirmasi, orijinal bulgunun (%63-80) zaman icinde "
                     "TUTARLI/TEKRAR EDEN bir ozellik mi yoksa donem-spesifik bir gozlem mi "
                     "oldugunu sinamak icin eklendi.").format(len(m30_up_channels), N_BLOCKS),
    "blok_bazinda": block_devam,
    "ilk_yari_blok1_2_devam_orani": ilk_yari,
    "ikinci_yari_blok3_4_devam_orani": ikinci_yari,
}
print("FAZ 2b tamamlandi.")

# ============================================================
# FAZ 3: M15 GIRIS-ZAMANLAMA PROJEKSIYONU (LOOK-AHEAD-SAFE) - SADECE M30-YUKSELEN, BUY
# ============================================================
print("=" * 70)
print("FAZ 3: M15 GIRIS-ZAMANLAMA PROJEKSIYONU (SADECE M30-YUKSELEN, YALNIZCA BUY)")
print("=" * 70)

m15_times = raw["M15"]['time'].astype(np.int64)
m15_closes = raw["M15"]['close'].astype(float)
m15_opens = raw["M15"]['open'].astype(float)
m15_highs = raw["M15"]['high'].astype(float)
m15_lows = raw["M15"]['low'].astype(float)
m15_atr = ATR["M15"]
m15_spread = raw["M15"]['spread'].astype(float)
N_M15 = len(m15_closes)
m15_t0, m15_t1 = int(m15_times[0]), int(m15_times[-1])


def project_and_find_entries_m15(channels_htf):
    candidates = []
    n_overlap = 0
    for c in channels_htf:
        conf_t = c["confirmed_active_time"]
        brk_known_t = c["break_known_time"]
        if brk_known_t < m15_t0 or conf_t > m15_t1:
            continue
        n_overlap += 1
        win_start = max(conf_t, m15_t0)
        win_end = min(brk_known_t, m15_t1)
        lo = np.searchsorted(m15_times, win_start, side="left")
        hi = np.searchsorted(m15_times, win_end, side="right")
        if hi - lo < 3:
            continue

        sign = 1  # YALNIZCA BUY - direction her zaman "up"
        anchor_price = c["anchor_price"]
        anchor_time = c["anchor_time"]
        bar_min_htf = TFS[c["tf"]][1]
        slope_per_bar = c["slope_per_bar_pts"] * POINT
        slope_per_sec = slope_per_bar / (bar_min_htf * 60)

        for i in range(lo, hi - 1):
            if np.isnan(m15_atr[i]):
                continue
            t_i = int(m15_times[i])
            projected = anchor_price + slope_per_sec * (t_i - anchor_time)
            tol = TOUCH_K * m15_atr[i]
            diff = m15_closes[i] - projected
            if abs(diff) <= tol:
                if i + 1 >= N_M15:
                    continue
                if sign * (m15_closes[i + 1] - m15_closes[i]) > 0:
                    exec_idx = i + 2
                    if exec_idx >= N_M15:
                        continue
                    if int(m15_times[exec_idx]) >= brk_known_t:
                        continue
                    candidates.append({
                        "exec_idx": exec_idx, "direction": "up",
                        "atr_at_signal": float(m15_atr[i + 1]) if not np.isnan(m15_atr[i + 1]) else float(m15_atr[i]),
                        "channel": c, "touch_idx": int(i), "trigger_idx": int(i + 1),
                    })
    return candidates, n_overlap


all_candidates, n_overlap_m30up = project_and_find_entries_m15(m30_up_channels)
all_candidates.sort(key=lambda x: x["exec_idx"])
print(f"M30(yukselen)->M15: ortusen kanal={n_overlap_m30up}, aday-giris (look-ahead-safe)="
      f"{len(all_candidates)}")

results["faz3_aday_giris_sayilari"] = {
    "ortusen_kanal_m30_yukselen": n_overlap_m30up,
    "toplam_aday_giris_look_ahead_safe": len(all_candidates),
}
print("FAZ 3 tamamlandi.")

# ============================================================
# FAZ 4: ON-KONTROL MADDE 2 - S1 MALIYET-ORANI, GERCEK SL/TP (H3'e OZEL kalibrasyon)
# ============================================================
print("=" * 70)
print("FAZ 4: ON-KONTROL MADDE 2 - S1 MALIYET-ORANI (GERCEK SL/TP, H3'E OZEL)")
print("=" * 70)

atr_m15_median = float(np.nanmedian(m15_atr))
spread_m15_median = float(np.median(m15_spread))
slippage_est_m15 = 0.037 * atr_m15_median
cost_pts_total = spread_m15_median + slippage_est_m15
print(f"M15: spread_median={spread_m15_median:.2f}, ATR14_median={atr_m15_median:.2f}, "
      f"slippage_est={slippage_est_m15:.2f}, TOPLAM_MALIYET={cost_pts_total:.2f} pts")

# H3'e OZEL grid: M30-yukselen alt-kumesinde devam-orani daha tutarli gozlemlendigi icin
# (Stratejist'in acik izniyle) TP grid'i H2'ninkinden BAGIMSIZ, biraz daha genis uctan da
# deneyerek olusturuldu - otomatik tasima YOK, sifirdan kalibre edildi.
SL_MULT_GRID = [0.5, 0.75, 1.0]
TP_MULT_GRID = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

precheck_rows = []
for tp_m in TP_MULT_GRID:
    tp_pts_repr = tp_m * atr_m15_median
    ratio = tp_pts_repr / cost_pts_total
    precheck_rows.append({
        "tp_mult_atr": tp_m, "temsili_tp_pts": round(tp_pts_repr, 1),
        "maliyet_orani": round(ratio, 2),
        "gecti_mi_15x": bool(ratio >= 15.0), "gecti_mi_20x": bool(ratio >= 20.0),
    })
    print(f"  TP={tp_m}xATR ({tp_pts_repr:.1f}pts) -> oran={ratio:.2f}x "
          f"[15x:{'GECTI' if ratio>=15 else 'KALDI'} / 20x:{'GECTI' if ratio>=20 else 'KALDI'}]")

TP_MULT_SURVIVED = [r["tp_mult_atr"] for r in precheck_rows if r["gecti_mi_15x"]]
print("On-kontrolu (>=15x) GECEN TP carpanlari:", TP_MULT_SURVIVED)

results["faz4_on_kontrol_maliyet_orani"] = {
    "spread_median_pts": round(spread_m15_median, 2),
    "atr14_median_pts": round(atr_m15_median, 2),
    "slippage_tahmini_pts": round(slippage_est_m15, 2),
    "toplam_maliyet_pts": round(cost_pts_total, 2),
    "sl_mult_grid": SL_MULT_GRID, "tp_mult_grid": TP_MULT_GRID,
    "hucre_bazinda_sonuc": precheck_rows,
    "on_kontrolu_gecen_tp_mult": TP_MULT_SURVIVED,
    "karar": "ANA_TESTE_GECILEBILIR" if TP_MULT_SURVIVED else "RED_ON_KONTROLDE_KAPANDI",
    "referans_karsilastirma_stratejici_tahmini": (
        "Stratejist raporu M30->M15 yukselen icin 15x=~4,4 saat / 20x=~7,2 saat tahmin etmisti "
        "(interpolasyon, OLCUM DEGIL); asagidaki hucre-bazinda sonuc GERCEK ATR/spread/SL-TP "
        "degerleriyle hesaplanmis, bagimsiz bir dogrulamadir."),
}
print("FAZ 4 tamamlandi. Karar:", results["faz4_on_kontrol_maliyet_orani"]["karar"])
assert TP_MULT_SURVIVED, "H3 on-kontrolde elendi (S1 >=15x hicbir TP carpaninda saglanamiyor)."

# ============================================================
# FAZ 5: COK-FOLD PURGED/EMBARGOLU WALK-FORWARD BLOK SINIRLARI
#   H2'nin TEK train/validation/test bolunmesinden FARKLI: Stratejist'in acik talebi
#   (gorev madde 4) geregi burada N_BLOCKS=4 kronolojik blok + expanding-window 3 FOLD
#   kullanilir (Fold1: train=Blok1,test=Blok2 / Fold2: train=Blok1+2,test=Blok3 /
#   Fold3: train=Blok1+2+3,test=Blok4), her blok siniri EMBARGO_DAYS ile ayrilir.
# ============================================================
print("=" * 70)
print("FAZ 5: COK-FOLD PURGED/EMBARGOLU WALK-FORWARD BLOK SINIRLARI")
print("=" * 70)

total_days = (m15_t1 - m15_t0) / 86400.0
block_len_days = total_days / N_BLOCKS
embargo_sec = EMBARGO_DAYS * 86400

# Her blogun "cekirdek" (embargo cikarilmis) baslangic/bitis zamanlari
raw_block_edges = [m15_t0 + int(i * block_len_days * 86400) for i in range(N_BLOCKS + 1)]
raw_block_edges[-1] = m15_t1
block_bounds = []
for i in range(N_BLOCKS):
    a = raw_block_edges[i] + (embargo_sec // 2 if i > 0 else 0)
    b = raw_block_edges[i + 1] - (embargo_sec // 2 if i < N_BLOCKS - 1 else 0)
    block_bounds.append((a, b))

for i, (a, b) in enumerate(block_bounds):
    print(f"  Blok {i+1}: {datetime.fromtimestamp(a, tz=timezone.utc)} -> "
          f"{datetime.fromtimestamp(b, tz=timezone.utc)} ({(b - a) / 86400.0:.0f} gun)")

results["faz5_blok_sinirlari"] = {
    f"blok_{i+1}": {"baslangic": str(datetime.fromtimestamp(a, tz=timezone.utc)),
                    "bitis": str(datetime.fromtimestamp(b, tz=timezone.utc)),
                    "gun": round((b - a) / 86400.0, 1)}
    for i, (a, b) in enumerate(block_bounds)
}
results["faz5_embargo_days"] = EMBARGO_DAYS


def time_in_block(t, bi):
    a, b = block_bounds[bi]
    return a <= t <= b


for cand in all_candidates:
    t_exec = int(m15_times[cand["exec_idx"]])
    cand["block"] = None
    for bi in range(N_BLOCKS):
        if time_in_block(t_exec, bi):
            cand["block"] = bi
            break
    # embargo bosluguna dusen adaylar "block=None" (embargo) kalir - foldlarda kullanilmaz

block_counts = {f"blok_{bi+1}": sum(1 for c in all_candidates if c["block"] == bi) for bi in range(N_BLOCKS)}
block_counts["embargo"] = sum(1 for c in all_candidates if c["block"] is None)
print("Aday-giris blok dagilimi:", block_counts)
results["faz5_aday_giris_blok_dagilimi"] = block_counts

FOLDS = []
for k in range(1, N_BLOCKS):
    train_blocks = list(range(0, k))
    test_block = k
    FOLDS.append({"fold_no": k, "train_blocks": train_blocks, "test_block": test_block})
results["faz5_fold_tanimlari"] = FOLDS
print(f"Toplam {len(FOLDS)} expanding-window fold tanimlandi (Stratejist'in 'birden fazla fold' talebi).")
print("FAZ 5 tamamlandi.")

# ============================================================
# FAZ 6: TRADE SIMULASYONU (tek-pozisyon, uc-kosullu cikis) - H2 ile AYNI mekanik
# ============================================================
print("=" * 70)
print("FAZ 6: TRADE SIMULASYONU FONKSIYONU")
print("=" * 70)


def floor_lot(x, step=LOT_STEP_USD):
    return math.floor(x / step) * step


def simulate_trades(candidates_subset, sl_mult, tp_mult, kasa=KASA_USD):
    """Tek-pozisyon sirali simulasyon (BUY-only, sign=+1 sabit). candidates_subset zaten
    exec_idx'e gore SIRALI olmali."""
    trades = []
    pos_open_until_idx = -1
    n_overlap_skipped = 0
    n_break_before_open = 0

    for cand in candidates_subset:
        entry_idx = cand["exec_idx"]
        if entry_idx <= pos_open_until_idx:
            n_overlap_skipped += 1
            continue

        sign = 1  # YALNIZCA BUY
        atr_sig = cand["atr_at_signal"]
        if np.isnan(atr_sig) or atr_sig <= 0:
            continue
        sl_pts = sl_mult * atr_sig
        tp_pts = tp_mult * atr_sig
        entry_price = float(m15_opens[entry_idx])
        break_known_t = cand["channel"]["break_known_time"]

        if int(m15_times[entry_idx]) >= break_known_t:
            n_break_before_open += 1
            continue

        sl_price = entry_price - sl_pts * POINT
        tp_price = entry_price + tp_pts * POINT

        exit_idx = None
        exit_reason = None
        exit_price = None
        j = entry_idx
        while j < N_M15:
            t_j = int(m15_times[j])
            bar_open_after_break = t_j >= break_known_t
            hi, lo = float(m15_highs[j]), float(m15_lows[j])
            sl_hit = lo <= sl_price
            tp_hit = hi >= tp_price

            if sl_hit:  # muhafazakar varsayim: ayni barda SL+TP varsa SL kazanir
                exit_idx, exit_reason, exit_price = j, "SL", sl_price
                break
            if tp_hit:
                exit_idx, exit_reason, exit_price = j, "TP", tp_price
                break
            if bar_open_after_break:
                exit_idx, exit_reason, exit_price = j, "KIRILIM_ERKEN_CIKIS", float(m15_closes[j])
                break
            j += 1
        if exit_idx is None:
            exit_idx = N_M15 - 1
            exit_reason = "VERI_SONU_ACIK"
            exit_price = float(m15_closes[exit_idx])

        gross_pnl_pts = sign * (exit_price - entry_price) / POINT
        net_pnl_pts = gross_pnl_pts - cost_pts_total

        lot = max(TABAN_LOT, floor_lot((kasa * RISK_PCT_UST_SINIR) / sl_pts))
        pnl_usd = net_pnl_pts * USD_PER_POINT_PER_LOT * lot

        hold_bars = exit_idx - entry_idx
        trades.append({
            "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
            "entry_time": str(datetime.fromtimestamp(int(m15_times[entry_idx]), tz=timezone.utc)),
            "exit_time": str(datetime.fromtimestamp(int(m15_times[exit_idx]), tz=timezone.utc)),
            "direction": "BUY", "tf_source": "M30",
            "sl_pts": round(sl_pts, 1), "tp_pts": round(tp_pts, 1),
            "exit_reason": exit_reason,
            "gross_pnl_pts": round(gross_pnl_pts, 2), "net_pnl_pts": round(net_pnl_pts, 2),
            "lot": round(lot, 2), "pnl_usd": round(pnl_usd, 4),
            "hold_bars_m15": int(hold_bars), "hold_hours": round(hold_bars * 15 / 60.0, 3),
            "block": cand.get("block"),
        })
        pos_open_until_idx = exit_idx

    return trades, n_overlap_skipped, n_break_before_open


def summarize_trades(trades):
    if not trades:
        return {"n_trades": 0}
    net_pts = np.array([t["net_pnl_pts"] for t in trades])
    pnl_usd = np.array([t["pnl_usd"] for t in trades])
    wins = net_pts > 0
    gross_profit = pnl_usd[pnl_usd > 0].sum()
    gross_loss = -pnl_usd[pnl_usd < 0].sum()
    pf = float(gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else None)

    equity = KASA_USD + np.cumsum(pnl_usd)
    running_max = np.maximum.accumulate(np.concatenate(([KASA_USD], equity)))[1:]
    drawdown = (running_max - equity) / running_max
    max_dd_pct = float(np.max(drawdown)) * 100 if len(drawdown) else 0.0

    hold_hours = np.array([t["hold_hours"] for t in trades])
    exit_reasons = {}
    for t in trades:
        exit_reasons[t["exit_reason"]] = exit_reasons.get(t["exit_reason"], 0) + 1

    return {
        "n_trades": len(trades),
        "win_rate": round(float(np.mean(wins)), 4),
        "profit_factor": round(pf, 4) if pf is not None and pf != float('inf') else pf,
        "net_profit_usd": round(float(pnl_usd.sum()), 2),
        "net_profit_pts": round(float(net_pts.sum()), 1),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "medyan_tutma_suresi_saat": round(float(np.median(hold_hours)), 2),
        "ortalama_tutma_suresi_saat": round(float(np.mean(hold_hours)), 2),
        "p10_p90_tutma_suresi_saat": [round(float(np.percentile(hold_hours, 10)), 2),
                                        round(float(np.percentile(hold_hours, 90)), 2)],
        "cikis_nedeni_dagilimi": exit_reasons,
    }


print("FAZ 6 fonksiyonlari tanimlandi.")

# ============================================================
# FAZ 7: HER FOLD ICIN SL/TP KALIBRASYONU (Train'de tara -> Test'te TEK KEZ)
#   Expanding-window walk-forward, 3 fold (H2'nin TEK bolunmesinden FARKLI)
# ============================================================
print("=" * 70)
print("FAZ 7: COK-FOLD WALK-FORWARD SL/TP KALIBRASYONU")
print("=" * 70)

MIN_TRADES_FOR_SELECTION = 15  # H2'nin 30'undan dusuk - H3'un daha kucuk orneklemine gore
                                 # ORANTILI sekilde ayarlandi (M30-yukselen tek-alt-kume,
                                 # daha az ortusen kanal) - bu ayarlama ACIKCA raporlanacak

fold_results = []
oos_trades_pooled = []
train_trades_pooled_per_fold = []

for fold in FOLDS:
    fold_no = fold["fold_no"]
    train_cands = [c for c in all_candidates if c["block"] in fold["train_blocks"]]
    test_cands = [c for c in all_candidates if c["block"] == fold["test_block"]]
    print(f"--- FOLD {fold_no}: train_blocks={fold['train_blocks']} (n_aday={len(train_cands)}), "
          f"test_block={fold['test_block']} (n_aday={len(test_cands)}) ---")

    grid_rows = []
    for sl_m in SL_MULT_GRID:
        for tp_m in TP_MULT_SURVIVED:
            tr_trades, _, _ = simulate_trades(train_cands, sl_m, tp_m)
            tr_sum = summarize_trades(tr_trades)
            grid_rows.append({"sl_mult": sl_m, "tp_mult": tp_m, "train": tr_sum})

    eligible = [g for g in grid_rows if g["train"].get("n_trades", 0) >= MIN_TRADES_FOR_SELECTION
                and g["train"].get("profit_factor") is not None]
    if eligible:
        best = max(eligible, key=lambda g: g["train"]["profit_factor"])
        secim_notu = f"Train'de PF'ye gore secildi (n>={MIN_TRADES_FOR_SELECTION} sarti saglayan {len(eligible)} hucre arasindan)."
    else:
        by_n = [g for g in grid_rows if g["train"].get("n_trades", 0) > 0]
        if by_n:
            best = max(by_n, key=lambda g: g["train"]["n_trades"])
            secim_notu = (f"HICBIR hucre Train'de n>={MIN_TRADES_FOR_SELECTION} esigini GECMEDI - "
                          f"en fazla islem sayisina sahip hucre secildi (n={best['train']['n_trades']}), "
                          f"bu secim ZAYIF/dusuk-guvenilirlikli olarak isaretlenmelidir.")
        else:
            best = grid_rows[0]
            secim_notu = "Train'de HICBIR hucrede islem olusmadi - ilk grid hucresi varsayilan (guvenilmez)."

    sel_sl, sel_tp = best["sl_mult"], best["tp_mult"]
    print(f"  Secilen: SL={sel_sl}xATR TP={sel_tp}xATR | {secim_notu}")

    train_trades_final, _, _ = simulate_trades(train_cands, sel_sl, sel_tp)
    test_trades_final, test_ov, test_brk = simulate_trades(test_cands, sel_sl, sel_tp)
    train_summary = summarize_trades(train_trades_final)
    test_summary = summarize_trades(test_trades_final)
    print(f"  TRAIN (in-sample): {train_summary}")
    print(f"  TEST  (out-of-sample, TEK KEZ): {test_summary}")

    oos_trades_pooled.extend(test_trades_final)
    train_trades_pooled_per_fold.append({"fold_no": fold_no, "trades": train_trades_final})

    fold_results.append({
        "fold_no": fold_no, "train_blocks": fold["train_blocks"], "test_block": fold["test_block"],
        "n_aday_train": len(train_cands), "n_aday_test": len(test_cands),
        "grid_tarama_train": grid_rows, "secilen_sl_mult": sel_sl, "secilen_tp_mult": sel_tp,
        "secim_notu": secim_notu,
        "train_in_sample": train_summary, "test_out_of_sample": test_summary,
    })

results["faz7_fold_sonuclari"] = fold_results

# Havuzlanmis out-of-sample (TUM fold'larin test-bloklari birlestirilmis, kronolojik, HER
# fold KENDI secilen SL/TP'siyle simule edilmis islemler) - genel OOS PF/WR gorunumu
oos_trades_pooled.sort(key=lambda t: t["entry_time"])
pooled_oos_summary = summarize_trades(oos_trades_pooled)
print("HAVUZLANMIS OUT-OF-SAMPLE (tum fold testleri birlikte):", pooled_oos_summary)

# Karsilastirma icin: TUM train (in-sample) islemlerin havuzu (fold'lar arasi ORTALAMA PF/WR,
# NOT toplam - cunku fold'lar arasi train setleri IC ICE/orantisiz genisliyor, dogrudan
# toplamak yaniltici olur; bunun yerine fold-bazinda ayri ayri rapor edilir, asagida)
in_sample_pf_list = [f["train_in_sample"].get("profit_factor") for f in fold_results
                      if f["train_in_sample"].get("profit_factor") is not None]
oos_pf_list = [f["test_out_of_sample"].get("profit_factor") for f in fold_results
               if f["test_out_of_sample"].get("profit_factor") is not None]

results["faz7_havuzlanmis_oos_ozet"] = pooled_oos_summary
results["faz7_in_sample_vs_oos_pf_karsilastirma"] = {
    "fold_bazinda_train_pf": [f["train_in_sample"].get("profit_factor") for f in fold_results],
    "fold_bazinda_test_pf": [f["test_out_of_sample"].get("profit_factor") for f in fold_results],
    "fold_bazinda_train_wr": [f["train_in_sample"].get("win_rate") for f in fold_results],
    "fold_bazinda_test_wr": [f["test_out_of_sample"].get("win_rate") for f in fold_results],
    "yontem_notu": ("Her fold'un SL/TP'si SADECE o fold'un TRAIN (in-sample) blogunda secilmis, "
                     "TEST (out-of-sample) blogunda TEK KEZ uygulanmistir (H2'deki ayni ilke, "
                     "cok-fold'a genisletilmis hali). Train-PF ile Test-PF arasindaki fark "
                     "buyukse OVERFITTING_RISKI flag'i asagida ayrica isaretlenir."),
}

# En sik secilen (SL,TP) kombinasyonu - "genel" bir kalibrasyon olarak ayrica raporlanir
sel_pairs = [(f["secilen_sl_mult"], f["secilen_tp_mult"]) for f in fold_results]
from collections import Counter
sel_counter = Counter(sel_pairs)
most_common_pair, most_common_n = sel_counter.most_common(1)[0]
results["faz7_fold_arasi_secim_tutarliligi"] = {
    "fold_bazinda_secimler": sel_pairs,
    "en_sik_secilen_kombinasyon": {"sl_mult": most_common_pair[0], "tp_mult": most_common_pair[1],
                                     "kac_foldda_secildi": most_common_n, "toplam_fold": len(FOLDS)},
    "tutarlilik_notu": (f"{len(FOLDS)} fold arasinda SL/TP secimi {len(sel_counter)} FARKLI "
                         f"kombinasyona dagildi (tam tutarlilik = 1 farkli kombinasyon olurdu). "
                         f"Dagilim genisse bu, kucuk orneklem nedeniyle SL/TP seciminin "
                         f"ISTIKRARSIZ oldugu anlamina gelir - Risk Analisti'ne acikca "
                         f"bildirilmelidir."),
}
print(f"Fold arasi secim tutarliligi: {sel_counter}")

# OVERFITTING_RISKI flag
overfitting_flag = False
overfitting_notlari = []
for f in fold_results:
    tr_pf = f["train_in_sample"].get("profit_factor")
    te_pf = f["test_out_of_sample"].get("profit_factor")
    if tr_pf is not None and te_pf is not None:
        if tr_pf > 1.0 and (te_pf is None or te_pf < 1.0 or (tr_pf - te_pf) > 0.5):
            overfitting_flag = True
            overfitting_notlari.append(f"Fold {f['fold_no']}: Train PF={tr_pf} ama Test PF={te_pf} "
                                        f"- buyuk fark/yon degisimi.")
    elif tr_pf is not None and tr_pf > 1.0 and te_pf is None:
        overfitting_flag = True
        overfitting_notlari.append(f"Fold {f['fold_no']}: Train PF={tr_pf} ama Test'te PF hesaplanamadi "
                                    f"(muhtemelen kazanc yok/n=0).")

results["faz7_overfitting_kontrolu"] = {
    "overfitting_riski_flag": overfitting_flag,
    "notlar": overfitting_notlari if overfitting_notlari else ["Fold'lar arasinda belirgin bir "
                                                                  "Train>1 / Test<<1 asimetrisi "
                                                                  "gozlenmedi (ama n kucuk, temkinli "
                                                                  "yorumlanmali)."],
}
print("FAZ 7 tamamlandi. Overfitting riski flag:", overfitting_flag)

# ============================================================
# FAZ 8: KIRILIM-BAZLI-ERKEN-CIKIS DOGRULAMA ORNEKLERI (havuzlanmis OOS uzerinde)
# ============================================================
print("=" * 70)
print("FAZ 8: KIRILIM-BAZLI-ERKEN-CIKIS DOGRULAMA")
print("=" * 70)

break_exit_trades = [t for t in oos_trades_pooled if t["exit_reason"] == "KIRILIM_ERKEN_CIKIS"]
print(f"Havuzlanmis OOS'ta KIRILIM_ERKEN_CIKIS ile kapanan islem sayisi: "
      f"{len(break_exit_trades)} / {len(oos_trades_pooled)}")

sample_examples = break_exit_trades[:5]
validation_examples = []
for t in sample_examples:
    validation_examples.append({
        "entry_time": t["entry_time"], "exit_time": t["exit_time"],
        "hold_hours": t["hold_hours"], "net_pnl_pts": t["net_pnl_pts"],
        "dogrulama": ("exit_time, ilgili kanalin break_known_time'indan (kanalin M30 kapanisiyla "
                       "kirildigi + bar suresi) SONRA veya AYNI ana denk gelmeli, VE bu bardan once "
                       "SL/TP tetiklenmemis olmali (H2 ile AYNI kod mantigi: SL/TP kontrolu "
                       "break kontrolunden ONCE yapilir, ayni bar icinde ikisi de gecerliyse "
                       "SL/TP ONCELIKLIDIR)."),
    })

results["faz8_kirilim_erken_cikis_dogrulama"] = {
    "toplam_kirilim_cikisi_oos": len(break_exit_trades),
    "toplam_islem_oos": len(oos_trades_pooled),
    "oran": round(len(break_exit_trades) / len(oos_trades_pooled), 4) if oos_trades_pooled else None,
    "ornek_islemler": validation_examples,
    "yontem_notu": ("Kod, her M15 barinda SIRASIYLA (1) SL, (2) TP, (3) kanal-kirilim-bilgisi-var-mi "
                     "kontrolu yapar - ayni barda SL/TP VE kirilim AYNI ANDA gecerliyse SL/TP "
                     "ONCELIKLIDIR (muhafazakar/gercekci varsayim, H1/H2 ile TUTARLI)."),
}
print("FAZ 8 tamamlandi.")

# ============================================================
# FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + KAYIT
# ============================================================
print("=" * 70)
print("FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + JSON/CSV YAZIMI")
print("=" * 70)

if oos_trades_pooled:
    entry_dates = sorted([datetime.fromisoformat(t["entry_time"]).date() for t in oos_trades_pooled])
    n_months = max(1, (entry_dates[-1].year - entry_dates[0].year) * 12
                   + (entry_dates[-1].month - entry_dates[0].month) + 1)
    n_years = (entry_dates[-1] - entry_dates[0]).days / 365.25 if len(entry_dates) > 1 else 1.0
    trades_per_month = len(oos_trades_pooled) / n_months
    trades_per_year = len(oos_trades_pooled) / n_years if n_years > 0 else None
else:
    trades_per_month = None
    trades_per_year = None

print(f"Islem/ay (havuzlanmis OOS): {trades_per_month}, Islem/yil: {trades_per_year}")

kirilim_block = {}
kirilim_exit = {}
for t in oos_trades_pooled:
    kirilim_block.setdefault(f"blok_{t['block']}", []).append(t["net_pnl_pts"])
    kirilim_exit.setdefault(t["exit_reason"], []).append(t["net_pnl_pts"])


def group_summary(d):
    out = {}
    for k, v in d.items():
        arr = np.array(v)
        wins = arr > 0
        gp = arr[arr > 0].sum()
        gl = -arr[arr < 0].sum()
        out[k] = {
            "n": len(arr), "win_rate": round(float(np.mean(wins)), 4),
            "profit_factor_pts_bazli": round(float(gp / gl), 4) if gl > 0 else None,
            "net_pts": round(float(arr.sum()), 1),
        }
    return out


results["faz9_islem_frekansi"] = {
    "islem_ay_sayisi_havuzlanmis_oos": round(trades_per_month, 3) if trades_per_month else None,
    "islem_yil_sayisi_havuzlanmis_oos": round(trades_per_year, 2) if trades_per_year else None,
    "toplam_islem_havuzlanmis_oos": len(oos_trades_pooled),
}
results["faz9_kirilim_blok"] = group_summary(kirilim_block)
results["faz9_kirilim_exit_nedeni"] = group_summary(kirilim_exit)

# Ornek islem logu (havuzlanmis OOS islemlerin TAMAMI - H2'den daha az sayida oldugu icin
# tam log dogrudan JSON'a da sigabilir, yine de CSV ayrica yazilir)
results["islem_logu_ornek"] = oos_trades_pooled[:20] + (oos_trades_pooled[-20:] if len(oos_trades_pooled) > 20 else [])

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("TAMAMLANDI ->", OUT_PATH)

if oos_trades_pooled:
    pd.DataFrame(oos_trades_pooled).to_csv(
        r"C:\MilaYatirim\Justin\backtest_A_ailesi_H3_islem_logu_oos.csv",
        index=False, encoding="utf-8-sig")
    print("Havuzlanmis OOS islem logu CSV yazildi.")

all_trades_for_log = []
for item in train_trades_pooled_per_fold:
    all_trades_for_log.extend(item["trades"])
if all_trades_for_log:
    pd.DataFrame(all_trades_for_log).to_csv(
        r"C:\MilaYatirim\Justin\backtest_A_ailesi_H3_islem_logu_train_foldlar.csv",
        index=False, encoding="utf-8-sig")
    print("Fold-bazinda train islem loglari CSV yazildi.")

mt5.shutdown()
print("BITTI.")
