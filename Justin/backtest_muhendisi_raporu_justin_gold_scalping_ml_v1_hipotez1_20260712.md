# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — ML/Feature-Tabanli Aile v1 — HIPOTEZ 1
## LightGBM Ikili Yon-Tahmini Modeli (N=16 M15-bar / k=1,5xATR14-M15)

Tarih: 2026-07-12 (2. TUR — tamamlama turu)
Hipotez adi: LightGBM Ikili Yon-Tahmini Modeli (N=16/k=1,5xATR14-M15) — HIPOTEZ 1
Yaklasim turu: Makine Ogrenmesi — Gradient Boosting (LightGBM, binary classifier)
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md` (Karar 1-4)
Script: `backtest_ml_v1_hipotez1.py` | Ham veri: `backtest_ml_v1_hipotez1_output.json`
Calisma loglari (kanit/tekrar-uretilebilirlik icin): `backtest_ml_v1_hipotez1_run_tur2.log`,
`backtest_ml_v1_hipotez1_run_tur2_diag.log`

---

## 0) BU TURUN OZETI (dongu notu)

**1. Tur nasil sonuclanmisti:** `backtest_muhendisi_20260712_1640` gorev-durum dosyasi
`"durum": "hata"` ve `"rapor_yolu": "C:\MilaYatirim\Justin\_patch2.py"` iceriyordu. Bu tur
baslamadan once diskte `_patch*.py` uzantili HICBIR dosya bulunmadigi dogrulandi (`find`
taramasi, sonuc: bos). Yani 1. tur, script'te gercek bir hata bulup onu "patch" dosyalariyla
duzeltmeye calisirken degil, muhtemelen (a) test-seti simulasyon asamasinin ne kadar surecegini
yanlis tahmin edip erken bir zaman-asimiyla kesintiye ugrayarak, veya (b) bu kesintiyi bir kod
hatasi sanip gereksiz patch denemelerine girisip turn/zaman tuketerek sonuclanmis olmali — ama
patch dosyalari kalici olarak diskte kalmadigina gore bu denemeler ya hic tamamlanmadan silindi
ya da hic diske yazilamadan surec kesildi. **Kesin kok-neden dogrulanamadi** (1. turun kendi
loglari elde degil), ancak asagidaki 2. tur bulgusu (`Madde 2`) bu ihtimali buyuk olcude
destekliyor.

**2. Bu turda yapilan dogrulama:** `backtest_ml_v1_hipotez1.py` degistirilmeden (SIFIRDAN
YAZILMADAN) `py backtest_ml_v1_hipotez1.py` ile calistirildi (timeout: 480.000 ms — cömert
pay). **Script BASTAN SONA, HICBIR HATA VERMEDEN, EXIT_CODE=0 ile tamamlandi.** MT5 baglantisi
(`mt5.initialize()`), veri cekme, feature/etiket hesaplama, DST dogrulamasi, S1 stres testi,
walk-forward, esik-kalibrasyonu, final model egitimi, TEST SETI siniflandirma AUC'u, PRIMARY ve
SUPPLEMENTARY test-islem simulasyon bloklari ve `hipotez_ozet` — TUMU calisti ve
`backtest_ml_v1_hipotez1_output.json`'a yazildi. **Script'te herhangi bir calisma-zamani hatasi
TESPIT EDILEMEDI** — bu yuzden kod uzerinde hicbir "duzeltme" yapilmadi (parametre/mantik
degisikligi YOK).

**3. Beklenmedik ama gecerli sonuc — 0 islem:** Script hatasiz calismasina ragmen hem PRIMARY
(hicbiri-haric) hem de SUPPLEMENTARY (hicbiri-dahil) test-seti simulasyonlarinda **0 (sifir)
islem tetiklendi**. Bunun bir veri/kod hatasi mi yoksa gercek bir model bulgusu mu oldugunu
ayirt etmek icin, script'e **sadece raporlama amacli, parametre/esik/yontem DEGISTIRMEYEN** kucuk
bir tani blogu eklendi (`test_p_dagilimi_TANI` — final modelin TEST setindeki p(yukari) olasilik
tahminlerinin min/max/ortalama/std/persentil dagilimini kaydeder) ve script **2. kez** calistirildi
(`backtest_ml_v1_hipotez1_run_tur2_diag.log`). Iki calistirma da BIREBIR AYNI walk-forward AUC'leri
(0,4938/0,5122/0,5251/0,4990), ayni final model ic-validasyon AUC'u (0,499034...) ve ayni TEST AUC'u
(0,516990...) uretti — **deterministik ve tekrar-uretilebilir**. Tani sonucu: TEST setinde
`p_test` **min=0,5037, max=0,5304, ortalama=0,5089, std=0,0047** — yani model olasiliklari
[0,45; 0,55] kalibre-edilmis karar bandinin DISINA hicbir zaman cikmiyor (en yuksek deger bile
0,5304, esik 0,55'in altinda). **0 islem, bir kod hatasi degil, modelin gercek/dogrulanmis bir
davranisidir**: final model, walk-forward'daki en dusuk-iterasyonlu fold'larla (fold 1 ve 4,
`best_iteration=1`) ayni sekilde SADECE 1 boosting turunda erken durmus (`best_iteration=1`,
final_model_egitimi bolumu), bu da olasilik ciktisinin cok dar bir bantta sikismasina yol acmis.
Esik-kalibrasyonu adimi ise 4 FARKLI fold modelinin (best_iteration 1/6/4/1, dolayisiyla farkli
olasilik-yayilimi) HAVUZLANMIS out-of-fold tahminleri uzerinden yapildigi icin, o havuzda
0,55/0,45 esigini asan ~210 ornek bulunabilmisti (bkz. `esik_kalibrasyonu.aday_tablosu`) — ama TEK
BIR final model (best_iteration=1, en dar yayilimli fold'larla ayni karakterde) bu esigi TEST
doneminde hic asmiyor. Bu, esik-kalibrasyonunun (OOF-havuz) ile canlida kullanilacak final modelin
(tek model) olasilik-yayilimi arasindaki bir TUTARSIZLIK/SINIRDIR — Stratejist'in tasarimina ait bir
sinirdir, Backtest Muhendisi'nin bunu duzeltme/esik degistirme yetkisi YOKTUR (Ortak Ilkeler:
"Parametreleri/mimariyi degistirme").

**4. Bu tur icin sonuc:** Nihai rapor URETILDI (bu dosya), 3. bir tur GEREKMEDI.

---

## 1) KUTUPHANE ON-KOSULU SONUCU

(1. turda kurulmustu, bu turda dogrulama amaciyla tekrar kontrol edildi — kurulum tekrarlanmadi.)

| Kutuphane   | Surum   | Durum |
|---|---|---|
| pandas      | 3.0.3   | Kurulu |
| lightgbm    | 4.6.0   | Kurulu |
| xgboost     | 3.3.0   | Kurulu |
| scikit-learn| 1.9.0   | Kurulu |
| numpy       | 2.5.0   | Kurulu |

Bilgi notu: Kurulum, calisma ortaminda (izole, geri-donulebilir) 1. turda yapilmisti; bu turda
sadece dogrulandi, yeniden kurulum GEREKMEDI.

---

## 2) ON-KONTROL SONUCLARI (S1 stres-testi + DST) — AYRIK, GECTI/GECMEDI

### 2.1 DST/Saat-Eslesme Dogrulamasi (Standart Madde 1) — **GECTI**

- Yontem: bu ML/M15 pipeline'i icin BAGIMSIZ olarak yeniden yazildi (H1/H2/H3'ten devralinmadi).
- 8/8 bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI gozlendi → MT5 sunucusu DST'yi TAKIP
  EDIYOR (sabit GMT+3 degil).
- Sonuc: saat-bazli feature'lar (hour_sin/cos, session_asia/london/ny, dow) sunucu-yerel zamana
  gore TUTARLI — **GECTI**.

### 2.2 S1 — Maliyet-Orani Stres Testi (Standart Madde 2)

| Olcum | Deger |
|---|---|
| ATR14(M15) medyan | 287,43 pts |
| ATR14(M15) P90 | 936,79 pts |
| Spread medyan | 27,0 pts |
| Spread P90 | 36,2 pts |
| Spread max | 137,0 pts |
| Hedef (k=1,5 x ATR medyan) | 431,14 pts |
| **Oran — medyan-spread uzerinden** | **15,97x** |
| **Oran — P90-spread STRES TESTI** | **11,91x** |
| Oran — max-spread (ekstrem) | 3,15x |
| Esik alt sinir | 15,0x |
| **Medyan uzerinden GECTI mi** | **EVET** |
| **P90 STRES TESTI GECTI mi** | **HAYIR** |

Degerlendirme: Stratejist'in medyan-spread on-tahmini (15,97x, esigin ALT SINIRINDA) burada
dogrulandi. **P90-spread stres testinde esik KAYBEDILIYOR** (11,91x < 15,0x esik). Gorev talimati
geregi bu esik kaybi ana testi DURDURMADI — Hipotez 1 asagida yine de calistirildi. Bu bulgu,
Hipotez 1 RED cikarsa Hipotez 3/k=2,0 varyantinin bir sonraki tur icin degerlendirilmesi
gerektigine isaret ediyor (bu tur kapsaminda degil).

---

## 3) ANA TEST TASARIMI / YONTEM (Stratejist Karar 1-3, degistirilmedi)

- **Model:** LightGBM ikili siniflandirici (`objective=binary`), sabit/dar hiperparametreler
  (grid-search YAPILMADI — S2 geregi): `num_leaves=31, max_depth=6, learning_rate=0.05,
  n_estimators=500, min_child_samples=50, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
  random_state=42`.
- **Etiket:** Triple-barrier, N=16 M15-bar (4 saat) zaman-bariyeri, SL=TP=1,5xATR14(M15) (RR=1:1).
  `hicbiri` (zaman-asimi) egitim/PRIMARY-test disi tutuldu (Karar 2).
- **Feature seti:** 23 sutun (5 grup: Volatilite[3], MTF-Confluence[4], Hacim[3],
  Oturum/Gun-Ici[6], Fiyat-Yapisi/Momentum[7]) — Stratejist Karar 3'teki ZORUNLU gruplarla birebir.
- **Veri bolumu (kronolojik, karistirilmadi):** toplam 99.999 M15 bar (2022-04-18 → 2026-07-10).
  TRAINVAL: ilk %80 (2022-04-18 → 2025-09-03, n=68.785 ikili-etiketli). PURGE: trainval ornekleri
  `i+N<=trainval_end_bar` ile sinirlandi. EMBARGO: 24 bar (6 saat). TEST: son dilim (2025-09-04 →
  2026-07-10, n=17.833 ikili-etiketli), **TEK KEZ** kullanildi.
- **Walk-forward:** TRAINVAL icinde 5 esit segment → 4 purged/embargolu fold (S2 Madde1).
- **Esik-kalibrasyonu:** SADECE out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR)
  taramasi — TEST SETINE BAKILMADI (S2 Madde2).
- **Feature-sizinti kontrol listesi (S2 Madde3):** tum maddeler teyit edildi (ileri-bakan bilgi
  yok, normalizasyon sadece egitim setinden, MACD HAM DEGER kullanildi — isaret degil).
- **Basari kriterleri (egitimden ONCE sabitlendi, S2 Madde4):** HEDEF_PF=1,5, HEDEF_WR=%60,0
  (RR=1:1 icin, `justin_gecmis_calisma.md`), HEDEF_DD=%20 kumulatif.
- **Maliyet modeli:** tick-bazli gercek maliyet (Justin ailesi standardi) — giris `signal_idx+1`
  barinin gercek bid/ask kotasyonu, slipaj + spread/2 toplam maliyet olarak `net_pts`'e uygulandi.
- **Lot/risk:** `justin_gecmis_calisma.md` geregi kasa=2.000 USD, lot=0,01 (sabit, bu kasa
  diliminde), risk-basi = kasa x %1 ust sinir.

---

## 4) SONUCLAR

### 4.1 Walk-Forward (Purged/Embargolu, 4 fold) — Model Ayirt Edicilik Onbulgusu

| Fold | Train n | Val n | Val AUC | best_iteration |
|---|---|---|---|---|
| 1 | 13.666 | 13.547 | 0,4938 | 1 |
| 2 | 27.240 | 13.693 | 0,5122 | 6 |
| 3 | 40.972 | 13.653 | 0,5251 | 4 |
| 4 | 54.654 | 14.105 | 0,4990 | 1 |

**AUC ozet: ortalama=0,5075, std=0,0122, min=0,4938, max=0,5251.**

> Bu sonuc **neredeyse RASSAL (coin-flip) seviyesindedir** (AUC=0,50 tam rassal ayirt-edicilik-
> sizligi temsil eder). Bu, Hipotez 1'in nihai testte HEDEF_PF=1,5'i karsilamasinin ZOR olacagina
> dair erken bir isarettir — **ancak bu tek basina RED KARARI ICIN YETERLI SAYILMADI**; S2
> protokolu geregi nihai karar test-seti simulasyonu tamamlandiktan sonra verilmistir (asagida).

### 4.2 Esik-Kalibrasyonu (Out-of-Fold, TEST SETINE BAKILMADAN)

| Esik (Long/Short) | Long n | Long WR-proxy | Short n | Short WR-proxy | Toplam n | Kapsama |
|---|---|---|---|---|---|---|
| 0,60 / 0,40 | 0 | - | 0 | - | 0 | %0,0 |
| 0,575 / 0,425 | 9 | 0,8889 (yetersiz n) | 0 | - | 9 | %0,02 |
| **0,55 / 0,45 (SECILEN)** | 132 | 0,6894 | 78 | 0,5641 | 210 | %0,38 |

**SECILEN ESIK: LONG>=0,55 / SHORT<=0,45** (her iki taraf da MIN_SAMPLE>=30 esigini gecti,
fallback UYGULANMADI). Kapsama orani (%0,38, ~55.000 OOF ornekte 210 islem) zaten cok dusuk —
modelin yuksek-guven bolgesine NADIREN ulastigini ONCEDEN isaret ediyordu.

### 4.3 Final Model Egitimi

- Egitim n=54.654, ic-validasyon n=14.105, ic-validasyon AUC=**0,4990** (rassal-seviye),
  `best_iteration=1` (erken durma SADECE 1 boosting turunda devreye girdi — model, pratikte tek bir
  sig agac).
- Feature-onem tablosu, ATR/trend/confluence gibi ana feature gruplarinin NEREDEYSE HIC agirlik
  almadigini gosteriyor (ör. `atr14_m15`=0, `m15_trend`=0, `confluence_flag`=0); en yuksek
  degerler bile cok dusuk (`dow`=6, `atr14_h1_aligned`=10) — bu, modelin anlamli bir sinyal
  OGRENEMEDIGININ ayri bir gostergesidir.
- **TEST SETI (tek-kez) siniflandirma AUC'u: 0,5170** — yine rassala yakin.

### 4.4 TANI: TEST Setinde Olasilik Dagilimi (bu tur eklendi, esik/karar DEGISTIRMEDI)

| Istatistik | Deger |
|---|---|
| p_test min | 0,5037 |
| p_test max | 0,5304 |
| p_test ortalama | 0,5089 |
| p_test std | 0,0047 |
| p95 | 0,5189 |
| p99 | 0,5252 |
| Esik LONG (>=0,55) asan bar sayisi | **0** |
| Esik SHORT (<=0,45) asan bar sayisi | **0** |

Final modelin TEST setindeki en yuksek olasiligi bile (0,5304) kalibre edilmis 0,55 esiginin
altinda kaliyor — bu yuzden **hem PRIMARY hem SUPPLEMENTARY simulasyonda 0 islem tetiklendi,
bu beklenen/dogrulanmis bir sonuctur, kod/veri hatasi DEGILDIR.**

### 4.5 PRIMARY Test-Seti Simulasyonu (hicbiri-haric, Karar-2-literal)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate | tanimsiz (n=0) |
| Profit Factor | tanimsiz (n=0) |
| Net kar (USD, 0,01 lot) | 0,0 |
| Max Drawdown | tanimsiz (n=0) |

### 4.6 SUPPLEMENTARY Test-Seti Simulasyonu (hicbiri-dahil, canliya-yakin capraz kontrol)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / PF / Net kar / Max DD | tumu tanimsiz (n=0) |

### 4.7 HEDEF_PF/HEDEF_WR/HEDEF_DD Karsilastirmasi ve GECTI/RED Karari

| Kriter | Hedef | Gozlemlenen (PRIMARY) | Gozlemlenen (SUPPLEMENTARY) |
|---|---|---|---|
| PF | >=1,5 | tanimsiz (n=0) | tanimsiz (n=0) |
| WR (RR=1:1) | >=%60,0 | tanimsiz (n=0) | tanimsiz (n=0) |
| DD | <=%20 kumulatif | tanimsiz (n=0) | tanimsiz (n=0) |

**KARAR: RED.** Gerekce (yorum degil, protokol-uygulamasi): Ortak Ilkeler'deki "Minimum orneklem
uyarisi" geregi, test edilen kumede HICBIR islem yoksa sonuc anlamli/olculebilir DEGILDIR;
S2 Madde4 (basari kriterleri onceden sabit) altinda bir kriterin "olculemedi" cikmasi, o
kriterin KARSILANDIGININ iddia edilemeyecegi anlamina gelir — dolayisiyla protokol geregi
varsayilan sonuc RED'dir (fallback: "esik gecemedi" degil, "test edilecek islem hic olusmadi").
Bu, walk-forward AUC'sinin (~0,51, rassal-seviye) ve final-model TEST AUC'sinin (0,517) zaten
isaret ettigi zayifligin, test doneminde MODELIN KENDI KALIBRE ETTIGI ESIGE HIC ULASAMAMASIYLA
sonuclandigini gosteriyor.

---

## 5) HIPOTEZ 2 (XGBoost) DURUMU

**CALISTIRILMADI — ERTELENDI.** Gorev tanimi geregi Hipotez 2 (ayni feature/label/N/k,
XGBoost) ZORUNLU degildi ("sure/kaynak yetmezse sadece Hipotez 1 ile devam et"). Bu tur, 1.
turun yarim kalan Hipotez 1 tamamlama gorevine odaklandigi icin Hipotez 2 bu turda
calistirilmadi. Diskte `backtest_ml_v1_hipotez2.py` gibi bir dosya YOK. Hipotez 2'nin
calistirilip calistirilmayacagina (Hipotez 1'in RED sonucu isiginda anlamli olup olmadigina)
Stratejist/Orkestrator karar vermelidir.

---

## 6) GECICI DOSYA TEMIZLIGI NOTU

`_patch*.py` deseninde diskte HICBIR dosya bulunamadi (proje-genelinde tarama yapildi) — 1.
turdan kalma gecici bir patch dosyasi YOKTU, temizlenecek bir sey olmadi. Bu tur, tani amacli
ekstra bir alan (`test_p_dagilimi_TANI`) disinda `backtest_ml_v1_hipotez1.py` uzerinde baska
hicbir degisiklik YAPMADI (sinyal tanimlari, ATR/RR/esik degerleri, maliyet modeli, hiperparametreler
— hepsi 1. turdaki gibi degismeden kaldi).

---

## 7) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — LightGBM Ikili Yon-Tahmini (N=16/k=1,5xATR14-M15) — ML/Gradient Boosting — 2026-07-12

Egitim / Walk-Forward (4 fold, purged+embargolu, TRAINVAL icinde):
  AUC ortalama=0,5075 (std=0,0122, min=0,4938, max=0,5251) — RASSAL SEVIYEYE YAKIN
  Esik-kalibrasyonu (OOF-havuz): LONG>=0,55 (n=132, WR-proxy=%68,9) / SHORT<=0,45 (n=78, WR-proxy=%56,4)
  Final model ic-validasyon AUC=0,4990, best_iteration=1 (erken durma — pratikte tek agac)

Gorulmemis Veri (TEST seti, TEK KEZ, 2025-09-04 -> 2026-07-10, n=17.833):
  TEST AUC=0,5170 (rassala yakin)
  p_test dagilimi: min=0,5037 max=0,5304 ortalama=0,5089 (kalibre edilen 0,55/0,45 esigine HICBIR ZAMAN ulasmiyor)
  PRIMARY (hicbiri-haric) islem sayisi = 0 -> PF/WR/DD tanimsiz
  SUPPLEMENTARY (hicbiri-dahil, canliya-yakin) islem sayisi = 0 -> PF/WR/DD tanimsiz
  HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 -> HICBIRI OLCULEMEDI (n=0)
  KARAR: RED (olcum yoksa hedefin karsilandigi iddia edilemez, S2 Madde4 + Ortak Ilkeler)

Dikkat noktalari:
  - Walk-forward AUC (~0,51) ve final-model TEST AUC (0,517) tutarli sekilde rassal-seviyede - model,
    feature setiyle anlamli bir yon-tahmin sinyali OGRENEMEMIS gorunuyor (feature-onem tablosunda
    ATR/trend/confluence gibi ana gruplar neredeyse HIC agirlik almiyor).
  - Esik-kalibrasyonu 4 FARKLI fold modelinin (best_iteration 1/6/4/1) HAVUZLANMIS OOF tahminleri
    uzerinden yapildi; final model TEK BASINA en dar-yayilimli fold'larla (1/4, best_iteration=1) ayni
    karakterde - bu YONTEMSEL TUTARSIZLIK, esik-kalibrasyonunun neden OOF'ta 210 islem uretip TEST'te
    0 islem urettigini aciklayan olasi bir kok-nedendir. Bu, Stratejist'in dikkatine sunulmalidir
    (esik-kalibrasyonu SADECE final modelin kendi olasilik dagilimindan yapilsaydi sonuc farkli
    olabilirdi - ama bu bir TASARIM/YONTEM sorusu, Backtest Muhendisi'nin degistirme yetkisi DISINDA).
  - S1 (maliyet-orani) P90-stres testinde esik kaybediliyor (11,91x < 15,0x) - Hipotez 1 RED
    cikarsa bu, Hipotez 3/k=2,0 yedeginin gerekliligini pekistiren ayri bir bulgu.
  - OVERFITTING_RISKI: Ters yonde bir gozlem var - egitim (walk-forward) ve test AUC'leri birbirine
    yakin (0,5075 vs 0,5170), yani IS/OOS arasinda BUYUK fark YOK; asiri uyum degil, TUTARLI
    ZAYIFLIK (modelin hicbir donemde ayirt edici gucu olmamasi) gozlemleniyor.
  - Hipotez 2 (XGBoost) bu turda calistirilmadi, ertelendi.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1_output.json
```

---

## 8) iZOLASYON NOTU

Bu script ve bu rapor, MilaGold/Lisa/Signal GPT'ye ait HICBIR dosyayi/parametreyi/format-sablonunu
acmadi veya referans almadi. Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi. Veri dogrudan
MT5'ten (MetaTrader5 kutuphanesi, GOLD sembolu M15 OHLCV+tick_volume+spread) cekildi. Rapor
sablonu, izolasyon kapsamindaki 14 Temmuz netlestirmesine uygun olarak Justin projesinin KENDI
onceki backtest raporlarindan (H1/H2/H3, ayni proje) turetildi — MilaGold'a ait hicbir sablon
acilmadi.

---

## 9) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (script calistirma +
raporlama), canli sisteme dokunus YOK, Justin demo/arastirma asamasindadir (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam (hicbir kalici/geri-donulmez islem
yapilmadi), mali etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru).
→ **STOP-genis/bilgi-notu kategorisi, Ertan onayi GEREKMEZ.** Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
