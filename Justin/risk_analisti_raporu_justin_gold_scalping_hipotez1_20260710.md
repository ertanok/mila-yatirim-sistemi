=== RiSK ANALiZi RAPORU ===
Hipotez        : Seans-Filtreli Asimetrik Ortalamaya-Donus (Mean-Reversion) — HIPOTEZ 1
Proje          : PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi), Yol1 pipeline 4/4 (son adim)
Yaklasim Turu  : Kural-tabanli (SMA20 +/- k*std sapma filtresi + ATR-bazli risk yonetimi)
Tarih          : 2026-07-10
KARAR          : **RED**

---

## ON-NOT — EKSIK BILGI (Orkestrator'a/Ertan'a iletilmek uzere)

Bu, Justin projesi icin ILK Risk Analisti turu oldugundan, asagidaki proje-ozel bilgiler
henuz tanimlanmamis ve bana saglanmadi:

- **HEDEF_PF / HEDEF_WR / HEDEF_DD** — Stratejist'in bu proje icin belirledigi basari kriterleri
  (Gold'daki `stratejici_gold_gecmis_calisma.md` benzeri bir "Justin gecmis calisma" dosyasi yok)
- **Kasa buyuklugu / islem basina risk / lot buyuklugu** — Justin'in canli hesabi henuz yok
  (CLAUDE.md: "Gelistirme — Beklemede", hesap tipi belirlenmedi)

Bu eksiklik nedeniyle KONTROL 4 ve KONTROL 8'deki dolar-bazli hesaplamalar YAPILMADI —
yalniz oransal/yuzde-bazli degerlendirme yapildi (kendi sistem promptumun kurali geregi:
"Hedef/parametre uydurma"). Ancak asagida gorulecegi gibi, KONTROL 2 ve KONTROL 6/7'de ortaya
cikan sonuc o kadar acik ki (ana konfigurasyon ve tarama kombinasyonlarinin neredeyse tamaminda
VE 6 walk-forward penceresinin TAMAMINDA profit factor 1'in altinda), bu eksik bilgiler karari
degistirmiyor: **PF<1, hangi hedef PF belirlenirse belirlensin (hicbir mantikli proje PF hedefini
1'in altina koymaz), zaten karsiz/zarar eden bir sistem demektir.**

Ayrica: Backtest Muhendisi'nin raporunda **tam islem logu paylasilmamis** (boyut nedeniyle
699 islemden yalniz 50 ornek — ilk 25 + son 25 — tutulmus). Bu, KONTROL 3 (Monte Carlo) ve
KONTROL 5'in (kar konsantrasyonu) tam/kesin sekilde hesaplanmasini ENGELLEDI. Bu iki kontrol
icin sonuc kalitatif/kismi kaldi ve Muhendis'ten tam log istenmesi gerektigi asagida ayrica
belirtildi.

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik**: GECTI → Egitim/IS islem sayisi 486 (>=150 esigi asiyor, "Guclu"
kategorisi). OOS islem sayisi 213 (>=15 esiginin cok uzerinde, anlamli). En dar alt-kirilim
(k=2,5 OOS, n=88) sinirda ama tek basina karar dayanagi olarak kullanilmiyor — Muhendis de
bunu belirtmis. Walk-forward 6 penceresi ~17 ay boyunca 100-130 islem araliginda nispeten esit
dagilmis (tek bir kisa/dar trend doneminden gelen bir carpitma yok). Model-tabanli/stokastik
yontem olmadigindan (kural-tabanli) seed tekrari N/A.

**[2] Egitim/Gorulmemis Bozulma**: KIRMIZI → PF bozulmasi = Egitim PF (0,774) / OOS PF (0,96) =
**0,806**. Bu deger klasik "IS iyi, OOS kotu" overfitting paterninin **TERSI** — IS aslinda
OOS'tan DAHA KOTU. WR farki = 46,91% - 49,3% = -2,39 puan (esik altinda, kirmizi bayrak degil).
DD degisimi noktasal olarak OOS'ta daha dusuk (fiyat seviyesi degistigi icin puan bazinda dogrudan
karsilastirma sinirli). **Ancak asil kirmizi bayrak farkli bir yerden geliyor: hem IS (0,774) hem
OOS (0,96) profit factor DEGERI 1'IN ALTINDA.** Bu, klasik "egitimde ezberledi, gorulmemiste
cozuldu" tipi bir overfitting degil — **strateji ne egitimde ne de gorulmemis veride hicbir zaman
net pozitif olmamis.** Bu, overfitting'den farkli ama esit derecede ciddi bir bulgu: gercek bir
edge yoklugu. Hedef PF her ne olursa olsun (proje ozel deger tanimlanmamis olsa da), PF<1 =
zarar eden sistem demektir, dolayisiyla "gorulmemis veri PF hedefin belirgin altinda" kriteri
fiilen saglanmis sayilir.

**[3] Monte Carlo (%5 DD)**: KIRMIZI/VERI YETERSIZ → Tam islem logu saglanmadigi icin (699
islemden yalniz 50 ornek), sistem promptumdaki 500-shuffle Monte Carlo simulasyonu TAM VE DOGRU
olarak calistirilamadi — bu bir veri eksikligi, Muhendis'ten tam log istenmesi gerekiyor. Kalitatif
degerlendirme: toplam net sonuc negatif oldugu icin (tum donem net -39.408,21 puan, 699 islem),
kar/zarar sirasi ne sekilde karistirilirsa karistirilsin (shuffle) NIHAI toplam sonuc HER ZAMAN
ayni negatif deger olarak kalir — sadece yol (max drawdown paterni) degisir. Negatif beklentili
(expectancy) bir sistemde %5'lik en kotu senaryonun oransal drawdown'i yapisal olarak yuksek
cikar; bu nedenle KONTROL 3'un GECTI/UYARI cikma olasiligi dusuktur. Kesin yuzde deger
hesaplanamadi ama yon acik: olumsuz.

**[4] Pes Pese Kayip**: UYARI/VERI YETERSIZ → Teorik beklenti (tum-donem WR=%47,64):
log(0,05)/log(1-0,4764) = log(0,05)/log(0,5236) ≈ **4,6 → ~5 ardisik kayip**. Gorunen 50 islemlik
ornekte (699'un yalniz bir kismi) en az **4 ardisik kayip serisi** goruluyor (2026-06-24 tarihli
blok, saat 15-16, art arda 4 SL), bu teorik beklentiye yakin/uyumlu ama ORNEK TAM DEGIL — gercek
maksimum seri (699 islem uzerinden) daha yuksek olabilir, tam log olmadan kesinlestirilemiyor.
**Dolar/yuzde etkisi hesaplanamadi** — kasa buyuklugu ve ortalama kayip tutari (USD) proje
baglaminda tanimlanmamis (Justin'in canli hesabi yok); varsayim uydurulmadi, bilgi Orkestrator'a/
Ertan'a iletiliyor.

**[5] Kar Konsantrasyonu**: VERI YETERSIZ → Tam islem logu olmadigi icin "en iyi 3/10 islem, toplam
karin yuzde kaci" hesabi KESIN olarak yapilamiyor — bu Muhendis'ten istenecek bir eksik (tam
islem_logu, boyut kisitlamasi asilarak veya ozetlenmis dagilim istatistigi olarak). Not: zaten
tum-donem net sonuc negatif oldugu (kar degil zarar) icin, bu kontrolun "saglikli dagilim" sonucu
vermesi durum degistirmez — strateji zaten toplamda para kaybediyor.

**[6] Kirilim Analizi (Seans)**: KIRMIZI → Seans kirilimi mevcut (filtresiz / birincil 15-18 /
birincil+ikincil 15-18+3-4). **Hicbir dilimde profit factor 1'in uzerine cikmiyor**:
filtresiz PF 0,876 (IS 0,857 / OOS 0,902), birincil-15-18 PF 0,843 (IS 0,774 / OOS 0,96),
birincil+ikincil PF 0,865 (IS 0,822 / OOS 0,937). Islem sayilari hepsinde >=5 (yeterli), yani
"anlamsiz kucuk ornek" sorunu yok — sonuc guvenilir sekilde negatif. Ayrica **walk-forward'un
6 penceresinin TAMAMI da PF<1** (0,684-0,993 araligi) — tek bir donem/rejimin sonucu carpitmasi
degil, ~17 ay boyunca TUTARLI negatif performans. Bu, stratejinin herhangi bir seans/donem
kosulunda surdurulebilir bir edge sergilemedigini gosteriyor.

**[7] Parametre Hassasiyeti**: KISMEN TEST EDILDI → Muhendis, sistem promptumun onerdigi
"parametre +/- bir adim" testini fiilen zaten kapsamli yapmis: k-tarama (1,5/2,0/2,5 → PF hepsi
<1: 0,857/0,843/0,728), giris yontemi (next_open/close → PF 0,843/0,88, ikisi de <1), cikis
yontemi (N-bar-zaman/ATR-TP-SL/combined → PF 0,953/0,846/0,843), detrend (ham/detrended-long/
detrended-simetrik → PF 0,843/0,86/0,82). **Sonuc genis bir parametre bolgesinde tutarli sekilde
negatif** — bu aslinda "kirilgan bir esik noktasina rastlama" (overfit bir nokta) ihtimalini
ZAYIFLATIYOR, cunku sonuc esige cok yakin degil, genis bir bolgede sistematik olarak kotu.
Test EDILMEYEN parametreler: SMA penceresi (sabit 20), ATR periyodu (sabit 14), R:R orani
(sabit 1:1) hic degistirilmedi — bu 3 parametrenin hassasiyeti bilinmiyor. Tek istisna:
"yalniz N-bar zaman-bazli cikis" varyanti OOS'ta PF=1,238 (IS'te PF=0,79) — Muhendis'in
kendisinin de belirttigi gibi bu **OVERFITTING RISKI** tasiyor: walk-forward ile dogrulanmadi,
tek bir 70/30 bolmeye dayaniyor, ve tam-donem PF'si (0,953) yine de 1'in altinda kaliyor.
Bu istisnayi guvenilir bir pozitif bulgu olarak KABUL ETMIYORUM.

