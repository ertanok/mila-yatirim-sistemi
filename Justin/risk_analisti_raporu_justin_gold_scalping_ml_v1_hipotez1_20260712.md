=== RISK ANALIZI RAPORU ===
Hipotez        : LightGBM Ikili Yon-Tahmini Modeli (N=16 M15-bar / k=1,5xATR14-M15) — HIPOTEZ 1
Yaklasim Turu  : Makine Ogrenmesi — Gradient Boosting (LightGBM, binary classifier) — Justin/ML
                 ailesinin ILK Risk Analisti turu (kural-tabanli H1/H2/H3'ten AYRI metodoloji)
Tarih          : 2026-07-12
KARAR          : RED

---

## ON-NOT — BAGIMSIZ DOGRULAMA

Bu degerlendirme oncesinde Backtest Muhendisi'nin raporu (`backtest_muhendisi_raporu_
justin_gold_scalping_ml_v1_hipotez1_20260712.md`) ile ham cikti dosyasi (`backtest_ml_v1_
hipotez1_output.json`) satir satir karsilastirildi: walk-forward AUC degerleri (fold 1-4:
0,4938/0,5122/0,5251/0,4990), final model ic-validasyon AUC'u (0,4990, best_iteration=1), TEST
AUC'u (0,5170), esik-kalibrasyonu aday tablosu (0,55/0,45 icin LONG n=132/WR-proxy=0,6894, SHORT
n=78/WR-proxy=0,5641), S1 oranlari (medyan 15,97x / P90 11,91x) ve PRIMARY/SUPPLEMENTARY islem
sayilari (ikisi de 0) — HAM JSON ile RAPOR arasinda hicbir sayisal tutarsizlik bulunamadi. Rapor
guvenilir kaynak olarak kabul edildi; asagidaki 8 kontrol kendi bagimsiz yorumumla uygulanmistir.

Ayrica: Orkestrator cagrisindaki gorev-takip "hata" etiketi notu goz ardi edildi, sadece rapor
ICERIGI degerlendirildi (talimat geregi). Yan not (karari etkilemez): `justin_gecmis_calisma.md`
dosyasinin basinda "14 Temmuz 2026" tarihli bir olusturma/onay kaydi var, ancak bugunun tarihi
12 Temmuz 2026 olarak bildirildi — bu bir tarih-tutarsizligi gibi gorunuyor, Orkestrator'un
bilgisine sunulur, ama hedef/parametre degerlerini (HEDEF_PF=1,5/HEDEF_WR=%60/HEDEF_DD=%20/
kasa=2000 USD) etkilemiyor, bu degerlendirmeyi degistirmez.

Hedef kriterler (kaynak: `justin_gecmis_calisma.md`): HEDEF_PF=1,5 | HEDEF_WR=%60,0 (RR=1:1) |
HEDEF_DD=%20 kumulatif | kasa=2.000 USD | islem-basi risk=%1 ust sinir | lot=0,01 baslangic.

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik : KIRMIZI** → Gorulmemis veri (TEST, tek-kez, n=17.833 siniflandirma
ornegi) icinde tetiklenen islem sayisi = **0**. Bu, kontrol listesindeki "OOS islem sayisi < 15 ise
sonuc anlamsiz" esiginin cok altinda — otomatik olarak anlamsiz/olculemez bir sonuc. Egitim
tarafinda gercek bir trade-bazli backtest yok; onun yerine esik-kalibrasyonu OOF-havuzunda
(4 farkli fold modelinin havuzlanmis tahminleri uzerinde) n=210 aday-islem (132 long + 78 short)
bulunuyor — ama bu, TEK bir modelin performansini degil 4 FARKLI modelin (best_iteration
1/6/4/1) karisik havuzunu temsil ediyor, dolayisiyla klasik "egitim islem sayisi" tablosuna
dogrudan uygulanamaz (yanlis guven verir). Ek olarak (model-tabanli ozel not): tek random_state
(42) kullanildi, coklu-seed tekrarlama yapilmadi — LightGBM gradient boosting icin RL kadar
kritik olmasa da, sonuc zaten rassal-sinira bu kadar yakinken tek-seed sonucuna guvenmek riskli.

**[2] Egitim/Gorulmemis Bozulma : KIRMIZI** → Klasik PF Bozulmasi/WR Farki hesaplanamiyor
(her iki tarafta da gercek PF/WR "tanimsiz", trade yok). Bunun yerine AUC uzerinden bakildi:
walk-forward ort. AUC=0,5075 vs TEST AUC=0,5170 — fark kucuk (0,0095), yani klasik "egitimde
iyi/testte kotu" ORTIME (overfitting) DESENI YOK. Ancak bu iyi haber degil: **her iki taraf da
rassal-seviyeye (0,50) bu kadar yakinken**, model hicbir donemde anlamli bir yon-tahmin sinyali
tasimiyor demektir — Muhendis'in "TUTARLI ZAYIFLIK" tanimlamasina katiliyorum. Karar
Cercevesi'ndeki "Gorulmemis veri PF, hedefin belirgin altindaysa RED" kuralinin en agir hali:
PF hedefin altinda degil, PF hic OLCULEMIYOR — bu daha zayif bir durum, otomatik KIRMIZI.
Ek bulgu: final model feature-onem tablosunda ATR/trend/confluence gibi Stratejist'in
"ZORUNLU" isaretledigi ana feature gruplari neredeyse SIFIR agirlik aliyor (atr14_m15=0,
m15_trend=0, confluence_flag=0, h1_trend_aligned=0) — model pratik olarak anlamli hicbir
iliski ogrenmemis, best_iteration=1 (tek agac) bunu dogruluyor.

**[3] Monte Carlo (%5 DD) : KIRMIZI** → Uygulanamadi (islem_logu_PRIMARY_tam ve
islem_logu_SUPPLEMENTARY_tam ikisi de BOS dizi, n=0). Monte Carlo'nun kendisi degil, Monte
Carlo'nun YAPILAMAMASININ NEDENI (hic islem yok) burada kirmizi bayrak — "olcum yoklugu",
"dusuk risk" ile karistirilmamali.

**[4] Pes Pese Kayip : KIRMIZI** → Ayni nedenle hesaplanamadi (n=0 islem, ne gercek ne teorik
pes-pese kayip serisi kurulabilir). Kasa/risk parametreleri (2.000 USD, %1) bu asamada
uygulanamaz durumda.

**[5] Kar Konsantrasyonu : KIRMIZI** → Ayni nedenle hesaplanamadi (0 islem → "en iyi 3/10 islem"
tanimsiz). Not: bu, "dagilim saglikli" anlamina GELMEZ — olcumun kendisi yok.

**[6] Kirilim Analizi : N/A** → Rapor bu hipotez turu icin seans/gun/kosul bazli bir kirilim
tablosu icermiyor (0 islem oldugu icin zaten kirilim de anlamli olamazdi). N/A olarak
isaretleniyor, atlanmiyor.

**[7] Parametre/Model Hassasiyeti : KIRMIZI** → S2 protokolu geregi hiperparametre grid-search
BILINCLI olarak yapilmadi (arama uzayini genisletip overfitting riskini artirmamak icin) — bu
kismen dogru bir tercih, ama beraberinde iki somut, TEST-EDILMEMIS/DOGRULANMAMIS risk birakiyor:
(a) `best_iteration=1` — fold 1 ve 4'te ve final modelde erken durma SADECE 1 turda devreye
girdi; model pratikte tek bir sig agac, bu son derece kirilgan bir egitim durumu (learning_rate/
early_stopping ayarlari veya n_estimators farkli secilseydi sonuc degisebilirdi, hic test
edilmedi). (b) Muhendis'in kendisinin isaretledigi bir YONTEMSEL TUTARSIZLIK: esik-kalibrasyonu
4 FARKLI fold modelinin (best_iteration 1/6/4/1, yani farkli olasilik-yayilim karakterinde)
HAVUZLANMIS OOF tahminleri uzerinden yapildi, ama CANLIDA/TESTTE kullanilacak TEK final model
en-dar-yayilimli fold'larla (1/4, best_iteration=1) ayni karakterde — bu, esik-kalibrasyonunun
neden OOF'ta 210 islem uretip final model TEST'inde 0 islem urettigini aciklayan olasi kok-neden.
Bu bir "hipotetik hassasiyet sorusu" degil, ZATEN GOZLEMLENMIS bir tasarim kusuru — bu yuzden
"TEST YOK" degil KIRMIZI olarak isaretliyorum. Backtest Muhendisi'nin bunu duzeltme yetkisi
olmadigini dogru tespit etmis olmasi, riski ORTADAN KALDIRMAZ — Stratejist'e somut olarak
iletilmesi gerekiyor (asagida).

**[8] Gercek Hayat Duzeltmesi : KIRMIZI** → 0 islem uzerinden slipaj/psikoloji duzeltmesi
uygulanacak bir Net Kar/PF yok (Duzeltilmis Net Kar = 0 - 0 - 0 = 0, anlamli bir duzeltme degil).
Gercek hesapta bu hipotezin MEVCUT esik/model haliyle hicbir islem uretmeyecegi, dolayisiyla ne
kar ne zarar getirmeyecegi (firsat maliyeti haric) anlamina gelir.

---

## --- OZET ---

**Guclu Yanlar:**
- Metodoloji saglam: purged/embargolu walk-forward (4 fold), test-seti tek-kullanim kurali,
  feature-sizinti kontrol listesi tam teyit edilmis, DST/saat-eslesme bu ML hattı icin bagimsiz
  yeniden dogrulanmis — S2 protokolune UYUM tam.
- Tekrar-uretilebilirlik kanitlanmis: script iki kez calistirildi (tani-blogu eklenerek), BIREBIR
  AYNI deterministik sonuclar uretti — bu bir metodoloji/altyapi guveni verir (ML hattinin
  kendisi kararli calisiyor, sorun rastgelelikte degil).
- Egitim(walk-forward) ve TEST AUC'leri birbirine yakin — klasik "egitimde ezberleme"
  (overfitting) DESENI yok; asagidaki zayiflik "sahte basari" degil, durust/tutarli bir
  basarisizlik olarak raporlanmis.
- Backtest Muhendisi kendi yetkisi disindaki bir yontemsel sorunu (OOF-havuz vs final-model
  tutarsizligi) ORTUP GECMEDEN acikca isaretlemis — bu seffaflik Risk Analisti acisindan degerli.

**Zayif Yanlar / Riskler:**
- Modelin ayirt edici gucu (AUC~0,50-0,52) neredeyse tam rassal — hem egitimde hem testte.
- Final model pratik olarak tek agac (best_iteration=1), feature-onem tablosunda ana feature
  gruplari (ATR/trend/confluence) sifira yakin agirlikta — model anlamli bir sinyal ogrenmemis.
- Esik-kalibrasyonu (OOF-havuz) ile final model (tek model) arasinda dagilim uyusmazligi —
  kalibre edilen esige (0,55/0,45) final model TEST'te HICBIR ZAMAN ulasamiyor (p_test max=0,5304).
- Sonuc olarak 0 islem: PF/WR/DD olculemedi, hedef karsilandi/karsilanmadi denemez.
- S1 maliyet-orani P90-stres testinde esik kaybediliyor (11,91x < 15,0x) — model calissaydi bile
  yuksek-spread anlarinda marj dar.
- Hicbir Monte Carlo/pes-pese-kayip/kar-konsantrasyonu olcumu YAPILAMADI — bu kontrollerin
  "GECTI" cikmasi degil, hic yapilamamis olmasi ayri bir risk katmanidir.

---

## --- KARAR GEREKCE ---

Bu hipotez, HEDEF_PF/HEDEF_WR/HEDEF_DD kriterlerinin hicbirini "karsiladi" ya da "karsilamadi"
diye degerlendirilemez — TEST setinde tek bir islem bile tetiklenmemistir (n=0), ve bunun bir
kod/veri hatasi degil modelin kendi dogrulanmis/deterministik davranisi oldugu bagimsiz olarak
teyit edilmistir (raw JSON capraz kontrolu dahil). Bagimsiz kontrol listemin 8 maddesinden 6'si
(1,2,3,4,5,8) dogrudan bu olcum-yoklugu nedeniyle KIRMIZI, 7. madde (parametre/model hassasiyeti)
ise zaten GOZLEMLENMIS bir yontemsel tutarsizlik (esik-kalibrasyonu OOF-havuz vs final-model)
nedeniyle KIRMIZI. Karar Cercevesi'ndeki RED kriterlerinden en az ikisi acikca saglaniyor:
"gorulmemis veri PF/WR/DD, hedefin cok altinda/olculemez" ve "modelin AUC'u rassal-seviye,
feature-onem tablosu anlamli sinyal gostermiyor". Bu, Backtest Muhendisi'nin RED kararini
bagimsiz olarak DOGRULAR — iki farkli degerlendirme yontemi (protokol-uygulamasi vs 8-kontrol
cercevesi) ayni sonuca varmistir.

---

## --- STRATEJISTE GERI BILDIRIM ---

1. **Esik-kalibrasyon yontemi duzeltilmeli:** Kalibrasyon SADECE final modelin kendi OOF
   tahminlerinden (ya da en azindan final modelle AYNI egitim-boyutu/karakterdeki bir fold'dan)
   yapilmali — 4 FARKLI best_iteration'li (1/6/4/1) modelin havuzlanmis tahminleri uzerinden
   esik secmek, final modelin gercekte hicbir zaman ulasamayacagi bir esik uretebiliyor (bu tur
   tam olarak bunu gozlemledi). Bu duzeltilmeden bir sonraki tur da ayni riski tasir.
2. **Model ogrenme kapasitesi sorgulanmali:** best_iteration=1 (pratikte tek agac) ve
   ATR/trend/confluence gibi ana feature gruplarinin sifira yakin agirligi, mevcut N=16/k=1,5
   etiket tanimi + 23-feature setinin bu haliyle anlamli bir sinyal tasimadigina isaret ediyor.
   Ogrenme oranı/early-stopping ayarlarinin (S2 kapsaminda kalarak, dar bir aralikta) yeniden
   gozden gecirilmesi veya farkli bir etiket/N-k kombinasyonunun (Hipotez 3, k=2,0) test
   edilmesi onerilir.
3. **S1 P90-stres testi hatirlatmasi:** k=1,5 medyan-spread'de esigi zar-zor geciyor (15,97x)
   ama P90-stres testinde kaybediyor (11,91x<15,0x) — Hipotez 1 RED ciktigina gore, Hipotez 3
   (k=2,0, cost-ratio 21,29x, daha genis marj) bir sonraki tur icin oncelikli degerlendirilmeli.
4. **Hipotez 2 (XGBoost) calistirilmasi degerlendirilmeli:** Ayni feature/etiket ile farkli bir
   model ailesinin de rassal-seviyede kalip kalmadigini gormek, sorunun "LightGBM'e ozgu"
   mu yoksa "feature/etiket tanimina ozgu" mu oldugunu ayirt etmeye yardimci olur.
5. **Arastirmaci'ya geri-bildirim onerisi:** AUC'nin (~0,50-0,52) ve feature-onem tablosunun
   (ana gruplar sifira yakin) birlikte gosterdigi tablo, mevcut feature setinin (BULGU 1-9)
   yeterli sinyal tasimadigi izlenimini guclendiriyor — bir sonraki arastirma turunde farkli/ek
   feature aileleri (ornegin mikro-yapi, farkli zaman pencereleri) dusunulmesi Stratejist'e
   onerilir.

---

## --- KULLANICIYA ---

Justin projesinin ilk yapay-zeka (makine ogrenmesi) tabanli deneme sonucu incelendi ve
onaylanamadi (KARAR: RED). Model, gecmis veriden fiyatin yon-tahminini ogrenmeye calisti ama
hem egitim hem de hic gormedigi (gelecege benzer) veri uzerinde tahminleri neredeyse yazi-tura
atmakla ayni seviyede kaldi — yani model, aslinda anlamli bir "sinyal" bulamadi. Bunun sonucu
olarak, gercek hesaba benzer test doneminde model hicbir zaman islem acacak kadar "kendinden
emin" olmadi (0 islem) — bu iyi ya da kotu bir kar/zarar degil, olcemedigimiz bir bosluk, ve
bosluk varken "basarili" denemez. Ayrica Muhendis, esik belirleme yonteminde kucuk ama onemli
bir tutarsizlik da tespit etti; bu, sonraki denemede duzeltilmesi gereken bir nokta. Ozetle: bu
ilk ML denemesi bu haliyle canliya/ilerki asamaya gecmeye hazir degil, ama sistemin kendisi
(test surecleri, tekrar-uretilebilirlik) saglikli calisiyor — sorun surecte degil, bu spesifik
modelin/etiket tanimin fiyat hareketini tahmin etmekte yetersiz kalmasinda. Stratejist'e somut
duzeltme onerileri iletildi (esik-kalibrasyon yontemi, farkli parametre varyanti Hipotez 3,
ikinci model ailesi Hipotez 2).
