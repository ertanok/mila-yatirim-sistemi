# STRATEJIST RAPORU — Justin / Gold Scalping Hipotezleri (RAFINE — v4)

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: Yol1 dongusu 4 — Hipotez 3 on-kosul (Bolum 6, v3) sonucunun degerlendirilmesi
Tarih: 13 Temmuz 2026
Girdi:
  - Kendi onceki raporum: stratejici_raporu_justin_gold_scalping_20260712.md (v3, Bolum 3 karar
    kurali ve Bolum 6 ek-veri talebi burada tanimli)
  - Arastirmaci raporu: C:\MilaYatirim\Justin\_ek_bolum_rejim.md (Hipotez 3 on-kosul, rejim-
    segmentli BULGU3/4 + anlamlilik testleri)
  - Referans (degismedi): arastirmaci_gold_scalping_raporu.md (Hipotez 3'un orijinal tanimi)
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)

---

## OTURUM OZETI

Arastirmaci, v3 raporunun Bolum 6'sinda istenen dar-kapsamli ek-veri gorevini tamamladi:
BULGU3 (ardisik-bar-yon-devami) ve BULGU4 (buyuk-bar-sonrasi-yon), VOL (ATR14/trailing-100-
medyan) ve TREND (ER20/trailing-100-medyan) rejim etiketlerine gore alt-orneklemlere bolunerek
yeniden hesaplandi, her alt-orneklem icin binom/ki-kare anlamlilik testi uygulandi. Ham sonuc:
BULGU3-genel 8/8 rejim-segmentinde anlamli, BULGU3-streak 32 hucreden 25'i anlamli (7'si degil,
4'u streak=5), BULGU4 8 segmentten 7'si anlamli (istisna: M5 TREND-trend, p=0,0547). Coklu-
karsilastirma duzeltmesi UYGULANMADI notu raporda acikca var.

Bu raporda v3 Bolum 3'teki karar kuralimi ("rejim bazinda en az bir alt-kumede anlamli sapma
bulunursa -> Backtest Muhendisi'ne gecis") bu sayilara uyguluyorum. **KARAR: EVET — Backtest
Muhendisi'ne Hipotez 3 gorevi verilir, ancak asagida Bolum 2'de gerekceli sekilde SIKILASTIRILMIS
kosullarla** (coklu-karsilastirma duzeltmesi eklenmesi, M1 odakli/M5 ikincil oncelik, gercekci-
maliyet erken kontrolu). Bolum 3'te literal kuralin neden yeterli olmadigini, kendi hesapladigim
kaba Bonferroni duzeltmesiyle birlikte aciklıyorum. Bolum 5'te Backtest Muhendisi icin somut
GOREV tanimi birakiyorum (Orkestrator'un tetiklemesi icin).

Izolasyon kontrolu: Bu oturumda da stratejici_gold_gecmis_calisma.md veya herhangi bir
MilaGold/Lisa/Signal GPT dosyasi ACILMADI/referans ALINMADI. Girdi olarak yalniz kendi onceki
raporum, Arastirmaci'nin ek-veri raporu ve Hipotez 3'un degismeyen orijinal tanimi kullanildi.

---

## 1) HAM SONUCUN OKUNMASI — LITERAL KURAL vs. HIPOTEZ 3'UN TEMEL VARSAYIMI

v3 Bolum 3'teki kural sadece "en az bir alt-kumede istatistiksel olarak anlamli sapma var mi"
sorusunu soruyor — bu soruya cevap acik ve ezici bicimde EVET (8/8, 25/32, 7/8). Literal kural
bu haliyle Backtest Muhendisi'ne gecisi gerektiriyor.

Ancak bu kararı vermeden once, Hipotez 3'un KENDI mantiginin (v3 Bolum 2, tasima notu 2) bu
veriyle gercekten dogrulanip dogrulanmadigini ayirt etmem gerekiyor:

**Hipotez 3'un temel varsayimi**, aggregate/kosulsuz BULGU3-4 sonucunun (%50'ye yakin, zayif)
"birbirini iptal eden iki alt-rejimin (trend'de bir yon, range'de baska bir yon/donus) karisimi"
olabilecegiydi — yani rejim ayristirildiginda bir rejimde GUCLU bir sapma, digerinde ZAYIF veya
TERS yonlu bir sapma beklenirdi (kanselasyon/maskeleme hipotezi).

