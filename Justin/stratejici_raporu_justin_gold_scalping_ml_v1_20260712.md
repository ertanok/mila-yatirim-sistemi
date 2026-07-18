# STRATEJICI RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile (M15+), v1

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
Pipeline adimi: 2/4 (Arastirmaci → **Stratejist** → Backtest Muhendisi → Risk Analisti)
Tarih: 12 Temmuz 2026 (VPS-yerel)
Gorev kaynagi: Orkestrator gorev tanimi, "GOREV TANIMI — Orkestrator → Stratejist (ML/
Feature-Tabanli Gold Scalping, v1 — Faz 2)"
Girdi raporu: `arastirmaci_gold_scalping_ml_raporu.md` (Arastirmaci, Faz 2, 1/4 — TAMAMLANDI)

**Not (gorev-takip harness durumu):** Bir onceki (Arastirmaci) adiminin durum dosyasi "hata"
olarak isaretlenmis olsa da, Orkestrator'un incelemesi bunun rapor icerigiyle degil harness'in
basari-kriteri tespitiyle (maxTurns siniri) ilgili oldugunu belirlemis; rapor eksiksiz/tutarli
bulunmus ve bu bilgiyle pipeline'a devam edilmesine karar verilmistir. Bu Stratejist adimi bu
karari sorgulamaz, sadece kayit dusmek icin tekrarlanmistir.

---

## OTURUM OZETI

Bu oturumda **Arastirmaci'nin M15/H1/H4 ML/feature-tabanli Gold Scalping raporu** (BULGU 1-11,
Onerilen Feature Seti/Label Tanimi, ML Tasarim Onerisi, Riskler, Acik Sorular) girdi olarak
alinmistir. Yeniden arastirma yapilmamis, asagidaki sayisal bulgular DOGRUDAN Arastirmaci'nin
olcumlerinden devralinmis ve bunlarin uzerine karar/sentez insa edilmistir:

- **BULGU 10 (Triple-Barrier taban dagilimi):** N (bar/saat) ve k (xATR14-M15) kombinasyonlarina
  gore TP-once/SL-once/hicbiri oranlari. Ozellikle N=8/k=1,0-2,0 ve N=16/k=1,0-2,0 hucreleri
  karsilastirilmistir.
- **BULGU 11 (Maliyet-orani on-tahmini):** M15 medyan ATR14 (287,43 pts) / M15 medyan spread (27
  pts) = 10,65x (k=1,0); k=1,5 → 15,97x; k=2,0 → 21,29x. S1 esigi (~15-20x) k=1,5'te ALT SINIRDA,
  k=2,0'da rahatca karsilaniyor.
- **BULGU 5 (Coklu-TF Confluence):** Confluence orani %44,8; confluence varken (ozellikle
  yukari-confluence) 2 saatlik ileri getiri confluence-yok duruma gore belirgin sekilde daha
  buyuk (+36,48 vs +21,76 puan).
- **BULGU 1-2 (Saat/Oturum Profili):** ATR14 saat bazinda 2,3-2,9 kat farklilasiyor (en yuksek
  16-19, en dusuk 1-3/8-9 sunucu saati); spread gun boyunca goreceli dar (27-33 pts).
- **BULGU 6-7-9 (Momentum/Yapisi/Hacim):** RSI/MACD (ham deger, isaret degil — mekanik
  otokorelasyon uyarisi), HH/LL streak, hacim-anomali sonrasi %30,4 daha genis range.
- **RISKLER Madde 1 (kutuphane kisiti):** Arastirmaci ortaminda pandas/lightgbm/xgboost/
  scikit-learn kurulu degil, gercek model egitimi YAPILMAMIS — bu bir acik bagimlilik olarak
  Backtest Muhendisi'ne devredilmistir (asagida, "Karar 4" ve "Backtest Muhendisi icin Notlar").

Bu oturumda benim (Stratejist) katkim: (1) N/k'yi KESIN olarak belirlemek, (2) etiket semasina
karar vermek, (3) feature onceligini netlestirmek, (4) kutuphane bagimliligina iliskin notu
Backtest Muhendisi'ne tasimak, ve bunlara dayali 3 somut hipotez uretmek.