**[8] Gercek Hayat Duzeltmesi**: KIRMIZI → Tum-donem: PF=0,843, Net=-39.408,21 puan (699 islem).
Bu degerlerden GP/GL turetilebilir: PF=GP/GL=0,843 ve GP-GL=-39.408,21 → GL≈250.975 puan,
GP≈211.567 puan. Slipaj: backtest zaten bar-kapanis broker-spread'ini (ortalama 33,05 puan/islem)
maliyet olarak icermis durumda; ek bir slipaj varsayimi projeden/gorevden gelmedigi icin
UYDURULMADI (cift sayma riskinden kacinmak icin de dogru olan budur). Psikoloji/uygulama payi:
proje ayrica belirtmedigi icin muhafazakar varsayilan (%10-15) uygulaniyor — ANCAK net sonuc
zaten NEGATIF oldugundan, bu duzeltme kari azaltmiyor, **zarari buyutuyor**: yaklasik
Duzeltilmis Net ≈ -39.408,21 × (1+~0,125) ≈ **-44.300 puan civari**, Duzeltilmis PF **0,843'ten
daha da uzaklasarak ~0,75-0,80 bandina** iner (yaklasik, GP/GL kesin ayrimi olmadan tam
hesaplanamiyor — bu bir varsayim olarak isaretleniyor). **Sonuc: gercek hesapta durum
backtest'ten DAHA KOTU olacak**, zaten backtest'te PF<1.

