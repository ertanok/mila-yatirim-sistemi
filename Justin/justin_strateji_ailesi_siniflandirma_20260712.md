# JUSTIN / GOLD SCALPING — STRATEJI AILESI SINIFLANDIRMASI VE DENEME-DURUM TABLOSU

Tarih: 12 Temmuz 2026
Olusturan: Orkestrator (bu gorev icin Fable 5'e yukseltilmis — Ertan'in acik talimati)
Gorev kaynagi: Ertan bildirimi, 12 Temmuz 2026 — "sistemli/kapsayici siniflandirma + durum
tablosu; hicbir agent tetiklenmesin, hicbir karar/tavsiye verilmesin"
Statu: DURUM-TESPIT DOSYASI — **bu dosya hicbir karar veya tavsiye icermez.** "Hangi aile
denenmeli" sorusunun cevabi bu dosyada YOKTUR ve bilerek yoktur; sonraki adim karari
Ertan'a/Stratejist'e aittir.

Izolasyon notu: Bu dosya hazirlanirken yalniz C:\MilaYatirim\Justin\ ici dosyalar (salt-okunur)
ve harici/akademik web kaynaklari kullanilmistir. Baska hicbir proje dosyasi acilmamis/referans
alinmamistir. Siniflandirmanin kendisi genel/akademik niteliktedir.

---

## 0) YONTEM

1. Trading strateji ailelerinin siniflandirmasi, birbirinden bagimsiz uc kaynak turunden
   capraz-dogrulanarak derlendi: (a) kitap/teorik cerceveler (Narang, Chan), (b) kurumsal/
   endustri siniflandirmalari (HFR hedge-fon strateji siniflandirma sistemi), (c) pratik strateji
   ansiklopedileri ve akademik makaleler (Quantpedia, QuantInsti, arXiv, Fed/ECB calisma
   raporlari). Tam kaynak listesi Bolum 4'te.
2. Justin/Gold-Scalping'in su ana kadarki denemeleri (H1-H3 kural-tabanli aile, ML Tam Tur 1
   Hipotez 1-3, ML Tam Tur 2) Justin klasorundeki birincil raporlardan dogrulandi (Arastirmaci/
   Stratejist/Backtest Muhendisi/Risk Analisti raporlari + governance kaydi).
3. Her deneme, siniflandirmadaki aile(ler)e gerekcesiyle yerlestirildi; her aile icin denenme
   durumu isaretlendi.

**Onemli cerceve karari (gorev tanimindan):** Siniflandirma **sinyal-mantigi/piyasa-tipi
bazindadir, yontemden BAGIMSIZDIR.** Yani "ML" bir strateji ailesi DEGILDIR — ML, herhangi bir
ailenin sinyalini uretmek icin kullanilabilen bir YONTEMdir. Bu ayrim Narang'in "theory-driven
vs data-driven" ayrimiyla uyumludur ve Bolum 1.2'de ayrica islenmistir.

---

## 1) SINIFLANDIRMA CERCEVESI

### 1.1 Uc ortogonal eksen

Literaturde stratejiler cogunlukla uc bagimsiz eksende tarif edilir; bu dosyanin ana ekseni
birincisidir:

- **Eksen 1 — Sinyal mantigi / edge kaynagi (ANA EKSEN, Bolum 2):** Kar beklentisi hangi piyasa
  davranisindan/anomalisinden geliyor? (trend devami, asiri-hareket donusu, kirilim, takvim
  etkisi, emir-akisi dengesizligi, vb.)
- **Eksen 2 — Yontem (ortogonal):** Sinyal nasil uretiliyor? Kural-tabanli / istatistiksel model /
  klasik ML (agac-tabanli vb.) / derin ogrenme / pekistirmeli ogrenme (RL) / hibrit. AYNI sinyal
  mantigi bu yontemlerin herhangi biriyle uygulanabilir.
- **Eksen 3 — Zaman ufku (ortogonal):** Tick/mikrosaniye (HFT) → M1-M15 (scalping/intraday) →
  saatlik-gunluk (swing) → haftalik-aylik (pozisyon). Ayni aile farkli ufuklarda cok farkli
  davranir (orn. donus kisa ufukta, momentum orta-uzun ufukta daha guclu belgelenmistir —
  QuantInsti/Ghosh).

### 1.2 "ML bir aile degildir" notu

