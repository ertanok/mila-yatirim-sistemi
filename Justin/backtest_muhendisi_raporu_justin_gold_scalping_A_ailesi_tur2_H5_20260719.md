# BACKTEST MUHENDISI RAPORU — Justin / Gold Scalping — A Ailesi (Tur 2), HIPOTEZ H5
## "Kanal-Disi Kirilim Girisi" (A ailesi ICINDE kirilim-tabanli giris varyanti)

Tarih: 19 Temmuz 2026
Gorev kaynagi: Orkestrator cagrisi (19 Temmuz 2026, 09:20)
Yaklasim turu: Kural-tabanli (H1/M30 yapisal kanal rejim-filtresi + kanal-disi kirilim giris tetigi)

---

## ONEMLI ON-UYARI — KAYNAK DOSYA EKSIKLIGI (once bildirilmeli)

Gorev tanimindaki "ONCEKI ADIMIN CIKTISI" olarak belirtilen dosya —
`C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md`
("HIPOTEZ H5 bolumu + BACKTEST MUHENDISI ICIN NOTLAR 1-10", gorevin "dogrudan kaynagi" olarak
tanimlanan dosya) — **calisma dizininde (`C:\MilaYatirim\Justin\`) BULUNAMADI.** Dosya sistemi
tam olarak tarandi (glob ile 144 dosyanin tamami kontrol edildi), bu isimde veya yakin bir
isimde (tur2/adim1/H5 icerikli) baska bir Stratejici raporu da yok. Ayrica ilgili `gorev_
backtest_muhendisi_..._H5...md` gorev-tanimi dosyasi da bulunamadi (bu Orkestrator cagrisi
muhtemelen dogrudan sozlu/canli cagri olarak iletildi, ayrica dosyalanmadi).

Bu, gecmis calisma dosyasi degil — bu gorevin **birincil girdi kaynagi** olarak tanimlanan
belge. Sistem promptum geregi ("eger o dosyada artik gecerli olmayan/eskimis bir varsayim
goruyorsan... sessizce kullanma, bildir") bunu ACIKCA bildiriyorum, sessizce varsaymadim.

**Nasil ilerlendi:** Orkestrator cagrisinin kendisi ADIM 0-3 icin cok detayli/kendi-kendine-
yeterli bir teknik tanim icermektedir (tasma esigi, HTF/LTF/yon kombinasyonlari, giris/cikis
mekanizmasi, walk-forward, lot/risk). Bu script SADECE bu cagridaki tanima ve Tam Tur 1
raporundaki (`stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md`) ile
H2/H3 backtest scriptlerindeki DEGISMEMIS kanal-tespit metodolojisine dayanmaktadir. **Ancak
eksik dosyanin "BACKTEST MUHENDISI ICIN NOTLAR 1-10" kismi, bu raporda bilinmeyen/goruleme
yen ek notlar/kisitlamalar icerebilir** — bu rapor bu notlari HESABA KATAMAMISTIR, cunku
erisilebilir degildir. Bu, sonuclarin gecersiz oldugu anlamina gelmez, ama Risk Analisti/
Orkestrator'un bu raporu "tam" degil "cagrida verilen tanima gore tam, eksik dosyanin notlarina
gore EKSIK OLABILIR" olarak degerlendirmesi gerektigi anlamina gelir.

**Ayrica bir YENI TASARIM UNSURU acikca isaretlenmelidir:** H2/H3'un kanal algoritmasi yalniz
TEK bir cizgi (trend/destek-direnc cizgisi) uretir; "DIS SINIR" (kanal genisligi) kavraminin
KENDISI H1-H3'te YOKTU. Bu rapor icin bu kavram, eksik kaynak dosya nedeniyle Stratejist
tarafindan tanimlanmis BULUNAMADI — bu yuzden bu gorevde SIFIRDAN, acikca belgelenerek
tasarlanmistir (bkz. "Ana Test Tasarimi/Yontem" bolumu, "Kanal Genisligi / Dis Sinir Tanimi").
**Bu bir VARSAYIMDIR ve Stratejist'in gozden gecirip onaylamasi/reddetmesi/duzeltmesi
onerilir** — asagidaki tum sayisal sonuclar bu varsayima BAGLIDIR.

---

## ON-TARAMA SONUCU (ADIM 0 — ZORUNLU, ana testten ONCE)

Script: `backtest_H5_adim0_ontarama.py` -> `backtest_H5_adim0_ontarama_output.json`

**Yontem:** H1/M30'da onaylanmis (>=3 dokunus + EMA50/200 + MACD teyitli, N=5 sag-pencereli
fraktal, 5-bar-gecikmeli look-ahead-duzeltmesi ile) aktif/kirilmamis kanallarin, "DIS SINIR"
(trend-yonundeki karsi sinir — yukselen kanalda ust, alcalan kanalda alt; tanim asagida)
projeksiyonuna karsi, bir M15 (birincil) / M5 (ikincil) barinin kapanisinin, kanalin ICINDEN
DISINA, trend yonunde, en az 0,5xATR14(LTF) mesafede tasma olayi sayildi. Sayim, ayni yonde
UST USTE gelen bar dizilerini TEK bir olay olarak sayacak sekilde (rising-edge/transition
bazli) yapilmistir — yoksa uzun bir tasma-disi-kalma donemi yapay olarak cok sayida "olay"
gibi gorunurdu.

**Onaylanmis kanal sayilari (tum veri, look-ahead-duzeltilmis):** H1 yukselen=31, H1
alcalan=42, M30 yukselen=30, M30 alcalan=39.

**Tasma olayi sayisi — HTF x yon x LTF kombinasyonu bazinda:**

| HTF | Yon | M15 (birincil) olay sayisi | M5 (ikincil/capraz) olay sayisi |
|---|---|---|---|
| H1  | Yukselen | 171 | 91  |
| H1  | Alcalan  | 100 | 61  |
| M30 | Yukselen | 226 | 125 |
| M30 | Alcalan  | 251 | 106 |
| **TOPLAM** | | **748** | **383** |

**KARAR: DEVAM EDILDI.** Olay sayisi HICBIR kombinasyonda tek haneli DEGIL — en dusuk deger
bile (H1 alcalan, M15: 100) Tam Tur 1'in H1 varyantinin yasadigi kirilganlikla (2-8 bagimsiz
kanal) kiyaslanamayacak kadar buyuk. Bu, ADIM 0'in "devam et" esigini net bicimde asmaktadir
— bu bir kalite/edge degerlendirmesi DEGILDIR, sadece bir olay-sayimi esik testidir.

**Ek gozlem (baglam, karari etkilemez):** Kanal genisligi (DIS sinir mesafesi) medyan
degerleri: H1 yukselen=1555,8 pts, H1 alcalan=1806,1 pts, M30 yukselen=1284,8 pts, M30
alcalan=1682,1 pts (ATR14-M15 medyani ~289 pts ile kiyaslandiginda kanal genisligi ATR'nin
~4,4-6,3 kati mertebesinde - DIS sinir "dar" bir bant DEGIL).

---

## ON-KONTROL SONUCLARI (ADIM 1)

Script: `backtest_H5_main.py` -> `backtest_H5_main_output.json`

### (a) DST / Saat-Esleme BAGIMSIZ Dogrulama (Madde 1)

H1 ve M15 verisinde BAGIMSIZ olarak (H2/H3'ten devralinmadan) yeniden kosturuldu:

| Gecis tarihi | Oncesi Cuma kapanis saatleri (UTC) | Sonrasi Cuma kapanis saatleri (UTC) | Kayma tespit edildi mi |
|---|---|---|---|
| 2025-03-30 | 22,22,22 | 23,23,23 | EVET |
| 2025-10-26 | 23,23,23 | 22,23,23 | HAYIR (mod=23, tek bir 22 sapmasi disinda) |
| 2026-03-29 | 22,22,22 | 23,23,23 | EVET |

H1 ve M15 sonuclari BIREBIR AYNI (toplam hafta-sonu-gecis sayisi: H1=3827, M15=224 — farkli
bar sayisi TF'ye bagli, kayma paterni tutarli). Canli capraz kontrol: MT5 sunucu epoch/UTC
okumasi ile VPS yerel saati arasinda ~131.563 saniye (~36,5 saat) fark var — bu, VPS'in yerel
saatinin MT5 sunucu-tick zaman damgasindan farkli bir referans noktasinda oldugunu gosterir
(veri son bar 2026-07-17 23:57, script 2026-07-19 12:30'da calistirildi — makul, "gecikmis
veri" degil, hafta sonu/en-son-tick zaman farki). **Sonuc: H2/H3'teki (ve H1/H2/H3 oncesi 4
bagimsiz teyidin) bulgusuyla TUTARLI** — sunucu, AB/Kibris DST takvimini izliyor gorunmektedir
(2025-03-30 ve 2026-03-29 bahar-ileri gecislerinde net +1 saat kayma; 2025-10-26 guz-geri
gecisinde kayma orani daha zayif/karisik gorunmus, bu H2/H3'te de benzer sekilde raporlanan
bir netlik-sinirlamasidir).

### (b) Maliyet-Orani (S1) — GERCEK SL/TP mesafeleriyle (Madde 2)

- Spread medyani (M15): 27,0 pts
- ATR14 medyani (M15): 289,21 pts
- Slipaj tahmini: 0,037 x ATR14 = 10,70 pts (H2/H3'teki ayni-proje-ici kalibrasyon referansi)
- **Toplam maliyet: 37,70 pts**

| TP carpani (xATR14-M15) | Temsili TP (pts) | Maliyet orani | >=15x | >=20x |
|---|---|---|---|---|
| 1,0 | 289,2  | 7,67x  | KALDI | KALDI |
| 1,5 | 433,8  | 11,51x | KALDI | KALDI |
| 2,0 | 578,4  | 15,34x | GECTI | KALDI |
| 2,5 | 723,0  | 19,18x | GECTI | KALDI |
| 3,0 | 867,6  | 23,01x | GECTI | GECTI |
| 4,0 | 1156,9 | 30,69x | GECTI | GECTI |

**KARAR: ANA TESTE GECILEBILIR.** TP>=2,0xATR14(M15) icin S1 (>=15x) saglaniyor; TP>=3,0x
icin >=20x de saglaniyor. On-kontrolu GECEN TP carpanlari (asagidaki walk-forward grid'ine
girenler): [2,0; 2,5; 3,0; 4,0].

### (c) SL/TP — H5'e Ozel Kalibrasyon, Otomatik Tasima Yok (Madde 3)

H1/H2/H3'ten hicbir SL/TP degeri tasinmadi. H5'e ozel:
- **SL grid:** [0,3; 0,4; 0,5] x ATR14(M15, giris ani) — Orkestrator cagrisindaki "~0,3-0,5x
  ATR14, false-breakout icin hizli cikis" araligi dogrudan grid olarak kullanildi.
- **TP grid:** [1,0; 1,5; 2,0; 2,5; 3,0; 4,0] x ATR14(M15, giris ani) — S1 on-kontrolunden
  gecenler [2,0-4,0] arasindan walk-forward ile secildi (asagida).
- Secim, Train'de tarama -> Validation'da PF'ye gore secim (n>=30 esigi) -> Test'te TEK KEZ
  uygulama seklinde yapildi (H2/H3 ile ayni disiplin).

---

## LOOK-AHEAD BIAS DOGRULAMASI (ADIM 2)

1. **Kanal/pivot tanimi Tam Tur 1'den DEGISMEDI:** N=5 sag-pencereli fraktal swing, >=3
   dokunus (tol=0,5xATR14-HTF), EMA50/200 + MACD(12,26,9) teyidi. Bir swing'in "swing" oldugu
   ancak N=5 bar SONRA kesinlesir; kanal, 3. dokunus barindan (`confirm_idx_ham`) 5 bar SONRA
   (`confirmed_active_idx`) "bilinir" kabul edildi — bu, H2/H3'teki AYNI look-ahead-duzeltmesidir.
2. **H5'e OZEL ek netlik sorusu (gorev tanimi geregi ayrica cevaplaniyor):** Kirilim ANI'nin
   kendisi mi, yoksa kanal cizgisinin kendisi mi gecikmeli? **Cevap: IKI AYRI KAVRAM, DOGRU
   AYRISTIRILMISTIR.** Kanalin cizgisi + genisligi (DIS sinir), sadece `confirmed_active_idx`'te
   "bilinir" hale gelir (5-bar-gecikmeli - madde 1). ANCAK kanal genisligi (DIS sinir mesafesi)
   SADECE `anchor_idx..confirm_idx_ham` (yani `confirmed_active_idx`'ten ONCEKI) verilerden
   turetilmistir — yani kanalin DIS SINIRI, `confirmed_active_idx` anina geldiginde ZATEN
   tam olarak hesaplanabilir durumdadir, ek bir gecikme GEREKTIRMEZ. Tasma taramasi da SADECE
   `confirmed_active_time`'dan itibaren yapilmaktadir. Bu nedenle, bir M15/M5 barinin kapanisinin
   DIS sinirin disinda oldugunu tespit etmek — bu bar kapandigi ANDA, o ana kadar bilinen
   veriyle (kanal cizgisi + sabit genislik + o barin kendi ATR14'u) yapilabilir bir islemdir;
   EK bir gelecek-bilgisi kullanilmamaktadir. **Sonuc: kirilim/tasma ANI GERCEK-ZAMANLI tespit
   edilmektedir, kanalin/genisligin BILINIRLIGI ise 5-bar-gecikmelidir — ikisi FARKLI
   kavramlardir ve bu backtestte ayri ayri, DOGRU modellenmistir.**
3. Giris fiyati = kirilim barinin KENDI kapanisi (gorev tanimi geregi, ek teyit bari
   BEKLENMEDI). Cikis taramasi entry_idx+1'den baslar (ayni barda hem karar hem SL/TP tetigi
   OLUSTURULMAMISTIR - bu, entry barinin ZATEN kapanmis olmasindan kaynaklanan dogal bir
   ayrimdir, ek bir varsayim degildir).

---

## ANA TEST TASARIMI / YONTEM (ADIM 3)

### Kanal Genisligi / Dis Sinir Tanimi (YENI, bu gorevde tasarlandi — bkz. ust uyari)

Her onaylanmis kanal icin, OLUSUM penceresinde (`anchor_idx -> confirm_idx_ham`, yani anchor'dan
3. dokunusun HAM (henuz 5-bar-gecikme uygulanmamis) barina kadar), trend cizgisinin KARSI
tarafindaki fiyat ucu (yukselen kanalda `high`, alcalan kanalda `low`) ile trend cizgisi
arasindaki dikey mesafenin MAKSIMUMU "kanal genisligi" olarak alindi. DIS sinir, onay sonrasi
her bar icin `trend_cizgisi(t) + yon*genislik` olarak sabit-genislikte projekte edildi. Bu,
Stratejist tarafindan tanimlanmamis (kaynak eksik) bir tasarim kararidir — Stratejist
onayina/duzeltmesine ACIKTIR.

### Giris

- HTF: H1 veya M30, HER IKI yon (simetrik). LTF: M15 (birincil, karar bu veriyle verildi),
  M5 (ikincil/capraz-kontrol — bkz. Sinirlamalar, M5 veri derinligi 2025-02-18'den once
  YOKTUR, bu daha once Arastirmaci tarafindan bagimsiz dogrulanmis bir MT5-hesap sinirlamasi).
- Tetik: bir LTF barinin kapanisi, aktif/kirilmamis kanalin DIS sinirini trend yonunde
  >=0,5xATR14(LTF) mesafede astiginda (ve bir onceki bar bu esigi asmiyorsa — TEK bar tetigi,
  rising-edge).
- Giris fiyati: tetigi olusturan barin KENDI kapanisi.

### Cikis (uc kosuldan HANGISI ONCE gerceklesirse, sirayla kontrol: SL -> TP -> erken-cikis)

1. **SL (false-breakout hizli cikis):** kirilan DIS sinirin (giris anindaki degeriyle SABIT)
   GERISINE, `SL_mult x ATR14(M15, giris)` mesafede.
2. **TP (ATR14-bazli dinamik hedef):** giris fiyatindan `TP_mult x ATR14(M15, giris)` mesafede.
3. **Kanala-geri-donus erken cikis (H5'e ozel, H4'un kuralinin TERS-CEVRILMISI — KARISTIRILMAMALI):**
   bar KAPANISI, o anki (guncel, projekte edilmeye devam eden) DIS sinirin GERISINE (kanalin
   icine) donerse, SL/TP beklenmeden kapatilir.
- Ayni barda SL VE TP araligina (high/low) girilmisse, MUHAFAZAKAR varsayimla SL kazanir
  (H2/H3 ile ayni konvansiyon).

### Lot / Risk (`justin_gecmis_calisma.md`)

Kasa=2000 USD (sabit, compounding modellenmedi — H2/H3 ile ayni basitlestirme, bkz.
Sinirlamalar), islem-basi risk ust siniri %1, lot = asagi-yuvarlanan(kasa x 0,01 / SL_pts),
taban 0,01 lot.

### Train / Validation / Test Ayrimi (purged/embargolu)

| Split | Baslangic | Bitis | Gun | M15 aday-giris (n) |
|---|---|---|---|---|
| Train | 2022-04-25 | 2024-06-05 | 772 | 453 |
| (embargo 45 gun) | | | | (40 aday embargoda dislandi) |
| Validation | 2024-07-20 | 2025-08-10 | 386 | 69 |
| (embargo 45 gun) | | | | |
| Test | 2025-09-24 | 2026-07-17 | 296 | 186 |

### N-Bar-Ileri Medyan Hareket Olcumu (TP baglami — TRAIN-ONLY, sizinti yok)

| Ufuk (M15 bar) | Saat karsiligi | n | Medyan MFE (ATR-birim) |
|---|---|---|---|
| 4  | 1  | 453 | 0,743 |
| 8  | 2  | 453 | 1,011 |
| 16 | 4  | 453 | 1,608 |
| 24 | 6  | 453 | 1,962 |
| 48 | 12 | 453 | 2,635 |

Bu olcum, TP grid'inin (1-4x ATR) makul bir aralikta oldugunu gosterir (12 saatlik ufukta
medyan lehte hareket ~2,6xATR) — ama walk-forward SECIMI PF'ye gore yapildi, bu tablo sadece
BAGLAM/capraz-kontrol amaclidir, dogrudan TP degerini BELIRLEMEDI.

---

## SONUCLAR

### Walk-Forward Grid Taramasi (SL x TP, Train -> Validation)

| SL (xATR) | TP (xATR) | Train n | Train PF | Validation n | Validation PF |
|---|---|---|---|---|---|
| 0,3 | 2,0 | 327 | 0,9082 | 56 | 0,7678 |
| 0,3 | 2,5 | 320 | 0,8160 | 54 | 0,7882 |
| 0,3 | 3,0 | 311 | 0,7887 | 53 | 0,8874 |
| 0,3 | 4,0 | 299 | 0,8747 | 52 | 0,9166 |
| 0,4 | 2,0 | 324 | 0,9032 | 55 | 0,7715 |
| 0,4 | 2,5 | 317 | 0,8100 | 53 | 0,7964 |
| 0,4 | 3,0 | 308 | 0,7737 | 52 | 0,8946 |
| **0,4** | **4,0** | **294** | **0,8963** | **51** | **0,9228 (SECILDI)** |
| 0,5 | 2,0 | 322 | 0,8872 | 55 | 0,7274 |
| 0,5 | 2,5 | 316 | 0,7995 | 53 | 0,7519 |
| 0,5 | 3,0 | 306 | 0,7510 | 52 | 0,8413 |
| 0,5 | 4,0 | 292 | 0,8727 | 51 | 0,8722 |

Secim kurali: Validation'da n>=30 sarti saglayan 12 hucrenin (grid'in tamami saglandi)
PF'si en yuksek olani -> **SL=0,4xATR14(M15), TP=4,0xATR14(M15)**.

**ONEMLI SINIRLAMA (grid-sinir etkisi):** Validation PF, TP arttikca (2,0->4,0) her SL
seviyesinde ARTAN bir egilim gosteriyor (orn. SL=0,4: 0,7715->0,7964->0,8946->0,9228); grid
TP=4,0'da SONLANDIGI icin, secilen deger grid'in UST SINIRINDA — gercek (grid-disi) optimum
daha yuksek bir TP'de olabilir, bu grid bunu TARAYAMAMISTIR. Bu, secilen parametrenin kesin
optimum degil, "denenen araligin en iyisi" oldugu anlamina gelir; asagidaki TUM PF degerleri
1,0'in ALTINDA kaldigi icin (bkz. asagi), bu grid-sinir etkisi sonucun YONUNU degistirmiyor
olabilir ama KESINLIK acisindan acikca belirtilmelidir.

### Secilen Kombinasyon (SL=0,4x, TP=4,0x) — Split Bazinda Sonuclar

| Metrik | Train | Validation | **Test (OOS, tek kez)** | Tam Donem (birlesik) |
|---|---|---|---|---|
| n islem | 294 | 51 | **126** | 502 |
| Win rate | %25,51 | %21,57 | **%18,25** | %23,31 |
| Profit Factor | 0,8963 | 0,9228 | **0,7353** | 0,8632 |
| Net kar/zarar (USD) | -1.589,12 | -171,77 | **-1.432,80** | -3.365,73 |
| Net (pts) | -2.619,2 | -5.183,9 | **-33.636,5** | -40.574,5 |
| Max Drawdown (%) | 109,28 | 28,84 | **76,14** | 156,00 |
| Medyan tutma suresi (saat) | 1,62 | 1,25 | **1,25** | 1,50 |
| Ortalama tutma suresi (saat) | 4,72 | 3,18 | **2,76** | 3,98 |
| Cikis: SL_FALSE_BREAKOUT | 137 | 20 | **66** | 239 |
| Cikis: TP | 74 | 11 | **22** | 115 |
| Cikis: KANALA_GERI_DONUS | 83 | 20 | **38** | 148 |
| **False-breakout sikligi** | %46,60 | %39,22 | **%52,38** | %47,61 |

**HEDEF karsilastirmasi (ham sayi, yorum degil):** HEDEF_PF=1,5 — hicbir split'te
saglanmiyor (en yuksek deger Validation'da 0,9228, PF'nin kendisi 1,0'in bile ALTINDA, tum
grid hucrelerinde de ayni durum gecerli — bkz. yukaridaki grid tablosu, hicbir hucre Train'de
PF>1,0'a ulasmiyor). HEDEF_DD=%20 (kumulatif) — Validation (%28,84) haric TUM split'lerde
asiliyor (Train %109,28, Test %76,14, Tam Donem %156,00).

**Max Drawdown %156 hakkinda ACIKCA belirtilmesi gereken bir notasyon-sinirlamasi:** Bu
simulasyon, H2/H3 ile AYNI basitlestirmeyi (statik `KASA_USD=2000`, compounding YOK, lot
kasa BUYUMESIYLE guncellenmeden sabit-formulle hesaplaniyor) kullanir. %100'u asan bir DD
degeri, gercek bir hesabin sifirin ALTINA duserek islem yapmaya devam ettigi ANLAMINA GELMEZ
(gercekte DD-stop, `justin_gecmis_calisma.md` geregi %20'de devreye girip islemi durdururdu)
— bu sayi, DD-stop UYGULANMADAN ("tum sinyaller islenirse ne olurdu") hesaplanmis HAM bir
rakamdir, canli bir hesabin gercekte yasayacagi kayip DEGILDIR. Bu notasyon farki Risk
Analisti'ne acikca iletilmelidir.

---

## ISLEM FREKANSI

- Tam donem (train+val+test birlikte, tek-pozisyon kurali TUM eksende): **502 islem**,
  ~9,84 islem/ay, ~119,84 islem/yil.
- Bu, Tam Tur 1'deki H1/H2/H3'un yillik kanal-sayisina dayali dusuk frekansindan (2,9-6,8
  kanal/yil) BELIRGIN sekilde YUKSEK — H5, kanal SAYISINA degil kanal-ICI tasma OLAYLARINA
  dayandigi icin (bir kanal aktifken birden fazla tasma olusabiliyor, bkz. ADIM 0), islem
  sikligi scalping-beklentisine (sik islem) H1-H3'e gore daha yakin.
- Kirilim (HTF) kaynagi bazinda: H1=191 islem (WR %27,75, PF_pts=0,8442), M30=311 islem
  (WR %20,58, PF_pts=0,8421). Yon bazinda: yukselen=266 islem (WR %27,07, PF_pts=0,867),
  alcalan=236 islem (WR %19,07, PF_pts=0,812).

---

## A/C SINIR NETLIGI NOTU (ZORUNLU)

Bu rapor boyunca test edilen mekanizma, **A ailesinin (Momentum/Trend-Following) ICINDE,
zaten onaylanmis bir H1/M30 yapisal kanali REJIM-FILTRESI olarak KULLANAN, kanal-disina
kirilim anini giris-tetigi olarak degerlendiren bir varyanttir.** Bu, Ertan'in 14 Temmuz
2026 A/C duzeltmesi geregi **C ailesinin (Breakout Order, Proje 9) ayri/bagimsiz bir
canlanmasi DEGILDIR** — C, A'nin icinde yer yer kullanilabilecek bir EK ARAC olarak
tanimlanmisti (`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`, Bolum 2); H5 bu
tanima uygun sekilde, A'nin rejim-filtresi (onaylanmis kanal) mantigina bagimli kalarak
kirilimi bir giris-zamanlama detayi olarak kullanmaktadir. Proje 9 (Breakout Order) ile
KARISTIRILMAMALIDIR — bu iki ayri proje/kavramdir.

---

## RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — H5 "Kanal-Disi Kirilim Girisi" — Kural-tabanli (A ailesi ici varyant) — 19 Temmuz 2026

ON-TARAMA: 748 tasma olayi (M15, 4 HTF/yon kombinasyonu, hicbiri tek haneli degil) -> devam edildi.
ON-KONTROL: DST tutarli (H2/H3 ile), S1 TP>=2,0xATR'de gecti (15,34x), SL/TP otomatik tasinmadi.

Train (In-Sample):
  n=294, WR=%25,51, PF=0,8963, Net=-1.589,12 USD, MaxDD=%109,28 (DD-stop UYGULANMADAN ham deger)

Gorulmemis Veri (Validation + Test, tek-kez):
  Validation: n=51, WR=%21,57, PF=0,9228, Net=-171,77 USD, MaxDD=%28,84
  Test (OOS): n=126, WR=%18,25, PF=0,7353, Net=-1.432,80 USD, MaxDD=%76,14, False-breakout sikligi=%52,38

Dikkat noktalari:
  - HICBIR split'te (grid'in HICBIR hucresinde) PF>=1,0'a ulasilmiyor - bu, overfitting'den
    once, grid'in TAMAMINDA sistemik bir durum (Train de dahil in-sample).
  - PF, Train(0,8963)->Validation(0,9228)->Test(0,7353) sirasinda DUSUYOR (OOS'ta daha da
    zayifliyor) - klasik OVERFITTING_RISKI paterniyle KISMEN tutarli, ama Train zaten <1,0
    oldugu icin bu "in-sample'da iyi, OOS'ta kotu" degil, "her yerde zayif, OOS'ta en zayif" paterni.
  - Secilen TP (4,0xATR) grid'in UST SINIRINDA - gercek optimum grid-disi olabilir, taranmadi.
  - Kanal genisligi/DIS SINIR tanimi Stratejist'in eksik kaynak dosyasi nedeniyle Backtest
    Muhendisi tarafindan SIFIRDAN tasarlandi (varsayim, Stratejist onayina acik).
  - Max Drawdown rakamlari DD-stop mekanizmasi UYGULANMADAN hesaplanmis HAM degerlerdir (bkz. rapor).
  - False-breakout (SL) sikligi yuksek (%40-52 arasi tum split'lerde).
  - Islem frekansi H1-H3'e gore belirgin yuksek (~120/yil, medyan tutma ~1,25-1,6 saat) - scalping
    tutma-suresi karakterine H1-H3'ten daha yakin.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_tur2_H5_20260719.md
Ham veri/script: backtest_H5_adim0_ontarama.py(+_output.json), backtest_H5_main.py(+_output.json),
                 backtest_H5_islem_logu_tam.csv
```

---

## UYARILAR (ozet, tekrar)

1. **Kaynak dosya eksikligi** (bkz. rapor basi) — bu raporun "dogrudan kaynagi" sayilan
   Stratejist dosyasi bulunamadi; bu raporun ADIM1-3 tasarimi Orkestrator cagrisina ve Tam
   Tur 1/H2-H3 metodolojisine dayanir, eksik dosyanin notlari (1-10) HESABA KATILAMADI.
2. **Kanal genisligi/DIS SINIR tanimi Stratejist tarafindan onaylanmamis bir VARSAYIMDIR**
   (bu gorevde tasarlandi) — tum sayisal sonuclar bu varsayima baglidir; farkli bir genislik
   tanimi (orn. paralel-kanal regresyonu, sabit ATR-carpani genislik, vb.) FARKLI sonuclar
   verebilir.
3. **Grid-sinir etkisi:** secilen TP (4,0xATR) grid'in ust sinirinda; daha genis bir TP grid'i
   (orn. 5-8xATR) test edilmemistir.
4. **M5 (ikincil/capraz-kontrol) veri derinligi sinirlidir** (2025-02-18 oncesi GOLD M5 verisi
   bu MT5 hesabinda YOKTUR — Arastirmaci tarafindan onceden bagimsiz dogrulanmis bir bulgu,
   bkz. `arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_raporu.md`); M5 sonuclari bu
   raporda SADECE ADIM 0 olay-sayimi olarak verildi, tam walk-forward simulasyonu M5 icin
   YAPILMADI (gorev tanimindaki "ikincil/capraz-kontrol" rolune uygun).
5. **Compounding/DD-stop modellenmedi** (H2/H3 ile ayni basitlestirme) — Max Drawdown
   rakamlari HAM'dir, gercek bir hesabin DD-stop sonrasi yasayacagi kaybi TEMSIL ETMEZ.
6. **Tasma olaylari BAGIMSIZ DEGILDIR** — ayni kanal penceresi icindeki ardisik tasma
   olaylari zaman/fiyat olarak otokorelasyonlu olabilir (H1/H2/H3'teki ayni turden bir
   sinirlama, Arastirmaci'nin ic-ice-kanal bulgusuyla tutarli).
7. **Minimum orneklem:** Validation'da n=51-69 (H2/H3'teki 30 esigini asar ama H1'in
   kirilganligina gore daha genis, yine de "buyuk" bir orneklem degil); Test'te n=126,
   istatistiksel olarak daha anlamli ama tek bir donemi (296 gun, 2025-09/2026-07) yansitir.

---

## IZOLASYON NOTU

Bu rapor ve uretilen scriptler yalnizca `C:\MilaYatirim\Justin\` klasoru icinde calisilmis,
tek veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD sembolu ham OHLCV
verisi kullanilmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, deger veya format/sablon
referans olarak ACILMAMISTIR. Kanal tespit algoritmasi (metodolojik olarak), ayni-proje-ici
H2/H3 backtest scriptleriyle ve Arastirmaci'nin pivot/kanal tarama scriptleriyle TUTARLI
tutulmustur (karsilastirilabilirlik amacli, izolasyon ihlali degil — kural yalniz BASKA
proje dosyalarini yasaklar).

---

## ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (on-tarama dahil),
canli sisteme dokunus YOK, Justin arastirma asamasinda (canli/demo hesap henuz baglanmadi).
4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu
degil, etki alani dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan
onayi gerekmez. **Ek olarak:** kaynak-dosya eksikligi ve kanal-genisligi varsayimi nedeniyle,
bu raporun Stratejist tarafindan gozden gecirilmesi (ozellikle DIS SINIR tanimi ve eksik
"NOTLAR 1-10" icin) ONERILIR — bu bir onay-engeli degil, seffaflik/tamlik notudur.

---

## EK DOSYALAR

- `C:\MilaYatirim\Justin\backtest_H5_adim0_ontarama.py` (ADIM 0 script)
- `C:\MilaYatirim\Justin\backtest_H5_adim0_ontarama_output.json` (ADIM 0 ham veri)
- `C:\MilaYatirim\Justin\backtest_H5_main.py` (ADIM 1-3 script)
- `C:\MilaYatirim\Justin\backtest_H5_main_output.json` (ADIM 1-3 ham veri, tum FAZ'lar)
- `C:\MilaYatirim\Justin\backtest_H5_islem_logu_tam.csv` (tam islem logu, 502 satir)
