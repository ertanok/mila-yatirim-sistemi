# BACKTEST MUHENDISI RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile v2 (ML Tam Tur 2)
## HIPOTEZ 2 — LightGBM 3-Sinifli (Deadzone) + Grup B Eklenmis Feature Seti [ETIKET-IZOLE, PARALEL]

Tarih: 12 Temmuz 2026
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md` (Karar 1-5, HIPOTEZ 2 tanimi)
Cerceve dosyalari: `justin_gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md` (S2),
`justin_backtest_onkontrol_standardi.md` (S1 + DST + SL/TP-ozel)
Kod/ciktisi: `backtest_ml_v2_hipotez2.py`, `backtest_ml_v2_hipotez2_output.json`,
`backtest_ml_v2_hipotez2_run.log`

**Bu gorev, Hipotez 1 (v2) icin ayni anda calisan Backtest gorevini BEKLEMEDEN, ONA PARALEL
calistirilmistir** (Stratejist'in onerisi geregi). Rapor yazilma anina kadar Hipotez 1 (v2)'nin
ciktisi da tamamlanmis bulundugu icin Bolum 5'teki karsilastirma tablosu gercek sayilarla
doldurulabilmistir; ancak bu iki calisma BIRBIRINDEN BAGIMSIZ/KOORDINASYONSUZ yurutuldugu icin
Bolum 3'te acikca belirtilen bir feature-seti farkliligi ortaya cikmistir (bkz. Bolum 3, Not).

---

## 1) ON-KONTROL SONUCLARI

### 1.1 Kutuphane On-Kosulu
Hipotez 1 (v2) ile PAYLASILAN kurulum — ayri kurulum YAPILMADI, sadece versiyon teyit edildi:
pandas 3.0.3, lightgbm 4.6.0, scikit-learn 1.9.0 (Orkestrator gorev talimati Madde 1 ile UYUMLU,
degisiklik YOK).

### 1.2 DST / Saat-Eslesme Dogrulamasi
Gorev talimati bu dogrulamanin Hipotez 1 (v2)'den DEVRALINABILECEGINI soyluyordu ("ayni ML/v2
ailesi ici paylasim, H1/H2/H3 kural-tabanli aileden devralma degil"). **Ancak bu script calistigi
anda Hipotez 1 (v2)'nin ciktisi dosya sisteminde HENUZ YOKTU** (paralel calisiyordu) — bu yuzden
"devralindi" diye bir dosya KOPYALANMADI. Bunun yerine, AYNI feature-uretim kodu (hour_sin/cos,
session_asia/london/ny, dow bloklari — v1/Hipotez1 ML ailesiyle BIREBIR AYNI) burada BAGIMSIZ
olarak YENIDEN CALISTIRILDI (ek maliyeti ihmal edilebilir):

- **SONUC: 8/8 bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI** → MT5 sunucusu DST'yi
  TAKIP EDIYOR (sabit GMT+3 DEGIL).
- Bu sonuc, Hipotez 1 (v2)'nin (sonradan tamamlanan) kendi bagimsiz DST taramasiyla (ayni
  8/8 sonuc, `backtest_ml_v2_hipotez1_output.json`) **TUTARLIDIR** — beklenen sonuc, zira ayni
  mekanizma/veri kullanilmistir.

### 1.3 S1 — Maliyet-Orani Stres Testi
k_risk=1,5xATR14 Hipotez 1 ile AYNI oldugu icin (model mimarisinden/etiket semasindan BAGIMSIZ
bir mekanizma) sonuc Hipotez 1 (v2) raporundan DEVRALINABILIRDI; tutarlilik teyidi icin burada da
(BASIT/rolling-ortalama ATR ile, k_risk mekanizmasiyla AYNI ATR tanimi) yeniden hesaplandi:

| Olcum | Deger |
|---|---|
| ATR14(M15) medyan (puan) | 287,43 |
| ATR14(M15) P90 (puan) | 936,79 |
| Spread medyan (puan) | 27,00 |
| Spread P90 (puan) | 36,20 |
| Spread max (puan) | 137,00 |
| Hedef (1,5xATR14 medyan) | 431,14 puan |
| **Oran (medyan spread uzerinden)** | **15,97x** — esik (15,0x) **GECTI** |
| **Oran (P90 stres testi)** | **11,91x** — esik (15,0x) **KAYBEDILDI** |
| Oran (max/ekstrem spread) | 3,15x (bilgi amacli) |

Bu sayilar Hipotez 1 (v2) icin ayrica hesaplanan degerlerle (15,97x / 11,91x) **BIREBIR AYNIDIR**
— beklenen sonuc, cunku k_risk barrier tasarimi (N=16/k=1,5, ATR/spread dagilimi) model
mimarisinden ve etiket semasindan TAMAMEN BAGIMSIZDIR. Gorev talimati geregi P90-stres kaybi ana
testi DURDURMADI, Hipotez 2 asagida yine de calistirilmistir.

---

## 2) k_label YENIDEN-HESAPLAMA SONUCU (N=16, KRITIK NOKTA)

### 2.1 Iki Farkli k — Ayrimin Kod Duzeyinde Uygulanmasi
Stratejist'in ozel uyarisi geregi, script boyunca **iki AYRI, acikca isimlendirilmis ATR/k
degiskeni** kullanildi — hicbir yerde birbirinin yerine KULLANILMADI:

| Degisken | Anlami | Kullanim yeri |
|---|---|---|
| `atr14_m15_simple` + `K_RISK_ATR_MULT=1,5` | GERCEK SL/TP mesafesi | Triple-barrier pozisyon yonetimi (Hipotez 1 ile AYNI) |
| `atr14_m15_wilder` + `K_LABEL_ATR_MULT` (baslangic 0,3) | SADECE 3-sinif egitim etiketi | Model egitim hedefi (yukari/asagi/notr) |

### 2.2 ATR Tutarsizligi — Sessizce Cozulmedi, Acikca Raporlandi
Stratejist notu "ATR14 hesabi Wilder-smoothed (v1/Tur1 ile TUTARLI olmasi icin)" diyordu. Kod
incelemesi yapildi: **v1/Hipotez1(v1 ve v2)'nin FIILI ATR fonksiyonu (`compute_atr_points` /
`rolling_mean_causal`) BASIT rolling-ortalamadir, Wilder DEGILDIR.** Bu, Stratejist notundaki
"Wilder = v1 ile tutarlilik" varsayiminin kod-incelemesiyle DOGRULANAMADIGI, olasi bir
terminoloji karisikligi anlamina gelir. Bu tutarsizlik sessizce cozulmedi:
- **k_risk** icin BASIT ATR kullanilmaya devam edildi (Hipotez 1 ile birebir ayni SL/TP mesafesini
  uretmesi ZORUNLU oldugu icin).
- **k_label** icin Stratejist'in YAZILI talimati harfiyen uygulanarak WILDER-smoothed ATR
  kullanildi.
- Bu, Risk Analisti'ne ACIKCA bildirilmesi gereken bir bulgudur (asagida Bolum 6'da tekrarlanir).

### 2.3 N=16 Dagilimi — TRAINVAL-SADECE Olcum (Test Setine Bakilmadan)
S2 Madde 4 geregi, k_label egitimden ONCE ve TEST SETINE BAKMADAN sabitlenmelidir. Bu yuzden
dagilim SADECE trainval (chronolojik ilk %80) kesitinde olculdu:

| k_label (baslangic) | n (trainval) | yukari_oran | asagi_oran | notr_oran |
|---|---|---|---|---|
| 0,3 x ATR14-Wilder | 78.170 | %46,53 | %42,47 | **%11,00** |

**notr_oran (%11,00) [%5-%40] dengeli araliginin ICINDE** — bu yuzden k_label DEGISTIRILMEDI,
grid-arama (0,15-0,5) TETIKLENMEDI, **K_LABEL_ATR_MULT_FINAL = 0,3** olarak sabitlendi.

**N=8 (Arastirmaci BULGU10, %43,9/%40,5/%15,6) ile BIREBIR KARSILASTIRMA YAPILMAMISTIR** —
gorev talimati/Stratejist Karar 2 geregi bu bir YENIDEN-OLCUMdur, farkli N ve farkli ATR
tanimi (Wilder vs BULGU10'un kendi basit-ortalamasi) kullanir. Niteliksel olarak: N=16'da notr
orani (%11,0) N=8'e (%15,6) gore biraz DUSUK — bu, sabit k_label esiginin daha uzun ufukta
(N=16, 4 saat) fiyatin threshold'u asma olasiligini artirmasiyla (rastgele-yuruyus varyansinin
ufukla buyumesi) NITEL OLARAK tutarlidir, ama resmi bir karsilastirma degildir.

Tum veri (train+test) uzerindeki dagilim (SADECE bilgi amacli, k_label secimine ETKI ETMEDI):
yukari %46,61 / asagi %42,50 / notr %10,89 — trainval-only olcumle NEREDEYSE AYNI (dagilim
kararli, zaman icinde surukleme belirtisi yok).

---

## 3) ANA TEST TASARIMI

- **Model:** LightGBM multiclass (`objective=multiclass, num_class=3`), dar hiperparametre
  araligi (num_leaves=31, max_depth=6, learning_rate=0,05, n_estimators=500 + early-stopping=30,
  min_child_samples=50, subsample/colsample=0,8, reg_lambda=1,0) — Hipotez 1 (v2) ile AYNI
  karmasiklik duzeyi, multiclass'a gecisin kendisi ek karmasiklik oldugu icin arama
  GENISLETILMEDI (S2 geregi).
- **Feature seti: 27 sutun** — Grup 1-5 (23 sutun, v1/Hipotez1 ile BIREBIR AYNI) + Grup B (4 YENI
  sutun: `dist_daily_pivot_pts`, `dist_weekly_pivot_pts`, `dist_roll20_high_pts`,
  `dist_roll20_low_pts`).
  - **ONEMLI KARSILASTIRILABILIRLIK NOTU:** Hipotez 1 (v2), paralel/bagimsiz calistigi icin
    **29 sutunla** tamamlandi (Grup B'ye ek olarak `dist_daily_r1/s1`e karsilik gelen degil, ama
    `near_roll20_high_flag`/`near_roll20_low_flag` adinda 2 EK causal-yakinlik-bayragi icerir).
    Bu script (Hipotez 2) tasarim asamasinda bu 2 bayragi **BILINCLI OLARAK DAHIL ETMEDI** — Grup
    B icin sadece 4 ham mesafe sutunu kullanildi, ek bir "yakinlik" bayragi eklenmedi (basit/net
    kalmasi tercih edildi). **Sonuc: Hipotez 1 (29 sutun) ile Hipotez 2 (27 sutun) feature seti
    Stratejist'in istedigi gibi BIREBIR AYNI DEGILDIR** — bu, gorevin "Hipotez 1'in ciktisini
    BEKLEMEDEN paralel calis" talimatinin dogal bir sonucudur (feature-uretim kodu, H1 (v2)
    script'i henuz yazilmamisken bagimsiz olarak turetildi). Karsilastirma tablosunda
    (Bolum 5) bu fark ACIKCA isaretlenmistir; "etiket etkisi izole edildi mi" sorusuna verilecek
    yanit bu 2-sutunluk farktan dolayi %100 saf DEGILDIR, ama HAKIM/kacinilmaz feature ailesi
    (Grup1-5 + 4 pivot/S-R mesafesi) ORTAKTIR.
- **Etiket:** 3-sinif deadzone, N=16, k_label=0,3xATR14-Wilder (Bolum 2).
- **Karar kurali:** argmax(P)==yukari VE P_yukari>=esik_yukari → LONG; argmax(P)==asagi VE
  P_asagi>=esik_asagi → SHORT; aksi halde (argmax==notr VEYA esik asilmadi) → ISLEM YOK.
- **SL/TP/Risk:** k_risk=1,5xATR14 (BASIT/rolling-ortalama), N=16 zaman-bariyeri, RR=1:1 — Hipotez
  1 ile BIREBIR AYNI, k_label'dan tamamen BAGIMSIZ. Lot/risk: `justin_gecmis_calisma.md`
  (kasa=2.000 USD, 0,01 lot sabit).
- **Veri bolumu:** Toplam 99.999 M15 bar (2022-04-18 → 2026-07-10). Trainval 78.155 ornek
  (2022-04-18 → 2025-09-03), embargo 24 bar (6 saat), Test 19.960 ornek (2025-09-04 → 2026-07-10,
  TEK KEZ kullanildi). Purge: egitim orneklerinin etiket penceresi (i+N) trainval sinirini
  ASMAYACAK sekilde kisitlandi.
- **Purged/embargolu walk-forward:** 5 esit segment (4 fold), her fold'da SADECE o ana kadarki
  trainval verisiyle egitim; esik kalibrasyonu SADECE out-of-fold (OOF) tahminleriyle yapildi,
  test setine bu asamada KESINLIKLE BAKILMADI.

### Feature-Sizinti Kontrol Listesi (S2 Madde 3) — ozet
1. Ileri-bakan bilgi: HAYIR (tum feature'lar nedensel/rolling; H1/H4 hizalamasi bir onceki
   KAPANMIS bar).
2. Label-sizintisi: HAYIR (k_label sadece bar i ATR'si + i+16 kapanisi; k_risk barrier sadece
   bar i ATR'si + i+1..i+16 yolu; hicbir feature bu ileri veriyi kullanmaz).
3. Normalizasyon: SADECE fold/final TRAIN kesitinden (ortalama/std), test'e bu istatistikler
   uygulandi.
4. DST: GECTI (Bolum 1.2).
5. MACD ham deger (isaret degil) — v1 ile AYNI, BULGU6 SINIR geregi.
6. **Grup B gunluk/haftalik pivot:** EVET, `.shift(1)` ile bir SONRAKI gune/haftaya atanir; bugunun
   KENDI (tamamlanmamis) OHLC'si ASLA kullanilmaz.
7. **Grup B roll20 high/low:** EVET, GUNLUK seri uzerinde `.rolling(20).shift(1)` — sadece ONCEKI
   20 TAMAMLANMIS gunu kullanir. Merge sonrasi bar sayisinin degismedigi (`assert len(df_b)==n`)
   ayrica dogrulandi.

---

## 4) SONUCLAR

### 4.1 Purged Walk-Forward (Trainval Ici, OOF)

| Fold | Train n | Val n | Val multiclass-logloss | Val accuracy |
|---|---|---|---|---|
| 1 | 14.155 | 15.961 | 0,9715 | 0,4356 |
| 2 | 30.155 | 15.961 | 0,9651 | 0,4530 |
| 3 | 46.155 | 15.961 | 0,9504 | 0,4733 |
| 4 | 62.155 | 15.961 | 0,9523 | 0,4755 |

Ozet: logloss ortalama 0,9598 (std 0,0088), accuracy ortalama 0,4594 (std 0,0163). Rastgele-taban
referansi: 3 sinif icin rastgele tahmin accuracy~0,333, logloss~ln(3)=1,099 (sinif dagilimi
esitsiz oldugu icin taban biraz farkli olabilir). **Fold'lar arasi VARYANS DUSUK** (accuracy
std=0,016) — bu, model DAVRANISININ zaman icinde nispeten ISTIKRARLI oldugunu gosterir (iyi VEYA
kotu bir davranista ISRAR ediyor, Bolum 4.3'e bakiniz).

### 4.2 Esik Kalibrasyonu (OOF, test setine bakilmadan)

| esik_yukari/asagi | long_n | long_WR-proxy | short_n | short_WR-proxy | toplam_n | kapsama |
|---|---|---|---|---|---|---|
| 0,40 | 31.772 | 0,4886 | 32.066 | 0,4303 | 63.838 | %99,99 |
| 0,45 | 27.081 | 0,4899 | 28.024 | 0,4370 | 55.105 | %86,31 |
| **0,50** | **3.476** | **0,4974** | **5.264** | **0,4438** | 8.740 | %13,69 |
| 0,55 | 405 | 0,5432 | 426 | 0,3756 | 831 | %1,30 |

Secim kurali (MIN_SAMPLE>=30 gecen taraflarin ortalama precision'i) **0,50/0,50** esigini secti.
**DIKKAT:** Hicbir esik adayinda long/short WR-proxy %50'yi (rastgele-yuruyus taban cizgisi)
anlamli sekilde ASMADI — en yuksek esikte (0,55) bile short-proxy (0,3756) rastgeleden DUSUK.
Bu, esik-kalibrasyonunun kendisinin bir "gercek edge" bulmadigini, sadece en az kotu adayi
sectigini gosterir.

### 4.3 Final Model — Ic-Validasyon vs Test (Overfitting Kontrolu)

| Kume | n | multiclass-logloss | accuracy |
|---|---|---|---|
| Ic-validasyon (final_innerval) | 15.961 | 0,9523 | 0,4755 |
| **TEST (tek-kez)** | 19.960 | **0,9578** | **0,4218** |

Ic-validasyon ile test arasinda logloss farki KUCUK (0,9523→0,9578) — **OVERFITTING_RISKI
bayrak ANLAMINDA DUSUK/YOK** (klasik "IS >> OOS" patern gozlenmedi). Ancak accuracy'de gozle
gorulur bir dusus var (0,4755→0,4218) — bu, modelin test doneminde (2025-09→2026-07) sinif
sinirlarina daha az uyumlu oldugunu, ancak agir bir asiri-uyumdan ziyade **rejim/donem
farkliligina** isaret edebilecegini gosterir (kesin ayrim icin ek analiz gerekir, bu raporun
kapsami disinda).

**Confusion Matrix (TEST, satir=gercek, sutun=tahmin, sira=[asagi, notr, yukari]):**

| Gercek \ Tahmin | asagi | notr | yukari |
|---|---|---|---|
| **asagi** (n=8.495) | 2.140 | 0 | 6.355 |
| **notr** (n=2.093) | 605 | 0 | 1.488 |
| **yukari** (n=9.372) | 3.093 | 0 | 6.279 |

**KRITIK BULGU (Orkestrator Madde 7 geregi ozellikle raporlanmali):** Modelin argmax tahmini
**HICBIR test barinda "notr" sinifini SECMEDI** (orta sutun tamamen sifir). Model, egitimde
notr sinifini (%11 agirlikla) gormesine ragmen, TEST setinde fiilen 2 sinifli (yukari/asagi)
bir siniflandiriciya COKMUS durumdadir — bu, `p_notr` olasiliginin dagilimindan da dogrulanir:
`p_notr_mean=0,1148, std=0,0072` (neredeyse SABIT, bara gore neredeyse hic degismiyor; model
notr'u "ayirt etmiyor", sadece sabit bir taban-olasilik atiyor).

**Naif taban cizgisi karsilastirmasi (ONEMLI):** Test setinde en buyuk sinif "yukari"dir
(9.372/19.960 = %46,96). Yani "HER ZAMAN yukari tahmin et" seklindeki TRIVIAL bir siniflandirici
%46,96 accuracy verirdi — modelin fiili test accuracy'si (%42,18) **BU TRIVIAL TABAN CIZGISININ
ALTINDADIR.** Bu, modelin sadece "notr'u kacirmakla" kalmadigini, GENEL siniflandirma gucunun
en basit sabit-tahmin stratejisinden bile ZAYIF oldugunu gosterir — Tur 1'in "rassal-seviye
AUC" bulgusuyla NITELIKSEL OLARAK tutarli bir sonuc (farkli metrikle, ayni yonde).

Multiclass log-loss (0,9578) rastgele-taban (ln(3)=1,099)'dan DUSUK gorunse de, bu ozellikle
sinif dagiliminin esit-olmamasindan (yukari/asagi ~%46/%42, notr ~%11) kaynaklanir — sabit/
"her zaman ayni 3 olasiligi ver" (marjinal dagilim) bir tahminci bile logloss'u rastgele-esit-
dagilimdan DUSUK yapar; bu yuzden logloss'un TEK BASINA "model ogreniyor" anlamina GELMEDIGI
acikca belirtilir (confusion matrix / accuracy-vs-trivial-taban karsilastirmasi cok daha
ACIKLAYICI, yukarida verildi).

### 4.4 Test Trade Simulasyonu (Tick-Bazli Gercek Maliyet)

Karar kuralinin (argmax + esik 0,50/0,50) test setinde tetikledigi bar sayisi cok DUSUKTU:
sadece 46 bar argmax==yukari VE P_yukari>=0,50 kosulunu sagladi; **argmax==asagi VE
P_asagi>=0,50 kosulunu saglayan SIFIR bar** vardi (`esik_asagi_asan_VE_argmax_asagi_bar_sayisi:
0`) — yani SHORT sinyali HIC uretilmedi.

31 sinyal N=16-bar cakisma nedeniyle atlandi (bir onceki islem hala acikken yeni sinyal
gormezden gelinir), geriye **15 PRIMARY islem** kaldi (hepsi LONG):

| Metrik | Deger |
|---|---|
| Toplam islem | **15** (n<MIN_SAMPLE=30 — **YETERSIZ ORNEKLEM UYARISI**) |
| Win rate | %66,67 |
| **Profit Factor** | **0,781** (HEDEF_PF=1,5 KARSILANMADI) |
| Net kar/zarar | -3.256,54 puan / **-32,57 USD** (0,01 lot) |
| Max drawdown | %-4,762 (kasa=2.000 USD referansi) |
| Ortalama risk/kasa | %0,924 (RISK_PCT_CAP %1 SINIRI ICINDE) |
| Ortalama toplam maliyet | 79,4 puan/islem |
| Ortalama ATR (giris ani) | 1.231,96 puan |
| Tick lookup | 15 cagri, 0 hit (cache), 0 miss — tum kotasyonlar basariyla alindi |

**SHORT islem: 0 adet** (esik hicbir test barinda asagi-argmax + P_asagi>=0,50 kosulunu
saglamadi). LONG taraf da n=15 ile MIN_SAMPLE esiginin ALTINDA — bu sonuc **yorumlanabilir ama
TEK BASINA karar dayanagi OLAMAZ** (Ortak Ilkeler, minimum orneklem uyarisi).

---

## 5) HIPOTEZ 1 vs HIPOTEZ 2 KARSILASTIRMA TABLOSU

*(Hipotez 1 (v2) verileri `backtest_ml_v2_hipotez1_output.json`/`_run.log`'dan alinmistir — bu
Backtest Muhendisi'nin KENDI paralel calismasi, MilaGold degil, izolasyon disi bir referans
degildir.)*

| Boyut | Hipotez 1 (v2) — Ikili | Hipotez 2 (v2) — 3-Sinifli (bu rapor) |
|---|---|---|
| Etiket | Barrier-touch ikili (TP-once/SL-once) | 3-sinif deadzone (k_label=0,3xATR14-Wilder, N=16) |
| Feature sutun sayisi | **29** (Grup1-5 + 6 Grup B: 4 mesafe + 2 causal-yakinlik-bayragi) | **27** (Grup1-5 + 4 Grup B mesafe, yakinlik-bayragi YOK) |
| **Feature seti birebir ayni mi?** | **HAYIR** — bkz. Bolum 3 Not (paralel/bagimsiz gelistirme sonucu 2 sutunluk fark) | |
| Walk-forward OOS metrik | AUC ortalama **0,5098** (std 0,0142) — rastgele-seviye | logloss ortalama 0,9598, accuracy ortalama **0,4594** |
| Esik kalibrasyonu (secilen) | LONG>=0,575 / SHORT<=0,425 | YUKARI>=0,50 / ASAGI>=0,50 |
| Final ic-validasyon performansi | AUC 0,5300 | logloss 0,9523 / accuracy 0,4755 |
| **TEST performansi (tek-kez)** | **AUC 0,5190** (rastgele-seviye) | **logloss 0,9578 / accuracy 0,4218** (TRIVIAL-taban-cizgisinin (0,4696) ALTINDA) |
| Test confusion/notr davranisi | (Ikili model, notr kavramı yok) | **"notr" argmax'ta HICBIR ZAMAN secilmedi** — model fiilen 2-sinifli davraniyor |
| Test'te tetiklenen islem sayisi | **0 (SIFIR)** — esik hicbir test barinda asilmadi | **15 (LONG), 0 SHORT** |
| PRIMARY Profit Factor | Hesaplanamadi (n=0) | **0,781** (HEDEF 1,5 KARSILANMADI) |
| PRIMARY Win Rate | Hesaplanamadi (n=0) | %66,67 (n=15, YETERSIZ ORNEKLEM) |
| Final model feature-onem (top-3, split-sayisi) | dist_weekly_pivot_pts(18), atr14_h1_aligned(15), dist_roll20_low_pts(8) — **TOPLAM split sayisi COK DUSUK** (sig/basit agac, Tur1 paterniyle tutarli) | dist_roll20_low_pts(79), dist_roll20_high_pts(53), dist_weekly_pivot_pts(47) — **Grup B feature'lari ACIKCA en yuksek siralarda, split sayilari Hipotez1'e gore BELIRGIN DAHA YUKSEK** |
| S1 (cost-ratio) | 15,97x medyan (GECTI) / 11,91x P90 (KAYBEDILDI) | **AYNI** (15,97x / 11,91x) — beklenen, mekanizma ortak |
| DST | GECTI (8/8) | GECTI (8/8) — tutarli |

**"Etiket degisikligi feature-onem paternini/performansi DEGISTIRDI mi?" sorusuna yanit
(gorev talimati Madde 9):**
- **Feature-onem paterni ACIKCA DEGISTI:** Hipotez 1'in (ikili) modeli SIG bir agac kaldi
  (toplam split sayisi dusuk, Tur1'in "best_iteration=1" paternine benzer bir yetersiz-ogrenme
  isareti), Hipotez 2'nin (3-sinifli) modeli ise GOZLE GORULUR sekilde DAHA FAZLA split
  kullandi ve Grup B (pivot/S-R) feature'lari en yuksek 3 sirada yer aldi. **3-sinifli deadzone
  etiketi, modelin en azindan "bir seyler ogrenmesini" (train icinde split kullanmasini) TESVIK
  ETTI** — ancak bu, Bolum 4.3'te gosterildigi gibi TEST performansina (trivial tabanin ALTINDA
  kalan accuracy, hicbir esik adayinda %50 WR-proxy'yi asamayan LONG/SHORT) **OLUMLU sekilde
  YANSIMADI.**
- **P&L performansi ACISINDAN:** Hipotez 1 HICBIR islem uretemedi (n=0, degerlendirilemez);
  Hipotez 2 cok kucuk bir ornekte (n=15) PF=0,781 uretti — HEDEF_PF=1,5'in ALTINDA. Yani
  **HICBIRI HEDEFI KARSILAMADI**, ama Hipotez 2 en azindan test edilebilir (n>0) bir islem akisi
  urettigi icin, "modelin karar-uretme kapasitesi" acisindan Hipotez 1'den BIRAZ daha ileridedir
  — bu, "daha iyi bir STRATEJI" anlamina GELMEZ, sadece "esik-kalibrasyonunun daha az asiri-dar
  bir olasilik dagilimiyla calistigi" anlamina gelir (Stratejist'in Hipotez 2 MANTIK bolumunde
  one surdugu "asiri-dar-olasilik-dagilimi sorununu farkli bir acidan ele alma" hipotezi KISMEN
  DOGRULANDI — islem SIFIRDAN 15'e cikti — ama sonuc HALA REDdir, cunku PF hedefin altinda ve
  orneklem yetersizdir).

---

## 6) RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — Hipotez 2 (LightGBM 3-Sinifli/Deadzone, Grup B) — ML/Feature-Tabanli — 12 Temmuz 2026

Egitim / Walk-Forward (OOF, trainval):
  logloss ortalama 0,9598 (std 0,0088), accuracy ortalama 0,4594 (std 0,0163)
  Esik-kalibrasyonu: hicbir aday adayinda long/short WR-proxy anlamli sekilde %50 rastgele-tabanini asmadi

Gorulmemis Veri (TEST, tek-kez):
  multiclass-logloss 0,9578, accuracy 0,4218 — TRIVIAL "her-zaman-yukari-tahmin-et" tabaninin (0,4696) ALTINDA
  Confusion matrix: "notr" sinifi argmax'ta HICBIR ZAMAN secilmedi (model fiilen 2-sinifli davraniyor)
  Trade sim: 15 islem (hepsi LONG, SHORT=0), WR %66,67, PF 0,781 (HEDEF 1,5 KARSILANMADI), net -32,57 USD, DD %-4,76

Dikkat noktalari:
  - ORNEKLEM YETERSIZ: 15 islem < MIN_SAMPLE(30) - PF/WR tek basina karar dayanagi OLAMAZ
  - Model test performansi TRIVIAL taban cizgisinin ALTINDA - Tur 1'in "rassal-seviye" bulgusuyla NITELIKSEL tutarli
  - Feature-seti Hipotez 1 (v2) ile BIREBIR AYNI DEGIL (27 vs 29 sutun, paralel/bagimsiz gelistirme sonucu) - karsilastirma %100 saf izole degil
  - ATR TUTARSIZLIGI: Stratejist notu "Wilder=v1 ile tutarli" dedi ama v1'in fiili kodu BASIT ATR kullaniyor - k_risk BASIT, k_label WILDER olarak AYRI tutuldu, bu KENDI BASINA bir karar/varsayimdir, Risk Analisti'nin degerlendirmesi gerekir
  - S1 P90-stres-testi KAYBEDILDI (11,91x < 15,0x esigi) - Hipotez 1 ile AYNI, model-secimden bagimsiz bir yapisal risk
  - Feature-onem paterni Hipotez1'e gore degisti (Grup B feature'lari daha yuksek split-sayisi aldi) ama bu P&L'e YANSIMADI
  - OVERFITTING: ic-validasyon vs test logloss farki KUCUK (IS>>OOS patern YOK) - ama accuracy dususu (0,4755->0,4218) rejim-farkliligina isaret edebilir

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez2_20260712.md
Ham veri/script: C:\MilaYatirim\Justin\backtest_ml_v2_hipotez2.py, backtest_ml_v2_hipotez2_output.json
```