Narang'in cercevesinde teorik-gudumlu alfa modelleri alti fenomen sinifina oturur (trend,
donus, teknik-sentiment, deger/getiri, buyume, kalite); veri-gudumlu (ML) modeller ise bu
siniflardan herhangi birinin sinyalini OGRENEBILIR veya siniflandirmaya onceden oturmayan
oruntuler arayabilir. Bu nedenle asagidaki durum tablosunda ML denemeleri, "ML ailesi" olarak
degil, **feature setlerinin dokundugu sinyal-mantigi ailelerine** gore yerlestirilmistir
(Bolum 3'te gerekceli).

---

## 2) STRATEJI AILELERI KATALOGU (sinyal-mantigi bazinda, 14 aile)

Her aile icin: tanim / tipik sinyal mantigi / piyasa kosulu varsayimi. "Uygulanabilirlik notu"
satirlari yalnizca nesnel kisit tespitidir (tek enstruman: GOLD spot CFD, XM/MT5, retail
erisim), tavsiye degildir.

### A) Trend-Takibi / Momentum (devam ailesi)
- **Tanim:** Fiyat hareketinin basladigi yonde devam edecegi beklentisiyle, hareket YONUNDE
  pozisyon alma. Iki ana alt-tur: (A1) zaman-serisi momentum (enstrumanin kendi gecmisine gore,
  orn. MA kesisimi, N-periyot getiri isareti), (A2) kesitsel momentum (bir evrendeki gorece
  kazananlari al / kaybedenleri sat — coklu enstruman gerektirir).
- **Tipik sinyal mantigi:** MA/EMA kesisimleri, kanal yonu, N-bar getiri isareti, 52-hafta/N-gun
  yuksegine yakinlik (George & Hwang tipi "yakin-zirve momentum"), ADX+DI yonu.
- **Piyasa kosulu varsayimi:** Fiyatta pozitif otokorelasyon / surdurulen trend fazlari; davranissal
  olarak yetersiz-tepki (underreaction) ve suru davranisi. Trendsiz/testere piyasada zarar uretir.
- Uygulanabilirlik notu: A1 tek enstrumanla uygulanabilir; A2 (kesitsel) tek-enstruman kapsaminda
  uygulanamaz.

### B) Ortalamaya-Donus / Kisa-Vade Donus (reversal/fade ailesi)
- **Tanim:** Fiyatin bir referans "adil deger/ortalama"dan asiri sapmasinin geri kapanacagi
  beklentisiyle, hareketin TERSINE pozisyon alma.
- **Tipik sinyal mantigi:** Bollinger/SMA+k*std sapmasi, RSI asiri-alim/satim, z-skor, buyuk-bar/
  ani-hareket sonrasi fade, kisa-ufuk donus (short-term reversal) etkisi.
- **Piyasa kosulu varsayimi:** Negatif kisa-vade otokorelasyon; asiri-tepki (overreaction) ve
  likidite saglayicilarin fiyati geri cekmesi. Guclu trend/kirilim rejiminde zarar uretir. Literatur
  bu ailenin kisa ufuklarda (gun-ici/birkac gun) gorece daha belirgin oldugunu not eder.

### C) Breakout / Volatilite-Genislemesi (kirilim ailesi)
- **Tanim:** Fiyatin belirlenmis bir aralik/seviyeden (destek-direnc, N-gun yuksek/dusuk, acilis
  araligi) cikisinin YENI bir yonlu hareketin baslangici oldugu beklentisi. Momentumla akraba ama
  sinyal tetigi farklidir: devam eden hareket degil, SIKISMADAN CIKIS ani.
- **Tipik sinyal mantigi:** Donchian kanali (Turtle), opening-range-breakout (ORB), volatilite
  sikismasi (squeeze) sonrasi genisleme, onceki gun/hafta yuksek-dusuk kirilimi, pivot seviye
  kirilimi.
- **Piyasa kosulu varsayimi:** Sikisma-genisleme dongusu (volatilite kumelenmesi) + kirilim sonrasi
  takip-alimi. Yanlis-kirilim (false breakout) orani yuksek piyasada zarar uretir. (Not: ayni
  seviye-verisi ters mantikla da kullanilabilir — "yanlis-kirilim fade'i" B ailesine duser; aileyi
  belirleyen VERI degil SINYAL MANTIGIdir.)

### D) Volatilite Stratejileri (volatilitenin kendisi uzerine)
- **Tanim:** Yon degil, VOLATILITE seviyesi/degisimi uzerine pozisyon: volatilite risk-primi satisi,
  vol-hedefleme (vol-targeting), varyans/gamma stratejileri.
- **Tipik sinyal mantigi:** Ima-edilen-vs-gerceklesen volatilite farki (opsiyon gerektirir),
  gerceklesen volatilite tahmini + pozisyon boyutu ayari, VIX-tipi endeks sinyalleri.
- **Piyasa kosulu varsayimi:** Volatilite kumelenmesi ve ortalamaya-donen volatilite; vol-primi
  icin "sigorta satana prim oder" yapisi.
- Uygulanabilirlik notu: Saf vol-primi/varyans stratejileri opsiyon/varyans-swap gerektirir (mevcut
  spot CFD kapsaminda yok). Vol-hedefleme ise herhangi bir yon stratejisinin USTUNE gelen bir
  boyutlandirma katmanidir (basina alfa ailesi olmaktan cok risk-modeli bileseni).

### E) Arbitraj / Istatistiksel Arbitraj / Goreli-Deger
- **Tanim:** Iki+ enstruman arasindaki fiyat ILISKISINDEKI sapmanin kapanmasi uzerine,
  piyasa-notr/cift-bacakli pozisyon (HFR "Relative Value" ana sinifi).
- **Tipik sinyal mantigi:** Pairs-trading/kointegrasyon (spread z-skoru), ucgen arbitraj,
  spot-vadeli baz arbitraji, ETF-NAV arbitraji.
- **Piyasa kosulu varsayimi:** Iliskinin (spread'in) duragan/ortalamaya-donen olmasi; hiz ve dusuk
  maliyet kritik.
- Uygulanabilirlik notu: Tanimi geregi coklu-enstruman/coklu-mekan gerektirir; tek-enstruman GOLD
  kapsaminda dogrudan uygulanamaz (XAUUSD-XAGUSD, XAUUSD-DXY gibi capraz ciftler ayri bir kapsam
  genisletmesi olur).

### F) Market-Making / Likidite Saglama
- **Tanim:** Cift-yonlu kotasyonla bid-ask spread'ini toplama; envanter riskini yonetme (HFT
  literaturunde en yaygin sinif — Ait-Sahalia & Saglam, O'Hara).
- **Tipik sinyal mantigi:** Spread geniskligi, emir-defteri derinligi, envanter-dengeleme,
  ters-secim (adverse selection) tahmini.
- **Piyasa kosulu varsayimi:** Akisin cogunun bilgisiz (uninformed) olmasi; dusuk gecikme ve
  maker-ucret yapisi.
- Uygulanabilirlik notu: Retail CFD hesabinda (fiyat-alici, spread-odeyen taraf) yapisal olarak
  uygulanamaz — bu ailede "denenmemis" durumu bir tercih degil, erisim kisitidir.

### G) Mikro-Yapi / Emir-Akisi (order-flow)
- **Tanim:** Emir-defteri/islem-akisi verisinden (imbalance, agresor taraf, kotasyon dinamigi)
  cok-kisa-vadeli yon/hareket tahmini. Market-making'den farki: spread toplamak degil, akistan
  YON sinyali cikarmak.
- **Tipik sinyal mantigi:** Bid-ask imbalance, order-flow-imbalance (OFI), tick-kurali ile
  agresor-taraf proxy'si, hacim-profil/likidite-bosluklari.
- **Piyasa kosulu varsayimi:** Emir akisinin ozel bilgi tasidigi (Hasbrouck cizgisi); sinyalin
  omru cok kisa, maliyet/gecikme belirleyici.
- Uygulanabilirlik notu: Gercek emir-defteri (L2) verisi mevcut kapsamda yok; tick-kural-tabanli
  proxy'ler mumkun (nitekim denendi — Bolum 3, Tur 2 Grup D).

### H) Olay-Tabanli / Haber-Takvim (event-driven, bilinen-zamanli)
- **Tanim:** Zamani onceden bilinen olaylarin (FED/FOMC, CPI, NFP) oncesi/sonrasi sistematik fiyat
  davranisi uzerine pozisyon — veya bu pencerelerde pozisyondan kacinma. (HFR "Event Driven" ana
  sinifinin, makro-takvim tarafina duyarli hali.)
- **Tipik sinyal mantigi:** Duyuru-oncesi drift (orn. pre-FOMC drift — Lucca & Moench), duyuru-ani
  volatilite patlamasi stratejileri, duyuru-sonrasi trend (post-announcement drift), surpriz-endeksi
  (beklenti-vs-gerceklesen) tepkisi.
- **Piyasa kosulu varsayimi:** Olay penceresinde sistematik risk-primi/bilgi-sizintisi/yetersiz-tepki;
  takvim disi zamanlarda sinyal yok.

### I) Sentiment / Konumlanma
- **Tanim:** Piyasa katilimcilarinin ruh hali/konumlanmasindan (haber tonu, sosyal medya, COT
  raporlari, opsiyon put-call orani, teknik-sentiment gostergeleri) yon sinyali.
- **Tipik sinyal mantigi:** NLP-tabanli haber/metin skoru (FinBERT tipi), asiri-konumlanma
  kontrarian sinyali (COT uc degerleri), Narang'in "teknik sentiment" sinifi (fiyat-disi islem
  verisinden cikarilan iyimserlik/karamsarlik).
- **Piyasa kosulu varsayimi:** Sentiment'in fiyata gecikmeyle yansimasi (momentum tarafi) veya
  asiri-sentiment'in donus habercisi olmasi (kontrarian taraf).

### J) Mevsimsellik / Takvim Anomalileri
- **Tanim:** Takvime bagli sistematik getiri oruntuleri: gun-ici saat/oturum etkileri, haftanin-gunu,
  ay-donumu, ay-ici, yil-ici mevsimsellik. Altin ozelinde belgelenmis ornekler mevcuttur
  (haftanin-gunu etkisi, ay bazli mevsimsellik — bkz. kaynaklar).
- **Tipik sinyal mantigi:** "X gununde/saatinde al-sat" tipi kosulsuz-takvim kurali; veya takvim
  degiskeninin baska bir sinyale filtre/feature olarak eklenmesi.
- **Piyasa kosulu varsayimi:** Kurumsal akis/rutin (rebalans, fixing, oturum acilislari) kaynakli
  tekrarlayan davranis; literatur bu anomalilerin zamanla zayiflayabildigini/kaybolabildigini not
  eder.

### K) Carry / Vade-Yapisi / Tasima-Maliyeti
- **Tanim:** Fiyat hareketi degil, POZISYON TASIMANIN getirisinden (faiz farki, roll-getirisi,
  vade-yapisi egimi) kazanc; vade-yapisinin sekli (contango/backwardation) sinyaldir.
- **Tipik sinyal mantigi:** FX carry (faiz farki), emtia vadeli baz/roll sinyali, vade-yapisi
  egimine gore uzun/kisa secimi.
- **Piyasa kosulu varsayimi:** Carry'nin krizde ters donme (crash) riskine karsi prim odedigi yapi.
  Altin tipik olarak yapisal contango'dadir (dusuk convenience yield).
- Uygulanabilirlik notu: Spot CFD'de carry, swap/gecelik-faiz olarak MALIYET tarafinda gorunur;
  vade-yapisi sinyali icin vadeli-kontrat verisi gerekir (mevcut kapsamda dogrulanmis kaynak yok —
  Tur 2'de USDX futures verisi bile "supheli/dogrulanmamis" cikmisti).

### L) Capraz-Varlik / Intermarket Lead-Lag
- **Tanim:** Baska bir piyasanin (DXY, reel faiz, hisse endeksleri, gumus) hareketinin hedef
  enstrumani ONCULEMESI (lead-lag) uzerine yon sinyali. Arbitrajdan farki: cift-bacakli notr
  pozisyon degil, tek-bacakli yon tahmini.
- **Tipik sinyal mantigi:** Onculeyen serinin gecikmeli getirisi → hedefin gelecek getirisi;
  korelasyon-rejimi degisimleri; makro-faktor gecisleri.
- **Piyasa kosulu varsayimi:** Bilginin piyasalar arasi GECIKMELI yayilmasi. Kritik ayrim:
  es-zamanli korelasyon (yaygin/guclu) ile ongorucu lead-lag (nadir/zayif) ayni sey degildir —
  Tur 2 olcumu bunu somut gosterdi (Bolum 3).

### M) Temel/Makro-Deger (fundamental)
- **Tanim:** Enstrumanin "adil degerine" iliskin fiyat-disi veriden (altin icin: reel faizler,
  enflasyon beklentisi, merkez bankasi alimlari, ETF akislari; hisse icin: bilanco/karlilik) orta-uzun
  vadeli yon. Narang'in value/yield-growth-quality siniflari ve HFR "Macro" ana sinifi buraya duser.
- **Tipik sinyal mantigi:** Deger-sapmasi (fiyat vs model-deger), makro-faktor regresyonlari,
  akis-verisi sinyalleri.
- **Piyasa kosulu varsayimi:** Fiyatin uzun vadede temel degere yakinsamasi; kisa ufukta gurultu
  baskin.
- Uygulanabilirlik notu: Mevcut veri kapsami (yalniz XM/MT5 fiyat verisi) fiyat-disi temel/makro
  veri icermez; bu ailenin denenmesi kapsam/veri-kaynagi genisletmesi gerektirir (tespit, tavsiye
  degil).

### N) Rejim-Degisimi / Adaptif (meta-aile)
- **Tanim:** Kendi basina yon sinyali uretmekten cok, piyasayi rejimlere (trend/range,
  dusuk/yuksek-vol, boga/ayi) ayirip HANGI ailenin ne zaman calistirilacagini secen ust-katman;
  veya parametrelerin rejime gore adaptasyonu.
- **Tipik sinyal mantigi:** HMM/Markov-rejim-degisim modelleri, ADX/vol-esikli rejim etiketleri,
  kumeleme; rejim → strateji/parametre eslemesi.
- **Piyasa kosulu varsayimi:** Rejimlerin (a) tespit edilebilir ve (b) yeterince kalici olmasi;
  rejim-ici davranis farkinin islem edilebilir buyuklukte olmasi.
- Not: Bu aile tipik olarak baska bir aileyle BIRLESIK calisir ("rejim X ise aile-A, degilse
  aile-B") — tek basina "rejim etiketi" alfa uretmeyebilir (Tur 2 olcumu: ADX rejimi buyukluk
  bilgisi tasidi, yon bilgisi tasimadi — Bolum 3).

### Kapsam-disi not: Execution algoritmalari (VWAP/TWAP, iceberg vb.)
Bazi kaynaklar bunlari "strateji" listelerine dahil eder; ancak bunlar alfa uretmez, buyuk
emirlerin piyasa-etkisini azaltir. Alfa-ailesi siniflandirmasina DAHIL EDILMEMISTIR (Narang'da da
ayri "Execution Model" katmanidir).

---

## 3) JUSTIN/GOLD-SCALPING DENEMELERININ YERLESTIRILMESI

Asagidaki durumlar Justin klasorundeki birincil raporlardan dogrulanmistir (12 Temmuz 2026
itibariyle mevcut dosyalar).

### 3.1 Kural-tabanli aile (Yol1, M1) — Madde-7 ile KAPATILDI

| Deneme | Ozet | Aile yerlesimi | Gerekce | Sonuc |
|---|---|---|---|---|
| **H1** | Seans-filtreli asimetrik ortalamaya-donus (SMA20 +/- k*std, M1) | **B (Ortalamaya-Donus)** — birincil; **J (Mevsimsellik)** — ikincil (seans filtresi) | Sinyal mantigi: ortalamadan sapmanin donusu. Seans filtresi takvim-degiskenini FILTRE olarak kullanir, sinyal kaynagi degildir | RED (Risk Analisti, 10 Temmuz) |
| **H2** | Buyuk-bar ters-yon/fade (range-esikli) | **B (Ortalamaya-Donus)** — kisa-vade donus/fade alt-turu | Ani buyuk harekete ters pozisyon = klasik overreaction-fade | RED (11 Temmuz) |
| **H3** | Rejimden-bagimsiz uniform zayif devam/donus; VOL/TREND rejim etiketi ikincil filtre | **B (Ortalamaya-Donus)** — birincil (fade bileseni baskin); **N (Rejim)** — ikincil/kismi (24-hucre rejim ayrimi denendi, hicbir segmentte edge cikmadi) | Rejim etiketi ust-katman SECICI olarak degil, ikincil filtre olarak kullanildi; rejim-anahtarlamali gercek bir adaptif strateji kurulmadi | RED, Madde-7 tetiklendi (11-14 Temmuz) |

Ortak patern (governance kaydindan): aggregate/on-kontrolde "anlamli" gorunen sinyal, tam testte
(walk-forward/OOS/gercekci maliyet) tutarli PF<1. Ek yapisal bulgu: M1'de maliyet/ATR orani
~%15-19 (SL'in ~%28-34'u).

### 3.2 ML/feature-tabanli aile (M15, N=16 bar / k*ATR14 triple-barrier)

ML denemeleri yontem olarak "klasik ML (gradient boosting)"tir; sinyal-mantigi acisindan
feature setlerinin dokundugu ailelere gore yerlestirilmistir (Bolum 1.2 geregi):

| Deneme | Ozet | Dokundugu aileler (feature duzeyinde) | Sonuc |
|---|---|---|---|
| **ML1** (Tur 1, Hipotez 1) | LightGBM ikili yon-tahmini, N=16/k=1,5; feature'lar: ATR/vol-rejim, coklu-TF confluence, momentum (RSI/MACD ham), HH/LL streak, oturum/saat, hacim | **A (Momentum)** — feature duzeyinde; **N (Rejim/vol)** — feature duzeyinde; **J (Mevsimsellik)** — oturum-feature duzeyinde | RED (12 Temmuz): AUC rassal (~0,50-0,52), ana feature'lar ~sifir agirlik, esik-kalibrasyonunda 0 islem |
| **ML2** (Tur 1, Hipotez 2) | XGBoost, ayni feature/etiket | Ayni | RED — ayni patern |
| **ML3** (Tur 1, Hipotez 3) | LightGBM k=2,0 varyanti, duzeltilmis esik-kalibrasyonu | Ayni | RED — ayni patern. Tur 1 toplu sonucu: "sorun model/barrier degil, feature seti/etiket tasarimi" |
| **ML Tur 2, Hipotez 1** | LightGBM ikili + YENI Grup B feature'lari (gunluk/haftalik pivot mesafesi, 20-gun rolling yuksek/dusuk yakinligi) | **A (Momentum)** — "yakin-zirve/gorece-konum" bilgisi (George-Hwang-tipi yakin-zirve momentum ile ayni bilgi turu); **C (Breakout)** — SADECE veri duzeyinde komsu (seviye-mesafesi olculdu; kirilim SINYAL MANTIGI kurulmadi) | RED (12 Temmuz, Risk Analisti tur2 raporu): test setinde 0 islem |
| **ML Tur 2, Hipotez 2** | LightGBM 3-sinifli deadzone etiketi (k=0,3xATR) + ayni feature'lar | Ayni (etiket degisikligi aile degistirmez) | RED (12 Temmuz): test setinde 15 islem (MIN_SAMPLE=30 alti), yalniz LONG |
| **ML Tur 2, Hipotez 3** | Tick-imbalance proxy (Grup D) + Hipotez-1 feature seti, SADECE son 90 gun, dusuk-oncelik pilot | **G (Mikro-yapi/Emir-akisi)** — proxy duzeyinde ILK temas | Backtest raporu mevcut (12 Temmuz); Risk Analisti'nin tur2 nihai degerlendirmesine DAHIL EDILMEDI (oncelik-3, "tek basina dayanak olamaz"); olceklenebilirlik COZULMEDI. Nihai aile-karari bu pilota dayandirilamaz |

### 3.3 Arastirma asamasinda OLCULUP hipotez asamasina GECIRILMEYEN aileler (Tur 2)

| Olcum | Aile | Sonuc (olcum, karar degil) |
|---|---|---|
| ADX(14) rejim etiketi (Grup A) | **N (Rejim)** | Rejim etiketi buyukluk/vol bilgisi tasiyor (%16,6 fark) ama yon-sureklilik ucunde de rassal (~%49) → Stratejist tarafindan bu tur icin ELENDI |
| DXY (USDX-SEP26) lead-lag (Grup C) | **L (Capraz-varlik)** | Es-zamanli korelasyon guclu (-0,41) ama ONGORUCU lead-lag pratikte sifir (-0,0008); veri kaynagi supheli → ELENDI. Bu bir OLCUM sonucudur; aile "backtest'te RED" statusunde DEGILDIR (hipotez kurulmadi) |

---

## 4) DURUM TABLOSU — AILE x DENENME DURUMU (12 Temmuz 2026 itibariyle)

Durum kodlari:
- **DENENDI-RED** = en az bir tam pipeline turu (Risk Analisti karari) ile test edildi, RED
- **KISMEN (ikincil/feature)** = birincil sinyal mantigi olarak HIC kurulmadi; yalniz filtre/feature
  olarak baska bir denemenin icinde yer aldi
- **OLCULDU-ELENDI** = Arastirmaci olcumu yapildi, hipotez asamasina gecirilmedi (backtest yok)
- **PILOT** = kisitli pencerede on-gozlem var, nihai karar yok
- **HIC DENENMEDI** = ne birincil ne ikincil olarak dokunulmadi

| # | Aile | Durum | Dayanak |
|---|---|---|---|
| A | Trend-Takibi / Momentum | **KISMEN (feature)** | Birincil trend-takibi hipotezi (MA-kesisim, kanal, N-bar devam kurali) HIC kurulmadi. Momentum bilgisi yalniz ML feature'i olarak girdi (RSI/MACD ham, HH/LL streak — Tur 1; 20-gun-yuksek yakinligi — Tur 2) ve modeller icinde ~sifir agirlik aldi / islem uretemedi |
| A2 | Kesitsel momentum (coklu-enstruman) | **HIC DENENMEDI** | Tek-enstruman kapsam; yapisal olarak denenemezdi |
| B | Ortalamaya-Donus / Donus | **DENENDI-RED (3 kez, aile kapatildi)** | H1, H2, H3 — uc bagimsiz varyant, uc RED, Madde-7 |
| C | Breakout / Volatilite-Genislemesi | **HIC DENENMEDI (birincil olarak)** | Kirilim sinyal mantigi (Donchian/ORB/seviye-kirilimi + kirilim YONUNDE giris) hicbir hipotezde kurulmadi. Tur 2'de seviye-MESAFESI feature olarak olculdu ama kirilim-tetigi degil |
| D | Volatilite stratejileri | **HIC DENENMEDI** | Vol yalniz feature/boyutlandirma girdisi olarak kullanildi; volatilitenin kendisi uzerine strateji (vol-primi vb.) yok. Saf turleri opsiyon verisi gerektirir (kapsamda yok) |
| E | Arbitraj / Stat-Arb / Goreli-Deger | **HIC DENENMEDI** | Coklu-enstruman gerektirir; tek-enstruman kapsamda yapisal olarak denenemezdi |
| F | Market-Making / Likidite | **HIC DENENMEDI** | Retail CFD erisiminde yapisal olarak uygulanamaz (erisim kisiti, tercih degil) |
| G | Mikro-Yapi / Emir-Akisi | **PILOT (nihai karar yok)** | Tur 2 Hipotez 3: tick-imbalance proxy, yalniz son 90 gun, dusuk-oncelik; L2/gercek order-flow verisi yok; olceklenebilirlik cozulmedi |
| H | Olay-Tabanli / Haber-Takvim | **HIC DENENMEDI** | Hicbir denemede olay/duyuru penceresi ne sinyal ne filtre olarak kullanildi |
| I | Sentiment / Konumlanma | **HIC DENENMEDI** | Haber/COT/konumlanma verisi hic kullanilmadi (mevcut veri kapsaminda da yok) |
| J | Mevsimsellik / Takvim | **KISMEN (filtre/feature)** | H1'de seans filtresi, ML'de oturum/saat feature'lari. Birincil takvim-anomali hipotezi (orn. haftanin-gunu, gun-ici saat-bazli kosulsuz oruntu) HIC kurulmadi |
| K | Carry / Vade-Yapisi | **HIC DENENMEDI** | Vade-yapisi/roll sinyali hic kullanilmadi; guvenilir vadeli-veri kaynagi da dogrulanmadi |
| L | Capraz-Varlik / Lead-Lag | **OLCULDU-ELENDI** | Tur 2 Grup C: DXY lead-lag ~0 olculdu, hipotez kurulmadi. Tek proxy (supheli USDX serisi) ile tek olcum — aile backtest duzeyinde test EDILMEDI |
| M | Temel / Makro-Deger | **HIC DENENMEDI** | Fiyat-disi veri (reel faiz, ETF akisi vb.) mevcut veri kapsaminda yok |
| N | Rejim-Degisimi / Adaptif | **KISMEN (ikincil) + OLCULDU-ELENDI** | H3'te rejim etiketi ikincil filtre (edge yok); Tur 2'de ADX rejimi olculdu (yon bilgisi rassal) ve elendi. Birincil rejim-anahtarlamali strateji (HMM tipi rejim tespiti + rejime gore strateji/parametre secimi) HIC kurulmadi |

### Ortogonal eksenlerde durum (bilgi amacli)

- **Yontem ekseni:** Kural-tabanli (H1-H3) ve klasik-ML/gradient-boosting (ML1-3, Tur 2) denendi.
  Derin ogrenme, RL, istatistiksel zaman-serisi modelleri (ARIMA/GARCH/HMM) DENENMEDI. (Bu bir
  durum tespitidir; yontem secimi bu dosyanin kapsami disindadir.)
- **Zaman-ufku ekseni:** M1 (H1-H3) ve M15-giris/4-saat-tutma (ML turlari) denendi. Tick/HFT ufku
  (90-gun pilot haric) ve saatlik-ustu/gunluk+ ufuklar DENENMEDI.

---

## 5) HIC DENENMEYEN AILELER — ACIK LISTE

Birincil sinyal mantigi olarak hicbir pipeline turunde test edilmemis aileler:

1. **A — Trend-Takibi / Momentum (birincil kural/model olarak)** — yalniz feature duzeyinde dokunuldu
2. **A2 — Kesitsel momentum** (yapisal kisit: tek enstruman)
3. **C — Breakout / Volatilite-Genislemesi**
4. **D — Volatilite stratejileri** (saf turleri icin veri kisiti)
5. **E — Arbitraj / Stat-Arb / Goreli-Deger** (yapisal kisit: tek enstruman)
6. **F — Market-Making** (yapisal kisit: retail CFD erisimi)
7. **H — Olay-Tabanli / Haber-Takvim**
8. **I — Sentiment / Konumlanma** (veri kisiti)
9. **J — Mevsimsellik / Takvim (birincil sinyal olarak)** — yalniz filtre/feature duzeyinde dokunuldu
10. **K — Carry / Vade-Yapisi** (veri kisiti)
11. **M — Temel / Makro-Deger** (veri kisiti)
12. **N — Rejim-Degisimi / Adaptif (birincil/ust-katman olarak)** — yalniz ikincil filtre duzeyinde dokunuldu

Kismi/ara statude olanlar (yukaridaki tabloda detayli): **G (Mikro-yapi — PILOT)**,
**L (Capraz-varlik — OLCULDU-ELENDI)**.

**Tekrar (gorev tanimi geregi):** Bu liste bir oneri siralamasi DEGILDIR. "Yapisal kisit" ve
"veri kisiti" notlari nesnel tespittir; hangi ailenin denenecegine/denenmeyecegine iliskin
hicbir karar veya tavsiye bu dosyada yer almaz.

---

## 6) KAYNAKLAR

Kitap/teorik cerceve:
- Rishi K. Narang, *Inside the Black Box: A Simple Guide to Quantitative and High-Frequency
  Trading* (Wiley, 2. baski) — teorik-alfa taksonomisi (trend, donus, teknik-sentiment,
  deger/getiri, buyume, kalite; theory-driven vs data-driven ayrimi)
- Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their Rationale* (Wiley, 2013) —
  mean-reversion vs momentum ana ayrimi
- George & Hwang (2004), "The 52-Week High and Momentum Investing" — yakin-zirve momentum
  (Tur 2 Grup B bulgusunun literatur karsiligi)

Kurumsal/endustri siniflandirmalari:
- HFR Hedge Fund Strategy Classification System — Equity Hedge / Event-Driven / Macro /
  Relative Value ana siniflari (hfr.com)
- CFA Level 2 mufredati, "An Overview and Categorization of Hedge Fund Strategies" (AnalystPrep
  ozeti)
- CME/JPM, "Momentum Strategies Across Asset Classes" (2015); CME, "An Introduction to Global
  Carry" — carry ailesinin varlik-siniflari-ustu tanimi

Pratik strateji ansiklopedileri/rehberleri:
- Quantpedia (quantpedia.com) — strateji screener kategorileri (momentum, reversal, seasonality,
  trendfollowing, volatility effect, sentiment, ML vb.)
- QuantInsti / Prodipta Ghosh, "Types of Trading Strategies" — momentum/mean-reversion ve ufuk
  iliskisi
- QuantStart, "Market Regime Detection using Hidden Markov Models" — rejim ailesi pratigi

Akademik makale/calisma raporlari:
- Lucca & Moench, "The Pre-FOMC Announcement Drift" (NY Fed Staff Report 512) — olay-tabanli aile
- ECB Working Paper 1901, "Price drift before U.S. macroeconomic news" — duyuru-oncesi drift
- Ait-Sahalia & Saglam, "High Frequency Market Making" — market-making ailesi
- O'Hara (2015), "High frequency market microstructure" (J. Financial Economics) — mikro-yapi ailesi
- Kohli (2012), "Day-of-the-week effect and January effect examined in gold and silver metals";
  ScienceDirect, "Seasonal patterns and calendar anomalies in the commodity market for natural
  resources" — altin takvim anomalileri
- MDPI, "Regime-Switching Factor Investing with Hidden Markov Models" — rejim/adaptif aile
- arXiv 2409.06289, "Automate Strategy Finding with LLM in Quant Investment" — sinyal-taksonomisi
  ornegi (momentum, mean-reversion, volatilite, likidite, teknik, makro vb. kategoriler)
- Academia.edu, "Testing a price breakout strategy using Donchian Channels" — breakout ailesi
  ampirik testi

Justin-ici birincil dosyalar (durum dogrulamasi icin okunanlar):
- justin_gecmis_calisma.md; justin_gold_scalping_karar_ve_governance_20260714.md
- stratejici_raporu_justin_gold_scalping_20260714.md (v5, H1-H3 ozet + Madde-7)
- stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md; ..._ml_v2_20260712.md
- arastirmaci_gold_scalping_ml_v2_raporu.md
- risk_analisti_raporu_justin_gold_scalping_ml_v2_tur2_20260712.md (Tur 2 H1/H2: RED)
- backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez3_20260712.md (pilot cerceveleme)