---

## KARAR VERMENIZ BEKLENEN OZEL NOKTALAR — YANITLAR

### Karar 1 — N/k Secimi (KESIN)

**Secim: N=16 (4 saat / 16 M15-bar), k=1,5xATR14(M15).**

Gerekce:
- Cost-ratio (S1) acisindan k, N'den BAGIMSIZ hesaplanir (yalniz M15 ATR14 medyanina baglidir);
  yani N=8/k=1,5 ile N=16/k=1,5 AYNI cost-ratio'ya (15,97x) sahiptir — N secimi cost-ratio'yu
  degistirmez, SADECE sinif dengesini ve efektif ornek sayisini degistirir.
- Bu sabitken, N=16/k=1,5 (TP %44,45, SL %42,47, hicbiri %13,07) N=8/k=1,5'e (TP %35,03, SL
  %34,05, hicbiri %30,93) gore ACIKCA ustundur: ayni maliyet-orani icin ~2,4 kat daha az veri
  israfi (hicbiri) ve daha yuksek TP+SL toplam orani (~%86,9 vs ~%69,1) — S2 protokolunun
  "yeterli/kararli ornek" ilkesiyle daha uyumlu, cunku egitim/test/embargo ayrimindan sonra
  kalan efektif ornek sayisi (yaklasik 86.800) N=8/k=1,5'e (yaklasik 69.000) gore daha genis bir
  taban sunar.
- k=2,0 (N=16: TP %38,23, SL %36,85, hicbiri %24,92, cost-ratio 21,29x) daha rahat bir
  maliyet-orani marjina sahip olsa da, hicbiri orani ~1,9 kat artmakta (13,07→24,92) ve TP+SL
  toplam orani dusmektedir (%86,9→%75,1) — bu, k=1,5'e gore DAHA FAZLA veri israfi anlamina
  gelir. k=1,5'in cost-ratio'su (15,97x) esigin (~15-20x) ALT SINIRINDA olsa da esigi
  KARSILAMAKTADIR (esik altinda degil); bu nedenle k=1,5 BASLANGIC/ANA tasarim olarak secilmistir.
- **Guvenlik marji icin:** k=1,5'in esigin alt sinirinda olmasi riskini yalniz "bilgi notu" olarak
  birakmak yerine, asagidaki Hipotez 3'te AYNI N=16 ile k=2,0 varyanti da ikinci/opsiyonel bir
  DUYARLILIK (sensitivity) testi olarak sunulmustur — Backtest Muhendisi iki k degerini paralel
  test ederse, cost-ratio guvenlik marji ile sinif-dengesi/veri-verimliligi arasindaki
  degis-tokusu ampirik olarak (gercek P&L uzerinden) karsilastirabilir.
- N=16 (4 saatlik tutma suresi), M15-girisli bir "scalping" projesi icin goreceli UZUN bir
  ufuktur (bu, proje adindaki "scalping" beklentisiyle bir miktar gerilim yaratabilir — bu,
  asagida RISKLER'de ayrica not edilmistir); ancak veri BUNU DESTEKLEMEKTEDIR (N kucultuldukce
  sinif dengesizligi/veri israfi hizla kotulesiyor, BULGU 10) — Stratejist olarak veriye
  dayanmayan bir "daha kisa olmali" tercihini one cikarmiyorum.

### Karar 2 — Etiket Semasi (KESIN)

**Secim: IKILI siniflandirma — "yukari-bariyer-once" (entry+k*ATR ilk dokunulan) vs
"asagi-bariyer-once" (entry-k*ATR ilk dokunulan); "hicbiri" ornekleri EGITIM/TEST SETINDEN
CIKARILIR (filtrelenir).**

Gerekce:
- N=16/k=1,5'te "hicbiri" orani zaten dusuk (%13,07) — filtrelemenin orneklem kaybi kucuktur
  (99.871 barin ~%13'u disarida kalir, ~86.800 ornek kalir — bu, LightGBM/XGBoost gibi
  agac-tabanli modeller icin fazlasiyla yeterli bir buyuklüktür).
