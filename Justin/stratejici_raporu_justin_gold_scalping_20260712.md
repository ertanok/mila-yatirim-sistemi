# STRATEJICI RAPORU — Justin / Gold Scalping (FAZ 1 GOREV-TANIMI TURU — v6)

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: Yol1 disi ozel tur — bu bir "yeni hipotez uret" veya "governance/karar-sunum"
turu DEGIL. **Faz 1 — Stratejist v6 turu**: onceki turde Ertan'in onayladigi genis-kapsamli
cerceveyi somut, calistirilabilir bir Arastirmaci gorev tanimina cevirme turu.
Tarih: 12 Temmuz 2026 (VPS-yerel)
Girdi:
  - Gorev tanimi: `gorev_stratejici_justin_gold_scalping_v6.md` (Orkestrator)
  - `justin_gold_scalping_karar_ve_governance_20260714.md` (Ertan'in resmi karari + S1/S2/S3)
  - `orkestrator_degerlendirme_madde7_gold_scalping_20260714.md` (Bolum 2 — maliyet duvari
    ayristirmasi, Bolum 5 — plan taslagi)
  - `justin_backtest_onkontrol_standardi.md`, `justin_ml_anti_overfitting_protokolu.md`,
    `justin_gecmis_calisma.md` (kalici standart/cerceve dosyalari)
  - Kendi onceki raporum: `stratejici_raporu_justin_gold_scalping_20260714.md` (v5, Bolum 2 —
    genis-kapsamli (a) onerisinin ilk taslagi, burada somutlastiriliyor)
Calisma dizini: yalniz `C:\MilaYatirim\Justin\` (okuma/yazma)

**Not (dosya-adi tekrari):** Bu dosya adi (…20260712.md) daha once Yol1 dongusundeki bir
Stratejist rafine turu (Hipotez 2 RED sonrasi, "v3") icin de kullanilmisti. Gorev tanimindaki
"Beklenen Cikti" acikca bu yolu belirttigi icin dosya bu FAZ 1/v6 icerigiyle GUNCELLENMISTIR;
eski v3 icerigi artik gecerli degildir, guncel/aktif Yol1 durumu bu raporun "GUNCEL HIPOTEZ/AILE
DURUMU OZETI" bolumundedir (Hipotez 1/2/3 uc dogal RED oldu, Madde-7 tetiklendi — bkz. v4/v5
raporlari, `stratejici_raporu_justin_gold_scalping_20260713.md` ve `..._20260714.md`).

Izolasyon kontrolu: Bu oturumda da `stratejici_gold_gecmis_calisma.md` veya herhangi bir
MilaGold/Lisa/Signal GPT dosyasi ACILMADI/referans ALINMADI. Girdi olarak yalniz yukaridaki
Justin-ici dosyalar kullanildi.

---

## OTURUM OZETI

Bu tur bir hipotez uretim turu DEGIL. Ertan onceki turde Stratejist v5 Bolum 3'teki (a) —
genis-kapsamli yontem-degisikligi secenegini, Orkestrator'un onerdigi UC SERTLESTIRME (S1, S2,
S3) ile birlikte onaylamis; Faz 0 (gecmis-calisma dosyasi, kalici on-kontrol standardi, S2
protokol metni, S3 governance kaydi) tamamlanmisti. Bu turdeki tek gorevim: Bolum 2 cercevesini
(ozellik-tabanli klasik ML + zorunlu zaman-ufku genislemesi) somut, tek ve calistirilabilir bir
**Arastirmaci gorev tanimina** cevirmek — YAKLASIM TURU/aday model, ZAMAN-DILIMI, VERI/FEATURE
ihtiyaci konularinda gerekceli karar vermek, S1/S2/S3'u aynen islemek, `justin_gecmis_calisma.md`
sabitlerini referans olarak eklemek ve izolasyon kisitini tekrarlamak.

Asagida once uc acik karari (yaklasim/model, zaman-dilimi, feature seti) gerekceleriyle
sunuyorum (Bolum 1-3), sonra S1/S2/S3'un gorev tanimina nasil islendigini ozetliyorum (Bolum 4),
sonra `justin_gecmis_calisma.md` sabitlerini ve izolasyon kisitini tasiyorum (Bolum 5-6), ve son
olarak Orkestrator'un bir sonraki turde dogrudan kullanabilecegi **TAM Arastirmaci gorev
tanimini** (Bolum 7) ve riskleri (Bolum 8) birakiyorum.

---

## 1) YAKLASIM TURU VE ADAY MODEL KARARI

Gorev tanimindaki aday (LightGBM/XGBoost) **teyit ediyorum, LightGBM'i birincil aday olarak
belirliyorum**, gerekcesiyle:

- **LightGBM (birincil aday):** Kategorik ozellikleri (oturum bayragi, gun-ici konum kovasi vb.)
  native destekler, buyuk/genis feature setlerinde egitim hizi yuksek, hiperparametre arama
  maliyeti dusuk — bu, S2'nin gerektirdigi purged/embargolu walk-forward'in COK SAYIDA katlama
  (fold) calistirmasi gerektigi bir protokolde pratik bir avantaj (Muhendis'in hesaplama
  butcesini asiri zorlamaz).
- **XGBoost (ikincil/kiyaslama modeli):** Arastirmaci raporunda LightGBM ile birlikte
  KIYASLAMALI olarak sunulmasi onerilir (ayni feature seti, ayni walk-forward katlamalari
  uzerinde) — tek modele erken kilitlenmek yerine, iki benzer-aileden model birbirini capraz
  dogrulasin. Bu bir zorunluluk degil, dusuk maliyetli bir saglamlik kontrolu.
- **Derin ogrenme (LSTM/Transformer) BU ILK TURDE ONERILMIYOR.** Gerekce: (i) Justin'in
  arastirma-veri hacmi/gecmisi henuz sinirli, derin modeller daha fazla veri ve daha fazla
  duzenlileştirme (regularization) altyapisi ister; (ii) S2 protokolunun tasarlandigi
  karmasiklik seviyesinin uzerine cikmak, ayni anti-overfitting onlemleriyle bile yalanci-pozitif
  riskini gereksiz artirir; (iii) "sade tut" ilkesi — ilk ML turunde yorumlanabilir, hizli
  egitilen, canliya-gecebilirligi kolay dogrulanan bir aile ile baslamak, karmasikligi
  gerekmedikce artirmama ilkesine uygun. Bu yol tukenirse (S3 esigine yaklasilirsa) derin
  ogrenme/RL bir sonraki ac secenek olarak Ertan'a ayrica sunulabilir — bu turde kapatilmiyor,
  sadece ilk adim olarak secilmiyor.

**YAKLASIM TURU (gorev tanimina yazilacak):** Makine ogrenmesi — SAF ozellik-tabanli klasik ML
(LightGBM birincil, XGBoost kiyaslama). Hibrit (kural-tabanli filtre + ML) bu turde ONERILMIYOR
— cunku H1/H2/H3'un basarisiz kural-tabanli sinyalinden herhangi birini "on-filtre" olarak
tasimak, madde-7'nin kendisinin elemis oldugu bir bileseni gizlice geri sokmak anlamina
gelebilir. Arastirmaci tamamen bagimsiz/orijinal bir feature-tabanli analiz yapmali.

---

## 2) ZAMAN-DILIMI / TUTMA-SURESI KARARI

Gorev tanimindaki iki alt-secenek: (i) M15+ veya (ii) M1-giris + genis-ATR-hedef. **Karar:
M15+ (giris VE tutma-suresi) birincil/zorunlu tasarim olarak seciliyor.** M1-giris+genis-ATR-
hedef zorunlu degil, Arastirmaci'nin veri gozleminde acikca daha iyi bir sinyal gorurse
raporunda **ikincil/opsiyonel bir varyant** olarak sunabilecegi bir yol (asagida sinirlariyla
birlikte aciklaniyor).

**Gerekce (Bolum 2'deki maliyet-duvari ayristirmasina dayali):**

1. Orkestrator'un degerlendirmesinde referans alinan H2/M5 kesitindeki ~%3,7 maliyet/ATR
   orani, "fiziksel olarak tutarli/kabul edilebilir" kalibrasyon ornegi olarak kalici on-kontrol
   standardina zaten islenmis (bkz. `justin_backtest_onkontrol_standardi.md`, Madde 2). M15,
   M5'ten daha genis bir bar oldugu icin ATR'i M5'ten de buyuk olacak, dolayisiyla ayni sabit
   islem-basi maliyet (spread+slipaj, bir giris+bir cikis) ATR'ye oranla DAHA KUCUK bir pay
   kaplayacaktir — yani M15+ tasarimi, zaten kabul-edilebilir bulunmus bir referans noktasindan
   (M5) daha fazla guvenlik payi ile S1'in 15-20x esigini karsilamaya baslar.
2. **M1-giris+genis-ATR-hedef alternatifinin daha zorlu oldugunu gosteren yaklasik hesap**
   (numeric-tutarlilik uyarisi: asagidaki ATR(M1)~358 pts rakami, Orkestrator'un kendi
   degerlendirmesinde uretilen, Muhendis tarafindan BAGIMSIZ dogrulanmamis yaklasik bir tahmindir
   — burada sadece goreli buyukluk/yon karsilastirmasi icin kullaniliyor, kesin karar girdisi
   degildir): sabit toplam maliyet ~51-56 pts iken, S1'in 15-20x esigini karsilamak icin
   islem-basi BRUT hedef ~780-1.040 pts olmasi gerekir — bu, ATR(M1)~358 pts referansina gore
   ~2,2-2,9x ATR(M1) buyuklugunde bir hareket demektir. Boyle genis bir hareketi M1 granularity'
   sinde guvenilir sekilde onceden kestirebilmek, normal-buyuklukte bir ATR(M15) hareketini
   kestirmekten cok daha zor/nadir bir hedeftir — pratikte cok dusuk bir isabet orani (WR) riski
   tasir.
3. **Overfitting/gurultu acisindan da M15+ daha guvenli:** M1 barlari arasinda otokorelasyon ve
   mikro-yapisal gurultu (spread sicramasi, tick-kumeleme) M15'e gore cok daha yuksektir; S2'nin
   purge/embargo mekanizmasi bu gurultuyu tamamen ortadan kaldiramaz, sadece azaltir. Daha az
   sayida ama daha "anlamli" (daha az mikro-gurultulu) bar uzerinde calismak, ayni anti-
   overfitting protokolunun ise yaramasini kolaylastirir.
4. **Canliya-gecebilirlik acisindan da M15+ daha az riskli:** Karar dongusu her 15 dakikada bir
   calistigi icin MT5 agent icinde ozellik hesaplama + model cikarim suresi butcesi cok rahat
   (saniyeler mertebesinde bir sure bile M15 dongusunde onemsizdir) — M1 tabanli bir tasarimin
   her dakika stabil sekilde calismasi gereken daha siki bir gerceklestirme kisidi olurdu.

**Tutma-suresi netligi:** Kesin bar sayisi (orn. "8 M15 bari" gibi) bu asamada ONCEDEN
SABITLENMIYOR — bu, asiri-optimize etmemek ilkesine uygun olarak Arastirmaci'nin veri
gozlemine/Backtest Muhendisi'nin taramasina birakilan bir parametredir. Zorunlu olan: SL/TP'nin
ATR(M15) tabanli belirlenmesi VE tasarimin ON-KONTROLDE (S1) maliyet-orani esigini gecmesi.

**M1-giris+genis-ATR-hedef icin sinir:** Eger Arastirmaci veri kesfinde M1 granularity'sinde
belirgin bir on-bulgu gorurse, bunu raporunda ikincil/opsiyonel bir bolum olarak sunabilir —
ANCAK bu varyant da AYNI S1 on-kontrolunden (15-20x maliyet orani) gecmek ZORUNDADIR, otomatik
istisna yoktur ve Backtest Muhendisi tarafindan ayni kalici on-kontrol standardiyla degerlendirilir.

---

## 3) VERI / FEATURE IHTIYACI

Kapali bir liste degil — Arastirmaci kendi bagimsiz analiziyle genisletebilir/degistirebilir.
Baslangic noktasi olarak asagidaki kategoriler oneriliyor (hepsi genel/herkese-acik teknik
kavramlar, izolasyon ihlali yok):

1. **Coklu-zaman-dilimi confluence:** M15 fiyatinin H1/H4 trend yonuyle uyumu (orn. H1/H4
   hareketli ortalamalara gore konum, farkli zaman dilimlerinde trend yonu ayni mi).
2. **Volatilite ozellikleri:** ATR(14, M15), ATR genisleme/daralma orani (kisa-donem ATR / uzun-
   donem ATR), Bollinger bandi genisligi.
3. **Hacim/tick-yogunlugu:** M15 bar basina tick-hacmi, tick-hacim momentum/anomali (ani
   artis/azalis).
4. **Oturum/gun-ici konum:** Asya/Londra/NY oturum bayraklari, gun-ici saat (dongusel/cyclic
   sin-cos kodlamasi), oturum acilis/kapanisina mesafe, haftanin gunu.
5. **Fiyat yapisi/momentum:** Kisa-donem getiri (lag return'ler), RSI, MACD, higher-high/lower-
   low ardisiklik sayaci (genel TA kavramlari — herkese acik, izolasyon disi).
6. **Maliyet/likidite gostergesi:** Ortalama spread ve spread volatilitesi (hem feature hem de
   S1 on-kontrolundeki maliyet tahmini icin girdi olarak kullanilabilir).

**Etiket (label) tanimi onerisi:** Triple-barrier yontemi (N-bar ileriye bakarak TP-once-mi /
SL-once-mi / hicbiri-mi siniflandirmasi) — bu hem finansal ML literaturunde standart bir
yaklasimdir hem de S2'deki feature-sizinti kontrol listesindeki "hedef degiskenin hesaplanmasinda
kullanilan veriyi feature'in dolayli icermesi" riskini azaltir (net, onceden tanimli bir sinir
[barrier] kullanildigi icin).

**Veri ihtiyaci:** M15 OHLCV + tick-hacim (dogrudan MetaTrader5 kutuphanesi), coklu-zaman-dilimi
turetilmis barlar (H1/H4) AYNI ham M15/tick veriden yeniden ornekleme yoluyla turetilmeli — ayri
bir kaynaga gerek yok. Egitim/dogrulama/test icin yeterli uzunlukta bir tarihsel donem (Arastirmaci
mevcut veri erisiminin kapsadigi en genis araligi raporlamali).

---

## 4) S1 / S2 / S3'UN GOREV TANIMINA NASIL ISLENDIGI — OZET

- **S1 (maliyet-orani zorunlulugu):** Bolum 7'deki gorev tanimina, tasarimin (M15+ zaman-dilimi
  + secilecek SL/TP/ATR semasi) Backtest Muhendisi'nin kalici on-kontrolunden (S1: brut kazanc >=
  ~15-20x tahmini maliyet) GECMESI GEREKTIGI acikca yazildi, referans:
  `justin_backtest_onkontrol_standardi.md`, Madde 2.
- **S2 (ML anti-overfitting protokolu):** Gorev tanimina, protokolun kendi "Uygulama Notu"
  bolumunde belirttigi satir AYNEN eklendi (Bolum 7, "Zorunlu Protokol" alt basligi) — purged/
  embargolu walk-forward, test-seti tek-kullanim, feature sizinti kontrol listesi, basari
  kriterlerinin egitimden ONCE sabitlenmesi, ilk turden itibaren gecerli.
- **S3 (on-taahhutlu gunbatimi maddesi):** Gorev tanimina AYNEN islendi (Bolum 7, "Governance
  Esigi" alt basligi) — tam metin, "tam tur"/"ayni olumsuz patern" tanimlari, sayacin Faz 1'in
  ilk turunden SIFIRDAN baslamasi, gunluk pipeline dongu sinirinin (5/gun) bagimsiz/paralel
  gecerliligi dahil. Bu esigin varligi Arastirmaci'ya BILGI olarak yaziliyor — esigin
  isletilmesi/onay sorusu Orkestrator'un sorumlulugunda kaliyor.

---

## 5) JUSTIN_GECMIS_CALISMA.MD REFERANSI

Asagidaki sabitler `justin_gecmis_calisma.md`'den aynen tasiniyor (Faz 0/Madde 1 kapsaminda
tamamlandi, gorev tanimina da eklendi — bkz. Bolum 7):

- HEDEF_PF = 1,5
- HEDEF_DD = %20 — KUMULATIF/TOPLAM DONEM BAZINDA, GUNLUK DEGIL (MilaGold'un gunluk emniyet-
  stopuyla KARISTIRILMAMALI)
- Kasa buyuklugu = 2.000 USD
- Islem-basi risk yuzdesi = %1 (ust sinir)
- Lot/olceklendirme kurali: baslangic 0,01 lot (sabit), her tam 2.000 USD kasa = 0,01 lot
- HEDEF_WR sabit degil, R:R senaryosuna gore turetilir (1:1 → %60,0; 1:2 → %42,9; 2:1 → %75,0) —
  Backtest Muhendisi R:R'yi henuz secmedi, secildiginde ilgili WR esigi kullanilacak.

---

## 6) VERI IZOLASYONU — GOREV TANIMINA YAZILACAK IFADE

Gorev tanimina, MilaGold/Signal GPT'ye ait hicbir sey isimlendirilmeden asagidaki ifade
eklendi (Bolum 7, "Veri Izolasyonu" basligi): "Bu proje kapsaminda baska bir dahili sistemin
bulgu/veri/parametresine erisim veya atif YOKTUR; tamamen bagimsiz/orijinal analiz yapilmalidir.
Tek veri kaynagi XM/MT5 fiyat verisidir (dogrudan MetaTrader5 kutuphanesi araciligiyla).
Calisma dizini yalniz C:\MilaYatirim\Justin\ altindadir."

---

## 7) TAM ARASTIRMACI GOREV TANIMI (FAZ 1 CIKTISI — Orkestrator'un bir sonraki turde
dogrudan kullanabilecegi icerik)

> Asagidaki blok, Orkestrator'un bir sonraki (Faz 2) turde `gorev_arastirmaci_justin_gold_
> scalping_ml_v1.md` olarak dogrudan kaydedip kullanabilecegi tam gorev tanimidir.

---

### GOREV TANIMI (taslak) — Orkestrator → Arastirmaci (ML/Feature-Tabanli Gold Scalping, v1)

**Gorev Kimligi**
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile —
  kural-tabanli fiyat-aksiyonu ailesi H1/H2/H3 ile Madde-7 tetiklenerek kapatildi)
- Pipeline adimi: 1/4 (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti)

**Amac**
XAUUSD (Gold) uzerinde, **M15 ve uzeri zaman-dilimi/tutma-suresine** dayanan, **ozellik-tabanli
klasik ML (LightGBM birincil aday, XGBoost kiyaslama modeli)** kullanan YENI bir Gold Scalping
yaklasimi icin arastirma/hipotez raporu uret. Bu M1 kural-tabanli fiyat-aksiyonu ailesinin
(H1/H2/H3, hepsi RED) YERINE gecen, iki bileseni BIRLIKTE ("VE", opsiyonel degil) iceren bir
yon degisikligidir: (i) kural-tabanli yerine ozellik-tabanli ML, (ii) M1 yerine daha genis bir
zaman-dilimi/tutma-suresi.

**Zaman-Dilimi / Tutma-Suresi**
- **M15+ birincil/zorunlu tasarim.** Giris sinyali ve tutma-suresi M15 (veya daha genis, orn.
  H1) bazinda kurgulanmali. Kesin bar sayisi onceden sabitlenmiyor — veri gozlemine birak.
- SL/TP semasi ATR(M15) tabanli olmali (kesin katsayi Stratejist'in bir sonraki turde bu
  yaklasima OZEL belirleyecegi bir deger/aralik olacak — otomatik tasima yok, bkz.
  `justin_backtest_onkontrol_standardi.md`, Madde 3).
- M1-giris+genis-ATR-hedef varyanti ZORUNLU degil; veri kesfinde acik bir on-bulgu varsa
  raporda ikincil/opsiyonel bir bolum olarak sunulabilir, ama ayni maliyet-orani on-kontrolune
  (asagida) tabidir.

**Yaklasim Turu ve Aday Model**
- Ozellik-tabanli klasik ML. Birincil aday: **LightGBM**. Ikincil/kiyaslama: **XGBoost** (ayni
  feature seti uzerinde, karsilastirmali sunulmasi onerilir, zorunlu degil).
- Hibrit (eski kural-tabanli sinyalleri on-filtre olarak kullanma) bu turde ONERILMIYOR —
  tamamen bagimsiz/orijinal feature-tabanli analiz yapilmali.
- Derin ogrenme/RL bu ilk turde kapsam DISI (veri hacmi/karmasiklik-overfitting gerekcesiyle);
  ileride ayrica degerlendirilebilir.

**Veri / Feature Ihtiyaci (baslangic noktasi, kapali liste degil)**
1. Coklu-zaman-dilimi confluence (M15/H1/H4 trend uyumu)
2. Volatilite ozellikleri (ATR(14) M15, ATR genisleme/daralma orani, bant genisligi)
3. Hacim/tick-yogunlugu (M15 bar basina tick-hacim, hacim momentum/anomali)
4. Oturum/gun-ici konum (Asya/Londra/NY bayraklari, dongusel saat kodlamasi, oturum
   acilis/kapanisina mesafe, haftanin gunu)
5. Fiyat yapisi/momentum (lag return'ler, RSI, MACD, higher-high/lower-low ardisiklik)
6. Maliyet/likidite gostergesi (ortalama spread, spread volatilitesi)
- **Etiket (label) onerisi:** Triple-barrier yontemi (N-bar ileri TP-once/SL-once/hicbiri).
- Veri kaynagi: M15 OHLCV + tick-hacim, dogrudan MetaTrader5 kutuphanesi; H1/H4 barlari ayni
  ham veriden yeniden ornekleme yoluyla turetilmeli.

**VERI IZOLASYONU — ZORUNLU KISIT**
Bu proje kapsaminda baska bir dahili sistemin bulgu/veri/parametresine erisim veya atif YOKTUR;
tamamen bagimsiz/orijinal analiz yapilmalidir. Tek veri kaynagi XM/MT5 fiyat verisidir
(dogrudan MetaTrader5 kutuphanesi araciligiyla). Calisma dizini yalniz
`C:\MilaYatirim\Justin\` altindadir, disina erisim yok.

**Zorunlu Protokol (S2 — ML Anti-Overfitting)**
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md` (ML/hibrit yaklasimlar icin
ZORUNLU anti-overfitting protokolu — purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri onceden sabit). Bu protokol Arastirmaci
asamasindan itibaren (feature tasarimi/label tanimi/veri bolme mantiginda) gecerlidir — sonradan
eklenecek bir kontrol degildir.

**On-Kontrol Hatirlatmasi (S1 — Maliyet-Orani, Backtest Muhendisi asamasinda uygulanacak
ama tasarim BUNU DIKKATE ALARAK yapilmali)**
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` — tasarimin hedef islem-basi
brut kazanci, tahmini toplam maliyetin (spread+slipaj) en az ~15-20 kati olacak sekilde
kurgulanmis olmali; bunu karsilamayan tasarimlar Muhendis on-kontrolunde otomatik elenir.
Arastirmaci raporunda, onerilen zaman-dilimi/hedef buyuklugunun bu orani nasil karsilamasi
beklendigine dair kaba bir on-tahmin (ATR(M15) buyuklugu, tipik spread) sunmasi faydali olur.

**Governance Esigi (S3 — bilgi amacli, Arastirmaci'nin bilmesi gereken)**
ML ailesinde 2 tam tur (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti zinciri,
bir Risk Analisti KARARI ile sonuclanan) ayni olumsuz paternle (aggregate/on-kontrolde
"anlamli" gorunen bir sinyal/model, tam testte tutarli PF<1/sistematik RED) sonuclanirsa,
Orkestrator otomatik olarak Ertan'a onay sorusu yoneltir, varsayilan oneri alt-hedefi
durdurmadir. Sayac bu Faz 1'in ilk turunden sifirdan baslar (H1/H2/H3 sayaci devrolmez).
Gunluk pipeline dongu siniri (5/gun) bu sayactan bagimsiz, paralel gecerlidir.

**Gecmis Calisma / Cerceve Dosyasi (zorunlu referans)**
`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — HEDEF_PF=1,5; HEDEF_DD=%20 (kumulatif/toplam
donem, gunluk degil); kasa=2.000 USD; islem-basi risk=%1 (ust sinir); lot 0,01 sabit baslangic,
her 2.000 USD kasa=0,01 lot; HEDEF_WR R:R'ye gore turetilir (1:1→%60,0; 1:2→%42,9; 2:1→%75,0).

**Beklenen Cikti**
- Rapor formati: Markdown, `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_ml_raporu.md`
- Bolumler: Ozet, Gozlemler (M15+ volatilite/hacim/oturum paternleri), Onerilen Feature Seti
  ve Label Tanimi, En Az 1 Somut ML Tasarim Onerisi (model + feature + zaman-dilimi + kaba
  maliyet-orani on-tahmini), Riskler/Sinirlamalar (overfitting, veri sizintisi, canliya-
  gecebilirlik dahil), Acik Sorular, Izolasyon Notu.

**Sonraki Adim**
Rapor tamamlaninca Orkestrator, Stratejist'i bu raporla gorevlendirir (pipeline sirasi geregi
Backtest Muhendisi'ne dogrudan atlanmaz); Stratejist bu asamada yaklasima ozel SL/TP/ATR
katsayisini belirler.

**Bildirim**
Bu gorev tamamlandiginda Orkestrator, Ertan'a Telegram bilgi notu gonderir (onay talebi degil,
bilgilendirme) ve Orkestrator_Loglar'a kayit dusar.

