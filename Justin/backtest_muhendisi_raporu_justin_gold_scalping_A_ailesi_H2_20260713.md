# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following) — HIPOTEZ H2

Hipotez adi: "Genis-Orneklem M15-Giris" (H1/M30 Yapisal Kanal + M15 Giris-Zamanlama, Simetrik Iki Yon)
Yaklasim turu: Kural-tabanli
Proje: Justin (Gold Scalping alt-hedefi) — A Ailesi, Tam Tur 1
Test tarihi: 2026-07-13
Girdi: `stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md` (H2 bolumu + Backtest
Muhendisi'ne Devir Notlari 1-8)
Gorev: `gorev_backtest_muhendisi_justin_gold_scalping_A_ailesi_H2.md`
Calisma dizini: yalniz `C:\MilaYatirim\Justin\`
Kod: `backtest_A_ailesi_H2.py`
Ham cikti: `backtest_A_ailesi_H2_output.json`, tam islem logu: `backtest_A_ailesi_H2_islem_logu_tam.csv`

Referans (kalici on-kontrol standardi): `justin_backtest_onkontrol_standardi.md`
Referans (kasa/risk/lot): `justin_gecmis_calisma.md`

**"Onceki-Tur-Ayrisma-Teyidi": N/A** — bu, A ailesinin ilk tam turudur (Tam Tur 1); Ertan'in
Cevap 1 kurali (varyasyon-cesitliligi teyidi) Tur 2'den itibaren gecerlidir
(`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`).

---

## 0) OZET (en onemli bulgu, once)

H2, on-kontrolleri (DST + S1 gercek-maliyet-orani) GECTI ve ana teste ALINDI. Ancak ana test
sonucu **RED**dir: Train/Validation/Test'in **UCUNDE DE Profit Factor 1'in ALTINDA** (Train
0,7715, Validation 0,9205, Test 0,9197 — Test seti TEK KEZ kullanildi), win rate ~%22,6-24,5
araliginda cok dusuk (RR asimetrisiyle kismen telafi edilse de yetersiz), ve **operasyonel
%20 kumulatif DD-stop esigi** (kasa 1.600 USD) gercek-zamanli/restart-simulasyonunda **~4,3
yillik test donemi boyunca 120 KEZ tetiklenirdi** (ilkini sadece **39. islemde**, ilk 3 gun
icinde). Bu, mevcut haliyle H2'nin gunluk pipeline/operasyonel cerceve altinda pratikte
surekli STOP-START (Ertan onayi gerektiren) dongusune girecegi anlamina gelir.

Onemli bir metodolojik bulgu: Stratejist'in devrettigi "4,4-10,3 saat tutma suresi"
beklentisi bir PROXY olcumdu (N-bar-ileri fiyat hareketinin S1-esigine ulasma suresi, SL
UYGULANMADAN). **Gercek trade simulasyonunda (SL/TP uygulanarak) medyan tutma suresi 0,5
saattir** — yani H2, Ertan'in "dakikalar-birkac saat" scalping tanimina (Cevap 3) BEKLENENDEN
CIDDI OLCUDE DAHA UYUMLU cikmistir (scalping-tanimi gerilimi bu hipotez icin PRATIKTE
COZULMUSTUR) — ama bu, sonucu KURTARMAZ: kisa tutma suresi, cogunlukla hizli SL-vurmasindan
(SL-cikislarin medyan tutma suresi 0,25 saat) kaynaklanmaktadir, karligin degil.

**Bu bir "A ailesi olu" sonucu DEGILDIR** — Stratejist'in atif-netligi notu geregi, bu sonuc
"scalping-tanimi geriliminin cozulmus olmasina RAGMEN edge yetersizligi/SL-butcesi-vs-
volatilite-gurultusu sorunu" olarak okunmalidir (asagida Bolum 6/7'de detaylandirilmistir).

---

## 1) ON-KONTROL SONUCLARI

### 1.1 Madde 1 — DST/Saat-Esleme BAGIMSIZ Dogrulamasi

H1'den DEVRALINMADI — bu turde H1 VE M15 verisi uzerinde AYRI/BAGIMSIZ olarak kosturuldu
(gorev madde 1a geregi, M15 zaman-projeksiyonunun bu dogrulamadan ozellikle etkilenebilecegi
notuyla).

**(a) Canli-an capraz kontrol:** epoch-UTC-okuma = 2026-07-13 18:28:30, VPS-yerel-simdi =
2026-07-13 18:28:30,79 → fark 0,79 saniye. VPS'in yerel isletim-sistemi saati **sabit UTC+3**
(Turkiye/TST, 2016'dan beri DST uygulamiyor) — bu, MT5 SUNUCUSUNUN da sabit oldugu anlamina
GELMEZ, asagidaki hafta-sonu-gecis testi sunucu davranisini ayrica olcer.

**(b) Hafta-sonu-gecis (DST) testi, H1 VE M15'te BAGIMSIZ tekrarlandi:**

| Gecis tarihi | H1: once→sonra Cuma kapanis saati | M15: once→sonra Cuma kapanis saati | Kayma? |
|---|---|---|---|
| 2025-03-30 | 22→23 | 22→23 | **EVET** (H1 ve M15'te AYNI) |
| 2025-10-26 | 23→22/23 (karisik) | 23→22/23 (karisik) | Belirsiz (ABD-DST farkli tarihte gectigi icin) |
| 2026-03-29 | 22→23 | 22→23 | **EVET** (H1 ve M15'te AYNI) |

**SONUC:** MT5/XM sunucusu AB/Kibris DST takvimini izliyor (yaz GMT+3, kis muhtemelen GMT+2)
— onceki turlerde (Hipotez 1/2/3) dogrulanan bulguyla TUTARLI, bu turde H1 VE M15'te AYRI
AYRI (H1'den devralinmadan) bagimsiz dogrulandi. **Sonuc:** kis aylarinda M15
kanal-projeksiyonu fiilen 1 saat kaymis olabilir — bu dogrulanmamis belirsizlik Risk
Analisti'ne asagida ayrica iletiliyor.

### 1.2 Madde 2 — S1 Maliyet-Orani, GERCEK SL/TP Mesafeleriyle (proxy DEGIL)

Arastirmaci'nin proxy hesaplamasi (N-bar-ileri medyan hareket) burada KULLANILMADI; bunun
yerine Stratejist'in ATR14_M15-bazli SL/TP CERCEVESI icin somut SL/TP carpan adaylari
tanimlanip HER birinin GERCEK nokta-mesafesi/maliyet orani hesaplandi.

Global M15 maliyet (bagimsiz yeniden hesaplandi, Arastirmaci'nin ayni formulu — spread_medyan
+ 0,037×ATR14_medyan — ile, ama KENDI veri cekimimizle):

| Metrik | Deger |
|---|---|
| Spread medyan (pts) | 27,00 |
| ATR14_M15 medyan (pts) | 287,71 |
| Slipaj tahmini (0,037×ATR) | 10,65 |
| **TOPLAM MALIYET** | **37,65 pts** |

TP-carpani on-kontrolu (SL grid: 0,5/0,75/1,0×ATR; TP grid: 1,0/1,5/2,0/2,5/3,0/4,0×ATR —
temsili deger = carpan × ATR14_M15 medyani):

| TP carpani | Temsili TP (pts) | Maliyet orani | >=15x? | >=20x? |
|---|---|---|---|---|
| 1,0× | 287,7 | 7,64x | KALDI | KALDI |
| 1,5× | 431,6 | 11,46x | KALDI | KALDI |
| **2,0×** | 575,4 | 15,29x | **GECTI** | KALDI |
| **2,5×** | 719,3 | 19,11x | **GECTI** | KALDI |
| **3,0×** | 863,1 | 22,93x | **GECTI** | **GECTI** |
| **4,0×** | 1150,9 | 30,57x | **GECTI** | **GECTI** |

**Karar: ANA TESTE GECILEBILIR** — TP>=2,0×ATR14_M15 secenekleri >=15x esigini gecti (TP=1,0×
ve 1,5× on-kontrolde ELENDI, ana teste/walk-forward'a hic SOKULMADI). SL grid'i (0,5/0,75/1,0×)
oldugu gibi (maliyet-orani SL'e degil TP/hedefe uygulanir, Madde 2 tanimi geregi) tum
kombinasyonlarda tarandi.

### 1.3 SL/TP — H2'ye Ozel Kalibrasyon (otomatik tasima YOK)

`justin_backtest_onkontrol_standardi.md` Madde 3 geregi, H1'den (veya baska bir onceki
hipotezden) hicbir SL/TP degeri devralinmadi. Asagida (Bolum 3.2) H2'ye ozel, Train/Validation
verisiyle kalibre edilen SL=0,75×ATR14_M15 / TP=2,5×ATR14_M15 kombinasyonu SIFIRDAN secildi.

---

## 2) LOOK-AHEAD BIAS DOGRULAMASI

**Sorun (Stratejist'in devir notu 2, H1 ile ayni gerekce):** Pivot/swing tanimi (N=5 fraktal,
sol+sag pencereli) ILERI-BAKISLIDIR — bar `i`'nin swing oldugu ancak `i+5` barinda (5 bar sag
penceresi tamamlaninca) KESINLESIR. Bu, kanalin "3. dokunus" ile GECERLI sayildigi an
(`confirm_idx`) da dahil olmak uzere, kanalin butun anatomisinin (anchor, second, ara-
dokunuslar, confirm) gercek-zamanli bilinemeyecek kadar erken bir zaman damgasi tasimasi
riskini yaratir.

**Uygulanan duzeltme (bu script, `detect_channels()` fonksiyonu):**
- `confirmed_active_idx = confirm_idx + 5` hesaplanir — kanal SADECE bu barda ve sonrasinda
  "bilinir/kullanilabilir" sayilir.
- **EMA50/EMA200 ve MACD teyidi, `confirm_idx`'TE DEGIL, `confirmed_active_idx`'TE
  degerlendirilir** — cunku gercek-zamanli karar ani budur (confirm_idx henuz "bilinmiyor").
  Bu, Arastirmaci'nin on-tarama scriptinden (EMA/MACD'yi confirm_idx'te kontrol eden)
  BILINCLI bir sapmadir ve bu look-ahead duzeltmesinin dogrudan bir sonucudur.
- **`break_idx` (kirilim) duzeltme GEREKTIRMEZ** — kirilim tespiti SADECE o ana kadarki
  KAPANIS fiyatlarini tarar (ileri-bakisli swing bilgisine ihtiyac duymaz), bu nedenle
  gercek-zamanli olarak zaten GUVENLIDIR ve degistirilmeden kullanildi.
- M15 giris-projeksiyonu, kanalin **`confirmed_active_time` → `break_known_time`**
  araligiyla SINIRLANDI (break_known_time = break_idx barinin KAPANIS ani, yani break_idx
  barinin acilis zamanindan bar-suresi kadar SONRASI — kirilimin GERCEKTEN bilindigi an).

**Ek yurutme-mekanigi duzeltmesi (bu script'in ekledigi, sistem promptunun Ortak Ilkeler
bolumundeki "giris bir sonraki bar acilisinda gerceklesir" standardi geregi):** Stratejist'in
tanimi "tetigi olusturan barin KAPANISINDA giris" seklindeydi — bu, sifir-gecikme/ayni-anda-
islem varsayimidir ve teknik olarak bir look-ahead riski tasir (o barin kapanis fiyatinda
islem yapabilmek icin barin kapanmasini beklemeniz gerekir, ama o ANDA islem gerceklesmez).
Bu script, SL/TP/filtre PARAMETRELERINE DOKUNMADAN, sadece YURUTME anini bir bar ileri
kaydirdi: giris = tetik barindan (dokunus-barinin bir sonrasi) **BIR SONRAKI barin ACILISI**
(`exec_idx = touch_idx + 2`). Yurutme aninda kanal zaten kirilmis bilgisi varsa (`exec_idx`
zamani `break_known_time`'i gecmisse) giris GECERSIZ SAYILIR (bu turde 0 kez gerceklesti —
bkz. Bolum 4, "kanal_kirilmis_giris_reddi": 0/0/0).

**Kantitatif etki (kanal sayilarindaki degisim):** Look-ahead-duzeltmeli EMA/MACD-teyit-
zamanlamasi, Arastirmaci'nin ham on-tarama sonuclarindan HAFIFCE farkli kanal sayilari
uretti (beklenen bir sonuc — duzeltme farkli bir zaman noktasinda filtre uyguluyor):

| Ufuk/Yon | Arastirmaci (duzeltmesiz) | Bu script (look-ahead-duzeltilmis) |
|---|---|---|
| H1 yukselen | 27 | 31 |
| H1 alcalan | 39 | 42 |
| M30 yukselen | 20 | 29 |
| M30 alcalan | 39 | 38 |

Fark kucuk/tutarli yonde (ayni mertebe) — look-ahead duzeltmesinin sonuc buyuklugunu
NITELIKSEL olarak degistirmedigini, ama sayisal olarak ETKILEDIGINI gosterir; bu, Arastirmaci
raporundaki "n_kanal ortusen kucuktur, bagimsiz gozlem sayisi az" uyarisinin bu script icin de
GECERLI oldugunu teyit eder (bkz. Bolum 5, Faz 3 ortusen-kanal sayilari).

---

## 3) ANA TEST TASARIMI / YONTEM

### 3.1 Giris/Cikis Mekanizmasi (Stratejist tasarimi, degistirilmedi — sadece yurutme-mekanigi
yukarida Bolum 2'de duzeltildi)

- **Rejim/giris-filtresi:** H1 VEYA M30'da onaylanmis (>=3 dokunus + EMA50/EMA200 + MACD
  teyitli, look-ahead-duzeltilmis) kanal aktif olmali.
- **Giris tetigi:** kanalin M15 projeksiyonuna bir M15 barinin `|kapanis-projeksiyon| <=
  0,5×ATR14_M15` ile dokunmasi + bir sonraki M15 barinin trend yonunde kapanmasi. Yurutme:
  bu tetigin OLUSTUGU bardan bir sonraki M15 barinin ACILISI (bkz. Bolum 2).
- **Yon:** simetrik iki yon (yukselen kanal→BUY, alcalan kanal→SELL).
- **Cikis (uc-kosullu, HANGISI ONCE gerceklesirse):**
  1. **SL** = SL_carpan × ATR14_M15 (giris/tetik barindaki ATR degeri)
  2. **TP** = TP_carpan × ATR14_M15 (ayni ATR)
  3. **Kirilim-bazli erken-cikis:** kanal, pozisyon acikken KIRILIRSA (break_known_time'a
     ulasilirsa), SL/TP beklenmeden o barin KAPANISINDA kapatilir.
  - Ayni barda SL VE TP ARALIGINA GIRILMISSE: muhafazakar varsayimla **SL ONCELIKLI**
    sayilir (Ortak Ilkeler geregi).
  - Ayni barda SL/TP ile kirilim-bilgisi CAKISIRSA: **SL/TP ONCELIKLIDIR** (fiyat-seviyesi
    tetigi, "kanal artik gecersiz" bilgisinden mantiken once tetiklenmis olur).
- **Pozisyon yonetimi:** TEK POZISYON (4 alt-kombinasyon — H1↑/H1↓/M30↑/M30↓ — birlesik tek
  bir zaman ekseninde yonetilir; cakisan sinyaller ATLANIR). Bu, Stratejist'in gorev
  tanimindan devralinmayan, bu script'in ENGINEERING KARARIDIR (Stratejist tek-pozisyon/
  cok-pozisyon konusunda talimat vermedi) — asagida Sinirlamalar'da acikca isaretlenmistir.

### 3.2 Train / Validation / Test Ayrimi (Purged/Embargolu, Zaman-Bazli)

Toplam M15 veri araligi: 2022-04-18 → 2026-07-13 (~1547 gun). Embargo = 45 gun (medyan kanal
omru H1/M30'da ~22-35 gun'un UZERINDE secildi, sizinti riskini azaltmak icin).

| Split | Baslangic | Bitis | Gun |
|---|---|---|---|
| Train | 2022-04-18 | 2024-05-31 | 773,4 |
| *(embargo)* | 2024-05-31 | 2024-07-15 | 45 |
| Validation | 2024-07-15 | 2025-08-06 | 386,7 |
| *(embargo)* | 2025-08-06 | 2025-09-20 | 45 |
| Test | 2025-09-20 | 2026-07-13 | 296,7 |

**Robustluk kontrolu (cross-split kanal):** 140 kanalin sadece **2'si** confirm/break
anlarinda FARKLI split'lere dusuyor (%1,4) — purge/embargo etkin, kanal-duzeyinde sizinti
riski DUSUK. (Not: split atamasi ENTRY-zamanina gore yapildi, kanal-duzeyinde DEGIL — bu
sayi, o basitlestirmenin ne kadar az soruna yol actigini gosteriyor; bkz. Sinirlamalar.)

**Hiperparametre secimi (SL/TP carpani):** grid (SL: 0,5/0,75/1,0×; TP: on-kontrolu gecen
2,0/2,5/3,0/4,0× — 12 hucre), Train'de tarandi, **secim SADECE Validation Profit Factor'una
gore yapildi** (n>=30 islem sarti — tum 12 hucre bu sarti rahatlikla gecti, en dusuk hucre
n=1693). **Test seti TEK KEZ, secim TAMAMLANDIKTAN SONRA kullanildi.**

Grid tarama sonuclari (ozet — tam tablo JSON'da `faz7_grid_tarama`):

| SL× | TP× | Train n / PF | Validation n / PF |
|---|---|---|---|
| 0,50 | 2,0 | 11756 / 0,6473 | 5188 / 0,7844 |
| 0,50 | 2,5 | 9370 / 0,6958 | 4303 / 0,8009 |
| 0,50 | 3,0 | 8078 / 0,7292 | 3767 / 0,8246 |
| 0,50 | 4,0 | 6182 / 0,7224 | 2957 / 0,8544 |
| 0,75 | 2,0 | 8526 / 0,7179 | 3861 / 0,8728 |
| **0,75** | **2,5** | **6805 / 0,7715** | **3079 / 0,9205 (EN IYI)** |
| 0,75 | 3,0 | 5884 / 0,7773 | 2719 / 0,8796 |
| 0,75 | 4,0 | 4338 / 0,7983 | 2122 / 0,8983 |
| 1,00 | 2,0 | 6618 / 0,7670 | 3073 / 0,9148 |
| 1,00 | 2,5 | 5336 / 0,7750 | 2470 / 0,9111 |
| 1,00 | 3,0 | 4447 / 0,7898 | 2141 / 0,9065 |
| 1,00 | 4,0 | 3322 / 0,8138 | 1693 / 0,8782 |

**KRITIK GOZLEM:** Grid'in **HICBIR hucresi Validation'da PF>=1'e ULASAMADI** (en iyisi
0,9205). Bu, SL/TP kalibrasyonunun/asiri-optimizasyonun degil, mekanizmanin KENDISININ
(dokunus+devam-tetigi) bu veri setinde tutarli/pozitif bir edge URETMEDIGINI gosteren guclu
bir isarettir — herhangi bir tekil hucre secimine bagli bir sonuc DEGILDIR.

**Secilen kombinasyon: SL=0,75×ATR14_M15, TP=2,5×ATR14_M15** (Validation PF=0,9205 ile en
iyi, n>=30 sartini rahatlikla asan 12 hucre arasindan).

---

## 4) SONUCLAR (Walk-Forward)

| | Train (Egitim) | Validation | **Test (TEK KEZ)** | Tam Donem Birlesik* |
|---|---|---|---|---|
| Islem sayisi | 6.805 | 3.079 | **2.699** | 13.486 |
| Win rate | %23,75 | %24,46 | **%22,56** | %23,45 |
| Profit Factor | 0,7715 | 0,9205 | **0,9197** | 0,8222 |
| Net kar (USD) | -28.157,74 | -3.811,86 | **-2.982,52** | -39.816,66 |
| Net kar (pts, lot-agnostik) | -200.430,1 | -58.599,8 | **-202.333,7** | -520.432,3 |
| Max Drawdown %** | %1.413,97 | %216,13 | **%134,26** | %1.999,59 |
| Medyan tutma suresi | 0,5 saat | 0,5 saat | **0,5 saat** | 0,5 saat |
| Cikis: SL / TP / Kirilim / Veri-sonu | 5189/1615/1/0 | 2326/753/0/0 | **2089/608/1/1** | 10323/3160/2/1 |

\* Tam Donem Birlesik: Train+Validation+Test'in TUMU, tek-pozisyon kurali TUM zaman
ekseninde YENIDEN uygulanarak (split sinirlarindan bagimsiz) hesaplanmistir — sadece genel
bir referans/H1-ile-karsilastirma gorunumudur, kalibrasyon/karar bu sutuna DAYANMAMISTIR.

\*\* **ONEMLI UYARI — Max Drawdown %:** Bu rakam, kasa=2.000 USD SABIT (compounding YOK,
gorev madde 7 geregi) ve **HICBIR DD-STOP UYGULANMADAN** (mark-to-market, sinirsiz-devam
varsayimiyla) hesaplanan teorik bir buyuklüktur — Test'te bile %134 (yani baslangic
kasasinin tamamindan fazlasi kaybedilmis GORUNUYOR, ki gercek hesapta bu imkansizdir, marj
cagrisi/hesap sifirlanmasi cok once gerceklesirdi). Bu rakam DOGRUDAN yorumlanmamalidir;
asil ANLAMLI/operasyonel bulgu asagidaki DD-STOP RESTART-SIMULASYONUDUR.

### 4.1 DD-Stop Restart-Simulasyonu (operasyonel gerceklik testi)

`justin_gecmis_calisma.md` geregi, kumulatif drawdown %20'ye (kasa 1.600 USD) ulastiginda
islem OTOMATIK DURUR; yeniden baslama Ertan'in onayini gerektirir. Bu kurali, tam-donem islem
dizisi uzerinde ("STOP tetiklenince kasa/peak sifirlanir, restart varsayilir" basitlestirmesiyle)
simule ettim:

- **Ilk -%20 DD-stop esigi, sadece 39. islemde (2022-04-21, ilk 3 GUN icinde) asiliyor.**
- Tam ~4,3 yillik donemde, bu esik **TOPLAM 120 KEZ** tetiklenirdi (restart varsayimiyla —
  yani ortalama her ~13 gunde bir).

**Anlami:** H2, mevcut kalibrasyonuyla, Justin'in operasyonel STOP/START governance kuraliyla
(bkz. CLAUDE.md Mimari Boyut E/F, `justin_gecmis_calisma.md`) BIRLIKTE dusunuldugunde CANLIYA
gecse, pratikte surekli STOP'a girip her seferinde Ertan'in manuel onayini bekleyen bir sistem
olurdu — bu, gunluk pipeline dongu sinirindan (Mimari Boyut E, 5 tur/gun) TAMAMEN AYRI, ama
BENZER RUHDA bir operasyonel-uygulanabilirlik sorunudur.

### 4.2 Islem Kaynagi/Yon Kirilimi (tam donem, pts-bazli PF)

| Kirilim | n | Win rate | PF (pts) | Net pts |
|---|---|---|---|---|
| H1 kaynakli | 8.852 | %23,38 | 0,8806 | -373.896,1 |
| M30 kaynakli | 4.634 | %23,57 | 0,8751 | -146.536,2 |
| Yukselen (BUY) | 6.895 | %23,86 | 0,8987 | -237.574,9 |
| Alcalan (SELL) | 6.591 | %23,02 | 0,8556 | -282.857,5 |

Her iki ufuk kaynagi (H1/M30) ve her iki yon (BUY/SELL) BENZER sekilde PF<1 — sonuc TEK bir
alt-kombinasyonun/yonun carpitmasi DEGIL, mekanizmanin GENELINDE tutarli.

---

## 5) KIRILIM-BAZLI-ERKEN-CIKIS DOGRULAMASI

**Bulgu (beklenmedik ama mantikli):** Tam donemde SADECE **2/13.486 (%0,01)** islem
KIRILIM_ERKEN_CIKIS ile kapandi. Bu bir UYGULAMA HATASI DEGIL, YAPISAL bir sonuctur: SL/TP
medyan **0,5 saatte** cozuluyor, kanallarin medyan omru ise **haftalarca** (H1: ~28,5-35,5
gun, M30: ~21,6-24,8 gun, bkz. Arastirmaci raporu) — yani bir pozisyonun, kendi SL/TP'si
tetiklenmeden ONCE kanalin kirilmasini "yasayacak kadar" uzun acik kalmasi istatistiksel
olarak COK NADIR bir olaydir.

**Dogrulama (2 ornek islem, manuel izlenebilir):**

| Giris | Cikis | Yon | Kaynak | Tutma suresi | Net pts |
|---|---|---|---|---|---|
| 2024-03-05 17:30 | 2024-03-06 09:00 | SELL | H1 | 14,5 saat | +167,35 |
| 2026-05-27 17:00 | 2026-05-28 02:00 | BUY | M30 | 8,0 saat | +2.572,35 |

Her iki ornekte de tutma suresi (8-14,5 saat), genel medyanin (0,5 saat) COK UZERINDE — bu,
kirilim-cikisinin SADECE "olagandisi uzun surede acik kalan" nadir pozisyonlarda devreye
girdigini teyit eder (kod: `simulate_trades()` ic donguSU SL→TP→kirilim SIRASIYLA kontrol
eder; kirilime ulasan bir bar zaten SL/TP'yi GECMIS demektir).

**ONEMLI SONUC ICIN RISK ANALISTI'NE NOT:** Stratejist'in bu mekanizmayi ozellikle "onay-
sonrasi devam-oraninin tutarsizligi" riskine karsi bir GUVENLIK AGI olarak tasarladigi
hatirlanmalidir (Stratejist raporu, H1/H2 RISKLER bolumu). **Bu guvenlik agi, mevcut ATR-bazli
SL/TP olceginde PRATIKTE NEREDEYSE HIC DEVREYE GIRMEMEKTEDIR** — yani "yanlis onaylanmis
kanal" riskine karsi tasarlanan koruma, gercekte islemlerin buyuk cogunlugu icin ISLEVSIZDIR
(SL/TP zaten cok daha once devreye giriyor). Bu, mekanizmanin YANLIS oldugu anlamina gelmez,
ama Stratejist'in bu riske karsi "korundugumuzu" varsaymamasi gerektigini gosterir.

---

## 6) SCALPING-TANIMI GERILIMI (ayri, acik bolum)

**Beklenti (Stratejist devir notu 5, proxy-bazli):** 4,4-10,3 saat tutma suresi — Ertan'in
Cevap 3 (scalping karakteri KESIN, "dakikalar-birkac saat") ile sinir-bolgesi.

**Gerceklesen (bu backtest, SL/TP UYGULANMIS gercek simulasyon):**

| Metrik | Tum islemler | Sadece SL-cikisi | Sadece TP-cikisi |
|---|---|---|---|
| n | 13.486 | 10.323 | 3.160 |
| Medyan tutma suresi | **0,5 saat** | 0,25 saat | 1,25 saat |
| Ortalama tutma suresi | 1,29-1,44 saat (split'e gore) | 1,03 saat | 2,56 saat |
| p90 tutma suresi | 3,5 saat | - | - |
| p99 tutma suresi | 14,75 saat | - | - |

**SONUC OTOMATIK "SCALPING-UYUMLU" OLARAK KABUL EDILMEMISTIR — somut degerlendirme:**

1. **Medyan/ortalama tutma suresi ("dakikalar-birkac saat") Ertan'in Cevap 3 tanimina
   RAHATLIKLA UYUYOR** — Stratejist'in proxy-bazli 4,4-10,3 saatlik beklentisinden CIDDI
   OLCUDE KISA. **Bu tutarsizlik, PROXY olcumun (SL uygulanmadan N-bar-ileri fiyat hareketi)
   GERCEK bir trade simulasyonundan (SL erken keser) YAPISAL OLARAK FARKLI bir sey olctugunu
   gosterir** — proxy, gercekci tutma-suresi tahmini icin SISTEMATIK OLARAK YUKARI SAPMALIDIR
   (SL kesintisini modellemedigi icin). Bu, gelecekteki hipotezlerin S1/tutma-suresi proxy
   degerlerini yorumlarken akilda tutulmasi gereken GENEL bir metodolojik derstir.
2. **p99 (14,75 saat) ve kirilim-cikisi ornekleri (8-14,5 saat) gosteriyor ki kuyrukta
   "gunun buyuk kismi" mertebesine yaklasan nadir islemler VAR** — ama bunlar ISTISNA, KURAL
   DEGIL.
3. **Ancak bu uyum, sonucu KURTARMAZ:** kisa tutma suresi buyuk olcude HIZLI SL-VURMASINDAN
   (medyan 0,25 saat, %76,5 islem SL ile kapaniyor) kaynaklanmaktadir — yani sistem
   "scalping hizinda" ISLEM YAPIYOR, ama "scalping hizinda KAYBEDIYOR" da. Bu, Justin'in
   kendi gecmis_calisma dosyasindaki "SL butcesi vs volatilite gurultusu" TEMASININ (MilaGold
   icin degil, Justin'in KENDI T=500-islem/binom-DD analizinde de vurgulanan bir ilke) bu
   yaklasimda da GECERLI OLDUGUNU gosteriyor gibi gorunmektedir: SL=0,75×ATR14_M15 (~216 pts),
   M15 barlarinin TIPIK ARALIGININ (ATR14 medyani ~288 pts) ALTINDA — yani SL genisligi,
   sirf NORMAL bar-ici gurultu ile bile SIK SIK asiliyor olabilir. **Grid taramasi bu
   yorumu DESTEKLIYOR: SL=1,0×ATR (bar-araligina daha yakin/esit) bile Validation'da PF'yi
   1'in UZERINE TASIYAMADI (en iyisi 0,9148)** — yani sorun SADECE "SL cok dar" degil, daha
   TEMEL bir edge-yetersizligi/maliyet sorunu olarak GORUNMEKTEDIR (kesin ayrim icin Risk
   Analisti'nin/Stratejist'in ek analizi gerekebilir).

**Netlestirme (Stratejist'in atif-netligi ilkesi geregi):** RED sonucu, "scalping-tanimi
geriliminden" DEGIL (bu gerilim aslinda PRATIKTE COZULMUS gorunuyor), **edge/maliyet
yetersizliginden** kaynaklanmaktadir. Bu ayrim Risk Analisti'nin karar surecinde onemlidir.

---

## 7) ISLEM FREKANSI

| Metrik | Deger |
|---|---|
| Toplam islem (tam donem, ~4,3 yil) | 13.486 |
| **Islem/ay (tam donem ortalamasi)** | **~259,3** |
| **Islem/yil (tam donem ortalamasi)** | **~3.186,1** |
| Yillik kanal sayisi (H1/M30, referans — Arastirmaci) | ~2,9-6,8/yil |

**KRITIK AYRIM (task madde 6 geregi acikca vurgulanmali):** "Yillik kanal sayisi" (~2,9-6,8)
bir YAPISAL OLAY sayisidir (kac ayri trend-epizodu onaylandi); "islem/yil" (~3.186) ise o az
sayidaki kanal AKTIFKEN, M15 dokunus+devam tetiginin KAC KEZ ates ettigidir (Arastirmaci'nin
"binlerce giris tetigi, birkac kanal icinde" uyarisiyla dogrudan tutarli — bu backtest, o
binlerce ham-tetigi TEK-POZISYON kurallariyla 13.486 GERCEK islemE indirgeyerek somutlastirdi).
**Islem frekansi mutlak olarak scalping'e uygun (gunde ~9 islem)** — ama Bolum 4.1'deki
DD-stop bulgusuyla birlikte okunmalidir: yuksek frekans, dusuk-PF'li bir sistemde DD-stop'a
ULASMA HIZINI da artirir (39 islem = sadece 3 gun).

---

## 8) RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — A Ailesi H2 "Genis-Orneklem M15-Giris" — Kural-tabanli — 2026-07-13

Egitim / Train:
  Islem: 6.805 | Win rate: %23,75 | Profit Factor: 0,7715 | Net: -28.157,74 USD

Gorulmemis Veri (Validation, hiperparametre secimi burada yapildi):
  Islem: 3.079 | Win rate: %24,46 | Profit Factor: 0,9205 | Net: -3.811,86 USD

Gorulmemis Veri (TEST, TEK KEZ kullanildi):
  Islem: 2.699 | Win rate: %22,56 | Profit Factor: 0,9197 | Net: -2.982,52 USD

SONUC: RED. Train/Validation/Test UCUNDE DE PF<1. Grid taramasindaki 12 SL/TP hucresinin
HICBIRI Validation'da PF>=1'e ulasmadi (en iyisi 0,9205) - bu, tek bir parametre secimine
bagli bir sonuc DEGIL, mekanizmanin (kanal-dokunus+devam-tetigi, M15 giris) KENDISININ bu
veri setinde tutarli pozitif edge URETMEDIGINI gosteriyor.

Dikkat noktalari:
  - ATIF NETLIGI (Stratejist'in talimati): Bu RED "A ailesi olu" veya "scalping-tanimi
    gerilimi cozulmedi" olarak OKUNMAMALIDIR - gercek tutma suresi (medyan 0,5 saat) Ertan'in
    scalping tanimina (Cevap 3) RAHATLIKLA uyuyor (Stratejist'in proxy-bazli 4,4-10,3 saatlik
    beklentisinden cok daha kisa - proxy, SL-erken-kesmeyi modellemedigi icin sistematik
    olarak yuksek tahmin ediyor gorunuyor). RED'in kaynagi EDGE/MALIYET YETERSIZLIGI, tutma-
    suresi uyumsuzlugu DEGIL.
  - OPERASYONEL DD-STOP BULGUSU (en somut/aciklanabilir risk sinyali): restart-simulasyonunda
    Justin'in %20 kumulatif DD-stop esigi TAM DONEMDE 120 KEZ tetiklenirdi, ILKI SADECE 39.
    ISLEMDE (ilk 3 gun icinde). Mevcut governance kurali geregi (START her zaman Ertan onayi
    gerektirir, otomatik degil) bu, pratikte surekli mudahale gerektiren bir sistem demektir.
  - KIRILIM-BAZLI ERKEN-CIKIS GUVENLIK AGI NEREDEYSE HIC DEVREYE GIRMIYOR (2/13.486, %0,01) -
    SL/TP medyan 0,5 saatte cozulurken kanallar haftalarca surdugu icin YAPISAL olarak nadir
    bir olay; Stratejist'in bu mekanizmayla "onay-sonrasi tutarsiz devam-orani" riskine karsi
    korundugu varsayimi bu backtest'te DOGRULANMADI (mekanizma dogru CALISIYOR, ama pratikte
    ISLEVSIZ - farkli bir SL/TP olceginde durum degisebilir, bu turde TEST EDILMEDI).
  - SL BUTCESI VS VOLATILITE GURULTUSU ISARETI: secilen SL (0,75xATR14_M15 ~216 pts), M15
    barlarinin TIPIK araliginin (ATR medyani ~288 pts) ALTINDA - bu, sik SL-vurmasinin (%76,5
    islem SL ile kapaniyor, medyan tutma 0,25 saat) bir nedeni olabilir. Ancak SL=1,0xATR
    (bara esit/daha genis) DENENDIGINDE BILE PF 1'in altinda kaldi (en iyisi 0,9148) - yani
    sorun SADECE dar-SL degil, muhtemelen daha temel bir edge sorunu (Risk Analisti/Stratejist
    ek inceleme yapabilir).
  - DST BELIRSIZLIGI (bagimsiz dogrulandi, H1 VE M15'te AYRI AYRI): 2025-03-30 ve 2026-03-29
    gecislerinde 1-saat kayma tespit edildi (H1/M15'te AYNI sonuc) - M15 kanal-projeksiyonu
    kis aylarinda 1 saat kaymis olabilir, bu backtest GMT+3-sabit varsayimiyla hesaplanmistir.
  - LOOK-AHEAD DUZELTMESI UYGULANDI (confirm_idx+5 bar gecikme + yurutme bir-bar-ileri) -
    duzeltme sonrasi kanal sayilari Arastirmaci'nin ham on-tarama sayilarindan HAFIFCE farkli
    (ayni mertebede) - bu FARKLILIK BEKLENEN bir sonuctur, hata degildir.
  - TEK-POZISYON VARSAYIMI: Stratejist bu konuda talimat vermedigi icin Backtest Muhendisi
    ENGINEERING KARARI olarak tek-pozisyon (4 alt-kombinasyon birlesik tek eksende) uyguladi -
    bu, gercek islem sayisini (96.976 ham aday -> 13.486 gercek islem) onemli olcude
    ASAGI CEKMISTIR; farkli bir pozisyon-yonetim politikasi (orn. cok-pozisyon/portfoy)
    FARKLI sonuc verebilir, bu turde TEST EDILMEDI.
  - MINIMUM ORNEKLEM: tum split'lerde n>1600 (Train 6805, Validation 3079, Test 2699) -
    "yetersiz veri" uyarisi GEREKMIYOR bu duzeyde. Ancak alttaki YAPISAL kanal sayisi
    (H1/M30 birlesik, ~140 kanal, ortusen-kanal 7-19 arasi kombinasyon basina) KUCUKTUR -
    binlerce islem AYNI birkac onlarca kanal icinde BAGIMSIZ-OLMAYAN, otokorelasyonlu
    gozlemlerdir (Arastirmaci'nin ayni uyarisi burada da GECERLIDIR).

Detay dosya: C:\MilaYatirim\Justin\backtest_A_ailesi_H2_output.json (tum fazlar + grid tarama
  + split sinirlari + kirilim analizleri), tam islem logu:
  C:\MilaYatirim\Justin\backtest_A_ailesi_H2_islem_logu_tam.csv (13.486 islemin TAMAMI)
Kod: C:\MilaYatirim\Justin\backtest_A_ailesi_H2.py
```

---

## 9) JSON RAPORU (STANDART SABLON)

```json
{
  "hipotez_adi": "A Ailesi H2 - Genis-Orneklem M15-Giris",
  "yaklasim_turu": "kural-tabanli (yapisal kanal + M15 giris-zamanlama, ATR-bazli dinamik SL/TP)",
  "test_tarihi": "2026-07-13",
  "parametreler": {
    "min_touches": 3, "touch_k_atr_carpani": 0.5, "swing_n_fraktal": 5,
    "lookahead_lag_bars": 5, "ema_fast": 50, "ema_slow": 200, "macd": [12, 26, 9],
    "sl_carpani_secilen": 0.75, "tp_carpani_secilen": 2.5,
    "sl_tp_taban": "ATR14_M15 (giris/tetik barindaki deger)",
    "kasa_usd": 2000, "risk_pct_ust_sinir": 0.01, "taban_lot": 0.01
  },
  "veri": {
    "kaynak": "MT5/XM, GOLD sembolu, dogrudan MetaTrader5 kutuphanesi (H1/M30/M15)",
    "baslangic": "2022-04-18", "bitis": "2026-07-13",
    "toplam_ornek": 99999,
    "bolum_bilgisi": "Train: 2022-04-18/2024-05-31 (773g) | embargo 45g | Validation: 2024-07-15/2025-08-06 (387g) | embargo 45g | Test: 2025-09-20/2026-07-13 (297g), TEK KEZ kullanildi"
  },
  "sonuclar": {
    "toplam_islem": 6805,
    "win_rate": 0.2375,
    "profit_factor": 0.7715,
    "net_profit_usd": -28157.74,
    "max_drawdown_pct_dd_stopsuz": 1413.97,
    "medyan_tutma_suresi_saat": 0.5
  },
  "gorulmemis_veri_sonuclari": {
    "validation": {"toplam_islem": 3079, "win_rate": 0.2446, "profit_factor": 0.9205, "net_profit_usd": -3811.86, "max_drawdown_pct_dd_stopsuz": 216.13},
    "test_tek_kez": {"toplam_islem": 2699, "win_rate": 0.2256, "profit_factor": 0.9197, "net_profit_usd": -2982.52, "max_drawdown_pct_dd_stopsuz": 134.26}
  },
  "kirilim_analizi": {
    "tf_kaynagi": {"H1": {"n": 8852, "win_rate": 0.2338, "pf_pts": 0.8806}, "M30": {"n": 4634, "win_rate": 0.2357, "pf_pts": 0.8751}},
    "yon": {"BUY": {"n": 6895, "win_rate": 0.2386, "pf_pts": 0.8987}, "SELL": {"n": 6591, "win_rate": 0.2302, "pf_pts": 0.8556}},
    "cikis_nedeni_tam_donem": {"SL": 10323, "TP": 3160, "KIRILIM_ERKEN_CIKIS": 2, "VERI_SONU_ACIK": 1},
    "dd_stop_restart_simulasyonu": {"ilk_tetiklenme_islem_no": 39, "ilk_tetiklenme_tarih": "2022-04-21", "toplam_tetiklenme_tam_donem": 120}
  },
  "islem_logu": "Tam log CSV dosyasinda - backtest_A_ailesi_H2_islem_logu_tam.csv (13.486 islemin TAMAMI, ornek degil)",
  "uyarilar": [
    "RED: Train/Validation/Test UCUNDE DE PF<1; grid'in 12 hucresinden HICBIRI Validation'da PF>=1'e ulasmadi.",
    "ATIF_NETLIGI: RED sebebi scalping-tanimi-gerilimi DEGIL (bu gerilim pratikte cozulmus - medyan tutma 0.5 saat) - edge/maliyet yetersizligi.",
    "DD_STOP_OPERASYONEL_RISK: restart-simulasyonunda %20 kumulatif DD-stop tam donemde 120 kez tetiklenirdi, ilki sadece 39. islemde.",
    "KIRILIM_ERKEN_CIKIS_ISLEVSIZ_PRATIKTE: guvenlik agi sadece 2/13486 islemde devreye girdi (SL/TP cok daha hizli cozuluyor).",
    "PROXY_VS_GERCEK_TUTMA_SURESI_SAPMASI: Stratejist/Arastirmaci proxy'si (4.4-10.3 saat) gercek SL-uygulanan simulasyondan (medyan 0.5 saat) ciddi sapiyor - proxy sistematik olarak yuksek tahmin ediyor gorunuyor (SL-erken-kesmeyi modellemiyor).",
    "TEK_POZISYON_MUHENDISLIK_KARARI: Stratejist talimat vermedigi icin Backtest Muhendisi karari (96976 ham aday -> 13486 gercek islem) - farkli politika farkli sonuc verebilir, test edilmedi.",
    "DST_BELIRSIZLIGI: 2025-03-30/2026-03-29 gecislerinde 1-saat kayma (H1 ve M15'te bagimsiz dogrulandi) - kis aylari icin M15 projeksiyonu etkilenebilir.",
    "MALIYET_MODELI_SINIRI: cift-tarafli gercek tick simulasyonu YAPILMADI - global medyan spread+slipaj-tahmini (37.65 pts/islem) kullanildi, Justin projesinde onceden tick-dogrulanmis (~ATR'nin %3.7'si) bir oranla tutarli."
  ]
}
```

---

## 10) IZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md,
  backtest_muhendisi_gold_gecmis_calisma.md vb.) ACILMADI veya referans ALINMADI.
