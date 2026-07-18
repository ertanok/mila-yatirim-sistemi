# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — ML/Feature-Tabanli Aile v2 (ML Tam Tur 2) — HIPOTEZ 3
## OLCEKLENEBILIRLIK PILOTU (DUSUK ONCELIK) — Grup D (Mikro-Yapi/Tick-Proxy) + Hipotez 1 Feature Seti, 90-Gunluk Kisitli Pencere

Tarih: 2026-07-12
Hipotez adi: LightGBM Ikili Yon-Tahmini + Grup 1-5/B/D — 90 GUNLUK KISITLI/PILOT PENCERE — HIPOTEZ 3 (v2/Tur2)
Yaklasim turu: Makine Ogrenmesi — Gradient Boosting (LightGBM, binary) + kural-tabanli tick-agregasyon (Grup D girdisi)
Oncelik: **3-Dusuk** (Stratejist raporu) — bu sonuc Tur 2'nin nihai KABUL/RED kararinin **TEK BASINA
dayanagi DEGILDIR**; Hipotez 1/2 birincil, bu hipotez tamamlayici/on-gozlem niteligindedir.
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md` (Karar 4, Hipotez 3)
Cerceve: `justin_gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md` (S2, ZORUNLU),
`justin_backtest_onkontrol_standardi.md` (S1 + DST + SL/TP-ozel, ZORUNLU)
Script: `backtest_ml_v2_hipotez3.py` | Ham veri: `backtest_ml_v2_hipotez3_output.json`
Karsilastirma referansi (baglam icin, DOGRUDAN KARSILASTIRILAMAZ): `backtest_muhendisi_raporu_
justin_gold_scalping_ml_v2_hipotez1_20260712.md`

---

## 0) CERCEVELEME (Stratejist'in ZORUNLU talebi — rapor bastan boyle okunmalidir)

Bu hipotez, ana Hipotez 1/2'nin 4,2 yillik egitim/test setinden **TAMAMEN AYRI**, kucuk-olcekli bir
alt-deneydir (Stratejist Karar 4). Veri penceresi SADECE son 90 islem gunudur (~%1,1'i tam-tarihsel
serinin). Bu nedenle:
- Sonuc **"KESIN RED/KABUL" olarak SUNULMAZ** — "bu olcekte ilk gozlem, tam-tarihsel olceklendirme
  HALA cozulmemis" seklinde cercevelenir.
- **Olceklenebilirlik durumu COZULMEDI:** bu hipotez BASARILI (KABUL) ciksa bile, Grup D'nin 4,2
  yillik tam egitim setine nasil tasinacagi (M1-proxy veya baska bir yontem) bu raporla COZULMEZ —
  ayri bir tasarim/muhendislik sorusu olarak ACIK birakilir.
- Bu turun Risk Analisti'nin Tur 2 nihai KABUL/RED kararinda Hipotez 1/2 BIRINCIL dayanaktir; bu
  hipotez SADECE tamamlayici/on-gozlem niteligindedir (S3 governance sayacini etkileyen ana karar
  bu hipoteze DAYANDIRILMAMALIDIR).

---

## 1) KUTUPHANE ON-KOSULU

Hipotez 1/2 (v2/Tur2) turlerinde zaten dogrulanmisti (pandas 3.0.3, lightgbm 4.6.0, scikit-learn
1.9.0). Bu turde YENIDEN KURULUM YAPILMADI — gorev talimati geregi (Stratejist Notu Madde 7) atlandi,
versiyonlarin DEGISMEDIGI teyit edildi.

---

## 2) VERI PENCERESI / TICK-CEKME SURESI

### 2.1 Pencere Tanimi
- **Pencere: SADECE son 90 islem gunu** (2026-03-06 → 2026-07-10, 8.238 M15-bar). Stratejist'in
  onerdigi 60-90 gun araliginin **UST SINIRI** secildi — gerekce: (a) daha genis orneklem, kucuk-n'in
  dogurdugu dusuk-istatistiksel-guc riskini kismen azaltir; (b) ampirik tick-cekme suresi (asagida)
  bu secimi PRATIK olarak rahatlikla destekliyor, ek maliyet onemsiz.
- **Warmup: 25 ek islem gunu** (2026-01-23'ten itibaren, toplam cekilen 14.000 M15-bar / 154 islem
  gunu icinden) — SADECE nedensel rolling feature'larin (ROLL_SR_WINDOW=20 gun, TRAIL_WINDOW=100 bar,
  MTF SMA20) ilk degerlerini doldurmak icin kullanildi; bu barlar egitim/test/ornek SAYISINA
  KATILMADI (feature_valid_in_window = feature_valid & window_mask ile cift-guvenceli kisitlama,
  bkz. Bolum 4, feature-sizinti-kontrol-listesi Madde 7).
- Bu, ana Hipotez 1/2'nin 4,2 yillik (2022-04-18→2026-07-10) TRAINVAL/TEST bolumuyle **TAMAMEN AYRI**
  bir alt-deneydir; hicbir bar/ornek iki sette ORTAK KULLANILMADI.

### 2.2 Tick-Cekme Suresi (Grup D icin, ampirik olcum)
Script calistirilmadan once, 4 farkli pencere buyuklugunde (60/75/90/120 islem gunu) bu ortamda
BAGIMSIZ bir on-olcum yapildi:

| Pencere (islem gunu) | Tick sayisi | Cekme suresi (sn) |
|---|---|---|
| 60 | 22.046.968 | 7,791 |
| 75 | 27.987.987 | 9,927 |
| 90 | 34.404.837 | 4,184 |
| 120 | 46.262.729 | 17,764 |

(Sureler makine/onbellek durumuna gore degisken olabilir — nihai script calistirmasinda 90-gunluk
pencere icin GERCEK cekme suresi **2,247 saniye**, 34.404.837 tick idi.) Stratejist'in "60-90 gun
~7-11 saniye" tahmini, bu ortamda GERCEKTE DAHA HIZLI cikti (tek `copy_ticks_range` cagrisi,
bellek-verimli filtreleme) — bu, 90-gunluk (ust sinir) secimini PRATIK olarak rahatlikla destekler.

### 2.3 Feature Seti
Hipotez 1 ile **BIREBIR AYNI** Grup 1-5 + Grup B (29 sutun) + **YENI Grup D** (4 sutun:
`tick_imbalance_ratio`, `tick_count_bucket`, `tick_mid_ret_std`, `tick_avg_spread_pts`) = **33 sutun
toplam**. Grup D tanimlari Arastirmaci BULGU 7-9 ile AYNI kavramsal tanima dayanir (tick-kural
isareti/imbalance, bucket-ici tick sayisi, mid-fiyat getiri std'si, ask-bid ortalamasi) — ancak KOD
BAGIMSIZ olarak sifirdan yazildi (Arastirmaci'nin script'i referans ALINMADI).

**Grup D ozet istatistikler (bu pencere, n=8.238 bucket, eslesme orani %100,0):**

| Olcum | Bu pencere (90 gun) | Arastirmaci BULGU 7-9 (20 gun, referans/DOGRUDAN KARSILASTIRILAMAZ) |
|---|---|---|
| Bucket-basi medyan tick sayisi | 3.939,5 | 4.520,5 |
| Imbalance medyan | 0,0013 | 0,0027 |
| Imbalance P10/P90 | [-0,0481 / +0,0522] | [-0,0407 / +0,0610] |
| Tick-seviyesi ortalama spread medyan | 53,46 pts | 54,82 pts |
| mid_ret_std medyan | 1,933e-05 | 1,847e-05 |

Bu sayilar **farkli pencere/uzunluk** (90 gun vs 20 gun, farkli tarih araligi) nedeniyle DOGRUDAN
esitlenmesi beklenmez (CLAUDE.md sayisal-tutarlilik ilkesi) — ancak BUYUKLUK MERTEBESI olarak
BULGU 7-9 ile TUTARLI cikmasi, Grup D olcum yonteminin (bagimsiz kod ile) makul sekilde
tekrarlanabilir oldugunu gosterir.

---

## 3) NEDENSELLIK KONTROLU [GRUP D] — BAGIMSIZ (Stratejist'in ozel talebi geregi, Arastirmaci'nin
kendi ic-mantik iddiasi YETERLI SAYILMADI)

Uc AYRI kontrol uygulandi (script, `grup_d_nedensellik_dogrulamasi_BAGIMSIZ` bolumu):

1. **Bucket-sinir spot-check (200 ornek bucket, tam tarama sinir-disi sayaci):** her ornek bucket'in
   TUM ticklerinin epoch'u `[bucket_key*900, bucket_key*900+900)` araliginda mi kontrol edildi.
   **Sonuc: 200/200 bucket'ta sinir-disi tick sayisi = 0.** Ornek (bucket_key=1969732): 961 tick,
   ilk_tick_epoch=1772758831, son_tick_epoch=1772759665, ikisi de [1772758800, 1772759700) icinde.
2. **Bar-epoch/tick-bucket birim uyumu (3 ornek bar):** her ornek barin epoch'unun 900'un tam kati
   oldugu (M15 hizalamasi) dogrulandi — **3/3 bar_epoch_multiple_of_900_mu = True.**
3. **"Son tick < bar bitisi" kontrolu (ayni 3 ornek bar):** her barin Grup D degerini besleyen
   bucket'taki SON tick'in epoch'unun, o barin bitis epoch'undan (bar_key*900+900) KESINLIKLE ONCE
   oldugu dogrulandi — **3/3 son_tick_bar_bitisinden_ONCE_mi = True** (ornek: bar_idx=7821,
   bucket_son_tick_epoch=1775642399 < bar_bitis_epoch=1775642400).

**SONUC: GECTI** — Grup D'nin tick-agregasyonlarinin M15-bucket icinde NEDENSEL/ileri-bakissiz
oldugu, Arastirmaci'nin BULGU 7-9'daki kendi iddiasina DAYANILMADAN, sifirdan/bagimsiz kod-
incelemesi + assert + spot-check ile dogrulandi. Hicbir ihlal bulunmadi (script bu kontrolleri
`assert` ile de zorunlu kilar — herhangi bir ihlal olsaydi script HATA verip duracakti).

**Yontemsel not (SINIR olarak acikca belirtilir):** `mid_ret_std` hesaplamasinda tick-bazli getiri
GLOBAL/surekli hesaplanip sonra bucket'a gore gruplanmistir — bucket sinirini gecen TEK bir getiri
noktasi (onceki bucket'in son tick'inden bu bucket'in ilk tick'ine) bir YAKLASIKLIK olarak kabul
edilmistir (Arastirmaci'nin BULGU 8 tanimiyla AYNI ruhta, birebir ayni kod DEGIL). Bu, ~8.238
bucket'tan HER birinde SADECE 1 sinir-noktasini etkileyen ihmal edilebilir bir yaklasikliktir,
ileri-bakis riski TASIMAZ (o sinir-noktasindaki iki tick de HALA GECMISTEN gelir).

---

## 4) FEATURE-SIZINTI KONTROL LiSTESi (S2 Madde 3 — madde madde teyit)

| # | Kontrol | Sonuc |
|---|---|---|
| 1 | Ileri-bakan bilgi var mi | HAYIR — Grup 1-5/B Hipotez1 ile AYNI (nedensel rolling); Grup D yukaridaki 3 bagimsiz kontrolle dogrulandi |
| 2 | Etiket-hesaplama veriyi dolayli iceriyor mu | HAYIR — etiket SADECE bar i'nin ATR14'u + i+1..i+16 yolu; Grup D SADECE bar i'nin KENDI [t_i,t_i+900) araligi |
| 3 | Normalizasyon SADECE egitim setinden mi | EVET — fold/final_train_idx'ten hesaplanan mu/sd, val/TEST'e uygulanir; Grup D de HICBIR global/test-icerikli istatistikle olceklendirilmedi |
| 4 | DST dogrulamasindan gecti mi | EVET — BAGIMSIZ tekrar calistirildi (Bolum 5) |
| 5 | MACD ham deger mi | HAM DEGER (Hipotez1 ile AYNI) |
| 6 | Grup D nedensellik BAGIMSIZ kontrolu | EVET — Bolum 3, Arastirmaci'nin iddiasina DAYANILMADAN |
| 7 | Pilot pencere warmup sizintisi var mi | HAYIR — warmup barlari idx_pool'a hicbir zaman DAHIL EDILMEDI (cift-guvenceli window_mask kisitlamasi) |

---

## 5) DST / SAAT-ESLESME DOGRULAMASI — BAGIMSIZ, TEKRAR CALISTIRILDI

Onceki turden DEVRALINMADI (gorev talimati geregi — Grup B gun/hafta-siniri + Grup D tick-bucket-
siniri GMT+3/DST varsayimina dayandigi icin). Toplam cekilen veri (warmup+pencere, 2025-12-04 →
2026-07-10) icinde bilinen DST gecisleri tarandi: **1/1 degerlendirilebilir DST gecisinde
(2026-03-29) piyasa-acilis saati 1 SAAT KAYDI** — MT5 sunucusu DST'yi TAKIP EDIYOR, Hipotez1/2 ile
AYNI sonuc BAGIMSIZ olarak tekrar-uretildi. (Diger DST gecisleri (2022-2025) bu 154-gunluk cekilen
veri araliginin DISINDA kaldigi icin degerlendirilemedi — bu, veri araliginin kisaligindan
kaynaklanan DOGAL bir sinirdir, bir hata degildir.)

---

## 6) ANA TEST TASARIMI

### 6.1 Etiket ve Risk (Hipotez 1 ile BIREBIR AYNI — Backtest-Onkontrol-Standardi Madde 3 geregi
otomatik tasima YOK, bu deger Stratejist'in ACIKCA belirttigi bir karardir)
- Triple-barrier, **N=16 M15-bar (4 saat)** zaman-bariyeri, **SL=TP=1,5xATR14(M15)** (RR=1:1).
- Model: LightGBM ikili siniflandirici, Hipotez 1 ile BIREBIR AYNI sabit/dar hiperparametreler
  (`num_leaves=31, max_depth=6, learning_rate=0.05, n_estimators=500, min_child_samples=50,
  subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, random_state=42`).
- Lot/risk: `justin_gecmis_calisma.md` geregi kasa=2.000 USD, lot=0,01 (sabit), risk-basi=kasa x %1
  UST SINIR.

### 6.2 Pencere-Ici Veri Bolumu (Karar 4 geregi ORANTILI kucultulmus purge/embargo)
- Pencere: 8.238 bar (2026-03-06→2026-07-10). Kronolojik **TRAINVAL (%80, ilk) / TEST (%20, son)**.
- **Embargo: "N=16-bar purge + 1 GUNLUK embargo"** — Stratejist'in onerisi geregi Hipotez1/2'nin
  tam-tarihsel 24-bar/6-saat SABIT embargosu YERINE, bu 90-gunluk pencereye ORANTILI, GUN-BAZLI bir
  deger kullanildi: bu penceredeki tipik/aktif islem gununun medyan bar sayisi (92 bar/gun) esas
  alinarak **EMBARGO_BARS_PILOT=92 bar (1 islem gunu)** hesaplandi. Purge, ana Hipotez1/2 ile AYNI
  ilkeyle (`i+N_BARS<=trainval_end_bar`) AYRICA/EK olarak uygulandi.
- TRAINVAL: 2026-03-06→2026-06-16 (n=5.924 ikili-etiketli). TEST: 2026-06-17→2026-07-10 (n=1.370
  ikili-etiketli), **TEK KEZ** kullanildi (S2 Madde 2).
- Toplam pencere etiket dagilimi: gecerli_bar=8.222, yukari-bariyer-once=3.353, asagi-bariyer-
  once=4.039, hicbiri=830 (**hicbiri orani ~%10,1** — Hipotez1'in tam-tarihsel ~%13,1'inden biraz
  DUSUK, farkli/daha kisa donem+volatilite rejimi nedeniyle beklenen bir fark).

### 6.3 Purged/Embargolu Walk-Forward (S2 Madde 1 ZORUNLU — pencere kucuk oldugu icin fold-basi n
Hipotez1'den ONEMLI OLCUDE DUSUK, bu ACIKCA raporlanir)

| Fold | Train n | Val n | Val AUC | best_iteration |
|---|---|---|---|---|
| 1 | 1.197 | 1.091 | 0,5823 | 3 |
| 2 | 2.389 | 1.072 | 0,4555 | 1 |
| 3 | 3.550 | 1.096 | 0,5876 | 39 |
| 4 | 4.747 | 1.086 | 0,5510 | 2 |

**AUC ozet: ortalama=0,5441, std=0,0530, min=0,4555, max=0,5876.**

> Hipotez 1'in tam-tarihsel walk-forward AUC'undan (ortalama=0,5075, std=0,0122) DAHA YUKSEK
> ORTALAMA ve BELIRGIN OLCUDE DAHA YUKSEK STD (0,0530 vs 0,0122) gozlemlendi. Bu, kucuk fold-basi
> n'in (ortalama ~1.086 val, Hipotez1'in ortalama ~11.930'unun ~%9'u) AUC tahminine getirdigi
> GURULTUYU/VARYANSI yansitiyor olabilir — DAHA YUKSEK ortalama AUC, GERCEK bir sinyal artisindan
> ZIYADE kucuk-orneklem-varyansi ile TUTARLI, bu asagidaki TEST sonucuyla (Bolum 6.4) birlikte
> degerlendirilmelidir (bu bir yorum degil, Bolum 0'daki cerceveleme ilkesinin dogrudan uygulamasi).

### 6.4 Esik Kalibrasyonu (out-of-fold, TEST setine BAKILMADI — S2 Madde 2)

| Esik (Long/Short) | Long n | Long WR-proxy | Short n | Short WR-proxy | Toplam n | Kapsama |
|---|---|---|---|---|---|---|
| 0,60 / 0,40 | 77 | 0,5844 | 743 | 0,6191 | 820 | %18,87 |
| 0,575 / 0,425 | 101 | 0,5545 | 1.301 | 0,5611 | 1.402 | %32,27 |
| 0,55 / 0,45 | 136 | 0,5074 | 2.022 | 0,5445 | 2.158 | %49,67 |

**SECILEN ESIK: 0,60 / 0,40** (en yuksek ortalama precision-proxy, MIN_SAMPLE=30 esigini HER IKI
tarafta da rahatlikla gecti — **fallback GEREKMEDI**, Hipotez1'in aksine burada out-of-fold kumede
gercek adaylar bulundu).

### 6.5 Final Model Egitimi
- Egitim n=4.747, ic-validasyon n=1.086, **ic-validasyon AUC=0,5510**, **best_iteration=2** (erken
  durma yine cok erken — pratikte 1-3 agac, Hipotez1'in best_iteration=1'i ile AYNI KARAKTERDE).
- **Feature-onem tablosu (gain/split, ilk 10):**

| Feature | Onem |
|---|---|
| dist_daily_pivot_pts (Grup B) | 10 |
| dist_roll20_low_pts (Grup B) | 8 |
| rsi14 (Grup 5) | 5 |
| dist_roll20_high_pts (Grup B) | 5 |
| hour_cos (Grup 4) | 4 |
| dow (Grup 4) | 3 |
| dist_weekly_pivot_pts (Grup B) | 3 |
| atr_regime_ratio (Grup 1) | 2 |
| hour_sin (Grup 4) | 2 |
| lag_ret_8 (Grup 5) | 2 |
| **tick_avg_spread_pts (Grup D)** | **2** |
| **tick_mid_ret_std (Grup D)** | **1** |
| **tick_imbalance_ratio (Grup D)** | **0** |
| **tick_count_bucket (Grup D)** | **0** |
| atr14_m15, m15_trend, h1_trend_aligned, h4_trend_aligned, confluence_flag, vol_ratio_trail100, session_*, lag_ret_1/4, macd_line, directional_streak, near_roll20_*_flag | 0 (tumu) |

**ONEMLI GOZLEM (Grup D'nin ana motivasyonu olan imbalance feature'i icin):** Arastirmaci'nin
BULGU 7'de "guclu ama kirilgan" olarak isaretledigi **`tick_imbalance_ratio` bu pencerede modele
HICBIR (0) agirlik kazandirmadi** — model bu feature'i pratik olarak HIC KULLANMADI. `tick_
avg_spread_pts` ve `tick_mid_ret_std` sadece marjinal (2 ve 1) agirlik aldi. Buna karsilik, Grup
B'nin (pivot/rolling-S-R) gorece-konum feature'lari (`dist_daily_pivot_pts=10, dist_roll20_low_
pts=8, dist_roll20_high_pts=5, dist_weekly_pivot_pts=3`) bu pencerede Hipotez1'in tam-tarihsel
sonucundan (atr14_h1_aligned=10, dow=6 en yuksekti, Grup B o zaman ~0-dusuk idi) FARKLI BIR PATERN
gostererek en yuksek agirliklari aldi. Bu, **DOGRUDAN KARSILASTIRILAMAZ** (farkli veri araligi/
olcek) ama **kayda-deger bir gozlemdir**: kisitli/yakin-donem pencerede Grup B relatif olarak daha
belirgin, Grup D (mikro-yapi/imbalance) ise ZAYIF kaldi — Arastirmaci'nin BULGU 7'deki medyan-fark
buyuklugu (-254 vs +4 puan) ile modelin bu feature'a verdigi ~sifir agirlik arasindaki CELISKI,
Arastirmaci'nin kendisinin de BULGU 7'de flagledigi "medyan-fark, birkac buyuk-buyuklukte outlier
bar tarafindan yonlendirilmis olabilir" uyarisiyla TUTARLIDIR.

### 6.6 TEST Seti (tek-kez) Siniflandirma Performansi ve Tani
- **TEST AUC=0,5084** (rassal-seviyeye yakin, Hipotez1'in tam-tarihsel TEST AUC'u 0,5170'e YAKIN).
- p_test dagilimi: **min=0,4200, max=0,5087, ortalama=0,4564, std=0,0139** — kalibre edilen esige
  (0,60 LONG / 0,40 SHORT) **HICBIR ZAMAN ulasmiyor** (esik_long_asan=0, esik_short_asan=0 bar).

---

## 7) SONUCLAR [ISTATISTIKSEL GUC SINIRLI]

### 7.1 PRIMARY Test-Seti Simulasyonu (hicbiri-haric)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / Profit Factor / Net Kar / Max DD | tumu tanimsiz (n=0) |

### 7.2 SUPPLEMENTARY Test-Seti Simulasyonu (hicbiri-dahil, canliya-yakin capraz kontrol)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / PF / Net kar / Max DD | tumu tanimsiz (n=0) |

### 7.3 HEDEF Karsilastirmasi ve KARAR

| Kriter | Hedef | Gozlemlenen (PRIMARY) | Gozlemlenen (SUPPLEMENTARY) |
|---|---|---|---|
| PF | >=1,5 | tanimsiz (n=0) | tanimsiz (n=0) |
| WR (RR=1:1) | >=%60,0 | tanimsiz (n=0) | tanimsiz (n=0) |
| DD | <=%20 kumulatif | tanimsiz (n=0) | tanimsiz (n=0) |

**KARAR: RED.** Gerekce: PRIMARY test setinde 0 islem tetiklendi (p_test max=0,5087, kalibre
edilen esik 0,60'in altinda kaldi) — Ortak Ilkeler'deki minimum orneklem uyarisi + S2 Madde 4
(basari kriterlerinin egitimden once sabitlenmesi, sonradan gevsetilmemesi) geregi, olculemeyen
bir kriterin karsilandigi iddia edilemez.

> **CERCEVELEME HATIRLATMASI (Bolum 0, tekrar):** Bu RED karari **"Grup D/mikro-yapi kesin
> basarisiz" ANLAMINA GELMEZ** — sonuc, bu 90-gunluk kisitli pencerede (istatistiksel guc SINIRLI,
> ~1.370 test-bar) modelin TEST setinde yeterince guvenli/ayirt-edici olasiliklar URETEMEDIGINI
> gosterir; bu Hipotez1'in TAM-TARIHSEL sonucuyla (0 islem, RED) **NITEL OLARAK TUTARLI**dir, ama
> FARKLI olcekte/pencerede elde edilmis, BAGIMSIZ bir gozlemdir.

### 7.4 S1 — Maliyet-Orani (Pencereye Ozel, OPSIYONEL Ek Teyit — ZORUNLU DEGILDI)

| Olcum | Deger |
|---|---|
| ATR14(M15) medyan (bu pencere) | 983,61 pts |
| Bar-kapanis spread medyan (bu pencere) | 40,0 pts |
| Tick-seviyesi ORTALAMA spread medyan (Grup D) | 53,46 pts |
| Hedef (1,5xATR medyan) | 1.475,41 pts |
| Oran — medyan bar-kapanis-spread | **36,89x** |
| Oran — P90 bar-kapanis-spread (stres testi) | **28,93x** |
| Oran — medyan TICK-SEVIYESI spread (ek/muhafazakar teyit) | **27,60x** |
| Esik alt sinir | 15,0x |
| GECTI mi (medyan/P90/tick-teyit, ucu de) | **EVET/EVET/EVET** |

Bu pencereye ozel oranlar (36,89x/28,93x), Hipotez1'in tam-tarihsel oranlarindan (15,97x/11,91x)
**BELIRGIN OLCUDE YUKSEK** — bu bir hata DEGIL, bu 90-gunluk yakin-donemin (2026 Q1-Q2) daha genis
ATR'ye/gorece dar spread'e sahip olmasini yansitir (FARKLI veri araligi, DOGRUDAN
KARSILASTIRILAMAZ). Sonuc: bu pencerede maliyet-duvari ENDISESI YOKTU — 0-islem sonucu maliyet
kisitindan DEGIL, modelin olasilik-dagiliminin esige ulasamamasindan kaynaklanir (Bolum 6.6).

---

## 8) OLCEKLENEBILIRLIK DURUMU [COZULMEDI — ACIK SORU OLARAK KALIR]

Bu hipotezin sonucu (RED, 0-islem, TEST AUC~0,51) ne olursa olsun, **Grup D'nin (mikro-yapi/tick-
proxy) 4,2 yillik tam Hipotez1/2 egitim setine nasil tasinacagi bu rapor tarafindan COZULMEMISTIR**:

- Bu pencerede 90 islem gunu icin 34,4 milyon tick 2,25 saniyede cekilebildi/islenebildi — ancak
  4,2 yillik (~1.050+ islem gunu) tam tarihe DOGRUDAN oranlama yapilirsa (~90 gunun ~11,7 kati)
  tahmini tick hacmi **~400+ milyon tick** mertebesine ulasir. Bu raporun script'i BU OLCEGI
  DENEMEDI/TEST ETMEDI (gorev tanimi kapsami disinda) — MT5 tarafinin bu hacmi TEK bir
  `copy_ticks_range` cagrisinda karsilayip karsilamayacagi, bellek/zaman-asimi siniri olup
  olmadigi BILINMIYOR.
- Alternatif yontemler (orn. Karar 4'te bahsedilen "secenek (b): M1-bar-tabanli kaba proxy") bu
  turde TASARLANMADI/TEST EDILMEDI — Stratejist'in Karar 4'u bunu ACIKCA bu turun kapsami disinda
  birakmisti.
- **Sonuc: bu rapor Grup D icin "kucuk pencerede TEKNIK OLARAK CALISIYOR" seklinde bir on-gozlem
  sunar (nedensellik dogrulandi, tick-cekme pratik, feature hesaplama basarili) — ama "4,2 yillik
  tarihe NASIL olceklenecegi" sorusuna HICBIR YANIT VERMEZ.** Bu, ayri bir tasarim/muhendislik
  gorevi olarak Stratejist/Orkestrator'a acik birakilmalidir (Acik Soru, gorev tanimi Karar4 ile
  TUTARLI).

---

## 9) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — LightGBM Ikili Yon-Tahmini + Grup 1-5/B/D (90-GUNLUK KISITLI PILOT) — HIPOTEZ 3 (v2/Tur2, ML/Gradient Boosting) — 2026-07-12

*** ONCELIK: 3-DUSUK / ON-GOZLEM — Hipotez 1/2 birincil dayanaktir, bu sonuc Tur 2 nihai kararinin TEK BASINA dayanagi OLAMAZ ***
*** ISTATISTIKSEL GUC SINIRLI: pencere=90 islem gunu (8.238 bar), TEST n=1.370 - sonuc "KESIN RED/KABUL" degil "bu olcekte ilk gozlem" olarak okunmalidir ***

Veri Penceresi: 2026-03-06 -> 2026-07-10 (90 islem gunu, ana Hipotez1/2'nin 4,2 yillik setinden TAMAMEN AYRI)
Grup D tick-cekme: 34.404.837 tick, 2,25 saniyede cekildi - nedensellik BAGIMSIZ dogrulandi (3/3 kontrol GECTI, Bolum 3)

Egitim / Walk-Forward (4 fold, purged+embargolu-1-gun, SADECE diagnostik):
  AUC ortalama=0,5441 (std=0,0530, min=0,4555, max=0,5876) - Hipotez1'in tam-tarihsel (0,5075/std0,0122) degerinden YUKSEK
  ORTALAMA ve BELIRGIN DAHA YUKSEK VARYANS - kucuk fold-basi n (~1.086) kaynakli gurultu ihtimali YUKSEK, TEST sonucuyla
  birlikte degerlendirilmeli (asagida).
  Final model ic-validasyon AUC=0,5510, best_iteration=2 (Hipotez1'in best_iteration=1'i ile AYNI KARAKTERDE - pratikte sig agac)

Esik Kalibrasyonu (out-of-fold, TEST'e BAKILMADI): SECILEN 0,60/0,40 (fallback GEREKMEDI - Hipotez1'in aksine burada gercek
  adaylar MIN_SAMPLE esigini rahatlikla gecti, long_n=77/short_n=743, kapsama %18,87)

Gorulmemis Veri (TEST seti, TEK KEZ, 2026-06-17->2026-07-10, n=1.370):
  TEST AUC=0,5084 (rassala yakin, Hipotez1'in 0,5170'ine YAKIN)
  p_test dagilimi: min=0,4200 max=0,5087 ortalama=0,4564 (kalibre edilen 0,60/0,40 esigine HICBIR ZAMAN ulasmiyor)
  PRIMARY (hicbiri-haric) islem sayisi = 0 -> PF/WR/DD tanimsiz
  SUPPLEMENTARY (hicbiri-dahil, canliya-yakin) islem sayisi = 0 -> PF/WR/DD tanimsiz
  HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 -> HICBIRI OLCULEMEDI (n=0)
  KARAR: RED (olcum yoksa hedefin karsilandigi iddia edilemez, S2 Madde4 + Ortak Ilkeler)

Dikkat noktalari:
  - S1 (pencereye ozel, OPSIYONEL): medyan 36,89x / P90 28,93x / tick-seviyesi-teyit 27,60x - UCU DE esigi (15,0x) rahatlikla
    GECTI. Bu pencerede 0-islem sonucu MALIYET DUVARINDAN DEGIL, modelin olasilik-dagiliminin esige ulasamamasindan kaynaklanir.
  - ONEMLI GOZLEM (feature-onem): Arastirmaci'nin BULGU 7'de "guclu ama kirilgan" isaretledigi tick_imbalance_ratio bu pencerede
    modele SIFIR (0) agirlik kazandirdi - model bu feature'i pratik olarak HIC KULLANMADI. tick_avg_spread_pts/tick_mid_ret_std
    sadece marjinal (2/1) agirlik aldi. Buna karsilik Grup B (pivot/rolling-S-R) feature'lari bu pencerede EN YUKSEK agirliklari
    aldi (dist_daily_pivot_pts=10, dist_roll20_low_pts=8) - Hipotez1'in tam-tarihsel paterninden (o zaman atr14_h1_aligned=10
    en yuksekti, Grup B dusuktu) FARKLI - DOGRUDAN KARSILASTIRILAMAZ ama kayda-deger, Arastirmaci'nin kendi BULGU 7 uyarisiyla
    (medyan-fark outlier-kaynakli olabilir) TUTARLI.
  - Nedensellik/ileri-bakis (Grup D): BAGIMSIZ 3 kontrolle (bucket-sinir 200-ornek, bar-bucket-birim, son-tick<bar-bitis) GECTI,
    hicbir ihlal yok - Arastirmaci'nin kendi iddiasina DAYANILMADI (Stratejist'in ozel talebi karsilandi).
  - OLCEKLENEBILIRLIK DURUMU COZULMEDI (ONEMLI): bu hipotez BASARILI cikSa bile (bu turde CIKMADI) Grup D'nin 4,2 yillik tam
    veriye tasinma yontemi (~400+ milyon tick tahmini) bu raporla COZULMEZ, ayri bir tasarim/muhendislik sorusu olarak ACIK.
  - Walk-forward std (0,0530) Hipotez1'inkinden (0,0122) belirgin YUKSEK - kucuk-orneklem varyansi ihtimali, TEK BASINA
    "sinyal var" seklinde YORUMLANMAMALI (TEST AUC 0,5084 ile birlikte okunmali).
  - OVERFITTING_RISKI: walk-forward ort (0,5441) ile TEST (0,5084) arasinda orta duzey bir fark var (0,036) - Hipotez1'deki
    (0,5075 vs 0,5170, fark ~0,01) FARKI biraz daha genis; kucuk-n kaynakli walk-forward varyansiyla TUTARLI olabilir, KESIN
    egitimde-iyi/testte-kotu (klasik overfitting) deseni olarak ISARETLENMEDI ama BU pencerede izlenmeye deger bir gozlem.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez3_20260712.md
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v2_hipotez3_output.json
Script: C:\MilaYatirim\Justin\backtest_ml_v2_hipotez3.py
```