**Bu veri, bu varsayimi DOGRULAMIYOR.** BULGU3-genel'de 8 rejim-segmentinin TAMAMI ayni yonde
(ayni-yon orani hepsinde %50'nin altinda) ve BENZER buyuklukte (0,483-0,494 — sadece 0,011
puanlik bir aralik) sapma gosteriyor. Trend'de bir yon, range'de baska bir yon/donus DEGIL — her
ikisinde de AYNI zayif reversal-egilimi var. BULGU4'te de ayni durum (0,463-0,490 araligi, tek
istisna disinda hepsi ayni yonde). Yani **kanselasyon/maskeleme bulunmadi** — rejim ayristirmasi,
onceden gizlenmis daha guclu bir sinyal ORTAYA CIKARMADI; sadece aggregate'te zaten bilinen zayif
sapmayi her alt-kumede TEKRAR dogruladi.

Bu, Hipotez 3'un "rejim-FARKINDA" cercevesini (rejime gore FARKLI davranan bir sinyal) zayiflatir
— bulunan sey rejimden BAGIMSIZ, uniform bir zayif reversal-egilimidir. Bu ayrim onemli cunku
literal kural teknik olarak karsilaniyor olsa da, gerekce (mantik) degisti: bir sonraki asamada
Backtest Muhendisi'nin test edecegi sey "trend'de X, range'de Y farkli kural" degil, "rejimden
bagimsiz uniform zayif sinyal, rejim etiketi sadece bir FILTRE/dogrulayici olarak kullanilabilir"
olmali (Bolum 5'te somutlastirildi).

---

## 2) COKLU-KARSILASTIRMA DUZELTMESI — KABA BONFERRONI ILE YENIDEN OKUMA

Arastirmaci raporun Bolum 7'sinde acikca not dustugu gibi, duzeltme uygulanmadi. Toplam test
sayisi: BULGU3-genel (8) + BULGU3-streak (32) + BULGU4 (8) = **48 test**. Kaba/muhafazakar
Bonferroni ile duzeltilmis alfa = 0,05/48 ≈ **0,00104**. Arastirmaci'nin raporladigi ham
p-degerlerine bu esigi uyguladigimda (yeni veri/hesaplama degil, mevcut sayilarin
yeniden-degerlendirilmesi):

- **BULGU3-genel (8 segment):** M1'in 4 segmenti de rahatlikla hayatta kaliyor (p'ler 1e-06'nin
  cok altinda). M5'in 4 segmentinden sadece VOL-dar (p=0,00082) sinirda hayatta kaliyor; VOL-genis
  (p=0,00903), TREND-trend (p=0,00111) ve TREND-range (p=0,00706) duzeltilmis esigin USTUNE
  cikiyor (anlamliligini kaybediyor). **Sonuc: 8/8 -> 5/8.**
- **BULGU3-streak (32 hucre):** Duzeltilmis esikte 32 hucreden yaklasik **9'u** hayatta kaliyor
  (M1 tarafinda 5, M5 tarafinda 4) — geri kalan ~23 hucre (onceden "anlamli" isaretlenmisken)
  duzeltmeyle anlamliligini kaybediyor. **Sonuc: 25/32 -> ~9/32.**
- **BULGU4 (8 segment):** M1'in 4 segmenti duzeltilmis esikte de rahatlikla hayatta kaliyor;
  M5'in 4 segmentinin TAMAMI (VOL-genis p=0,00502, VOL-dar p=0,0396, TREND-trend zaten ns,
  TREND-range p=0,00225) duzeltilmis esigin ustunde kaliyor. **Sonuc: 7/8 -> 4/8 (yalniz M1).**

