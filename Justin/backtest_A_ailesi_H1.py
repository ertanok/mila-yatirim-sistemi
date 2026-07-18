# -*- coding: utf-8 -*-
"""
Backtest Muhendisi - Justin / Gold Scalping - A Ailesi (Momentum/Trend-Following) - HIPOTEZ H1
"Dar-Kanit M5-Giris" - TEKRAR DENEME (onceki gorev_id: backtest_muhendisi_20260713_1816,
durum: hata - onceki script SADECE kanal-tespiti fazini calistirip erken sonlanmisti).

Bu surum, H2'nin FAZ 0-9 yapisiyla AYNI KAPSAMDA, M5-giris mekanizmasina uyarlanmis TAM
script'tir (onceki kismi denemenin devami degil, sifirdan/tam kapsamli yeniden yazim).

Kaynak: stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md (H1 bolumu +
Backtest Muhendisi'ne Devir Notlari 1-8) + gorev_backtest_muhendisi_justin_gold_scalping_A_
ailesi_H1_tekrar.md (bu tekrar-deneme cagrisi).

Mekanizma (Stratejist'in tasarimi, DEGISTIRILMEDI):
- Rejim/giris-filtresi: H1 VEYA M30'da onaylanmis (>=3 dokunus + EMA50/200 + MACD teyitli)
  aktif/kirilmamis yapisal kanal.
- Giris tetigi: kanal cizgisinin M5 projeksiyonuna bir M5 barinin
  |kapanis-projeksiyon| <= 0.5xATR14_M5 ile dokunmasi + BIR SONRAKI M5 barinin trend
  yonunde kapanmasi.
- Cikis: uc kosuldan ilk gerceklesen -> (i) SL (k_sl x ATR14_M5), (ii) TP (k_tp x ATR14_M5),
  (iii) kirilim-bazli erken cikis (uretici kanal KIRILIRSA SL/TP beklenmeden kapat).
- Yon: simetrik, iki yon (BUY + SELL), AYNI k_sl/k_tp katsayilari her iki yonde de kullanilir.

YURUTME-ANI NOTU (Look-Ahead-Safety detayi, Risk Analistine acikca raporlanacak):
Stratejist raporu girisi "tetigi olusturan (bir sonraki) M5 barinin kapanisinda" olarak
tanimliyor - bu script, H2'nin (ayni turun kardes hipotezi, ayni giris-tetigi cumlesiyle
yazilmis) UYGULAMA KONVANSIYONUNU izleyerek girisi bir bar SONRA (dokunus-bari=i,
yon-teyit-bari=i+1 kapanisi, GIRIS=i+2 barinin ACILISI) olarak uygular - bu, hem CLAUDE.md/
sistem-promptu genel ilkesiyle ("sinyal kapanista uretilir, giris bir sonraki bar acilisinda
gerceklesir") hem H2 ile metodolojik tutarlilikla (ayni turda capraz-kontrol amaci) daha
uyumludur; Stratejist'in MEKANIZMASI (dokunma + yon-teyidi kosullari) DEGISTIRILMEMISTIR,
sadece kesin yurutme-fiyati ani (Stratejist tarafindan acikca belirtilmemis bir uygulama
detayi) H2 ile tutarli/muhafazakar sekilde secilmistir. Asagida ayrica raporlanir.

KRITIK MUHENDISLIK DUZELTMESI (Look-Ahead Bias):
Pivot/swing tanimi (N=5 fraktal, sag pencereli) ILERI-BAKISLIDIR - bar i'nin "swing" oldugu
ancak bar i+5'te (5 bar SONRA) kesinlesir. Bu script bu gecikmeyi ACIKCA modeller: bir
kanalin >=3-dokunus + EMA/MACD onayi GERCEKTEN "bilinir" hale gelen an, onay barinin
KENDISI degil, onay barindan LOOKAHEAD_LAG_BARS(=5) bar SONRASIDIR (known_idx = confirm_idx
+ LAG_BARS). EK DUZELTME (bu turde eklendi): known_idx'in KENDI ic bilgisi (o barin
kapanis/EMA/MACD degerleri) bile ancak o barin KAPANISINDA bilinir - bu yuzden
"known_time" = time[known_idx] + bar_suresi olarak hesaplanir (H2'nin break_known_time'da
zaten uyguladigi mantik, known_time'a da simetrik olarak uygulandi). Karsilastirma icin NAIVE
(bias'li, confirm_idx'in kendisini kullanan, lag=0) versiyon da hesaplanip raporlanir.

Onceki-adim/ara-sonuc notu: `bt_h1_step_channels.json` (onceki kismi denemeden kalan) ve
`bt_h1_step0_dst_check_output.json` (bu tekrar-denemenin FAZ0'i olarak zaten BAGIMSIZ
calistirilmisti) mevcuttur. DST sonucu asagida FAZ1'e AYNEN tasinmistir (ayni turun kendi
bagimsiz olcumudur, devralinmadi). bt_h1_step_channels.json ise DOGRUDAN KULLANILMADI -
gerekce FAZ2 yorumlarinda acikca verilmistir (index-tutarliligi riski).

Veri izolasyonu: bu script yalniz C:\\MilaYatirim\\Justin\\ icinde calisir, MilaGold/Lisa/
Signal GPT'ye ait hicbir dosya/deger/format kullanilmaz. Tek veri kaynagi: MT5/GOLD ham OHLCV.
"""
import json
import math
import traceback
import os
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date

OUT_PATH = r"C:\MilaYatirim\Justin\backtest_A_ailesi_H1_output.json"
HATA_LOG_PATH = r"C:\MilaYatirim\Justin\backtest_A_ailesi_H1_hata_log.txt"
OLD_CHANNELS_JSON = r"C:\MilaYatirim\Justin\bt_h1_step_channels.json"
OLD_DST_JSON = r"C:\MilaYatirim\Justin\bt_h1_step0_dst_check_output.json"

# onceki basarisiz/yarim denemeden kalan hata logu varsa (bu turden once) temizle - bu
# calistirmanin SONUCUNA gore (basarili/basarisiz) asagida yeniden yazilacak/silinecek
if os.path.exists(HATA_LOG_PATH):
    os.remove(HATA_LOG_PATH)


