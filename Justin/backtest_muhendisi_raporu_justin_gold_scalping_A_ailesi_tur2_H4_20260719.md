# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following) — TUR 2 — HIPOTEZ H4

Hipotez adi: "Momentum-Esikli Teyit" (Yon + Govde/ATR14 Conviction Esigi, Kanal-Ici Dokunus Korunuyor)
Yaklasim turu: Kural-tabanli
Proje: Justin (Gold Scalping alt-hedefi) — A Ailesi, TUR 2
Test tarihi: 2026-07-19
Girdi: `stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md`, HIPOTEZ H4 bolumu +
"BACKTEST MUHENDISI ICIN NOTLAR" 1-10 (H5/H6 bu gorevin kapsaminda DEGILDIR)
Gorev: Orkestrator cagrisi, 2026-07-19 09:20
Calisma dizini: yalniz `C:\MilaYatirim\mila-yatirim-sistemi\Justin\`
Kod: `backtest_H4_momentum_esikli_teyit.py`
Ham cikti: `backtest_H4_momentum_esikli_teyit_output.json`
Tam islem loglari: `backtest_H4_M15_k10_islem_logu_tam.csv`, `backtest_H4_M15_k05_islem_logu_tam.csv`,
`backtest_H4_M5_k10_islem_logu_tam.csv`

Referans (kalici on-kontrol standardi): `justin_backtest_onkontrol_standardi.md`
Referans (kasa/risk/lot): `justin_gecmis_calisma.md`
Karsilastirma tabani (Tam Tur 1, ayni HTF/LTF/orneklem): `backtest_A_ailesi_H2.py` /
`backtest_A_ailesi_H2_output.json` (mekanizma degil, SADECE karsilastirma referansi olarak
okundu — H2'nin hicbir SL/TP/parametre degeri bu rapora TASINMADI, bkz. Bolum 8 Izolasyon Notu).

**"Onceki-Tur-Ayrisma-Teyidi":** Stratejist raporunda zaten yapildi ve "GECTI" olarak
kayitlandi (H4, Tam Tur 1'in yon-devami-yeterli varsayimina YENI bir olcut-turu — govde/ATR
conviction esigi — ekliyor). Bu backtest o teyidi TEKRARLAMAZ, sadece SAYISAL sonucunu uretir.

---

## 0) OZET (en onemli bulgu, once)

H4'un UC kombinasyonu da (M15 birincil k=1,0; M15 duyarlilik k=0,5; M5 capraz-kontrol k=1,0)
on-kontrolleri (DST bagimsiz + S1 gercek-maliyet-orani) GECTI ve ana teste ALINDI. Ancak
UCUNUN DE ana test sonucu **RED**dir: Train/Validation/Test/Tam-Donem'in **HEPSINDE Profit
Factor 1'in ALTINDA** kaldi, ve 3 kombinasyon x 12 hucrelik (toplam 36 hucre) SL/TP grid
taramasinin **HICBIRI Validation'da PF>=1'e ULASMADI** (en iyisi 0,9531).

**Mekanizma-degisikliginin somut etkisi (Stratejist'in "mekanizma degisince sonuc gercekten
degisiyor mu" sorusuna dogrudan cevap):** Momentum-esikli teyit (k=1,0), Tam Tur 1 H2'nin
("dokunus+hemen-devam", ayni HTF/LTF/orneklem tabani) tetik sayisini **~%89 azaltti** (10.691
vs 96.976 ham aday) ve **win rate'i belirgin yukseltti** (%28,3-30,4 vs H2'nin %22,6-24,5),
ama **Profit Factor'u breakeven'in UZERINE TASIMAYA YETMEDI** (Test PF 0,942 vs H2'nin 0,9197
— hafif iyilesme, Tam Donem PF 0,8238 vs H2'nin 0,8222 — pratikte AYNI). **Sonuc: mekanizma
degisikligi olculebilir/tutarli bir yon degisimi uretti (daha secici, daha yuksek WR) ama
edge'i pozitife CEVIRMEDI — ayni RED bandinda, biraz daha az negatif.**

Duyarlilik (k=0,5) ve capraz-kontrol (M5, k=1,0) kombinasyonlari da AYNI kalitatif sonucu
veriyor (RED, PF 0,84-0,88 tam donemde) — ayrintilar Bolum 3-4'te.

---

## 1) ON-KONTROL SONUCLARI

### 1.1 Madde 1 — DST/Saat-Esleme BAGIMSIZ Dogrulamasi

Tam Tur 1/H2'den DEVRALINMADI — bu turde H1, M15 VE M5 verisi uzerinde AYRI/BAGIMSIZ olarak
(uc timeframe icin de) yeniden kosturuldu.

**(a) Canli-an capraz kontrol:** epoch-UTC-okuma = 2026-07-17 23:57:56, VPS-yerel-simdi =
2026-07-19 12:28:45,99 → fark **131.450 saniye (~36,5 saat)**. **Bu bir DST/saat-desenkron
sinyali DEGILDIR** — 2026-07-19 bir PAZAR gunudur ve GOLD piyasasi Cuma 23:57 UTC'den beri
KAPALI; MT5'in son tick zaman-damgasi dogal olarak son piyasa-kapanisinda "donmus" haldedir.
Fark, piyasa hafta-sonu kapanisiyla BIREBIR ORANTILI (Cuma kapanisindan Pazar ogleye kadar
gecen sure) — bu, H1/H2 turlarindaki (~0,79 sn) hafta-ici canli-an olcumunden farkli bir
durumdur, YANLIS YORUMLANMAMALIDIR.

**(b) Hafta-sonu-gecis (DST) testi, H1, M15 VE M5'te BAGIMSIZ tekrarlandi:**

| Gecis tarihi | H1 | M15 | M5 | Kayma? |
|---|---|---|---|---|
| 2025-03-30 | 22→23 | 22→23 | 22→23 | **EVET** (ucunde de AYNI) |
| 2025-10-26 | 23→22/23 (karisik) | 23→22/23 (karisik) | 23→22/23 (karisik) | Belirsiz (ABD-DST farkli tarihte gectigi icin) |
| 2026-03-29 | 22→23 | 22→23 | 22→23 | **EVET** (ucunde de AYNI) |

**SONUC:** MT5/XM sunucusu AB/Kibris DST takvimini izliyor (yaz GMT+3, kis GMT+2) — onceki
turlerde (Hipotez 1/2/3, H1, H2) dogrulanan bulguyla TUTARLI, bu turde H1/M15/M5'te AYRI AYRI
(hicbirinden devralinmadan) bagimsiz dogrulandi. Kis aylarinda kanal-projeksiyonu (her uc LTF
icin de) fiilen 1 saat kaymis olabilir — bu dogrulanmamis belirsizlik asagida Risk Analisti'ne
tekrar iletiliyor.

### 1.2 Madde 2 — S1 Maliyet-Orani, GERCEK/OLAY-KOSULLU SL-TP Mesafeleriyle

Arastirmaci'nin proxy hesaplamasi (N-bar-ileri medyan hareket, SL uygulanmadan) burada
KULLANILMADI. Ayrica H2'nin GLOBAL-bar-ATR-medyani yaklasimindan da FARKLI olarak, H4'e ozel
bir incelik uygulandi: maliyet-orani, **momentum-filtreli OLAY KUMESININ KENDI ATR-at-sinyal
medyanina** gore hesaplandi (govde/ATR esigi, dogal olarak ortalamadan farkli ATR bolgelerini
secebilecegi icin — bkz. asagidaki tablo, event-ATR'lerin global-bar-ATR'den farkli cikmasi).

| Kombinasyon | n_olay | Spread medyan (pts) | ATR-event medyan (pts) | Slipaj tahmini (0,037xATR) | TOPLAM MALIYET (pts) |
|---|---|---|---|---|---|
| M15 k=1,0 (BIRINCIL) | 10.691 | 27,00 | 300,86 | 11,13 | **38,13** |
| M15 k=0,5 (DUYARLILIK) | 36.308 | 27,00 | 304,29 | 11,26 | **38,26** |
| M5 k=1,0 (CAPRAZ-KONTROL) | 7.579 | 34,00 | 430,64 | 15,93 | **49,93** |

TP-carpani on-kontrolu (SL grid: 0,5/0,75/1,0×; TP grid: 1,0/1,5/2,0/2,5/3,0/4,0×ATR-event):

| TP carpani | M15 k=1,0 orani | M15 k=0,5 orani | M5 k=1,0 orani | >=15x? |
|---|---|---|---|---|
| 1,0× | 7,89x | 7,95x | 8,62x | KALDI (ucunde de) |
| 1,5× | 11,83x | 11,93x | 12,94x | KALDI (ucunde de) |
| **2,0×** | **15,78x** | **15,91x** | **17,25x** | **GECTI (ucunde de)** |
| **2,5×** | **19,72x** | **19,88x** | **21,56x** | **GECTI (ucunde de, M5'te >=20x de)** |
| **3,0×** | **23,67x** | **23,86x** | **25,87x** | **GECTI + >=20x (ucunde de)** |
| **4,0×** | **31,56x** | **31,81x** | **34,50x** | **GECTI + >=20x (ucunde de)** |

**Karar: UC kombinasyon da ANA_TESTE_GECILEBILIR** — TP>=2,0×ATR-event secenekleri >=15x
esigini gecti (TP=1,0× ve 1,5× ucunde de on-kontrolde ELENDI, walk-forward grid'ine hic
SOKULMADI, sadece SL grid'i x TP>={2,0;2,5;3,0;4,0} = 12 hucre tarandi). **Hicbir kombinasyon
Madde-2'de RED almadi** — H4'un momentum filtresi, event-ATR'yi hafifce yukselttigi icin
(300,9-430,6 vs H2'nin global-bar-ATR'si 287,7) maliyet-orani AC I dan biraz daha rahat.

### 1.3 SL/TP — H4'e Ozel Kalibrasyon (otomatik tasima YOK)

`justin_backtest_onkontrol_standardi.md` Madde 3 geregi, H1/H2/H3'ten (Tam Tur 1) VEYA
birbirlerinden (M15 k=1,0 / k=0,5 / M5 k=1,0 uc kombinasyon KENDI ICINDE de) hicbir SL/TP
degeri devralinmadi. Grid ARAMA-UZAYI (SL: 0,5/0,75/1,0×; TP: 1,0/1,5/2,0/2,5/3,0/4,0×ATR) H2
ile AYNI YAPIDADIR (metodolojik tutarlilik icin standart bir tarama seti — bu bir SL/TP
DEGERI degil, bir ARAMA ARALIGI tanimidir), ancak SECILEN nihai katsayilar HER UC kombinasyon
icin KENDI Train/Validation verisinden BAGIMSIZ olarak asagida (Bolum 3.3) belirlendi:

| Kombinasyon | Secilen SL | Secilen TP | Secim kaynagi |
|---|---|---|---|
| M15 k=1,0 (BIRINCIL) | 1,0×ATR14(M15) | 2,5×ATR14(M15) | Validation PF (n=1218, en iyi 12 hucre arasindan) |
| M15 k=0,5 (DUYARLILIK) | 1,0×ATR14(M15) | 3,0×ATR14(M15) | Validation PF (n=1816, en iyi 12 hucre arasindan) |
| M5 k=1,0 (CAPRAZ-KONTROL) | 1,0×ATR14(M5) | 2,5×ATR14(M5) | Validation PF (n=1264, en iyi 12 hucre arasindan) |

---

## 2) LOOK-AHEAD BIAS DOGRULAMASI (ayri, acik bolum — KRITIK, Stratejist'in vurgusu)

**Sorun (Tam Tur 1'den DEGISMEDI):** Kanal/pivot tanimi (N=5 sag-pencereli fraktal swing)
ILERI-BAKISLIDIR — bar `i`'nin swing oldugu ancak `i+5` barinda (5-bar sag penceresi
tamamlandiginda) GEOMETRIK olarak kesinlesir. Bir kanalin "3. dokunus" ile gecerli sayildigi
`confirm_idx_ham` bari DOGRUDAN kullanilirsa, gercek-zamanli sistemde henuz bilinmeyen bir
bilgiyi (5 bar sonrasinin fiyatlarini) gerektirmis olur.

**Uygulanan duzeltme (bu script, `detect_channels()`):**
- `confirmed_active_idx = confirm_idx_ham + 5` — kanal SADECE bu bardan itibaren "bilinir/
  kullanilabilir" sayilir. **EMA50/EMA200/MACD teyidi confirm_idx_ham'DA DEGIL,
  confirmed_active_idx'TE degerlendirilir.**
- Dokunus tespiti (FAZ 3) ve momentum-tetik uretimi (FAZ 4), kanalin **confirmed_active_time
  → break_known_time** penceresiyle SINIRLANDI — confirm_idx_ham hicbir yerde dogrudan
  dokunus/tetik/giris hesaplamasinda KULLANILMADI, sadece kanal-kaydinda referans olarak
  saklandi.
- Yurutme mekanigi H2 ile AYNI: giris, teyit barindan (i+1, momentum-kosulunun kontrol
  edildigi bar) BIR SONRAKI barin (i+2) ACILISINDADIR. Yurutme aninda kanal zaten kirilmis
  bilgisi varsa (`exec_idx` zamani `break_known_time`'i gecmisse) giris **GECERSIZ SAYILIR**
  (ucu kombinasyonda da 0 kez gerceklesti — bkz. Bolum 4, "kanal_kirilmis_giris_reddi": hepsi 0).

**Ic-tutarlilik dogrulamasi (bu turun EK kontrolu):** 142 confirmed kanalin (H1 up=31/
down=42, M30 up=30/down=39) TAMAMINDA `confirmed_active_idx - confirm_idx_ham = 5` (sabit,
min=max=5) olarak dogrulandi — yani duzeltme HER kanalda, istisnasiz, tutarli uygulandi.

**Kantitatif etki (dokunus/aday-giris sayisi acisindan, H2 ile karsilastirma):** H4'un
momentum filtresi UYGULANMADAN once, ayni look-ahead-duzeltilmis kanal/dokunus tabani zaten
H2 ile PAYLASILIYOR (H2'nin ayni turdeki toplam ham-aday sayisi 96.976 idi — bu script o
tabani YENIDEN URETMEDI, sadece momentum-filtreli alt-kumeyi hesapladi); Bolum 4'teki
%87-89 azalma bu ORTAK tabana gore olculmustur.

---

## 3) ANA TEST TASARIMI / YONTEM

### 3.1 Giris/Cikis Mekanizmasi

- **Rejim/giris-filtresi:** Tam Tur 1/H2 ile AYNI — H1 VEYA M30'da onaylanmis (>=3 dokunus +
  EMA50/EMA200 + MACD teyitli, look-ahead-duzeltilmis) kanal aktif olmali (bu, Ertan'in Cevap
  4'unu — range'de islem yok — yapisal olarak korur).
- **Dokunus:** AYNI tanim — kanal projeksiyonuna `|kapanis-projeksiyon| <= 0,5xATR14(ltf)`.
- **Teyit/tetik (DEGISEN kisim — H4'un tek mekanizma-farki):** dokunus barindan (i) SONRAKI
  barin (i+1) hem trend yonunde kapanmasi HEM DE `|kapanis[i+1]-acilis[i+1]|/ATR14(i+1) >= k`.
  **k=1,0 (BIRINCIL)**, **k=0,5 (DUYARLILIK, ayni raporda ek hucre)**.
- **Giris:** teyit gerceklestiginde, bir SONRAKI barin (i+2) ACILISINDA.
- **Cikis (uc-kosullu, HANGISI ONCE gerceklesirse, H2 ile AYNI):** (1) SL = SL-carpan x
  ATR14(teyit bari), (2) TP = TP-carpan x ATR14(teyit bari), (3) kirilim-bazli erken-cikis
  (kanal kirilirsa SL/TP beklenmeden kapat). Ayni barda SL+TP varsa MUHAFAZAKAR varsayimla SL
  ONCELIKLIDIR; SL/TP ile kirilim-bilgisi cakisirsa SL/TP ONCELIKLIDIR (H2 ile AYNI mantik).
- **Yon:** simetrik iki yon (yukselen kanal→BUY, alcalan kanal→SELL).
- **Pozisyon yonetimi:** TEK POZISYON (H1/M30 x up/down 4 alt-kombinasyon birlesik tek zaman
  ekseninde; cakisan sinyaller ATLANIR) — H2 ile AYNI muhendislik varsayimi, karsilastirilabilirlik
  icin bilincli olarak korundu.

### 3.2 LTF/HTF Kapsam (Stratejist tasarimi)

| Kombinasyon | LTF giris | HTF (kanal) | Yon | Rol |
|---|---|---|---|---|
| M15_k10 | M15 | H1 + M30 | Her ikisi | **BIRINCIL** — H2 (M15-giris, en genis-orneklem/en net RED) ile DOGRUDAN karsilastirma |
| M15_k05 | M15 | H1 + M30 | Her ikisi | **DUYARLILIK** — ayni mekanizma, farkli esik |
| M5_k10 | M5 | H1 + M30 | Her ikisi | **IKINCIL/CAPRAZ-KONTROL** — Arastirmaci'nin en belirgin hizlanma bulgusu |

M1 bu hipotezde KULLANILMADI (Stratejist'in gerekcesi: en kirilgan veri parcasi, birincil test
icin yeterli temel degil — bu backtest bu karari degistirmedi).

**M5 veri-derinligi kisiti (YENI bulgu, Stratejist raporunda ONGORULMEMISTI):** MT5/broker
terminali M5 icin sadece **515 gun** (2025-02-18 → 2026-07-17) gecmis veri tutuyor — M15'in
**1.545 gun**luk (2022-04-25 → 2026-07-17) kapsamindan cok daha kisa. Bu, Stratejist'in "M5
sonucu kanal-sayisi acisindan daha kirilgan kabul edilmeli" uyarisina **EK, BAGIMSIZ bir
kirilganlik kaynagidir** — M5 kombinasyonunun Train/Validation/Test bolumleri de orantili
olarak kisaldi (asagida Bolum 3.3), Test bolumu sadece **38,7 gun**dur.

### 3.3 Train / Validation / Test Ayrimi (Purged/Embargolu, Zaman-Bazli — H2 ile AYNI yapisal metodoloji)

| Split | M15 kombinasyonlari (k=1,0 / k=0,5, AYNI M15 zaman ekseni) | M5 kombinasyonu (k=1,0) |
|---|---|---|
| Train | 2022-04-25 → 2024-06-05 (772,4 gun) | 2025-02-18 → 2025-11-02 (257,3 gun) |
| *(embargo, 45 gun)* | 2024-06-05 → 2024-07-20 | 2025-11-02 → 2025-12-17 |
| Validation | 2024-07-20 → 2025-08-10 (386,2 gun) | 2025-12-17 → 2026-04-25 (128,7 gun) |
| *(embargo, 45 gun)* | 2025-08-10 → 2025-09-24 | 2026-04-25 → 2026-06-09 |
| Test | 2025-09-24 → 2026-07-17 (296,2 gun) | **2026-06-09 → 2026-07-17 (38,7 gun)** |

**UYARI (M5 Test bolumu):** 38,7 gunluk bir Test penceresi, GOLD'un rejim-degisikligine acik
kisa-vadeli davranisini genellemek icin COK KISADIR — Test sonuclari (Bolum 4.3) bu nedenle
ozellikle temkinli okunmalidir, sadece bir "yon-tutarliligi" isareti olarak, kesin bir
dogrulama olarak DEGIL.

**Hiperparametre secimi:** Grid (SL: 0,5/0,75/1,0×; TP: on-kontrolu gecen 2,0/2,5/3,0/4,0× —
12 hucre), Train'de tarandi, secim SADECE Validation Profit Factor'una gore yapildi (n>=30
sarti — HER 12 hucre de her uc kombinasyonda bu sarti rahatlikla gecti). **Test seti TEK KEZ,
secim TAMAMLANDIKTAN SONRA kullanildi.**

**Grid tarama ozeti (tam tablo JSON'da `faz7_grid_tarama`, 3x12=36 hucre):**

| Kombinasyon | En iyi Validation PF | Hangi hucrede | Grid'in 12 hucresinden PF>=1 olan? |
|---|---|---|---|
| M15 k=1,0 | 0,9430 | SL=1,0× TP=2,5× | **HICBIRI** |
| M15 k=0,5 | 0,9385 | SL=1,0× TP=3,0× | **HICBIRI** |
| M5 k=1,0 | 0,9531 | SL=1,0× TP=2,5× | **HICBIRI** |

**KRITIK GOZLEM (H2 ile AYNI patern):** 36 hucrenin HICBIRI Validation'da PF>=1'e ULASAMADI.
Bu, herhangi bir tekil SL/TP secimine bagli bir sonuc DEGIL — momentum-esikli mekanizmanin
KENDISI de, esik degeri (k=1,0 veya 0,5) ve LTF (M15 veya M5) degistirilse dahi, bu veri
setinde tutarli/pozitif bir edge URETMIYOR.

---

## 4) SONUCLAR (Walk-Forward)

### 4.1 M15 — k=1,0 (BIRINCIL)

| | Train | Validation | **Test (TEK KEZ)** | Tam Donem Birlesik |
|---|---|---|---|---|
| Islem sayisi | 3.136 | 1.218 | **1.111** | 5.863 |
| Win rate | %28,57 | %30,38 | **%28,26** (Wilson 95: %25,69-30,98) | %28,74 |
| Profit Factor | 0,7618 | 0,9430 | **0,9420** | 0,8238 |
| Net kar (USD) | -12.126,32 | -946,98 | **-819,96** | -15.477,72 |
| Net kar (pts) | -99.684,3 | -3.254,3 | **-85.060,5** | -207.659,1 |
| Max DD % (DD-stopsuz, teorik) | %614,41 | %80,37 | **%53,85** | %774,15 |
| Medyan tutma suresi | 0,5 saat | 0,5 saat | **0,75 saat** | 0,5 saat |
| Cikis: SL/TP/Kirilim | 2240/896/0 | 848/370/0 | **797/314/0** | 4178/1685/0 |

### 4.2 M15 — k=0,5 (DUYARLILIK)

| | Train | Validation | **Test (TEK KEZ)** | Tam Donem Birlesik |
|---|---|---|---|---|
| Islem sayisi | 4.056 | 1.816 | **1.626** | 8.007 |
| Win rate | %25,32 | %26,38 | **%24,54** (Wilson 95: %22,51-26,69) | %25,23 |
| Profit Factor | 0,7997 | 0,9385 | **0,9096** | 0,8456 |
| Net kar (USD) | -13.516,14 | -1.597,16 | **-2.000,88** | -19.085,08 |
| Net kar (pts) | -117.707,9 | -19.695,6 | **-124.189,6** | -301.003,6 |
| Max DD % (DD-stopsuz, teorik) | %677,80 | %106,91 | **%103,37** | %940,45 |
| Medyan tutma suresi | 0,75 saat | 1,0 saat | **1,0 saat** | 0,75 saat |
| Cikis: SL/TP/Kirilim | 3029/1026/1 | 1337/478/1 | **1227/398/1** | 5987/2017/3 |

### 4.3 M5 — k=1,0 (IKINCIL/CAPRAZ-KONTROL) — Test penceresi COK KISA (38,7 gun), temkinli okuyunuz

| | Train | Validation | **Test (TEK KEZ, n kucuk + pencere kisa)** | Tam Donem Birlesik |
|---|---|---|---|---|
| Islem sayisi | 2.031 | 1.264 | **419** | 4.184 |
| Win rate | %29,69 | %29,59 | **%30,31** (Wilson 95: %26,10-34,87) | %29,57 |
| Profit Factor | 0,8351 | 0,9531 | **0,9402** | 0,8793 |
| Net kar (USD) | -5.039,64 | -771,89 | **-340,72** | -7.157,57 |
| Net kar (pts) | -98.206,6 | -41.783,0 | **-3.465,0** | -164.814,0 |
| Max DD % (DD-stopsuz, teorik) | %273,24 | %43,15 | **%40,43** | %364,66 |
| Medyan tutma suresi | 0,25 saat | 0,25 saat | **0,25 saat** | 0,25 saat |
| Cikis: SL/TP/Kirilim | 1428/603/0 | 890/374/0 | **292/127/0** | 2947/1237/0 |

### 4.4 H2 ile Dogrudan Karsilastirma (Tam Tur 1, ayni HTF/LTF/orneklem tabani — M15 giris, H1+M30)

Bu karsilastirma, Stratejist'in bilincli tasarim kararinin (H4'un M15/H1+M30/her-iki-yon
kombinasyonu H2'yle AYNI tabanda tutuldu) dogrudan sonucudur: **"mekanizma degisince sonuc
gercekten degisiyor mu" sorusuna en temiz cevap.**

| Metrik (Tam Donem) | **H2** (dokunus+hemen-devam, esiksiz) | **H4 M15 k=1,0** (BIRINCIL) | **H4 M15 k=0,5** (duyarlilik) |
|---|---|---|---|
| Ham aday-giris sayisi | 96.976 | 10.691 (**-%89,0**) | 36.308 (**-%62,6**) |
| Gercek islem (tek-pozisyon sonrasi) | 13.486 | 5.863 (-%56,5) | 8.007 (-%40,6) |
| Win rate (tam donem) | %23,45 | **%28,74** (+5,3pp) | **%25,23** (+1,8pp) |
| Profit Factor (tam donem) | 0,8222 | 0,8238 (**pratikte AYNI**) | 0,8456 (hafif iyi) |
| Profit Factor (Test, tek kez) | 0,9197 | **0,9420** (hafif iyi) | 0,9096 (hafif kotu) |
| Profit Factor (Validation) | 0,9205 | 0,9430 (hafif iyi) | 0,9385 (hafif iyi) |
| Islem/ay (tam donem) | 259,3 | 112,75 | 153,98 |
| Islem/yil (tam donem) | 3.186,1 | 1.386,96 | 1.894,14 |

**Yorum (sayisal, karar-verici DEGIL — bu Risk Analisti'nin isi):**
1. Momentum filtresi win-rate'i BELIRGIN yukseltiyor (ozellikle k=1,0'da +5,3pp) — bu, "govde/
   ATR conviction esigi" fikrinin en azindan ISLEM-SECICILIGI acisindan olculebilir bir etkisi
   oldugunu gosteriyor.
2. Ancak Profit Factor'da iyilesme MARJINAL ve TUTARSIZ yonlu: Test'te k=1,0 hafif iyi
   (0,9420 vs 0,9197), ama Tam-Donem'de k=1,0 ile H2 PRATIKTE AYNI (0,8238 vs 0,8222) — yani
   RR-asimetrisi (SL/TP orani), yukselen WR'nin getirdigi avantaji byuk olcude GOTURUYOR
   (govde/ATR esigi gecen barlarin ATR'si de yuksek oldugu icin SL/TP mesafeleri de
   buyuyor — "daha secici ama orantili olarak daha genis SL/TP" etkilesimi).
3. **k=1,0 ile k=0,5 arasindaki karsilastirma KENDI ICINDE TUTARSIZ:** Tam-Donem'de k=0,5 (PF
   0,8456) k=1,0'dan (0,8238) DAHA IYI gorunuyor, ama Test-setinde durum TERSINE DONUYOR (k=1,0
   0,9420 > k=0,5 0,9096). Bu, esik-secimine gore sonucun HANGI donemde bakildigina bagli
   olarak YON DEGISTIREBILDIGINI gosterir — kucuk-orneklem/tek-donem sonuclarina asiri
   guvenilmemesi gerektigine dair somut bir uyaridir (bkz. Bolum 5).
4. **SONUC DEGISMIYOR:** Ne k=1,0 ne k=0,5 ne de M5-capraz-kontrol, PF'yi 1'in UZERINE
   TASIYABILDI — H2'nin RED'i, momentum-esikli teyitle de DOGRULANDI/TEKRARLANDI, iptal
   EDILMEDI.

### 4.5 Kirilim/Yon Dagilimi (Tam Donem, pts-bazli PF)

| Kombinasyon | H1-kaynakli (n, WR, PF_pts) | M30-kaynakli (n, WR, PF_pts) | Yukselen/BUY (n, WR, PF_pts) | Alcalan/SELL (n, WR, PF_pts) |
|---|---|---|---|---|
| M15 k=1,0 | 3.763, %29,07, 0,9233 | 2.100, %28,14, 0,8456 | 2.972, %29,64, 0,9437 | 2.891, %27,81, 0,8572 |
| M15 k=0,5 | 5.189, %25,28, 0,9127 | 2.818, %25,12, 0,8969 | 4.043, %26,44, 0,9785 | 3.964, %23,99, 0,8312 |
| M5 k=1,0 | 3.054, %29,83, 0,9220 | 1.130, %28,85, 0,8670 | 2.217, %30,27, 0,9150 | 1.967, %28,77, 0,9019 |

Her uc kombinasyonda da HTF-kaynagi (H1/M30) ve yon (BUY/SELL) BENZER sekilde PF<1 — RED tek
bir alt-kombinasyon/yon tarafindan carpitilmis DEGIL, mekanizmanin GENELINDE tutarli.

### 4.6 Kirilim-Bazli-Erken-Cikis Dogrulamasi

| Kombinasyon | Kirilim-cikis sayisi / Toplam | Oran |
|---|---|---|
| M15 k=1,0 | 0 / 5.863 | %0,00 |
| M15 k=0,5 | 3 / 8.007 | %0,04 |
| M5 k=1,0 | 0 / 4.184 | %0,00 |

**H2 ile AYNI YAPISAL bulgu:** guvenlik agi (kanal-kirilirsa-erken-cik kurali) H4'te de
PRATIKTE NEREDEYSE HIC DEVREYE GIRMIYOR — SL/TP medyan 0,25-1,0 saatte cozulurken, kanallarin
medyan omru haftalarca surdugu icin, bir pozisyonun SL/TP'den ONCE kanal-kirilmasini
"yasayacak kadar" uzun acik kalmasi istatistiksel olarak nadir bir olay olmaya devam ediyor.
3 ornek (k=0,5'te) manuel izlenebilir: 2024-03-05/06 (14,5 saat, +166,74pts), 2025-07-14/15
(9,25 saat, +425,74pts), 2026-05-27/28 (8,25 saat, +3.397,74pts) — hepsi medyanin (0,5-1,0
saat) COK uzerinde tutma suresine sahip, beklenen paternle tutarli.

### 4.7 Operasyonel DD-Stop Restart-Simulasyonu (basit gosterge, H2 ile AYNI basitlestirme)

`justin_gecmis_calisma.md` geregi kumulatif drawdown %20'ye (kasa 1.600 USD) ulastiginda
islem OTOMATIK DURUR (restart Ertan onayi gerektirir). Tam-donem islem dizisi uzerinde
("STOP tetiklenince kasa/peak sifirlanir, restart varsayilir" basitlestirmesiyle) simule
edildi:

| Kombinasyon | Toplam islem | DD-stop tetiklenme sayisi | Ilk tetiklenme (islem no) |
|---|---|---|---|
| M15 k=1,0 | 5.863 | 50 | 110 |
| M15 k=0,5 | 8.007 | 71 | 205 |
| M5 k=1,0 | 4.184 | 27 | 74 |
| *(referans) H2* | 13.486 | 120 | 39 |

Tetiklenme ORANI (stop/islem) H4'un uc kombinasyonunda da H2 ile BENZER mertebede (%0,64-0,89
vs H2'nin %0,89) — islem sayisi azaldigi icin MUTLAK tetiklenme sayisi da azaldi, ama BU
BASITLESTIRILMIS simulasyon TAKVIM-GUNU bazinda ilk-tetiklenme hizini OLCMEDI (sadece islem-
sirasi bazinda) — bu nedenle "H4 operasyonel olarak daha az sorunlu" sonucu buradan DOGRUDAN
CIKARILAMAZ, sadece islem-basi orani BENZER kaldigi soylenebilir. Bu basitlestirme H2'deki ile
AYNIDIR (Sinirlama olarak asagida tekrar not edilmistir).

---

## 5) ORNEKLEM BUYUKLUGU / GUVEN ARALIGI NOTU

- **Test-seti islem sayilari** (n=1.111 / 1.626 / 419) H2'nin Test-setinden (n=2.699) daha
  KUCUKTUR ama "tek haneli/yetersiz" duzeyde DEGILDIR — M15 kombinasyonlari icin **"yeterli
  n" varsayimi MAKUL**, M5 icin ise **n=419 buyuk gorunse de sadece 38,7 gunluk bir pencerede
  yogunlasmistir** (yukarida Bolum 3.2/3.3), bu nedenle M5 Test sonucu ZAYIF/dusuk-genellenebilir
  kabul edilmelidir.
- **Wilson %95 guven araliklari** (win-rate icin, kucuk-n durumunda normal-yaklasimdan daha
  guvenilir): M15 k=1,0 Test [%25,69-%30,98] (genislik ~5,3pp), M15 k=0,5 Test [%22,51-%26,69]
  (~4,2pp), M5 k=1,0 Test [%26,10-%34,87] (~8,8pp — EN GENIS, kucuk n'in dogal sonucu).
- **Yapisal (bagimsiz-kanal) orneklem KUCUKTUR ve H4'te DE DEGISMEDI:** H1+M30 birlesik
  confirmed-kanal sayisi 142 (H1 up=31/down=42, M30 up=30/down=39); M15-ortusen-kanal
  kombinasyon basina 7-19, M5-ortusen-kanal kombinasyon basina SADECE 3-8. Binlerce/on-binlerce
  islem AYNI birkac onlarca yapisal kanal icinde uretiliyor — bu, Arastirmaci'nin "bagimsiz
  gozlem sayisi kucuk, islemler otokorelasyonlu" uyarisinin H4 icin de AYNEN GECERLI oldugunu
  gosterir (momentum filtresi tetik-basi olay sayisini azaltti ama ALTTAKI yapisal-kanal
  cesitliligini DEGISTIRMEDI — Stratejist'in devir notu 8 ile tutarli).
- **"Yeterli n" varsayilmamalidir** (Stratejist'in acik talebi) — yukaridaki Bolum 4.4 madde 3
  (k=1,0 vs k=0,5'in donem-bagimli yon-degistirmesi) bu uyarinin SOMUT bir ornegidir.

---

## 6) ISLEM FREKANSI

| Kombinasyon | Islem/ay (tam donem) | Islem/yil (tam donem) | Kapsanan donem |
|---|---|---|---|
| M15 k=1,0 (BIRINCIL) | 112,75 | 1.386,96 | ~4,23 yil (2022-04-25→2026-07-17) |
| M15 k=0,5 (DUYARLILIK) | 153,98 | 1.894,14 | ~4,23 yil (ayni) |
| M5 k=1,0 (CAPRAZ-KONTROL) | 232,44 | 2.973,16 | **~1,41 yil (2025-02-18→2026-07-17) — KISA donemden EKSTRAPOLE, dikkatli okunmali** |
| *(referans)* H2 | 259,3 | 3.186,1 | ~4,23 yil |

**Scalping-gerilimi (Ertan'in Cevap 3'u, Risk Analisti'nin ayrica degerlendirmesi gereken
konu):** Momentum filtresi islem frekansini H2'ye gore **%56-%128** dusurdu (M15 k=1,0'da en
fazla, M5'te en az), ama gunluk islem sayisi HALA YUKSEK (M15 k=1,0: gunde ~3,8 islem, M15
k=0,5: gunde ~5,1 islem, M5: gunde ~8 islem — kisa donem ekstrapolasyonu). Medyan tutma suresi
(0,25-1,0 saat) Ertan'in "dakikalar-birkac saat" scalping tanimina RAHATLIKLA uyuyor (H2'de de
gozlenen bir bulgu) — **scalping-tanimi geriliminin bu acidan COZULMUS oldugu soylenebilir**,
ama frekans/PF birlikte dusunuldugunde yuksek-frekansli-negatif-edge sorunu (Bolum 4.7'deki
DD-stop bulgusuyla dogrudan ilintili) devam ediyor.

---

## 7) RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — A Ailesi H4 "Momentum-Esikli Teyit" — Kural-tabanli — 2026-07-19

UC KOMBINASYON DA test edildi: M15 k=1,0 (BIRINCIL), M15 k=0,5 (duyarlilik), M5 k=1,0 (capraz-
kontrol). UCU DE on-kontrolleri (DST + S1 >=15x) GECTI, UCU DE ana testte RED aldi.

Egitim / Train:
  M15 k=1,0: n=3.136, WR=%28,57, PF=0,7618, Net=-12.126,32 USD
  M15 k=0,5: n=4.056, WR=%25,32, PF=0,7997, Net=-13.516,14 USD
  M5  k=1,0: n=2.031, WR=%29,69, PF=0,8351, Net=-5.039,64 USD

Gorulmemis Veri (Validation, hiperparametre secimi burada yapildi):
  M15 k=1,0: n=1.218, WR=%30,38, PF=0,9430, Net=-946,98 USD
  M15 k=0,5: n=1.816, WR=%26,38, PF=0,9385, Net=-1.597,16 USD
  M5  k=1,0: n=1.264, WR=%29,59, PF=0,9531, Net=-771,89 USD

Gorulmemis Veri (TEST, TEK KEZ kullanildi):
  M15 k=1,0: n=1.111, WR=%28,26, PF=0,9420, Net=-819,96 USD (BIRINCIL sonuc — H2 ile dogrudan karsilastirilabilir)
  M15 k=0,5: n=1.626, WR=%24,54, PF=0,9096, Net=-2.000,88 USD
  M5  k=1,0: n=419,  WR=%30,31, PF=0,9402, Net=-340,72 USD (38,7 gunluk KISA pencere - temkinli okuyun)

SONUC: RED (ucunde de). Grid taramasindaki 36 hucrenin (3 kombinasyon x 12) HICBIRI Validation'da
PF>=1'e ulasmadi (en iyisi M5'te 0,9531). H2 ile DOGRUDAN karsilastirma (ayni M15/H1+M30 tabani):
momentum-esikli teyit win-rate'i belirgin yukseltti (+1,8 ila +5,3 puan) ama Profit Factor'u
sadece MARJINAL/TUTARSIZ yonde etkiledi (Tam-Donem'de PF pratikte AYNI: 0,8238 vs H2'nin 0,8222;
Test'te hafif iyi: 0,9420 vs 0,9197) - mekanizma degisikligi RED sonucunu IPTAL ETMEDI.

Dikkat noktalari:
  - MEKANIZMA-SORUSUNA CEVAP (Stratejist'in ana sorusu): "yon-devami YETERLI DEGIL, GUC/
    conviction de gerekli" varsayimi olculebilir bir etki uretti (WR+, aday-sayisi -%89) ama
    PF'yi pozitife CEVIRMEDI - govde/ATR esigini gecen barlarin kendi ATR'si (ve dolayisiyla
    SL/TP mesafesi) de buyudugu icin, WR kazanci RR-asimetrisi tarafindan buyuk olcude
    goturuluyor gibi gorunuyor (kesin nedensellik icin ek analiz gerekebilir).
  - K-DUYARLILIK TUTARSIZLIGI (somut kucuk-n uyarisi): k=1,0 Tam-Donem'de k=0,5'ten KOTU
    (0,8238<0,8456) ama Test-setinde k=1,0 k=0,5'ten IYI (0,9420>0,9096) - esik-secimine gore
    sonuc YON DEGISTIREBILIYOR, "dogru k degeri budur" gibi kesin bir sonuc CIKARILAMAZ.
  - ORNEKLEM KUCULMESI DOGRULANDI: aday-giris sayisi H2'ye gore M15 k=1,0'da %89, k=0,5'te
    %62,6 azaldi (Stratejist'in "~87-90%" tahminiyle TUTARLI) - ama ALTTAKI yapisal-kanal
    cesitliligi (142 kanal, kombinasyon-basi ortusen 3-19) DEGISMEDI - otokorelasyon riski
    H2 ile AYNI DUZEYDE devam ediyor.
  - M5 VERI-DERINLIGI KISITI (YENI bulgu, onceden bilinmiyordu): MT5 terminali M5 icin sadece
    515 gun (M15'in 1.545 gununden COK KISA) tutuyor; M5 Test penceresi sadece 38,7 gun - M5
    capraz-kontrol sonucu bu nedenle EN DUSUK guvenilirlikli olarak okunmali (kanal-sayisi
    kirilganligina EK bir veri-uzunlugu kirilganligi).
  - KIRILIM-BAZLI ERKEN-CIKIS GUVENLIK AGI H2'DEKI GIBI PRATIKTE ISLEVSIZ (0-%0,04 arasi
    tetiklenme orani) - SL/TP cok daha hizli cozuluyor, guvenlik agi neredeyse hic devreye
    girmiyor (H2'de zaten belgelenen bir bulgunun H4'te TEKRARI).
  - DD-STOP OPERASYONEL RISK (basit restart-simulasyonu, H2 ile AYNI basitlestirme): M15 k=1,0
    icin 50 kez/5.863 islem (ilk 110. islemde), M15 k=0,5 icin 71 kez/8.007 (ilk 205. islemde),
    M5 icin 27 kez/4.184 (ilk 74. islemde) - islem-basi ORANI H2 ile (120/13.486) BENZER
    mertebede, mutlak sayi sadece islem-hacmi dustugu icin azaldi; bu basit simulasyon TAKVIM-
    GUNU bazinda ilk-tetiklenme HIZINI olcmedi, "H4 operasyonel olarak daha guvenli" sonucu
    BURADAN CIKARILAMAZ.
  - SCALPING-TANIMI: medyan tutma suresi (0,25-1,0 saat) Ertan'in Cevap 3 tanimina RAHATLIKLA
    uyuyor (H2'de de boyleydi) - ama yuksek islem frekansi (gunde ~3,8-8, kombinasyona gore)
    ile negatif-PF birlikte, DD-stop'a ulasma hizini ARTIRAN bir kombinasyon olusturuyor.
  - DST BELIRSIZLIGI (bagimsiz dogrulandi, H1/M15/M5'te AYRI AYRI, UCUNDE de AYNI sonuc):
    2025-03-30 ve 2026-03-29 gecislerinde 1-saat kayma tespit edildi; 2025-10-26 hala
    belirsiz/karisik. Bu backtest GMT+3-sabit varsayimiyla hesaplanmistir (H1/H2/H3'ten
    devam eden, cozulmemis bir belirsizlik).
  - CANLI-AN CAPRAZ KONTROL ANOMALISI ACIKLANDI: fark 131.450 saniye (~36,5 saat) olculdu ama
    bu bir DST-desenkron sinyali DEGIL - test 2026-07-19 PAZAR gunu yapildigi icin GOLD
    piyasasi kapaliydi (son tick Cuma 23:57 UTC kapanisinda donmus), yanlis alarm.
  - LOOK-AHEAD DUZELTMESI TEKRAR TEYIT EDILDI: 142 kanalin TAMAMINDA confirmed_active_idx -
    confirm_idx_ham = 5 (sabit) - duzeltme tutarli uygulandi, look-ahead riski H2 ile AYNI
    seviyede kontrol altinda.
  - TEK-POZISYON MUHENDISLIK KARARI (H2'den DEVAM EDEN, karsilastirilabilirlik icin bilincli
    korunan bir secim, YENIDEN tartisilmadi bu turde): farkli bir pozisyon-politikasi farkli
    sonuc verebilir, bu turde de TEST EDILMEDI.

Detay dosya: C:\MilaYatirim\mila-yatirim-sistemi\Justin\backtest_H4_momentum_esikli_teyit_output.json
  (tum fazlar + 3x12 grid tarama + split sinirlari + kirilim analizleri)
Tam islem loglari: backtest_H4_M15_k10_islem_logu_tam.csv (5.863 islem),
  backtest_H4_M15_k05_islem_logu_tam.csv (8.007 islem), backtest_H4_M5_k10_islem_logu_tam.csv (4.184 islem)
Kod: C:\MilaYatirim\mila-yatirim-sistemi\Justin\backtest_H4_momentum_esikli_teyit.py
```

