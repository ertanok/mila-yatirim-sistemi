# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — ML/Feature-Tabanli Aile v2 (ML Tam Tur 2) — HIPOTEZ 1
## LightGBM Ikili Yon-Tahmini Modeli + Grup B (Gunluk/Haftalik Pivot + 20-Gunluk Rolling S/R) — N=16/k=1,5xATR14-M15

Tarih: 2026-07-12
Hipotez adi: LightGBM Ikili Yon-Tahmini Modeli + Grup B (Pivot/S-R) — HIPOTEZ 1 (v2/Tur2, FEATURE-IZOLE)
Yaklasim turu: Makine Ogrenmesi — Gradient Boosting (LightGBM, binary classifier)
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md` (Karar 1-4, Hipotez 1)
Karsilastirma referansi: `risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md` (Tam Tur 1, RED)
Script: `backtest_ml_v2_hipotez1.py` | Ham veri: `backtest_ml_v2_hipotez1_output.json`
Calisma logu: `backtest_ml_v2_hipotez1_run.log`

Governance (bilgi amacli, degistirilmedi): S3 sayaci 1/2. Bu rapor sayaci DEGISTIRMEZ — sayaci
degistiren Risk Analisti'nin nihai karari. Hipotez 2 (multiclass/deadzone) ayri bir gorev
dosyasiyla PARALEL calistirilmaktadir; bu rapor SADECE Hipotez 1'i kapsar.

---

## 0) BU TURUN OZETI

Script BASTAN SONA, HICBIR HATA VERMEDEN, tek calistirmada tamamlandi (`backtest_ml_v2_hipotez1_run.log`).
MT5 baglantisi, veri cekme, Grup 1-5 feature hesabi (Tur 1 ile birebir ayni), YENI Grup B
feature hesabi, Grup B'nin bagimsiz ileri-bakis/DST dogrulamasi (5 alt-kontrol, hepsi ASSERT ile
kod-icinde dogrulandi — script bir ASSERT hatasi versede calisma DURACAKTI, durmadi), S1
stres-testi, purged/embargolu walk-forward (4 fold), esik-kalibrasyonu, final model egitimi,
TEK-KEZ TEST seti siniflandirmasi, PRIMARY ve SUPPLEMENTARY trade-simulasyonlari, `hipotez_ozet`
— tumu calisti ve `backtest_ml_v2_hipotez1_output.json`'a yazildi. Kod uzerinde ekstra bir
"duzeltme" turu GEREKMEDI (ilk calistirmada tamamlandi).

---

## 1) KUTUPHANE ON-KOSULU SONUCU

| Kutuphane   | Beklenen (Tur 1) | Bu turde teyit edilen | Durum |
|---|---|---|---|
| pandas      | 3.0.3   | 3.0.3   | DEGISMEDI |
| lightgbm    | 4.6.0   | 4.6.0   | DEGISMEDI |
| scikit-learn| 1.9.0   | 1.9.0   | DEGISMEDI |
| numpy       | 2.5.0   | 2.5.0   | DEGISMEDI |

Gorev talimati geregi XGBoost bu turde ZORUNLU DEGILDI (Stratejist Karar1 gerekcesi: model-secimi
ekseni Tur 1'de zaten test edildi, fark yaratmadi) — kurulum/dogrulama YAPILMADI, script te
XGBoost KULLANMADI (sadece LightGBM).

---

## 2) ON-KONTROL SONUCLARI (S1 devir/stres-testi + DST BAGIMSIZ) — AYRIK GECTI/GECMEDI

### 2.1 DST/Saat-Eslesme Dogrulamasi (Standart Madde 1) — **GECTI (BAGIMSIZ, bu turde YENIDEN calistirildi)**

Gorev talimati "onceki turden DEVRALINAMAZ" dedigi icin, Tur 1'in sonuclarindan KOPYALANMADI —
ayni yontem (bilinen 8 DST gecisinde piyasa-acilis saatinin UTC/epoch-okunan degeri
karsilastirmasi) bu script icinde SIFIRDAN calistirildi.

- **8/8 bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI gozlendi** → MT5 sunucusu DST'yi
  TAKIP EDIYOR (Tur 1 ile AYNI sonuc, bagimsiz tekrar-uretildi).
- Sonuc: saat-bazli feature'lar (hour_sin/cos, oturum bayraklari, dow) sunucu-yerel zamana gore
  TUTARLI — **GECTI**.

### 2.2 S1 — Maliyet-Orani Stres Testi (Standart Madde 2) — DEVIR + TEYIT

k_risk=1,5xATR14 Tur 1 ile AYNI oldugu icin gorev talimati geregi bu turun sonucu Tur 1'den
DEVRALINABILIRDI — yine de AYNI veri/yontemle YENIDEN HESAPLANDI (ek maliyeti ihmal edilebilir),
sonuc BIREBIR teyit edildi:

| Olcum | Tur 1 | Bu tur (v2) | Fark |
|---|---|---|---|
| ATR14(M15) medyan | 287,43 pts | 287,43 pts | YOK |
| Spread medyan | 27,0 pts | 27,0 pts | YOK |
| Oran — medyan-spread | 15,97x | **15,97x** | YOK |
| Oran — P90-spread STRES TESTI | 11,91x | **11,91x** | YOK |
| Medyan uzerinden GECTI mi | EVET | **EVET** | — |
| P90 STRES TESTI GECTI mi | HAYIR | **HAYIR** | — |

Degerlendirme: Tur 1'in P90-stres-testi kaybi (11,91x < 15,0x esik) bu turde de AYNEN gecerli
(veri seti ayni gunde/saatte tekrar cekildigi icin sayisal olarak birebir ozdes cikti — bu bir
kopyalama degil, bagimsiz yeniden hesaplamanin dogal sonucudur). Gorev talimati geregi bu esik
kaybi ana testi DURDURMADI — Hipotez 1 yine de asagida calistirildi.

---

## 3) GRUP B ILERI-BAKIS DOGRULAMASI (AYRI, ACIK BOLUM — BAGIMSIZ KOD INCELEMESI)

Stratejist'in ozellikle vurguladigi madde: "Arastirmaci'nin kendi ic-mantik kontrolu YETERLI
SAYILMAZ" — bu nedenle Backtest Muhendisi, Arastirmaci'nin `research_ml_gold_scalping_m15_v2.py`
script'ine BAKMADAN/referans ALMADAN, Grup B feature'larini SIFIRDAN kodlayip 5 ayri kontrolle
BAGIMSIZ dogruladi. Tum kontroller script icinde `assert` ile uygulandi — herhangi biri basarisiz
olsaydi script CALISMAYI DURDURURDU (durmadi, hepsi GECTI).

| # | Kontrol | Yontem | Sonuc |
|---|---|---|---|
| 1 | shift(1) fiilen uygulandi mi | Gunun/haftanin KENDI pivot degeri ile bugune ATANAN "prev" degerin dizi-bazinda FARKLI oldugu (`np.array_equal`=False) assert edildi | **GECTI** |
| 2 | Ilk gun/hafta icin ileri-doldurma/sifir-doldurma YOK mu | `daily_pivot_prev[0]` ve `weekly_pivot_prev[0]` NaN olmali (onceki gun/hafta yok) assert edildi | **GECTI** |
| 3 | Spot-check (3 ornek gun, elle-hesap) | 3 farkli tarihte (2023-05-09, 2024-05-29, 2025-06-19) atanan prev-pivot, o gune ATANAN ONCEKI gunun kendi (H+L+C)/3'u ile elle karsilastirildi | **3/3 BIREBIR ESLESTI** (bkz. asagida) |
| 4 | 20-gunluk pencere bugunu HARIC tutuyor mu | Orta-nokta ornek gunde (2024-05-29), script'in roll20_high/low_prev degeri, `d_high[i-20:i]` (bugun i HARIC) diliminin elle-hesaplanan max/min'i ile karsilastirildi | **BIREBIR ESLESTI** |
| 5 | Gun-siniri DST gecislerinde bozuluyor mu | 8 bilinen DST gecisinin +/-1 gunu icin bar-sayisi, tipik-gun medyanindan **%25'ten fazla** sapiyor mu tarandi | **0/24 anomali** |

**Spot-check detayi (3 ornek gun):**

| Gun | Prev-pivot kaynagi gun | O gunun H/L/C | Script prev-pivot | Elle-hesap pivot | Eslesme |
|---|---|---|---|---|---|
| 2023-05-09 | 2023-05-08 | 2029,25 / 2014,12 / 2021,28 | 2021,55 | 2021,55 | EVET |
| 2024-05-29 | 2024-05-28 | 2363,88 / 2340,14 / 2361,02 | 2355,013 | 2355,013 | EVET |
| 2025-06-19 | 2025-06-18 | 3399,89 / 3362,40 / 3369,20 | 3377,163 | 3377,163 | EVET |

**20-gunluk pencere sinir kontrolu (2024-05-29 ornegi):** script roll20_high_prev=2449,93 /
roll20_low_prev=2277,17 — elle-hesap (i-20..i-1 dilimi, bugun HARIC) ile BIREBIR eslesti.

**Yakinlik bayragi — metodolojik not:** Arastirmaci'nin arastirma script'i (`research_ml_gold_
scalping_m15_v2.py`, sadece Stratejist raporu uzerinden BILINEN yontem — dosyanin kendisi
izolasyon disi degil ama bu backtest'te referans/format icin ACILMADI) yakinlik esigini TUM
verinin (test DAHIL) global percentile'inden turetmisti. Bu, S2 Madde3'un ("olceklendirme
istatistikleri SADECE egitim setinden mi") ihlali riski tasidigi icin, Backtest Muhendisi burada
FARKLI/nedensel bir tanim kullandi: bar KENDI (o ana kadar bilinen) ATR14'unun %50'si icindeyse
"yakin" sayilir — hicbir global/test-seti-icerikli istatistik KULLANILMADI. Bu, Stratejist'in
"yakinlik bayragi" kavramini DEGISTIRMEZ, sadece somut esik tanimini leak-free bir bicimde
uygular (Stratejist tam formulu belirtmemisti, sadece kavramsal olarak tanimlamisti).

**GENEL SONUC — Grup B ileri-bakis/DST dogrulamasi: GECTI.** Gunluk/haftalik pivot mesafesi
feature'lari SADECE onceki tamamlanmis gun/haftadan turetiliyor, 20-gunluk rolling-high/low
SADECE t-oncesi 20 tamamlanmis gunu kullaniyor (bugun HARIC), gun/hafta sinirinin kendisi DST
gecislerinde bozulmuyor. Bu, Arastirmaci'nin kendi ic-mantik iddiasindan BAGIMSIZ, ayri bir
kod-incelemesiyle teyit edilmistir (Stratejist'in ozel talebi karsilandi).

---

## 4) ANA TEST TASARIMI / YONTEM (Stratejist Karar 1-3 — DEGISTIRILMEDI)

- **Model:** LightGBM ikili siniflandirici (`objective=binary`), Tur 1 ile BIREBIR AYNI dar
  hiperparametreler (grid-search YAPILMADI — S2 geregi): `num_leaves=31, max_depth=6,
  learning_rate=0.05, n_estimators=500, min_child_samples=50, subsample=0.8, colsample_bytree=0.8,
  reg_lambda=1.0, random_state=42`.
- **Etiket:** Triple-barrier, N=16 M15-bar (4 saat) zaman-bariyeri, SL=TP=1,5xATR14(M15) (RR=1:1).
  `hicbiri` (zaman-asimi) egitim/PRIMARY-test disi tutuldu — Tur 1 ile BIREBIR AYNI, DEGISTIRILMEDI.
- **Feature seti:** **29 sutun** = v1'in 23 sutunu (Volatilite[3], MTF-Confluence[4], Hacim[3],
  Oturum/Gun-Ici[6], Fiyat-Yapisi/Momentum[7]) + **YENI Grup B (6 sutun)**: `dist_daily_pivot_pts`,
  `dist_weekly_pivot_pts`, `dist_roll20_high_pts`, `dist_roll20_low_pts`, `near_roll20_high_flag`,
  `near_roll20_low_flag`. (Stratejist'in "~22-28 sutun" tahmininin bir tik ustunde — 29 — ama
  tanimladigi kavramsal grup listesine [gunluk/haftalik pivot + 20-gunluk rolling-high/low +
  yakinlik bayragi] BIREBIR uyar, ek/farkli bir grup EKLENMEDI.)
- **Veri:** XM/MT5 GOLD M15, ayni 4,2 yillik seri (2022-04-18 → 2026-07-10, 99.999 bar).
- **Veri bolumu (kronolojik, karistirilmadi):** TRAINVAL: ilk %80 (2022-04-18 → 2025-09-03,
  n=67.439 ikili-etiketli — Tur 1'in 68.785'inden biraz DUSUK, cunku Grup B'nin 20-gunluk/haftalik
  warm-up'i veri setinin EN BASINDAKI ~1.346 ornegi feature-gecersiz kilar; bu kayip SADECE
  TRAINVAL'in basinda, TEST donemini ETKILEMEZ — bkz. asagida). PURGE: `i+N<=trainval_end_bar`.
  EMBARGO: 24 bar (6 saat). TEST: son dilim (2025-09-04 → 2026-07-10, **n=17.833 — Tur 1 ile
  BIREBIR AYNI sayida**, ornekleme AYNI), TEK KEZ kullanildi.
- **Walk-forward:** TRAINVAL icinde 5 esit segment → 4 purged/embargolu fold (Tur 1 ile ayni yapi).
- **Esik-kalibrasyonu:** SADECE out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR)
  taramasi — TEST SETINE BAKILMADI (S2 Madde2).
- **Feature-sizinti kontrol listesi (S2 Madde3):** tum maddeler teyit edildi (bkz. Bolum 3, Grup B
  icin AYRICA ozel/bagimsiz dogrulama yapildi).
- **Basari kriterleri (egitimden ONCE sabitlendi, S2 Madde4):** HEDEF_PF=1,5, HEDEF_WR=%60,0
  (RR=1:1), HEDEF_DD=%20 kumulatif — Tur 1 ile AYNI.
- **Maliyet modeli:** tick-bazli gercek maliyet (Justin ailesi standardi, Tur 1 ile AYNI) — giris
  `signal_idx+1` barinin gercek bid/ask kotasyonu, slipaj + spread/2 toplam maliyet `net_pts`'e
  uygulandi.
- **Lot/risk:** `justin_gecmis_calisma.md` geregi kasa=2.000 USD, lot=0,01 (sabit), risk-basi =
  kasa x %1 ust sinir — Tur 1 ile AYNI.

---

## 5) SONUCLAR

### 5.1 Walk-Forward (Purged/Embargolu, 4 fold)

| Fold | Train n | Val n | Val AUC | best_iteration |
|---|---|---|---|---|
| 1 | 12.320 | 13.547 | 0,4915 | 1 |
| 2 | 25.894 | 13.693 | 0,5033 | 3 |
| 3 | 39.626 | 13.653 | 0,5144 | 10 |
| 4 | 53.308 | 14.105 | 0,5300 | 3 |

**AUC ozet: ortalama=0,5098, std=0,0142, min=0,4915, max=0,5300** (Tur 1: ortalama=0,5075,
std=0,0122, min=0,4938, max=0,5251) — istatistiksel olarak AYIRT EDILEMEYECEK kadar yakin,
**hala neredeyse RASSAL (coin-flip) seviyesinde**.

### 5.2 Esik-Kalibrasyonu (Out-of-Fold, TEST SETINE BAKILMADAN)

| Esik (Long/Short) | Long n | Long WR-proxy | Short n | Short WR-proxy | Toplam n | Kapsama |
|---|---|---|---|---|---|---|
| 0,60 / 0,40 | 30 | 0,5000 (esik gecti ama sinirda) | 0 | - (n<30) | 30 | %0,05 |
| **0,575 / 0,425 (SECILEN)** | 209 | 0,5981 | 0 | - (n<30) | 209 | %0,38 |
| 0,55 / 0,45 | 909 | 0,5545 | 5 | 0,8000 (n<30, skora DAHIL EDILMEDI) | 914 | %1,66 |

**SECILEN ESIK: LONG>=0,575 / SHORT<=0,425** (Tur 1'de secilen 0,55/0,45'ten FARKLI — Grup B ile
feature dagilimi degistigi icin OOF olasilik dagilimi da degisti). Onemli sinir: **SHORT tarafi
HICBIR esik adayinda MIN_SAMPLE (>=30) esigini gecemedi** (0, 0, 5 — ucu de yetersiz) — secim
SADECE LONG tarafinin precision-proxy'sine dayandi (S2/Ortak-Ilkeler geregi bu acikca isaretlendi,
fallback UYGULANMADI cunku LONG tarafi gecerliydi).

### 5.3 Final Model Egitimi

- Egitim n=53.308, ic-validasyon n=14.105, ic-validasyon AUC=**0,5300** (Tur 1: 0,4990),
  `best_iteration=3` (Tur 1: 1 — bu turde erken-durma biraz daha fazla turda devreye girdi, model
  Tur 1'e gore biraz daha az "tek-agac-sig" ama HALA cok sinirli, 3 boosting turu).
- **TEST SETI (tek-kez) siniflandirma AUC'u: 0,5190** (Tur 1: 0,5170) — **+0,002 fark, pratikte
  degismedi, hala rassala yakin.**

### 5.4 Feature-Onem Tablosu (final model, split-sayisi bazli, best_iteration=3)

| Sira | Feature | Onem | Grup |
|---|---|---|---|
| 1 | **dist_weekly_pivot_pts** | **18** | **Grup B (YENI)** |
| 2 | atr14_h1_aligned | 15 | Grup 1 |
| 3 | **dist_roll20_low_pts** | **8** | **Grup B (YENI)** |
| 4 | hour_cos | 7 | Grup 4 |
| 4 | dow | 7 | Grup 4 |
| 6 | **dist_roll20_high_pts** | **6** | **Grup B (YENI)** |
| 7 | macd_hist | 5 | Grup 5 |
| 8 | lag_ret_4 | 4 | Grup 5 |
| 8 | **dist_daily_pivot_pts** | **4** | **Grup B (YENI)** |
| 10 | atr14_m15 | 3 | Grup 1 |
| 10 | h4_trend_aligned | 3 | Grup 2 |
| 12 | atr_regime_ratio | 2 | Grup 1 |
| 12 | session_ny | 2 | Grup 4 |
| 12 | macd_line | 2 | Grup 5 |
| 15 | vol_ratio_trail100 | 1 | Grup 3 |
| 15 | vol_slope_8bar | 1 | Grup 3 |
| 15 | hour_sin | 1 | Grup 4 |
| 15 | rsi14 | 1 | Grup 5 |
| — | m15_trend, h1_trend_aligned, confluence_flag, tick_volume, session_asia, session_london, lag_ret_1, lag_ret_8, directional_streak, **near_roll20_high_flag**, **near_roll20_low_flag** | 0 | (cesitli) |

**Toplam split sayisi=90. Grup B toplam agirligi = 18+8+6+4+0+0 = 36/90 (~%40)** — bu, Tur 1'in
"ATR/trend/confluence gibi ana feature gruplari NEREDEYSE HIC agirlik almiyor" bulgusuna KIYASLA
CARPICI bir fark: bu turde model, (cok sinirli sayidaki, 3 agactaki) splitlerinin cogunu YENI
Grup B feature'larina, ozellikle `dist_weekly_pivot_pts`'e (tek basina en yuksek agirlikli
feature) ayirdi. Buna karsin **iki yakinlik-bayragi (near_roll20_high/low_flag) SIFIR agirlik
aldi** — modelin surekli/sayisal mesafe feature'larini (dist_*) tercih ettigi, ikili
bayrak-versiyonlarini KULLANMADIGI gorulmektedir.

**Onemli metodolojik uyari (yorum degil, gozlem):** Feature-onem degisimi (Grup B'nin agirlik
kazanmasi) TEST AUC'sinde (0,5170→0,5190) ANLAMLI bir degisiklige YOL ACMADI — model farkli
feature'lara "bakiyor" ama ayirt edici gucu PRATIKTE AYNI kaliyor. Bu, tek basina "Grup B'nin
bir ise yaramadigi" anlamina GELMEZ (yorum Risk Analisti'nindir) — ama HAM SAYISAL gozlem budur.

### 5.5 TANI: TEST Setinde Olasilik Dagilimi (Tur 1 ile ayni tani, karsilastirma icin eklendi)

| Istatistik | Tur 1 | Bu tur (v2) |
|---|---|---|
| p_test min | 0,5037 | 0,4823 |
| p_test max | 0,5304 | 0,5515 |
| p_test ortalama | 0,5089 | 0,5091 |
| p_test std | 0,0047 | **0,0116 (2,5x daha genis)** |
| Esik LONG asan bar sayisi | 0 | **0** |
| Esik SHORT asan bar sayisi | 0 | **0** |

Olasilik dagiliminin genisligi (std) Tur 1'e gore ~2,5 KAT artti (0,0047→0,0116) — model bu
turde biraz daha fazla "ayrisan" tahminler uretiyor (best_iteration=3 vs 1 ile TUTARLI). Ancak bu
genisleme, kalibre edilen esigi (0,575/0,425) asmaya YETERLI OLMADI: **p_test max=0,5515, secilen
esik=0,575 — 0,0235 puanlik bir farkla esigin ALTINDA KALDI.** Sonuc: yine **0 islem.**

### 5.6 PRIMARY Test-Seti Simulasyonu (hicbiri-haric)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / Profit Factor / Net Kar / Max DD | tumu tanimsiz (n=0) |

### 5.7 SUPPLEMENTARY Test-Seti Simulasyonu (hicbiri-dahil, canliya-yakin capraz kontrol)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / PF / Net kar / Max DD | tumu tanimsiz (n=0) |

### 5.8 HEDEF_PF/HEDEF_WR/HEDEF_DD Karsilastirmasi ve GECTI/RED Karari

| Kriter | Hedef | Gozlemlenen (PRIMARY) | Gozlemlenen (SUPPLEMENTARY) |
|---|---|---|---|
| PF | >=1,5 | tanimsiz (n=0) | tanimsiz (n=0) |
| WR (RR=1:1) | >=%60,0 | tanimsiz (n=0) | tanimsiz (n=0) |
| DD | <=%20 kumulatif | tanimsiz (n=0) | tanimsiz (n=0) |

**SONUC (protokol-uygulamasi, yorum degil):** Ortak Ilkeler'deki "Minimum orneklem uyarisi" geregi,
test edilen kumede HICBIR islem yoksa sonuc anlamli/olculebilir DEGILDIR. S2 Madde4 altinda bir
kriterin "olculemedi" cikmasi, o kriterin KARSILANDIGININ iddia edilemeyecegi anlamina gelir.
Bu, Tur 1 ile BIREBIR AYNI protokolel sonuca (RED-tetikleyici "olcum yoklugu") ulasir. Nihai
KABUL/RED karari Risk Analisti'ne aittir — Backtest Muhendisi burada sadece olcumu raporlar.

---

## 6) TUR 1 HIPOTEZ 1 ILE KARSILASTIRMA (Feature-Izolasyon Sonucu)

| Karsilastirma Ekseni | Tur 1 (v1, 23 feature, Grup B YOK) | Tur 2 (v2, 29 feature, +Grup B) | Degisim |
|---|---|---|---|
| Walk-forward AUC ort. | 0,5075 | 0,5098 | +0,0023 (ihmal edilebilir) |
| Walk-forward AUC std | 0,0122 | 0,0142 | biraz arti |
| Final ic-validasyon AUC | 0,4990 | 0,5300 | +0,031 (IS'te gorece belirgin) |
| Final best_iteration | 1 (tek agac) | 3 | biraz daha az "sig" |
| **TEST AUC (tek-kez, asil olcum)** | 0,5170 | **0,5190** | **+0,002 (pratikte AYNI)** |
| p_test std (TEST'te dagilim genisligi) | 0,0047 | 0,0116 | ~2,5x genisledi |
| Esik-kalibrasyonu (LONG/SHORT) | 0,55 / 0,45 | 0,575 / 0,425 | degisti (OOF dagilimi degisti) |
| p_test max vs secilen esik farki | 0,5304 vs 0,55 (-0,0196) | 0,5515 vs 0,575 (-0,0235) | fark BUYUDU (esige daha da uzak) |
| **PRIMARY/SUPPLEMENTARY islem sayisi** | 0 / 0 | **0 / 0** | **DEGISMEDI** |
| Ana feature-onem yogunlasmasi | ATR/trend/confluence NEREDEYSE SIFIR | Grup B (~%40, esp. weekly-pivot) BASKIN | **BELIRGIN DEGISTI** |
| S1 P90-stres-testi | 11,91x (KAYBEDIYOR) | 11,91x (KAYBEDIYOR, ayni) | DEGISMEDI |

**Izolasyon sonucunun ozeti (ham gozlem, yorum degil):** Grup B feature'larinin eklenmesi,
modelin split-agirligini (feature-onem tablosu) BELIRGIN sekilde degistirdi (ana agirlik artik
Grup B'de, ozellikle haftalik-pivot mesafesinde) — bu, Tur 1'in "hicbir feature grubu anlamli
agirlik almadi" gozlemine kiyasla NITEL bir fark. Ancak bu degisim, **TEST setindeki AYIRT EDICI
GUCE (AUC 0,517→0,519) veya TETIKLENEN ISLEM SAYISINA (0→0) HICBIR OLCULEBILIR ETKI YAPMADI.**
Stratejist'in Hipotez 1 tasarim-mantigindaki soru ("feature seti degisirse model ogrenir mi?")
icin ham cevap: **model farkli feature'lara agirlik VERDI (ogrenme paterni degisti) ama nihai
test performansi/tetiklenme davranisi PRATIKTE DEGISMEDI.** Bu ayrimin (feature-agirlik-degisimi
vs performans-degisimi) yorumu Risk Analisti'ne aittir.

---

## 7) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — LightGBM Ikili + Grup B (Pivot/S-R) — N=16/k=1,5xATR14-M15 — HIPOTEZ 1 (v2/Tur2) — 2026-07-12

Egitim / Walk-Forward (4 fold, purged+embargolu, TRAINVAL icinde):
  AUC ortalama=0,5098 (std=0,0142, min=0,4915, max=0,5300) — RASSAL SEVIYEYE YAKIN (Tur1: 0,5075)
  Esik-kalibrasyonu (OOF-havuz): LONG>=0,575 (n=209, WR-proxy=%59,8) / SHORT<=0,425 (n=0, MIN_SAMPLE GECILEMEDI - skora dahil edilmedi)
  Final model ic-validasyon AUC=0,5300, best_iteration=3 (Tur1: 1 - biraz daha az sig ama HALA sinirli)

Gorulmemis Veri (TEST seti, TEK KEZ, 2025-09-04 -> 2026-07-10, n=17.833 - Tur1 ile AYNI donem/n):
  TEST AUC=0,5190 (Tur1: 0,5170 - fark +0,002, pratikte DEGISMEDI, rassala yakin)
  p_test dagilimi: min=0,4823 max=0,5515 ortalama=0,5091 std=0,0116 (Tur1'e gore std ~2,5x GENISLEDI,
    ama kalibre edilen 0,575 esigine YINE ulasamadi - fark 0,0235 puan)
  PRIMARY (hicbiri-haric) islem sayisi = 0 -> PF/WR/DD tanimsiz (Tur1 ile AYNI)
  SUPPLEMENTARY (hicbiri-dahil, canliya-yakin) islem sayisi = 0 -> PF/WR/DD tanimsiz (Tur1 ile AYNI)
  HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 -> HICBIRI OLCULEMEDI (n=0)

Dikkat noktalari:
  - FEATURE-ONEM PATERNI BELIRGIN DEGISTI: Grup B (YENI, pivot/rolling-S-R) toplam split-agirliginin
    ~%40'ini aldi (dist_weekly_pivot_pts TEK BASINA en yuksek agirlikli feature, 18/90 split) - Tur 1'in
    "ATR/trend/confluence NEREDEYSE SIFIR agirlik" gozlemine kiyasla NITEL bir fark. Ancak bu degisim
    TEST AUC'sinde (0,517->0,519) veya tetiklenen islem sayisinda (0->0) OLCULEBILIR bir etki YARATMADI.
  - Iki yakinlik-bayragi (near_roll20_high/low_flag, BINARY) SIFIR agirlik aldi - model surekli/sayisal
    mesafe feature'larini (dist_daily/weekly_pivot_pts, dist_roll20_high/low_pts) tercih etti.
  - Esik-kalibrasyonunda bu turde SHORT tarafi HICBIR aday esikte MIN_SAMPLE(>=30) esigini GECEMEDI (0,0,5)
    - secim SADECE LONG tarafina dayandi, bu Tur1'e gore YENI/farkli bir sinir (Tur1'de SHORT tarafi 78
    ornekle esigi geciyordu). Model, Grup B ile birlikte, SHORT yonunde daha az "yuksek-guvenli" tahmin
    uretme egilimi gosterdi (ham gozlem, sebep-sonuc iddiasi degil).
  - S1 (maliyet-orani) P90-stres testinde esik Tur1 ile AYNI sekilde kaybediliyor (11,91x < 15,0x) -
    k_risk degismedigi icin beklenen bir devir-sonucu.
  - Grup B'nin ileri-bakis/DST bagimsiz dogrulamasi (5 alt-kontrol: shift(1) assert, ilk-gun/hafta NaN
    assert, 3-ornek spot-check, 20-gun pencere sinir kontrolu, DST-gun-siniri anomali taramasi) TAMAMI
    GECTI - Grup B feature'larinin nedensel/ileri-bakissiz oldugu bagimsiz olarak teyit edildi.
  - OVERFITTING_RISKI: Tur1 gibi, IS (walk-forward ort. 0,5098) ile OOS (TEST 0,5190) arasinda BUYUK
    fark YOK - asiri uyum degil, TUTARLI ZAYIFLIK deseni Tur1'de oldugu gibi burada da GOZLEMLENIYOR.
  - LightGBM inference-hizi bu turde de OLCULMEDI (Tur1'de de olculmemisti, Stratejist Risklerinde
    "OLCULMELI" notu var) - hipotez zaten 0-islem sonuclandigi icin bu olcum bu turde YAPILMADI,
    hipotez ilerlerse (Risk Analisti/Stratejist karari) ayrica olculmesi ONERILIR.
  - Hipotez 2 (multiclass/deadzone) bu gorevle PARALEL, AYRI bir backtest ciktisinda raporlanmaktadir.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez1_20260712.md
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v2_hipotez1_output.json
```