---

## 10) IZOLASYON NOTU

- Bu script ve bu rapor, MilaGold/Lisa/Signal GPT'ye ait HICBIR dosyayi/parametreyi/format-
  sablonunu ACMADI veya REFERANS ALMADI. Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi.
- Veri dogrudan MT5'ten (MetaTrader5 kutuphanesi): GOLD sembolu M15 OHLCV+tick_volume+spread
  (`copy_rates_from_pos`) + tick bid/ask verisi (`copy_ticks_range`, SADECE pilot pencere icin).
- Script, Hipotez1'in script'inden (`backtest_ml_v2_hipotez1.py`) yapi/kutuphane-kullanimi
  REFERANSI olarak turetildi (kopyalama degil, Grup 1-5/B fonksiyonlari birebir yeniden kullanildi
  cunku bu Justin'in KENDI onceki turudur) — bu, izolasyon kapsami DISINDADIR (izolasyon kurali
  MilaGold/Lisa/Signal GPT'ye ait dosyalar icin gecerlidir).
- Grup D (Arastirmaci BULGU 7-9'un kavramsal tanimi) kodu SIFIRDAN, Arastirmaci'nin kendi
  script'ine (varsa) BAKILMADAN yazildi; nedensellik dogrulamasi da BAGIMSIZ yapildi (Bolum 3).

---

## 11) GEÇICI DOSYA TEMIZLIGI NOTU

Bu tur icin gecici/patch dosyasi olusturulmadi. `backtest_ml_v2_hipotez3.py` tek calistirmada
(EXIT_CODE=0, hicbir hata, tum assert kontrolleri GECTI) bastan sona tamamlandi.

---

## 12) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (script calistirma +
raporlama), canli sisteme dokunus YOK, Justin demo/arastirma asamasindadir (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam (hicbir kalici/geri-donulmez islem
yapilmadi), mali etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru).
→ **STOP-genis/bilgi-notu kategorisi, Ertan onayi GEREKMEZ.** Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.

**Governance (S3, bilgi amacli, tekrar):** Bu hipotezin RED sonucu, Stratejist'in acikca belirttigi
gibi Tur 2'nin nihai KABUL/RED kararinin (S3 sayacini etkileyen karar) dayanagi DEGILDIR — o karar
Hipotez 1/2'nin sonuclarina gore verilecektir (bkz. ilgili raporlar).