- Ikili siniflandirma, 3-sinifliye gore daha az parametre/karar siniri karmasikligi tasir — S2
  protokolunun "arama uzayini dar tut" ilkesiyle dogrudan uyumludur (ilk tur icin daha dusuk
  overfitting riski).
- **Onemli cerceve netlestirmesi:** Arastirmaci'nin raporunda "TP-once"/"SL-once" adlandirmasi,
  olcumun SABIT (hipotetik long referans) bir cerceveden yapildigini ima ediyor (BULGU 8'deki
  yukari-yon onyargisiyla tutarli kucuk TP>SL farki). Bu Stratejist raporunda etiket, YON-TARAFSIZ
  bir bicimde yeniden cerceveleniyor: "yukari-bariyer-once" = entry+k*ATR ilk dokunulan (bu barda
  LONG acilsaydi kazanirdi), "asagi-bariyer-once" = entry-k*ATR ilk dokunulan (bu barda SHORT
  acilsaydi kazanirdi). Boylece model, HER bar icin yon tahmini yapan BIRINCIL karar mekanizmasi
  olur — ayri bir kural-tabanli yon-belirleme katmanina ihtiyac YOKTUR (Arastirmaci'nin "En Az 1
  Somut ML Tasarim Onerisi" bolumundeki orijinal cerceveyle tutarlidir, sadece isimlendirme
  yon-tarafsiz hale getirilmistir).