**Gozlem (belirleyici):** Bu kaba yeniden-okuma net bir TF ayrimi ortaya cikariyor. **M1
sonuclari** duzeltmeye buyuk olcude dayanikli (buyuk n, cok kucuk p-degerleri) — bu, gurultu
degil gercek/tutarli bir yapiya isaret eder. **M5 sonuclari** duzeltmeye buyuk olcude dayanaksiz
— cogu M5 "anlamli" bulgusu, coklu-test + buyuk-n etkisinin bir sonucu olabilir, gercek bir
yapi olmayabilir. Bu, tam da Arastirmaci'nin Bolum 7'de isaret ettigi riskin somutlasmis hali
(coklu-test duzeltmesi olmadan alfa=0,05 kullanmanin, sans-eseri-anlamli sonuc riskini
artirmasi) ve karara doğrudan yansitilmasi gereken en onemli bulgu.

**Not:** Bu benim (Stratejist) yaptigim kaba/illustratif bir yeniden-hesaplama — Bonferroni en
muhafazakar duzeltme yontemidir (FDR/Benjamini-Hochberg daha az muhafazakar sonuc verirdi).
Kesin/resmi duzeltme hesaplamasi Backtest Muhendisi'nin kendi IS-donem analizinde YAPILMALI
(Bolum 5, on-kontrol 2) — buradaki sayilar sadece karar yonumu belirlemek icin kullanildi.

---

## 3) KARAR

**KARAR: EVET — Backtest Muhendisi'ne Hipotez 3 (Asama 1/2, kural-tabanli) gorevi verilir.**
Ancak asagidaki gerekceyle, v3'teki genel notlara ek olarak SIKILASTIRILMIS/odak-degistirilmis
kosullarla (Bolum 5'te somutlastirildi):

1. **Literal kural (v3 Bolum 3) acik ve ezici bicimde karsilaniyor** — 8/8, 25/32, 7/8 raw
   anlamli. Bu, "hicbir alt-kumede anlamli sapma bulunmadi" senaryosuna girmiyor; Hipotez 3'un de
   erken kapanmasi icin gerekce yok.
2. **Ancak Bolum 1'deki bulgu (kanselasyon/maskeleme YOK, uniform zayif sinyal VAR) ve Bolum
   2'deki kaba Bonferroni yeniden-okuma (M1 dayanikli, M5 buyuk olcude dayanaksiz), Backtest
   Muhendisi'ne verilecek gorevin KAPSAMINI degistiriyor** — "rejime gore FARKLI kural" degil
   "M1-agirlikli, rejimden bagimsiz uniform sinyal + rejim etiketi ikincil filtre" olarak
   çerçevelenmeli, M5 kesfi ikincil/exploratory kalmali.
3. **H1 ve H2'nin RED gerekcesi ile bu turun bulgusu ayni riski tasiyor: buyuk-n'de istatistiksel
   anlamlilik, kucuk/pratik-degeri-supheli etki buyuklugu (0,011-0,037 puanlik sapmalar) ile
   birlikte geliyor.** H1 ve H2'de bu tur sapmalar gercekci maliyet/seans filtresi altinda
   kayboldu. Bu riski Hipotez 3'te ERKEN (tam walk-forward'dan once) test etmek icin Bolum 5'te
   bir on-kontrol ekliyorum — H1/H2'nin Backtest Muhendisi/Risk Analisti asamasinda ogrendigimiz
   dersin, Hipotez 3'e bastan/erken uygulanmis hali.
