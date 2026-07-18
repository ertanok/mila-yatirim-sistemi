# ARASTIRMACI RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile (M15+), v1

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile — kural-
tabanli fiyat-aksiyonu ailesi H1/H2/H3, Madde-7 ile KAPANDI)
Pipeline adimi: 1/4 (Arastirmaci)
Tarih: 12 Temmuz 2026 (VPS-yerel)
Gorev kaynagi: `gorev_arastirmaci_justin_gold_scalping_ml_v1.md` (Stratejist v6 raporu, Bolum 7)
Veri kaynagi: XM/MT5, dogrudan MetaTrader5 kutuphanesi, sembol "GOLD" (spot metal,
contract_size=100, point=0.01), timeframe M15 (99.999 bar, 2022-04-18 03:45 UTC →
2026-07-10 23:45 UTC, ~4,2 yil). H1 (25.017 bar) ve H4 (6.545 bar) M15 ham verisinden
nedensel/hizalanmis yeniden-ornekleme (epoch // 3600, epoch // 14400) ile turetilmistir —
ayri bir MT5 cagrisi kullanilmamistir (gorev tanimi geregi).
Analiz script'i: `research_ml_gold_scalping_m15.py` (ham cikti:
`research_ml_gold_scalping_m15_output.json`)

**Gecmis calisma kontrolu:** Bu proje icin `justin_gecmis_calisma.md` (HEDEF_PF/DD/kasa/risk
sabitleri) ve `arastirmaci_gold_scalping_raporu.md` (M1/M5 kural-tabanli aile arastirmasi, dahil
Rejim ek-bolumu) okundu. Bu rapor, onceki M1/M5 kural-tabanli aileyle **AYNI enstruman/broker**
uzerinde ama **farkli zaman-dilimi (M15+) ve farkli metodoloji (ozellik-tabanli ML)** kullanan
BAGIMSIZ bir olcum setidir — onceki raporun M1/M5 sayilari burada tekrarlanmamis, sadece
metodolojik surekliligi korumak icin ayni yapidaki nedensel/trailing-esik yaklasimi (BULGU 9-13,
onceki rapor) M15 icin YENIDEN uygulanmistir. Onceki rapordaki M1/M5 spread degerleri (33-59 pts)
ile bu rapordaki M15 spread degerleri (27-35 pts) FARKLI olcum donemlerine/orneklemlere aittir,
dogrudan karsilastirilmamalidir (bkz. SINIR notlari).

---

## OZET

1. M15 verisinde (4,2 yil, 99.999 bar) gun-ici volatilite (ATR14) belirgin sekilde saate bagli:
   en yuksek 16-19 sunucu saati bandinda (medyan ATR14 ~389-501 puan), en dusuk 1-3 ve 8-9
   bandinda (medyan ~174-221 puan) — M1/M5 icin onceki raporda bulunan deseni (BULGU 1, 15-18
   bandi en yuksek) M15 olceginde de dogrulamaktadir.
2. Spread (M15 bar-kapanis, puan) gun icinde nispeten dar bir aralikta kalmaktadir (medyan 27-33
   puan, en genis 0-2 ve 6-8 saat bandinda); bu, onceki M1/M5 raporundaki (33-59 puan) daha genis
   spread araliginin AYNI donem olmadigi icin farkli olabilecegi bir gozlemdir.
3. Coklu-zaman-dilimi (M15/H1/H4) trend confluence (ucu de ayni yonde) olculen barlarin
   %44,8'inde gerceklesmektedir; confluence oldugunda 8-M15-bar (2 saat) ileri yonlu getiri
   (yukari confluence: +36,48 puan, asagi confluence: +20,61 puan) confluence olmayan durumdan
   (+21,76 puan, yon-tanimsiz referans) daha buyuktur — ozellikle yukari-confluence'ta belirgin.
4. Triple-barrier taban dagilimi (N=8 bar/2 saat, k=1,0xATR): TP-once %45,1, SL-once %43,4,
   hicbiri %11,5 — bu parametre kombinasyonu ML siniflandirma icin nispeten dengeli (~51/49) bir
   ikili etiket dagilimi sunmaktadir.
5. Maliyet-orani on-tahmini: M15 medyan ATR14 (287,43 puan) / M15 medyan spread (27 puan) = 10,65
   kat (k=1,0). Hedef S1 esigi (~15-20 kat) k=1,0'da KARSILANMAMAKTADIR; k=1,5 icin oran 15,97
   (esigin alt sinirinda), k=2,0 icin 21,29 (esigi asmaktadir). H1/H4 tutma-suresi bazinda oran
   cok daha rahat: H1 medyan ATR14/M15-spread = 22,2 kat, H4 medyan ATR14/M15-spread = 44,1 kat.