---

## 8) RISKLER

- **Overfitting:** Genis feature seti + GBM'in esnekligi, dar kural-tabanli hipotezlere gore
  cok daha yuksek yalanci-pozitif riski tasir. S2 protokolu (purge/embargo, tek-kullanimlik
  test seti, onceden sabit basari kriterleri) bu riski AZALTIR ama SIFIRLAMAZ — Backtest
  Muhendisi'nin egitim/test performans farkina (buyuk fark = overfitting isareti) ozellikle
  dikkat etmesi gerekir.
- **Veri sizintisi (look-ahead bias):** Coklu-zaman-dilimi feature'larda (H1/H4 turetilmis
  barlar) ozellikle dikkat: bir H1 bari TAMAMLANMADAN o barin degerini M15 feature'ina
  sizdirmak klasik bir hata kaynagidir — feature hesaplama zaman damgasi, o M15 aninda
  GERCEKTEN mevcut olan en son KAPANMIS ust-zaman-dilimi barina dayanmali. S2'nin feature
  sizinti kontrol listesi bunu ayrica teyit etmeli.
- **DST/saat-eslesme riski (coklu-zaman-dilimi join karmasikligindan artan bir turev risk):**
  M15/H1/H4 barlarinin dogru zaman hizalanmasi, VPS'in DST davranisina bagli — kalici on-kontrol
  standardinin Madde 1'i (DST dogrulamasi) burada normalden daha kritik, cunku tek-zaman-dilimi
  degil COKLU-zaman-dilimi hizalama hatasi riski var.
