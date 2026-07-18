# STRATEJICI RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile (M15+), v2 (ML Tam Tur 2)

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
Pipeline adimi: 2/4 (Arastirmaci → **Stratejist** → Backtest Muhendisi → Risk Analisti)
Tarih: 12 Temmuz 2026 (VPS-yerel)
Gorev kaynagi: Orkestrator gorev tanimi, "GOREV TANIMI — Orkestrator → Stratejist (ML/
Feature-Tabanli Gold Scalping, v2 — ML Ailesi TAM TUR 2)"
Girdi raporu: `arastirmaci_gold_scalping_ml_v2_raporu.md` (Arastirmaci, ML Tam Tur 2, 1/4 —
TAMAMLANDI)

**Governance durumu (bilgi amacli, tekrar):** S3 sayaci Tam Tur 1'in ucu-de-RED sonucuyla
su an **1/2**. Bu Stratejist adimi bir Risk Analisti karari uretmedigi icin sayaci
DEGISTIRMEZ. Bu turun (Tur 2) nihai Risk Analisti karari RED ve AYNI patern (model rassal-
seviye AUC, ana feature'lar ~sifir agirlik, esik-kalibrasyonunda 0 islem) ile sonuclanirsa
sayac 2/2'ye ulasir ve Orkestrator bir sonraki Arastirmaci turunu Ertan onayi olmadan
baslatmaz. Bu, asagidaki hipotezlerin tasarimini bilgilendiren bir arka-plan riskidir.

---

## OTURUM OZETI

Bu oturumda **Arastirmaci'nin v2 raporu** (BULGU 1-11, Onerilen Feature Seti/Label Tanimi, ML
Tasarim Onerisi, Riskler, Acik Sorular) ham girdi olarak alinmistir. Ozellikle:

- **BULGU 1-2 (Grup A/ADX-rejim):** ADX rejim etiketi BUYUKLUK/volatilite bilgisi tasiyor
  (trend rejiminde %16,6 daha buyuk hareket) ama yon-sureklilik orani ucunde de %48,99-49,91
  — RASSAL SEVIYE. Yon-tahmin-edici DEGIL.
- **BULGU 4-5 (Grup B/pivot-S-R):** Gunluk/haftalik pivot mesafesi olculdu (net bir yon-etkisi
  gozlenmedi). 20-gunluk rolling-high yakinliginda ASIMETRIK bir momentum bulgusu var: yuksege
  yakinken +52 puan medyan (belirgin), dusuge yakinken -2 puan (yon yok). Arastirmaci bunu
  "digerlerinden goreceli daha guclu bir aday" olarak isaretledi.
- **BULGU 6 (Grup C/DXY):** Es-zamanli korelasyon guclu (-0,41) ama ONGORUCU/lead-lag
  korelasyon PRATIKTE SIFIR (-0,0008). Veri kaynagi (USDX-SEP26) da SUPHELI/dogrulanmamis
  (olasi surekli-kontrat/splice serisi).
- **BULGU 7-9 (Grup D/mikro-yapi):** SADECE son 20 islem gunu (n=1.260 bucket) icin olculebildi.
  Yuksek-imbalance sonrasi medyan -254 puan, dusuk-imbalance sonrasi +4 puan — BUYUK bir
  medyan-fark, ANCAK dogrudan korelasyon ZAYIF (-0,0315), n=251/grup KUCUK, bu tutarsizlik
  Arastirmaci tarafindan "guclu bir sinyal DEGIL, arastirilmaya deger ama dogrulanmamis" olarak
  isaretlendi. Olceklenebilirlik (4,2 yillik tam gecmis) COZULMEMIS bir sorun.
- **BULGU 10-11 (Etiket alternatifleri):** 3-sinifli deadzone (k=0,3xATR14, N=8) orta-dengeli
  bir dagilim veriyor (%43,9/%40,5/%15,6). Regresyon-hedefi (BULGU 11) sinyal/gurultu orani
  ~74x ile ONERILMIYOR.

**Tam Tur 1'den (v1 Stratejist raporu) neyi DEVRALDIM / neyi DEGISTIRDIM:**

| Unsur | Tur 1 (v1) | Tur 2 (bu rapor) | Degisti mi? |
|---|---|---|---|
| N (tutma suresi) | 16 M15-bar (4 saat) | 16 M15-bar (4 saat) | **KORUNUYOR** |
| k (barrier/SL-TP) | 1,5xATR14 (ana) + 2,0 (duyarlilik) | 1,5xATR14 (ana, ayni gerekce) | **KORUNUYOR** |
| Etiket semasi | Ikili (TP-once/SL-once, hicbiri filtre) | Ikili (Hipotez 1) + 3-sinifli deadzone (Hipotez 2, YENI, PARALEL) | **GENISLETILDI** |
| Feature seti | Grup 1-5 (ATR, MTF-confluence, hacim, oturum, momentum) | Ayni + Grup B (pivot/S-R, YENI, ZORUNLU) | **GENISLETILDI** |
| Model | LightGBM (ana) + XGBoost (kiyaslama) | LightGBM (bu tur icin yeterli, gerekce asagida) | **DARALTILDI (gerekceli)** |
| Grup A (ADX) | Yoktu | Degerlendirildi, **ELENDI** | — |
| Grup C (DXY) | Yoktu | Degerlendirildi, **ELENDI** | — |
| Grup D (mikro-yapi) | Yoktu | KISITLI/PILOT olarak Hipotez 3'e ALINDI | **YENI, dar kapsam** |

