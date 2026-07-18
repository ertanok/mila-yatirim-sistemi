# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — ML/Feature-Tabanli Aile v1 — HIPOTEZ 3
## LightGBM Ikili Yon-Tahmini Modeli — Guvenlik-Marji/Duyarlilik Varyanti (N=16 M15-bar / k=2,0xATR14-M15)

Tarih: 2026-07-12
Hipotez adi: LightGBM Ikili Yon-Tahmini Modeli (N=16/k=2,0xATR14-M15) — HIPOTEZ 3 (Hipotez 1'in
guvenlik-marji/duyarlilik varyanti)
Yaklasim turu: Makine Ogrenmesi — Gradient Boosting (LightGBM, binary classifier)
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md` (Bolum "HIPOTEZ 3"),
`risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md` (ZORUNLU duzeltme kaynagi)
Script: `backtest_ml_v1_hipotez3.py` | Ham veri: `backtest_ml_v1_hipotez3_output.json`
Karsilastirma referansi: `backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md`

---

## 0) ESIK-KALIBRASYON YONTEMi DUZELTMESi (ZORUNLU, gorev tanimi geregi ONCELIKLE aciklaniyor)

**Hipotez 1'deki sorun (Risk Analisti raporu, Kontrol [7] ve Geri Bildirim Madde 1):**
Hipotez 1'de esik-kalibrasyonu, purged/embargolu walk-forward'un 4 FARKLI fold modelinin
(best_iteration sirasiyla 1/6/4/1 — yani 4 ayri egitim, 4 ayri olasilik-yayilim karakteri)
HAVUZLANMIS out-of-fold (OOF) tahminleri uzerinden yapilmisti. Bu havuzda 0,55/0,45 esigini asan
210 aday-islem bulunmustu (132 long + 78 short). Ancak canlida/TEST'te kullanilacak TEK final
model (kendi best_iteration'i=1, en dar-yayilimli fold'larla — 1 ve 4 — ayni karakterde) bu esige
TEST doneminde HICBIR ZAMAN ulasamadi (p_test max=0,5304 < 0,55) — sonuc: OOF'ta 210 aday-islem,
final model TEST'inde 0 islem. Risk Analisti bunu acikca KIRMIZI/RED gerekcesi olarak isaretledi
ve "esik-kalibrasyonu SADECE final modelin kendi OOF tahminlerinden (ya da final modelle AYNI
egitim-boyutu/karakterdeki TEK bir fold'dan) yapilmali" duzeltmesini talep etti.

**Bu turde uygulanan duzeltme:** `backtest_ml_v1_hipotez3.py` icinde esik-kalibrasyonu ARTIK
SADECE final modelin KENDI ic-validasyon (`final_innerval_idx`) tahminlerinden yapiliyor.
Ayrintilar:
- `final_innerval_idx`, `final_train_idx`'e gore ZAMAN OLARAK SONRA gelen, purge+embargo (24 bar
  / 6 saat) ile TRAIN'den ayrilmis bir kesittir (n=12.219).
- Final model bu veriyle GRADYAN GUNCELLEMESI yapmadi — sadece `lgb.early_stopping` icin
  `eval_set` olarak kullanildi. Bu iliski, Hipotez 1'deki HER walk-forward fold'unun kendi
  validasyon setiyle olan iliskisiyle AYNI karakterdedir (fold da kendi val'ini sadece
  early-stopping icin kullanmisti) — yani bu, gorev tanimindaki "final modelle AYNI
  egitim-boyutu/karakterdeki TEK bir fold'dan" sartini karsilar.
- Esik-aday tablosu (0,60/0,40, 0,575/0,425, 0,55/0,45) artik BU TEK kaynaktan hesaplaniyor;
  4 farkli modelin havuzlanmis OOF tahminleri HICBIR yerde kullanilmadi.
- Purged/embargolu walk-forward (4 fold) YINE DE calistirildi (S2 Madde1 zorunlulugu, ana test
  tasarimindan cikarilmadi) ama ARTIK SADECE model-stabilite/AUC-diagnostigi icin — esik
  SECIMINE hicbir katkisi yok. Bu, Muhendis'in kendi yetkisi disinda bir model/mimari degisikligi
  DEGIL, sadece kalibrasyonun HANGI VERIDEN yapildigina dair bir yontemsel duzeltmedir (Risk
  Analisti'nin acikca talep ettigi degisiklik).
- MIN_SAMPLE (>=30) korumasi ve fallback mantigi (hicbir aday esigi gecemezse en genis
  kapsamli aday secilir + YETERSIZ_VERI bayragi) Hipotez 1 ile BIREBIR AYNI kaldi.

**Duzeltmenin sonucu (bu turde gozlemlenen — Bolum 4.2'de detay):** Duzeltilmis kaynakla
(final_innerval_idx, n=12.219) TUM esik adaylari (0,60/0,40 dahil, en genis aday) SIFIR ornek
uretti (`long_n=0, short_n=0` her uc aday icin de) — yani fallback devreye girdi ve
YETERSIZ_ORNEKLEM bayragi kaldirildi (asagida). **Bu, Hipotez 1'deki paradoksu (OOF'ta sinyal
var gibi gorunup TEST'te yok olmasi) ORTADAN KALDIRDI:** duzeltilmis kalibrasyon kaynagi da
(final modelin kendi ic-validasyonu) TEST ile TUTARLI sekilde sinyal-yoklugu gosteriyor — yani
sonuc artik YONTEMSEL BIR ARTEFAKT degil, modelin GERCEKTEN hicbir donemde (ne ic-validasyon ne
TEST) yuksek-guven bolgesine ulasamadiginin dogru/tutarli bir yansimasidir.

---

## 1) KUTUPHANE ON-KOSULU

Hipotez 1/2 turlerinde zaten dogrulanmisti (pandas 3.0.3, lightgbm 4.6.0, xgboost 3.3.0,
scikit-learn 1.9.0, numpy 2.5.0 — hepsi kurulu). Bu turde YENIDEN KURULUM YAPILMADI, gorev
talimati geregi atlandi.

---

## 2) ON-KONTROL SONUCLARI (S1 stres-testi + DST) — AYRIK, GECTI/GECMEDI

### 2.1 DST/Saat-Eslesme Dogrulamasi — **DEVRALINAN + BU TURDE TEKRAR TEYIT EDILDI**

Hipotez 1 ile AYNI feature/oturum pipeline'i kullanildigi icin gorev talimati geregi Hipotez 1'in
GECTI sonucu devralinabilirdi; script yine de ayni kodla BAGIMSIZ olarak tekrar calistirildi
(ekstra maliyeti onemsiz) — sonuc: **8/8 bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI**,
MT5 sunucusunun DST'yi TAKIP ETTIGI Hipotez 1'deki gibi burada da dogrulandi. **GECTI.**

### 2.2 S1 — Maliyet-Orani Stres Testi (k=2,0 icin AYRICA/YENIDEN hesaplandi)

Hipotez 1'in P90 sonucu (k=1,5'e ozel) devralinamazdi (gorev talimati) — bu k degeri icin
yeniden hesaplandi:

| Olcum | Hipotez 1 (k=1,5) | Hipotez 3 (k=2,0) |
|---|---|---|
| ATR14(M15) medyan | 287,43 pts | 287,43 pts |
| ATR14(M15) P90 | 936,79 pts | 936,79 pts |
| Spread medyan | 27,0 pts | 27,0 pts |
| Spread P90 | 36,2 pts | 36,2 pts |
| Spread max | 137,0 pts | 137,0 pts |
| Hedef (k x ATR medyan) | 431,14 pts | 574,86 pts |
| **Oran — medyan-spread** | 15,97x | **21,29x** |
| **Oran — P90-spread (STRES TESTI)** | 11,91x | **15,88x** |
| Oran — max-spread (ekstrem) | 3,15x | 4,20x |
| Esik alt sinir | 15,0x | 15,0x |
| Medyan uzerinden GECTI mi | EVET | **EVET** |
| **P90 STRES TESTI GECTI mi** | **HAYIR** | **EVET** |

**Degerlendirme:** Stratejist'in on-tahmini (medyan 21,29x) burada dogrulandi. k=2,0, Hipotez 1'in
kaybettigi P90-stres testini GECIYOR (15,88x >= 15,0x esik) — bu, Hipotez 3'un ana amaci olan
guvenlik-marji genislemesini AMPIRIK olarak dogrular. Ancak asagida gorulecegi gibi bu marj
avantaji, modelin kendi ogrenme yetersizligini TELAFI ETMIYOR (0 islem sonucu degismiyor).

---

## 3) ANA TEST TASARIMI / YONTEM (Stratejist Karar 1-3, Hipotez 1 ile AYNI — sadece K_ATR farkli)

- **Model:** LightGBM ikili siniflandirici (`objective=binary`), Hipotez 1 ile BIREBIR AYNI sabit/
  dar hiperparametreler (`num_leaves=31, max_depth=6, learning_rate=0.05, n_estimators=500,
  min_child_samples=50, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, random_state=42`).
- **Etiket:** Triple-barrier, N=16 M15-bar (4 saat) zaman-bariyeri, **SL=TP=2,0xATR14(M15)**
  (RR=1:1) — Hipotez 1'de 1,5xATR idi. `hicbiri` (zaman-asimi) egitim/PRIMARY-test disi tutuldu
  (Karar 2, Hipotez 1 ile ayni sema).
- **Feature seti:** 23 sutun — Hipotez 1 ile BIREBIR AYNI (5 grup: Volatilite[3], MTF-
  Confluence[4], Hacim[3], Oturum/Gun-Ici[6], Fiyat-Yapisi/Momentum[7]).
- **Veri bolumu (kronolojik, karistirilmadi):** toplam 99.999 M15 bar (2022-04-18 → 2026-07-10).
  TRAINVAL: ilk %80 (2022-04-18 → 2025-09-03, n=59.569 ikili-etiketli). PURGE: trainval ornekleri
  `i+N<=trainval_end_bar` ile sinirlandi. EMBARGO: 24 bar (6 saat). TEST: son dilim (2025-09-04 →
  2026-07-10, n=15.237 ikili-etiketli), **TEK KEZ** kullanildi.
- **Walk-forward:** TRAINVAL icinde 5 esit segment → 4 purged/embargolu fold (S2 Madde1) —
  ARTIK SADECE model-stabilite/AUC-diagnostigi icin, esik-kalibrasyonuna KATKISI YOK (bkz. Bolum 0).
- **Esik-kalibrasyonu:** DUZELTILMIS yontem — SADECE final modelin kendi ic-validasyon
  (`final_innerval_idx`, n=12.219) tahminleri uzerinde precision-proxy(WR) taramasi — TEST
  SETINE BAKILMADI (S2 Madde2 korunuyor).
- **Feature-sizinti kontrol listesi (S2 Madde3):** tum maddeler teyit edildi (ileri-bakan bilgi
  yok, normalizasyon sadece egitim setinden, MACD HAM DEGER kullanildi — isaret degil, K_ATR
  degisiminin bu maddeleri etkilemedigi teyit edildi).
- **Basari kriterleri (egitimden ONCE sabitlendi, S2 Madde4):** HEDEF_PF=1,5, HEDEF_WR=%60,0
  (RR=1:1 icin, `justin_gecmis_calisma.md`), HEDEF_DD=%20 kumulatif — Hipotez 1 ile AYNI (RR
  degismedigi icin).
- **Maliyet modeli:** tick-bazli gercek maliyet (Justin ailesi standardi) — Hipotez 1 ile AYNI.
- **Lot/risk:** `justin_gecmis_calisma.md` geregi kasa=2.000 USD, lot=0,01 (sabit, bu kasa
  diliminde), risk-basi = kasa x %1 ust sinir.
- **3-sinifli alt-varyant:** Stratejist raporunda OPSIYONEL/takdire-birakilmis olarak isaretlenen
  bu alt-varyant CALISTIRILMADI — bu tur, gorev tanimindaki ZORUNLU adimlara (S1 P90-testi, S2
  protokolu, esik-kalibrasyon duzeltmesi, Hipotez 1 karsilastirmasi) odaklandi. Bu bir eksiklik
  degil, Stratejist'in acikca birakti gi bir takdir kararidir.

---

## 4) SONUCLAR

### 4.1 Walk-Forward (Purged/Embargolu, 4 fold) — SADECE Diagnostik (esik-kalibrasyonuna KATKISI YOK)

| Fold | Train n | Val n | Val AUC | best_iteration |
|---|---|---|---|---|
| 1 | 11.855 | 11.793 | 0,4965 | (early-stop) |
| 2 | 23.666 | 11.834 | 0,5149 | (early-stop) |
| 3 | 35.539 | 11.769 | 0,4973 | (early-stop) |
| 4 | 47.332 | 12.219 | 0,5209 | (early-stop) |

**AUC ozet: ortalama=0,5074, std=0,0107, min=0,4965, max=0,5209.**

> Hipotez 1'deki (ortalama=0,5075, std=0,0122) ile PRATIKTE AYNI — k'nin buyumesi walk-forward
> ayirt-edicilik seviyesini DEGISTIRMEDI, hala neredeyse RASSAL.

### 4.2 Esik-Kalibrasyonu (DUZELTILMIS yontem — final modelin kendi ic-validasyonu, TEST SETINE BAKILMADI)

| Esik (Long/Short) | Long n | Long WR-proxy | Short n | Short WR-proxy | Toplam n | Kapsama |
|---|---|---|---|---|---|---|
| 0,60 / 0,40 | 0 | - | 0 | - | 0 | %0,0 |
| 0,575 / 0,425 | 0 | - | 0 | - | 0 | %0,0 |
| 0,55 / 0,45 | 0 | - | 0 | - | 0 | %0,0 |

**HICBIR aday MIN_SAMPLE (>=30) esigini gecmedi** (uc adayin da long_n=short_n=0) — fallback
uygulandi (en genis kapsamli aday, 0,60/0,40, secildi) ve **YETERSIZ_ORNEKLEM_FALLBACK_UYGULANDI
= True** olarak isaretlendi. Kalibrasyon kaynagi (`final_innerval_idx`, n=12.219) icindeki p
dagilimi, TEST setindekiyle (Bolum 4.4) TUTARLI sekilde dar bir bantta (rassal-seviyeye yakin)
kalmis — bu, Bolum 0'da aciklanan duzeltmenin BEKLENEN/DOGRU sonucudur: artik OOF-ile-final-model
arasinda bir CELISKI yok, ikisi de ayni (sinyal-yoklugu) gercekligi yansitiyor.

### 4.3 Final Model Egitimi

- Egitim n=47.332, ic-validasyon n=12.219, ic-validasyon AUC=**0,5209** (rassal-seviyeye yakin,
  Hipotez 1'in 0,4990'ina gore hafifce yuksek ama bu farki anlamli saymak icin yeterli kanit yok
  — TEST AUC'u ile karsilastirilmali, asagida).
- **best_iteration=1** — Hipotez 1 ile AYNI: erken durma yine SADECE 1 boosting turunda devreye
  girdi, model pratikte tek bir sig agac.
- **Feature-onem tablosu (gain/split):**

| Feature | Hipotez 1 (k=1,5) onem | Hipotez 3 (k=2,0) onem |
|---|---|---|
| atr14_m15 | 0 | 0 |
| atr_regime_ratio | (dusuk) | 0 |
| atr14_h1_aligned | 10 | **8** |
| m15_trend | 0 | 0 |
| h1_trend_aligned | 0 | 0 |
| h4_trend_aligned | (dusuk) | 1 |
| confluence_flag | 0 | 0 |
| tick_volume | (dusuk) | 1 |
| vol_slope_8bar | (dusuk) | 2 |
| hour_sin/cos | (dusuk) | 1 / 2 |
| dow | 6 | 2 |
| session_asia | (dusuk) | 1 |
| macd_line | (dusuk) | **7** |
| macd_hist | (dusuk) | 5 |
| (digerleri) | ~0 | 0 |

**Ozel gozlem (gorev tanimi Madde 6):** k=2,0'a gecis, Stratejist'in "ZORUNLU" isaretledigi ana
feature gruplarinin (ATR, MTF-trend, confluence) neredeyse SIFIR agirlik alma paternini
DEGISTIRMEDI — `atr14_m15=0, m15_trend=0, confluence_flag=0, h1_trend_aligned=0` Hipotez 1 ile
BIREBIR AYNI kaldi. En yuksek degerler bu turde `atr14_h1_aligned=8` ve `macd_line=7` (Hipotez
1'de `atr14_h1_aligned=10` ve `dow=6` idi) — sira/agirlik kucuk farklarla degisti ama BUYUKLUK
MERTEBESI (tek haneli, 500 boosting-turu-hakli n_estimators icinde pratik olarak onemsiz) AYNI
kaldi. **Sonuc: k'nin genisletilmesi (daha genis barrier, farkli sinif dengesi — hicbiri
%13,07→%24,92) modelin ogrenme kapasitesini/feature-kullanim paternini ANLAMLI OLCUDE
DEGISTIRMEDI.** Bu, sorunun barrier genisligi/sinif-dengesi degil, feature setinin (mevcut
haliyle) fiyat yonunu tahmin etmeye YETERSIZ olmasindan kaynaklandigina isaret ediyor.
- **TEST SETI (tek-kez) siniflandirma AUC'u: 0,5211** — Hipotez 1'in 0,5170'ine yakin, yine
  rassala yakin.

### 4.4 TANI: TEST Setinde Olasilik Dagilimi

| Istatistik | Hipotez 1 (k=1,5) | Hipotez 3 (k=2,0) |
|---|---|---|
| p_test min | 0,5037 | 0,4964 |
| p_test max | 0,5304 | 0,5280 |
| p_test ortalama | 0,5089 | 0,5100 |
| p_test std | 0,0047 | 0,0067 |
| Esik LONG (kalibre edilen ust sinir) asan bar sayisi | 0 | 0 |
| Esik SHORT (kalibre edilen alt sinir) asan bar sayisi | 0 | 0 |

Her iki hipotezde de final modelin TEST setindeki olasiliklari, kalibre edilen esige (Hipotez
1: 0,55/0,45; Hipotez 3: fallback 0,60/0,40) hicbir zaman ulasmiyor — **bu yuzden hem PRIMARY hem
SUPPLEMENTARY simulasyonda 0 islem tetiklendi, bu beklenen/dogrulanmis bir sonuctur, kod/veri
hatasi DEGILDIR.**

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

**KARAR: RED.** Gerekce (yorum degil, protokol-uygulamasi — Hipotez 1 ile AYNI mantik): Ortak
Ilkeler'deki "Minimum orneklem uyarisi" geregi, test edilen kumede HICBIR islem yoksa sonuc
anlamli/olculebilir DEGILDIR; S2 Madde4 (basari kriterleri onceden sabit) altinda bir kriterin
"olculemedi" cikmasi, o kriterin KARSILANDIGININ iddia edilemeyecegi anlamina gelir — dolayisiyla
protokol geregi varsayilan sonuc RED'dir. **Bu turde, ONEMLI bir metodolojik netlik kazanildi:**
Hipotez 1'deki 0-islem sonucu, kalibrasyon-yontemi kusuru (OOF-havuz vs final-model tutarsizligi)
yuzunden SORGULANABILIR bir durumdaydi (belki duzeltilseydi islem cikardi mi sorusu acikti). Bu
turde, DUZELTILMIS yontemle de (final modelin kendi ic-validasyonu) AYNI sinyal-yoklugu tekrar
gozlemlendi — yani 0-islem sonucu artik bir YONTEM ARTEFAKTI ihtimaliyle GOLGELENMIYOR, modelin
gercek/tutarli davranisidir.

---

## 5) KARSILASTIRMA — HIPOTEZ 1 (k=1,5) vs HIPOTEZ 3 (k=2,0) [ZORUNLU, gorev tanimi Madde 7]

| Boyut | Hipotez 1 (k=1,5) | Hipotez 3 (k=2,0) |
|---|---|---|
| Ikili-etiketli toplam n (trainval+test) | 86.618 | 74.806 |
| Hicbiri orani | ~%13,07 | ~%24,93 (beklenen degis-tokus, hata degil) |
| S1 medyan cost-ratio | 15,97x (esigin ALT SINIRI) | 21,29x (rahat marj) |
| **S1 P90-stres testi** | **KAYBEDILDI (11,91x < 15,0x)** | **GECILDI (15,88x >= 15,0x)** |
| Walk-forward AUC (ort, diagnostik) | 0,5075 (std 0,0122) | 0,5074 (std 0,0107) — pratikte AYNI |
| Final model ic-validasyon AUC | 0,4990 | 0,5209 |
| Final model TEST AUC (tek-kez) | 0,5170 | 0,5211 — ikisi de rassala yakin |
| Final model best_iteration | 1 (tek agac) | 1 (tek agac) — AYNI |
| Feature-onem (ATR/trend/confluence) | ~sifir | ~sifir — AYNI patern, degismedi |
| Esik-kalibrasyon kaynagi | 4-fold HAVUZLANMIS OOF (FLAWED) | final modelin KENDI ic-validasyonu (DUZELTILMIS) |
| Esik-kalibrasyon kaynaginda gecen aday sayisi | 210 (OOF-havuz, ama final modelle TUTARSIZ) | 0 (TUM adaylarda, final modelle TUTARLI) |
| Secilen esik | 0,55 / 0,45 | 0,60 / 0,40 (fallback, YETERSIZ_VERI bayrakli) |
| p_test'in esige ulasip ulasmadigi | HAYIR (max 0,5304 < 0,55) | HAYIR (max 0,5280 < 0,60) |
| PRIMARY islem sayisi | 0 | 0 |
| SUPPLEMENTARY islem sayisi | 0 | 0 |
| PF/WR/DD | tanimsiz | tanimsiz |
| **KARAR** | **RED** | **RED** |

**Sentez:** k=2,0, S1 maliyet-orani guvenlik marjini AMPIRIK olarak genisletti (P90-stres testini
gecti, Hipotez 1'in kaybettigi yerde) — bu, Hipotez 3'un tasarim amacini basariyla dogruladi.
Ancak bu marj genislemesi, modelin ayirt edici gucundeki (AUC~0,50-0,52) temel zayifligi
DEGISTIRMEDI: walk-forward AUC, final model best_iteration (=1), feature-onem paterni (ana
gruplar ~sifir) ve nihai TEST AUC'u Hipotez 1 ile PRATIKTE AYNI kaldi. Esik-kalibrasyon
duzeltmesi sayesinde bu turde 0-islem sonucu artik YONTEMSEL BIR SORU ISARETI tasimiyor —
kalibrasyon kaynagi ve TEST tutarli sekilde ayni sinyal-yoklugunu gosteriyor. **Sonuc: sorun
barrier genisligi (k) DEGIL, mevcut 23-feature/N=16 tasarimin fiyat yonunu tahmin etmeye
YETERSIZ kalmasidir** — bu, Risk Analisti'nin Hipotez 1 raporundaki "Arastirmaci'ya geri-bildirim
onerisi" (farkli/ek feature aileleri denenmesi) tavsiyesini bu turde de PEKISTIRIYOR.

---

## 6) GECICI DOSYA TEMIZLIGI NOTU

Bu tur icin gecici/patch dosyasi olusturulmadi. `backtest_ml_v1_hipotez3.py` Hipotez 1
script'inden (yapi/kutuphane-kullanimi referansi olarak, kopyalama degil) turetilerek SIFIRDAN
yazildi; script tek calistirmada (EXIT_CODE=0, hicbir hata) bastan sona tamamlandi.

---

## 7) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — LightGBM Ikili Yon-Tahmini (N=16/k=2,0xATR14-M15) — HIPOTEZ 3 (guvenlik-marji varyanti) — ML/Gradient Boosting — 2026-07-12

Egitim / Walk-Forward (4 fold, purged+embargolu, SADECE diagnostik - esik-kalibrasyonuna KATKISI YOK):
  AUC ortalama=0,5074 (std=0,0107, min=0,4965, max=0,5209) - Hipotez 1 (0,5075) ile PRATIKTE AYNI
  Final model ic-validasyon AUC=0,5209, best_iteration=1 (erken durma - pratikte tek agac, Hipotez 1 ile AYNI)

ESIK-KALIBRASYON YONTEMi DUZELTMESI (Risk Analisti'nin Hipotez 1 Geri Bildirim Madde 1 talebi UYGULANDI):
  Kalibrasyon ARTIK SADECE final modelin KENDI ic-validasyonundan (final_innerval_idx, n=12.219) yapiliyor,
  4-fold havuzlanmis OOF KULLANILMADI. Sonuc: TUM esik adaylarinda (0,60/0,40 dahil, en genis aday) n=0 -
  fallback + YETERSIZ_VERI bayragi (secilen esik: 0,60/0,40). Bu, Hipotez 1'deki OOF-vs-final-model
  PARADOKSUNU ORTADAN KALDIRDI: kalibrasyon kaynagi artik TEST ile TUTARLI (ikisi de sinyal-yoklugu).

Gorulmemis Veri (TEST seti, TEK KEZ, 2025-09-04 -> 2026-07-10, n=15.237):
  TEST AUC=0,5211 (rassala yakin, Hipotez 1'in 0,5170'ine yakin)
  p_test dagilimi: min=0,4964 max=0,5280 ortalama=0,5100 (kalibre edilen 0,60/0,40 esigine HICBIR ZAMAN ulasmiyor)
  PRIMARY (hicbiri-haric) islem sayisi = 0 -> PF/WR/DD tanimsiz
  SUPPLEMENTARY (hicbiri-dahil, canliya-yakin) islem sayisi = 0 -> PF/WR/DD tanimsiz
  HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 -> HICBIRI OLCULEMEDI (n=0)
  KARAR: RED (olcum yoksa hedefin karsilandigi iddia edilemez, S2 Madde4 + Ortak Ilkeler)

Dikkat noktalari:
  - S1 P90-stres testi bu k'da GECILDI (15,88x >= 15,0x) - Hipotez 1'in kaybettigi yerde (11,91x). Guvenlik-
    marji tasarim amaci AMPIRIK olarak dogrulandi, ama modelin AUC/best_iteration/feature-onem zayifligini
    TELAFI ETMEDI.
  - Model ogrenme kapasitesi (gorev Madde 6 ozel istegi): best_iteration=1 ve ATR/trend/confluence
    feature'larinin ~sifir agirligi Hipotez 1 ile BIREBIR AYNI kaldi - k'nin genisletilmesi modelin
    ogrenme kapasitesini/feature-kullanim paternini DEGISTIRMEDI. Bu, sorunun barrier/sinif-dengesi degil,
    mevcut feature setinin YETERSIZLIGINE isaret ediyor.
  - OVERFITTING_RISKI: Hipotez 1'deki gibi burada da YOK - walk-forward (0,5074) ve TEST (0,5211) AUC'leri
    birbirine yakin, yani egitimde-iyi/testte-kotu deseni yok; iki donemde de TUTARLI ZAYIFLIK var.
  - Esik-kalibrasyon duzeltmesi basariyla uygulandi ve dogrulandi (Bolum 0) - Hipotez 1'deki yontemsel
    tutarsizlik bu turde YOK, sonuc artik metodolojik olarak temiz.
  - Hipotez 1 ile karsilastirmali tam tablo (Bolum 5) - iki hipotez de RED, k=2,0'nin tek somut kazanci
    S1 P90-stres testini gecmesi, model performansinda hicbir iyilesme YOK.
  - Opsiyonel 3-sinifli alt-varyant (Stratejist raporu, takdire birakilmis) bu turde CALISTIRILMADI.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez3_20260712.md
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v1_hipotez3_output.json
```

---

## 8) iZOLASYON NOTU

Bu script ve bu rapor, MilaGold/Lisa/Signal GPT'ye ait HICBIR dosyayi/parametreyi/format-sablonunu
acmadi veya referans almadi. Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi. Veri dogrudan
MT5'ten (MetaTrader5 kutuphanesi, GOLD sembolu M15 OHLCV+tick_volume+spread) cekildi. Script,
Hipotez 1'in script'inden (`backtest_ml_v1_hipotez1.py`) yapi/kutuphane-kullanimi REFERANSI
olarak turetildi (kopyalama degil) — bu, Justin'in KENDI onceki turu oldugu icin izolasyon
kapsami DISINDADIR (izolasyon kurali MilaGold/Lisa/Signal GPT'ye ait dosyalar icin gecerlidir).

---

## 9) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (script calistirma +
raporlama), canli sisteme dokunus YOK, Justin demo/arastirma asamasindadir (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam (hicbir kalici/geri-donulmez islem
yapilmadi), mali etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru).
→ **STOP-genis/bilgi-notu kategorisi, Ertan onayi GEREKMEZ.** Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