---

## --- OZET ---

**Guclu Yanlar:**
- Ornekleme yeterli: IS n=486 (Guclu, 150+ esigi), OOS n=213 — istatistiksel olarak anlamsiz
  degil.
- Muhendis metodolojik olarak titiz calismis: ZORUNLU detrend testi yapilmis, saat-esleme/DST
  sorunu bagimsiz dogrulanmis ve acikca raporlanmis, 6 pencerelik walk-forward + genis parametre
  taramasi (k/giris/cikis) yapilmis. Izolasyon kurallarina tam uyum var.
- Sonucun genis bir parametre bolgesinde (k=1,5-2,5, giris/cikis varyantlari, detrend/ham)
  TUTARLI olmasi, "sansli bir noktaya rastlama" (klasik curve-fit) ihtimalini zayiflatiyor —
  yani sorun bir esik-optimizasyonu degil, stratejinin temel mantiginda.

**Zayif Yanlar / Riskler:**
- **Ana konfigurasyon ve nerdeyse TUM tarama kombinasyonlarinda profit factor 1'in altinda**
  (hem tum-donem hem IS hem OOS) — strateji temelde zarar ediyor.
- **6 walk-forward penceresinin 6'si da PF<1** (0,684-0,993) — tek donemlik bir talihsizlik degil,
  ~17 ay boyunca sistematik/tutarli negatif performans.