Risk Analisti'nin Tam Tur 1'deki UC BAGIMSIZ RED gerekcesi ozetle: model AUC rassal-seviye
(~0,50-0,52), ana feature'larin (ATR/trend/confluence) SHAP/gain-agirligi ~sifir,
`best_iteration=1` (pratikte tek sig agac), esik-kalibrasyonunda TUM adaylar 0 islem uretti.
Ucu de (LightGBM k=1,5, XGBoost k=1,5, LightGBM k=2,0) AYNI paterne ulasti — sonuc: "sorun
model-secimi veya barrier-genisligi degil, feature seti/etiket tasariminin kendisi." Bu
raporun tum hipotez tasarimi DOGRUDAN bu tespite karsilik vermek uzerine kuruludur: **feature
seti ve etiket, bu turde BILEREK ve AYRI AYRI (izole) degistirilmistir**, boylece Backtest
Muhendisi/Risk Analisti hangi degiskenin (feature mi, etiket mi) sonucu etkiledigini
ayirt edebilir.

---

## KARAR VERMENIZ BEKLENEN OZEL NOKTALAR — YANITLAR

### Karar 1 — Feature Grubu Secimi/Onceligi (Grup A-D) — KESIN

| Grup | Karar | Gerekce |
|---|---|---|
| **A (ADX/rejim)** | **ELENDI (bu tur icin)** | BULGU 2, yon-sureklilik oranini UCUNDE de %48,99-49,91 (rassal-seviye) olarak olcmustur — bu grup sadece BUYUKLUK/volatilite bilgisi tasir. Tam Tur 1'in RED gerekcesi zaten "ATR-tabanli volatilite feature'lari (v1 Grup 1) ~sifir agirlik aldi" idi (Risk Analisti feature-onem tablosu, `atr14_m15=0`) — ADX, KAVRAMSAL OLARAK AYNI BILGI TURUNU (volatilite buyuklugu) FARKLI bir formulle olcen bir feature'dir; zaten basarisiz olmus bir bilgi turunu ikinci bir formulle tekrarlamak, S2'nin "dar arama uzayi" ilkesiyle CELISIR (ek karmasiklik, dusuk beklenen fayda). Pozisyon-boyutlandirma icin ileride (ayri bir tasarim sorusu olarak) degerlendirilebilir, ama bu turun YON-tahmin modeline ZORUNLU DEGIL.
| **B (pivot/gorece S-R)** | **ZORUNLU (YENI)** | BULGU 5, digerlerinden GORECELI olarak en somut asimetriyi sunuyor (+52 vs -2 puan medyan, 20-gun-yuksege-yakinlik). Bu, v1'in feature setinde HIC OLMAYAN bir "gorece konum" bilgisidir (mutlak fiyat/ATR degil, fiyatin KENDI YAKIN-GECMISINE gore nerede oldugu) — kavramsal olarak v1'in basarisiz feature'larindan (ATR buyuklugu, trend isareti) FARKLI bir bilgi turu, bu yuzden "ayni basarisiz bilgiyi tekrarlama" riski digerlerine gore daha dusuktur.
| **C (DXY)** | **ELENDI (bu tur icin)** | BULGU 6, ongorucu/lead-lag korelasyonun PRATIKTE SIFIR (-0,0008) oldugunu gostermistir — bu, feature'in yon-tahmininde katki saglamasinin BEKLENMEDIGININ dogrudan sayisal kanitidir. Ek olarak veri kaynaginin kendisi SUPHELI (olasi splice-seri, BULGU 6 SINIR). Iki bagimsiz zayif gerekce (sinyal yok + kaynak guvenilirligi supheli) bir arada, bu grubu bu tur icin ELEMEK icin yeterlidir; DXY'yi test etmek ayri, kendi basina bir arastirma/dogrulama turu gerektirir (Acik Soru 2).
| **D (mikro-yapi/tick-proxy)** | **KISITLI/PILOT (Hipotez 3'e ozel, ayri madde)** | Asagida Karar 4'te detaylandirilmistir — ana Hipotez 1/2'ye DAHIL EDILMEMISTIR.

### Karar 2 — Etiket Semasi — KESIN

**Secim: IKI SEMA PARALEL test edilecek — (a) Hipotez 1'de Tur 1 ile AYNI ikili
(TP-once/SL-once, hicbiri filtre, N=16/k=1,5) KORUNUYOR; (b) Hipotez 2'de YENI 3-sinifli
deadzone (BULGU 10 yontemi, k_label=0,3xATR14, N=16'ya UYARLANMIS) denenecek.**

Gerekce:
- Gorev tanimi acikca "ayni ikili semayi mi tekrar mi, yoksa 3-sinifliye mi gececeksiniz, KESIN
  belirleyin" diyor — bu Stratejist KESIN karari **her ikisini de, PARALEL ve AYRI hipotezler
  olarak** test etmektir. Gerekce: Tam Tur 1'in RED nedeni "feature VEYA etiket tasarimi"
  seklinde BIRLESIK ifade edilmisti; eger bu turde AYNI ANDA hem feature (Grup B) hem etiket
  (3-sinif) degistirilseydi, RED/KABUL sonucunun HANGI degiskenden geldigi ayirt edilemezdi
  (confounding). Bu yuzden **Hipotez 1 = SADECE feature degisikligi (etiket sabit, ikili)**,
  **Hipotez 2 = feature degisikligi + etiket degisikligi (3-sinif)** olarak tasarlanmistir —
  Hipotez 1 vs Hipotez 2 karsilastirmasi, etiket degisikliginin EK bir katki saglayip
  saglamadigini izole eder.
- **ONEMLI SAYISAL TUTARLILIK NOTU (CLAUDE.md geregi):** BULGU 10'daki 3-sinifli dagilim
  (%43,9/%40,5/%15,6) Arastirmaci tarafindan N=8 (2 saat) ufkunda olculmustur; Hipotez 2 N=16
  (4 saat) kullandigi icin bu dagilim DOGRUDAN GECERLI DEGILDIR — Backtest Muhendisi bu dagilimi
  N=16 ufkunda YENIDEN HESAPLAMALIDIR (k_label=0,3xATR14 baslangic noktasi olarak kullanilabilir,
  ama N degistigi icin yukari/asagi/notr oranlari FARKLI cikabilir; bu bir yeniden-olcumdur, BULGU
  10 ile birebir karsilastirilmamalidir).
- **Iki farkli k ayrimi acikca isaretlenmeli:** Hipotez 2'de KI IKI FARKLI k parametresi vardir:
  `k_label=0,3xATR14` (SADECE egitim etiketini/sinifini belirlemek icin, "yukari/asagi/notr"
  siniflandirmasi) ve `k_risk=1,5xATR14` (GERCEK SL/TP mesafesi, pozisyon risk yonetimi icin,
  Hipotez 1 ile AYNI). Bu iki k KARISTIRILMAMALIDIR — model 3 sinif tahmin eder ama pozisyon
  acildiginda risk yonetimi HER ZAMAN k_risk=1,5xATR14 ile yapilir (S1 cost-ratio, 15,97x, bu
  nedenle Hipotez 1 ile AYNI kalir, yeniden hesaplanmasi GEREKMEZ).
- Regresyon-hedefi (BULGU 11) bu turde de ONERILMEMEKTEDIR — Arastirmaci'nin kendi onerisiyle
  (sinyal/gurultu ~74x) ve Risk Analisti'nin AUC~0,50-0,52 bulgusuyla (nitel tutarlilik)
  uyumlu olarak, bu rapor da regresyonu bir hipotez olarak SUNMAMAKTADIR.

### Karar 3 — N/k (Zaman-Dilimi/Tutma-Suresi) — KESIN: KORUNUYOR

**Secim: N=16 (4 saat), k=1,5xATR14 (Hipotez 1/2/3'un UCUNDE de AYNI) — degistirilmiyor.**

Gerekce:
- Tam Tur 1'in RED gerekcesi (Risk Analisti, "Hipotez 1/2 vs Hipotez 3 tutarlilik
  degerlendirmesi") ACIKCA soyle diyor: "barrier genisliginin (k=1,5 vs k=2,0) degistirilmesi
  modelin ogrenme kapasitesini/feature-kullanim paternini ANLAMLI OLCUDE DEGISTIRMEDI... sorunun
  barrier genisligine degil, feature setinin kendisine bagli oldugu UC BAGIMSIZ kanitla
  desteklenmis durumda." Yani N/k EKSENI zaten Tur 1'de test edildi ve sonucu DEGISTIRMEDIGI
  gosterildi — bu eksende tekrar oynamanin (orn. N=8'e donmek veya k=2,0'a gecmek) bu turde
  EK bir tani-koyucu deger saglamasi BEKLENMEZ.
- Ayrica, eger N/k bu turde de degistirilseydi, feature/etiket degisikliginin etkisini feature/
  etiket'ten mi yoksa barrier degisiminden mi geldigini ayirt etmek IMKANSIZ hale gelirdi
  (Karar 2'deki izolasyon mantigiyla AYNI gerekce, bu kez N/k eksenine uygulanmis hali).
- **Grup B/D farkli bir ufuk gerektirir mi?** Grup B (pivot/S-R mesafesi) bir "DURUM" (state)
  feature'idir — herhangi bir tutma-suresiyle uyumlu calisir, N=16'ya ozel bir ufuk gerektirmez.
  Grup D (mikro-yapi, Hipotez 3) Arastirmaci'nin kendi olcumunde N=8 (2 saat) ufku kullanmisti
  (BULGU 7) — Hipotez 3'te bu N=16'ya UYARLANACAK (asagida, Karar 4), bu da BULGU 7'nin ham
  sayilarinin dogrudan tekrari degil, YENIDEN OLCUM olarak isaretlenmistir.

### Karar 4 — Grup D (Mikro-Yapi) Olceklenebilirlik Karari — KESIN

**Secim: Acik Soru 1'in secenek (a)'si — SADECE SON DONEM icin egitim+test, KISITLI/PILOT bir
hipotez (Hipotez 3) olarak, ANA/birincil hipotezlere (1/2) DAHIL EDILMEDEN.**

Gerekce:
- Secenek (b) (M1-bar-tabanli kaba proxy) bu turde SECILMEDI — bu, YENI bir veri-toplama/
  hesaplama metodolojisi gerektirir (M1 OHLC'den buy/sell-pressure yaklasik hesabi), bu HENUZ
  olculmemis/tasarlanmamis bir yontemdir; bu turde bunu tasarlamak "yeniden arastirma" sinirina
  girer (gorev tanimi bunu bu Stratejist turunun kapsami DISINDA tanimliyor).
- Secenek (c) (tamamen ELEME) da secilMEDI, cunku BULGU 7 (medyan-fark -254 vs +4 puan), her ne
  kadar korelasyonla celiskili olsa da, bu turun ARASTIRILAN TUM feature gruplari icinde (A-D)
  YON bilgisine dair TEK somut buyuk-buyuklukte gozlemdir (Grup A yon-sinyali TASIMIYOR, Grup B
  sadece medyan-asimetri, Grup C ongorucu-sifir) — bunu HIC test etmeden tamamen elemek, olasi
  bir sinyali erken kapatmak anlamina gelebilir.
- Bu nedenle **secenek (a)**: Hipotez 3, tick verisinin fiilen cekilebilir oldugu bir donemde
  (Arastirmaci'nin son 20 islem gunu ornegi TOO KUCUK, n=251/grup; bu tur icin ONERI: son 60-90
  islem gunu, Acik Soru 5'e de cevap olacak sekilde genisletilmis) SINIRLI bir egitim/test
  penceresinde calisir — TAM 4,2 yillik tarihe olceklenmeye CALISILMAZ. Bu, bir "olceklenebilirlik
  cozumu" DEGIL, dar kapsamli bir ON-TEST/pilot niteligindedir; sonucu ne olursa olsun (KABUL
  veya RED) tam-tarihsel olceklendirme sorusu (Acik Soru 1, Riskler Madde 2) bu raporla
  COZULMUS SAYILMAZ.

### Karar 5 — DXY Veri Kaynagi Guveni — Bilgi Amacli Yanit

Grup C (DXY) bu turun HICBIR hipotezine DAHIL EDILMEDIGI icin (Karar 1), Backtest Muhendisi'nin
bu tur icin USDX-SEP26 serisini BAGIMSIZ dogrulama ZORUNLULUGU YOKTUR — bu dogrulama ihtiyaci
sadece Grup C ileride (ayri bir tur/karar ile) yeniden gundeme gelirse devreye girer. Bu karar,
Acik Soru 2'yi COZMEZ, sadece bu tur icin ONCELIKSIZ oldugunu teyit eder (Arastirmaci'nin kendi
onerisiyle, "DUSUK ONCELIKLI aday", tutarlidir).

---

## HIPOTEZLER

### HIPOTEZ 1 — LightGBM Ikili + Grup B (Pivot/S-R) Eklenmis Feature Seti [ANA HIPOTEZ, FEATURE-IZOLE]

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (LightGBM)

**MANTIK:** Tam Tur 1'in RED gerekcesi "sorun model-secimi/barrier-genisligi degil, feature
seti/etiket tasariminin kendisi" idi. Bu hipotez, etiketi ve N/k'yi TAMAMEN SABIT tutarak
(Karar 2/3), SADECE feature setine BULGU 5'in en somut yeni adayini (Grup B, pivot/20-gunluk
S-R mesafesi) ekleyerek, "feature seti degisirse model ogrenir mi" sorusunu TEK BASINA izole
test eder. Eger bu hipotez de AYNI patern (rassal AUC, Grup B dahil TUM feature'lar ~sifir
agirlik, 0-islem esik-kalibrasyonu) ile RED olursa, bu ONEMLI bir ek kanit olur: sorun tek bir
yeni feature eklemekle cozulemeyecek kadar derin, yani M15 OHLC-turevi/gorece-konum
feature'larinin GENELDE bu etiket/ufuk kombinasyonunda yon tahmin edemedigi.

**YONTEM DETAYI:**
- Model: LightGBM binary classifier (`objective=binary`), Tur 1 ile AYNI dar hiperparametre
  araligi (num_leaves ~15-31, sinirli derinlik, genis grid-search YOK — S2 geregi).
  XGBoost kiyaslamasi bu turde ZORUNLU DEGIL (Tur 1'de zaten iki model ailesi test edildi, fark
  yaratmadi — Risk Analisti'nin "sorun model-secimi degil" tespitini tekrar dogrulamanin
  marjinal degeri dusuk; ek hesaplama maliyeti feature/etiket testine ayrilmali).
- Feature seti: v1'in ZORUNLU gruplari (1-Volatilite/ATR, 2-MTF Confluence, 3-Hacim/Tick-
  Yogunlugu, 4-Oturum/Gun-Ici cekirdek, 5-Fiyat Yapisi/Momentum, ~18-22 sutun) + **YENI Grup B**
  (gunluk/haftalik pivot mesafesi, 20-gunluk rolling-high/low mesafesi + yakinlik bayragi,
  ~4-6 ek sutun). Toplam tahmini **~22-28 sutun**.
- Veri: XM/MT5 GOLD M15, ayni 4,2 yillik seri (2022-04-18→2026-07-10).

**GIRIS/CIKIS MEKANIZMASI:** Hipotez 1 (Tur 1) ile AYNI: model her barda P(yukari-bariyer-once)
uretir; esik (baslangic onerisi p>=0,55-0,60 → LONG, p<=0,40-0,45 → SHORT, arasi → ISLEM YOK)
egitim/validasyon setinde kalibre edilir (S2 Madde 2, test setine bakilmadan).

**SL/TP veya RISK YONETIMI:** SL=TP=k x ATR14(M15)=1,5xATR14(giris ani, simetrik), N=16 zaman-
bariyeri (Tur 1 ile BIREBIR AYNI). RR=1:1 → HEDEF_WR=%60,0. Lot/risk kurallari
`justin_gecmis_calisma.md` geregi (kasa=2.000 USD, risk-basi %1 ust sinir, taban 0,01 lot, her
2.000 USD=+0,01 lot).

**DOGRULAMA IHTIYACI:** Purged/embargolu walk-forward (N=16-bar + embargo, S2 Madde 1) ZORUNLU.
Test-seti tek-kullanim (S2 Madde 2). Feature-sizinti kontrol listesi (S2 Madde 3) — Grup B icin
OZELLIKLE: gunluk/haftalik pivotun ONCEKI TAMAMLANMIS gun/haftadan (nedensel shift) dogru
kesildigi, 20-gunluk rolling-high/low'un ILERI-BAKIS icermedigi (sadece t anindan ONCEKI 20 gun)
BAGIMSIZ olarak yeniden dogrulanmali (Arastirmaci'nin kendi ic-mantik kontrolu YETERLI DEGIL,
ayri bir kod incelemesi gerekir — Arastirmaci raporu Riskler Madde 5'te bunu zaten belirtmis).

**RISKLER:**
- **Ana risk (dogrulama olmadan yargi vermeme geregi):** BULGU 5'teki +52/-2 puan medyan-
  asimetri, tipki BULGU 7'deki (Grup D) medyan-fark gibi, "aggregate'te guclu gorunen ama
  testte cokebilecek" bir gozlem OLABILIR — Arastirmaci'nin STRATEJIST'E NOT bolumu bunu acikca
  uyarmistir. Bu hipotezin KABUL/RED sonucu bu riski dogrudan test eder.
- N=16 (4 saat tutma), "scalping" projesi icin goreceli uzun ufuktur (Tur 1'de zaten not edildi,
  degismedi).
- Overfitting: feature sayisi ~22-28'e cikti (v1'in ~18-22'sinden biraz genis) — S2 geregi dar
  hiperparametre araligi KORUNMALI, feature sayisindaki artis hiperparametre aramasinin
  genisletilmesini GEREKTIRMEZ.
- Canliya-gecebilirlik: LightGBM inference hizi Tur 1'de de dogrulanmamisti (varsayim <10ms),
  bu turde de OLCULMELI (ek 4-6 feature hesaplama maliyeti kucuk ama MT5 agent icinde pivot/
  rolling-S-R hesaplarinin gercek-zamanli guncellenmesi ayrica dogrulanmali).
- S3 governance riski: bu hipotez RED olursa (ve Hipotez 2 de RED ile ayni paternde sonuclanirsa)
  S3 sayaci 2/2'ye ulasir — bu, hipotezin GECERLILIGINI etkilemez ama Orkestrator'un bir sonraki
  adiminda Ertan onayi gerektirecegi anlamina gelir (bilgi amacli, Stratejist is akisini
  degistirmez).

**ONCELIK: 1-Yuksek** — Risk Analisti'nin "feature seti tasarimin kendisi" tespitine dogrudan,
IZOLE (etiket/N/k sabit) karsilik veren tek hipotez; Tur 2'nin TEMEL/ilk test edilmesi gereken
tasarimi.

---

### HIPOTEZ 2 — LightGBM 3-Sinifli (Deadzone) + Grup B Eklenmis Feature Seti [ETIKET-IZOLE, PARALEL]

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (LightGBM, multiclass)

**MANTIK:** Hipotez 1 sadece feature setini degistirir (etiket sabit). Bu hipotez AYNI (Grup B
eklenmis) feature setini kullanir ama etiketi Karar 2 geregi 3-sinifli deadzone'a (BULGU 10
yontemi, N=16'ya uyarlanmis) degistirir — boylece Hipotez 1 vs Hipotez 2 karsilastirmasi,
etiket-tasarimi degisikliginin (barrier-touch ikili yerine sabit-ufuk-deadzone) EK bir katki
saglayip saglamadigini izole eder. Risk Analisti'nin Tur 1'deki "esik-kalibrasyonunda TUM
adaylar 0 islem uretti, modelin olasilik dagilimi cok DAR" bulgusu, ikili siniflandirmanin
KENDI karar sinirinin (0,5 civari) belki de yanlis yerde oldugunu dusundurebilir — 3-sinifli
deadzone, ORTA (notr) bandi ACIKCA modelin kendisine ogretilmis bir kategori haline getirerek,
bu "asiri-dar-olasilik-dagilimi" sorununu FARKLI bir acidan (esik-sonrasi filtre yerine
sinif-onceden-tanimli) ele alma potansiyeli tasir (bu bir GARANTI DEGIL, denenmesi gereken bir
alternatif tasarimdir).

**YONTEM DETAYI:**
- Model: LightGBM multiclass classifier (`objective=multiclass`, `num_class=3`), Hipotez 1 ile
  AYNI dar hiperparametre araligi.
- Feature seti: Hipotez 1 ile BIREBIR AYNI (~22-28 sutun, Grup B dahil).
- Etiket: 3-sinif — "yukari" (N=16-bar ileri getiri > k_label x ATR14), "asagi" (< -k_label x
  ATR14), "notr" (arada). **k_label=0,3xATR14 BASLANGIC noktasi** (BULGU 10'dan devralinan
  oran, ama N=16 icin YENIDEN HESAPLANMALI — Karar 2'deki sayisal-tutarlilik notu gecerli).
  ATR14 hesabi Wilder-smoothed (v1/Tur 1 ile TUTARLI olmasi icin; Arastirmaci'nin BULGU 10'da
  kullandigi basit-rolling-ortalama ATR14'TEN farkli olabilir, Backtest Muhendisi hangisini
  kullandigini ACIKCA raporlamali).

**GIRIS/CIKIS MEKANIZMASI:** Model her barda 3 sinif olasiligi (P_yukari, P_asagi, P_notr)
uretir. Karar kurali (baslangic onerisi): en yuksek olasilikli sinif "yukari" ise VE
P_yukari>=0,45 (baslangic esigi, Backtest Muhendisi'nce kalibre edilecek) → LONG; "asagi" icin
simetrik → SHORT; "notr" en yuksekse veya hicbir sinif esigi asamiyorsa → ISLEM YOK.

**SL/TP veya RISK YONETIMI:** **k_risk=1,5xATR14 (Hipotez 1 ile AYNI, k_label'dan BAGIMSIZ) —
SL=TP simetrik, N=16 zaman-bariyeri.** RR=1:1, HEDEF_WR=%60,0 (Karar 2'de acikca ayrildigi gibi,
etiket-uretim k'si ile pozisyon-risk k'si FARKLI kavramlardir, KARISTIRILMAMALI). Lot/risk
kurallari Hipotez 1 ile AYNI.

**DOGRULAMA IHTIYACI:** Hipotez 1 ile AYNI protokol (purged walk-forward, test-tek-kullanim,
feature-sizinti listesi). EK olarak: 3-sinifli siniflandirmada basari kriteri NASIL
degerlendirilecegi ONCEDEN (S2 Madde 4 geregi, egitimden ONCE) yazili sabitlenmeli — orn.
"yukari"/"asagi" sinifi P&L'e donusturulurken "notr" tahmini dogru mu yanlis mi sayilacak
(islem acilmadigi icin bu sinifin dogrulugu P&L'i DOGRUDAN ETKILEMEZ, ama modelin genel
ayirt-edicilik gucunu degerlendirmek icin confusion-matrix/multiclass-AUC ayrica raporlanmali).
Hipotez 1 ile Hipotez 2'nin OOS PF/WR/islem-sayisi YAN YANA raporlanmali (feature sabit,
sadece etiket degisti — fark varsa bu ETIKETTEN kaynaklanir).

**RISKLER:**
- Hipotez 1'in tum riskleri (Grup B'nin kirilganlik riski, overfitting, canliya-gecebilirlik,
  S3 governance) GECERLI.
- **Ek risk — iki-k karisikligi:** k_label ve k_risk'in KOD DUZEYINDE karistirilmasi (orn. yanlislikla
  ayni degiskenin kullanilmasi) ciddi bir sessiz-hata riski tasir — Backtest Muhendisi'nin bu
  ikisini AYRI, acikca isimlendirilmis degiskenler olarak tutmasi ZORUNLU, kod incelemesinde
  ozellikle kontrol edilmeli.
- Multiclass model, binary'ye gore biraz daha fazla parametre/karmasiklik tasir (3 sinifin
  olasilik kalibrasyonu binary'den daha az sezgiseldir) — S2'nin "dar arama uzayi" ilkesi
  burada da uygulanmali, multiclass'a GECMENIN KENDISI bir karmasiklik artisi oldugu icin
  hiperparametre aramasinin AYRICA genisletilmemesi onerilir.
- N=16 icin yeniden hesaplanan deadzone dagiliminin (BULGU 10'un N=8 sonuclarindan FARKLI
  cikmasi beklenir) cok dengesiz (orn. "notr" >%40 veya <%5) cikmasi ihtimali VAR — bu durumda
  k_label=0,3 baslangic degeri Backtest Muhendisi tarafindan (S2 Madde 4 geregi, egitimden ONCE,
  test setine BAKMADAN) 0,15-0,5 araliginda ayarlanabilir.

**ONCELIK: 1-Yuksek** — Hipotez 1 ile PARALEL calistirilmasi ONERILIR (gorev tanimi Madde 2'nin
"paralel test" secenegini karsilar, ek hesaplama maliyeti feature-pipeline paylasildigi icin
kucuktur). Sentez agirligi Hipotez 1'dedir (feature-etkisi ilk once izole edilmeli), Hipotez 2
onu TAMAMLAYAN bir ikinci-degisken testidir.

---

### HIPOTEZ 3 — Grup D (Mikro-Yapi) Kisitli/Pilot Testi — 60-90 Gunluk Pencere [OLCEKLENEBILIRLIK PILOTU]

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (LightGBM, binary) + kural-tabanli
on-filtre (hibrit sayilabilir: mikro-yapi feature'i modele girdi olarak verilir, ayri bir
kural katmani DEGILDIR)

**MANTIK:** BULGU 7, bu turun arastirilan TUM feature gruplari (A-D) icinde YON bilgisine dair
TEK somut BUYUK-BUYUKLUKTE gozlemdir (yuksek-imbalance sonrasi -254 puan vs dusuk-imbalance
sonrasi +4 puan medyan) — ANCAK bu, kucuk bir orneklemde (n=251/grup, 20 islem gunu) ve zayif
dogrudan korelasyonla (-0,0315) birlikte gozlenmistir, yani "guclu ama kirilgan" olabilecek tam
da Arastirmaci'nin uyardigi turden bir bulgudur. Bu hipotez, Grup D'yi TAM TARIHE olceklemeden
(Karar 4 geregi), DAHA GENIS ama HALA YONETILEBILIR bir pencerede (son 60-90 islem gunu, ~%1,3
yerine ~%4-6'lik bir orneklem) test ederek hem Acik Soru 5'e (bulgu tekrarlanir mi) kismi bir
yanit uretir hem de bu bilginin GERCEKTEN yon-tahmin degeri tasiyip tasimadigina dair (dusuk
n'e ragmen) bir ilk sinyal saglar.

**YONTEM DETAYI:**
- Model: LightGBM binary classifier, Hipotez 1 ile AYNI feature seti (Grup 1-5 + Grup B) + EK
  olarak Grup D feature'lari (tick-kural-tabanli imbalance orani, tick-sayisi, tick-ici
  mikro-volatilite/mid_ret_std, tick-seviyesi ortalama spread — BULGU 7-9).
- Veri penceresi: SADECE son 60-90 islem gunu (kesin sayi Backtest Muhendisi'nin tick-verisi
  cekme suresine gore belirlenebilir — Riskler Madde 2'deki "20 gun 2,4 saniye surdu" oranindan
  kaba orantiyla 60-90 gun ~7-11 saniye beklenir, PRATIK). Bu, TAM 4,2 yillik egitim/test
  penceresinden TAMAMEN AYRI, kucuk-olcekli bir alt-deney olarak ele alinmalidir — ana Hipotez
  1/2'nin egitim/test bolme mantigina KARISTIRILMAMALI.
- Egitim/test bolme: 60-90 gunluk pencere kucuk oldugu icin purge/embargo ORANTILI kucultulmeli
  (orn. N=16-bar + 1 gunluk embargo, tam-tarihsel Hipotez 1/2'deki gibi haftalik/aylik degil) —
  bu, S2'nin ruhuna (bilgi sizintisini onleme) uygun kalirken orneklem boyutunu asiri
  kismamalidir.

**GIRIS/CIKIS MEKANIZMASI:** Hipotez 1 ile AYNI (olasilik esigi tabanli P(yukari-bariyer-once)).

**SL/TP veya RISK YONETIMI:** Hipotez 1 ile BIREBIR AYNI (k_risk=1,5xATR14, N=16, RR=1:1,
HEDEF_WR=%60,0, ayni lot/risk kurallari) — S1 cost-ratio (15,97x) bu kisitli pencerede de
GECERLI kabul edilir (ayni k, ayni ATR/spread mekanizmasi); Backtest Muhendisi isterse bu
kucuk pencerede spread'in KENDI medyanini da ayrica olcup S1'i teyit edebilir (opsiyonel, ek
saglamlik kontrolu).

**DOGRULAMA IHTIYACI:** Ayni S2 protokolu (purge/embargo ORANTILI, test-tek-kullanim, feature-
sizinti listesi — tick-agregasyonlarinin M15-bucket icinde NEDENSEL/ileri-bakissiz oldugu
ozellikle dogrulanmali, BULGU 7 zaten bunu iddia ediyor ama BAGIMSIZ tekrar kontrol edilmeli).
**Ozel not:** Bu hipotezin kucuk orneklem boyutu (60-90 gun, tahmini ~3.780-5.670 M15-bucket)
nedeniyle istatistiksel guc SINIRLIDIR — Backtest Muhendisi raporunda bu sinirlamayi ACIKCA
belirtmeli, sonuc "KESIN RED/KABUL" degil "bu olcekte ilk gozlem, tam-tarihsel olceklendirme
HALA cozulmemis" seklinde cerceve  lenmelidir.

**RISKLER:**
- **Olceklenebilirlik COZULMEDI (tekrar):** Bu hipotez BASARILI (KABUL) cikSa bile, Grup D'nin
  TAM 4,2 yillik egitim setine nasil tasinacagi (secenek (b) M1-proxy veya baska bir yontem)
  HALA ayri bir tasarim/muhendislik sorunudur — bu hipotez o sorunu COZMEZ, sadece "denemeye
  deger mi" sorusuna kucuk-olcekli bir ilk yanit verir.
- Kucuk n nedeniyle YALANCI-POZITIF riski YUKSEKTIR (60-90 gunluk pencerede rastlantisal bir
  patern "sinyal" gibi gorunebilir) — S2'nin purge/embargo/test-tek-kullanim ilkeleri burada
  DAHA DA kritik onem tasir, kucuk n bu ilkelerin gevsetilmesi icin bir GEREKCE DEGILDIR.
- Gercek order-flow verisi YOK (quote-tick proxy, BULGU 7 SINIR) — canliya gecilse bile bu
  proxy'nin gercek piyasa davranisini ne kadar temsil ettigi BILINMIYOR.
- Canliya-gecebilirlik: tick-verisi tabanli feature'larin MT5 agent icinde GERCEK ZAMANLI
  hesaplanmasi (her M15 bar kapanisinda son 15 dakikalik TUM tick'lerin islenmesi), Hipotez 1/2
  deki OHLC-tabanli feature'lardan DAHA YUKSEK hesaplama/veri-hacmi yuku tasir — bu, KABUL
  edilse bile Risk Analisti asamasinda ayrica sorgulanmali (bu bir hipotezin KABUL edilebilirlik
  kriteri DEGIL ama canli-uygulanabilirlik riskidir).

**ONCELIK: 3-Dusuk** — Hipotez 1/2'nin sonuclari alindiktan SONRA degerlendirilmesi onerilir
(kucuk n, yuksek yalanci-pozitif riski, cozulmemis olceklenebilirlik sorunu nedeniyle ana karar
agirligini TASIMAMALIDIR); Backtest Muhendisi kapasitesi izin veriyorsa Hipotez 1/2 ile PARALEL
de calistirilabilir (bagimsiz/kucuk veri seti oldugu icin ana pipeline'i BLOKE ETMEZ), ama
sonuc SADECE bir on-gozlem olarak yorumlanmali, Tur 2'nin nihai KABUL/RED kararinin tek basina
DAYANAGI OLMAMALIDIR.

---

## BACKTEST MUHENDISI ICIN NOTLAR

1. **S1 (Maliyet-Orani On-Kontrolu):** Hipotez 1/2/3'un UCUNDE de k_risk=1,5xATR14 (Tur 1 ile
   AYNI) kullanildigi icin cost-ratio (15,97x, esigin ALT SINIRINDA) TEKRAR HESAPLANMASI
   GEREKMEZ — Tur 1'deki P90/max-spread stres-testi sonucu (eger yapildiysa) devralinabilir;
   yapilmadiysa bu turde de ZORUNLU (standart Madde 2). Hipotez 3'un kisitli-pencere spread
   olcumu OPSIYONEL bir ek teyit olabilir (yukarida belirtildi).
2. **S2 (Anti-Overfitting Protokolu) — TAMAMI ZORUNLU, ozellikle:**
   - Grup B (pivot/rolling-S-R) icin ileri-bakis kontrolu: gunluk/haftalik pivotun ONCEKI
     TAMAMLANMIS gun/haftadan turetildigi, 20-gunluk rolling-high/low'un SADECE t-oncesi 20 gunu
     kullandigi BAGIMSIZ dogrulanmali.
   - Hipotez 2'deki k_label (0,3xATR14, etiket) ile k_risk (1,5xATR14, SL/TP) AYRI degiskenler
     olarak kod-duzeyinde net ayristirilmali (Karar 2/Hipotez 2 Riskler'de detaylandirildi).
   - Hipotez 3'un tick-agregasyonlarinin M15-bucket icinde nedensel oldugu (ileri-bakis yok)
     dogrulanmali; kisitli-pencere purge/embargo oranli kucultulmeli ama ATLANMAMALI.
3. **DST/Saat-Eslesme:** Feature Grup 4 (oturum/gun-ici) ve Grup B (gunluk/haftalik pivot, GUN/
   HAFTA siniri GMT+3 varsayimina dayanir) kullanildigi icin BAGIMSIZ DST dogrulamasi ZORUNLU
   (`justin_backtest_onkontrol_standardi.md` Madde 1) — onceki turden DEVRALINAMAZ.
4. **SL/TP otomatik tasima YOK:** Bu rapordaki N=16/k_risk=1,5 tasarimi Tur 1 ile AYNI OLARAK
   KORUNMUSTUR (bilinCli bir karar, Karar 3) — ama bu, Backtest Muhendisi'nin yine de KENDI
   basina bu degeri "otomatik tasima" YAPMAMASI gerektigi anlamina gelir; bu raporun Karar 3
   bolumu bunu ACIKCA GEREKCELENDIRMISTIR, sessiz bir varsayim degildir.
5. **Grup D (Hipotez 3) veri penceresi:** 60-90 islem gunu ONERILMISTIR (kesin sayi Backtest
   Muhendisi'nin tick-cekme performansina gore ayarlanabilir) — bu, ana Hipotez 1/2'nin 4,2
   yillik egitim/test setinden TAMAMEN AYRI, bagimsiz kucuk-olcekli bir alt-deneydir, ana
   pipeline ile KARISTIRILMAMALI.
6. **DXY (Grup C) — bu turde KULLANILMIYOR:** Backtest Muhendisi'nin USDX-SEP26 veri-kaynagini
   bu tur icin dogrulama ZORUNLULUGU YOKTUR (Karar 5) — ileride Grup C yeniden gundeme gelirse
   bu dogrulama AYRI bir gorev olarak acilmali.
7. **Kutuphane on-kosulu:** Tur 1'de pandas/lightgbm/scikit-learn/xgboost kurulumu zaten
   dogrulanmisti (Arastirmaci v2 raporu, "Kutuphane durumu guncellemesi") — bu turde ek
   kurulum GEREKMEZ, ama Backtest Muhendisi baslamadan once versiyonlarin (pandas 3.0.3,
   lightgbm 4.6.0, scikit-learn 1.9.0) DEGISMEDIGINI teyit etmelidir.
8. **Basari kriterleri (S2 Madde 4, EGITIMDEN ONCE sabit):** HEDEF_PF=1,5, HEDEF_WR=%60,0
   (RR=1:1), HEDEF_DD=%20 kumulatif (`justin_gecmis_calisma.md`) — Hipotez 1/2/3'un UCUNDE de
   AYNI, RR degismedigi icin. Hipotez 2'nin multiclass ciktisi icin EK olarak (P&L'e donusmeyen
   ama modelin ayirt-ediciligini gosteren) confusion-matrix/multiclass-log-loss de raporlanmali
   (Madde "Hipotez 2 Dogrulama Ihtiyaci" bolumunde belirtildi).
9. **Hipotez 1 vs Hipotez 2 karsilastirmasi (izolasyon amaci):** Raporlarda bu iki hipotezin
   OOS sonuclari (PF, WR, islem sayisi, feature-onem tablosu) YAN YANA sunulmali — amac SADECE
   "hangisi gecti" degil, "etiket degisikligi feature-onem paternini/performansi DEGISTIRDI mi"
   sorusuna cevap vermek (Tur 1'in "barrier genisligi degistirmedi" bulgusuna benzer bir
   karsilastirmali analiz).
10. **Governance (S3, bilgi amacli):** Bu turun Risk Analisti kararlari RED ve Tur 1 ile AYNI
    patern (rassal AUC, ~sifir feature-onem, 0-islem esik-kalibrasyonu) ile sonuclanirsa S3
    sayaci 2/2'ye ulasir — Orkestrator bir sonraki Arastirmaci turunu Ertan onayi olmadan
    baslatmaz. Bu, Backtest Muhendisi/Risk Analisti'nin karar SURECINI degistirmez (kriterlere
    gore objektif KABUL/RED vermeye devam ederler), ama raporlama asamasinda bu esigin
    farkinda olunmasi onerilir.

---

## IZOLASYON TEYIDI

- Bu rapor icin MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json, milagold_trades.json,
  lisa_performance.json, stratejici_gold_gecmis_calisma.md, positions_status.json vb.) okunmadi
  veya referans alinmadi — ne veri/parametre kopyalama ne de format/sablon referansi icin.
- Rapor formati, bu Stratejist'in sistem promptundaki (`stratejici_system_prompt.md`) genel
  sablondan ve Justin'in KENDI onceki (Tur 1/v1) Stratejist raporundan (ayni proje ici
  sureklilik, izolasyon disi) turetildi.
- Calisma yalniz `C:\MilaYatirim\Justin\` dizinindeki girdi dosyalarina (Arastirmaci v2 raporu,
  Tur 1 Stratejist raporu, Tur 1 Risk Analisti hipotez 1/2/3 raporlari, `justin_gecmis_
  calisma.md`, `justin_ml_anti_overfitting_protokolu.md`, `justin_backtest_onkontrol_
  standardi.md`) dayandi; tek dis veri kaynagi (dolayli, Arastirmaci uzerinden) XM/MT5 GOLD
  sembolüdür.
- Bu raporda kullanilan tum kavramlar (LightGBM, ikili/multiclass siniflandirma, pivot/S-R,
  purged walk-forward, ATR) genel/kamuya-acik ML/finans kavramlaridir; MilaGold'a ozel hicbir
  esik/parametre/format bu rapora TASINMADI.

---

## SONUC / ONAY NOKTASI

Bu rapor bir hipotez/tasarim ciktisidir, canli sisteme/hesaba hicbir etkisi YOKTUR (Justin
arastirma/demo-oncesi asamada, gercek hesap yok). STOP-genis/bilgi-notu kategorisi — Ertan
onayi gerekmez; Orkestrator rapor tamamlaninca Telegram bilgi notu + Orkestrator_Loglar kaydi
dusecektir. Bir sonraki adim: **Backtest Muhendisi**, Hipotez 1'i (ana/oncelikli), Hipotez 2'yi
(paralel, etiket-izole karsilastirma) ve olanak varsa Hipotez 3'u (kisitli pilot, dusuk
oncelik) yukaridaki notlar dogrultusunda dogrulamalidir. Bu turun (Tur 2) Risk Analisti karari
RED ve Tur 1 ile AYNI paternde sonuclanirsa, S3 governance esigi (2/2) tetiklenir — Orkestrator
bu durumda Ertan'a somut bir onay sorusu yoneltecektir (bu Stratejist raporunun kapsami
disinda, Orkestrator'un sorumlulugu).
