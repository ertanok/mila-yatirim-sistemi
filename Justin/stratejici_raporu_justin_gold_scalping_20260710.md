# STRATEJiST RAPORU — Justin / Gold Scalping Hipotezleri

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: 2/4 (Stratejist)
Tarih: 10 Temmuz 2026
Girdi: C:\MilaYatirim\Justin\arastirmaci_gold_scalping_raporu.md + research_scalping_output.json
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)

---

## OTURUM OZETI

Bu, Justin projesi icin ilk Stratejist turudur — daha once uretilmis bir hipotez veya "gecmis calisma"
dosyasi yok. Girdi olarak Arastirmaci'nin 8 bulgusu (saatlik volatilite/spread profili, bar-yon
devamliligi, buyuk-bar sonrasi takip davranisi, 20-bar SMA sapmasi sonrasi ileri getiri, orneklem
drift onyargisi, haftanin gunune gore volatilite, hafta sonu gap riski) ve 4 aday yaklasim
(Seans/Saat-Filtreli Volatilite-Breakout; Ortalamaya-Donus/Kisa-Vadeli Sapma; Rejim-Farkinda Hibrit;
Gun-Donusu/Hafta-Sonu Filtresi) kullanildi.

Onemli bir gozlem: Arastirmaci'nin Aday 1'i ("range kirilinca yonunde gir") BULGU 4 tarafindan zayif
destekleniyor — buyuk barlardan sonra gelen bar, ayni yonde devam etmek yerine hafifce TERS yonde
kapaniyor (M5 %48,6 ayni yon / %51,4 ters yon, M1 %47,1 ayni yon / %52,9 ters yon). Bu nedenle asagida
Aday 1'i oldugu gibi degil, BULGU 4'un gercekte gosterdigi yone (fade/ters-donus) cevirerek Hipotez 2
olarak yeniden kurguladim. Aday 4 (gun-donusu/hafta sonu filtresi) bagimsiz bir strateji degil, tum
hipotezlere uygulanabilir bir risk-katmani oldugu icin ayri bir hipotez yapmadim; her hipotezin
"Seans filtresi" alaninda entegre ettim ve Muhendis notlarinda tekrar vurguladim.

Izolasyon kontrolu: Bu oturumda stratejici_gold_gecmis_calisma.md veya herhangi bir MilaGold/Lisa/Signal
GPT dosyasi ACILMADI/referans ALINMADI. MilaGold'un aktif parametreleri (M5 EMA20, EMA100 streak>=13,
trailing stop, lot/SL/TP degerleri: 0.01 lot, 5$/3$/5$/8$) fikir kaynagi olarak KULLANILMADI — asagidaki
SL/TP mekanizmalari (ATR-bazli, dinamik) bilhassa bu sabit-dolar yapiyi TEKRARLAMAMAK ve BULGU 1'deki
saatlik range degiskenligine (2-3 kat fark) dogrudan cevap vermek uzere bagimsiz olarak tasarlandi.

---

## HiPOTEZLER (Dogrulama Onceligine Gore Sirali)

### HIPOTEZ 1 — Seans-Filtreli Asimetrik Ortalamaya-Donus (Mean-Reversion)

YAKLASIM TURU: Kural-tabanli (istatistiksel sapma filtresi + ATR-bazli risk yonetimi)