---

## 8) IZOLASYON NOTU

Bu script ve bu rapor, MilaGold/Lisa/Signal GPT'ye ait HICBIR dosyayi/parametreyi/format-sablonunu
acmadi veya referans almadi. Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi. Veri dogrudan
MT5'ten (MetaTrader5 kutuphanesi, GOLD sembolu M15 OHLCV+tick_volume+spread) cekildi. Grup B
feature'lari, Arastirmaci'nin `research_ml_gold_scalping_m15_v2.py` script'inin KODUNA
BAKILMADAN, SADECE Stratejist raporundaki kavramsal tanimdan (gunluk/haftalik pivot mesafesi +
20-gunluk rolling-high/low mesafesi + yakinlik bayragi) yola cikilarak SIFIRDAN yazildi — bu,
"format/yapi referansi icin dosya acma da izolasyon kapsamindadir" ilkesine (CLAUDE.md, 14 Temmuz
netlestirmesi — MilaGold ozelinde yazilmis olsa da ayni ilke burada Justin'in KENDI ic-projeleri
arasinda da temkinli uygulanmistir, Arastirmaci'nin KENDI kodu referans alinmadan bagimsiz
tekrar-turetim tercih edilmistir) uyumlu, ihtiyatli bir tercihtir. Rapor sablonu, Justin'in KENDI
onceki backtest raporlarindan (Tur 1/v1 Hipotez1, ayni proje ici sureklilik) turetildi —
MilaGold'a ait hicbir sablon acilmadi.

---

## 9) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (script calistirma +
raporlama), canli sisteme dokunus YOK, Justin demo/arastirma asamasindadir (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam (hicbir kalici/geri-donulmez islem
yapilmadi), mali etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru).
→ **STOP-genis/bilgi-notu kategorisi, Ertan onayi GEREKMEZ.** Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