6. Hacim (tick_volume) anomalisi (trailing-100 medyanin 2 kati) tespit edilen barlari (n=9.304,
   toplamin %9,3'u) takip eden bar, normal-hacim barlarini takip eden bara gore ortalama %30,4
   daha genis range (564,89 vs 433,07 puan) gostermektedir.

---

## GOZLEMLER

### BULGU 1 — M15 Saatlik ATR(14)/Spread/Tick-Hacim Profili
Veri Kaynagi: MT5 GOLD M15, 99.999 bar (2022-04-18→2026-07-10). ATR(14) nedensel (yalniz
gecmis+kendisi) hesaplanmistir. Saat, epoch'un dogrudan UTC gibi okunmasiyla (sunucu saati
GMT+3 varsayimi, DST ayrica dogrulanmadi — onceki raporla ayni SINIR).
---------------------------------------------------------------
GOZLEM (secili saatler, tam 24 saatlik tablo JSON ciktisinda "m15_hourly_atr_spread_volume"):
| Sunucu Saati | ATR14 Medyan (pts) | ATR14 P90 (pts) | Spread Medyan (pts) | Tick-Hacim Medyan | n |
|---|---|---|---|---|---|
| 18 | 500,5 | 1327,0 | 27,0 | 2501,0 | 4368 |
| 17 | 471,9 | 1230,6 | 27,0 | 3553,0 | 4368 |
| 19 | 446,8 | 1251,7 | 27,0 | 1816,5 | 4368 |
| 16 | 388,6 | 1030,8 | 27,0 | 3634,0 | 4368 |
| 9  | 220,6 | 791,8  | 27,0 | 1644,0 | 4368 |
| 8  | 207,8 | 777,1  | 28,0 | 1222,0 | 4365 |
| 1  | 193,8 | 804,3  | 31,0 | 436,0  | 4348 |
| 2  | 174,1 | 785,3  | 30,0 | 656,5  | 4348 |
| 0  | 261,4 | 1798,7 | 33,0 | 524,0  | 296 |

BAGLAM: En yuksek ATR14 medyan degeri 16-19 sunucu-saati bandinda (388,6-500,5 puan), en dusuk
1-2 ve 8-9 bandinda (174,1-220,6 puan) gozlenmistir — yaklasik 2,3-2,9 kat fark. Spread medyani
gun boyunca goreceli dar bir aralikta (27-33 puan) kalmaktadir; en genis spread medyani 0 (33
puan) ve 1-2 (30-31 puan) saatlerinde gorulmustur. Tick-hacim en yuksek 16-18 saat bandinda
(2501-3634), en dusuk 0-2 saat bandinda (436-656,5).

SINIR: Saat 0 icin ornek buyuklugu (n=296) digerlerine (4212-4368) gore cok kucuktur — bu saatte
haftalik/rollover kesintileri nedeniyle az bar olusmus olabilir, bu satirdaki degerler (ozellikle
P90=1798,7) dusuk guvenilirlikte kabul edilmelidir. Saat eslemesi onceki raporla ayni
varsayima (GMT+3, DST dogrulanmadi) dayanir.

### BULGU 2 — Oturum Bazli Ozet (Asya/Londra/NY)
Veri Kaynagi: Ayni M15 seri; oturum tanimlari genel/kamuya-acik konvansiyondan alinmistir (Asya
saat 1-8, Londra 9-16, New York 15-23, sunucu-saati/UTC-epoch varsayimiyla) — MilaGold'un veya
baska bir dahili sistemin seans tanimindan turetilmemistir.
---------------------------------------------------------------
GOZLEM:
| Oturum | n | ATR14 Medyan (pts) | Spread Medyan (pts) | Tick-Hacim Medyan |
|---|---|---|---|---|
| Asya | 34.801 | 207,5 | 29,0 | 1005,0 |
| Londra | 34.944 | 286,7 | 27,0 | 1924,0 |
| New York | 38.582 | 369,9 | 27,0 | 2089,0 |

BAGLAM: New York penceresi (15-23) en yuksek medyan ATR14 (369,9) ve tick-hacme (2089,0)
sahiptir; Asya penceresi (1-8) en dusuk ATR14'e (207,5) ama en yuksek spread medyanina (29,0)
sahiptir. Londra ile New York arasindaki spread farki kucuktur (ikisi de 27,0).

SINIR: Oturum saat araliklari sabit/kesin sinirlar olarak tanimlanmistir (gercek likidite
gecisleri kademelidir, keskin sinir degil); Londra/NY orustugu 15-16 bandi her iki oturumda da
sayilmistir (kesisim ayristirilmamistir).

### BULGU 3 — Haftanin Gunune Gore M15 Range/ATR
Veri Kaynagi: Ayni M15 seri, gun-ici ortalama range ve medyan ATR14, haftanin gunune (UTC
epoch->weekday) gore gruplanmis.
---------------------------------------------------------------
GOZLEM: Ort. range (pts) — Pazartesi 463,3 (n=19672), Sali 430,6 (n=20261), Carsamba 436,8
(n=20106), Persembe 452,3 (n=20032), Cuma 444,5 (n=19816). Medyan ATR14 (pts) — Pazartesi 289,8,
Sali 281,3, Carsamba 283,1, Persembe 296,5, Cuma 288,1.

