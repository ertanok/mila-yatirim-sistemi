# ARASTIRMACI RAPORU — Justin / Gold Scalping Arastirmasi

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: 1/4 (Arastirmaci)
Tarih: 10 Temmuz 2026
Veri kaynagi: XM/MT5, dogrudan MetaTrader5 kutuphanesi, sembol "GOLD" (spot metal, contract_size=100, point=0.01)
Analiz script'i: C:\MilaYatirim\Justin\research_scalping.py (ham cikti: research_scalping_output.json)

---

## OZET

- Bu rapor MT5'ten cekilen ham M1/M5 OHLCV+spread verisiyle GOLD'un kisa vadeli davranisini olcer.
- M1 veri araligi: 2026-03-30 → 2026-07-10 (99.999 bar, ~69 islem gunu). M5 veri araligi: 2025-02-10 → 2026-07-10 (99.999 bar, ~17 ay).
- Onemli bulgu: bar-to-bar yon devamliligi (M1 ve M5) rastgele yürüyüse yakin (~%48-49), yani basit "bir onceki bar hangi yondeyse devam eder" varsayimi bu veri setinde zayif destekleniyor.
- Volatilite (bar range) sunucu saatine gore belirgin sekilde degisken: en yuksek 15-17 sunucu saati bandinda, en dusuk 23 ve 6-7 sunucu saati bandinda.
- Spread, gun icinde ~%35-40 oraninda dalgalaniyor; en genis ve en degisken spread gun donusu/rollover saatlerinde (0-2 sunucu saati) ve seans kapanisina yakin saatlerde (22-23) gorulüyor.
- Hafta sonu gap riski somut ve buyuk: 75 hafta sonu gecisinde medyan mutlak gap ~592 puan ($5,92/ons), ortalama ~1270 puan, maksimum 8531 puan ($85,31/ons) — bu, M5 medyan bar range'inin (343 puan) kat kat uzerinde.
- Veri setinin kendisi yon-notr degil: M5 orneklemi (17 ay) %43,3 net yukselis, M1 orneklemi (69 gun) %8,1 net dusus icermektedir — bu durum devamlilik/ortalamaya-donus olcumlerini etkileyebilecek bir trend-onyargisi (drift bias) olarak SINIR bolumunde ayrica belirtilmistir.

---

## GOZLEMLER

### BULGU 1 — Saatlik Volatilite Profili (bar range)
Veri Kaynagi: MT5 GOLD M1 ve M5, copy_rates_from_pos, M1: 99.999 bar (2026-03-30→2026-07-10), M5: 99.999 bar (2025-02-10→2026-07-10). Saat, sunucu saatine gore (VPS/MT5 sunucu saat dilimi GMT+3 varsayimiyla; kesin DST/ofset dogrulanmadi, bkz. ACIK SORULAR).
---------------------------------------------------------------
GOZLEM (M5, ortalama bar range, puan cinsinden — 1 puan = 0,01 USD):
| Sunucu Saati | Ort. Range | Medyan Range | P90 Range | n |
|---|---|---|---|---|
| 16 | 733,8 | 573,0 | 1346,0 | 4380 |
| 17 | 723,3 | 555,0 | 1296,0 | 4380 |
| 15 | 617,2 | 475,0 | 1114,0 | 4380 |
| 18 | 558,1 | 421,5 | 1034,0 | 4380 |
| 3 | 556,0 | 404,0 | 1048,4 | 4344 |
| 4 | 570,0 | 435,0 | 1050,0 | 4344 |
| ... | | | | |
| 23 | 279,8 | 197,0 | 525,9 | 3792 |
| 6 | 342,7 | 274,0 | 632,0 | 4351 |
| 7 | 365,2 | 267,5 | 684,0 | 4356 |

(Tam 24 saatlik tablo research_scalping_output.json icinde "M5_hourly" ve "M1_hourly" anahtarlarinda mevcuttur.)

BAGLAM: Sunucu saatiyle 15-18 bandi, olcum donemi boyunca en yuksek ortalama/medyan/P90 bar range degerlerine sahip saat dilimidir (M5 medyan range 16. saatte 573 puan, 23. saatteki 197 puanin ~2,9 katidir). 3-4. saat bandinda ikinci bir yerel tepe gozlenmektedir. En dusuk volatilite 23. saatte (gun sonu) ve 6-7. saat bandinda (yerel cukur) olcülmustur.

SINIR: Saat eslemesi sunucu epoch degerinin dogrudan UTC gibi okunmasiyla yapilmistir (MT5 standart davranisi); GMT+3 varsayimi CLAUDE.md'deki VPS bilgisine dayanir ama DST donemlerinde sunucunun kendi ofset degisikligi ayrica dogrulanmamistir. Ornek buyuklugu saat basina ~3800-4380 bar (M5) ile yeterli.