MANTIK: BULGU 5, M5'te alt-sapma (fiyat 20-bar SMA'nin 2 std altina dustugunde) sonrasi 5 bar ileride
ortalama getirinin +14,18 puan (M1'de +18,47 puan) oldugunu gosteriyor — tutarli bir yukari-donus
egilimi. Ust-sapma sonrasi da pozitif getiri gozlenmis ancak bu, BULGU 6'daki genel yukselis onyargisiyla
(M5 orneklem +%43,34) karisik olabilecegi icin daha az guvenilir bir sinyal. Ayrica BULGU 1/2, sunucu
saati 15-18 bandinin hem en genis range'e hem en dar/en istikrarli spread'e sahip oldugunu gosteriyor —
bu, sinyal/maliyet oranini iyilestirebilecek somut bir pencere.

YONTEM DETAYI: M5 grafik, 20-bar SMA + rolling std (BULGU 5'teki ayni tanim). Giris tetikleyicisi:
kapanis fiyati SMA - (k x std) altina dustugunde (k baslangic degeri 2,0 — BULGU 5 ile tutarli,
Backtest Muhendisi dar bir aralikta [orn. 1,5-2,5] test edebilir ama ince ayara girilmemeli). Ilk
asamada YALNIZCA uzun (long) yon test edilmesi onerilir (alt-sapma sinyali); kisa yon/ust-sapma
versiyonu ayri ve ikincil bir test olarak ele alinmali (drift onyargisindan ayristirma gerektirir,
bkz. RISKLER).

GIRIS/CIKIS MEKANIZMASI: Giris — M5 kapanisi SMA20-2std esigini asagi kirdiginda (kirilma barinin
kapanisinda veya bir sonraki bar acilisinda teyitli giris, ikisi de test edilmeli) long pozisyon.
Cikis — N bar (baslangic 5 bar, BULGU 5 ile tutarli) sonra zaman-bazli cikis VEYA ATR-bazli TP/SL'den
hangisi once tetiklenirse; Backtest Muhendisi ikisini ayri ayri ve birlikte karsilastirmali.

SL/TP: ATR(14, M5) bazli, baslangic orani 1:1 (TP ~1x ATR, SL ~1x ATR) — Backtest Muhendisi risk/odul
oranini dar bir aralikta tarayabilir. Sabit puan/USD mesafesi ONERILMIYOR: BULGU 1, saatlik ortalama
range'in ~2-3 kat degistigini gosteriyor (16. saat 574 puan medyan vs 23. saat 197 puan medyan);
sabit mesafe bazi saatlerde cok dar (erken SL), bazilarinda cok genis (hedefe ulasmayan) kalir.

Seans filtresi: yalnizca sunucu saati 15-18 (ikincil olarak 3-4) bandinda islem acilir; 0-2 ve 22-23
sunucu saatinde (BULGU 2, genis/degisken spread — max 216-248 puan sicramalari) ve hafta sonu
kapanisi/acilisi oncesi-sonrasi belirli bir pencerede (BULGU 8, gap riski) yeni islem ACILMAZ.

DOGRULAMA IHTIYACI: (1) Klasik train/test ayrimi (orn. ilk ~%70 parametre kesfi, son ~%30 disarida
tutulan test) ile temel karlilik olculmeli. (2) Walk-forward (rolling pencere) ile zaman-ustu tutarlilik
test edilmeli. (3) Detrend testi ZORUNLU: ayni analiz, fiyat serisinden rolling lineer trend cikarilmis
(detrended) bir versiyon uzerinde tekrarlanip BULGU 6 onyargisinin sonucu ne kadar etkiledigi olculmeli
— uzun yon (long-only) ile simetrik (long+short) versiyon ayri ayri karsilastirilmali.

RISKLER: (1) BULGU 6 drift onyargisi — ozellikle kisa yon/ust-sapma versiyonunda yanlis-pozitif sinyal
riski yuksek; bu yuzden ilk asamada yalniz uzun yon onerildi. (2) Overfitting — k (std carpani) ve N
(bar sayisi/tutus suresi) parametrelerinde asiri ince ayar riski; birden fazla kombinasyon denenirse
walk-forward disi (out-of-sample) performans mutlaka kontrol edilmeli. (3) Spread/hedef orani — ATR
kucuk oldugunda (dusuk volatilite saatlerinde) spread (BULGU 2, medyan 30-39 puan M5) hedefin onemli
bir kismini yiyebilir; TP'nin o anki spread'in kac katina denk geldigi backtest'te ayrica raporlanmali.
(4) Canliya gecebilirlik — kural tabanli, hafif hesaplama (SMA/std/ATR) gerektirir, gercek zamanli MT5
agent icinde hizli calisir; bu acidan risk dusuk.

ONCELIK: 1-Yuksek — en somut ham bulguya (BULGU 5) dogrudan dayaniyor, az parametreli/basit, hesaplama
maliyeti dusuk, drift riski onceden tespit edilip long-only ile sinirlandirildi, canliya gecis riski
dusuk.

---

### HIPOTEZ 2 — Buyuk-Bar Ters-Yon (Fade) Kisa Vadeli Sinyal

YAKLASIM TURU: Kural-tabanli

MANTIK: BULGU 4, ortalama range'in 1,5 katini asan "buyuk bar"lardan sonra gelen barin M5'te %51,4,
M1'de %52,9 oraninda TERS yonde kapandigini gosteriyor — yani "kirilma yonunde devam" varsayimi (orijinal
Aday 1 mantigi) yerine hafif ama olculebilir bir fade/ters-donus egilimi gozleniyor (%50'den ~1,4-2,9
puan sapma, n=16.501/15.734 ile istatistiksel olarak incelemeye deger buyuklukte bir ornek).

YONTEM DETAYI: M1 ve/veya M5'te, son N barin (orn. 20 bar) ortalama range'inin 1,5 katini asan bar
"buyuk bar" olarak isaretlenir (BULGU 4 ile ayni esik, baslangic noktasi). Giris yonu: buyuk barin
TERS yonu (buyuk bar yukari kapandiysa kisa, asagi kapandiysa uzun).

GIRIS/CIKIS MEKANIZMASI: Giris — buyuk bar kapanisinin hemen ardindan (t+1 bar acilisi) ters yonde
piyasa emri; ek olarak bir teyit katmani da test edilmeli (orn. t+1 barin da ters yonde kapanip
kapanmadigi beklenip t+2'de giris — BULGU 4 yalnizca t+1 ufkunu olcmustur, t+2/t+3 ayri test gerektirir).
Cikis — kisa vadeli sabit bar sayisi (orn. 1-3 bar) veya ATR-bazli TP/SL.

SL/TP: ATR bazli, dar mesafe. Bu bir fade/scalp sinyali oldugu icin genis SL/TP secilirse edge'in
kucuklugu (~%1,4-2,9 puan) maliyetlere kolayca yenilir; sunucu saati 15-18 bandinda (dar/istikrarli
spread, BULGU 2) test edilmesi onerilir.

DOGRULAMA IHTIYACI: (1) ONCELIKLE istatistiksel anlamlilik testi (binom/ki-kare) ile %51,4/%52,9
oraninin gercekten rastgeleden anlamli sapip sapmadigi teyit edilmeli. (2) Ardindan spread+slipaj
DAHIL net getiri simulasyonu (copy_ticks_range ile gercek tick verisi kullanilarak) — bu adim bu
hipotez icin KRITIK, cunku ham edge cok kucuk ve maliyetle kolayca silinebilir. (3) Klasik train/test
+ walk-forward, esik carpani (1,5x) ve teyit ufku (t+1 vs t+2) icin.

RISKLER: (1) Edge cok kucuk (~%1,4-2,9 puan) — islem maliyeti (spread+slipaj) bu edge'i kolayca
yutabilir, BULGU 2'deki spread degerleriyle net karsilastirma sart, dogrulama olmadan canli
uygulanabilirligi belirsiz. (2) Yuksek islem frekansi gerektirebilir (her buyuk bar bir sinyal
uretir) — kumulatif maliyet riski (Arastirmaci'nin Genel Risk 5 notu). (3) Overfitting — esik carpani
ve teyit ufku uzerinde asiri arama yapilmamali, genis/az sayida kombinasyon tercih edilmeli.
(4) Canliya gecebilirlik — basit kural, hizli hesaplanir, teknik risk dusuk; asil risk ekonomik
(maliyet/edge orani).

ONCELIK: 2-Orta — istatistiksel olarak ilginc ve hizli test edilebilir, ancak edge kucuk oldugundan
maliyet-once dogrulamasi olmadan canli uygulanabilirligi belirsiz. Hipotez 1 ile paralel/bagimsiz
dogrulanabilir, birbirini engellemez.

---

### HIPOTEZ 3 — Rejim-Farkinda Hibrit (Trend/Range Siniflandirici + Kosullu Mantik)

YAKLASIM TURU: Hibrit (kural-tabanli rejim etiketleme + opsiyonel klasik ML siniflandirici, orn.
LightGBM/Gradient Boosting)

MANTIK: BULGU 3/4, rejim ayristirilmamis (ham) bar-yon devaminin genel olarak %50'ye yakin/zayif
oldugunu gosteriyor. Ancak bu ortalama sonuc trend ve range rejimlerini karistiriyor olabilir —
Arastirmaci'nin Aday 3 hipotezine gore, rejim ayristirildiginda alt-orneklemlerde devamlilik veya
donus orani %50'den daha belirgin sapabilir. Bu ayni zamanda Justin'in ML/RL deneme beklentisiyle
(CLAUDE.md, PROJE 2 profili) dogrudan uyumlu bir hipotezdir.

YONTEM DETAYI:
- Asama 1 (kural-tabanli rejim etiketi): ATR(14)/rolling-std genisligi ve N-bar (orn. 20 bar) net
  fiyat egimi kullanilarak her bar "trend" veya "range" olarak etiketlenir.
- Asama 2 (kosullu mantik): range rejiminde Hipotez 1'deki mean-reversion mantigi, trend rejiminde
  devam-yonlu (momentum) bir mantik ayri ayri test edilir.
- Asama 3 (opsiyonel, ML): rejim etiketleri + BULGU 1-5 turunden ozellikler (feature: saat, ATR,
  kisa-vadeli sapma buyuklugu, mevcut streak uzunlugu) girdi olarak bir gradient boosting
  siniflandiricisina (orn. LightGBM) verilip "sonraki N bar yonu/rejim devami" tahmini icin egitilebilir.

GIRIS/CIKIS MEKANIZMASI: Kural-tabanli versiyon — rejim etiketine gore Hipotez 1 (range rejiminde) veya
basit momentum kurali (trend rejiminde) devreye girer. ML versiyonu — siniflandiricinin uretecegi
olasilik skoru bir esigi (orn. >0,55-0,60) astiginda giris, esik altinda islem yok.

SL/TP: ATR bazli (Hipotez 1 ile ayni mantik), rejime gore carpan farklilastirilabilir (trend
rejiminde daha genis TP, range rejiminde daha dar).

DOGRULAMA IHTIYACI: ML versiyonu icin ZORUNLU zaman-sirali train/validation/test ayrimi (orn.
%60/%20/%20, karistirilmadan) + walk-forward; train/test arasi performans farki genislerse (overfitting
isareti) model karmasikligi azaltilmali veya veri artirilmali. Kural-tabanli versiyon icin klasik
train/test + walk-forward yeterli olabilir, ML asamasindan once ayri raporlanmali.

RISKLER: (1) Rejim tanimi kendisi bir parametre secimidir — asiri-uyum riski yuksek; esik degerleri
gorece genis araliklarda test edilmeli, ince ayara girilmemeli. (2) Veri sizintisi (look-ahead bias)
riski ML versiyonunda daha yuksek — rejim etiketleme ve feature hesaplamalarinin yalnizca gecmis
veriyi kullandigi (ileri-bakis yok) dikkatle dogrulanmali. (3) Alt-orneklem kuculmesi — bazi
rejimlerde (orn. "guclu trend") yeterli ornek olmayabilir, istatistiksel guven dusebilir.
(4) Canliya gecebilirlik — ML versiyonu gercek zamanli MT5 agent icinde model yukleme/tahmin suresi
gerektirir; bu surenin MT5 agent'in dongu periyoduyla uyumlu olup olmadigi ayrica dogrulanmali, ayrica
model versiyonlama/dagitim karmasikligi ekler (kural-tabanli versiyona gore). (5) En yuksek karmasiklik
= en yuksek risk; Hipotez 1/2 sonuclari once alinip bu hipotez onlarin uzerine (feature olarak) insa
edilmesi onerilir.

ONCELIK: 3-Dusuk (bu turda) — konsept olarak degerli ve Justin'in ML/RL profiliyle uyumlu, ancak
Hipotez 1/2'den daha karmasik/riskli (overfitting + canliya gecebilirlik). Once kural-tabanli rejim
versiyonuyla baslanip (Hipotez 1/2 sonuclarindan sonra) ML versiyonuna kademeli gecilmesi onerilir.

---

## BACKTEST MUHENDiSi iCiN NOTLAR

1. **Sira onerisi:** Hipotez 1 → Hipotez 2 (paralel/bagimsiz olabilir) → Hipotez 3 (once kural-tabanli
   alt-versiyonu, sonra ML). Hipotez 3'un feature seti Hipotez 1/2'nin sonuclarindan beslenebilir,
   bu yuzden en son siraya alindi.
2. **Evrensel filtre katmani (Aday 4):** Yukaridaki uc hipotezin hepsi icin — sunucu saati 0-2 ve 22-23
   bandinda ve hafta sonu acilis/kapanis penceresinde yeni islem ACILMAMASI ayri ayri test edilmeli
   (filtreli vs filtresiz karsilastirmasi ile filtrenin net katkisi olculmeli, korlemesine eklenmemeli).
3. **Saat esleme dogrulamasi (Acik Soru 1):** Tum saat-bazli filtreler (15-18 bandi, 0-2/22-23 haric
   tutma) MT5 sunucu saatinin GMT+3'e tam esit oldugu varsayimina dayanir; DST donemlerinde bu ofset
   degisebilir. Backtest calismaya baslamadan once bu varsayim (orn. bilinen bir haber/rollover
   zamanindan geriye dogru dogrulanarak) teyit edilmeli, aksi halde saat-bazli filtreler kaymis olabilir.
4. **Detrend/drift kontrolu:** Hipotez 1 (ve varsa Hipotez 3'un range-rejim alt versiyonu) icin
   detrended veri testi zorunlu adimdir, atlanmamali (BULGU 6).
5. **Maliyet dahil simulasyon:** Hipotez 2 icin spread+slipaj dahil net getiri hesaplamasi olmadan
   "calisir" degerlendirmesi yapilmamali; mumkunse tum hipotezler icin bar-kapanis spread'i yerine
   tick-bazli spread/slipaj kullanilmasi (BULGU 2 SINIR notu) daha guvenilir sonuc verir.
6. **Istatistiksel anlamlilik:** Hipotez 2'nin ham edge'i kucuk oldugundan, backtest sonucu yaninda
   binom/ki-kare gibi bir anlamlilik testi de raporlanmali.
7. **Overfitting guvenlik agi:** Hicbir hipotezde parametre taramasi genis olmamali (birkac makul
   deger, ince ayar degil); her taramada mutlaka out-of-sample/walk-forward karsilastirmasi rapor
   edilmeli.
8. Sonuclar geldiginde Stratejist bu rapor uzerine (ayni dosya adi + tarih artimi ile) rafine edecek;
   Justin icin ilk "gecmis calisma/cerceve" dosyasinin cekirdegi bu rapor ile sonraki Backtest
   Muhendisi turunun sonuclari olabilir.

---

## iZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (stratejici_gold_gecmis_calisma.md,
  signal.json, milagold_trades.json, lisa_performance.json, positions_status.json vb.) ACILMADI
  veya referans ALINMADI.
- MilaGold'un aktif filtreleri/parametreleri (M5 EMA20, EMA100 streak>=13, trailing stop, 0,01 lot,
  5$/3$/5$/8$ SL/TP degerleri) fikir kaynagi olarak KULLANILMADI; yukaridaki ATR-bazli dinamik SL/TP
  tercihi bilhassa bu sabit-dolar yapiyi tekrarlamamak icin BULGU 1'deki saatlik range degiskenligine
  dayanarak bagimsiz kurgulandi.
- Calisma yalnizca C:\MilaYatirim\Justin\ dizininde yapildi (girdi: arastirmaci_gold_scalping_raporu.md,
  research_scalping_output.json; cikti: bu dosya).

---

## ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (canli sisteme dokunus yok, Justin
demo/arastirma asamasinda). Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