- MilaGold'un aktif parametreleri (M5 EMA20, EMA100 streak>=13, trailing stop, 0,01 lot,
  5$/3$/5$/8$ SL/TP, %20 GUNLUK emniyet stopu) hicbir sekilde kullanilmadi. Bu backtest'in
  SL/TP'si tamamen ATR14_M15-bazli/dinamik (Stratejist'in H2 tasarimina gore, walk-forward'da
  kalibre edilmis); DD-stop kurali Justin'in KENDI %20 KUMULATIF (gunluk degil) kuralidir
  (`justin_gecmis_calisma.md`), MilaGold'un gunluk kuraliyla KARISTIRILMAMISTIR.
- Kanal tespit algoritmasi, ayni proje icindeki Arastirmaci'nin pivot/kanal tarama
  scriptiyle METODOLOJIK OLARAK tutarli tutuldu (izolasyon kurali yalniz BASKA proje
  dosyalarini yasaklar, ayni-proje-ici tutarlilik degil) — ama BAGIMSIZ yeniden yazildi ve
  LOOK-AHEAD DUZELTMESI + tam bir trade-simulator (SL/TP/kirilim-cikisi/lot-boyutlandirma/
  walk-forward) eklenerek O SCRIPT'TEN TEMELDE FARKLI bir arac uretildi.
