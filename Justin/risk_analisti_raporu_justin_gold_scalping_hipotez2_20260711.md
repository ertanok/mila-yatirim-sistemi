=== RiSK ANALiZi RAPORU ===
Hipotez        : Buyuk-Bar Ters-Yon/Fade — HIPOTEZ 2
Proje          : PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi), Yol1 pipeline 4/4 (son adim)
Yaklasim Turu  : Kural-tabanli (range-esikli buyuk-bar tespiti + ATR-bazli risk yonetimi)
Tarih          : 2026-07-11
KARAR          : **RED**

---

## ON-NOT — EKSIK BILGI VE METODOLOJI ADAPTASYONU (Orkestrator'a/Ertan'a iletilmek uzere)

Hipotez 1 turunde oldugu gibi, Justin projesi icin proje-ozel HEDEF_PF/HEDEF_WR/HEDEF_DD ve
kasa buyuklugu/islem basina risk/lot buyuklugu hala tanimlanmamis (Justin'in gecmis calisma
dosyasi yok, canli hesabi yok). Bu nedenle KONTROL 4 ve KONTROL 8'deki dolar-bazli hesaplamalar
YAPILMADI, yalniz oransal degerlendirme yapildi. Asagida gorulecegi gibi sonuc o kadar acik ki
(ana konfigurasyon + TUM tarama kombinasyonlari + 6/6 walk-forward penceresi + 18/18 ay PF<1
veya net<0) bu eksik bilgi karari degistirmiyor.