- **Hesaplama maliyeti:** Purged/embargolu walk-forward + coklu model (LightGBM+XGBoost
  kiyaslama) + coklu-zaman-dilimi feature muhendisligi, H1/H2/H3'teki kural-tabanli testlere
  gore Backtest Muhendisi asamasinda daha yuksek hesaplama/sure butcesi gerektirebilir —
  Muhendis'in gorev tanimini alirken bunu bir kapasite/sure notu olarak isaretlemesi faydali
  olur.
- **Canliya-gecebilirlik:** M15 karar dongusu, gercek-zamanli cikarim suresi acisindan M1'e
  gore COK daha rahat bir butce sunar (agentin her 15 dakikada bir feature hesaplayip model
  cikarimi yapmasi yeterli — saniyeler mertebesindeki bir sure onemsizdir). Asil risk model
  DAGITIM SEKLI: egitilmis LightGBM/XGBoost modelinin (orn. .txt/.pkl/.joblib) MT5 agent'in
  calistigi Python ortamina nasil tasinacagi, kutuphane surum uyumlulugu (egitim ortami vs
  canli agent ortami ayni LightGBM/XGBoost surumu olmali) ve feature hesaplama kodunun
  egitim/canli arasinda BIREBIR ayni mantikla (ayni normalizasyon, ayni zaman-hizalama)
  calismasi gerektigi Arastirmaci/Backtest Muhendisi raporlarinda acikca ele alinmalidir —
  aksi halde "egitimde iyi, canlida farkli" tutarsizligi (training-serving skew) olusabilir.

