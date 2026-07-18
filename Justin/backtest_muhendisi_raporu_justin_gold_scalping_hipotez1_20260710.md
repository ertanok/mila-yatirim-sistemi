# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — HIPOTEZ 1

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: 3/4 (Backtest Muhendisi)
Tarih: 10 Temmuz 2026
Girdi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260710.md (HIPOTEZ 1, satir 38-88)
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)
Kod: C:\MilaYatirim\Justin\backtest_hipotez1.py
Ham cikti (tam detay, tum senaryolar): C:\MilaYatirim\Justin\backtest_hipotez1_output.json

Izolasyon notu: Bu calisma sirasinda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya
(signal.json, milagold_trades.json, lisa_performance.json, positions_status.json,
stratejici_gold_gecmis_calisma.md vb.) okunmadi/kullanilmadi. MilaGold'un sabit
0,01 lot / 5$-3$-5$-8$ SL-TP yapisi hic bir yerde referans alinmadi; SL/TP tamami ile
ATR(14,M5)-bazli ve Stratejist'in tasarimina gore uygulandi. Veri dogrudan MT5'ten
(GOLD sembolu, copy_rates_from_pos, M5, 99.999 bar) cekildi.

---

## 0) SAAT ESLEME DOGRULAMASI (Acik Soru 1 / Muhendis Notu 3 — ZORUNLU)

Iki bagimsiz kontrol yapildi:

**(a) Canli-an capraz kontrolu:** MT5'in son tick zamani (`tick.time`) UTC gibi okunup
VPS'in yerel saatiyle (CLAUDE.md: VPS = GMT+3) karsilastirildi.
- Epoch-UTC-okuma: 2026-07-10 19:58:25
- VPS yerel simdi: 2026-07-10 19:58:25.62
- Fark: 0,62 saniye → su anki (Temmuz 2026, yaz/yaz-saati donemi) offset = GMT+3 dogrulanmistir.

**(b) Hafta sonu gecis (DST) kontrolu — bilinen rollover zamanindan geriye dogru dogrulama:**
Veri araligi (2025-02-10 → 2026-07-10) icinde AB/GMT+2↔+3 DST gecis tarihlerinin uc tanesi
(2025-03-30, 2025-10-26, 2026-03-29) yer aliyor. Her gecis civarinda Cuma-kapanis barinin
(hafta sonu bosluğundan hemen once) sunucu-saat etiketi incelendi:

| Gecis Tarihi | Once (Cuma kapanis saati) | Sonra (Cuma kapanis saati) | Kayma Tespit Edildi mi? |
|---|---|---|---|
| 2025-03-30 | 22 (sabit) | 23 (sabit) | **EVET** |
| 2025-10-26 | 23 (sabit) | 22/23 (karisik, gecis haftalari) | Belirsiz (US-DST farkli tarihte degistigi icin karisik) |
| 2026-03-29 | 22 (sabit) | 23 (sabit) | **EVET** |