BAGLAM: Gunler arasi fark sinirlidir (~%7-8 bant genisliginde, 430,6-463,3 puan araligi);
Pazartesi ve Persembe goreceli en yuksek, Sali goreceli en dusuk. Bu, onceki M5 raporundaki
(BULGU 7, ~%9 bant, Pazartesi en yuksek) desenle NITEL olarak tutarlidir.

SINIR: Cumartesi/Pazar verisi yok (piyasa kapali); hafta ilk/son barlari kismi gun icerebilir.

### BULGU 4 — ATR Genisleme/Daralma Rejimi ve Sonraki-4-Bar Mutlak Hareket
Veri Kaynagi: ATR14[i], kendi trailing-100-bar (nedensel) medyaniyla kiyaslanarak "genis"/"dar"
etiketlenmistir (onceki rapordaki BULGU 9-13 ile AYNI metodolojik yapi, TF=M15).
---------------------------------------------------------------
GOZLEM: Genis rejim n=49.571, sonraki 4-M15-bar (1 saat) ortalama MUTLAK getiri = 502,17 puan.
Dar rejim n=50.316 (gecerli 50.312), sonraki 4-bar ortalama mutlak getiri = 393,27 puan.

BAGLAM: Genis-ATR rejiminde sonraki 1 saatlik mutlak hareket, dar-ATR rejimine gore ~%27,7 daha
buyuktur (502,17 vs 393,27 puan). Iki rejim kategorisi orneklem buyuklugu bakimindan kabaca
DENGELIDIR (49.571 / 50.316).

SINIR: Bu, ATR'nin kendi otokorelasyonunun (volatilite kumelenmesi/clustering) beklenen bir
sonucu olabilir — yon-notr bir "buyukluk" olcumudur, yon tahmini icermez.