---

## BACKTEST MUHENDISI ICIN NOTLAR

Bu turde Backtest Muhendisi'ne aktif bir gorev yok (Arastirmaci onceki adim). Ileride Arastirmaci
raporu geldiginde ve Stratejist SL/TP/ATR katsayisini belirledikten sonra: (i) kalici on-kontrol
standardinin UCU DE (DST, maliyet-orani, SL/TP-ozel) uygulanmali, (ii) S2 protokolu (purge/
embargo, tek-kullanimlik test seti) BASTAN entegre edilmeli — sonradan eklenecek bir adim
degildir, (iii) egitim/test performans farki (overfitting isareti) raporda ayrica ele alinmali,
(iv) coklu-zaman-dilimi feature'larin zaman-hizalama dogrulamasi (Risklerdeki DST-turevi risk)
ayrica teyit edilmeli.

## ARASTIRMACI ICIN NOTLAR

Bolum 7'deki tam gorev tanimi, Orkestrator tarafindan bir sonraki turde dogrudan
kullanilacak/kaydedilecek icerik olarak hazirlanmistir. Arastirmaci, bu gorev geldiginde
YAKLASIM TURU (LightGBM birincil), ZAMAN-DILIMI (M15+ birincil), VERI/FEATURE listesi ve S1/S2/
S3 kisitlarinin TAMAMINI baslangic noktasi olarak almali; bunlarin disina cikmak isterse
(orn. farkli bir model ailesi, M1-giris varyanti) gerekcesini raporunda acikca belirtmelidir.