---

## 7bis) JSON RAPORU (STANDART SABLON — BIRINCIL kombinasyon icin ozet, tam veri output-JSON'da)

```json
{
  "hipotez_adi": "A Ailesi H4 - Momentum-Esikli Teyit (M15 k=1,0, BIRINCIL)",
  "yaklasim_turu": "kural-tabanli (yapisal kanal + M15 giris-zamanlama + govde/ATR conviction esigi, ATR-bazli dinamik SL/TP)",
  "test_tarihi": "2026-07-19",
  "parametreler": {
    "min_touches": 3, "touch_k_atr_carpani": 0.5, "swing_n_fraktal": 5,
    "lookahead_lag_bars": 5, "ema_fast": 50, "ema_slow": 200, "macd": [12, 26, 9],
    "momentum_govde_atr_esigi_k": 1.0,
    "sl_carpani_secilen": 1.0, "tp_carpani_secilen": 2.5,
    "sl_tp_taban": "ATR14_M15 (teyit barindaki deger)",
    "kasa_usd": 2000, "risk_pct_ust_sinir": 0.01, "taban_lot": 0.01
  },
  "veri": {
    "kaynak": "MT5/XM, GOLD sembolu, dogrudan MetaTrader5 kutuphanesi (H1/M30/M15)",
    "baslangic": "2022-04-25", "bitis": "2026-07-17",
    "toplam_ornek": 99999,
    "bolum_bilgisi": "Train: 2022-04-25/2024-06-05 (772g) | embargo 45g | Validation: 2024-07-20/2025-08-10 (386g) | embargo 45g | Test: 2025-09-24/2026-07-17 (296g), TEK KEZ kullanildi"
  },
  "sonuclar": {
    "toplam_islem": 3136, "win_rate": 0.2857, "profit_factor": 0.7618,
    "net_profit_usd": -12126.32, "max_drawdown_pct_dd_stopsuz": 614.41, "medyan_tutma_suresi_saat": 0.5
  },
  "gorulmemis_veri_sonuclari": {
    "validation": {"toplam_islem": 1218, "win_rate": 0.3038, "profit_factor": 0.943, "net_profit_usd": -946.98, "max_drawdown_pct_dd_stopsuz": 80.37},
    "test_tek_kez": {"toplam_islem": 1111, "win_rate": 0.2826, "profit_factor": 0.942, "net_profit_usd": -819.96, "max_drawdown_pct_dd_stopsuz": 53.85, "win_rate_wilson_95ci": [0.2569, 0.3098]}
  },
  "kirilim_analizi": {
    "tf_kaynagi": {"H1": {"n": 3763, "win_rate": 0.2907, "pf_pts": 0.9233}, "M30": {"n": 2100, "win_rate": 0.2814, "pf_pts": 0.8456}},
    "yon": {"up": {"n": 2972, "win_rate": 0.2964, "pf_pts": 0.9437}, "down": {"n": 2891, "win_rate": 0.2781, "pf_pts": 0.8572}},
    "cikis_nedeni_tam_donem": {"SL": 4178, "TP": 1685, "KIRILIM_ERKEN_CIKIS": 0},
    "dd_stop_restart_simulasyonu": {"ilk_tetiklenme_islem_no": 110, "toplam_tetiklenme_tam_donem": 50}
  },
  "islem_logu": "Tam log CSV dosyasinda - backtest_H4_M15_k10_islem_logu_tam.csv (5.863 islemin TAMAMI)",
  "uyarilar": [
    "RED: Train/Validation/Test/Tam-Donem UCUNDE DE PF<1; 36 hucrelik (3 kombinasyon) grid taramasinin HICBIRI Validation'da PF>=1'e ulasmadi.",
    "H2_ILE_KARSILASTIRMA: ayni HTF/LTF/orneklem tabaninda momentum-esikli teyit WR'yi yukseltti (+5,3pp) ama PF'yi Tam-Donem'de PRATIKTE DEGISTIRMEDI (0,8238 vs 0,8222).",
    "K_DUYARLILIK_TUTARSIZ_YON: k=1,0/k=0,5 karsilastirmasi Tam-Donem'de ve Test'te FARKLI yonde sonuc veriyor - kucuk-n donem-bagimliligina somut ornek.",
    "M5_VERI_KISITI: MT5 terminali M5 icin sadece 515 gun tutuyor (Test penceresi 38,7 gun) - M5 sonucu en dusuk guvenilirlikli.",
    "ORNEKLEM_KUCULMESI: aday-giris sayisi H2'ye gore %89 (k=1,0) / %62,6 (k=0,5) azaldi - Stratejist'in tahminiyle tutarli, ama yapisal-kanal cesitliligi (142 kanal) DEGISMEDI.",
    "KIRILIM_ERKEN_CIKIS_ISLEVSIZ_PRATIKTE: guvenlik agi 0-%0,04 arasi tetiklenme orani (H2'deki %0,01 ile ayni yapisal patern).",
    "DST_BELIRSIZLIGI: 2025-03-30/2026-03-29 gecislerinde 1-saat kayma (H1/M15/M5'te bagimsiz dogrulandi) - kis aylari icin projeksiyon etkilenebilir.",
    "CANLI_AN_ANOMALI_ACIKLANDI: 131.450 sn fark, hafta-sonu piyasa-kapanisi kaynakli (test 2026-07-19 Pazar gunu yapildi), DST-desenkron degil.",
    "TEK_POZISYON_MUHENDISLIK_KARARI: H2'den devam eden, bu turde yeniden tartisilmadi.",
    "MALIYET_MODELI_SINIRI: global medyan spread + olay-kosullu ATR-bazli slipaj-tahmini kullanildi, cift-tarafli tick-simulasyonu YAPILMADI."
  ]
}
```