**Bu turde onceki turden (Hipotez 1) farkli olarak TAM islem logu mevcuttu** (2203 islemin
tamami, `islem_logu_tam`), bu sayede KONTROL 3 (Monte Carlo) ve KONTROL 5 (kar konsantrasyonu)
bu kez BAGIMSIZ VE TAM olarak yeniden hesaplandi (asagida bkz.), Muhendis'in ozet rakamlariyla
capraz kontrol edildi ve BIREBIR TUTARLI cikti (gross_profit 251.002,11 - gross_loss 449.882,06
= net -198.879,95, Muhendis'in rakamiyla tam eslesiyor).

**Monte Carlo metodoloji notu:** Kasa buyuklugu (baslangic_kasasi) tanimlanmadigi icin standart
promptumdaki "%-bazli oransal kasa" hesaplamasi dogrudan uygulanamadi. Bunun yerine islem
basina ortalama kayip buyuklugu (R = 346,33 puan/lot, kaybeden islemlerin ortalamasi) risk
birimi olarak kullanildi ve 500-shuffle simulasyonu R-katlari cinsinden calistirildi — bu,
kasa buyuklugunden bagimsiz, oransal bir olcum saglar (asagida KONTROL 3).

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik**: KIRMIZI → Ornek hacmi kendi basina fazlasiyla yeterli: IS
islem=1533 (>=150, "Guclu"), OOS islem=670 (>=15 esiginin cok uzerinde). Walk-forward'un 6
penceresi de 334-402 islem araliginda nispeten esit dagilmis (tek bir kisa/dar donemden gelen
carpitma yok). Model-tabanli/stokastik yontem olmadigi icin seed tekrari N/A. **ANCAK asil
kirmizi bayrak burada, hacimden degil, edge'in kendisinden geliyor:** Muhendis'in ONCE-KONTROL
olarak yaptigi binom/ki-kare testi, FIILEN ISLEM EDILEN alt-orneklemde (M5, seans 15-18)
buyuk-bar-sonrasi ters-yon oraninin **%48,86 oldugunu ve 0,50'den ISTATISTIKSEL OLARAK ANLAMLI
SEKILDE SAPMADIGINI (binom p=0,2234) gosteriyor.** Global (filtresiz) M5 orneklemde (%50,94,
p=0,0288) ve M1'de (%53,15, p<0,001) anlamli sapma olsa da, bu **uygulanan seans filtresiyle
birlikte tamamen kayboluyor.** Yani hipotezin dayandigi ham istatistiksel edge, gercekte
islem edilen populasyonda zaten YOK — bu, asagidaki tum negatif PF sonuclarinin neden
sasirtici olmadigini onceden isaret ediyor (tesadufi bir kotu ornekleme degil, yapisal bir
edge-yoklugu).

**[2] Egitim/Gorulmemis Bozulma**: KIRMIZI → PF bozulmasi = Egitim PF (0,517) / OOS PF (0,623)
= **0,830**. Bu esigin (1,6) cok altinda ve yon TERSI (IS, OOS'tan daha kotu) — yani klasik
"egitimde ezberledi, gorulmemiste cozuldu" tipi overfitting DEGIL. WR farki = %40,51 - %42,24
= **-1,73 puan** (esik altinda, bayrak degil). DD degisimi (islem-basi normalize): IS
133.794,60 puan / 1533 islem = 87,28 puan/islem; OOS 67.978,60 puan / 670 islem = 101,46
puan/islem → oran 1,16x (1,5x esiginin altinda, bayrak degil). **Asil kirmizi bayrak: HEM IS
(0,517) HEM OOS (0,623) profit factor DEGERI 1'IN ALTINDA** — strateji ne egitimde ne
gorulmemis veride hicbir zaman net pozitif olmamis. Overfitting'den farkli ama esit derecede
ciddi: gercek edge yoklugu, Kontrol 1'deki istatistiksel bulguyla tam tutarli.

**[3] Monte Carlo (R-katlari, kasa buyuklugu tanimsiz oldugu icin oransal risk-birimi
kullanildi)**: KIRMIZI BAYRAK → Tam islem logu (2203 islem) uzerinde 500-shuffle simulasyonu
BAGIMSIZ olarak calistirildi (R = 346,33 puan/lot, ortalama kaybeden islem buyuklugu):

| Metrik | Deger (R-katlari) |
|---|---|
| Medyan max drawdown | ~577 R |
| En kotu %5 (95. persentil) | ~585 R |
| En iyi %5 (5. persentil) | ~574 R |
| Tum 500 shuffle araligi | 574 R – 599 R |

**Kritik bulgu: 500 shuffle'in TAMAMI neredeyse AYNI buyuklukte agir drawdown ile sonucleniyor**
(574-599 R dar araligi, sadece ~4,3% varyasyon). Bunun sebebi, toplam beklenti o kadar derin
negatif (gross_loss 449.882 puan, gross_profit'in 251.002 puanindan ~1,79 kat fazla) ki, kar/
zarar sirasi nasil karistirilirsa karistirilsin sonuc pratik olarak DETERMINISTIK sekilde
kotu cikiyor — yani "sansli bir sira" ihtimali burada neredeyse yok. Herhangi bir makul
kasa/risk-yonetimi altinda (ihtiyatli bir hesap tipik olarak 20-30R'lik bir dususu bile
guclukle tolere eder), 574-599R'lik kesintisiz negatif suruklenme **hesabi pratik olarak
sifirlar/iflas ettirir.** Bu, sistem promptumdaki ">%35 = KIRMIZI BAYRAK" kategorisinin acikca
otesinde bir bulgu.

**[4] Pes Pese Kayip**: KIRMIZI/UYARI → Gercek max ardisik kayip (bagimsiz dogrulandi): **14
islem**. Teorik beklenti (tum-donem WR=%41,03): log(0,05)/log(1-0,4103) = log(0,05)/log(0,5897)
≈ **5,67**. **Gozlenen (14), teorik beklentinin (~5,67) yaklasik 2,5 kati** — saf rastgele/
bagimsiz-ozdes (iid) varsayimindan daha kotu bir kumelenme gosteriyor, negatif-egde ile
tutarli. Dolar/yuzde etkisi HESAPLANAMADI (kasa buyuklugu/lot Justin icin tanimsiz — varsayim
uydurulmadi). Oransal ifade: 14 ardisik kayip = ortalama kayip biriminin (R) 14 kati arka
arkaya — R-cinsinden bu, Kontrol 3'teki 574-599R'lik toplam drawdown'in kucuk ama gozle
gorulur bir kismini (~%2,4-2,5'ini) tek bir seride olusturuyor.

**[5] Kar Konsantrasyonu**: GECTI (ama sonucu kurtarmiyor) → Bagimsiz hesap (904 kazanan islem
uzerinden): en iyi 3 islem = brut karin **%2,70'i**, en iyi 10 islem = **%6,44'u** (Muhendis'in
rakamiyla birebir ayni) — her ikisi de %20 esiginin cok altinda, saglikli/dagilmis bir kazanc
profili. Ayrica **18 aylik kirilimin TAMAMINDA (18/18) net_pts NEGATIF** — pozitif net
gosteren tek bir ay bile yok, dolayisiyla "tek bir ay/hafta toplam karin %40'ini olusturuyor
mu" sorusu anlamsiz (olusacak bir "toplam kar" yok, toplam zaten zarar). Bu kontrol teknik
olarak GECTI (dagilim saglikli) ama bu, stratejinin toplamda para kaybettigi gercegini
degistirmiyor.

**[6] Kirilim Analizi (Teyit Ufku / Cikis Yontemi / Seans Filtresi / Walk-Forward / Aylik)**:
KIRMIZI → Raporlanan TUM kirilim boyutlarinda profit factor 1'in altinda kaliyor:
- Teyit ufku: t+1=0,558, t+2=0,631, t+3=0,675 — tumu <1 (islem sayisi da 2203→673'e dususe,
  potansiyel secim etkisiyle karisik degerlendirilmeli).
- Cikis yontemi: en iyisi bile (yalniz-zaman-N3) PF=0,912, <1.
- Seans filtresi: filtresiz 0,519, birincil-15-18 0,558 — ikisi de <1.
- Walk-forward: 6 pencerenin TAMAMI PF<1 (0,401-0,782 araligi) — tek donem carpitmasi yok,
  tutarli negatif.
- Aylik: 18/18 ay net negatif.
Islem sayilari her dilimde >=213 (en dar: t+3/OOS), yani "anlamsiz kucuk ornek" sorunu yok,
sonuc guvenilir sekilde negatif. Hicbir kirilim diliminde >=1 PF'ye ulasilamiyor.

**[7] Parametre Hassasiyeti**: KISMEN TEST EDILDI → Muhendis 3 boyutta (confirm_horizon,
cikis yontemi, seans filtresi) kapsamli tarama yapmis; sonuc bu 3 boyutun TUMUNDE tutarli
negatif — bu, "kirilgan bir esik noktasina rastlama" (klasik curve-fit) ihtimalini
ZAYIFLATIYOR. **Test EDILMEYEN parametreler:** BIGBAR_MULT (1,5x sabit tutuldu — gorev
talimatiyla bilinCli bir "overfitting guvenlik agi" karari, muhendis ihmali degil),
ATR_FRACTION (0,5 sabit), RR_RATIO (1:1 sabit) — bu 3 parametrenin hassasiyeti bilinmiyor.
Sonuc zaten genis bir bolgede (3 farkli tarama boyutu) sistematik olarak negatif oldugu icin
bu bilinmezligin karari degistirme olasiligi dusuk, ama tam kapsamli degerlendirme icin
kayitlara geciyor. **Ayrica:** Muhendis'in bu turde kendi ekledigi MAX_TICK_MISMATCH_SEC=60
parametresi — Stratejist tarafindan belirlenmemis bir muhendislik karari, ayrica onaylanmasi
gerekiyor (bkz. Stratejiste Geri Bildirim). Etkisi olcumsel olarak ihmal edilebilir (12.210
tick sorgusundan yalniz 2'si reddedildi, ~%0,016) ama governance acisindan not dusuluyor.

**[8] Gercek Hayat Duzeltmesi**: KIRMIZI → Tum-donem: PF=0,558, Net=-198.879,95 puan/lot
(2203 islem), GP=251.002,11, GL=449.882,06 (bagimsiz dogrulandi, Muhendis'in rakamiyla birebir
eslesiyor). Slipaj: giris tarafi zaten gercek tick-bazli bid/ask ile hesaplanmis
(ortalama toplam maliyet 45,99 puan/islem = spread + slipaj), EK bir slipaj varsayimi
UYDURULMADI (cift sayma riskinden kacinmak icin). Psikoloji/uygulama payi: proje ayrica
belirtmedigi icin muhafazakar varsayilan (%10-15, orta nokta %12,5) uygulaniyor — ANCAK net
sonuc zaten NEGATIF oldugundan bu duzeltme kari azaltmiyor, **zarari buyutuyor**:
Duzeltilmis Net ≈ -198.879,95 × 1,125 ≈ **-223.739,94 puan**, Duzeltilmis PF ≈
GP/(GL+ek_maliyet) = 251.002,11/(449.882,06+24.859,99) ≈ **0,529**. Duzeltme, sonucu daha da
kotulestiriyor — bu bir varsayim olarak isaretlenmistir (kesin dolar/lot rakami olmadan
yaklasik). **Sonuc: gercek hesapta durum backtest'ten DAHA KOTU olacak, zaten backtest'te
PF<1.**

---

## --- OZET ---

**Guclu Yanlar:**
- Ornekleme fazlasiyla yeterli: IS n=1533 (Guclu, 150+ esigi), OOS n=670, en dar alt-kirilim
  (t+3/OOS, n=213) bile yorumlanabilir sinirin uzerinde.
- Muhendis metodolojik olarak titiz: bu turde kritik bir KOD HATASI (tick-zaman-uyusmazligi,
  fiziksel olarak imkansiz slipaj) bagimsiz olarak tespit edilip duzeltilmis VE duzeltme
  sonucu "daha iyi" degil "daha kotu" cikmis (PF 0,867→0,558) — bu, sonucu iyi gostermeye
  calisan degil dogruya ulasmaya calisan bir muhendislik yaklasimi, guven artirici.
  saat-esleme/DST sorunu bagimsiz dogrulanmis, 6 pencerelik walk-forward + 3 boyutlu
  parametre taramasi + once-kontrol istatistiksel anlamlilik testi yapilmis.
- Bu turde TAM islem logu saglandigi icin (2203/2203) Monte Carlo ve kar konsantrasyonu
  BAGIMSIZ ve TAM olarak dogrulanabildi (Hipotez 1'deki eksiklik bu turde giderildi) — tum
  capraz kontroller Muhendis'in rakamlariyla birebir eslesti, veri butunlugu yuksek.
  Kar konsantrasyonu saglikli (top3 %2,70, top10 %6,44) — sonucun birkac buyuk islemden
  degil, genel/yaygin bir zarar deseninden geldigi anlasiliyor.
- Sonucun 3 farkli tarama boyutunda (teyit ufku, cikis yontemi, seans filtresi) VE 6/6
  walk-forward penceresinde tutarli olmasi, "sansli/sanssiz bir esik noktasina rastlama"
  (curve-fit) ihtimalini zayiflatiyor — sorun bir parametre ayari degil, hipotezin temel
  mantiginda.

**Zayif Yanlar / Riskler:**
- **Hipotezin dayandigi ham istatistiksel edge, fiilen islem edilen populasyonda (M5, seans
  15-18) ISTATISTIKSEL OLARAK ANLAMSIZ** (binom p=0,2234, %48,86 reversal orani) — global
  ornekte gorulen anlamli sapma (M5 %50,94/p=0,0288, M1 %53,15/p<0,001), uygulanan seans
  filtresiyle birlikte kayboluyor.
- **Ana konfigurasyon ve raporlanan TUM kombinasyonlarda (teyit ufku, cikis yontemi, seans
  filtresi) profit factor 1'in altinda** — en iyi tekil kirilim bile (yalniz-zaman-N3)
  PF=0,912 ile hala <1.
- **6 walk-forward penceresinin 6'si de PF<1** (0,401-0,782) ve **18 ayin 18'i de net negatif**
  — ~17 ay boyunca sistematik/tutarli zarar, tek donem carpitmasi degil.
- **Monte Carlo (bagimsiz, tam log uzerinde): 500 shuffle'in TAMAMI 574-599R araliginda agir
  drawdown ile sonucleniyor** — sonuc pratik olarak deterministik kotu, "sansli sira" ihtimali
  yok denecek kadar dusuk.
- Gercek max ardisik kayip (14), teorik beklentinin (~5,67) ~2,5 kati — kumelenme normalden
  fazla.
- Gercek-hayat duzeltmesi (psikoloji/uygulama payi) durumu daha da kotulestiriyor (PF
  ~0,558→~0,529).
- BIGBAR_MULT/ATR_FRACTION/RR_RATIO hic degistirilmedi (bilinCli guvenlik agi kararidir, ama
  hassasiyet bilinmiyor); MAX_TICK_MISMATCH_SEC=60 Muhendis tarafindan bu turde eklenen,
  Stratejist onayi bekleyen bir parametre.
- Saat-esleme/DST belirsizligi (Hipotez 1 ile ayni bulgu, bagimsiz tekrar dogrulandi) devam
  ediyor — kis aylarinda 15-18 seans filtresi fiilen kaymis olabilir.
- Justin projesi icin HEDEF_PF/HEDEF_WR/HEDEF_DD ve kasa buyuklugu/risk parametreleri hala
  tanimlanmamis (2. arka arkaya turde de ayni eksiklik).

---

## --- KARAR GEREKCE ---

Hipotezin temel dayanagi olan "buyuk-bar sonrasi ters-yon" edge'i, fiilen islem edilen
populasyonda (M5, seans-filtreli) istatistiksel olarak 0,50'den anlamli sekilde sapmiyor
(p=0,2234) — yani hipotez kendi uyguladigi filtreyle birlikte kendi temelini zayiflatiyor.
Bunun sonucu olarak ana konfigurasyon, raporlanan TUM tarama kombinasyonlari (teyit ufku,
cikis yontemi, seans filtresi), 6/6 walk-forward penceresi ve 18/18 ay net negatif/PF<1
cikmistir — bu bir donem/parametre carpitmasi degil, ~17 ay boyunca tutarli bir edge-yoklugu
paternidir. Bu turde bagimsiz olarak (tam islem logu uzerinden) yeniden calistirilan Monte
Carlo simulasyonu, 500 shuffle'in tamaminin 574-599R araliginda neredeyse degismez agir
drawdown urettigini gostermistir — yani sonucun kotulugu "sanssiz bir sira" degil, yapisal
olarak beklenen sonuctur. Gercek-hayat duzeltmesi durumu daha da kotulestirmektedir (PF
~0,529'a). Proje-ozel bir HEDEF_PF tanimlanmamis olsa da PF<1 evrensel olarak zarar eden
sistem anlamina gelir; bu tek basina RED icin yeterlidir.

---

## --- STRATEJISTE GERI BiLDiRIM ---

Bu hipotez (Buyuk-Bar Ters-Yon/Fade, HIPOTEZ 2) mevcut haliyle gercek/demo hesaba hazir
DEGILDIR. Somut oneriler:

1. **Temel edge yeniden dogrulanmali.** Fiilen islem edilen alt-orneklemde (M5, seans 15-18)
   buyuk-bar-sonrasi ters-yon orani (%48,86) 0,50'den istatistiksel olarak anlamli sekilde
   sapmiyor (p=0,2234) — global orneklemdeki anlamli sapma (M5/M1), uygulanan seans filtresiyle
   birlikte kayboluyor. Herhangi bir yeniden tasarimdan once, TAM OLARAK islem edilecek
   populasyonda (filtreler dahil) edge'in var oldugu once istatistiksel olarak gosterilmeli —
   aksi halde ayni sonuc tekrarlanir.
2. **Sonuc 3 farkli tarama boyutunda VE 6/6 walk-forward penceresinde tutarli negatif** — bu
   bir esik-ayari sorunu degil, "buyuk barin ardindan fade" mantiginin bu haliyle (bu enstruman/
   zaman dilimi/filtre kombinasyonunda) gecerli bir edge saglamadigini gosteriyor. Farkli bir
   temel mekanizma (orn. buyuk-bar YONUNDE devam/momentum hipotezi — fade'in tersi) veya
   tamamen farkli bir sinyal kaynagi degerlendirilmeli.
3. **BIGBAR_MULT (1,5x), ATR_FRACTION (0,5), RR_RATIO (1:1) hic test edilmedi** (bilinCli
   guvenlik-agi karari) — eger hipotez tamamen terk edilmeyip revize edilecekse, once bu 3
   parametrenin dar bir aralikta hassasiyeti test edilmeli; ancak mevcut sonucun genislik/
   derinligi goz onune alindiginda bu dusuk-oncelikli bir adimdir.
4. **MAX_TICK_MISMATCH_SEC=60 parametresi bu turde Muhendis tarafindan eklendi, Stratejist
   onayi bekliyor** — etkisi ihmal edilebilir olcude kucuk (12.210 sorgudan 2'si reddedildi)
   ama surec geregi ayrica onaylanmali/kayit altina alinmali.
5. **Saat-esleme/DST bulgusu** (Hipotez 1 ile ayni, bagimsiz dogrulandi) hala cozulmemis —
   Justin projesindeki TUM saat-bazli filtreler icin gecerli bir risk, VPS'in gercek DST
   davranisi netlestirilmeli.
6. **Justin icin proje-ozel "gecmis calisma" dosyasi hala olusturulmadi** — HEDEF_PF/
   HEDEF_WR/HEDEF_DD ve risk parametreleri (kasa buyuklugu, islem basina risk, lot buyuklugu)
   2. arka arkaya turde de tanimsiz kaldi; sonraki Risk Analisti turlerinin KONTROL 4/8'i tam
   yapabilmesi icin bu netlestirilmeli.
7. **Iki arka arkaya hipotez (Hipotez 1: mean-reversion, Hipotez 2: fade/ters-yon) RED oldu,
   ikisi de "tum donem boyunca tutarli edge-yoklugu" paterniyle** — bu, sadece hipotez
   duzeyinde degil, Arastirmaci asamasindaki varsayimlarin/veri kaynaginin da yeniden gozden
   gecirilmesini gerektirebilir (Orkestrator'a iletilmek uzere bir gozlem, karar Stratejist'e
   ait).

---

## --- KULLANICIYA ---

Justin projesinin ikinci stratejisi (buyuk bir mum hareketinden sonra fiyatin geri donecegini
varsayan "buyuk-bar ters-yon" fikri) test edildi ve sonuc yine olumsuz cikti — hem de Hipotez
1'e gore daha net bir sekilde. Once yapilan bir istatistik testi, stratejinin kullandigi
filtrelerle (belirli saat araligi) birlikte, "buyuk mumdan sonra fiyat gercekten ters mi
doner" varsayiminin kendisinin istatistiksel olarak dogru olmadigini gosterdi — yani fikrin
temeli, uygulanan filtreyle bir arada zaten sarsiliyor. Bunun dogal sonucu olarak: test edilen
her ayarlamada (farkli bekleme sureleri, farkli cikis yontemleri, saat filtresi acik/kapali)
ve gecmis 17 ayin ALTIYA bolunmus HER bir doneminde ve 18 ayin HER birinde, strateji para
kaybetti (kazandigindan fazlasini kaybetti). Bu turde ayrica, bir onceki turde bulunan bir
hesaplama hatasi (yanlis fiyat verisiyle slipaj hesaplanmasi) duzeltildi — duzeltme sonucu
DAHA DA kotu cikti, yani hata sonucu oldugundan iyi gosteriyordu. Bu kez elimizde TUM islem
kayitlari oldugu icin ("sansli bir sira mi yaptik" sorusunu test eden) bin'lerce olasi
farkli-sirali senaryo bagimsiz olarak denendi ve HEPSI benzer buyuklukte agir bir zarara
gotürdu — yani kotu sonuc sans eseri degil, yapisal. Bu nedenle bu hipotezi de RED (reddedildi)
olarak degerlendiriyorum; canli/demo hesapta denenmemeli. Stratejist'e, hem bu hipotezin temel
varsayiminin yeniden sorgulanmasi hem de arka arkaya iki hipotezin de ayni olumsuz deseni
gostermesi nedeniyle daha genis bir yeniden degerlendirme onerisi icin somut geri bildirim
iletildi.

---

## --- BAGIMSIZ DOGRULAMA NOTU (metodoloji seffafligi) ---

Bu raporda asagidaki hesaplamalar Muhendis'in JSON ciktisindan (`backtest_hipotez2_output.json`,
`senaryolar.ANA_KONFIGURASYON.islem_logu_tam`, 2203 kayit) BAGIMSIZ olarak yeniden turetildi
ve Muhendis'in ozet rakamlariyla capraz kontrol edildi (hepsi eslesti):
- Toplam islem, kazanma orani, profit factor, gross profit/loss
- Max ardisik kazanc/kayip serisi
- En iyi 3/10 islemin brut kara orani
- 18 aylik kirilimde pozitif ay sayisi (0/18, bagimsiz sayildi)
- 500-shuffle Monte Carlo simulasyonu (R-katlari cinsinden, kasa buyuklugu tanimsiz oldugu
  icin oransal risk-birimi metodolojisiyle, sistem promptumdaki standart yontemin bu proje
  icin adapte edilmis hali)