- 3-sinifli sema (hicbiri dahil), hicbiri oraninin daha yuksek oldugu k=2,0 varyanti icin
  IKINCI TUR/OPSIYONEL bir alternatif olarak saklanmistir (asagida Hipotez 3'un notlarinda).

### Karar 3 — Feature Onceligi (KESIN)

| Grup | Icerik | Durum (Tur 1) | Gerekce |
|---|---|---|---|
| 1 — Volatilite | ATR14 (M15/H1/H4), genis/dar rejim orani | **ZORUNLU** | k'nin kendisi ATR'e dayanir; BULGU 4 rejim ayrimi net (genis rejimde %27,7 daha buyuk hareket) |
| 2 — Coklu-TF Confluence | M15/H1/H4 trend isareti, confluence bayragi/yonu | **ZORUNLU** | BULGU 5'teki en net yonlu edge (confluence + yukari-yon: +36,48 vs +21,76 puan) |
| 3 — Hacim/Tick-Yogunlugu | tick_volume, anomali bayragi, hacim egimi | **ZORUNLU** | BULGU 9'daki net iliski (anomali sonrasi %30,4 daha genis range); UCUZ hesaplanir (2-3 sutun) |
| 4 — Oturum/Gun-Ici Konum (CEKIRDEK) | saat (sin/cos), oturum bayragi (Asya/Londra/NY), haftanin gunu | **ZORUNLU** | BULGU 1-2'deki guclu saat etkisi (2,3-2,9x ATR farki) |
| 4 — Seans acilis/kapanisina mesafe (ALT-PARCA) | — | **OPSIYONEL / Tur 2** | Arastirmaci bu alt-parcayi OLCMEDI (Acik Soru 3); saat/oturum cekirdegi zaten guclu sinyal veriyor, ek karmasiklik ilk turda gereksiz |
| 5 — Fiyat Yapisi/Momentum | Lag getiriler (1/4/8/16-bar), RSI14 (ham), MACD hatti+histogram (ham deger — isaret DEGIL, BULGU 6 SINIR), HH/LL streak uzunlugu | **ZORUNLU** | Standart/ucuz momentum feature'lari; MACD icin Arastirmaci'nin acik uyarisina (isaret-kaliciligi degil ham deger) HARFIYEN uyulmali |
| 6 — Maliyet/Likidite | M15 spread (ham+trailing) | **MODEL FEATURE'I DEGIL** — S1 on-kontrol girdisi | Arastirmaci'nin onerisiyle ayni: bu bir on-filtre/on-kontrol degeri, egitim feature setine KARISTIRILMAMALI (S1 ile modelin karar mekanizmasinin ayrisik kalmasi icin) |

Toplam ilk-tur feature sayisi: yaklasik **18-22 sutun** (Gruplar 1+2+3+4-cekirdek+5) —
Arastirmaci'nin onerdigi 15-25 araliginin alt-orta bandinda, S2'nin "dar arama uzayi" ilkesiyle
uyumlu bir baslangic.

### Karar 4 — Kutuphane Bagimliligi (Backtest Muhendisi'ne Not, Stratejist karar alani DISINDA)

Bu arastirma/stratejici ortaminda pandas/lightgbm/xgboost/scikit-learn KURULU DEGIL — Arastirmaci
gercek model egitimi yapmamis, bu rapor da (Stratejist asamasi oldugu icin zaten) model
calistirmamistir. **Backtest Muhendisi asamasi icin varsayim/istek:** bu kutuphanelerin VPS
uzerinde (veya ayri, izole bir Python ortaminda/venv) kurulu olmasi GEREKIR; bu asamaya
BASLAMADAN ONCE bir bagimlilik/on-kosul kontrolu (`pip show lightgbm xgboost scikit-learn
pandas` veya esdegeri) yapilmasi ve eksikse kurulumun ayri bir adim olarak GORUNUR sekilde
raporlanmasi onerilir (sessizce/otomatik kurulum degil — VPS'e paket ekleme bir ust-seviye
etkiye sahip olabilir, en azindan bir bilgi notu gerektirir). Veri boyutu (~87.000-100.000
satir, ~20 feature) goz onune alindiginda GPU gerekmez, standart CPU (VPS'in mevcut donanimi)
yeterli olmalidir — egitim suresi (LightGBM icin, bu olcekte) dakikalar mertebesinde beklenir,
ama bu tahmindir, Backtest Muhendisi olcup raporlamalidir.

---

## HIPOTEZLER

### HIPOTEZ 1 — LightGBM Ikili Yon-Tahmini Modeli (N=16/k=1,5) [ANA HIPOTEZ]

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (LightGBM, birincil aday)

**MANTIK:** Arastirmaci'nin BULGU 10-11 verisi, N=16/k=1,5 kombinasyonunun hem S1 maliyet-orani
esigini (15,97x, alt sinirda ama karsilaniyor) karsiladigini hem de en dengeli/en genis efektif
ornek tabanini (TP %44,45, SL %42,47, hicbiri sadece %13,07) sundugunu gostermektedir. BULGU
5'teki confluence edge'i ve BULGU 1-2'deki saat/oturum etkisi, dogrudan ham fiyat/indikator
kurallariyla degil, bir modelin bu sinyalleri BIRLIKTE agirliklandirmasiyla daha iyi
degerlendirilebilir turden (dogrusal olmayan, feature-etkilesimli) bir yapidadir — bu, agac
tabanli bir modelin (LightGBM) dogal gucudur.

**YONTEM DETAYI:**
- Model: LightGBM binary classifier (`objective=binary`, temel hiperparametre araligi:
  num_leaves ~15-31, max_depth sinirli/orta — S2 geregi genis grid-search YAPILMAMALI, dar bir
  aralik ONCEDEN sabitlenmeli).
- Feature seti: Karar 3'teki ZORUNLU gruplar (1, 2, 3, 4-cekirdek, 5) — ~18-22 sutun.
- Veri: XM/MT5 GOLD M15, ayni Arastirmaci veri araligi (2022-04-18→2026-07-10, ~99.871 gecerli
  bar N=16 icin).

**GIRIS/CIKIS MEKANIZMASI:** Model her barda P(yukari-bariyer-once) olasiligini uretir. Esik
degeri (baslangic onerisi: p>=0,55-0,60 → LONG, p<=0,40-0,45 → SHORT; ikisi arasi → ISLEM YOK)
Backtest Muhendisi tarafindan egitim/validasyon setinde ROC-AUC + precision-recall egrisiyle
KALIBRE EDILMELI (test setine bakilmadan, S2 Madde 2 geregi). Model boylece hem yon hem
"islem yapilmali mi" kararini AYNI ANDA uretir — ayri bir kural-tabanli entry-tetikleyicisi
YOKTUR.

**SL/TP veya RISK YONETIMI:**
- SL = k x ATR14(M15) = 1,5 x ATR14(giris ani), TP = ayni mesafe (simetrik, k=1,5xATR).
- Zaman-bariyeri (time-stop): N=16 M15-bar (4 saat) icinde ne TP ne SL tetiklenirse, pozisyon
  bar-16 kapanisinda KAPATILIR (Backtest Muhendisi'nin "hicbiri" durumunu nasil P&L'e
  yansitacagi net olmali — bu bir zaman-asimi cikisidir, ayri bir kayip/kazanc kategorisi).
- RR orani = 1:1 (simetrik k) → `justin_gecmis_calisma.md` formulune gore HEDEF_PF=1,5 icin
  gerekli WR = **%60,0**. Ham taban dagilimi (TP+SL icinde TP orani ~%51,1 = 44,45/(44,45+42,47))
  bu esigin ALTINDADIR — modelin GOREVI, olasilik esigiyle FILTRELEME yaparak (dusuk-guven
  islemleri eleyerek) YUKSEK-GUVEN alt-kumede WR'yi %60'a tasimaktir. Bu, ham taban oranindan
  daha az ama daha kaliteli islem sayisi anlamina gelir — Backtest Muhendisi bu degis-tokusu
  (esik yukseldikce islem sayisi/WR egrisi) raporlamalidir.
- Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1 (ust sinir), lot =
  (kasa x 0,01) / (SL_puan x puan-degeri), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot.

**DOGRULAMA IHTIYACI:** Purged/embargolu walk-forward (S2 Madde 1) ZORUNLU — egitim/test
pencereleri arasinda N=16-bar (4 saat) + makul bir ek embargo (orn. ek 4-8 saat) purge edilmeli
(triple-barrier etiketinin kendisi 4 saat ileriye baktigi icin, sinir bolgesindeki barlarin
etiketi test penceresine "sizabilir"). Test seti TEK KEZ, tum model/esik secimi bittikten sonra
calistirilmali (S2 Madde 2). Feature-sizinti kontrol listesi (S2 Madde 3) her feature icin
madde madde teyit edilmeli — ozellikle normalizasyon istatistiklerinin SADECE egitim setinden
hesaplandigi.

**RISKLER:**
- N=16 (4 saat tutma), bir "scalping" projesi icin goreceli uzun bir ufuktur — canli ortamda
  pozisyonun 4 saat acik kalmasi, ek haber/rejim riski tasir (bu, kural-tabanli H1/H2/H3
  ailesinden farkli bir risk profilidir, ayrica Risk Analisti asamasinda degerlendirilmeli).
- Overfitting: LightGBM hiperparametre araligi (num_leaves, learning_rate, n_estimators) DAR
  tutulmali, genis grid-search YAPILMAMALI (S2 gerekcesi — ML ailesinde arama uzayi zaten
  kural-tabanliden genis).
- Veri sizintisi: MACD histogramin mekanik otokorelasyonu (BULGU 6 SINIR, %92,3 isaret-kaliciligi)
  purge/embargo dogru uygulanmazsa sahte-performansa yol acabilir.
- Canliya-gecebilirlik: LightGBM inference tipik olarak cok hizlidir (<10ms/tahmin beklenir) ama
  bu OLCULMEMISTIR — MT5 agent icinde gercek-zamanli calistirilabilirligi (model dosyasinin
  VPS'e tasinmasi, Python bagimliliklarinin orada da kurulu olmasi, M15 bar kapanisinda tetikleme
  gecikmesi) Backtest Muhendisi/Risk Analisti asamasinda ayrica dogrulanmali.
- Maliyet-orani (15,97x) esigin ALT SINIRINDA — P90/max spread ile stres testinde (Backtest
  Muhendisi'nin gorevi) esik kaybedilebilir; bu durumda Hipotez 3'teki k=2,0 varyantina
  gecilmesi (asagida) bir yedek/fallback olarak dusunulebilir.

**ONCELIK: 1-Yuksek** — Arastirmaci'nin ana ML tasarim onerisiyle dogrudan uyumlu, en iyi
sinif-dengesi/veri-verimliligini sunan, cost-ratio esigini karsilayan tek-model tasarimdir.

---

### HIPOTEZ 2 — XGBoost Kiyaslama (Ayni Tasarim, Ayni Feature/Label/N/k)

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (XGBoost, ikincil/kiyaslama)

**MANTIK:** Gorev tanimi acikca XGBoost'u "opsiyonel kiyaslama" olarak istemektedir. Ayni
feature seti, ayni etiket (Karar 1-3), ayni N/k ile, SADECE model mimarisi degistirilerek
LightGBM sonucunun model-secimine mi yoksa veri/sinyale mi bagli oldugu ayristirilabilir — eger
iki model de benzer performans verirse, sinyal muhtemelen genellenebilir (belirli bir modelin
idiosinkrazisi degil); buyuk fark varsa, bu hiperparametre/model-mimarisi hassasiyetine isaret
eder (ek dikkatle yorumlanmali).

**YONTEM DETAYI:** XGBoost binary classifier (`objective=binary:logistic`), AYNI egitim/test/
embargo bolme, AYNI feature seti (Hipotez 1 ile birebir), AYNI hiperparametre arama disiplini
(dar aralik, S2 geregi).

**GIRIS/CIKIS MEKANIZMASI:** Hipotez 1 ile AYNI (olasilik esigi tabanli yon/islem karari) —
sadece olasiligi ureten model farkli.

**SL/TP veya RISK YONETIMI:** Hipotez 1 ile BIREBIR AYNI (N=16, k=1,5xATR, RR=1:1, ayni lot/risk
kurallari) — S1 standardinin 3. maddesi geregi (SL/TP her yaklasima ozel belirlenir) burada
"yaklasim" LightGBM/XGBoost ayrimini degil, N=16/k=1,5 barrier tasarimini ifade eder; iki model
AYNI barrier tasarimini paylastigi icin SL/TP tekrar tasima DEGIL, aynı tasarimin dogal bir
parcasidir.

**DOGRULAMA IHTIYACI:** Hipotez 1 ile AYNI purged walk-forward + test-tek-kullanim protokolu.
Ek olarak: iki modelin OOS performansi (PF, WR, esik-kalibrasyonlu islem sayisi) YAN YANA
raporlanmali; buyuk sapma (orn. bir model gecerken digeri kalirsa) ayrica aciklanmali (feature
onemi/SHAP karsilastirmasi onerilir, ama bu zorunlu degil, ek bilgi).

**RISKLER:** Hipotez 1'in tum riskleri (overfitting, veri sizintisi, canliya-gecebilirlik)
gecerlidir + ek olarak: iki modelin PARALEL egitilmesi hesaplama maliyetini ikiye katlar
(kucuk bir risk, veri boyutu bu olcekte ikisi icin de yonetilebilir). Kutuphane bagimliligi
(Karar 4) hem lightgbm hem xgboost icin ayri ayri gecerlidir.

**ONCELIK: 2-Orta** — Gorev tanimindaki acik istek geregi yapilmali, ama LightGBM sonucu RED
cikarsa (sinyal zayifsa) XGBoost'un da benzer sekilde RED cikmasi beklenir; bu nedenle asil
karar agirligi Hipotez 1'dedir, Hipotez 2 onu DOGRULAYAN/CAPRAZ-KONTROL EDEN bir ikinci olcumdur.

---

### HIPOTEZ 3 — Duyarlilik/Guvenlik-Marji Varyanti: LightGBM, N=16/k=2,0 (+ 3-sinifli opsiyon)

**YAKLASIM TURU:** Makine ogrenmesi — Gradient Boosting (LightGBM), Hipotez 1'in barrier
parametresi degistirilmis (k) DUYARLILIK TESTI varyanti

**MANTIK:** Hipotez 1'deki k=1,5 cost-ratio'su (15,97x) S1 esiginin (~15-20x) ALT SINIRINDA'dir;
P90/max spread ile Backtest Muhendisi'nin ayrica yapacagi stres testinde bu esik kaybedilebilir
(Arastirmaci BULGU 11 SINIR notu). k=2,0 (cost-ratio 21,29x) bu riski onemli olcude azaltir,
bedeli ise daha yuksek "hicbiri" orani (%24,92, Hipotez 1'in ~1,9 kati) ve daha az efektif
ornek sayisidir (~75.000). Bu hipotez, Hipotez 1'in bir ALTERNATIFI degil, PARALEL bir
GUVENLIK-MARJI karsilastirmasidir — Backtest Muhendisi ikisini de calistirip cost-ratio/
veri-verimliligi degis-tokusunu GERCEK P&L uzerinden karsilastirabilir.

**YONTEM DETAYI:** Hipotez 1 ile BIREBIR AYNI feature seti/model ailesi/egitim disiplini,
SADECE k=1,5 yerine k=2,0. Ek olarak, bu varyantta "hicbiri" orani daha yuksek oldugu icin
(%24,92), OPSIYONEL bir ikinci alt-varyant olarak 3-sinifli etiket semasi (TP-once/SL-once/
hicbiri, hicbiri disarida birakilmadan) da denenebilir — bu, Karar 2'de secilen ikili semanin
"hicbiri az oldugunda" varsayimina dayandigi icin, hicbiri oraninin arttigi bu k degerinde
alternatif bir kontrol saglar. Bu alt-varyant ZORUNLU DEGIL, Backtest Muhendisi'nin takdirine
birakilmistir.

**GIRIS/CIKIS MEKANIZMASI:** Hipotez 1 ile ayni (olasilik esigi tabanli), sadece barrier k=2,0.

**SL/TP veya RISK YONETIMI:** SL=TP=k x ATR14(M15) = 2,0 x ATR14(giris ani), N=16 zaman-bariyeri
ayni. RR=1:1, HEDEF_WR=%60,0 ayni sekilde gecerli (R:R degismedigi icin). Lot/risk kurallari
Hipotez 1 ile ayni (`justin_gecmis_calisma.md`).

**DOGRULAMA IHTIYACI:** Hipotez 1 ile ayni protokol (purged walk-forward, test-tek-kullanim).
Ek olarak: Bu varyantin ana amaci DUYARLILIK/GUVENLIK-MARJI karsilastirmasi oldugu icin,
Backtest Muhendisi raporunda Hipotez 1 (k=1,5) ile Hipotez 3 (k=2,0) SONUCLARI YAN YANA
(PF, WR, islem sayisi, maliyet-orani stres-testi sonucu) sunulmalidir — hangisinin daha
saglam/kararli oldugu bu karsilastirmadan cikarilmalidir.

**RISKLER:** Hipotez 1'in riskleriyle buyuk olcude ORTAK (overfitting, veri sizintisi, canliya-
gecebilirlik) + ek olarak: daha az islem sayisi (dusuk sinyal frekansi), `justin_gecmis_calisma.md`
'daki T=500-islem varsayimina ulasmayi daha uzun takvim suresi gerektirebilir (bu bir
GECERSIZLIK degil, sadece DD-modelinin T=500 varsayiminin gerceklesme suresini uzatan bir
gozlemdir — Risk Analisti asamasinda not edilmeli).

**ONCELIK: 3-Dusuk (ikinci-tur/duyarlilik testi)** — Hipotez 1'in ana sonucu alindiktan sonra,
ozellikle Hipotez 1'in maliyet-orani stres-testinde (P90/max spread) sinirda kalmasi durumunda
DEGERLENDIRILMESI onerilir; Hipotez 1/2 ile AYNI ANDA/PARALEL calistirilmasi da mumkundur (ek
maliyet kucuktur, feature/pipeline paylasilir) ama sentez/karar agirligi Hipotez 1'dedir.

---

## BACKTEST MUHENDISI ICIN NOTLAR

1. **S1 (Maliyet-Orani On-Kontrolu):** Hipotez 1/2 icin k=1,5 (cost-ratio 15,97x medyan
   uzerinden) ON-KONTROLU GECER, ama bu ALT SINIRDA bir gecistir — `justin_backtest_
   onkontrol_standardi.md` Madde 2 geregi P90/max spread ile STRES-TESTI YAPILMASI ZORUNLU
   (Arastirmaci BULGU 11 SINIR, bu rapor Karar 1'de de tekrarlandi). Stres testinde esik
   kaybedilirse, Hipotez 3 (k=2,0, cost-ratio 21,29x, daha genis marj) devreye alinmali.
2. **S2 (Anti-Overfitting Protokolu) — TAMAMI ZORUNLU:** Purged/embargolu walk-forward (N=16-bar
   + ek embargo), test-seti tek-kullanim (esik/hiperparametre secimi TAMAMLANDIKTAN SONRA tek
   calistirma), feature-sizinti kontrol listesi (ozellikle MACD ham-deger kurali ve normalizasyon
   istatistiklerinin SADECE egitim setinden hesaplanmasi), basari kriterlerinin (HEDEF_PF=1,5,
   HEDEF_WR=%60,0 [RR=1:1 icin], HEDEF_DD=%20 kumulatif) EGITIMDEN ONCE yazili sabitlenmesi.
3. **DST/Saat-Eslesme (Backtest standardi Madde 1):** Feature Grubu 4 (saat/oturum) kullanildigi
   icin BAGIMSIZ DST/saat-eslesme dogrulamasi ZORUNLU — onceki H1/H2/H3 veya Arastirmaci
   turlerinden DEVRALINAMAZ.
4. **SL/TP otomatik tasima YOK (Backtest standardi Madde 3):** Bu rapordaki N=16/k=1,5 (ve
   k=2,0 varyanti) BU YAKLASIMA OZELDIR, onceki kural-tabanli H1/H2/H3 hipotezlerinin SL/TP
   degerlerinden BAGIMSIZDIR.
5. **Kutuphane on-kosulu (Karar 4):** Ana teste baslamadan once pandas/lightgbm/xgboost/
   scikit-learn kurulumu dogrulanmali/saglanmali; bu adim GORUNUR sekilde raporlanmali.
6. **Etiket/yon cercevesi (Karar 2):** Model dogrudan yon (yukari-bariyer-once/asagi-bariyer-
   once) tahmin ettigi icin ayri bir kural-tabanli entry-tetikleyici KULLANILMAMALI — model
   olasilik ciktisi + esik = tam giris/cikis kararı.
7. **Governance (bilgi amacli):** Bu, ML ailesinin ILK backtest turudur; S3 governance esigi
   (2 tam tur ayni olumsuz paternle biterse Ertan onayi) bu turda henuz islemez.

---

## IZOLASYON TEYIDI

- Bu rapor icin MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json, milagold_trades.json,
  lisa_performance.json, stratejici_gold_gecmis_calisma.md, positions_status.json vb.) okunmadi
  veya referans alinmadi — ne veri/parametre kopyalama ne de format/sablon referansi icin.
- Rapor formati, bu Stratejist'in sistem promptundaki (`stratejici_system_prompt.md`) genel
  sablondan ve Justin'in KENDI onceki Stratejist raporlarindan (ayni proje ici sureklilik,
  izolasyon disi) turetildi.
- Calisma yalniz `C:\MilaYatirim\Justin\` dizinindeki girdi dosyalarina (Arastirmaci ML raporu,
  `justin_gecmis_calisma.md`, `justin_ml_anti_overfitting_protokolu.md`,
  `justin_backtest_onkontrol_standardi.md`) dayandi; tek dis veri kaynagi (dolayli, Arastirmaci
  uzerinden) XM/MT5 GOLD sembolüdür.
- Bu raporda kullanilan tum kavramlar (LightGBM/XGBoost, triple-barrier, purged walk-forward,
  ATR/RSI/MACD/confluence) genel/kamuya-acik ML/finans kavramlaridir; MilaGold'a ozel hicbir
  esik/parametre/format bu rapora TASINMADI.

---

## SONUC / ONAY NOKTASI

Bu rapor bir hipotez/tasarim ciktisidir, canli sisteme/hesaba hicbir etkisi YOKTUR (Justin
arastirma/demo-oncesi asamada, gercek hesap yok). STOP-genis/bilgi-notu kategorisi — Ertan
onayi gerekmez; Orkestrator rapor tamamlaninca Telegram bilgi notu + Orkestrator_Loglar kaydi
dusecektir. Bir sonraki adim: **Backtest Muhendisi**, Hipotez 1'i (ve olanak varsa paralel
olarak Hipotez 2/3'u) yukaridaki notlar dogrultusunda dogrulamalidir.