---

## 7) IZOLASYON NOTU

- Bu script/rapor icin MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md,
  positions_status.json vb.) okunmadi veya referans alinmadi — ne veri/parametre kopyalama ne de
  format/sablon referansi icin.
  Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi (veri MT5'ten dogrudan, GOLD sembolu).
- Yapi referansi SADECE Justin'in KENDI onceki turlerinden alindi (`backtest_ml_v1_hipotez1.py`,
  `backtest_ml_v1_hipotez2.py`, `research_ml_gold_scalping_m15_v2.py`) — izolasyon disi (ayni
  proje ici sureklilik).
- Kullanilan tum kavramlar (LightGBM multiclass, triple-barrier, pivot/S-R, purged walk-forward,
  Wilder ATR, confusion matrix, log-loss) genel/kamuya-acik ML/finans kavramlaridir; MilaGold'a
  ozel hicbir esik/parametre/format bu rapora TASINMADI.

---

## 8) ONAY NOKTASI

Bu rapor bir dogrulama/backtest ciktisidir — salt-okunur/analitik/offline calisma, canli
sisteme/hesaba hicbir etkisi YOKTUR (Justin arastirma/demo-oncesi asamada, gercek hesap yok).
4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil,
etki alani dar (yalniz Justin klasoru) → **STOP-genis/bilgi-notu kategorisi, Ertan onayi
gerekmez.** Rapor tamamlaninca Orkestrator tarafindan Ertan'a Telegram bilgi notu +
Orkestrator_Loglar kaydi dusulecektir.

**Bir sonraki adim:** Risk Analisti, bu raporu Hipotez 1 (v2) raporuyla BIRLIKTE (S3 governance
notu geregi, tek bir degerlendirme turunda) inceleyip nihai KABUL/RED kararini verecektir. Bu
Backtest Muhendisi raporu bir yargida BULUNMAZ (KABUL/RED etiketlemez) — yalniz sayisal
bulgulari, iki hipotezin BIRBIRINDEN NASIL FARKLI/BENZER ciktigini ve tespit edilen tum
tutarsizliklari (feature-seti farki, ATR tanimi farki, orneklem yetersizligi) SEFFAF sekilde
raporlar.