---

## GUNCEL HIPOTEZ/AILE DURUMU OZETI

| Aile / Hipotez | Durum | Not |
|---|---|---|
| Kural-tabanli fiyat-aksiyonu (H1, H2, H3) | KAPANDI (RED, Madde-7 tetiklendi) | — |
| ML/feature-tabanli (LightGBM birincil, M15+) | **Faz 1 — gorev tanimi hazirlandi, HENUZ Arastirmaci'ya verilmedi** | S3 sayaci bu aileden SIFIRDAN baslayacak |

---

## IZOLASYON NOTU

- Bu oturumda da MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (stratejici_gold_gecmis_
  calisma.md, signal.json, milagold_trades.json, lisa_performance.json, positions_status.json
  vb.) ACILMADI veya referans ALINMADI.
- Calisma yalnizca `C:\MilaYatirim\Justin\` dizininde yapildi (girdi: gorev tanimi, governance/
  degerlendirme/standart/cerceve dosyalari, kendi onceki raporum v5; cikti: bu dosya).
- Yukarida hazirlanan Arastirmaci gorev tanimina da (Bolum 7) MilaGold/Signal GPT'ye ait hicbir
  sey isimlendirilmeden, sadece "tamamen bagimsiz/orijinal analiz yap" ifadesiyle izolasyon
  hatirlatmasi eklendi.

---

## ONAY NOKTASI

Bilgi notu — bu Faz 1 turunun kendisi (Arastirmaci'ya henuz gorev VERILMIYOR, sadece gorev
TANIMI yazildi) salt-analiz/dokumantasyon niteliginde, canli sisteme/hesaba hicbir etkisi yok.
4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok (Justin arastirma/demo asamasi,
canli hesap yok), tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) →
STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecek.

**Devam notu:** Faz 1 bu turun (Stratejist v6) TEK adimidir, tamamlandi. Devaminda (Bolum 7'deki
gorev taniminin fiilen `gorev_arastirmaci_justin_gold_scalping_ml_v1.md` olarak kaydedilip
Arastirmaci'nin agent_cagir ile tetiklenmesi, Faz 2) Orkestrator'un otonom dongusune birakiliyor.