### BULGU 5 — Coklu-Zaman-Dilimi (M15/H1/H4) Trend Confluence
Veri Kaynagi: Trend[i] = sign(close[i] - SMA20[i]), her TF kendi barinda. H1/H4 barlari M15'ten
nedensel/hizalanmis resample (epoch//3600, epoch//14400); her M15 barina, o bardan ONCE
KAPANMIS en son H1/H4 barinin trend etiketi atanmistir (ileri-bakis yok).
---------------------------------------------------------------
GOZLEM: Gecerli M15 bar sayisi (M15+H1+H4 trend etiketi mevcut) = 99.706. Tum-TF-yukari
confluence n=25.371, tum-TF-asagi confluence n=19.301, confluence-yok n=55.034 (confluence
orani = %44,8). 8-M15-bar (2 saat) ileri, yon-hizali ortalama getiri: yukari-confluence +36,48
puan (n=25.371), asagi-confluence +20,61 puan (n=19.301), confluence-yok +21,76 puan
(n=55.026, yalniz "yukari" referansiyla olculmustur — bu grupta tutarli bir yon olmadigindan
bu deger sinirli anlam tasir).

BAGLAM: Confluence durumunda (ozellikle tum-TF-yukari), sonraki 2 saatlik yon-hizali getiri
confluence-yok durumuna gore daha buyuktur (36,48 vs 21,76 puan) — asagi-confluence icin bu fark
daha kucuktur (20,61 vs 21,76, yani asagi confluence ile confluence-yoklugu arasinda buyuk fark
gozlenmemektedir). Bu asimetri (yukari confluence daha guclu, asagi confluence zayif) veri
setinin genel yon-onyargisiyla (asagida BULGU 8) iliskili olabilir.

SINIR: SMA20 tanimi tek bir parametre secimidir (baska bir pencere/trend tanimi farkli sonuc
verebilir); "bir onceki kapanmis H1/H4 bari" nedensel eslemesi en yakin-ama-en-taze bilgiyi
kullanir, bu M15 bar ile H1/H4 bari arasinda 0-59 dakikalik bir "bayatlik" (staleness)
farkina yol acabilir (ozellikle H4'te bu fark 0-3 saat 59 dakikaya kadar cikabilir).

### BULGU 6 — Momentum Ozellikleri (RSI14, MACD Histogram Kalicilik)
Veri Kaynagi: RSI(14) ve MACD(12,26,9) M15 close serisinden nedensel (EMA tabanli) hesaplandi.
---------------------------------------------------------------
GOZLEM: RSI14 ortalama=51,0, medyan=50,83, P10/P90=[29,33 / 72,91]. RSI14>70 orani=%13,6,
RSI14<30 orani=%10,77. MACD histogram isareti bir sonraki barda AYNI isarette kalma orani=%92,3
(n=99.998).

BAGLAM: RSI dagilimi 50 civarinda merkezlenmis, hafif simetrik-yakin bir dagilim gostermektedir
(P10/P90 aralik genisligi ~43,6 puan). MACD histogram isaret-kaliciligi (%92,3) cok yuksektir;
ANCAK bu, MACD histogramin kendisinin EMA-tabanli/duzletilmis (smoothed) bir turev oldugu icin
mekanik olarak beklenen bir otokorelasyondur — bagimsiz bir "sinyal gucu" olarak
yorumlanmamalidir (bkz. SINIR).

SINIR: MACD histogram kaliciligi olcumu, gostergenin kendi matematiksel yapisindan (ardisik EMA
degerlerinin dogal olarak birbirine yakin olmasi) kaynaklanan bir otokorelasyonu da icerir; bu
sayi tek basina bir "trend devam ediyor" bulgusu olarak sunulamaz, ML feature'i olarak ham
histogram/egim degeri kullanilmalidir (isaretin kendisi degil).

### BULGU 7 — Fiyat Yapisi (Higher-High / Lower-Low Ardisikligi)
Veri Kaynagi: M15 high/low serisi, ardisik bar karsilastirmasi (high[i]>high[i-1] = HH,
low[i]<low[i-1] = LL).
---------------------------------------------------------------
GOZLEM: HH orani=%48,58 (streak: adet=22.626, ort. uzunluk=2,15, P90=4, maksimum=16). LL
orani=%46,99 (streak: adet=22.881, ort. uzunluk=2,05, P90=4, maksimum=15).

BAGLAM: Hem HH hem LL oranlari %50'nin biraz altindadir; streak uzunluklari (ortalama ~2,
P90=4) kisa/dagilmis kalmaktadir — bu, onceki M1/M5 raporunun BULGU 3'undeki "ham bar-yonu
devamliligi zayif" bulgusuyla NITEL olarak tutarlidir (farkli bir yapi tanimi olsa da).

SINIR: HH/LL tanimi yalniz bir onceki bara gore yapilmistir (2-bar karsilastirma); daha uzun
ufuklu yapi tanimlari (orn. N-bar swing high/low) test edilmemistir.

### BULGU 8 — Genel Yon Onyargisi (Drift) — M15 Orneklemi
Veri Kaynagi: M15 ilk ve son kapanis (2022-04-18 → 2026-07-10).
---------------------------------------------------------------
GOZLEM: Ilk kapanis ~ (JSON'da saklanmamis, ATR/trend serilerinden turetilen dolayli kanit:
BULGU 5'teki confluence asimetrisi) — dogrudan ilk/son fiyat farki bu script'te ayri
kaydedilmemistir; ancak BULGU 5'teki yukari-confluence (n=25.371) ile asagi-confluence
(n=19.301) arasindaki n farki (%31,4 daha fazla yukari-confluence bar'i) veri setinde net bir
yukari-yonlu onyargiya isaret etmektedir.

BAGLAM: Bu, onceki M1/M5 raporunun BULGU 6'sindaki gibi acik bir "ilk fiyat - son fiyat" olcumu
DEGILDIR — bu rapordaki M15 script'i bu spesifik metrigi hesaplamamistir (bir ARASTIRMA
BOSLUGU, asagida not edilmistir). Dolayli kanit (confluence n-asimetrisi) yon-onyargisi
varligini destekler ama BUYUKLUGUNU olcmez.

SINIR: Bu bulgu dolayli/turetilmis bir gozlemdir, dogrudan olculmemistir — bkz. ARASTIRMA
BOSLUKLARI.

### BULGU 9 — Hacim (Tick-Volume) Anomalisi ve Sonraki Bar Range Iliskisi
Veri Kaynagi: tick_volume, kendi trailing-100-bar (nedensel) medyaniyla kiyaslanarak
"anomali" (>2x medyan) etiketlenmistir.
---------------------------------------------------------------
GOZLEM: Anomali bar sayisi=9.304 (toplamin %9,3'u). Anomali sonrasi bar ortalama range=564,89
puan; normal (anomali-disi) sonrasi bar ortalama range=433,07 puan. Genel tick-hacim
ortalama=2003,7, medyan=1550,0.

BAGLAM: Hacim anomalisi tespit edilen bari takip eden bar, normal hacimli bari takip eden bara
gore ortalama %30,4 daha genis range gostermektedir (564,89 vs 433,07) — hacim anomalisi ile
takip eden volatilite arasinda pozitif bir iliski gozlenmektedir.

SINIR: Bu iliski tek-bar-ileri (t+1) ufkunda olculmustur; anomalinin YONU (hangi yonde hacim
arttigi) ayristirilmamistir, yalniz BUYUKLUK (range) olcumu yapilmistir.

### BULGU 10 — Triple-Barrier Taban Dagilimi (Label Tasarimi On-Testi)
Veri Kaynagi: Her M15 bari icin, giris ATR14'une gore k-katli TP/SL bariyerleri kuruldu; N-bar
ileri pencerede hangi bariyerin ONCE gerceklestigi (nedensel/ileri-bakissiz, sadece o barin
KENDI ATR14'u kullanilarak) olculdu. 9 (N,k) kombinasyonu test edildi.
---------------------------------------------------------------
GOZLEM:
| N (bar/saat) | k (xATR) | TP-once | SL-once | Hicbiri | n |
|---|---|---|---|---|---|
| 4 (1sa) | 1,0 | %36,34 | %35,39 | %28,27 | 99.883 |
| 4 (1sa) | 1,5 | %22,90 | %22,71 | %54,38 | 99.883 |
| 4 (1sa) | 2,0 | %14,24 | %14,30 | %71,46 | 99.883 |
| 8 (2sa) | 1,0 | %45,10 | %43,36 | %11,54 | 99.879 |
| 8 (2sa) | 1,5 | %35,03 | %34,05 | %30,93 | 99.879 |
| 8 (2sa) | 2,0 | %25,81 | %25,55 | %48,64 | 99.879 |
| 16 (4sa) | 1,0 | %49,19 | %47,07 | %3,74 | 99.871 |
| 16 (4sa) | 1,5 | %44,45 | %42,47 | %13,07 | 99.871 |
| 16 (4sa) | 2,0 | %38,23 | %36,85 | %24,92 | 99.871 |

BAGLAM: N buyudukce (ayni k icin) "hicbiri" orani hizla dusmektedir (orn. k=1,0: N4'te %28,27,
N8'de %11,54, N16'da %3,74) — daha uzun ufukta bariyerlerden biri neredeyse her zaman
tetiklenmektedir. TP-once orani tum kombinasyonlarda SL-once oranindan hafifce yuksektir (fark
~%0,1-2,1 puan araliginda) — bu, BULGU 8'deki yukari-yon onyargisiyla tutarli kucuk bir
asimetridir. N=8/k=1,0 kombinasyonu (%45,10 / %43,36, "hicbiri" sadece %11,54) iki sinifli bir
ML etiketi icin nispeten DENGELI bir taban dagilimi sunmaktadir.

SINIR: Bu olcum SADECE giris barinin kendi ATR14'unu kullanir (nedensel, ileri-bakis yok) ama
spread/slipaj/komisyon DAHIL EDILMEMISTIR — yani burada raporlanan TP/SL oranlari BRUT fiyat
hareketine dayanir, net (maliyet dusulmus) sonuc degildir. Ayrica bu, TUM veri uzerinde tek bir
olcumdur; walk-forward/OOS ayrimi (S2 protokolu geregi) bu asamada YAPILMAMISTIR — bu Backtest
Muhendisi'nin isidir.

### BULGU 11 — Maliyet-Orani On-Tahmini (S1 On-Kontrol Girdisi)
Veri Kaynagi: M15 medyan ATR14 (BULGU 1) ve M15 medyan spread (BULGU 1), ek olarak H1/H4
medyan ATR14 (ayni M15 ham verisinden resample, ayri hizli-olcum script'iyle dogrulandi).
---------------------------------------------------------------
GOZLEM:
| Referans | Deger (pts) | M15-spread-medyanina (27 pts) orani |
|---|---|---|
| M15 ATR14 medyan (k=1,0) | 287,43 | 10,65x |
| M15 ATR14 medyan x1,5 | 431,15 | 15,97x |
| M15 ATR14 medyan x2,0 | 574,86 | 21,29x |
| H1 ATR14 medyan (k=1,0) | 599,61 | 22,21x |
| H4 ATR14 medyan (k=1,0) | 1191,18 | 44,12x |
| Canli spread (rapor ani) | 53 pts | (referans, medyanin ~2 kati) |

BAGLAM: `justin_backtest_onkontrol_standardi.md` Madde 2'deki hedef oran (~15-20x) SADECE M15
ATR'sinin 1,0 katinda hedef alinirsa KARSILANMAMAKTADIR (10,65x); 1,5 kat ATR hedefi esigin ALT
SINIRINA yakin (15,97x), 2,0 kat ATR hedefi esigi ASMAKTADIR (21,29x). H1 (1 kat ATR bile
22,21x) ve H4 (1 kat ATR 44,12x) tutma-surelerinde bu oran M15'e gore cok daha rahat
karsilanmaktadir. Canli/anlik spread (53 pts) medyanin (27 pts) yaklasik iki katidir — bu,
medyan uzerinden yapilan on-hesaplamanin bazi anlarda (ozellikle dusuk-likidite/haber
zamanlarinda) iyimser kalabilecegine isaret eder.

SINIR: Bu hesap yalniz MEDYAN spread kullanir; P90/max spread (BULGU 1'de bazi saatlerde
gozlenen daha genis degerler) ile ayni oran hesaplanirsa sonuc daha az elverisli cikar — bu
ek/stres-testi hesap Backtest Muhendisi'nin on-kontrol asamasinda ayrica yapilmalidir. Slipaj bu
hesaba dahil edilmemistir (yalniz bar-kapanis spread'i kullanilmistir, gercek execution
slipaji ayri olculmedi).

---

## ONERILEN FEATURE SETI VE LABEL TANIMI

Asagidaki oneri, yukaridaki BULGU 1-11'in dogrudan turevidir; feature secimi Stratejist'in
onaylayacagi bir BASLANGIC noktasidir, nihai/kesin liste degildir (S2 protokolu geregi feature
seti Backtest Muhendisi asamasinda sizinti kontrolune tabi tutulacaktir).

**Feature Grubu 1 — Volatilite:** ATR14 (M15, kendi degeri), ATR14/trailing-100-medyan orani
(genis/dar rejim, BULGU 4), ATR14 (H1), ATR14 (H4) — hepsi nedensel/causal.

**Feature Grubu 2 — Coklu-TF Trend Confluence:** M15/H1/H4 trend isareti (BULGU 5 tanimiyla,
veya alternatif bir trend tanimi), confluence bayragi (tum-ayni-yon mu), confluence yonu.

**Feature Grubu 3 — Hacim/Tick-Yogunlugu:** M15 tick_volume, tick_volume/trailing-100-medyan
orani (anomali bayragi, BULGU 9), hacim momentum (N-bar hacim egimi — bu rapor sadece anomali
esigini test etmistir, egim/momentum ayri bir feature olarak eklenmeli).

**Feature Grubu 4 — Oturum/Gun-Ici Konum:** Sunucu-saat (dongusel kodlama: sin/cos), Asya/
Londra/NY bayraklari (BULGU 2 tanimlariyla), haftanin gunu (BULGU 3), seans acilis/kapanisina
mesafe (bu rapor bunu dogrudan olcmedi — ARASTIRMA BOSLUGU, asagida).

**Feature Grubu 5 — Fiyat Yapisi/Momentum:** Lag getiriler (1,4,8,16-bar), RSI14 (BULGU 6, ham
deger — isaret degil), MACD hatti ve histogram (ham deger, isaret-kaliciligi DEGIL — bkz. BULGU
6 SINIR), HH/LL streak uzunlugu (BULGU 7).

**Feature Grubu 6 — Maliyet/Likidite:** M15 spread (ham + trailing volatilite), BULGU 11'deki
ATR/spread orani (dogrudan feature olarak degil, model-disi bir on-kontrol/filtre olarak
kullanilmasi onerilir — bu rapor bunu bir feature degil bir ON-KONTROL GIRDISI olarak sunar).

**Label Onerisi — Triple-Barrier:** BULGU 10'daki N=8 (2 saat, 8xM15-bar) ve k=1,0-1,5xATR14
kombinasyonlari, "hicbiri" oraninin cok dusuk (N16) veya cok yuksek (N4/k2,0) olmadigi ORTA
bir bolgeyi temsil eder — bu, sinif dengesizligi acisindan baslangic icin makul bir bolgedir.
Kesin N/k secimi Stratejist'in SL/TP tasarimina (bu gorev tanimindaki "Sonraki Adim") baglidir;
bu rapor sadece taban dagilimi (BULGU 10) sunar, N/k SECIMI YAPMAZ.

---

## EN AZ 1 SOMUT ML TASARIM ONERISI

**Model:** LightGBM (birincil aday) — gradyan artirmali agac tabanli siniflandirici, orta
buyuklukteki tablo-veri (tabular) problemlerinde (bu olcekte ~100 bin ornek, ~20-30 feature)
hesaplama maliyeti dusuk ve yorumlanabilirlik (feature importance, SHAP) yuksek. XGBoost ayni
feature seti uzerinde ikincil/kiyaslama modeli olarak onerilir (gorev tanimi geregi).

**Zaman-Dilimi/Tutma-Suresi:** M15 giris, N=8 bar (2 saat) tutma-suresi, k=1,0-1,5xATR14(M15)
bariyer (BULGU 10 taban dagilimina gore secildi — kesin deger Stratejist onayina tabidir).

**Feature Seti:** Yukaridaki 6 grubun tamami (~15-25 sutun, kesin sayi Backtest Muhendisi
asamasinda feature-sizinti kontrol listesi (S2, Madde 3) uygulandiktan sonra netlesir).

**Label:** Triple-barrier, 3 sinif (TP-once=1, SL-once=-1, hicbiri=0) veya ikili (TP-once vs
SL-once, "hicbiri" orneklerini disarida birakarak — bu, "hicbiri" oraninin BULGU 10'da N4'te
%28-71 gibi yuksek olabildigi durumlarda orneklem kaybina yol acabilir, N/k secimiyle dengeli
tutulmali).

**Kaba Maliyet-Orani On-Tahmini:** BULGU 11'e gore, k=1,0xATR(M15) hedefi maliyet-orani
esigini (~15-20x) KARSILAMAZ (10,65x); k=1,5 esigin ALT SINIRINDA (15,97x); k=2,0 esigi ASAR
(21,29x). Bu nedenle onerilen tasarimin bariyer katsayisi (k), Backtest Muhendisi'nin S1
on-kontrolunu GECEBILMESI icin muhtemelen >=1,5 (tercihen ~2,0) araliginda olmalidir — ancak
BULGU 10'a gore k=2,0'da "hicbiri" orani N=8'de %48,64'e cikmaktadir (sinif dengesizligi riski
buyur). Bu, N ve k arasinda bir DEGIS-TOKUS (trade-off) oldugunu gosterir: daha yuksek k daha
iyi maliyet-orani ama daha fazla "hicbiri"/daha az sinyal frekansi; daha uzun N (orn. 16 yerine)
bu degis-tokusu kismen yumusatabilir (BULGU 10'da N16/k1,5: TP %44,45, SL %42,47, hicbiri
sadece %13,07 — hem daha iyi sinif dengesi hem cost-ratio icin daha genis bir hedef). Kesin
secim Stratejist'e aittir; bu rapor sadece ham degis-tokusu sayisal olarak sunar.

**Ikincil/Opsiyonel Varyant (M1-giris + genis-ATR-hedef):** Bu rapor kapsaminda test
EDILMEMISTIR (kapsam disi birakildi — ana odak M15+ idi); acik bir on-bulgu bu rapor icin
uretilmedi, dolayisiyla bu varyant oneri OLARAK SUNULMAMAKTADIR (gorev tanimindaki "zorunlu
degil, acik bir on-bulgu varsa" kosulu bu turda karsilanmamistir).

---

## RiSKLER / SINIRLAMALAR

1. **Kutuphane kisiti (bu ortam):** Bu arastirma ortaminda `pandas`, `lightgbm`, `xgboost`,
   `scikit-learn` KURULU DEGIL (yalniz `numpy`/`scipy` mevcut, dogrulandi). Bu rapor GERCEK BIR
   MODEL EGITMEMISTIR — yalniz numpy ile ham feature/label dagilimlari olculmustur. Model
   egitimi/hiperparametre aramasi icin Backtest Muhendisi asamasinda bu kutuphanelerin kurulu
   oldugu bir ortam gerekecektir; bu bir ACIK SORU/bagimlilik olarak asagida da not edilmistir.
2. **Overfitting/genis arama uzayi (S2):** ML/feature-tabanli yaklasimin arama uzayi (feature
   sayisi, hiperparametre, N/k kombinasyonu) kural-tabanli aileden (H1/H2/H3) cok daha genistir;
   `justin_ml_anti_overfitting_protokolu.md` (purged/embargolu walk-forward, test-seti
   tek-kullanim, feature-sizinti kontrol listesi, basari kriterlerinin onceden sabitlenmesi)
   Backtest Muhendisi asamasindan itibaren HARFI HARFINE uygulanmalidir.
3. **Veri sizintisi riski:** Bu raporda kullanilan tum rolling/trailing hesaplamalar (ATR,
   trend-SMA, RSI, MACD, hacim-medyan) NEDENSEL olarak tasarlanmistir (bar i sadece i ve
   oncesini kullanir); H1/H4 confluence eslemesi de bar i'den ONCE kapanmis H1/H4 barini
   kullanir (BULGU 5). Ancak feature normalizasyonu (olceklendirme istatistikleri) bu rapor
   asamasinda HENUZ TANIMLANMAMISTIR — Backtest Muhendisi'nin egitim-setinden-hesapla kuralini
   (S2, Madde 3) uygulamasi gerekir.
4. **Canliya-gecebilirlik:** Triple-barrier BULGU 10 SADECE brut fiyat hareketini olcer;
   spread/slipaj/komisyon dahil degildir. Gercek canli/demo performans, BULGU 11'deki
   maliyet-orani on-tahmininden daha kotu cikabilir (ozellikle P90/max spread anlarinda veya
   haber donemlerinde, bu rapor tarafindan olculmemistir).
5. **Confluence/momentum feature'larinin mekanik otokorelasyonu:** BULGU 6'daki MACD histogram
   kaliciligi (%92,3) buyuk olcude gostergenin kendi EMA-tabanli yapisindan kaynaklanir; ham
   ML modeline boyle bir feature dogrudan eklenirse, model bu mekanik otokorelasyonu "sahte bir
   sinyal" olarak ogrenebilir (ozellikle purge/embargo uygulanmazsa) — bu, S2 protokolunun
   feature-sizinti kontrol listesindeki "ileri-bakan feature" maddesinden farkli ama iliskili
   bir risktir (burada ileri-bakis yok, ama otokorelasyon nedeniyle egitim/test ayriminda
   sizinti benzeri bir sahte-performans riski var), ayrica not edilmistir.
6. **Ornek disi genelleme:** Tum bulgular XM/MT5'in GOLD sembolu icin sagladigi 2022-2026 arasi
   gecmis veriye dayanir; farkli bir donem (orn. farkli bir makro rejim) farkli sonuc verebilir.
7. **DST/saat-eslemesi:** BULGU 1/2'deki saat bazli bulgular, sunucu saatinin GMT+3 oldugu
   varsayimina dayanir (DST donemlerinde kesin davranis bu raporda dogrulanmamistir) — bu,
   `justin_backtest_onkontrol_standardi.md` Madde 1 geregi Backtest Muhendisi asamasinda
   BAGIMSIZ olarak yeniden dogrulanmalidir.

---

## ACIK SORULAR

1. Bu ortamda `pandas`/`lightgbm`/`xgboost`/`scikit-learn` kurulu degil — Backtest Muhendisi
   asamasinda bu kutuphanelerin hangi ortamda (VPS mi, ayri bir Python ortami mi) kurulacagi
   netlestirilmeli.
2. BULGU 8 (genel yon-onyargisi/drift), onceki M1/M5 raporundaki gibi dogrudan "ilk fiyat - son
   fiyat" olarak bu M15 script'inde HESAPLANMAMISTIR — sadece dolayli/turetilmis bir kanit
   (confluence n-asimetrisi) sunulmustur; istenirse ayri bir olcum turu ile netlestirilebilir.
3. Seans acilis/kapanisina mesafe (Feature Grubu 4'te onerilen ama bu raporda dogrudan
   OLCULMEYEN bir feature) ayrica hesaplanmali mi, yoksa basit saat/oturum bayraklari (BULGU
   1-2) yeterli mi — bu, Stratejist'in feature-onceligi kararina birakilmistir.
4. BULGU 11'deki maliyet-orani P90/max spread ile (medyan yerine) yeniden hesaplanirsa esik
   hala karsilaniyor mu? Bu rapor SADECE medyan uzerinden hesaplamistir; stres-testi hesap
   Backtest Muhendisi'nin on-kontrol asamasina birakilmistir.
5. HH/LL streak (BULGU 7) ve MTF confluence (BULGU 5) arasindaki olasi ETKILESIM (orn.
   confluence VARKEN HH/LL streak davranisi farkli mi) bu raporda AYRI test edilmemistir —
   feature etkilesimleri modelin kendisi (agac-tabanli model, dogal olarak etkilesim yakalar)
   tarafindan ogrenilebilir, ama bu rapor bunu ayrica dogrulamamistir.
6. Gercek slipaj (tick-bazli, sadece bar-kapanis spread'i degil) bu raporda olculmedi — onceki
   M1/M5 raporunun ACIK SORU 2'sindeki ayni bosluk burada da gecerlidir (copy_ticks_range ile
   ayri bir olcum gerektirir).

---

## iZOLASYON NOTU

- MilaGold, Lisa (ters muhendislik) ve Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md,
  positions_status.json vb.) bu arastirma sirasinda okunmadi veya referans alinmadi.
- Bu rapor icin format/sablon referansi olarak da MilaGold/Lisa/Signal GPT dosyalari
  ACILMADI — rapor formati Justin'in kendi onceki Arastirmaci raporundan (ayni proje icinde,
  `arastirmaci_gold_scalping_raporu.md`, kural-tabanli aile) ve sistem promptundaki genel
  formattan turetildi.
- Hibrit yaklasim (eski kural-tabanli M1/M5 bulgularinin/esiklerinin bu ML tasariminda on-filtre
  veya feature olarak kullanilmasi) BILINCLI OLARAK YAPILMADI — bu raporda kullanilan tum
  feature/label tanimlari (ATR, trend-SMA, RSI, MACD, HH/LL, hacim-anomali, triple-barrier)
  genel/kamuya-acik finans/ML kavramlaridir, MilaGold'un veya onceki M1/M5 raporunun spesifik
  esik/parametrelerinden (orn. EMA20/EMA100/streak>=13 gibi MilaGold'a ozel degerler)
  TURETILMEMISTIR. Metodolojik yapi (nedensel/trailing-medyan rejim etiketleme) onceki
  Justin-ici rapordan (ayni proje, izolasyon disi) devam ettirilmistir — bu, MilaGold/Lisa/
  Signal GPT izolasyonunu ihlal ETMEZ (izolasyon kurali sadece disaridan/MilaGold ailesinden
  gelen bulgu/parametre/format aktarimini kapsar, Justin'in kendi ic surekliligini degil).
  - Calisma yalniz `C:\MilaYatirim\Justin\` dizininde yapildi (girdi: gorev dosyasi,
  `justin_gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md`,
  `justin_backtest_onkontrol_standardi.md`, `arastirmaci_gold_scalping_raporu.md`; cikti:
  `research_ml_gold_scalping_m15.py`, `research_ml_gold_scalping_m15_output.json`, bu rapor).
- Tek veri kaynagi XM/MT5 GOLD sembolu, dogrudan MetaTrader5 kutuphanesi araciligiyla.

---

## STRATEJiST'E NOT

Bu rapordaki hicbir bulgu "su feature'i/N-k kombinasyonunu/modeli kullan" demez. Tum sayilar
MT5'ten dogrudan olculmustur (bkz. research_ml_gold_scalping_m15.py,
research_ml_gold_scalping_m15_output.json). Ozellikle BULGU 10-11'deki N/k degis-tokusu ve
maliyet-orani sayilari, bir sonraki asamada Stratejist'in SL/TP/ATR katsayisini belirlerken
kullanabilecegi ham girdidir — hangi N/k kombinasyonunun secilecegine, hangi feature'larin
oncelikli oldugu, hedef siniflandirma semasi (ikili vs 3-sinif) karar Stratejist'e aittir. Bu
rapor ayrica bir GERCEK MODEL EGITIMI ICERMEMEKTEDIR (kutuphane kisiti, bkz. Riskler madde 1) —
bu, Backtest Muhendisi asamasina acik bir bagimlilik/on-kosul olarak tasinmalidir.
