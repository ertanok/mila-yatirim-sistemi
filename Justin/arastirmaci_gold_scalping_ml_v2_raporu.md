# ARASTIRMACI RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile (M15+), v2 (ML Tam Tur 2)

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
Pipeline adimi: 1/4 (Arastirmaci)
Tarih: 12 Temmuz 2026 (VPS-yerel)
Gorev kaynagi: `gorev_arastirmaci_justin_gold_scalping_ml_v2.md` (ML ailesi Tam Tur 1'in — Hipotez
1/2/3, ucu de RED — ayni patern uzerine acilan Tam Tur 2'nin ilk adimi)
Veri kaynagi: XM/MT5, dogrudan MetaTrader5 kutuphanesi. GOLD M15 (99.999 bar, 2022-04-18 →
2026-07-10, ~4,2 yil, v1 ile AYNI seri) + USDX-SEP26 futures (M15, 99.999 bar donen veri —
"veri erisimi kismi/sinirli" notuyla, bkz. BULGU 6 ve SINIR) + GOLD tick verisi (yalniz son 20
islem gunu, mikro-yapi bolumu icin, bkz. BULGU 7-9 ve SINIR).
Analiz script'i: `research_ml_gold_scalping_m15_v2.py` (ham cikti:
`research_ml_gold_scalping_m15_v2_output.json`)