- ZORUNLU detrend testi, BULGU6 (17 aylik yon-onyargisi) fiyattan cikarildiktan SONRA bile
  edge'i pozitife DONDURMEDI (long-only PF 0,86/0,875, simetrik PF 0,82/0,806) — yani mean-
  reversion hipotezinin kendisi, trend-onyargisindan bagimsiz olarak dogrulanamiyor.
- Tek istisna (N-bar-zaman-cikis, OOS PF=1,238), Muhendis'in kendi ifadesiyle dogrulanmamis
  overfitting riski tasiyor (walk-forward yok, tek 70/30 bolme, IS'i hala <1).
- Saat-esleme/DST belirsizligi (kis aylarinda 15-18 filtresinin fiilen 1 saat kaymis olabilmesi)
  ayri bir metodolojik risk — ancak zaten sonuc PF<1 oldugu icin bu belirsizlik karari
  degistirmiyor (dogru saat de olsa strateji zarar ediyor gorunuyor).
- Tam islem logu saglanmadigi icin Monte Carlo (KONTROL 3) ve kar konsantrasyonu (KONTROL 5)
  tam olarak dogrulanamadi — bu bir raporlama eksikligi, karari tek basina belirlemiyor ama
  gelecek turlarda duzeltilmeli.
- Proje-ozel HEDEF_PF/HEDEF_WR/HEDEF_DD ve kasa buyuklugu/risk parametreleri henuz
  tanimlanmamis (Justin icin ilk Risk Analisti turu).

---

## --- KARAR GEREKCE ---

Ana konfigurasyon ve k/giris-yontemi/cikis-yontemi/detrend taramalarinin neredeyse TAMAMINDA
hem tum-donem hem IS hem OOS profit factor 1'in altinda olculmustur; daha da onemlisi 6 walk-
forward penceresinin TAMAMI da (0,684-0,993 araligi) 1'in altindadir — bu tek bir donemin
carpitmasi degil, ~17 ay boyunca tutarli/sistematik bir zarar paternidir. ZORUNLU detrend testi,
17-aylik trend-onyargisini fiyattan cikardiktan sonra bile edge'i pozitife donduremedi. Tek
istisna (N-bar-zaman-cikis, OOS PF=1,238), Muhendis'in kendisince de dogrulanmamis/overfitting-
riskli olarak isaretlenmis (walk-forward yok, IS hala <1). Proje-ozel bir HEDEF_PF sayisi henuz
tanimlanmamis olsa da, PF<1 evrensel olarak "karsiz sistem" anlamina gelir — bu tek basina RED
icin yeterli bir gerekcedir; gercek-hayat duzeltmesi (KONTROL 8) durumu daha da kotulestirmektedir.

---

## --- STRATEJISTE GERI BILDIRIM ---

Bu hipotez (Seans-Filtreli Asimetrik Mean-Reversion, HIPOTEZ 1) mevcut haliyle gercek hesaba
hazir DEGILDIR. Somut oneriler:

1. **Temel mantik yeniden gozden gecirilmeli.** SMA20 +/- k*std sapma + 1:1 R:R yapisi, genis bir
   parametre bolgesinde (k=1,5-2,5) ve 6/6 walk-forward penceresinde tutarli negatif PF veriyor —
   bu bir esik-ayari sorunu degil, olasi ki hipotezin kendisi (bu haliyle) bu piyasada/zaman
   dilimimde gecerli bir edge saglamiyor.
2. **Kazanma orani (%43-52 araligi, cogunlukla <%50) 1:1 R:R ile uyumsuz.** Ya R:R oranini
   degistirin (ornegin 1:1,5 veya asimetrik TP/SL), ya da giris filtresini kazanma oranini
   artiracak sekilde sikilastirmayi (ek confirmation) degerlendirin — ancak yeni bir filtre
   eklenirse yeniden TAM pipeline (Arastirmaci→Stratejist→Backtest→Risk) gerekir, sadece
   parametre kaydirma degil.
3. **N-bar-zaman-bazli-cikis varyantini AYRI bir hipotez olarak, walk-forward ile yeniden test
   ettirin** (Backtest Muhendisi'ne). Su an ki OOS PF=1,238 sonucu tek bir 70/30 bolmeye dayaniyor
   ve kendi IS'i (0,79) da <1 — guvenilir bir sinyal degil, ama tamamen goz ardi edilmemeli, ayri
   dogrulama gerekli.
4. **Saat-esleme/DST bulgusu** (kis aylarinda 15-18 filtresi fiilen kaymis olabilir) ayrica ele
   alinmali — VPS'in gercek DST davranisi teyit edilmeli, gerekirse saat-bazli filtreler mevsime
   gore ayarlanmali. Bu bulgu bu hipotezin RED kararini degistirmiyor ama Justin projesindeki
   TUM saat-bazli filtreler icin gecerli bir risk.
5. **Justin icin proje-ozel bir "gecmis calisma" dosyasi olusturulmali** (Gold'daki
   `stratejici_gold_gecmis_calisma.md` benzeri) — HEDEF_PF/HEDEF_WR/HEDEF_DD ve risk
   parametreleri (kasa buyuklugu, islem basina risk, lot buyuklugu) proje baslamadan
   netlestirilmeli; sonraki Risk Analisti turlari bu olmadan tam degerlendirilemez.
6. **Backtest Muhendisi'nden tam islem logu istenmeli** (699 islemin tamami, sadece 50 ornek
   degil) — Monte Carlo (KONTROL 3) ve kar-konsantrasyonu (KONTROL 5) analizlerinin tam
   yapilabilmesi icin gerekli.

---

## --- KULLANICIYA ---

Justin projesinin ilk stratejisi (Seans-Filtreli Ortalamaya-Donus fikri) test edildi ve sonuc
olumsuz cikti: neredeyse butun test kombinasyonlarinda ve gecmis 17 ayin altiya bolunmus HER
bir doneminde, strateji para KAYBEDIYOR (kazandigindan fazlasini kaybediyor — "profit factor"
denen kar/zarar orani surekli 1'in altinda kaldi, yani 1 birim kazanmak icin 1 birimden fazla
risk aliniyor). Bu tek bir kotu ay ya da sansli/sanssiz bir donemden kaynaklanmiyor — 17 ay
boyunca tutarli bir sekilde boyle. Ayrica farkli ayar denemelerinin (esik degerleri, giris/cikis
yontemleri) hemen hepsinde ayni sonuc cikti, yani "dogru ayari bulamadik" degil, fikrin
kendisinde bir sorun var gorunuyor. Bu nedenle bu hipotezi RED (reddedildi) olarak
degerlendiriyorum; canli/demo hesapta denenmemeli. Stratejist'e, hipotezi yeniden tasarlamasi
veya farkli bir yaklasim denemesi icin somut geri bildirim iletildi. Ayrica bu projenin (Justin)
henuz kendi hedef basari kriterleri (ne kadar kar/kayip beklentisi olmali) tanimlanmamis —
bunun ileriki analizler icin netlestirilmesi faydali olur.