**SONUC:** Iki net gecis noktasinda (2025-03-30, 2026-03-29) Cuma-kapanis saatinin sabit
degerden (22) baska bir sabit degere (23) kaydigi tespit edilmistir. Bu, sunucunun YIL BOYUNCA
sabit GMT+3 calismadigini, muhtemelen AB/Kibris DST takvimini izleyen bir offset kullandigini
gosterir (yaz aylarinda GMT+3, kis aylarinda muhtemelen GMT+2). **Bu, mevcut saat-bazli
filtrelerin (15-18, 0-2, 22-23) yalniz yaz-DST donemi (yaklasik son Mart - son Ekim) icin
"sunucu saati = GMT+3" varsayimiyla tutarli oldugu, kis aylarinda (son Ekim - son Mart) bu
filtrelerin 1 saat kaymis olabilecegi anlamina gelir.** Bu backtest'teki tum saat etiketleri
(Arastirmaci'nin BULGU1/BULGU2'siyle ayni yontemle, epoch'un UTC gibi okunmasiyla) hesaplanmistir;
yani asagidaki "15-18" filtresi mevsime gore fiilen GMT+3 (yaz) veya GMT+2 (kis) sunucu saatine
denk gelebilir. Bu bulgu Risk Analisti'ne ayrica iletiliyor (bkz. UYARILAR).

---

## 1) YONTEM / MUHENDISLIK VARSAYIMLARI

- **Sinyal:** M5 kapanis, 20-bar SMA − (k × rolling-std) esiginin ALTINA dustugunde LONG
  (alt-sapma), k=2,0 baseline; k∈{1,5; 2,0; 2,5} dar tarama (ince ayar yapilmadi).
- **Giris:** iki varyant ayri ayri test edildi — (A) sinyal barinin kapanisinda (fiili
  yürürlükte hafif iyimser: karar ve fiyat ayni bar), (B) bir sonraki bar acilisinda
  (bakis-siz/gerceklenebilir). ATR, sinyal barinin kapanisindaki degeri kullanir (iki
  varyantta da ileri-bakis yok).
- **Cikis:** (1) yalniz N=5 bar sonra zaman-bazli, (2) yalniz ATR(14,M5)-bazli TP/SL (1:1),
  taninmazsa 50 bar sonra zorla kapatma (muhendislik siniri, Stratejist N belirtmedigi icin),
  (3) combined: ATR TP/SL VEYA N=5 bar zaman-asimi, hangisi once ise. Ayni barda hem SL hem
  TP araligina girilirse muhafazakar varsayimla SL vuruldu sayildi.
- **Pozisyon yonetimi:** Tek pozisyon; bir islem acikken yeni sinyaller atlanir (non-overlapping,
  gercekci execution varsayimi — ham sinyal sayisi 6111 iken orta-kesinlikte cakisma nedeniyle
  539 sinyal atlandi).
- **Maliyet:** MT5'in bar-kapanisinda rapor ettigi broker spread'i (points), girisin
  gerceklestigi bardaki deger, round-trip maliyet olarak uygulandi. SINIR: bu, tam tick-bazli
  slipaj simulasyonu DEGILDIR (Arastirmaci'nin BULGU2 SINIR notuyla ayni kisit); ancak saatlik
  ortalama yerine HER islemin kendi giris barinin gercek spread'i kullanildigi icin, sabit/ortalama
  bir varsayimdan daha hassastir.
- **Detrend:** rolling lineer trend, 100-bar pencere (nedensel/causal — yalniz gecmis veriyle
  hesaplanir). GEREKCE: 100 bar (~8,3 saat), BULGU6'daki 17 aylik yon-onyargisini bastiracak
  kadar uzun, 20-barlik sinyal penceresini bozacak kadar kisa degil. Detrend testinde sinyal
  ZAMANLAMASI detrended seriden uretildi, GERCEK P&L ise ham/gercek fiyattan hesaplandi (piyasada
  yalniz gercek fiyat islem gorur).
- **Veri bolumu:** IS = ilk %70 (bar-index), OOS = son %30; ayrica 6 esit-uzunlukta walk-forward
  penceresi (~2,8 ay/pencere).
- **1,0 standart lot varsayimi:** Stratejist bu hipotez icin lot/risk-yonetimi belirlemedi;
  "net_profit_usd" degerleri yalniz KIYASLAMA amacli 1,0 standart lot varsayimiyla hesaplanmistir
  (1 puan = 1 USD/lot, point=0,01, contract_size=100). Gercek pozisyon boyutlandirma ayri bir
  karardir, bu raporun kapsami disindadir.

---

## 2) JSON RAPORU (ANA KONFIGURASYON)

```json
{
  "hipotez_adi": "Seans-Filtreli Asimetrik Ortalamaya-Donus (Mean-Reversion) - HIPOTEZ 1",
  "yaklasim_turu": "kural-tabanli (istatistiksel sapma filtresi + ATR-bazli risk)",
  "test_tarihi": "2026-07-10",
  "parametreler": {
    "sinyal_penceresi_SMA_std": 20,
    "k_sapma_carpani": 2.0,
    "k_tarama_araligi": [1.5, 2.0, 2.5],
    "atr_periyodu": 14,
    "rr_orani": 1.0,
    "n_bar_zaman_cikisi": 5,
    "giris_yontemi": "next_open (bir sonraki bar acilisi) - ana; close (sinyal bari kapanisi) - karsilastirma",
    "cikis_yontemi": "combined: ATR TP/SL veya N-bar zaman, hangisi once",
    "seans_filtresi": "sunucu saati 15-18 (birincil)",
    "detrend_penceresi": 100
  },
  "veri": {
    "kaynak": "MT5/XM, GOLD sembolu, copy_rates_from_pos M5",
    "baslangic": "2025-02-11",
    "bitis": "2026-07-10",
    "toplam_ornek": 99999,
    "bolum_bilgisi": "IS = ilk %70 (bar 0-69999, ~2025-02-11/2026-04-16), OOS = son %30 (bar 70000-99999, ~2026-04-16/2026-07-10); ayrica 6 esit walk-forward penceresi"
  },
  "sonuclar": {
    "toplam_islem": 699,
    "win_rate": 0.4764,
    "profit_factor": 0.843,
    "net_profit_usd_per_1_0_lot": -39408.21,
    "max_drawdown_pts": -42458.79,
    "ortalama_atr_entry_pts": 674.73,
    "ortalama_spread_entry_pts": 33.05,
    "spread_TP_orani_medyan": 0.06,
    "ham_sinyal_sayisi": 6111,
    "cakisma_nedeniyle_atlanan": 539,
    "seans_disi_nedeniyle_atlanan": 4873
  },
  "gorulmemis_veri_sonuclari": {
    "OOS_son_%30": {
      "toplam_islem": 213,
      "win_rate": 0.493,
      "profit_factor": 0.96,
      "net_profit_usd_per_1_0_lot": -3694.79,
      "max_drawdown_pts": -16260.79
    },
    "walk_forward_6_pencere_profit_factor": [0.839, 0.684, 0.727, 0.993, 0.891, 0.813],
    "walk_forward_6_pencere_net_pts": [-4856.43, -8736.43, -7945.64, -265.14, -8806.29, -8798.29]
  },
  "kirilim_analizi": {
    "giris_yontemi_close_vs_next_open_PF": {"next_open": 0.843, "close": 0.88},
    "cikis_yontemi_PF": {"yalniz_zaman_N5": 0.953, "yalniz_ATR_TP_SL": 0.846, "combined": 0.843},
    "cikis_yontemi_zaman_N5_IS_vs_OOS_PF": {"IS": 0.79, "OOS": 1.238},
    "k_duyarlilik_PF_tum_donem": {"1.5": 0.857, "2.0": 0.843, "2.5": 0.728},
    "k_duyarlilik_OOS_PF": {"1.5": 0.796, "2.0": 0.96, "2.5": 0.751},
    "seans_filtresi_PF": {"filtresiz": 0.876, "birincil_15_18": 0.843, "birincil+ikincil_15_18_3_4": 0.865},
    "seans_filtresi_OOS_PF": {"filtresiz": 0.902, "birincil_15_18": 0.96, "birincil+ikincil": 0.937},
    "detrend_PF": {"ham_fiyat_long_only": 0.843, "detrended_long_only": 0.86, "detrended_simetrik_long+short": 0.82},
    "detrend_OOS_PF": {"ham_fiyat_long_only": 0.96, "detrended_long_only": 0.875, "detrended_simetrik": 0.806},
    "detrend_simetrik_bacak_kirilimi_PF": {"long_bacagi": 0.862, "short_bacagi": 0.763}
  },
  "islem_logu": "Tam log JSON dosyasinda degil (boyut nedeniyle 25+25 ornek tutuldu); ana konfigurasyon icin bkz. backtest_hipotez1_output.json -> senaryolar.ANA_KONFIGURASYON.islem_logu_ornek",
  "uyarilar": [
    "SAAT_ESLEME_UYARISI: DST gecis analizinde 2 net gecis noktasinda 1-saat kayma tespit edildi - GMT+3 varsayimi yalniz yaz-DST doneminde net gecerli, kis aylarinda 15-18/0-2/22-23 filtreleri fiilen 1 saat kaymis olabilir.",
    "TUM_KONFIGURASYONLARDA_PROFIT_FACTOR_1_ALTINDA: ana konfigurasyon ve k/seans/detrend/giris-yontemi taramalarinin NEREDEYSE TAMAMINDA tum-donem PF<1 olcduldu; tek kismi istisna asagida.",
    "OVERFITTING_RISKI (yalniz-N-bar-zaman cikis varyanti): IS PF=0.79 iken OOS PF=1.238 - buyuk IS/OOS sapmasi, walk-forward ile dogrulanmadi (yalniz baseline/combined-exit icin 6-pencere walk-forward kosturuldu, bu varyant icin kosturulmadi) - bu OOS'taki pozitif sonuc tek bir 70/30 bolme uzerinden gelmektedir, ayri walk-forward olmadan guvenilir sayilamaz.",
    "SEANS_FiLTRESiNiN_NET_KATKISI_BELiRSiZ: filtresiz IS PF (0.857) filtreli-15-18 IS PF'den (0.774) daha iyi, ancak filtreli-15-18 OOS PF (0.96) filtresiz OOS PF'den (0.902) daha iyi - tutarli/tek yonlu bir katki gozlenmedi.",
    "DETREND_SONUCU: detrended seri BULGU6 drift onyargisini kaldirdiginda edge negatif kalmaya devam ediyor (PF hala <1 tum-donem ve OOS'ta); yani BULGU5'teki pozitif ortalama ileri-getiri, gercekci TP/SL/maliyet yapisiyla test edildiginde (ne ham ne detrended veride) tutarli bir pozitif profit_factor'e donusmuyor.",
    "SPREAD_MALIYET_KUCUK: spread/TP orani medyan 0,05-0,09 araliginda (Stratejist'in Risk-3 endisesinin aksine, bu ozel test kurgusunda spread kayiplarin ana kaynagi degil; kayiplarin kaynagi %50 altinda seyreden kazanma orani + 1:1 R:R yapisi).",
    "MALIYET_SIMULASYONU_SINIRI: tick-bazli slipaj degil, bar-kapanis broker-spread'i kullanildi (Arastirmaci BULGU2 SINIR notuyla ayni kisit).",
    "MAX_HOLD_MUHENDISLIK_SINIRI: yalniz-ATR-TP/SL varyantinda Stratejist bir zaman siniri belirtmedigi icin 50 bar (~4 saat) zorla-kapatma siniri eklendi - bu Stratejist'in tasarimina bir ekleme degil, test edilebilirlik icin gerekli bir muhendislik parametresidir, ayrica onaylanmalidir."
  ]
}
```

---

## 3) DETAYLI KIRILIM TABLOLARI

### 3.1 Giris Yontemi (next_open vs close), k=2,0, session=15-18, exit=combined

| Yontem | Islem | Win% | PF | Net (pts) | IS PF | OOS PF |
|---|---|---|---|---|---|---|
| next_open (ana) | 699 | 47,64 | 0,843 | -39.408,21 | 0,774 | 0,960 |
| close (kirilma bari) | 699 | 48,50 | 0,880 | -29.658,79 | 0,823 | 0,972 |

### 3.2 Cikis Yontemi, k=2,0, next_open, session=15-18

| Yontem | Islem | Win% | PF | Net (pts) | IS PF | OOS PF |
|---|---|---|---|---|---|---|
| yalniz N=5 bar zaman | 473 | 51,80 | 0,953 | -12.159,00 | 0,790 | **1,238** |
| yalniz ATR TP/SL (50-bar cap) | 699 | 48,21 | 0,846 | -39.495,14 | 0,778 | 0,961 |
| combined (ana) | 699 | 47,64 | 0,843 | -39.408,21 | 0,774 | 0,960 |

### 3.3 K Duyarlilik Taramasi (next_open, session=15-18, exit=combined)

| k | Islem | Win% (tum) | PF (tum) | PF (IS) | PF (OOS) |
|---|---|---|---|---|---|
| 1,5 | 1201 | 47,88 | 0,857 | 0,897 | 0,796 |
| 2,0 (baseline) | 699 | 47,64 | 0,843 | 0,774 | 0,960 |
| 2,5 | 304 | 45,72 | 0,728 | 0,713 | 0,751 |

### 3.4 Seans Filtresi (k=2,0, next_open, exit=combined)

| Filtre | Islem | PF (tum) | PF (IS) | PF (OOS) |
|---|---|---|---|---|
| filtresiz (tum saatler) | 3542 | 0,876 | 0,857 | 0,902 |
| birincil 15-18 (ana) | 699 | 0,843 | 0,774 | 0,960 |
| birincil+ikincil (15-18, 3-4) | 1103 | 0,865 | 0,822 | 0,937 |

### 3.5 Detrend Testi ZORUNLU (k=2,0, next_open, exit=combined, session=15-18)

| Varyant | Islem | PF (tum) | PF (IS) | PF (OOS) |
|---|---|---|---|---|
| ham fiyat, long-only (baseline) | 699 | 0,843 | 0,774 | 0,960 |
| detrended, long-only | 701 | 0,860 | 0,850 | 0,875 |
| detrended, simetrik (long+short) | 1238 | 0,820 | 0,830 | 0,806 |
| — detrended simetrik / yalniz long bacagi | 698 | 0,862 | - | - |
| — detrended simetrik / yalniz short bacagi | 540 | 0,763 | - | - |

### 3.6 Walk-Forward (6 pencere, ana konfigurasyon)

| Pencere | Tarih | Islem | Win% | PF | Net (pts) |
|---|---|---|---|---|---|
| 1 | 2025-02-11 / 2025-05-07 | 130 | 46,15 | 0,839 | -4.856,43 |
| 2 | 2025-05-07 / 2025-07-31 | 118 | 43,22 | 0,684 | -8.736,43 |
| 3 | 2025-07-31 / 2025-10-23 | 100 | 49,00 | 0,727 | -7.945,64 |
| 4 | 2025-10-23 / 2026-01-21 | 113 | 51,33 | 0,993 | -265,14 |
| 5 | 2026-01-21 / 2026-04-16 | 113 | 49,56 | 0,891 | -8.806,29 |
| 6 | 2026-04-16 / 2026-07-10 | 125 | 47,20 | 0,813 | -8.798,29 |

Not: 6 pencerenin de profit_factor'u 1'in altinda (0,684-0,993 araligi) — zaman ustunde
tutarli bir sekilde negatif, tek bir donemin sonucu carpitmasi soz konusu degil.

---

## 4) MINIMUM ORNEKLEM DEGERLENDIRMESI

Tum konfigurasyonlarda islem sayisi 88 (en dar k=2,5 OOS) ile 3542 (filtresiz tum donem)
arasinda degisiyor; ana konfigurasyonun IS (486) ve OOS (213) orneklemleri istatistiksel
olarak yeterli buyuklukte (n>200), "yetersiz veri" uyarisi gerekmiyor. En dar alt-kirilim
(k=2,5 OOS, n=88) sinirda ancak yorumlanabilir; tek basina karar dayanagi olarak
kullanilmamalidir.

---

## 5) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — Seans-Filtreli Asimetrik Ortalamaya-Donus (HIPOTEZ 1) — Kural-tabanli — 2026-07-10

Egitim / In-Sample (ilk %70, ~2025-02-11/2026-04-16):
  Islem: 486 | Win rate: %46,91 | Profit Factor: 0,774 | Net: -35.713 puan

Gorulmemis Veri (OOS, son %30, ~2026-04-16/2026-07-10):
  Islem: 213 | Win rate: %49,30 | Profit Factor: 0,960 | Net: -3.694,79 puan

Walk-Forward (6 pencere, ~17 ay): Profit Factor araligi 0,684-0,993, 6 pencerenin
  TAMAMI 1'in altinda (tutarli negatif, tek-donem carpitmasi yok).

Dikkat noktalari:
  - SAAT ESLEME: DST gecis analizi, sunucunun yil boyunca SABIT GMT+3 calismadigini,
    muhtemelen AB/Kibris DST takvimini izlediğini gosteriyor (2025-03-30 ve 2026-03-29
    gecislerinde Cuma-kapanis saat-etiketi 22->23 kaydi). Kis aylarinda (~son Ekim-son Mart)
    saat-bazli filtreler (15-18, 0-2, 22-23) fiilen 1 saat kaymis olabilir - bu backtest'in
    tum saat kirilimlari mevcut (dogrulanmamis) GMT+3-sabit varsayimiyla hesaplanmistir.
  - Ana konfigurasyon ve hemen hemen tum tarama kombinasyonlarinda (k, seans filtresi,
    detrend, giris yontemi) profit_factor 1'in ALTINDA olctu - tek istisna: "yalniz N-bar
    zaman-bazli cikis" varyanti OOS'ta PF=1,238 verdi, ancak IS'te PF=0,79 idi (OVERFITTING_RISKI
    flagi - buyuk IS/OOS sapmasi, ayrica walk-forward ile dogrulanmadi, tek 70/30 bolmeye dayanir).
  - Seans filtresinin (15-18) net katkisi TUTARSIZ: IS'te filtresiz konfigurasyon daha iyi
    (PF 0,857 vs 0,774), OOS'ta filtreli konfigurasyon daha iyi (PF 0,96 vs 0,902) - tek yonlu
    bir katki gozlenmedi.
  - ZORUNLU detrend testi: BULGU6 drift-onyargisi fiyattan cikarildiginda (100-bar rolling
    lineer trend) edge pozitife DONMEDI - hem long-only (PF 0,86 tum-donem / 0,875 OOS) hem
    simetrik long+short (PF 0,82 tum-donem / 0,806 OOS) versiyonlarda profit_factor 1'in altinda
    kaldi. Short bacagi (ust-sapma reversal) long bacagindan daha zayif (PF 0,763 vs 0,862).
  - Spread maliyeti kayiplarin ana kaynagi DEGIL (spread/TP orani medyan 0,05-0,09); asil
    etken kazanma oraninin (%43-52 araliginda, cogunlukla <%50) 1:1 risk/odul yapisiyla
    profit_factor>1 icin yeterli gelmemesi.
  - Maliyet simulasyonu bar-kapanis broker-spread'ine dayanir, tam tick-bazli slipaj DEGILDIR.
  - Minimum orneklem: ana IS/OOS yeterli (n=486/213); en dar alt-kirilim (k=2,5 OOS, n=88)
    sinirda, tek basina karar dayanagi olamaz.

Detay dosya: C:\MilaYatirim\Justin\backtest_hipotez1_output.json (tam senaryo detaylari)
Kod: C:\MilaYatirim\Justin\backtest_hipotez1.py
```

---

## 6) IZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) ACILMADI
  veya referans ALINMADI.
- MilaGold'un aktif parametreleri (M5 EMA20, EMA100 streak>=13, trailing stop, 0,01 lot,
  5$/3$/5$/8$ SL/TP) hicbir sekilde kullanilmadi; SL/TP tamamen ATR(14,M5)-bazli/dinamik olarak
  Stratejist'in HIPOTEZ 1 tasarimina gore uygulandi.
- Calisma yalniz C:\MilaYatirim\Justin\ dizininde yapildi; veri dogrudan MT5'ten (MetaTrader5
  python kutuphanesi, headless/RDP'siz) cekildi.

---

## 7) ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik dogrulama,
canli sisteme dokunus yok, Justin demo/arastirma asamasinda). Sonuc uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