4. **"3 ardisik hipotez, ayni patern" (madde-7, Risk Analisti'nin gozlemi) simdi TETIKLENMIYOR**
   — cunku Hipotez 3 henuz Backtest Muhendisi'nin tam testinden gecmedi, erken-kapanmadi. Ancak
   bunu ONCEDEN karara bagliyorum (Bolum 4): **eger Hipotez 3 de Backtest Muhendisi'nin tam
   testinde (walk-forward/OOS/gercek maliyet) H1 ve H2 ile ayni paternle (aggregate/on-kontrolde
   "anlamli" ama gercekci kosullarda PF<1/tutarli-negatif) RED olursa, bu artik acik ve otomatik
   bir madde-7 tetikleyicisidir** — bir sonraki Stratejist turu bunu yeniden tartismaya gerek
   kalmadan dogrudan Ertan'a sunacak sekilde.

---

## 4) MADDE-7 ON-KARARI (kosullu, ileriye donuk)

Eger Backtest Muhendisi'nin Bolum 5'teki gorev sonucunda Hipotez 3 de RED cikarsa (Asama 1/2
kural-tabanli versiyon PF>=1'i walk-forward/OOS'ta gosteremezse VEYA on-kontrol 3'teki gercekci-
maliyet/seans-filtresi kontrolunu gecemezse), bu durumda:

- **Otomatik sonuc: madde-7 tetiklenir.** 3 ardisik hipotez (mean-reversion, fade, rejim-
  segmentli devam/donus), 3 farkli mekanizma, HEPSI ayni patern (aggregate/on-kontrolde
  "istatistiksel olarak anlamli" ama gercek islem kosullarinda tutarli sekilde PF<1/negatif).
- **Bu senaryoda onerilen karar (bir sonraki Stratejist turunde resmilesecek):** Arastirmaci
  asamasina GENIS CAPLI donus (yeni bir temel yaklasim turu — orn. bu raporun basindaki
  "Yontem Cesitliligi" ilkesi geregi kural-tabanli disinda bir yontem: klasik ML/feature-tabanli
  bir yaklasim, veya farkli bir veri/timeframe kombinasyonu) GUNDEME GELMELI, VEYA bu alt-hedefte
  (Gold Scalping, kural-tabanli fiyat-aksiyonu ailesi) projenin durdurulup Justin'in kaynaklarinin
  farkli bir yaklasima yonlendirilmesi Ertan'a bir SECENEK olarak sunulmali. Bu iki secenek
  arasindaki tercih bu asamada onceden verilmiyor (Backtest Muhendisi'nin RED gerekcesinin
  detayina bagli olacak) ama "hicbir sey yapmadan devam etmek" secenegi bu senaryoda ACIKCA
  MASADA OLMAYACAK.
- Eger Hipotez 3 Backtest Muhendisi'nde POZITIF (PF>=1, walk-forward/OOS ve gercekci-maliyet
  kontrolunu gecerek) sonuclanirsa, madde-7 elbette gundeme gelmez; Risk Analisti asamasina
  normal akisla gecilir.

---

## 5) BACKTEST MUHENDISI ICIN GOREV TANIMI (Orkestrator'un tetikleyebilmesi icin)

**GOREV BASLIGI:** Hipotez 3 — Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali, Asama 1/2
(kural-tabanli), M1-agirlikli

**GIRDI DOSYALARI:**
- Bu rapor (stratejici_raporu_justin_gold_scalping_20260713.md)
- Arastirmaci ek-veri raporu (_ek_bolum_rejim.md) ve script/veri (research_scalping_rejim.py,
  research_scalping_rejim_output.json)
- Onceki Stratejist raporu v3 (Bolum 2, orijinal Backtest Muhendisi notlari — asagidakiler bunu
  GUNCELLER/SIKILASTIRIR, yerine gecmez)
- Orijinal Hipotez 3 tanimi (arastirmaci_gold_scalping_raporu.md)