- Calisma yalniz `C:\MilaYatirim\Justin\` dizininde yapildi; veri dogrudan MT5'ten
  (MetaTrader5 python kutuphanesi, GOLD sembolu) cekildi.

---

## 11) SINIRLAMALAR (ozet — bircogu yukarida ilgili bolumlerde detaylandirildi)

1. **Tek-pozisyon muhendislik karari** (Bolum 3.1, 8) — Stratejist talimat vermedi, Backtest
   Muhendisi karari; farkli politika farkli sonuc verebilir.
2. **Entry-zamani bazli split (kanal-bazli purge DEGIL)** — cross-split kanal sayisi dusuk
   (2/140, %1,4) oldugu icin risk KUCUK ama SIFIR degil (Bolum 3.2).
3. **Maliyet modeli** — global medyan spread+slipaj-tahmini kullanildi, tam cift-tarafli
   tick-bazli simulasyon YAPILMADI (Justin projesinde daha once tick-dogrulanmis bir oranla
   TUTARLI, ama bu turde YENIDEN dogrulanmadi).
4. **DD-stop restart-simulasyonu basit bir yaklasimdir** (STOP anında "peak sifirlanir, hemen
   restart" varsayimi) — gercekte restart Ertan'in onayini gerektirdigi icin GECIKMELI olur;
   120 rakami bir UST SINIR/gosterge niteligindedir, kesin bir operasyonel sayim degildir.
5. **Grid kucuk tutuldu** (3×6=18 hucre, TP-precheck sonrasi 3×4=12 hucre kullanildi) — asiri
   optimizasyondan kacinma ilkesi geregi genis bir tarama yapilmadi; daha genis bir grid farkli
   (muhtemelen yine PF<1 civarinda, ama kesin degil) sonuc verebilir.
6. **DST/saat-eslesme belirsizligi** (2025-10-26 gecisi hala "karisik/belirsiz") — bu turde de
   COZULMEDI, sadece tekrar dogrulandi (Bolum 1.1).
7. **Ortusen-kanal sayilari kucuk** (kombinasyon basina 7-19 kanal) — Arastirmaci'nin
   "binlerce ham-tetik, birkac kanal icinde, bagimsiz-olmayan gozlemler" uyarisi bu backtest
   icin de GECERLIDIR; 13.486 gercek-islem sayisi COK olsa da ALTTAKI yapisal-cesitlilik
   (kac FARKLI kanal/rejim test edildi) SINIRLIDIR.
8. **H1 ile dogrudan karsilastirma bu raporda YAPILAMADI** — H1'in Backtest Muhendisi turu bu
   yazim aninda paralel/bagimsiz calisiyor olabilir (gorev tanimi geregi H1'i beklemek
   gerekmiyordu). Bu raporun JSON semasi/split-metodolojisi H1 ile DOGRUDAN karsilastirmaya
   HAZIR sekilde tasarlandi (ayni split-oran/embargo mantigi, ayni metrik tanimlari) —
   Orkestrator/Risk Analisti H1 raporu geldiginde iki JSON'u yan yana koyabilir.

---

## 12) ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik/offline
backtest calismasi, canli sisteme dokunus yok, Justin arastirma asamasinda — canli/demo hesap
henuz baglanmadi). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu
kategorisi. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