---

## 8) IZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya ACILMADI veya referans ALINMADI.
  MilaGold'un aktif parametreleri (M5 EMA20/EMA100 streak, trailing stop, sabit $ SL/TP,
  GUNLUK %20 emniyet stopu) hicbir sekilde kullanilmadi.
- `backtest_A_ailesi_H2.py` / `backtest_A_ailesi_H2_output.json` **SADECE sayisal karsilastirma
  REFERANSI olarak okundu** (Bolum 4.4) — H2'nin SL/TP katsayilari, grid'i, split-tarihleri
  veya baska hicbir parametresi bu backtest'e KOPYALANMADI/TASINMADI; H4 kendi Train/Validation
  verisinde SIFIRDAN kalibre edildi (Bolum 1.3, 3.3).
- Kanal tespit algoritmasi (`detect_channels`), ayni proje icindeki `backtest_A_ailesi_H2.py`
  ile METODOLOJIK OLARAK tutarli tutuldu (izolasyon kurali yalniz BASKA proje dosyalarini
  yasaklar, ayni-proje-ici tutarlilik degil) — kod BAGIMSIZ olarak bu script icinde YENIDEN
  yazildi.
- Calisma yalniz `C:\MilaYatirim\mila-yatirim-sistemi\Justin\` dizininde yapildi; veri
  dogrudan MT5'ten (MetaTrader5 python kutuphanesi, GOLD sembolu) cekildi, BAGIMSIZ (H2'den
  devralinmadan) yeniden indirildi.

---

## 9) SINIRLAMALAR (ozet — bircogu yukarida ilgili bolumlerde detaylandirildi)

1. **Tek-pozisyon muhendislik karari** (Bolum 3.1) — H2'den devam eden, bu turde YENIDEN
   tartisilmadi; farkli politika farkli sonuc verebilir.
2. **Entry-zamani bazli split (kanal-bazli purge DEGIL)** — H2 ile AYNI basitlestirme, bu
   turde ayrica bir cross-split-kanal kontrolu KOSTURULMADI (H2'de %1,4 dusuk risk bulunmustu,
   H4'un ayni kanal tabanini KULLANMASI nedeniyle benzer dusuk risk BEKLENIR ama bu turde
   AYRICA DOGRULANMADI).
3. **Maliyet modeli** — global medyan spread + olay-kosullu ATR-bazli slipaj-tahmini (0,037x
   oran, Justin projesinde daha once tick-dogrulanmis) kullanildi; cift-tarafli tick-bazli tam
   simulasyon YAPILMADI (H2 ile AYNI sinir).
4. **DD-stop restart-simulasyonu basit bir yaklasimdir** (Bolum 4.7) — "STOP aninda peak
   sifirlanir, hemen restart" varsayimi gercekci degildir (gercekte Ertan onayi gerektiginden
   GECIKMELI olur); rakamlar UST-SINIR/gosterge niteligindedir, takvim-gunu bazinda kiyaslama
   YAPILMAMISTIR.
5. **Grid kucuk tutuldu** (3x6=18 hucre/kombinasyon, TP-precheck sonrasi 3x4=12 kullanildi) —
   asiri optimizasyondan kacinma ilkesi geregi genis tarama yapilmadi.
6. **M5 veri-derinligi kisiti (YENI, bu turde ortaya cikti)** — terminal/broker M5 gecmisi
   sadece 515 gun; M5 Test penceresi 38,7 gun ile COK KISA, sonuc genellenebilirligi DUSUK.
7. **DST/saat-eslesme belirsizligi** (2025-10-26 gecisi hala "karisik/belirsiz") — bu turde de
   COZULMEDI, sadece (H1/M15/M5'te ayri ayri) tekrar dogrulandi.
8. **Ortusen-kanal sayilari kucuk** (kombinasyon basina 3-19 kanal) — Arastirmaci'nin
   "binlerce ham-tetik, birkac kanal icinde, bagimsiz-olmayan gozlemler" uyarisi H4 icin de
   GECERLIDIR; momentum filtresi tetik-sayisini azaltti ama alttaki yapisal cesitliligi
   ARTIRMADI.
9. **k=0,5/k=1,0 karsilastirmasinin donem-bagimli yon-degistirmesi** (Bolum 4.4 madde 3) —
   bu, kucuk-orneklem/tek-donem sonuclarina asiri anlam yuklenmemesi gerektigine dair somut
   bir kanittir, ayrica bir hassasiyet analizi (orn. rolling-window) bu turde YAPILMADI.
10. **H5 ile dogrudan karsilastirma bu raporda YAPILAMADI** — H5, Stratejist raporunun acikca
    belirttigi gibi bu gorevin kapsaminda DEGILDIR (ayri/paralel gorevlendirildi); H4 ve H5
    sonuclari Risk Analisti asamasinda YAN YANA degerlendirilebilir.

---

## 10) ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik/offline
backtest calismasi, canli sisteme dokunus yok, Justin arastirma asamasinda — canli/demo hesap
henuz baglanmadi). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu
kategorisi. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.

**Governance hatirlatmasi:** Bu, A ailesinin Tur 2'sidir; gunluk tam-tur sayaci (1/5'ten
devam) bu backtest adimiyla DEGISMEZ — sayaci degistiren Risk Analisti'nin nihai/turu-kapatan
karari. H5 (on-tarama sartiyla) bu H4 gorevinden BAGIMSIZ/paralel ilerliyor olabilir; bu rapor
H5'i beklemedi/kapsamadi.