**Kutuphane durumu guncellemesi:** v1 raporunda `pandas`/`lightgbm`/`scikit-learn`/`xgboost` bu
ortamda KURULU DEGIL denmisti (Riskler Madde 1). Bu turde dogrulandi: **artik hepsi kurulu**
(pandas 3.0.3, lightgbm 4.6.0, scikit-learn 1.9.0, MetaTrader5 5.0.5735). Bu rapor bu nedenle
pandas kullanmistir (v1'in yalniz-numpy kisitindan farkli); yine de bu rapor GERCEK BIR MODEL
EGITMEMISTIR — model egitimi/hiperparametre araStirmasi hala Backtest Muhendisi'nin isidir, bu
sadece feature/label OLCUM asamasidir.

**Gecmis calisma kontrolu:** Bu gorev icin su dosyalar okundu: `arastirmaci_gold_scalping_ml_
raporu.md` (v1 — hangi feature ailelerinin ZATEN denendigi), `risk_analisti_raporu_justin_gold_
scalping_ml_v1_hipotez1/2/3_20260712.md` (Tam Tur 1'in RED gerekceleri, Stratejiste Geri Bildirim
bolumleri), `justin_gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md`, `justin_
backtest_onkontrol_standardi.md`, `justin_gold_scalping_karar_ve_governance_20260714.md`. Bu
rapor v1'in olcmedigi/kullanmadigi feature ailelerine ODAKLANIR — v1'deki BULGU 1-11 (ATR/
spread/hacim saatlik profili, MTF confluence, RSI/MACD, HH/LL, triple-barrier taban dagilimi,
maliyet-orani) BURADA TEKRAR OLCULMEMISTIR, sadece gerektiginde referans verilmistir (orn.
maliyet-orani, gorev tanimi geregi tekrar hesaplanmadi).

---

## OZET

1. ADX(14)-tabanli rejim siniflandirmasi (trend/range/gecis) veri setinin ~%45'ini trend,
   ~%35'ini range, ~%20'sini gecis olarak etiketler; trend rejiminde sonraki-2-saatlik mutlak
   hareket (345 puan medyan) range rejimine (296 puan) gore ~%16,6 daha buyuktur — ANCAK yon-
   sureklilik orani (mevcut bar yonunun sonraki-8-bar yonuyle ayni olma orani) HER UC rejimde de
   ~%49,0-49,9 ile RASSAL SEVIYEYE (%50) cok yakindir; ADX rejim etiketi buyukluk (volatilite)
   bilgisi tasir ama yon-devam bilgisi TASIMAMAKTADIR.
2. Gunluk/haftalik pivot noktalari ve 20-gunluk rolling S/R mesafesi olculdu (v1'de YOKTU): fiyat
   20-gunluk en-yuksege yakinken (en yakin %10'luk dilim, n=9.820) sonraki-2-saatlik yon-hizali
   getiri medyani +52 puan (belirgin momentum/devam egilimi), fiyat 20-gunluk en-dusuge yakinken
   (n=9.817) medyan -2 puan (belirgin bir yon YOK) — bu asimetri (yuksekte devam var, dusukte
   yok) genel yukari-onyargisiyla (v1 BULGU 8) tutarli olabilir.
3. Capraz-piyasa (USDX-SEP26, dolar endeksi futures proxy) es-zamanli M15 getiri korelasyonu
   GOLD ile GUCLU negatif (-0,41 tam-donem, rolling-20 medyan -0,46) — ANCAK onceki-8-bar DXY
   getirisi ile SONRAKI-8-bar GOLD getirisi arasindaki ONGORUCU (lead-lag) korelasyon PRATIKTE
   SIFIR (-0,0008, n=90.592). Es-zamanli iliski guclu, ongorucu iliski yok — bu iki farkli sey,
   feature tasarimi acisindan kritik bir ayrim (bkz. BULGU 6 BAGLAM).
4. Mikro-yapi (tick-kural-tabanli bid/ask "imbalance" proxy'si, GERCEK order-flow/trade-side
   verisi YOK — bu bir quote-tick feed'i) sinirli bir pencerede (son 20 islem gunu, n=1.260 M15
   bucket) olculdu: yuksek-imbalance (en ust %20) barlarini takip eden 2-saatlik getiri medyani
   -254 puan iken dusuk-imbalance (en alt %20) barlarinda +4 puan — buyuk bir medyan farki, ANCAK
   dogrudan korelasyon zayif (-0,032) ve orneklem kucuk (n=251/grup, 20 gunluk pencere) — bu,
   guclu bir sinyal olarak DEGIL, arastirilmaya deger ama dogrulanmamis bir gozlem olarak
   sunulmaktadir.
5. Tick-seviyesi ortalama spread (gun-ici tum ticklerin ortalamasi, 54,8 puan medyan) v1'in
   bar-kapanis-anlik spread medyanindan (27-33 puan) ~%66-100 daha genistir — bu, v1'in maliyet-
   orani on-tahmininin (BULGU 11, medyan bar-kapanis spread'i uzerinden) intraday ortalama
   maliyeti hafife alabilecegine dair ek bir kanittir.
6. Alternatif 3-sinifli (deadzone-tabanli, triple-barrier'DAN FARKLI bir yontem) etiket, k=0,3x
   ATR14 deadzone'unda %43,9 yukari / %40,5 asagi / %15,6 notr dagilimi verir — nispeten dengeli.
   Regresyon-hedefi (N=8 bar ileri getiri) dagilimi asiri gurultuludur: ortalama 17,0 puan, std
   1.252,6 puan (std/ortalama ~74x) — sinyal/gurultu orani cok dusuktur, bu v1'in AUC~0,50-0,52
   bulgusuyla NITEL olarak tutarlidir.

---

## GOZLEMLER

### BULGU 1 — ADX(14) Rejim Siniflandirmasi ve Dagilimi (YENI feature ailesi, v1'de YOKTU)
Veri Kaynagi: GOLD M15, 99.999 bar. ADX(14) standart Wilder tanimiyla (TR/+DM/-DM Wilder-smooth,
DI+/DI-, DX, ADX = DX'in Wilder-smoothed ortalamasi) nedensel hesaplandi (yalniz i ve oncesi).
Esikler: ADX>25 "trend", ADX<20 "range", arasi "gecis" (standart/kamuya-acik esikler, MilaGold'a
ozel degil).
---------------------------------------------------------------
GOZLEM:
| Rejim | n | Oran | 
|---|---|---|
| Trend (ADX>25) | 44.944 | %44,96 |
| Range (ADX<20) | 35.386 | %35,40 |
| Gecis (20-25) | 19.642 | %19,65 |

ADX medyan=23,60, P10/P90=[13,75 / 41,06].

BAGLAM: ADX dagilimi "trend" tarafina hafif kaymis (yaklasik %45 vs %35) — bu, GOLD M15'in tam
rastgele-yurüyus degil, zaman zaman belirgin trend fazlari gecirdigini gosterir (buyukluk
olcumu, yon degil). ADX medyaninin (23,60) tam "trend/range" sinirinda (20-25 gecis bandi
icinde) olmasi, esik secimine (25/20) sonucun orta derecede duyarli olabilecegine isaret eder.

SINIR: 25/20 esikleri standart/kamuya-acik degerlerdir, bu veri setine ozel optimize
edilmemistir — farkli esikler dagilimi degistirir. Wilder ADX ilk ~28 bar (2xADX_N) icin
tanimsizdir (n_valid=99.972, toplam 99.999'un %99,97'si).

### BULGU 2 — Rejime Gore Sonraki-8-Bar (2 Saat) Mutlak Hareket ve Yon-Sureklilik Orani
Veri Kaynagi: Ayni ADX rejim etiketi; sonraki 8-M15-bar mutlak getiri (buyukluk) VE mevcut barin
kapanis-yonu ile sonraki-8-bar kapanis-yonunun AYNI OLMA orani (sureklilik/continuation).
---------------------------------------------------------------
GOZLEM:
| Rejim | Sonraki-8-bar Mutlak Getiri Medyan (pts) | n | Yon-Sureklilik Orani | n (sureklilik) |
|---|---|---|---|---|
| Trend | 345,0 | 44.944 | %48,99 | 44.788 |
| Range | 296,0 | 35.386 | %49,76 | 35.232 |
| Gecis | 332,0 | 19.634 | %49,91 | 19.556 |

BAGLAM: Trend rejiminde sonraki hareketin BUYUKLUGU range'e gore ~%16,6 daha fazladir (345 vs
296 puan) — bu, ATR-tabanli genis/dar rejim bulgusuyla (v1 BULGU 4, ~%27,7 fark) AYNI yonde ama
DAHA ZAYIF bir volatilite-kumelenmesi sinyalidir (ADX farkli bir olcum oldugu icin beklenen bir
fark). ANCAK yon-sureklilik orani UCUNDE de %48,99-49,91 araliginda, yani RASSAL YAZI-TURA
SEVIYESINE (%50) pratik olarak esittir — ADX rejim etiketi (trend dahil) bir sonraki hareketin
YONUNU ONGORMEMEKTEDIR, sadece BUYUKLUGUNU zayif sekilde ongormektedir.

SINIR: "Sureklilik" burada sadece mevcut-bar-yonu ile sonraki-8-bar-yonu karsilastirmasidir — bu,
"trend rejiminde fiyat trend yonunde devam eder" varsayiminin NAIF bir testidir (ADX'in kendi
yon bilgisi, +DI/-DI farki, ayrica test edilmedi — bu bir ACIK SORU, asagida).

### BULGU 3 — Rejim Gecis Mesafesi (Bars-Since-Regime-Change)
Veri Kaynagi: Ayni ADX rejim serisi; her bar icin son rejim degisiminden bu yana gecen bar
sayisi (nedensel, sadece gecmis regime etiketleri kullanilarak).
---------------------------------------------------------------
GOZLEM: Medyan=11,0 bar (2 saat 45 dk), P90=45,0 bar (11 saat 15 dk).

BAGLAM: Rejimler ortalama ~11 bar surmektedir (medyan), ancak P90'in (45 bar) medyanin 4 katindan
fazla olmasi, rejim sürelerinin sag-carpik (bazi rejimlerin cok uzun surdugu) bir dagilima sahip
oldugunu gosterir.

SINIR: Bu metrik, ADX'in kendi gecis (20-25) bandinin "titresim" (flip-flop) davranisina
duyarlidir — ADX 20-25 araliginda salinirsa "gecis" rejiminde kisa-omurlu sik degisimler
olusabilir; bu ayristirilmamistir (bir ACIK SORU).

### BULGU 4 — Gunluk/Haftalik Pivot Mesafesi ve Pivot-Ustu/Alti Yon-Hizali Getiri (YENI, v1'de YOKTU)
Veri Kaynagi: Standart pivot formulu (P=(H+L+C)/3, R1=2P-L, S1=2P-H), ONCEKI TAMAMLANMIS gunun
H/L/C'sinden hesaplanip BUGUNE (nedensel, shift) atanmistir; haftalik pivot ayni mantikla ONCEKI
TAMAMLANMIS ISO-haftadan.
---------------------------------------------------------------
GOZLEM:
| Referans | Mesafe Medyan (mutlak, pts) | n |
|---|---|---|
| Gunluk Pivot | 912,0 | 99.918 |
| Gunluk R1 | 1.570,0 | 99.918 |
| Gunluk S1 | 1.848,3 | 99.918 |
| Haftalik Pivot | 2.580,0 | 99.550 |

Pivot-ustu barlarda (n=55.005) sonraki-8-bar yon-hizali getiri medyani +11,0 puan; pivot-alti
barlarda (n=44.898) +25,0 puan (her ikisi de POZITIF — genel yukari-onyargisiyla, v1 BULGU 8,
tutarli).

BAGLAM: Gunluk pivot mesafesi (medyan ~912 puan) ATR14 medyanindan (v1 BULGU 1, ~287 puan) ~3,2
kat daha genistir — yani fiyat gun-ici pivottan tipik olarak birkac ATR uzakta seyretmektedir,
pivot "yakinlik" esigi tanimlanirken bu olcek dikkate alinmalidir. Pivot-ustu/alti ayriminin
sonraki getiri BUYUKLUGUNE (yon degil, mutlak fark) belirgin bir etkisi bu olcumde
GOZLENMEMISTIR (ikisi de pozitif, farkli buyuklukte ama ikisi de genel onyargiyla ayni yonde).

SINIR: Sadece 1-gun/1-hafta gerikalim (lag) pivotu test edildi; cok-gunluk/cok-haftalik (orn.
aylik) pivot varyantlari olculmedi. Gun/hafta siniri GMT+3 varsayimina dayanir (DST bagimsiz
dogrulanmadi, v1 ile AYNI SINIR).

### BULGU 5 — 20-Gunluk Destek/Direnc (Rolling High/Low) Yakinligi ve Getiri Asimetrisi (YENI)
Veri Kaynagi: 20-onceki-TAMAMLANMIS-gunun rolling en-yuksek/en-dusuk degeri (nedensel, shift),
mesafenin en yakin %10'luk dilimi "yakin" olarak tanimlandi.
---------------------------------------------------------------
GOZLEM: 20-gun en-yuksege yakin barlarda (n=9.820) sonraki-8-bar yon-hizali getiri medyani
+52,0 puan; 20-gun en-dusuge yakin barlarda (n=9.817) medyan -2,0 puan.

BAGLAM: Fiyat 20-gunluk yuksege yaklastiginda sonraki hareket BELIRGIN sekilde yukari yonlu
(medyan +52 puan, ATR14 medyaninin (~287 puan) yaklasik %18'i) — bu bir "breakout-momentum"
paterni ile tutarlidir. Fiyat 20-gunluk dusuge yaklastiginda ise net bir yon YOKTUR (medyan ~0'a
cok yakin, -2 puan) — ne guclu bir "destek-sicramasi" (reversal) ne de guclu bir "kirilma-devami"
(breakdown) paterni bu medyan olcumunde gorulmemektedir. Bu asimetri (yuksekte momentum var,
dusukte yok), genel yukari-yonlu onyargiyla (v1 BULGU 8) ayni yonde bir gozlemdir.

SINIR: "Yakin" tanimi (en yakin %10'luk dilim) tek bir esik secimidir; 20-gunluk pencere de tek
bir parametre secimidir (10/50 gun gibi alternatifler test edilmedi). Bu, MEDYAN uzerinden bir
gozlemdir — dagilimin sag/sol kuyruklarindaki (P10/P90) davranis ayrica incelenmedi.

### BULGU 6 — Capraz-Piyasa (USDX-SEP26/Dolar Endeksi Futures Proxy) Korelasyon Analizi (YENI, v1'de YOKTU)
Veri Kaynagi: MT5 sembolu "USDX-SEP26" (ABD Dolar Endeksi Eylul-2026 vadeli islem sozlesmesi,
tek erisilebilir DXY-benzeri sembol — bkz. SINIR), M15, GOLD ile TAM AYNI epoch-zaman damgasi
uzerinden birlestirildi (exact merge, n=90.608/99.999 GOLD bari, %90,6 ortusme).
---------------------------------------------------------------
GOZLEM:
| Olcum | Deger | n |
|---|---|---|
| Es-zamanli M15 getiri korelasyonu (tam donem) | -0,4116 | 90.607 |
| Rolling-20-bar korelasyon medyani | -0,4611 | - |
| Rolling-20-bar korelasyon P10/P90 | [-0,7641 / -0,0418] | - |
| Onceki-8-bar DXY getirisi vs sonraki-8-bar GOLD getirisi (ongorucu/lead-lag) | -0,0008 | 90.592 |

BAGLAM: GOLD ve DXY arasinda GUCLU ve TUTARLI bir ES-ZAMANLI (ayni M15 bar icindeki) negatif
korelasyon vardir (-0,41 ortalama, rolling-20 medyan -0,46, P10/P90 araligi hep negatif tarafta:
[-0,76 / -0,04]) — bu, dolar guclenirken altinin ayni anda zayiflama (ve tersi) egiliminin bu
veri setinde de dogrulandigini gosterir (genel/kamuya-acik makro iliski). ANCAK bu ES-ZAMANLI
iliski, bir ONGORUCU (predictive) iliskiyle KARISTIRILMAMALIDIR: onceki 8 bar boyunca DXY'nin
hareket yonu/buyuklugu, sonraki 8 bar boyunca GOLD'un hareketiyle PRATIKTE HICBIR iliski
gostermemektedir (korelasyon -0,0008, sifira essiz yakin, n=90.592). Bir ML feature'i olarak
DXY'nin GECMIS hareketi (nedensel/causal, ileri-bakis yok) kullanilirsa, bu olcume gore
GOLD'un GELECEK yonunu tahmin etmede ZAYIF/SIFIR katki saglayacagi beklenir — DXY'nin sadece
ES-ZAMANLI (bar-ici, hem GOLD hem DXY'nin AYNI ANDA kapandigi) degeri kullanilirsa (ki bu M15
bar henuz kapanmadan bir islem karari icin kullanilamaz, LOOK-AHEAD riski tasir) daha guclu bir
iliski gorulür ama bu pratikte KULLANILAMAZ bir bilgidir.

SINIR (ONEMLI — veri erisimi kaydi): "USDX-SEP26" sembolunun kendi `symbol_info().start_time`
alani 2026 ortasi bir tarihe (Haziran 2026 civari) isaret etmektedir (vadeli islem sozlesmesinin
RESMI baslangici), ANCAK MT5 `copy_rates_from_pos` sorgusu bu sembol icin 2021-11-10'a kadar
giden 99.999 barlik bir seri DONDURMUSTUR. Bu, brokerin bu sembol icin GERIYE DONUK/SPLICE
EDILMIS (surekli-kontrat) bir grafik serisi sagladigini, sembolun KENDI GERCEK islem gecmisinin
bundan cok daha kisa oldugunu dusundurmektedir — bu rapor bu ayrimi BAGIMSIZ olarak DOGRULAYAMADI
(broker'in surekli-kontrat olusturma yontemi bilinmiyor). Bu nedenle BULGU 6'daki sayilar
"kismi/dogrulanmamis-kaynak" notuyla sunulmaktadir — Backtest Muhendisi asamasinda bu serinin
gercekten kullanilabilir/guvenilir olup olmadigi (orn. roll-over sicramalari, veri sürekliligi)
AYRICA dogrulanmalidir. Yalniz MT5/XM uzerinden erisilebilen TEK dolar-endeksi-benzeri sembol
budur (digger USDX kontratlari mevcut degil, bkz. Acik Sorular).

### BULGU 7 — Mikro-Yapi: Tick-Kural-Tabanli Bid/Ask "Imbalance" Proxy'si (YENI, SINIRLI PENCERE)
Veri Kaynagi: GOLD tick verisi (`copy_ticks_range`), SADECE SON 20 ISLEM GUNU (2026-06-21 →
2026-07-10, tam 4,2 yillik GOLD M15 serisinin cok kucuk bir alt-kumesi — bkz. SINIR). Bu feed
GERCEK trade-side/order-flow verisi ICERMEMEKTEDIR (her tick icin volume=0, last=0 — sadece
bid/ask kotasyon degisimi). Bu nedenle "imbalance" burada ORTA-FIYAT (mid=(bid+ask)/2) ardisik
hareketinin isaretinin (tick-rule: yukari kotasyon degisimi=+1, asagi=-1, degisim-yoksa bir
onceki isareti tasi) M15-bucket icindeki ORTALAMASIDIR — gercek alici/satici baskisi degil, bir
PROXY'dir (gorev tanimindaki "gercek order-flow verisi yoksa tick-kural-tabanli bir yaklasim"
notuyla ORTUSUYOR).
---------------------------------------------------------------
GOZLEM: Toplam M15-bucket=1.260, bucket-basi medyan tick sayisi=4.520,5. Imbalance medyan=
0,0027 (hafif alici-egilimli, sifira cok yakin), P10/P90=[-0,0407 / +0,0610].

Yuksek-imbalance (en ust %20, n=251) barlarini takip eden 8-bar (2 saat) yon-hizali getiri
medyani: **-254,0 puan**. Dusuk-imbalance (en alt %20, n=251) barlarini takip eden: **+4,0
puan**. Dogrudan (kesikli olmayan) korelasyon: imbalance vs sonraki-8-bar getiri = -0,0315
(n tum gecerli bucket).

BAGLAM: Ust-alt-%20 dilim karsilastirmasinda BUYUK bir medyan farki (-254 vs +4 puan)
gozlenmektedir — bu, "asiri yuksek kisa-vadeli alici-baskisi"ndan sonra GERI-DONUS (mean-
reversion/tersine-donme) egilimine isaret edebilecek bir gozlemdir. ANCAK bu farkin BUYUKLUGU,
dogrudan (tum-orneklem) korelasyonun ZAYIFLIGIYLA (-0,0315) CELISIR GIBI GORUNMEKTEDIR — bu,
medyan-fark gozleminin birkac BUYUK-BUYUKLUKTE outlier bar tarafindan yonlendirilmis olabilecegi
anlamina gelebilir (n=251 gorece kucuk bir orneklemdir). Bu, GUCLU bir sinyal olarak DEGIL,
ARASTIRILMAYA DEGER ama DOGRULANMAMIS bir on-gozlem olarak sunulmaktadir.

SINIR: Bu olcum SADECE son 20 islem gunune (n=1.260 bucket) dayanir — bu, GOLD M15 serisinin
tamaminin (~99.999 bar) sadece ~%1,3'udur. 4,2 yillik tam-tarihsel bir tick-tabanli feature
seti icin gereken veri hacmi (gunde ~480.000 tick x ~1.000+ islem gunu = yuz milyonlarca tick)
BU ORTAMDA PRATIK OLARAK CEKILEMEZ/ISLENEMEZ (bkz. Riskler Madde 2 ve Acik Sorular) — bu
feature ailesinin TAM GECMIS ustunde nasil olceklenecegi (orn. M1-bar-tabanli daha kaba bir
proxy'ye indirgeme) Backtest Muhendisi/Stratejist tarafindan ayrica karara baglanmalidir.

### BULGU 8 — Tick-Ici Mikro-Volatilite (Mid-Return Std) ve Sonraki Hareket Iliskisi
Veri Kaynagi: Ayni 20-gunluk tick penceresi; her M15-bucket icin tick-bazli mid-fiyat getirisinin
(pct_change) standart sapmasi ("bar-ici mikro-volatilite", SADECE OHLC'den degil tick-yogunluklu).
---------------------------------------------------------------
GOZLEM: mid_ret_std medyan=1,847e-05 (yaklasik %0,0018 bar-ici tick-getiri std'si). Bu deger ile
sonraki-8-bar MUTLAK getiri arasindaki korelasyon: +0,0618 (zayif pozitif).

BAGLAM: Tick-ici mikro-volatilite ile sonraki 2-saatlik mutlak hareket arasinda ZAYIF ama POZITIF
bir iliski gozlenmistir — bu, v1'in ATR-tabanli genis/dar rejim bulgusuyla (BULGU 4, volatilite
kumelenmesi) NITEL olarak AYNI yonde ama COK DAHA ZAYIF bir sinyaldir (korelasyon katsayisi
0,0618 kucuk bir etki buyuklugudur).

SINIR: Ayni 20-gunluk sinirli pencereye dayanir (bkz. BULGU 7 SINIR). Zayif korelasyon, kucuk
orneklem (n~1.260 bucket) ile birlikte guvenilirligi sinirlar.

### BULGU 9 — Tick-Seviyesi Ortalama Spread vs Bar-Kapanis Spread Karsilastirmasi
Veri Kaynagi: Ayni 20-gunluk tick penceresi; her M15-bucket icindeki TUM ticklerin ask-bid
farkinin ORTALAMASI (gun-ici tum kotasyon degisimlerinin ortalamasi), v1'in bar-KAPANIS-ANI
spread degeriyle (MT5'in `spread` alani, sadece bar kapanirken tek bir anlik deger) karsilastirma
amacli.
---------------------------------------------------------------
GOZLEM: Tick-seviyesi ortalama spread medyani = 54,82 puan (0,5482 fiyat birimi / 0,01 point).
v1 BULGU 1'deki bar-kapanis spread medyanlari: 27-33 puan (saate gore degisken).

BAGLAM: Gun-ici TUM kotasyonlarin ortalamasi (54,82 puan), bar-kapanis anindaki TEK BIR OLCUMUN
medyanindan (27-33 puan) YAKLASIK 1,7-2,0 KAT DAHA GENISTIR. Bu, v1 BULGU 11'de zaten not edilen
("canli/anlik spread 53 pts, medyanin ~2 kati") gozlemle SAYISAL OLARAK ORTUSMEKTEDIR (54,82 ≈
53) — yani bar-kapanis-anindaki medyan spread olcumu, GERCEK intraday ortalama maliyeti hafife
alan bir olcum olabilir; bu iki BAGIMSIZ olcum (v1'in canli-an-gozlemi vs bu raporun 20-gunluk
tick-ortalamasi) BENZER bir sonuca ULASMISTIR.

SINIR: Ayni 20-gunluk pencereye dayanir. Bu, spread'in kendisidir (slipaj DEGILDIR) — gercek
execution slipaji hala olculmemistir (v1 Acik Soru 6 ile AYNI bosluk).

### BULGU 10 — Etiket Alternatifi: 3-Sinifli (Deadzone-Tabanli) Etiket Dagilimi (YENI yontem —
TRIPLE-BARRIER DEGIL)
Veri Kaynagi: N=8 bar (2 saat) ileri getiri, kendi bari ATR14'unun (basit/nedensel rolling-
ortalama, Wilder DEGIL) k katindan buyukse "yukari" (1), kucukse "asagi" (-1), aradaysa "notr"
(0). **ONEMLI AYRIM (governance/sayisal-tutarlilik geregi):** Bu, v1 BULGU 10'daki TRIPLE-
BARRIER (TP/SL'den HANGISI ONCE tetiklenir) yontemiNDEN FARKLI bir etiket tanimidir — burada
SABIT bir N-bar ufkunda (barrier yok, sadece son-nokta getirisi) deadzone uygulanir. Bu iki
sayi/oran DOGRUDAN KARSILASTIRILMAMALIDIR (farkli hesaplama yontemleri, bkz. CLAUDE.md "Agent'lar
arasi sayisal tutarlilik" kurali).
---------------------------------------------------------------
GOZLEM:
| Deadzone (k x ATR14) | Yukari | Asagi | Notr |
|---|---|---|---|
| 0,15 | %47,75 | %44,42 | %7,84 |
| 0,30 | %43,86 | %40,54 | %15,61 |
| 0,50 | %38,78 | %35,60 | %25,61 |

BAGLAM: Deadzone genisledikce ("notr" bandi genisledikce) notr orani beklendigi gibi artar
(%7,84 → %15,61 → %25,61); k=0,3 civarinda ORTA bir denge (notr ~%15,6, digger iki sinif ~%40-44
araliginda, birbirine yakin) elde edilmektedir — bu, ML siniflandirmasi icin sinif dengesizligi
acisindan v1 BULGU 10'daki N=8/k=1,0 triple-barrier sonucuna (TP %45,1 / SL %43,4 / hicbiri
%11,5) BENZER (ama FARKLI yontemle uretilmis) bir denge sunar.

SINIR: k=0,3 kesin/optimize bir secim degildir, uc deger arasinda goreceli bir orta-nokta olarak
sunulmustur. ATR14 burada basit (Wilder degil) rolling-ortalama ile hesaplanmistir — v1'in
Wilder-ATR'siyle KUCUK sayisal farklar olabilir (yontem farki, ayni SINIR notu gecerli).

### BULGU 11 — Etiket Alternatifi: Regresyon-Hedefi (N=8 Bar Ileri Getiri) Dagilim Istatistikleri
Veri Kaynagi: Ayni N=8 bar ileri getiri, sinif etiketine cevrilmeden HAM (puan + ATR-normalize)
regresyon hedefi olarak.
---------------------------------------------------------------
GOZLEM: Ham (puan): ortalama=17,0, std=1.252,6, P10/P90=[-835,0 / 918,0]. ATR-normalize (getiri/
ATR14): ortalama=0,074, std=2,298, P10/P90=[-2,34 / 2,47].

BAGLAM: Ortalama (17,0 puan, ya da 0,074xATR) SIFIRA cok yakin ve standart sapmanin (1.252,6
puan, ya da 2,298xATR) YUZDE 1'inden bile kucuktur (std/ortalama ~74x) — bu, "buyukluk+yon"
dogrudan regresyonla tahmin edilmeye calisilirsa asiri DUSUK bir sinyal/gurultu orani ile
karsilasilacagini gostermektedir. Bu, v1'in AUC~0,50-0,52 (rassal-seviyeye yakin) bulgusuyla ve
Risk Analisti'nin uc hipotezde de gozlemledigi "model hicbir donemde anlamli sinyal tasimiyor"
sonucuyla NITEL olarak TUTARLIDIR — regresyon hedefine gecmek, siniflandirmadaki temel
sinyal-yoklugu sorununu KENDILIGINDEN COZMEZ (ayni gurultu, farkli hedef temsili).

SINIR: Bu, TUM veri uzerinde tek bir toplu dagilim olcumudur; regresyon hedefinin belirli
kosullarda (orn. yuksek-ADX/trend rejiminde, BULGU 1-2) daha az gurultulu olup olmadigi bu
raporda AYRI test edilmemistir (bir ACIK SORU, asagida).

---

## ONERILEN FEATURE SETI VE LABEL TANIMI

v1'in 6 feature grubu (Volatilite/ATR, MTF Confluence, Hacim/Tick-Yogunlugu-BAR-seviyesi, Oturum/
Gun-Ici, Fiyat Yapisi/Momentum-RSI-MACD-HH-LL, Maliyet/Likidite) BU RAPORDA TEKRARLANMAMISTIR —
gecerliligini korur, referans: `arastirmaci_gold_scalping_ml_raporu.md`.

**Bu turde EKLENEN/YENI feature gruplari (gorev tanimindaki "en az 2 YENI aile" sartini asan 4
YENI grup):**

**Grup A (YENI) — Rejim/ADX:** ADX(14) ham deger, rejim etiketi (trend/range/gecis, BULGU 1),
bars-since-regime-change (BULGU 3). BULGU 2'ye gore bu grup YON bilgisi TASIMIYOR (sureklilik
~%49-50), sadece zayif bir BUYUKLUK/volatilite bilgisi tasiyor — Stratejist'in bu grubu bir
"yon-tahmin-edici" olarak DEGIL, olsa olsa bir volatilite-buyuklugu/pozisyon-boyutlandirma
yardimcisi olarak degerlendirmesi onerilir (bu bir tavsiye DEGIL, BULGU 2'nin dogrudan sayisal
sonucudur).

**Grup B (YENI) — Gorece Fiyat Yapisi:** Gunluk pivot/R1/S1 mesafesi, haftalik pivot mesafesi
(BULGU 4), 20-gunluk rolling high/low mesafesi + "yakinlik" bayragi (BULGU 5). BULGU 5, 20-gun
yuksege yakinlikta belirgin bir momentum-benzeri asimetri gostermistir — bu grubun digerlerinden
goreceli olarak daha guclu bir aday olabilecegi gozlenmistir (yine bir tavsiye degil, sayisal
gozlem: +52 vs -2 puan medyan farki).

**Grup C (YENI, veri erisimi KISMI/DOGRULANMAMIS) — Capraz-Piyasa/DXY:** USDX-SEP26 es-zamanli
getiri (BULGU 6) — ANCAK bu raporun kendi olcumune gore (lead-lag korelasyon ~-0,0008) GECMIS
DXY hareketinin GOLD'un GELECEK yonunu tahmin etmede ONEMLI bir katki saglamasi BEKLENMEMEKTEDIR.
Bu grup, veri kaynaginin kendisinin de dogrulanmamis (surekli-kontrat suphesi, BULGU 6 SINIR)
olmasi nedeniyle DUSUK ONCELIKLI bir aday olarak sunulmaktadir.

**Grup D (YENI, SINIRLI PENCERE/olceklenebilirlik acik soru) — Mikro-Yapi/Tick-Proxy:** Tick-
kural-tabanli imbalance orani, tick-sayisi, tick-ici mikro-volatilite (mid_ret_std), tick-
seviyesi ortalama spread (BULGU 7-9). Bu grup sadece SON 20 GUNLUK bir orneklemde olculebilmistir
— TAM 4,2 yillik egitim seti icin bu ailenin nasil olceklenecegi COZULMEMIS bir problemdir (bkz.
Riskler Madde 2, Acik Sorular Madde 1).

**Label Onerileri:**
- Triple-barrier (v1 BULGU 10, TEKRARLANMADI burada) — halen gecerli bir secenek.
- **3-sinifli deadzone (BULGU 10, YENI yontem, triple-barrier'DAN FARKLI):** k=0,3xATR14 civari
  orta-dengeli bir dagilim sunar (%43,9/%40,5/%15,6) — Stratejist'in Gorev Tanimi Madde 3'unde
  belirtilen "3-sinifli alternatif" icin bu, triple-barrier'in "hicbiri" sinifina ek/alternatif
  bir yontemdir, ikisi ARASINDA SECIM Stratejist'e aittir.
- **Regresyon-hedefi (BULGU 11):** olculmustur ama sinyal/gurultu orani (std/ortalama ~74x)
  asiri dusuk bulunmustur — bu rapor bu secenegi ONERMEMEKTEDIR (bir sonraki denemede oncelikli
  olarak siniflandirma yerine regresyona gecilmesi icin bu olcumde DESTEKLEYICI bir kanit
  YOKTUR), ama tamamen elenmesi de bu rapor kapsaminda degildir — karar Stratejist'e aittir.

---

## EN AZ 1 SOMUT ML TASARIM ONERISI

**Model:** LightGBM (birincil aday, v1 ile AYNI gerekce — kategorik feature destegi, dusuk
hiperparametre maliyeti). Bu turde model AILESI degil, FEATURE/ETIKET tasarimi degisiyor (gorev
tanimi geregi) — XGBoost kiyaslamasi ZORUNLU DEGIL (v1'de zaten iki model ailesi denendi, fark
yaratmadi).

**Zaman-Dilimi/Tutma-Suresi:** M15 giris, N=8 bar (2 saat) tutma-suresi — gorev tanimi geregi
DEGISTIRILMEDI (M15+ karari sabit).

**Feature Seti:** v1'in 6 grubu (ATR/volatilite, MTF confluence, bar-seviyesi hacim, oturum/
gun-ici, RSI/MACD/HH-LL, spread) + bu raporun Grup A (ADX/rejim) ve Grup B (pivot/S-R) —
Grup C (DXY) DUSUK ONCELIKLI (BULGU 6'nin lead-lag bulgusu zayif oldugu icin), Grup D (mikro-
yapi/tick) SADECE olceklenebilirlik sorunu cozulurse (bkz. Acik Sorular) dahil edilmeli. Toplam
tahmini ~28-35 sutun (v1'in ~15-25'i + bu turun ~4-8 yeni sutunu, Grup C/D haric).

**Label:** 3-sinifli deadzone (BULGU 10, k=0,3xATR14 baslangic noktasi) ONERILIR — v1'in ikili
etiketinden (AUC~0,50-0,52, rassal-seviye) FARKLI bir hedef temsili denemek, Risk Analisti'nin
"feature seti/etiket tasarimi degismeli" geri bildirimine (Hipotez 3 raporu, Stratejiste Geri
Bildirim Madde 4) dogrudan karsilik verir. Regresyon-hedefi (BULGU 11) bu asamada
ONERILMEMEKTEDIR (sinyal/gurultu orani cok dusuk bulundu).

**Kaba Maliyet-Orani On-Tahmini:** v1 BULGU 11'deki degerler (medyan bar-kapanis-spread
uzerinden: k=1,0→10,65x, k=1,5→15,97x, k=2,0→21,29x) gorev tanimi geregi TEKRAR HESAPLANMADI,
referans olarak GECERLIDIR. EK NOT (bu turun BULGU 9'undan): tick-seviyesi gun-ici ORTALAMA
spread (54,82 puan), bar-kapanis medyanindan (27-33 puan) belirgin sekilde genistir — Backtest
Muhendisi'nin S1 stres-testinde (P90/max spread, zaten planli) bu tick-ortalamasi degerinin de
bir ek referans noktasi olarak degerlendirilmesi ONERILIR (bu bir ZORUNLULUK degil, bu raporun
BULGU 9'undan dogan bir gozlem-tabanli ek oneridir).

---

## RiSKLER / SINIRLAMALAR

1. **Kutuphane durumu artik degisti (v1'e gore IYILESME):** pandas/lightgbm/scikit-learn artik
   kurulu — ancak bu rapor hala GERCEK MODEL EGITMEDI (Backtest Muhendisi asamasina birakildi,
   S2 protokolu geregi zaten oyle olmali).
2. **Mikro-yapi (Grup D) olceklenebilirlik sorunu COZULMEDI:** Tick verisi gunde ~480.000 satir
   uretiyor; 4,2 yillik (~1.000+ islem gunu) tam gecmis icin bu YUZ MILYONLARCA satir demektir —
   bu ortamda tek seferde cekilip islenmesi PRATIK DEGIL (bu raporda SADECE 20 gunluk bir
   orneklem kullanildi, 2,4 saniyede cekildi — tam-tarihsel olcek bu hizin ~50-70 kati sure/bellek
   gerektirir, dogrulanmadi ama kaba orantiyla tahmin edilebilir). Bu grubun canli/backtest
   asamasinda nasil kullanilacagi (orn. sadece SON N-ay icin egitim, ya da M1-bar-tabanli daha
   kaba bir proxy'ye indirgeme) COZULMEMIS bir tasarim sorusudur.
3. **DXY veri kaynaginin dogrulugu SUPHELI:** BULGU 6 SINIR'da detaylandirildigi gibi, USDX-SEP26
   sembolunun MT5 uzerinden donen 4,2 yillik gecmisi, sembolun kendi ilan edilen baslangic
   tarihinden (2026 ortasi) cok daha eskidir — bu bir surekli-kontrat/splice serisi olabilir,
   BAGIMSIZ dogrulanmadi. Bu grup DUSUK GUVEN ile sunulmaktadir.
4. **Overfitting/genis arama uzayi (S2):** Bu turde eklenen 4 yeni feature grubu, arama uzayini
   v1'e gore DAHA DA GENISLETIR — `justin_ml_anti_overfitting_protokolu.md` (purged/embargolu
   walk-forward, test-seti tek-kullanim, feature-sizinti kontrol listesi) Backtest Muhendisi
   asamasinda HARFI HARFINE uygulanmalidir, ozellikle Grup B/C/D icin ileri-bakis riski (pivot/
   rolling-S/R hesaplamalarinin dogru GUN/HAFTA sinirlarinda kesildigi) ayrica dogrulanmalidir.
5. **Veri sizintisi/nedensellik:** Bu raporda kullanilan TUM rolling/trailing hesaplamalar
   (ADX, pivot, rolling-S/R, DXY-lag, tick-agregasyonlari) NEDENSEL olarak tasarlanmistir (yalniz
   gecmis+kendisi); gunluk/haftalik pivotlarin ONCEKI TAMAMLANMIS gun/haftadan turetildigi ayrica
   kontrol edildi (bkz. BULGU 4 aciklamasi). Ancak bu, BAGIMSIZ bir kod incelemesiyle DEGIL, bu
   raporu yazan ayni script'in kendi ic-mantik kontroluyle teyit edilmistir — Backtest
   Muhendisi'nin S2 feature-sizinti kontrol listesini BAGIMSIZ olarak yeniden uygulamasi
   gerekir.
6. **Mikro-yapi feature'lari GERCEK order-flow degildir:** BULGU 7'de acikca belirtildigi gibi,
   kullanilan tick feed'i quote-tick'tir (volume=0, last=0) — "imbalance" bir bid/ask-bounce
   PROXY'sidir, gercek alici/satici hacim dengesizligi DEGILDIR. Bu proxy'nin gercek order-flow
   ile ne kadar orustugu BILINMEMEKTEDIR (dogrulanamaz, bu broker/feed turunde gercek trade-tick
   verisi mevcut degil).
7. **Canliya-gecebilirlik:** Hicbir BULGU'da spread/slipaj/komisyon SONRASI net getiri
   hesaplanmamistir (v1 ile AYNI sinir) — BULGU 9'daki tick-ortalama-spread bulgusu, gercek
   maliyetin v1'in on-tahmininden DAHA YUKSEK olabilecegine dair bir ek isaret sunar ama kesin
   degildir.
8. **Ornek disi genelleme / DST:** v1 ile AYNI (2022-2026 XM/MT5 GOLD verisine ozel, GMT+3
   varsayimi DST bagimsiz dogrulanmadi — gun/hafta sinirlari BULGU 4-5'te bu varsayima
   dayanmaktadir).

---

## ACIK SORULAR

1. Mikro-yapi (Grup D) feature ailesi TAM 4,2 yillik egitim seti uzerinde nasil olceklenecek?
   Secenekler: (a) yalniz SON N-ay/yil icin egitim+test (kucuk ama tutarli pencere), (b) M1-bar
   OHLC'den daha kaba bir proxy turetme (tick yerine dakika-bar bazli buy/sell-pressure yaklasik
   hesabi, cok daha az veri hacmi), (c) bu grubu bu turde tamamen ELEME. Karar Stratejist/
   Backtest Muhendisi'ne aittir.
2. USDX-SEP26'nin 4,2 yillik gecmisi GERCEKTEN guvenilir surekli bir seri mi, yoksa bir
   veri-anomalisi/splice midir? Bu, Backtest Muhendisi'nin S2/feature-sizinti kontrol listesi
   kapsaminda (orn. roll-over tarihlerinde ani sicramalar var mi diye bakarak) BAGIMSIZ
   dogrulanmalidir — bu rapor bunu dogrulayamadi (tek script/tek gecis, capraz-dogrulama yok).
3. ADX'in kendi yon bilgisi (+DI/-DI farki veya isareti) BULGU 2'deki naif "mevcut-bar-yonu"
   sureklilik testinden FARKLI bir sonuc verir mi? Bu raporda test edilmedi (bir sonraki tur
   icin bir aday olcum).
4. Regresyon-hedefinin (BULGU 11) BELIRLI kosullarda (orn. yuksek-ADX/trend rejiminde, dusuk
   deadzone bandinda) daha az gurultulu olup olmadigi bu raporda ayrica test edilmedi.
5. BULGU 7'deki (yuksek/dusuk-imbalance medyan farki -254 vs +4 puan) bulgu, DAHA UZUN bir
   tick-penceresinde (orn. 60-90 gun) de tekrarlanir mi, yoksa 20 gunluk orneklemin bir
   artefakti mi? Bu rapor kapsaminda test edilmedi (kucuk n=251/grup nedeniyle oncelikli bir
   dogrulama sorusu).
6. Gercek execution slipaji (v1 Acik Soru 6 ile AYNI, hala cozulmedi) — bu turde de olculmedi.

---

## iZOLASYON NOTU

- MilaGold, Lisa (ters muhendislik) ve Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md,
  positions_status.json vb.) bu arastirma sirasinda okunmadi veya referans alinmadi.
- Bu rapor icin format/sablon referansi olarak da MilaGold/Lisa/Signal GPT dosyalari
  ACILMADI — rapor formati Justin'in kendi onceki Arastirmaci raporundan (`arastirmaci_gold_
  scalping_ml_raporu.md`, ayni proje icinde) ve sistem promptundaki genel formattan turetildi.
- Tek veri kaynagi XM/MT5 sembolleri (GOLD, USDX-SEP26), dogrudan MetaTrader5 kutuphanesi
  araciligiyla. Ekonomik takvim/DXY/tahvil gibi harici (MT5-disi) bir API/kaynak EKLENMEMISTIR —
  gorev tanimindaki "MT5 disi harici bir API/kaynak EKLEMEYIN" kisiti korunmustur; USDX-SEP26
  MT5'in KENDI sembol listesinden erisildigi icin bu kisiti IHLAL ETMEZ.
  - Calisma yalniz `C:\MilaYatirim\Justin\` dizininde yapildi (girdi: gorev dosyasi, `justin_
  gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md`, `justin_backtest_onkontrol_
  standardi.md`, `justin_gold_scalping_karar_ve_governance_20260714.md`, v1 raporu, Risk
  Analisti hipotez 1/2/3 raporlari; cikti: `research_ml_gold_scalping_m15_v2.py`, `research_ml_
  gold_scalping_m15_v2_output.json`, bu rapor).

---

## STRATEJiST'E NOT

Bu rapordaki hicbir bulgu "su feature'i/etiketi/modeli kullan" demez. Tum sayilar MT5'ten
dogrudan olculmustur (bkz. `research_ml_gold_scalping_m15_v2.py`,
`research_ml_gold_scalping_m15_v2_output.json`). Ozellikle BULGU 6 (DXY es-zamanli-guclu/
ongorucu-sifir ayrimi) ve BULGU 7 (imbalance medyan-fark/korelasyon celiskisi) DIKKATLE
okunmalidir — bunlar "guclu gorunen ama kirilgan/kullanilamaz" olabilecek gozlemlerdir, Tam
Tur 1'in RED paterninin (aggregate'te anlamli gorunen ama testte cokme) TEKRARLANMAMASI icin
Stratejist'in bu ayrimlari feature-tasarim kararina yansitirken hesaba katmasi onerilir (bu
hala bir tavsiye degil, iki BULGU'nun dogrudan sonucudur). BULGU 10-11'deki etiket-alternatifi
sayilari (3-sinif deadzone dagilimi, regresyon-hedefi gurultu orani) bir sonraki asamada
Stratejist'in etiket tasarimini belirlerken kullanabilecegi ham girdidir. Grup D (mikro-yapi)
icin olceklenebilirlik sorunu (Acik Soru 1) COZULMEDEN bu grubun TAM egitim setine dahil
edilmesi ONERILMEZ (bir tasarim/kapasite kisiti, tavsiye degil).