**KAPSAM/CERCEVE (v3'ten degisen):** Hipotez, "trend'de bir kural, range'de baska bir kural"
seklinde REJIME-GORE-FARKLI degil; Bolum 1'de gosterildigi gibi rejimden BAGIMSIZ, uniform, zayif
(yon-devam/donus orani ~%48-49) bir sinyaldir. Rejim etiketleri (VOL: ATR14/trailing-100-medyan;
TREND: ER20/trailing-100-medyan — research_scalping_rejim.py tanimiyla AYNEN) birincil sinyal
degil, IKINCIL bir FILTRE/dogrulayici olarak test edilmeli (orn. "sinyal + belirli rejimde miyiz"
kombinasyonunun PF'yi iyilestirip iyilestirmedigi).

**TIMEFRAME ONCELIGI:** M1 BIRINCIL odak (Bolum 2'deki kaba Bonferroni yeniden-okumada M1
sonuclari buyuk olcude dayanikli cikti). M5 IKINCIL/exploratory kalmali — M5 bulgularinin
cogunun coklu-test duzeltmesiyle anlamliligini kaybettigi Bolum 2'de gosterildi; M5 uzerinde
kaynak/zaman israf edilmemeli, once M1 sonucu netlessin.

**ON-KONTROLLER (tam walk-forward/OOS baslamadan ONCE, sirayla):**

1. **Saat-esleme/DST bagimsiz dogrulama — 4. kez tekrar.** Atlanmamali (rejim etiketleme +
   olasi seans filtresi birlestiginde ayni kayma riski gecerli, H1/H2/H3-ongorusunde 3 kez
   dogrulandi ve hep ayni sonuc cikti, ama metodolojik olarak zorunlu).
2. **Coklu-karsilastirma duzeltmesi (Bonferroni veya FDR/Benjamini-Hochberg, tercihen FDR — daha
   az muhafazakar ama gecerli) kendi IS-donem verisinde RESMI olarak uygulanmali.** Bolum 2'deki
   kaba Bonferroni yeniden-okuma sadece bir on-isaret; Backtest Muhendisi kendi test setinde
   (IS/OOS ayriminda) bu duzeltmeyi resmi olarak yapip hangi rejim-segmentlerinin/streak-
   hucrelerinin gercekten hayatta kaldigini raporlamali.
3. **Gercekci-maliyet/seans-filtresi erken kontrolu (H1/H2'den tasinan kritik ders).** Tam
   walk-forward'a gecmeden once, on-kontrol 1-2'yi gecen segmentler icin, gercekci islem
   kosullari (spread, slipaj, ve Justin'in olasi seans/saat kisitlari) altinda ham devam/donus
   oraninin hala %50'den anlamli sapip sapmadigi kontrol edilmeli — H1 ve H2'de tam bu adimda
   ("aggregate'te anlamli, fiilen-islem-edilen altkumede anlamsiz") RED cikti; bu kontrolu ERKEN
   yapmak, tam walk-forward donemine gecmeden once ayni riski elemek/onaylamak icin.
4. **MAX_TICK_MISMATCH_SEC=60 standart olarak kullanilir** (v3 Bolum 4'te onaylandi, degismedi).

**ANA TEST (on-kontroller 1-3 gecilirse):** Kural-tabanli Asama 1/2 versiyonun (M1 birincil, M5
ikincil) walk-forward/OOS testi, PF/WR kirilma-noktasi karsilastirmasi, en az 6 pencere/18 ay
standardı (H1/H2'de kullanilan standart) korunarak.

**ASAMA SIRASI/ML KAPISI (degismedi, v3'ten tasindi):** Kural-tabanli Asama 1/2 kendi basina
(walk-forward/OOS'ta PF>=1, tercihen kirilma-noktasinin uzerinde) pozitif sonuc vermeden ML
Asama 3'e (LightGBM vb.) GECILMEYECEK.

**OVERFITTING GUVENLIK AGI (degismedi):** Rejim tanimindaki esik degerleri (ATR/ER trailing
pencere genisligi) genis araliklarda taranmayacak; her taramada walk-forward/OOS raporlanacak.

**ALT-ORNEKLEM KUCULMESI:** Arastirmaci'nin Bolum 5'te raporladigi n degerleri (rejim ayrimi
sonrasi ~yariya, streak=5'te 1.196-1.592 araligina kadar dusuyor) Backtest Muhendisi'nin IS/OOS
bolme kararinda baslangic noktasi olarak kullanilmali — kucuk alt-orneklemlerde OOS'un pratik
olarak anlamli kalabilmesi icin pencere sayisi/genisligi buna gore ayarlanmali.

**TAM ISLEM LOGU:** H1/H2 standardi korunur — Risk Analisti'nin bagimsiz tam dogrulama
yapabilmesi icin tam islem logu bastan saglanir.

**BEKLENEN CIKTI:** Backtest Muhendisi raporu, on-kontrol 1-3 sonuclarini ayrik olarak (gecti/
gecmedi) raporlamali — herhangi biri gecilemezse ana teste gecilmeden Hipotez 3 bu asamada
sonuclandirilir (RED, madde-7 Bolum 4'teki kosullu karar devreye girer).

---

## GUNCEL HIPOTEZ DURUMU OZETI

| Hipotez | Durum | Oncelik |
|---|---|---|
| 1 — Seans-Filtreli Ortalamaya-Donus | KAPANDI (RED) | — |
| 1b — N-bar-zaman-cikis varyanti | Ayri hipotez olarak elendi, mekanizma H2'ye tasindi | — |
| 2 — Buyuk-Bar Ters-Yon (Fade) | KAPANDI (RED) | — |
| 3 — Rejimden-Bagimsiz Uniform Zayif Devam/Donus (eski adi: Rejim-Farkinda Hibrit) | **AKTIF — Backtest Muhendisi'ne gecildi (on-kosul gecti, kosullu/sikilastirilmis kapsamla)** | 1-Yuksek |

Not: Hipotez 3'un adi bu turde bilerek "Rejimden-Bagimsiz Uniform Zayif Devam/Donus" olarak
guncellendi — Bolum 1'de gosterildigi gibi bulunan sey rejime-gore-degisen bir sinyal degil,
rejimden bagimsiz uniform bir sinyal. Isim degisikligi mekanizmayi daha dogru yansitmak icin,
karar/oncelik durumunu etkilemiyor.

---

## ARASTIRMACI ICIN NOTLAR

Bu turde Arastirmaci'ya yeni bir gorev verilmiyor — Bolum 6 (v3) talebi tamamlandi ve
degerlendirildi. Backtest Muhendisi calismasi sirasinda (Bolum 5, on-kontrol 2-3) ek bir soru
cikarsa (orn. resmi FDR duzeltmesi icin ham veri/n detaylarinin dogrulanmasi), bu ayri, dar
kapsamli bir tur olarak gundeme gelebilir.

## BACKTEST MUHENDISI ICIN NOTLAR

Bolum 5'teki GOREV TANIMI birebir gecerlidir. Ozetle: M1 birincil/M5 ikincil odak, 3 on-kontrol
(DST — 4. kez, coklu-karsilastirma duzeltmesi — resmi, gercekci-maliyet/seans-filtresi — erken),
sonra ana walk-forward/OOS testi, ML kapisi degismedi, MAX_TICK_MISMATCH_SEC=60 standart.

---

## IZOLASYON NOTU

- Bu oturumda da MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (stratejici_gold_gecmis_calisma.md,
  signal.json, milagold_trades.json, lisa_performance.json, positions_status.json vb.) ACILMADI
  veya referans ALINMADI.
- Calisma yalnizca C:\MilaYatirim\Justin\ dizininde yapildi (girdi: kendi onceki raporum
  (v3), Arastirmaci'nin _ek_bolum_rejim.md raporu, arastirmaci_gold_scalping_raporu.md; cikti:
  bu dosya).

---

## ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik karar
adimi, canli sisteme dokunus yok, Justin demo/arastirma asamasinda, henuz canli hesabi yok).
Bolum 5'teki Backtest Muhendisi gorev tanimi da ayni kategoride (READ-ONLY/offline analiz)
kalir. Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator
tarafindan dusulecektir.