def main():
    # ============================================================
    # SABITLER
    # ============================================================
    SYMBOL = "GOLD"
    MIN_TOUCHES = 3             # kanal gecerlilik esigi (Stratejist tasarimi)
    TOUCH_K = 0.5                # dokunus toleransi: 0.5 x ATR14 (Stratejist/Arastirmaci tanimi)
    SWING_N = 5                  # fraktal pivot penceresi (N=5, sol+sag)
    LOOKAHEAD_LAG_BARS = 5       # swing bir bar'in "swing" oldugu ancak N=5 bar SONRA kesinlesir
    CAP_DAYS = 300                # kanal arama penceresi sinirlamasi (muhendislik pratikligi)
    EMA_FAST, EMA_SLOW = 50, 200
    MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 9

    KASA_USD = 2000.0             # justin_gecmis_calisma.md (MilaGold'dan bagimsiz, kendi cercevesi)
    RISK_PCT_UST_SINIR = 0.01     # islem-basi risk UST SINIRI (kasa x %1)
    TABAN_LOT = 0.01
    LOT_STEP_USD = 0.01           # lot yuvarlama adimi

    EMBARGO_DAYS = 45             # train/val/test arasi purge/embargo (H2 ile ayni kaynak/gerekce:
                                    # medyan kanal omru 25-35 gun < 45 - kanal-tespit mekanizmasi H1/H2
                                    # arasinda ORTAK oldugu icin bu sabit de ortaktir, MilaGold'dan
                                    # ALINMAMISTIR)
    TRAIN_FRAC, VAL_FRAC = 0.50, 0.25  # kalan Test'e (~%25)

    DST_TRANSITIONS = ["2025-03-30", "2025-10-26", "2026-03-29"]

    results = {"meta": {
        "hipotez_adi": "A Ailesi H1 - Dar-Kanit M5-Giris (TEKRAR DENEME)",
        "min_touches": MIN_TOUCHES, "touch_k": TOUCH_K, "swing_n": SWING_N,
        "lookahead_lag_bars": LOOKAHEAD_LAG_BARS, "cap_days": CAP_DAYS,
        "ema_fast": EMA_FAST, "ema_slow": EMA_SLOW, "macd": [MACD_FAST, MACD_SLOW, MACD_SIG],
        "kasa_usd": KASA_USD, "risk_pct_ust_sinir": RISK_PCT_UST_SINIR, "taban_lot": TABAN_LOT,
        "embargo_days": EMBARGO_DAYS,
    }}

    print("=" * 70)
    print("FAZ 0: MT5 BAGLANTI + HAM VERI")
    print("=" * 70)
    assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
    mt5.symbol_select(SYMBOL, True)
    info = mt5.symbol_info(SYMBOL)
    POINT = info.point
    CONTRACT_SIZE = info.trade_contract_size
    USD_PER_POINT_PER_LOT = CONTRACT_SIZE * POINT
    print(f"point={POINT}, contract_size={CONTRACT_SIZE}, USD/puan/1.0-lot={USD_PER_POINT_PER_LOT}")

    TFS = {
        "M5": (mt5.TIMEFRAME_M5, 5),
        "M30": (mt5.TIMEFRAME_M30, 30),
        "H1": (mt5.TIMEFRAME_H1, 60),
    }
    raw = {}
    for tf_name, (tf_const, bar_min) in TFS.items():
        rates = mt5.copy_rates_from_pos(SYMBOL, tf_const, 0, 99999)
        raw[tf_name] = rates
        t0 = datetime.fromtimestamp(int(rates[0]['time']), tz=timezone.utc)
        t1 = datetime.fromtimestamp(int(rates[-1]['time']), tz=timezone.utc)
        print(tf_name, "n=", len(rates), t0, "->", t1)

    results["veri_araligi"] = {tf: {"n_bar": int(len(raw[tf])),
                                     "baslangic": str(datetime.fromtimestamp(int(raw[tf][0]['time']), tz=timezone.utc)),
                                     "bitis": str(datetime.fromtimestamp(int(raw[tf][-1]['time']), tz=timezone.utc))}
                               for tf in TFS}

    # ============================================================
    # FAZ 1: ON-KONTROL MADDE 1 - DST / SAAT-ESLEME BAGIMSIZ DOGRULAMA
    # ============================================================
    print("=" * 70)
    print("FAZ 1: DST / SAAT-ESLEME BAGIMSIZ DOGRULAMA")
    print("=" * 70)

    def dst_check(rates, tf_label):
        n = len(rates)
        t = rates['time'].astype(np.int64)
        hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
        dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])
        gap_threshold_sec = 23 * 3600
        gaps = []
        for i in range(1, n):
            dt = t[i] - t[i - 1]
            if dt > gap_threshold_sec:
                gaps.append({"friday_close_utc_hour": int(hours[i - 1]), "friday_close_date": dates[i - 1],
                             "sunday_open_utc_hour": int(hours[i]), "sunday_open_date": dates[i]})

        def hour_mode_window(gaps_list, center_date_str, days=21):
            cy, cm, cd = [int(x) for x in center_date_str.split("-")]
            center = _date(cy, cm, cd)
            before, after = [], []
            for g in gaps_list:
                gy, gm, gd = [int(x) for x in g["friday_close_date"].split("-")]
                gdate = _date(gy, gm, gd)
                delta = (gdate - center).days
                if -days <= delta < 0:
                    before.append(g["friday_close_utc_hour"])
                elif 0 <= delta <= days:
                    after.append(g["friday_close_utc_hour"])
            return before, after

        dst_res = []
        for tr in DST_TRANSITIONS:
            before, after = hour_mode_window(gaps, tr)
            kayma = (bool(before) and bool(after) and
                     (max(set(before), key=before.count) != max(set(after), key=after.count)))
            dst_res.append({"gecis_tarihi": tr, "oncesi_cuma_kapanis_saatleri": before,
                             "sonrasi_cuma_kapanis_saatleri": after, "kayma_tespit_edildi_mi": bool(kayma)})
        return {"tf": tf_label, "toplam_hafta_sonu_gecis_sayisi": len(gaps), "dst_kontrolu": dst_res}

    tick_now = mt5.symbol_info_tick(SYMBOL)
    epoch_as_utc = datetime.fromtimestamp(tick_now.time, tz=timezone.utc).replace(tzinfo=None)
    vps_local_now = datetime.now()
    diff_seconds = abs((epoch_as_utc - vps_local_now).total_seconds())
    print(f"canli capraz kontrol: epoch_utc={epoch_as_utc}, vps_yerel={vps_local_now}, fark_sn={diff_seconds:.2f}")

    dst_h1 = dst_check(raw["H1"], "H1")
    dst_m5 = dst_check(raw["M5"], "M5")
    print("H1 DST kontrolu:", dst_h1["dst_kontrolu"])
    print("M5 DST kontrolu:", dst_m5["dst_kontrolu"])

    # bu turun FAZ0'i olarak zaten AYRI/bagimsiz calistirilmis olan onceki-adim sonucu (ayni
    # tekrar-deneme icinde, devralinmadi) - capraz-referans icin dahil edilir
    onceki_bagimsiz_dst_adimi = None
    if os.path.exists(OLD_DST_JSON):
        with open(OLD_DST_JSON, "r", encoding="utf-8") as f:
            onceki_bagimsiz_dst_adimi = json.load(f)

    results["faz1_on_kontrol_dst"] = {
        "canli_capraz_kontrol": {"epoch_utc_okuma": str(epoch_as_utc), "vps_yerel_simdi": str(vps_local_now),
                                  "fark_saniye": diff_seconds,
                                  "sonuc": "VPS yerel saat = UTC+3, DST GECISI GORULMUYOR (yerel OS saati "
                                           "yil boyunca sabit +3 - TST/Turkiye saati, 2016'dan beri DST "
                                           "uygulamiyor). Bu, MT5 SUNUCU saatinin de sabit oldugu anlamina "
                                           "GELMEZ - asagidaki H1/M5 hafta-sonu-gecis testi sunucu "
                                           "davranisini ayrica olcer."},
        "H1": dst_h1, "M5": dst_m5,
        "bu_turun_ayrica_calistirilmis_bagimsiz_on_adimi": onceki_bagimsiz_dst_adimi,
        "sonuc_notu": ("H1 VE M5 verisinde BAGIMSIZ olarak (H2'den veya onceki hipotezlerden "
                       "devralinmadan) bu tur icin YENIDEN kosturuldu - ayrica, bu tekrar-denemenin "
                       "kendi ilk adiminda (bt_h1_step0_dst_check.py) BAGIMSIZ bir kez daha olculmus, "
                       "sonuc yukarida capraz-referans olarak eklenmistir. Beklenen: MT5/XM sunucusu "
                       "AB/Kibris DST takvimini izliyor (yaz GMT+3, kis GMT+2) - onceki turlerde "
                       "(Hipotez 1/2/3, H2) bagimsiz dogrulanan bulguyla TUTARLI olup olmadigi asagida "
                       "H1/M5 kayma sonuclarindan okunmalidir. M5 kanal-projeksiyonu dakika-bazli oldugu "
                       "icin bu ayrim ozellikle onemlidir."),
    }
    print("FAZ 1 tamamlandi.")

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

    SWINGS = {}
    for tf in ("H1", "M30"):
        sh, sl_ = find_swings(raw[tf])
        SWINGS[tf] = {"swing_high": sh, "swing_low": sl_}
        print(tf, "swing_high n=", int(sh.sum()), "swing_low n=", int(sl_.sum()))

    # ============================================================
    # FAZ 2: PIVOT/KANAL TESPITI - NAIVE (bias'li) + CAUSAL (look-ahead duzeltmeli)
    # ============================================================
    print("=" * 70)
    print("FAZ 2: PIVOT/KANAL TESPITI (NAIVE + CAUSAL)")
    print("=" * 70)

    CAP_MINUTES = CAP_DAYS * 24 * 60

    def detect_channels(tf_name, direction, lag_bars):
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

            # bilinen-an (look-ahead duzeltmesi): confirm_idx bir swing'dir, ancak lag_bars kadar
            # SONRA "bilinir" (lag_bars=0 ise NAIVE/bias'li mod)
            known_idx = confirm_idx + lag_bars
            if known_idx >= n_total:
                pos += 1
                continue

            if direction == "up":
                ema_ok = ema50[known_idx] > ema200[known_idx]
                macd_ok = macd_l[known_idx] > macd_s[known_idx]
            else:
                ema_ok = ema50[known_idx] < ema200[known_idx]
                macd_ok = macd_l[known_idx] < macd_s[known_idx]

            if not (ema_ok and macd_ok):
                pos += 1
                continue

            break_idx = None
            limit_idx = min(n_total - 1, anchor + cap_bars)
            for i in range(known_idx + 1, limit_idx + 1):
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

            # EK DUZELTME (bu turde): known_idx ve break_idx'in KENDI ic bilgisi (o barin
            # kapanis/gostergeleri) ancak o barin KAPANISINDA (acilisinda degil) bilinir - bu
            # yuzden "bilinen zaman" = bar-acilis-zamani + bar-suresi olarak hesaplanir (H2'nin
            # break_known_time'da uyguladigi mantik, known_time'a da simetrik uygulanmistir)
            known_time = int(times[known_idx]) + bar_min * 60
            break_known_time = int(times[break_idx]) + bar_min * 60

            tradeable = break_idx > known_idx  # bilinen-andan ONCE kirilirsa hicbir zaman
            # "aktif ve bilinen" bir kanal olarak ISLEM ICIN kullanilamaz

            channels.append({
                "tf": tf_name, "direction": direction,
                "anchor_idx": int(anchor), "second_idx": int(second),
                "confirm_idx_ham": int(confirm_idx), "known_idx": int(known_idx),
                "break_idx": int(break_idx),
                "n_touches_total": int(len(touches)), "slope_per_bar_pts": float(slope / POINT),
                "anchor_time": int(anchor_time),
                "known_time": known_time, "break_time": int(times[break_idx]),
                "break_known_time": break_known_time,
                "anchor_price": float(anchor_price),
                "duration_bars_known_to_break": int(break_idx - known_idx),
                "censored_veri_sonu": bool(censored),
                "tradeable": bool(tradeable),
            })

            next_pos = np.searchsorted(swing_idx, break_idx, side="right")
            pos = max(next_pos, pos + 1)

        return channels

    channels_naive = {}
    channels_causal = {}
    for tf_name in ("H1", "M30"):
        channels_naive[tf_name] = {}
        channels_causal[tf_name] = {}
        for direction in ("up", "down"):
            ch_n = detect_channels(tf_name, direction, lag_bars=0)
            ch_c = detect_channels(tf_name, direction, lag_bars=LOOKAHEAD_LAG_BARS)
            channels_naive[tf_name][direction] = ch_n
            channels_causal[tf_name][direction] = ch_c
            n_tradeable = sum(1 for c in ch_c if c["tradeable"])
            print(tf_name, direction, "naive n=", len(ch_n), "causal n=", len(ch_c),
                  "causal tradeable=", n_tradeable)

    # onceki (kismi/hatali) denemeden kalan bt_h1_step_channels.json ile TUTARLILIK karsilastirmasi
    # (dogrudan KULLANILMADI - gerekce: copy_rates_from_pos farkli bir zaman noktasinda cagrilirsa
    # "count" pencere kaymasi nedeniyle array index'lerinin (anchor_idx/confirm_idx/known_idx/
    # break_idx) onceki calistirmadaki AYNI zaman noktalarina karsilik gelecegi garanti edilemez -
    # bu risk, ayni script calistirmasi icinde YENIDEN hesaplayarak ortadan kaldirildi. Asagida
    # sadece KANAL SAYISI bazinda bir tutarlilik/makul-luk kontrolu yapilir, index'ler KULLANILMAZ.)
    eski_json_karsilastirma = None
    if os.path.exists(OLD_CHANNELS_JSON):
        try:
            with open(OLD_CHANNELS_JSON, "r", encoding="utf-8") as f:
                eski = json.load(f)
            eski_json_karsilastirma = {}
            for tf_name in ("H1", "M30"):
                eski_json_karsilastirma[tf_name] = {}
                for direction in ("up", "down"):
                    eski_n = len(eski.get("causal", {}).get(tf_name, {}).get(direction, []))
                    yeni_n = len(channels_causal[tf_name][direction])
                    eski_json_karsilastirma[tf_name][direction] = {
                        "eski_dosya_causal_n": eski_n, "yeni_hesap_causal_n": yeni_n,
                        "fark": yeni_n - eski_n,
                        "tutarli_mi_yaklasik": abs(yeni_n - eski_n) <= max(2, round(0.1 * max(eski_n, yeni_n))),
                    }
        except Exception as e:
            eski_json_karsilastirma = {"hata": f"eski dosya okunamadi/karsilastirilamadi: {e}"}

    results["faz2_kanal_sayilari"] = {
        "naive": {tf: {d: len(channels_naive[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")},
        "causal": {tf: {d: len(channels_causal[tf][d]) for d in ("up", "down")} for tf in ("H1", "M30")},
        "causal_tradeable": {tf: {d: sum(1 for c in channels_causal[tf][d] if c["tradeable"])
                                   for d in ("up", "down")} for tf in ("H1", "M30")},
    }
    results["faz2_eski_dosya_ile_tutarlilik_karsilastirmasi"] = {
        "not": ("bt_h1_step_channels.json (onceki kismi denemeden kalan) DOGRUDAN KULLANILMADI - "
                "MT5 copy_rates_from_pos'un farkli zaman noktalarinda cagrildiginda array "
                "index'lerinin ayni zaman noktasina karsilik gelecegini GARANTI ETMEMESI riski "
                "nedeniyle butun kanal tespiti bu script icinde YENIDEN hesaplandi. Asagida sadece "
                "KANAL SAYISI bazinda bir makul-luk/tutarlilik kontrolu yapilmistir (index bazinda "
                "degil)."),
        "karsilastirma": eski_json_karsilastirma,
    }
    print("FAZ 2 tamamlandi. Eski dosyayla sayi-bazli karsilastirma:", eski_json_karsilastirma)

    # ============================================================
    # FAZ 3: M5 GIRIS-ZAMANLAMA PROJEKSIYONU (LOOK-AHEAD-SAFE)
    # ============================================================
    print("=" * 70)
    print("FAZ 3: M5 GIRIS-ZAMANLAMA PROJEKSIYONU (LOOK-AHEAD-SAFE)")
    print("=" * 70)

    m5_times = raw["M5"]['time'].astype(np.int64)
    m5_closes = raw["M5"]['close'].astype(float)
    m5_opens = raw["M5"]['open'].astype(float)
    m5_highs = raw["M5"]['high'].astype(float)
    m5_lows = raw["M5"]['low'].astype(float)
    m5_atr = ATR["M5"]
    m5_spread = raw["M5"]['spread'].astype(float)
    N_M5 = len(m5_closes)
    m5_t0, m5_t1 = int(m5_times[0]), int(m5_times[-1])

    def project_and_find_entries_m5(channels_htf):
        candidates = []
        n_overlap = 0
        for c in channels_htf:
            if not c["tradeable"]:
                continue
            conf_t = c["known_time"]
            brk_known_t = c["break_known_time"]
            if brk_known_t < m5_t0 or conf_t > m5_t1:
                continue
            n_overlap += 1
            win_start = max(conf_t, m5_t0)
            win_end = min(brk_known_t, m5_t1)
            lo = np.searchsorted(m5_times, win_start, side="left")
            hi = np.searchsorted(m5_times, win_end, side="right")
            if hi - lo < 3:
                continue

            sign = 1 if c["direction"] == "up" else -1
            anchor_price = c["anchor_price"]
            anchor_time = c["anchor_time"]
            bar_min_htf = TFS[c["tf"]][1]
            slope_per_bar = c["slope_per_bar_pts"] * POINT
            slope_per_sec = slope_per_bar / (bar_min_htf * 60)

            for i in range(lo, hi - 1):
                if np.isnan(m5_atr[i]):
                    continue
                t_i = int(m5_times[i])
                projected = anchor_price + slope_per_sec * (t_i - anchor_time)
                tol = TOUCH_K * m5_atr[i]
                diff = m5_closes[i] - projected
                if abs(diff) <= tol:
                    if i + 1 >= N_M5:
                        continue
                    # bir SONRAKI M5 barinin trend yonunde kapanmasi (yon-teyidi)
                    if sign * (m5_closes[i + 1] - m5_closes[i]) > 0:
                        exec_idx = i + 2  # yurutme-ani konvansiyonu (bkz. dosya-basi notu)
                        if exec_idx >= N_M5:
                            continue
                        if int(m5_times[exec_idx]) >= brk_known_t:
                            continue
                        candidates.append({
                            "exec_idx": exec_idx, "direction": c["direction"],
                            "atr_at_signal": float(m5_atr[i + 1]) if not np.isnan(m5_atr[i + 1]) else float(m5_atr[i]),
                            "channel": c, "touch_idx": int(i), "trigger_idx": int(i + 1),
                        })
        return candidates, n_overlap

    all_candidates = []
    overlap_counts = {}
    for tf_name in ("H1", "M30"):
        for direction in ("up", "down"):
            cands, n_ov = project_and_find_entries_m5(channels_causal[tf_name][direction])
            overlap_counts[f"{tf_name}_{direction}"] = n_ov
            all_candidates.extend(cands)
            print(f"{tf_name}->M5 {direction}: ortusen/tradeable kanal={n_ov}, aday-giris (look-ahead-safe)={len(cands)}")

    all_candidates.sort(key=lambda x: x["exec_idx"])
    print("Toplam aday-giris (dedup edilmemis, tum kombinasyonlar):", len(all_candidates))

    results["faz3_aday_giris_sayilari"] = {
        "kombinasyon_bazinda_ortusen_kanal": overlap_counts,
        "toplam_aday_giris_look_ahead_safe": len(all_candidates),
        "not_dar_orneklem": ("Bu, Stratejist'in Devir Notu 5'te isaretledigi dar-orneklem riskinin "
                              "dogrudan kaynagidir - H1/M30 kanal SAYISI (yukaridaki faz2) az, M5 "
                              "veri penceresiyle ORTUSEN ve tradeable olan kanal sayisi bundan da "
                              "azdir (yukaridaki 'ortusen/tradeable kanal' degerleri). Aday-giris "
                              "SAYISI yuksek gorunse bile, bunlar birkac bagimsiz kanal icinde "
                              "tekrarlanan olaylardir - bagimsiz orneklem buyuklugu kanal sayisidir, "
                              "aday-giris sayisi degil."),
    }
    print("FAZ 3 tamamlandi.")

    # ============================================================
    # FAZ 4: ON-KONTROL MADDE 2 - S1 MALIYET-ORANI, GERCEK SL/TP MESAFELERIYLE
    # ============================================================
    print("=" * 70)
    print("FAZ 4: ON-KONTROL MADDE 2 - S1 MALIYET-ORANI (GERCEK SL/TP, M5)")
    print("=" * 70)

    atr_m5_median = float(np.nanmedian(m5_atr))
    spread_m5_median = float(np.median(m5_spread))
    # slipaj kalibrasyonu: justin_backtest_onkontrol_standardi.md Madde 2'de referans alinan
    # ~%3.7 slipaj/ATR orani (M5 kesitinden turetilmis bir kalibrasyon) - burada dogrudan M5
    # verisiyle calisildigi icin AYNI kalibrasyon birebir uygulanabilir
    slippage_est_m5 = 0.037 * atr_m5_median
    cost_pts_total = spread_m5_median + slippage_est_m5
    print(f"M5: spread_median={spread_m5_median:.2f}, ATR14_median={atr_m5_median:.2f}, "
          f"slippage_est={slippage_est_m5:.2f}, TOPLAM_MALIYET={cost_pts_total:.2f} pts")

    # Dar/hizli (scalping-uyumlu) SL grid + S1'i test edecek genis bir TP grid - Stratejist SL/TP
    # kesin katsayisini BILEREK belirlemedi (asiri-optimize etmeme ilkesi), bu grid Backtest
    # Muhendisi'nin walk-forward kalibrasyonu icin tasarladigi arama uzayidir (mimari degil,
    # kalibrasyon serbestligi - justin_backtest_onkontrol_standardi.md Madde 3 ile tutarli)
    SL_MULT_GRID = [0.25, 0.5, 0.75, 1.0]
    TP_MULT_GRID = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]

    precheck_rows = []
    for tp_m in TP_MULT_GRID:
        tp_pts_repr = tp_m * atr_m5_median
        ratio = tp_pts_repr / cost_pts_total
        precheck_rows.append({
            "tp_mult_atr": tp_m, "temsili_tp_pts": round(tp_pts_repr, 1),
            "maliyet_orani": round(ratio, 2),
            "gecti_mi_15x": bool(ratio >= 15.0), "gecti_mi_20x": bool(ratio >= 20.0),
        })
        print(f"  TP={tp_m}xATR ({tp_pts_repr:.1f}pts) -> oran={ratio:.2f}x "
              f"[15x:{'GECTI' if ratio >= 15 else 'KALDI'} / 20x:{'GECTI' if ratio >= 20 else 'KALDI'}]")

    TP_MULT_SURVIVED = [r["tp_mult_atr"] for r in precheck_rows if r["gecti_mi_15x"]]
    print("On-kontrolu (>=15x) GECEN TP carpanlari:", TP_MULT_SURVIVED)

    on_kontrol_karar = "ANA_TESTE_GECILEBILIR" if TP_MULT_SURVIVED else "RED_ON_KONTROLDE_KAPANDI"
    results["faz4_on_kontrol_maliyet_orani"] = {
        "spread_median_pts": round(spread_m5_median, 2),
        "atr14_median_pts": round(atr_m5_median, 2),
        "slippage_tahmini_pts": round(slippage_est_m5, 2),
        "toplam_maliyet_pts": round(cost_pts_total, 2),
        "sl_mult_grid": SL_MULT_GRID, "tp_mult_grid": TP_MULT_GRID,
        "hucre_bazinda_sonuc": precheck_rows,
        "on_kontrolu_gecen_tp_mult": TP_MULT_SURVIVED,
        "karar": on_kontrol_karar,
    }
    print("FAZ 4 tamamlandi. Karar:", on_kontrol_karar)

    if not TP_MULT_SURVIVED:
        # RED - bu bir HATA/exception DEGIL, gecerli bir backtest sonucudur. Ana teste GECILMEZ,
        # ama script BASARIYLA tamamlanir (hata_log YAZILMAZ) - sadece rapor "on-kontrolde elendi"
        # der.
        results["nihai_durum"] = "RED_ON_KONTROLDE_KAPANDI_ANA_TESTE_GECILMEDI"
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print("H1 on-kontrolde elendi (S1 >=15x hicbir TP carpaninda saglanamiyor). JSON yazildi, "
              "ana test/walk-forward ATLANDI.")
        mt5.shutdown()
        return results

    # ============================================================
    # FAZ 5: TRAIN / VALIDATION / TEST AYRIMI (purged/embargolu, zaman-bazli)
    # ============================================================
    print("=" * 70)
    print("FAZ 5: TRAIN / VALIDATION / TEST AYRIMI")
    print("=" * 70)

    total_days = (m5_t1 - m5_t0) / 86400.0
    train_end_t = m5_t0 + int(total_days * TRAIN_FRAC * 86400)
    val_start_t = train_end_t + EMBARGO_DAYS * 86400
    val_end_t = val_start_t + int(total_days * VAL_FRAC * 86400)
    test_start_t = val_end_t + EMBARGO_DAYS * 86400
    test_end_t = m5_t1

    split_bounds = {
        "train": (m5_t0, train_end_t),
        "validation": (val_start_t, val_end_t),
        "test": (test_start_t, test_end_t),
    }
    for k, (a, b) in split_bounds.items():
        print(f"  {k}: {datetime.fromtimestamp(a, tz=timezone.utc)} -> {datetime.fromtimestamp(b, tz=timezone.utc)} "
              f"({(b - a) / 86400.0:.0f} gun)")

    results["faz5_split_sinirlari"] = {
        k: {"baslangic": str(datetime.fromtimestamp(a, tz=timezone.utc)),
            "bitis": str(datetime.fromtimestamp(b, tz=timezone.utc)),
            "gun": round((b - a) / 86400.0, 1)}
        for k, (a, b) in split_bounds.items()
    }

    def split_of_time(t):
        for k, (a, b) in split_bounds.items():
            if a <= t <= b:
                return k
        return "embargo"

    cross_split_channels = 0
    total_channels_checked = 0
    for tf_name in ("H1", "M30"):
        for direction in ("up", "down"):
            for c in channels_causal[tf_name][direction]:
                if not c["tradeable"]:
                    continue
                total_channels_checked += 1
                s1 = split_of_time(c["known_time"])
                s2 = split_of_time(c["break_known_time"])
                if s1 != s2 and s1 != "embargo" and s2 != "embargo":
                    cross_split_channels += 1
    print(f"Split-sinirini asan kanal sayisi (known ve break farkli split'te): "
          f"{cross_split_channels}/{total_channels_checked}")
    results["faz5_cross_split_kanal_uyarisi"] = {
        "cross_split_kanal_sayisi": cross_split_channels, "toplam_kanal": total_channels_checked,
        "not": ("Giris-zamani (entry exec_idx) bazinda split atamasi yapilmistir (kanal-bazli purge "
                "DEGIL). Bir kanalin known ve break anlari farkli split'lere dusuyorsa, o kanalin "
                "erken girisleri Train'de, gec girisleri Validation/Test'te gorunebilir - AYNI "
                "yapisal kanalin edge'inin birden fazla split'e sizmasi riski (zayif purge). Bu "
                "sayi yukaridaysa Validation/Test sonuclari o olcude daha az 'bagimsiz' okunmalidir "
                "- bu bir SINIRLAMA olarak asagida acikca raporlanir. H1'de kanal sayisi zaten az "
                "oldugu icin bu oran H2'ye gore DAHA VOLATIL/az-anlamli olabilir."),
    }

    for cand in all_candidates:
        cand["split"] = split_of_time(int(m5_times[cand["exec_idx"]]))

    split_counts = {}
    for k in ("train", "validation", "test", "embargo"):
        split_counts[k] = sum(1 for c in all_candidates if c["split"] == k)
    print("Aday-giris split dagilimi:", split_counts)
    results["faz5_aday_giris_split_dagilimi"] = split_counts
    print("FAZ 5 tamamlandi.")

    # ============================================================
    # FAZ 6: TRADE SIMULASYONU (tek-pozisyon, uc-kosullu cikis)
    # ============================================================
    print("=" * 70)
    print("FAZ 6: TRADE SIMULASYONU FONKSIYONU")
    print("=" * 70)

    def floor_lot(x, step=LOT_STEP_USD):
        return math.floor(x / step) * step

    def simulate_trades(candidates_subset, sl_mult, tp_mult, kasa=KASA_USD):
        """Tek-pozisyon sirali simulasyon. candidates_subset zaten exec_idx'e gore SIRALI olmali."""
        trades = []
        pos_open_until_idx = -1
        n_overlap_skipped = 0
        n_break_before_open = 0

        for cand in candidates_subset:
            entry_idx = cand["exec_idx"]
            if entry_idx <= pos_open_until_idx:
                n_overlap_skipped += 1
                continue

            direction = cand["direction"]
            sign = 1 if direction == "up" else -1
            atr_sig = cand["atr_at_signal"]
            if np.isnan(atr_sig) or atr_sig <= 0:
                continue
            sl_pts = sl_mult * atr_sig
            tp_pts = tp_mult * atr_sig
            entry_price = float(m5_opens[entry_idx])
            break_known_t = cand["channel"]["break_known_time"]

            if int(m5_times[entry_idx]) >= break_known_t:
                n_break_before_open += 1
                continue

            if sign == 1:
                sl_price = entry_price - sl_pts * POINT
                tp_price = entry_price + tp_pts * POINT
            else:
                sl_price = entry_price + sl_pts * POINT
                tp_price = entry_price - tp_pts * POINT

            exit_idx = None
            exit_reason = None
            exit_price = None
            j = entry_idx
            while j < N_M5:
                t_j = int(m5_times[j])
                bar_open_after_break = t_j >= break_known_t
                hi, lo = float(m5_highs[j]), float(m5_lows[j])
                if sign == 1:
                    sl_hit = lo <= sl_price
                    tp_hit = hi >= tp_price
                else:
                    sl_hit = hi >= sl_price
                    tp_hit = lo <= tp_price

                if sl_hit:  # muhafazakar varsayim: ayni barda SL+TP varsa SL kazanir
                    exit_idx, exit_reason, exit_price = j, "SL", sl_price
                    break
                if tp_hit:
                    exit_idx, exit_reason, exit_price = j, "TP", tp_price
                    break
                if bar_open_after_break:
                    exit_idx, exit_reason, exit_price = j, "KIRILIM_ERKEN_CIKIS", float(m5_closes[j])
                    break
                j += 1
            if exit_idx is None:
                exit_idx = N_M5 - 1
                exit_reason = "VERI_SONU_ACIK"
                exit_price = float(m5_closes[exit_idx])

            gross_pnl_pts = sign * (exit_price - entry_price) / POINT
            net_pnl_pts = gross_pnl_pts - cost_pts_total

            lot = max(TABAN_LOT, floor_lot((kasa * RISK_PCT_UST_SINIR) / sl_pts))
            pnl_usd = net_pnl_pts * USD_PER_POINT_PER_LOT * lot

            hold_bars = exit_idx - entry_idx
            trades.append({
                "entry_idx": int(entry_idx), "exit_idx": int(exit_idx),
                "entry_time": str(datetime.fromtimestamp(int(m5_times[entry_idx]), tz=timezone.utc)),
                "exit_time": str(datetime.fromtimestamp(int(m5_times[exit_idx]), tz=timezone.utc)),
                "direction": direction, "tf_source": cand["channel"]["tf"],
                "sl_pts": round(sl_pts, 1), "tp_pts": round(tp_pts, 1),
                "exit_reason": exit_reason,
                "gross_pnl_pts": round(gross_pnl_pts, 2), "net_pnl_pts": round(net_pnl_pts, 2),
                "lot": round(lot, 2), "pnl_usd": round(pnl_usd, 4),
                "hold_bars_m5": int(hold_bars), "hold_hours": round(hold_bars * 5 / 60.0, 3),
                "split": cand["split"],
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
    # FAZ 7: WALK-FORWARD SL/TP KALIBRASYONU
    # ============================================================
    print("=" * 70)
    print("FAZ 7: WALK-FORWARD SL/TP KALIBRASYONU")
    print("=" * 70)

    train_cands = [c for c in all_candidates if c["split"] == "train"]
    val_cands = [c for c in all_candidates if c["split"] == "validation"]
    test_cands = [c for c in all_candidates if c["split"] == "test"]
    print(f"Ham aday sayilari: train={len(train_cands)}, validation={len(val_cands)}, test={len(test_cands)}")

    MIN_TRADES_FOR_SELECTION = 30
    grid_results = []
    for sl_m in SL_MULT_GRID:
        for tp_m in TP_MULT_SURVIVED:
            tr_trades, tr_ov, tr_brk = simulate_trades(train_cands, sl_m, tp_m)
            va_trades, va_ov, va_brk = simulate_trades(val_cands, sl_m, tp_m)
            tr_sum = summarize_trades(tr_trades)
            va_sum = summarize_trades(va_trades)
            grid_results.append({
                "sl_mult": sl_m, "tp_mult": tp_m,
                "train": tr_sum, "validation": va_sum,
                "train_overlap_skipped": tr_ov, "validation_overlap_skipped": va_ov,
            })
            pf_tr = tr_sum.get("profit_factor")
            pf_va = va_sum.get("profit_factor")
            print(f"  SL={sl_m}xATR TP={tp_m}xATR -> Train(n={tr_sum.get('n_trades')}, PF={pf_tr}) | "
                  f"Validation(n={va_sum.get('n_trades')}, PF={pf_va})")

    results["faz7_grid_tarama"] = grid_results

    eligible = [g for g in grid_results if g["validation"].get("n_trades", 0) >= MIN_TRADES_FOR_SELECTION
                and g["validation"].get("profit_factor") is not None]
    if eligible:
        best = max(eligible, key=lambda g: g["validation"]["profit_factor"])
        secim_notu = f"Validation'da PF'ye gore secildi (n>={MIN_TRADES_FOR_SELECTION} sarti saglayan {len(eligible)} hucre arasindan)."
    else:
        candidates_by_n = [g for g in grid_results if g["validation"].get("n_trades", 0) > 0]
        if candidates_by_n:
            best = max(candidates_by_n, key=lambda g: g["validation"].get("n_trades", 0))
            secim_notu = (f"HICBIR hucre Validation'da n>={MIN_TRADES_FOR_SELECTION} esigini GECMEDI - "
                          f"en fazla islem sayisina sahip hucre secildi (n={best['validation']['n_trades']}), "
                          f"bu secim ZAYIF/dusuk-guvenilirlikli olarak isaretlenmelidir (H1'in dar-orneklem "
                          f"riskiyle DOGRUDAN tutarli bir sonuc).")
        else:
            best = grid_results[0]
            secim_notu = ("Validation'da HICBIR hucrede islem olusmadi - ilk grid hucresi varsayilan "
                          "olarak kullanildi (guvenilmez, H1'in dar-orneklem riskinin en agir gorunumu).")

    SELECTED_SL_MULT = best["sl_mult"]
    SELECTED_TP_MULT = best["tp_mult"]
    print(f"SECILEN KOMBINASYON: SL={SELECTED_SL_MULT}xATR14_M5, TP={SELECTED_TP_MULT}xATR14_M5")
    print(secim_notu)

    results["faz7_secim"] = {
        "secilen_sl_mult": SELECTED_SL_MULT, "secilen_tp_mult": SELECTED_TP_MULT,
        "secim_notu": secim_notu, "min_trades_esigi": MIN_TRADES_FOR_SELECTION,
    }

    test_trades, test_ov, test_brk = simulate_trades(test_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
    test_summary = summarize_trades(test_trades)
    print("TEST SONUCU (tek kez):", test_summary)

    train_trades_final, train_ov_final, train_brk_final = simulate_trades(train_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
    val_trades_final, val_ov_final, val_brk_final = simulate_trades(val_cands, SELECTED_SL_MULT, SELECTED_TP_MULT)
    train_summary_final = summarize_trades(train_trades_final)
    val_summary_final = summarize_trades(val_trades_final)

    all_cands_sorted = sorted(all_candidates, key=lambda x: x["exec_idx"])
    full_trades, full_ov, full_brk = simulate_trades(all_cands_sorted, SELECTED_SL_MULT, SELECTED_TP_MULT)
    full_summary = summarize_trades(full_trades)
    print("TAM DONEM (train+val+test birlikte, tek-pozisyon TUM eksende) SONUCU:", full_summary)

    results["faz7_final_sonuclar"] = {
        "train": train_summary_final, "validation": val_summary_final, "test": test_summary,
        "tam_donem_birlesik": full_summary,
        "overlap_skipped": {"train": train_ov_final, "validation": val_ov_final, "test": test_ov, "tam_donem": full_ov},
        "kanal_kirilmis_giris_reddi": {"train": train_brk_final, "validation": val_brk_final, "test": test_brk, "tam_donem": full_brk},
    }
    print("FAZ 7 tamamlandi.")

    # ============================================================
    # FAZ 8: KIRILIM-BAZLI-ERKEN-CIKIS DOGRULAMA ORNEKLERI
    # ============================================================
    print("=" * 70)
    print("FAZ 8: KIRILIM-BAZLI-ERKEN-CIKIS DOGRULAMA")
    print("=" * 70)

    break_exit_trades = [t for t in full_trades if t["exit_reason"] == "KIRILIM_ERKEN_CIKIS"]
    print(f"Tam donemde KIRILIM_ERKEN_CIKIS ile kapanan islem sayisi: {len(break_exit_trades)} / {len(full_trades)}")

    sample_examples = break_exit_trades[:5]
    validation_examples = []
    for t in sample_examples:
        validation_examples.append({
            "entry_time": t["entry_time"], "exit_time": t["exit_time"],
            "direction": t["direction"], "tf_source": t["tf_source"],
            "hold_hours": t["hold_hours"], "net_pnl_pts": t["net_pnl_pts"],
            "dogrulama": ("exit_time, ilgili kanalin break_known_time'indan (kanalin H1/M30 kapanisiyla "
                           "kirildigi + bar suresi) SONRA veya AYNI ana denk gelmeli, VE bu bardan once "
                           "SL/TP tetiklenmemis olmali (kod: 'j' dongusu SL/TP kontrolunu break kontrolunden "
                           "ONCE yapiyor, ayni bar icinde SL/TP varsa erken-cikisten ONCELIKLIDIR)."),
        })

    results["faz8_kirilim_erken_cikis_dogrulama"] = {
        "toplam_kirilim_cikisi": len(break_exit_trades), "toplam_islem_tam_donem": len(full_trades),
        "oran": round(len(break_exit_trades) / len(full_trades), 4) if full_trades else None,
        "ornek_islemler": validation_examples,
        "yontem_notu": ("Kod, her M5 barinda SIRASIYLA (1) SL, (2) TP, (3) kanal-kirilim-bilgisi-var-mi "
                         "kontrolu yapar (bkz. simulate_trades ic dongusu) - ayni barda SL/TP VE kirilim "
                         "AYNI ANDA gecerliyse SL/TP ONCELIKLIDIR (muhafazakar/gercekci varsayim). Bu, "
                         "Stratejist'in 'SL/TP/kirilim - HANGISI ONCE gerceklesirse' tanimiyla TUTARLIDIR."),
    }
    print("FAZ 8 tamamlandi.")

    # ============================================================
    # FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + KAYIT
    # ============================================================
    print("=" * 70)
    print("FAZ 9: ISLEM FREKANSI + KIRILIM ANALIZI + JSON YAZIMI")
    print("=" * 70)

    if full_trades:
        entry_dates = [datetime.fromisoformat(t["entry_time"]).date() for t in full_trades]
        n_months = max(1, (entry_dates[-1].year - entry_dates[0].year) * 12 + (entry_dates[-1].month - entry_dates[0].month) + 1)
        n_years = (entry_dates[-1] - entry_dates[0]).days / 365.25 if len(entry_dates) > 1 else 1.0
        trades_per_month = len(full_trades) / n_months
        trades_per_year = len(full_trades) / n_years if n_years > 0 else None
    else:
        trades_per_month = None
        trades_per_year = None

    print(f"Islem/ay (tam donem): {trades_per_month}, Islem/yil: {trades_per_year}")

    kirilim_tf = {}
    kirilim_yon = {}
    for t in full_trades:
        kirilim_tf.setdefault(t["tf_source"], []).append(t["net_pnl_pts"])
        kirilim_yon.setdefault(t["direction"], []).append(t["net_pnl_pts"])

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
        "islem_ay_sayisi_tam_donem": round(trades_per_month, 2) if trades_per_month else None,
        "islem_yil_sayisi_tam_donem": round(trades_per_year, 2) if trades_per_year else None,
        "toplam_islem_tam_donem": len(full_trades),
        "bagimsiz_kanal_sayisi_hatirlatma": results["faz2_kanal_sayilari"]["causal_tradeable"],
        "not": ("Islem/ay-yil sayisi YUKSEK gorunse bile, bunlarin kok orneklem buyuklugu az sayida "
                "bagimsiz H1/M30 kanaldir (yukaridaki 'bagimsiz_kanal_sayisi_hatirlatma') - Devir "
                "Notu 5/7 ve Stratejist'in 'dar-kanit' etiketiyle DOGRUDAN ilgili bir gerilim, Risk "
                "Analisti'ne SOMUT sayiyla burada tekrar vurgulanmistir."),
    }
    results["faz9_kirilim_tf_kaynagi"] = group_summary(kirilim_tf)
    results["faz9_kirilim_yon"] = group_summary(kirilim_yon)
    results["islem_logu_ornek"] = full_trades[:20] + (full_trades[-20:] if len(full_trades) > 20 else [])
    results["nihai_durum"] = "TAMAMLANDI"

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("TAMAMLANDI ->", OUT_PATH)

    if full_trades:
        pd.DataFrame(full_trades).to_csv(r"C:\MilaYatirim\Justin\backtest_A_ailesi_H1_islem_logu_tam.csv",
                                           index=False, encoding="utf-8-sig")
        print("Tam islem logu CSV yazildi.")

    mt5.shutdown()
    print("BITTI.")
    return results


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        with open(HATA_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(tb)
        print("HATA OLUSTU - traceback bt_h1_hata_log dosyasina yazildi:")
        print(tb)
        try:
            mt5.shutdown()
        except Exception:
            pass
        raise