### BULGU 2 — Saatlik Spread Profili
Veri Kaynagi: MT5 GOLD M1/M5 rates['spread'] alani (broker'in raporladigi puan cinsinden spread), ayni veri araligi.
---------------------------------------------------------------
GOZLEM (M1, puan cinsinden):
| Sunucu Saati | Ort. Spread | Medyan Spread | Max Spread |
|---|---|---|---|
| 1 | 59,3 | 54,0 | 232 |
| 2 | 51,3 | 52,0 | 59 |
| 16 | 44,2 | 46,0 | 55 |
| 17 | 44,2 | 46,0 | 55 |
| 23 | 50,2 | 50,0 | 143 |

Canli (rapor anindaki) spread: 56 puan.

BAGLAM: En dar ortalama/medyan spread 15-18 sunucu saati bandinda (44-45 puan) gozlenmistir — bu ayni zamanda BULGU 1'deki en yuksek volatilite bandiyla ortusmektedir. En genis ve en degisken spread (max deger sicramalari: 232, 216, 188, 143, 134 puan) gun donusune yakin saatlerde (0-2) ve gun/seans kapanisina yakin saatlerde (22-23) gorulmustur. Ortalama spread ile max spread arasindaki fark bu saatlerde (0-2, 22-23) digerlerine gore belirgin sekilde daha genis.

SINIR: Spread degeri MT5'in rapor ettigi anlik/bar-kapanis spread'idir, tick-by-tick spread dagilimi degildir; gercek execution sirasinda gorulen spread bundan farkli olabilir (ozellikle haber anlari, MT5 bar-close spread'inde yakalanmayabilir).

### BULGU 3 — Bar Yon Devamliligi (Continuation)
Veri Kaynagi: MT5 GOLD M1 (99.686 yonlu bar) ve M5 (99.787 yonlu bar), close-open isaretine gore yon.
---------------------------------------------------------------
GOZLEM:
- M1: ardisik iki barin ayni yonde olma orani = %48,6
- M5: ardisik iki barin ayni yonde olma orani = %49,3
- N ardisik ayni yonlu bar sonrasi bir sonraki barin ayni yonde olma orani (M1): 2-streak → %48,5 (n=25208), 3-streak → %47,4 (n=12224), 4-streak → %48,1 (n=5794), 5-streak → %46,2 (n=2788)
- Ayni olcum (M5): 2-streak → %48,7 (n=25422), 3-streak → %48,3 (n=12374), 4-streak → %46,5 (n=5979), 5-streak → %49,4 (n=2779)

BAGLAM: Tum streak uzunluklarinda sonraki-bar-ayni-yon orani %50'nin altinda veya cok yakininda seyretmektedir; artan streak uzunlugu ile orandaki degisim monoton veya belirgin degildir. Bu, ham bar-yonu bazinda basit devamlilik varsayiminin bu veri setinde guclu bir sinyal uretmedigini gosterir.

SINIR: Bu olcum yalnizca bar-open/close isaretine dayanir (intrabar hareket, fitil, hacim dikkate alinmamistir); farkli bir yon tanimi (orn. N-bar sonrasi net getiri) farkli sonuc verebilir.

### BULGU 4 — Buyuk Bar (Breakout) Sonrasi Takip Davranisi
Veri Kaynagi: MT5 GOLD M1/M5, range > 1,5 x ortalama range esigini asan barlar.
---------------------------------------------------------------
GOZLEM:
- M5: 16.520 "buyuk bar" tespit edildi; sonraki bar ayni yonde %48,6, ters yonde %51,4 (n=16.501 yonlu cift)
- M1: 15.734 "buyuk bar" tespit edildi; sonraki bar ayni yonde %47,1, ters yonde %52,9

BAGLAM: Ortalamanin 1,5 katini asan barlardan sonra gelen bar, olcum boyunca ayni yonde devam etmekten ziyade hafifce ters yonde kapanma egilimindedir (M1'de bu egilim M5'e gore biraz daha belirgin).

SINIR: Tek esik (1,5x) ve tek sonraki-bar ufku (t+1) test edilmistir; farkli esik/ufuk kombinasyonlari test edilmedi.

### BULGU 5 — 20-Bar SMA'dan Sapma Sonrasi 5-Bar Ileri Getiri (Mean Reversion Testi)
Veri Kaynagi: MT5 GOLD M1/M5, 20-bar SMA ve rolling std, sapma > 2 std esigi.
---------------------------------------------------------------
GOZLEM:
- M5: ust sapma (fiyat SMA+2std uzerinde) sonrasi 5 bar ileride ortalama getiri = +17,98 puan (n=6099); alt sapma (SMA-2std altinda) sonrasi 5 bar ileride ortalama getiri = +14,18 puan (n=6100)
- M1: ust sapma sonrasi 5 bar ileride ortalama getiri = +3,85 puan (n=5600); alt sapma sonrasi 5 bar ileride ortalama getiri = +18,47 puan (n=6090)

BAGLAM: Alt sapmalarda (fiyat ortalamanin altina dustugunde) 5 bar sonraki hareket pozitif (fiyat yukselmis) — bu ortalamaya-donus yonunde bir gozlemdir. Ust sapmalarda ise 5 bar sonraki hareket de pozitif cikmistir (fiyat yukselmeye devam etmis) — bu, ortalamaya-donusten ziyade yon devaminin bir isareti olabilir, ANCAK bu ayrimin veri setindeki genel yukselis onyargisindan (bkz. BULGU 6 ve SINIR) bagimsiz olup olmadigi bu analizde ayristirilmamistir.

SINIR: Bu bulgu, asagidaki BULGU 6'da tanimlanan yon-onyargili orneklem uzerinde yapilmistir; sonuclar trendden bagimsizlastirilmamis (detrend edilmemis) fiyat serisi uzerindendir.

### BULGU 6 — Orneklem Donemindeki Genel Yon Onyargisi (Drift)
Veri Kaynagi: MT5 GOLD M1/M5 ilk ve son kapanis fiyatlari, ayni veri araligi.
---------------------------------------------------------------
GOZLEM:
- M5 orneklemi (2025-02-10 → 2026-07-10, ~17 ay): ilk kapanis 2877,02, son kapanis 4123,88 → toplam degisim +1246,86 USD (+%43,34); yukari kapanan bar orani %50,59, asagi kapanan %49,20
- M1 orneklemi (2026-03-30 → 2026-07-10, ~69 gun): ilk kapanis 4488,07, son kapanis 4123,88 → toplam degisim -364,19 USD (-%8,11); yukari kapanan bar orani %49,54, asagi kapanan %50,15

BAGLAM: Bar bazinda yukari/asagi kapanis oranlari %50'ye yakin olsa da (mikro-seviyede dengeli), toplam fiyat degisimi her iki orneklemde de belirgin bir net yon icermektedir (M5'te guclu yukselis, M1'de daha kisa donemde net dusus). Bu, ozellikle BULGU 5'teki gibi yon-hassas olcumlerin yorumunda dikkate alinmasi gereken bir arka plan kosuludur.

SINIR: Bu iki orneklem farkli zaman araliklarini kapsadigindan (M1 kisa/yakin donem, M5 uzun/gecmis donem) dogrudan karsilastirilamaz; sadece "her ikisi de yon-notr degil" tespiti icin kullanilmistir.

### BULGU 7 — Haftanin Gunune Gore Volatilite
Veri Kaynagi: MT5 GOLD M5, gun-ici ortalama bar range, haftanin gunune gore gruplanmis (UTC gun damgasi).
---------------------------------------------------------------
GOZLEM: Ortalama M5 bar range (puan) — Pazartesi 492,0 (n=20175), Sali 453,3 (n=20424), Carsamba 455,4 (n=20328), Persembe 485,6 (n=19810), Cuma 474,2 (n=19262)

BAGLAM: Gunler arasi fark sinirlidir (~%9 bant genisliginde, 453-492 puan araligi); Pazartesi en yuksek, Sali/Carsamba goreceli en dusuk ortalama range'e sahiptir.

SINIR: Cumartesi/Pazar verisi yok (piyasa kapali); haftanin ilk/son bar(lar)i seans acilis/kapanis kesintileri nedeniyle kismi gun icerebilir.

### BULGU 8 — Hafta Sonu Gap Riski
Veri Kaynagi: MT5 GOLD M5, ardisik iki bar arasi zaman farki >24 saat olan gecisler (hafta sonu tatili) tespit edilip, o gecisteki open-close farki puan cinsinden olculdu.
---------------------------------------------------------------
GOZLEM: 75 hafta sonu gecisi tespit edildi (2025-02-10 → 2026-07-10 arasi). Mutlak gap: ortalama 1270,2 puan, medyan 592,0 puan, maksimum 8531,0 puan. Ornek buyuk gap'ler: 2025-04-07 haftabasi -3048,0 puan, 2025-04-14 haftabasi -1077,0 puan.

BAGLAM: Medyan hafta sonu gap (592 puan / $5,92 ons basi) BULGU 1'deki M5 medyan gun-ici bar range'inin (343 puan) yaklasik 1,7 kati buyuklugundedir; bazi haftalarda bu deger 8000 puanin (80 USD/ons) uzerine cikmaktadir.

SINIR: 75 ornek (~17 aylik donem), tum hafta sonu gap dagilimini temsil etmeyebilir; ozellikle 2025 Nisan ayindaki asiri degerler (muhtemelen makro/jeopolitik bir olaya bagli) dagilimi carpitiyor olabilir — bu olayin kendisi arastirilmamistir (kapsam disi).

---

## ADAY YAKLASIMLAR (Hipotez Duzeyinde, En Az 3)

Asagidaki yaklasimlar test edilebilir hipotezlerdir; nihai kural/parametre secimi Stratejist'e aittir.

### Aday 1 — Seans/Saat-Filtreli Volatilite-Breakout
**Hipotez:** Yuksek volatilite penceresinde (BULGU 1'e gore sunucu saati 15-18 ve ikincil olarak 3-4 bandi) olusan kisa-vadeli range genislemeleri, dusuk volatilite/genis-spread pencerelerine (0-2, 22-23 sunucu saati) gore daha elverisli bir risk/spread orani sunabilir (BULGU 2: bu saatlerde spread de goreceli dar).
**Test edilecek ham veri:** M1/M5 OHLC range, saat bazli spread (mevcut research_scalping.py cikti formatiyla genisletilebilir), gerceklesen slipaj icin tick verisi (copy_ticks_range).
**Riskler/Tuzaklar:** BULGU 4, buyuk barlardan sonra hafif ters-yon egilimi gosteriyor — saf "range kirilinca yonunde gir" mantigi bu veri setinde guclu bir avantaj sunmuyor olabilir; giris zamanlamasi/onay mekanizmasi (ikinci bar teyidi, hacim vb.) ayrica arastirilmali.

### Aday 2 — Ortalamaya-Donus / Kisa-Vadeli Sapma Yaklasimi
**Hipotez:** Fiyatin kisa donem hareketli ortalamadan (BULGU 5'te 20-bar SMA ornegi) belirli bir esigin (orn. N x rolling-std) otesine sapmasi, kisa vadede (birkac bar icinde) kismi bir geri donus/normallesme ile iliskili olabilir — ozellikle asagi yonlu sapmalarda (BULGU 5, alt sapma sonrasi pozitif ileri getiri).
**Test edilecek ham veri:** M1/M5 close serisi, rolling ortalama/std (VWAP hesaplanacaksa tick_volume/real_volume alani, GOLD'da real_volume genelde 0 olabilecegi icin tick_volume kullanimi ayrica dogrulanmali).
**Riskler/Tuzaklar:** BULGU 6'daki genel yon-onyargisi (drift) bu olcumu kirletebilir — trend donemlerinde "ortalamaya donus" sinyali surekli trend yonunde yanlis pozitif uretebilir; detrend/rejim-filtresi (trend vs range rejimi ayrimi) olmadan dogrudan uygulanmasi riskli.

### Aday 3 — Rejim-Farkinda (Regime-Aware) Hibrit Yaklasim
**Hipotez:** BULGU 3 ve 4, ham bar-yon devaminin genel olarak zayif (~%50'ye yakin) oldugunu gosteriyor; ancak bu, TUM rejimler icin ortalama bir sonuc olabilir — trend/range rejimi ayristirildiginda (orn. ATR bandı genisligi, N-bar net yon egimi gibi rejim gostergeleriyle) alt-orneklemlerde devamlilik veya donus orani %50'den belirgin sekilde sapabilir. Bu, klasik kural-tabanli yaklasimlarin yaninda basit bir ML siniflandirici (rejim etiketi → devam/donus olasiligi) ile de test edilebilir bir hipotezdir (Justin'in ML/RL denemesi beklentisiyle uyumlu).
**Test edilecek ham veri:** M1/M5 OHLC, ATR/rolling-std tabanli rejim etiketleri (ham fiyattan turetilir), continuation/reversal oranlarinin rejim bazinda yeniden hesaplanmasi.
**Riskler/Tuzaklar:** Rejim tanimi kendisi bir parametre secimidir (asiri-uyum/overfitting riski); alt-orneklem sayisi kuculdukce (orn. az sayida "guclu trend" bar'i) istatistiksel guven dusebilir.

### Aday 4 — Gun-Donusu/Rollover ve Hafta-Sonu Filtresi (Yaklasimdan Bagimsiz, Tum Adaylara Uygulanabilir Bir Katman)
**Hipotez:** BULGU 2 ve BULGU 8'e gore, gun donusu (0-2 sunucu saati) ve hafta sonu gecisleri, hem spread genisligi/degiskenligi hem de gap riski acisindan farkli bir risk rejimi olusturuyor; herhangi bir scalping yaklasimindan bagimsiz olarak, bu pencerelerde pozisyon acilmamasi veya acik pozisyonlarin bu pencereler oncesinde kapatilmasi ayri bir test konusu olabilir.
**Test edilecek ham veri:** Saat/gun bazli spread dagilimi (mevcut), hafta sonu gap dagilimi (mevcut, BULGU 8), gerceklesen islem maliyeti simulasyonu icin tick verisi.
**Riskler/Tuzaklar:** Bu bir "filtre" onerisidir, bagimsiz bir sinyal degildir; asiri kisitlayici uygulanirsa islem frekansini scalping icin yetersiz seviyeye indirebilir (frekans/getiri dengesi Stratejist'in karari).

---

## RiSKLER / SINIRLAMALAR (Genel)

1. **Spread/hedef orani:** BULGU 2'ye gore tipik spread 33-59 puan (0,33-0,59 USD/ons) araliginda; scalping hedefleri kucuk oldugunda (orn. birkac USD/ons mertebesinde bir hedef), spread tek basina hedefin onemli bir kismini olusturabilir. Kesin oran, Stratejist'in sececegi hedef/SL parametrelerine bagli olarak ayrica hesaplanmalidir (bu rapor kapsaminda parametre onerilmemistir).
2. **Slipaj:** Bu rapor yalnizca bar-kapanis spread'ini olcmustur; gercek emir gerceklesmesindeki slipaj (ozellikle BULGU 1'deki yuksek volatilite pencerelerinde) ayri bir olcum gerektirir (tick/emir gecmisi analizi).
3. **Gap riski:** BULGU 8, hafta sonu gap'lerinin buyuk ve degisken oldugunu gosteriyor; gun-ici gap riski (orn. dusuk likidite saatlerinde ani hareketler) bu raporda ayri olculmedi.
4. **Veri onyargisi (drift):** BULGU 6, her iki orneklemin de yon-notr olmadigini gosteriyor; devamlilik/donus istatistikleri (BULGU 3-5) bu onyargidan tam olarak ayristirilmamistir.
5. **Islem maliyeti/frekans:** Scalping'in dogasi geregi yuksek islem frekansi, kumulatif spread maliyetini buyutur; bu rapor tek-islem spread'ini olcmustur, kumulatif etki modellenmemistir.
6. **Ornek disi genelleme:** Tum bulgular MT5/XM'in GOLD sembolu icin sagladigi gecmis veriye dayanir; baska bir broker/likidite kaynaginda spread/gap davranisi farkli olabilir.

---

## ACIK SORULAR

1. MT5 sunucu saat diliminin (server time) GMT+3'e tam olarak esit olup olmadigi ve DST donemlerinde nasil davrandigi dogrulanmali (BULGU 1/2'deki saat eslemesi buna baglidir).
2. GOLD sembolunde real_volume alani anlamli mi (0 mi geliyor), yoksa VWAP/hacim-tabanli yaklasimlar icin yalnizca tick_volume mu kullanilmali?
3. Aday 3'teki "rejim" tanimi (trend vs range ayrimi) hangi somut esiklerle yapilacak — bu Stratejist'in karar alani.
4. Scalping icin hedeflenen tutus suresi/hedef buyuklugu (USD/ons veya puan cinsinden) netlestiginde, BULGU 2'deki spread verisiyle somut bir maliyet/hedef orani hesaplanabilir — bu oran olmadan "hangi yaklasim scalping'e uygun" sorusu tam yanitlanamaz.
5. 2025 Nisan ayindaki asiri hafta sonu gap'lerinin (BULGU 8) tekil bir olaya mi (orn. makro haber) yoksa daha genel bir volatilite rejimine mi bagli oldugu bu rapor kapsaminda arastirilmadi; gerekirse ayri bir arastirma konusu olabilir.
6. Bu ortamda WebSearch araci kullanilamadi (izin reddi); bu nedenle "genel/halka acik bilgi" bolumu MT5-disi bagimsiz kaynak taramasi icermiyor, yalnizca MT5'ten olculen ham verilere dayaniyor. Harici literatur/kaynak karsilastirmasi istenirse ayri bir arastirma turu (web erisimi acik bir ortamda) gerekir.

---

## iZOLASYON NOTU

- MilaGold, Lisa (ters muhendislik) ve Signal GPT'ye ait hicbir dosya (signal.json, milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md, positions_status.json vb.) bu arastirma sirasinda okunmadi veya referans alinmadi.
- Signal GPT'nin M30/M5 EMA100 karar mekanizmasi baslangic noktasi olarak KULLANILMADI.
- MilaGold'un aktif filtreleri (M5 EMA20, EMA100 streak>=13, trailing stop parametreleri, lot/SL/TP degerleri) fikir kaynagi olarak KULLANILMADI. Bu raporda gecen EMA/SMA/ATR gibi kavramlar genel/halka acik finans kavramlaridir, MilaGold'un spesifik parametrelerinden turetilmemistir.
- Calisma yalnizca C:\MilaYatirim\Justin\ dizininde yapildi (research_scalping.py, research_scalping_output.json, bu rapor).
- Bu ortamda WebSearch araci izin reddi nedeniyle kullanilamadi; bu, rapordaki "genel piyasa bilgisi" iceriginin harici/akademik kaynaklarla desteklenmedigi, yalnizca MT5'ten olculen ham veriye dayandigi anlamina gelir (ayrica bkz. ACIK SORULAR madde 6). Bu bir veri-izolasyon kisiti degil, arac erisim kisitidir — ayri not dusulmustur.

---

## STRATEJiST'E NOT

Bu rapordaki hicbir bulgu "su indikatoru/parametreyi kullan" demez. Tum sayilar MT5'ten dogrudan olculmustur (bkz. research_scalping.py, research_scalping_output.json). Stratejist bu ham gozlemleri kullanarak hipotez/parametre karari verecektir; ozellikle Aday 1-4 birbirinden bagimsiz baslangic noktalaridir, birlikte veya ayri ayri degerlendirilebilir.

---

## EK BOLUM (12 Temmuz 2026) — REJIM-SEGMENTLI BULGU 3/4 TEKRARI (Hipotez 3 On-Kosulu)

Kaynak gorev: Stratejist raporu stratejici_raporu_justin_gold_scalping_20260712.md, Bolum 6
("Arastirmaci icin dar kapsamli ek-veri talebi"). Bu bolum yeni bir arastirma konusu/veri
kaynagi ACMAZ — mevcut BULGU 3 ve BULGU 4'un AYNI olcumlerini, ayni GOLD M1/M5 serisi (99.999
bar) ve ayni buyuk-bar esigi (1,5x ortalama range) uzerinde, rejim etiketine gore alt-
orneklemlere bolerek tekrarlar. Analiz script'i: research_scalping_rejim.py (ham cikti:
research_scalping_rejim_output.json). Bu, Hipotez 3'un Backtest Muhendisi'ne gecip
gecmeyecegini belirleyen bir ON-KOSUL/KAPI olcumudur; hangi senaryonun (gecis/erken-kapanis)
gerceklestigine karar vermek Stratejist'e aittir.

**Yontem — Rejim etiketleme (nedensel/ileri-bakissiz):**
- **VOL etiketi (volatilite genisligi):** ATR(14), bar i'de yalniz bar(i-13..i) kullanilarak
  hesaplanir (causal). Bar i'nin ATR(14) degeri, KENDI trailing 100-barlik penceresinin
  (bar i-99..i, yine yalniz gecmis+kendisi) medyaniyla kiyaslanir -> "genis" (ATR14[i] >
  trailing medyan) veya "dar" (<=).
- **TREND etiketi (Kaufman Efficiency Ratio, 20-bar):** ER20[i] = |close[i]-close[i-20]| /
  sum(|close[j]-close[j-1]|, j=i-19..i) — net yer degistirme / kat edilen toplam yol; 1'e
  yakin deger guclu tek-yonlu hareketi (trend), 0'a yakin deger fiyatin net yer degistirmeden
  ileri-geri gittigi durumu (range/choppy) temsil eder. ER20[i], KENDI trailing 100-barlik
  penceresinin medyaniyla kiyaslanir -> "trend" (>medyan) veya "range" (<=medyan).
- Her iki esik de (ATR trailing medyan, ER trailing medyan) o ana kadarki GECMIS veriden
  turetilir; hicbir noktada ileri-bakis (gelecek bar) kullanilmamistir. Esikler sabit/global
  bir deger degil, her bar icin kendi trailing penceresidir.
- Regime etiketi bar i'ye atanir ve bir sonraki barin (i+1) yonunu tahmin etmek icin
  kullanilir — BULGU 3/4'un orijinal mantigiyla ayni ("bar i'de bilinen bilgiyle bar i+1 ne
  yapar"), sadece bar i'nin rejim etiketi de bilgiye eklenmistir.
- **Istatistiksel anlamlilik yontemi:** Risk Analisti'nin Hipotez 2'de uyguladigi yontemle
  BIREBIR AYNI — scipy.stats.binomtest (iki-yonlu, H0: p=0,5) + ki-kare uygunluk testi (df=1),
  alpha=0,05.

### BULGU 9 — Rejim Etiket Dagilimi (Orneklem Buyuklukleri)
Veri Kaynagi: research_scalping_rejim.py, compute_regime_labels(), M1 ve M5, 99.999 bar (ayni ana veri).
---------------------------------------------------------------
GOZLEM:
| TF | Etiketlenen bar (VOL/TREND) | VOL: genis / dar | TREND: trend / range |
|---|---|---|---|
| M1 | 99.887 / 99.880 | 45.564 / 54.323 | 49.451 / 50.429 |
| M5 | 99.887 / 99.880 | 50.032 / 49.855 | 49.392 / 50.488 |

BAGLAM: Toplam 99.999 bardan ~99.880-99.887'si etiketlenebilmistir (ilk ~112-119 bar, ATR/ER'nin
kendi 100-bar trailing-medyan esigini olusturacak yeterli gecmise sahip olmadigi icin
etiketsiz kalir — bu, nedensellik/ileri-bakissizlik kosulunun dogal bir maliyetidir). Her iki
etiket sisteminde de iki kategori (genis/dar, trend/range) orneklem hacmi bakimindan kabaca
DENGELIDIR (en fazla sapma M1 VOL'da %45,6/%54,3 — yine de her iki tarafta da onbinlerce bar
kalmaktadir).

SINIR: Trailing-medyan esikleri (100 bar) tek bir pencere buyuklugu ile sabitlenmistir; farkli
pencere (orn. 50 veya 200 bar) farkli bir denge/etiketleme dagilimi uretebilir — bu, Backtest
Muhendisi asamasinda ayri bir parametre-hassasiyet sorusu olabilir.

### BULGU 10 — M1: BULGU 3'un (Ardisik Bar Devami) Rejim-Segmentli Tekrari
Veri Kaynagi: research_scalping_rejim.py, continuation_by_regime(), M1, 99.999 bar.
---------------------------------------------------------------
GOZLEM (genel ardisik-ikili ayni-yon orani, rejim bazinda):
| Etiket | Kategori | n | Ayni-yon orani | binom p | anlamli mi (a=0,05) |
|---|---|---|---|---|---|
| VOL | genis | 45.333 | 0,487 | 1,47e-08 | EVET |
| VOL | dar | 53.922 | 0,486 | 1,60e-10 | EVET |
| TREND | trend | 49.137 | 0,483 | 5,25e-14 | EVET |
| TREND | range | 50.111 | 0,490 | 4,98e-06 | EVET |

GOZLEM (streak-sonrasi, sonraki-bar-ayni-yon orani; n / oran / anlamli mi):
| Streak | VOL-genis | VOL-dar | TREND-trend | TREND-range |
|---|---|---|---|---|
| 2 | 11.429 / 0,490 / EVET | 13.745 / 0,480 / EVET | 12.212 / 0,485 / EVET | 12.959 / 0,484 / EVET |
| 3 | 5.607 / 0,472 / EVET | 6.590 / 0,477 / EVET | 6.106 / 0,466 / EVET | 6.090 / 0,484 / EVET |
| 4 | 2.670 / 0,476 / EVET | 3.120 / 0,487 / HAYIR (p=0,168) | 2.989 / 0,472 / EVET | 2.801 / 0,494 / HAYIR (p=0,521) |
| 5 | 1.308 / 0,462 / EVET | 1.485 / 0,459 / EVET | 1.592 / 0,462 / EVET | 1.201 / 0,459 / EVET |

BAGLAM: M1'de 16 streak-testinden 14'u anlamli (p<0,05) cikmistir; anlamsiz cikan 2 test de
(VOL-dar streak-4, TREND-range streak-4) nokta tahmini yine 0,50'nin altinda kalmaktadir
(sirasiyla 0,487 ve 0,494) — yon degismemis, sadece bu n buyuklugunde (n=3.120, n=2.801) sapma
istatistiksel esigi gecmemistir. Hem VOL hem TREND etiketinde, hem "genis/trend" hem
"dar/range" tarafinda benzer buyuklukte (~0,46-0,49) ve ayni yonde (0,50'nin altinda) bir sapma
gozlenmektedir — iki rejim kategorisi arasinda BULGU'yu ayiran belirgin bir asimetri (bir
tarafta guclu sinyal, digerinde yok) bu TF/etiket kombinasyonunda gorulmemektedir.

SINIR: Tum degerler tam veri setinden (2026-03-30 -> 2026-07-10, M1) tek bir olcumdur;
walk-forward/OOS ayrimi bu asamada yapilmamistir (bu, Backtest Muhendisi asamasinin isidir).

### BULGU 11 — M5: BULGU 3'un (Ardisik Bar Devami) Rejim-Segmentli Tekrari
Veri Kaynagi: research_scalping_rejim.py, continuation_by_regime(), M5, 99.999 bar.
---------------------------------------------------------------
GOZLEM (genel ardisik-ikili ayni-yon orani, rejim bazinda):
| Etiket | Kategori | n | Ayni-yon orani | binom p | anlamli mi (a=0,05) |
|---|---|---|---|---|---|
| VOL | genis | 49.858 | 0,494 | 0,00903 | EVET |
| VOL | dar | 49.604 | 0,492 | 0,00082 | EVET |
| TREND | trend | 49.194 | 0,493 | 0,00111 | EVET |
| TREND | range | 50.261 | 0,494 | 0,00706 | EVET |

GOZLEM (streak-sonrasi, sonraki-bar-ayni-yon orani; n / oran / anlamli mi):
| Streak | VOL-genis | VOL-dar | TREND-trend | TREND-range |
|---|---|---|---|---|
| 2 | 12.534 / 0,492 / HAYIR (p=0,085) | 12.854 / 0,481 / EVET | 12.293 / 0,486 / EVET | 13.092 / 0,488 / EVET |
| 3 | 6.234 / 0,487 / EVET | 6.125 / 0,480 / EVET | 6.160 / 0,486 / EVET | 6.198 / 0,481 / EVET |
| 4 | 3.077 / 0,467 / EVET | 2.901 / 0,463 / EVET | 3.164 / 0,459 / EVET | 2.814 / 0,472 / EVET |
| 5 | 1.458 / 0,503 / HAYIR (p=0,814) | 1.323 / 0,484 / HAYIR (p=0,248) | 1.585 / 0,498 / HAYIR (p=0,880) | 1.196 / 0,489 / HAYIR (p=0,470) |

BAGLAM: M5'te 16 streak-testinden 11'i anlamli cikmistir; anlamsiz cikan 5 testin 4'u
streak-5 kategorisidir (en kucuk n, 1.196-1.585 arasi) — bu kategoride nokta tahminleri 0,50'ye
en yakin/bazen ustunde degerlerdir (0,503, 0,498, 0,489, 0,484), yani M5'te en uzun streak
(5-ardisik) sonrasinda rejim ayrimi herhangi bir yonde net bir sinyal GOSTERMEMEKTEDIR. Genel
(pair-level) ve streak 2-4 duzeyinde M1'e benzer sekilde, hem VOL hem TREND etiketinin HER IKI
kategorisinde de benzer buyuklukte (~0,46-0,49) asagi yonlu sapma gozlenmektedir.

SINIR: M5 verisi daha uzun bir donemi kapsar (2025-02-10 -> 2026-07-10, ~17 ay) ve BULGU 6'daki
genel yukselis onyargisini (drift) icerir; bu onyargi rejim etiketlerinden BAGIMSIZLASTIRILMAMIS
olabilir (detrend uygulanmadi).

### BULGU 12 — M1: BULGU 4'un (Buyuk-Bar Sonrasi Yon) Rejim-Segmentli Tekrari
Veri Kaynagi: research_scalping_rejim.py, breakout_by_regime(), M1, esik: range > 1,5 x ortalama range (BULGU 4 ile ayni).
---------------------------------------------------------------
GOZLEM:
| Etiket | Kategori | Buyuk bar (rejimde) | Yonlu cift n | Ayni-yon orani | binom p | anlamli mi |
|---|---|---|---|---|---|---|
| VOL | genis | 11.260 | 11.238 | 0,475 | 1,48e-07 | EVET |
| VOL | dar | 4.427 | 4.420 | 0,463 | 7,39e-07 | EVET |
| TREND | trend | 8.713 | 8.696 | 0,470 | 1,39e-08 | EVET |
| TREND | range | 6.974 | 6.962 | 0,474 | 1,87e-05 | EVET |

BAGLAM: M1'de 4 alt-orneklemin TAMAMI istatistiksel olarak anlamlidir; ayni-yon orani tum
kategorilerde 0,463-0,475 araliginda (yani sonraki bar COGUNLUKLA TERS yonde kapanmaktadir,
BULGU 4'un ham/kosulsuz halinde de gorulen egilimle ayni yonde). Rejim ayrimi burada da
kategoriler arasi belirgin bir asimetri gostermemektedir — hem "genis/dar" hem "trend/range"
tarafinda benzer buyuklukte ters-yon egilimi mevcuttur. Alt-orneklem toplamlari (VOL: 11.260+
4.427=15.687, TREND: 8.713+6.974=15.687) BULGU 4'un orijinal M1 toplamina (15.734 buyuk bar)
yakindir (kucuk fark, ilk ~112-119 barin rejim-etiketsiz kalmasindan kaynaklanmaktadir) — bu,
rejim-segmentli olcumun orijinal BULGU 4 ile TUTARLI oldugunun bir capraz-dogrulamasidir.

SINIR: Buyuk-bar esigi (1,5x ortalama range) rejime gore YENIDEN HESAPLANMAMISTIR — mean_r tum
veri setinin (rejimden bagimsiz) ortalamasidir; bu, orijinal BULGU 4 ile dogrudan
karsilastirilabilirligi korumak icin bilincli bir tercihtir, ancak rejime OZGU bir buyuk-bar
esigi farkli sonuc verebilir (test edilmedi).

### BULGU 13 — M5: BULGU 4'un (Buyuk-Bar Sonrasi Yon) Rejim-Segmentli Tekrari
Veri Kaynagi: research_scalping_rejim.py, breakout_by_regime(), M5, esik: range > 1,5 x ortalama range (BULGU 4 ile ayni).
---------------------------------------------------------------
GOZLEM:
| Etiket | Kategori | Buyuk bar (rejimde) | Yonlu cift n | Ayni-yon orani | binom p | anlamli mi |
|---|---|---|---|---|---|---|
| VOL | genis | 11.982 | 11.974 | 0,487 | 0,00502 | EVET |
| VOL | dar | 4.503 | 4.499 | 0,485 | 0,03963 | EVET |
| TREND | trend | 9.177 | 9.171 | 0,490 | 0,05468 | HAYIR (sinirda) |
| TREND | range | 7.308 | 7.302 | 0,482 | 0,00225 | EVET |

BAGLAM: 4 alt-orneklemden 3'u anlamlidir; TREND-trend kategorisi alpha=0,05 esiginin HEMEN
UZERINDE kalmistir (p=0,0547) — nokta tahmini (0,490) yine de 0,50'nin altindadir, sadece bu
n buyuklugunde (9.171) sapma anlamlilik esigini net gecmemistir. Alt-orneklem toplamlari (VOL:
11.982+4.503=16.485, TREND: 9.177+7.308=16.485) BULGU 4'un orijinal M5 toplamina (16.520 buyuk
bar) yakindir (kucuk fark, ayni rejim-etiketsiz ilk-bar nedeniyle) — capraz-dogrulama tutarlidir.

SINIR: BULGU 12 ile ayni (esik rejime gore yeniden hesaplanmadi, mean_r tum-veri ortalamasidir).

### SENTEZ — Bolum 6'daki ON-KOSUL Sorusu icin Ozet Sayilar
Bu bolum yalniz sayisal ozet sunar; hangi senaryonun (Backtest Muhendisi'ne gecis / Hipotez 3'un
erken kapanisi) gerceklestigine karar vermek Stratejist'e aittir (bkz. Stratejist raporu Bolum 3).
---------------------------------------------------------------
GOZLEM:
- Toplam alt-orneklem/istatistiksel-test sayisi: 48 (M1: 4 genel-pair + 16 streak + 4 breakout =
  24; M5: ayni yapi = 24; iki TF toplam 48).
- 48 testten 40'i (%83,3) istatistiksel olarak anlamli (p<0,05) cikmistir; 8'i (%16,7) anlamsiz
  kalmistir. Anlamsiz kalan 8 testin dagilimi: 4'u streak-5 (en kucuk n, 1.196-1.585 arasi,
  hepsi M5), 2'si streak-4 (n 2.801-3.120, ikisi de M1), 1'i streak-2 (M5 VOL-genis, n=12.534,
  p=0,085 - sinirda) ve 1'i breakout alt-orneklemi (M5 TREND-trend, n=9.171, p=0,0547 - sinirda).
- Anlamli cikan 40 testin TAMAMINDA ayni-yon/devam orani 0,50'NIN ALTINDADIR (araligi
  0,459-0,494). Anlamsiz kalan 8 testin nokta tahminlerinin 7'si de yine 0,50'nin altindadir
  (0,463-0,498 araliginda); tek istisna M5 VOL-genis streak-5'tir (oran=0,503, p=0,814 - burada
  yon de belirsizdir).
- Rejim kategorileri arasinda (VOL: genis vs dar; TREND: trend vs range) sapmanin buyuklugu VE
  yonu tutarlidir — hicbir TF/olcum kombinasyonunda "bir rejimde guclu/anlamli sapma, digerinde
  hicbir sapma yok" seklinde belirgin bir AYRISMA gozlenmemistir; anlamli olan 40 testin hepsi
  ayni yonde (0,50'nin altinda) ve benzer buyuklukte (~0,46-0,49) sapma gostermektedir.

BAGLAM: Bu sayilar, BULGU 3/4'un ham/kosulsuz halinde gorulen zayif-ama-tutarli asagi-yonlu
sapmanin (bkz. orijinal BULGU 3/4, ~%47-49), rejim (trend/range veya volatilite-genisligi)
ayrimindan BAGIMSIZ olarak HER IKI alt-rejimde de benzer sekilde var oldugunu gostermektedir.
Alt-orneklem buyuklukleri (BULGU 9) rejim ayrimiyla beklendigi gibi kuculmustur (orijinal
onbinlerce bar -> alt-orneklemler 1.196'dan 54.323'e kadar degisen bir aralikta), ancak genel
ve streak-2/3/4 seviyesindeki cogu test bu kucuk n'de bile anlamliligini korumustur; yalniz
streak-5 (en uzun/en seyrek streak) ve bir breakout alt-orneklemi anlamliligini kaybetmistir.

SINIR: Bu sentez yalniz istatistiksel anlamlilik (p<0,05) uzerinden sayilmistir; etki
buyuklugu/pratik onem (orn. bir strateji icin 0,49 ile 0,50 arasindaki farkin islem
maliyeti/spread karsisinda anlamli olup olmadigi) bu raporun kapsami disindadir — bu,
Backtest Muhendisi asamasinin (PF/WR/DD olcumu) konusudur. Ayrica bu sentez, farkli
esik/pencere secimleriyle (orn. TRAIL_WINDOW=100 yerine 50/200, ATR_PERIOD/ER_WINDOW farkli
degerler) tekrarlanmamistir - tek bir parametre setiyle uretilmis tek bir olcumdur.

---

## IZOLASYON NOTU (EK BOLUM icin, 12 Temmuz 2026)

- Bu ek-bolum calismasinda da MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md,
  positions_status.json vb.) ACILMADI veya referans ALINMADI.
- Yeni bir veri kaynagi ARANMADI - yalniz mevcut GOLD M1/M5 serisi (dogrudan MetaTrader5
  kutuphanesi) uzerinde, mevcut research_scalping.py'nin BULGU 3/4 olcumleri rejim-segmentli
  olarak tekrarlandi (research_scalping_rejim.py).
- Calisma yalniz C:\MilaYatirim\Justin\ dizininde yapildi (girdi: stratejici_raporu_justin_
  gold_scalping_20260712.md Bolum 6; cikti: research_scalping_rejim.py,
  research_scalping_rejim_output.json, bu ek bolum).

## STRATEJIST'E NOT (bu ek bolum icin)

Bu ek bolumdeki hicbir bulgu "Hipotez 3 Backtest Muhendisi'ne gecsin/gecmesin" demez - bu,
Stratejist'in Bolum 3'te onceden tanimladigi kapiya (en az bir rejimde anlamli sapma var mi)
gore kendisinin verecegi bir karardir. Rapor edilen ham sayilar (BULGU 9-13 + SENTEZ):
48 alt-orneklem testinden 40'i (VOL VE TREND etiketlerinin HER IKI kategorisinde de) 0,50'den
anlamli sekilde asagi yonde sapma gostermektedir; hicbir kombinasyonda "yalniz bir rejimde
anlamli, digerinde hic yok" seklinde bir ayrisma gozlenmemistir. Bu ozel gozlem (asimetri
yoklugu) ozellikle Bolum 3'teki degerlendirme icin ham girdi olarak sunulur; yorumu/karari
Stratejist'e aittir.
