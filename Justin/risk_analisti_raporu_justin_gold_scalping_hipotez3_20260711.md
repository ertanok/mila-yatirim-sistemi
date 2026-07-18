=== RiSK ANALiZi RAPORU ===
Hipotez        : Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali — HIPOTEZ 3 (6 senaryo:
                 GENEL-FADE, STREAK-FADE L2-L5, BIGBAR-FADE)
Proje          : PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi), Yol1 pipeline 4/4 (son adim)
Yaklasim Turu  : Kural-tabanli (fade/ters-yon, ATR-bazli risk, rejim ikincil-filtre, M1-agirlikli)
Tarih          : 2026-07-11
KARAR          : **RED**

---

## ON-NOT — EKSIK BILGI, METODOLOJI ADAPTASYONU VE BAGIMSIZ DOGRULAMA KAPSAMI

Justin projesi icin proje-ozel HEDEF_PF/HEDEF_WR/HEDEF_DD ve kasa buyuklugu/islem basina risk/
lot buyuklugu **ucuncu ardisik turde de** tanimsiz kaldi (Justin'in gecmis-calisma dosyasi yok,
canli hesabi yok). Bu nedenle KONTROL 4 ve KONTROL 8'deki dolar-bazli hesaplamalar bu turde de
YAPILMADI; yalniz oransal/R-katlari cinsinden degerlendirme yapildi. Sonuc o kadar acik ve genis
kapsamli ki (asagida detaylandirilan 60+ ayri kesitin TAMAMINDA PF<1) bu eksik bilgi karari
degistirmiyor — ancak bu eksiklik uc turdur devam ettigi icin ayrica Orkestrator'a/Ertan'a
iletiliyor (bkz. Stratejiste/Orkestratore Geri Bildirim).

**Bagimsiz dogrulama (bu turde tam islem loglari — 6 senaryo, toplam 17.361 islem — dogrudan
`backtest_hipotez3_output.json`'dan okunup KENDI KODUMLA yeniden hesaplandi):**
- Her 6 senaryo icin PF, WR, gross-profit/gross-loss BAGIMSIZ yeniden hesaplandi ve Muhendis'in
  ozet rakamlariyla **BIREBIR eslesti** (PF: 0,488/0,488/0,483/0,448/0,548/0,472 — tamami
  dogrulandi).
- Max ardisik kazanc/kayip serileri BAGIMSIZ yeniden hesaplandi ve Muhendis'in Bolum 5.4
  tablosuyla **BIREBIR eslesti** (GENEL-FADE 11/12, L2 9/14, L3 9/15, L4 11/9, L5 7/6,
  BIGBAR-FADE 11/10).
- En iyi 3/10 islemin brut-kara orani her 6 senaryo icin BAGIMSIZ hesaplandi (asagida KONTROL 5).
- 500-shuffle Monte Carlo simulasyonu her 6 senaryo icin BAGIMSIZ calistirildi; kasa buyuklugu
  tanimsiz oldugu icin R-katlari (R = ortalama kaybeden islem buyuklugu, ~201-208 puan/lot,
  senaryoya gore) cinsinden, oransal/kasa-bagimsiz metodoloji kullanildi (Hipotez 2'deki
  adaptasyonla ayni).
- Veri butunlugu YUKSEK: hicbir capraz kontrolde tutarsizlik bulunmadi.

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik**: GECTI (hacim acisindan) → Egitim (IS) islem sayilari: GENEL-FADE
5459, STREAK-L2 2881, STREAK-L3 1506, STREAK-L4 735, STREAK-L5 332, BIGBAR-FADE 1226 — **6
senaryonun 6'si da "Guclu" (150+) esiginin uzerinde**, en dar olani (L5) bile 332. Gorulmemis
veri (OOS) n: en dar L5 ile 162, 15 esiginin cok uzerinde. Walk-forward 6 penceresi her senaryoda
nispeten esit dagilmis (orn. GENEL-FADE 1277-1370, L4 162-186 araliginda) — tek bir kisa/carpik
donemden gelen bir sonuc degil. Model-tabanli/stokastik yontem olmadigi icin seed tekrari N/A.
Ayrica on-kontrol asamasinda (Muhendis raporu Bolum 1) 48 test uzerinde resmi coklu-karsilastirma
duzeltmesi (Bonferroni: 14, FDR: 25 hucre hayatta) uygulanmis — bu surec dogru isletilmis.
**Ancak hacmin yeterliligi burada bir teselli degil:** asagida gorulecegi gibi, bu genis
orneklem sadece "sonuc tesadufi degil, sistematik olarak negatif" bulgusunu GUCLENDIRIYOR.

**[2] Egitim/Gorulmemis Bozulma**: KIRMIZI (bozulma-orani degil, temel-sonuc acisindan) →
PF bozulmasi (IS PF/OOS PF) her 6 senaryo icin hesaplandi: GENEL-FADE 1,13x, L2 1,08x, L3 1,18x,
L4 1,51x (en yuksek), L5 1,21x, BIGBAR-FADE 0,88x (OOS, IS'ten iyi) — **hicbiri 1,6 esigini
gecmiyor, klasik "egitimde ezberleyip gorulmemiste cakma" (overfitting) deseni YOK.** WR farki
(IS-OOS, yuzde puani): GENEL-FADE 0,89, L2 1,12, L3 0,75, L4 **9,28** (en genis, 10pp esiginin
hemen altinda), L5 3,10, BIGBAR-FADE -3,26 — hicbiri 10pp esigini asmiyor ama L4 sinira cok
yakin. DD degisimi orani (islem-basi normalize): GENEL-FADE 1,06x, L2 1,01x, L3 1,10x, L4 **1,48x**
(1,5x esiginin hemen altinda), L5 1,24x, BIGBAR-FADE 0,77x. **Asil kirmizi bayrak burada esik
asimlarindan degil, temel gercekten geliyor: HEM IS HEM OOS profit factor 6 senaryonun 6'sinda
da 1'in ALTINDA** (IS araligi 0,455-0,580, OOS araligi 0,333-0,517) — strateji hicbir zaman,
hicbir veri diliminde net pozitif olmamis. Bu, Hipotez 2'deki ile ayni desen: overfitting'den
farkli ama esit derecede ciddi — gercek edge yoklugu. L4'un IS-OOS sapmasi (fark 0,168) diger
5 senaryoya (0,04-0,15 araligi) gore goreceli genis olsa da, IS zaten <1 oldugu icin bu "karli
gorunup cakma" degil, mevcut olumsuzlugun pekismesidir (Muhendis'in kendi degerlendirmesiyle
tutarli); n=305 (OOS) tek basina karar dayanagi degil.

**[3] Monte Carlo (R-katlari, kasa buyuklugu tanimsiz — Hipotez 2 ile ayni metodoloji, BAGIMSIZ
yeniden calistirildi)**: KIRMIZI BAYRAK → Her 6 senaryo icin 500-shuffle simulasyonu, tam islem
loglari uzerinde bagimsiz calistirildi (R = ortalama kaybeden islem buyuklugu, senaryoya gore
~201-208 puan/lot):

| Senaryo | Medyan DD (R) | En kotu %5 (R) | En iyi %5 (R) | 500 shuffle araligi |
|---|---|---|---|---|
| GENEL-FADE | 2130,4 | 2134,4 | 2128,9 | 2128,9 - 2139,3 |
| STREAK-FADE L2 | 1145,5 | 1149,6 | 1143,9 | 1143,9 - 1155,4 |
| STREAK-FADE L3 | 592,1 | 595,7 | 590,7 | 590,7 - 601,0 |
| STREAK-FADE L4 | 313,9 | 317,3 | 312,7 | 312,7 - 322,4 |
| STREAK-FADE L5 | 117,5 | 122,0 | 115,4 | 115,4 - 128,1 |
| BIGBAR-FADE | 502,8 | 506,1 | 501,5 | 501,5 - 514,6 |

**Kritik bulgu (Hipotez 2'deki ile ayni desen): her senaryonun 500 shuffle'inin TAMAMI, birbirine
son derece yakin (araliklarin genisligi medyanin sadece ~%0,5-4'u kadar) devasa drawdown
degerleriyle sonucleniyor.** Bunun sebebi, her senaryoda toplam gross-loss'un gross-profit'in
yaklasik 2-2,2 kati olmasi (orn. GENEL-FADE: GP=411.725,77 / GL=844.136,86) — kar/zarar sirasi
nasil karistirilirsa karistirilsin, sonuc pratik olarak DETERMINISTIK sekilde agir negatif
cikiyor; "sansli bir sira" ihtimali yok denecek kadar dusuk. Herhangi bir makul kasa/risk
yonetimi altinda (ihtiyatli bir hesap tipik olarak 20-30R'lik bir dususu bile guclukle tolere
eder), yuzlerce-binlerce R'lik kesintisiz negatif suruklenme **hesabi pratik olarak sifirlar/
iflas ettirir.** Sistem promptumdaki ">%35 = KIRMIZI BAYRAK" kategorisinin (oransal DD-yuzdesi
cercevesi) acikca cok otesinde, R-katlari cinsinden ifade edilen bir bulgu.

**[4] Pes Pese Kayip**: KIRMIZI/UYARI → Gercek max ardisik kayip (bagimsiz dogrulandi, Muhendis'in
Bolum 5.4 tablosuyla birebir eslesiyor): GENEL-FADE 12, L2 14, L3 **15**, L4 9, L5 6, BIGBAR-FADE
10. Teorik beklenti [log(0,05)/log(1-WR)] her senaryo icin hesaplandi:

| Senaryo | WR | Teorik beklenti | Gercek | Oran |
|---|---|---|---|---|
| GENEL-FADE | 46,86% | 4,74 | 12 | 2,53x |
| STREAK-FADE L2 | 45,72% | 4,90 | 14 | 2,86x |
| STREAK-FADE L3 | 46,59% | 4,78 | 15 | **3,14x** |
| STREAK-FADE L4 | 45,58% | 4,92 | 9 | 1,83x |
| STREAK-FADE L5 | 48,38% | 4,53 | 6 | 1,32x |
| BIGBAR-FADE | 45,59% | 4,92 | 10 | 2,03x |

**6 senaryonun 6'sinda da gercek max seri, teorik/iid beklentinin en az 1,3 kati, en fazla 3,1
kati** — saf rastgele/bagimsiz-ozdes varsayimindan daha kotu bir kumelenme, negatif-edge ile
tutarli. Dolar/yuzde etkisi HESAPLANAMADI (Justin icin kasa/lot tanimsiz — varsayim
uydurulmadi). Oransal ifade: STREAK-FADE L3'te 15 ardisik kayip = R'nin (~204 puan/lot) 15
kati arka arkaya; bu tek basina, KONTROL 3'teki (L3) ~592R'lik toplam Monte Carlo drawdown'inin
kucuk ama gozle gorulur bir kismini (~%2,5'ini) tek bir seride olusturuyor.

**[5] Kar Konsantrasyonu**: GECTI (dagilim saglikli, ama sonucu kurtarmiyor) → Bagimsiz hesap
(6 senaryo, brut kara oran):

| Senaryo | En iyi 3 / brut kar | En iyi 10 / brut kar |
|---|---|---|
| GENEL-FADE | %0,39 | %1,10 |
| STREAK-FADE L2 | %0,75 | %2,01 |
| STREAK-FADE L3 | %1,21 | %3,27 |
| STREAK-FADE L4 | %2,11 | %6,21 |
| STREAK-FADE L5 | %3,66 | %10,91 |
| BIGBAR-FADE | %1,20 | %3,70 |

**6 senaryonun 6'sinda da en iyi-3 orani %20 esiginin cok altinda** — sonuc birkac buyuk
islemden degil, genel/yaygin bir zarar deseninden geliyor. Gunluk/haftalik konsantrasyon verisi
bu raporda saglanmadi (yalniz aylik/pencere kirilimi var) — bu, "tek bir gun/hafta karin
%40'ini olusturuyor mu" sorusunu N/A birakiyor; ancak zaten toplamda pozitif bir "kar" olmadigi
icin (6 senaryonun 6'si da tum-donem net negatif) bu soru pratikte anlamsizlasiyor, Hipotez
2'deki ile ayni mantik.

**[6] Kirilim Analizi (Walk-Forward + Rejim Post-Hoc)**: KIRMIZI → Raporlanan HER kirilim
boyutunda profit factor 1'in altinda kaliyor, istisna yok:
- Walk-forward: **36/36 kesit** (6 senaryo x 6 pencere) PF<1 (araligi 0,303-0,627); en iyi tekil
  pencere dahi (GENEL-FADE pencere-1, PF=0,597) 1'in altinda — tek-donem sansi/carpitmasi yok,
  sonuc zaman ustunde tutarli negatif.
- Rejim post-hoc (VOL genis/dar, TREND trend/range, ayni islem seti uzerinde ikincil filtre):
  **24/24 hucre** (6 senaryo x 4 rejim-etiketi) PF<1 (araligi 0,377-0,652); en iyisi bile
  (STREAK-FADE L5, VOL-genis, n=301, PF=0,652) 1'in altinda. Hicbir rejim segmentinde gizli bir
  edge YOK — bu, Hipotez 3'un "rejimden bagimsiz uniform sinyal" temel iddiasiyla yon olarak
  tutarli, ama uniform olan sey burada uniform bir ZARARDIR.
- En dar rejim-post-hoc hucreleri (STREAK-FADE L5/VOL-dar n=193, STREAK-FADE L4/VOL-dar n=424)
  goreceli kucuk — yorumlanabilir ama tek basina karar dayanagi olarak kullanilmadi (Muhendis'in
  kendi notuyla tutarli).
- **Toplamda 6 senaryo x [tum-donem+IS+OOS+6-WF+4-rejim] = 66 ayri kesitin 66'sinda da PF<1** —
  hicbir istisna yok. Bu, Hipotez 1 ve Hipotez 2'den bile daha genis kapsamli ve daha tutarli
  bir olumsuz sonuc.

**[7] Parametre Hassasiyeti**: KISMEN TEST EDILDI / TEST YOK (karisik) → STREAK_LENGTHS (2,3,4,5)
4 farkli deger tarandi ve TUMUNDE PF<1 bulundu — bu genis bir aralikta tutarli negatif oldugu
icin "kirilgan/sansli bir tek noktaya rastlama" (curve-fit) ihtimalini ZAYIFLATIYOR, olumlu bir
gozlem. **Ancak ATR_FRACTION (0,5 sabit), RR_RATIO (1:1 sabit), N_BARS_TIME (1 sabit),
BIGBAR_MULT (1,5x sabit) hic degistirilmedi** — bu, bilincli bir "overfitting guvenlik agi"
karari (Stratejist'in gorev tanimindan), muhendis ihmali degil, ama hassasiyeti bilinmiyor.
Seans filtresi (15-18) da tek deger olarak test edildi, tarama yapilmadi. **Ayrica: SL/TP semasi
(ATR14x0,5, RR=1:1) Stratejist'in Hipotez-3'e ozel bir deger belirtmemesi nedeniyle H1/H2'den
DOGRUDAN TASINDI** — Muhendis bunu ayrica bir muhendislik karari olarak isaretledi, **Stratejist
onayi bekliyor.** Sonuc zaten genis bir bolgede (66/66 kesit) sistematik olarak negatif oldugu
icin bu bilinmezliklerin karari degistirme olasiligi dusuk, ama governance acisindan kayitlara
geciyor.

**[8] Gercek Hayat Duzeltmesi**: KIRMIZI → Slipaj: giris tarafi zaten gercek tick-bazli bid/ask
ile hesaplanmis (ortalama toplam maliyet ~51-56 puan/islem = spread+slipaj), EK bir slipaj
varsayimi UYDURULMADI (cift sayma riskinden kacinmak icin). Psikoloji/uygulama payi: proje ayrica
belirtmedigi icin muhafazakar varsayilan (%10-15, orta nokta %12,5) uygulandi — Hipotez 2'deki
ayni yontemle (zaten negatif olan net sonuc, bu duzeltmeyle DAHA da kotulesiyor):

| Senaryo | Tum-donem PF | GP | GL | Duzeltilmis Net (pts) | Duzeltilmis PF |
|---|---|---|---|---|---|
| GENEL-FADE | 0,488 | 411.725,77 | 844.136,86 | -486.462,48 | **0,459** |
| STREAK-FADE L2 | 0,488 | 219.182,82 | 449.184,62 | -258.752,03 | **0,459** |
| STREAK-FADE L3 | 0,483 | 112.661,97 | 233.160,34 | -135.560,67 | **0,454** |
| STREAK-FADE L4 | 0,448 | 52.651,08 | 117.652,05 | -73.126,09 | **0,419** |
| STREAK-FADE L5 | 0,548 | 28.450,50 | 51.960,43 | -26.448,67 | **0,518** |
| BIGBAR-FADE | 0,472 | 92.227,64 | 195.362,34 | -115.976,54 | **0,443** |

Duzeltilmis PF, 6 senaryonun 6'sinda da ham PF'nin bile ALTINDA (0,419-0,518 araligi) — gercek
hesapta durum backtest'ten DAHA KOTU olacaktir. Justin icin bir HEDEF_PF tanimlanmamis olsa da,
PF<1 (hem ham hem duzeltilmis) evrensel olarak "islem basina ortalama zarar eden sistem" anlamina
gelir; bu tek basina RED icin yeterli ve mutlak bir esiktir (herhangi bir proje-ozel hedeften
bagimsiz).

---

## --- OZET ---

**Guclu Yanlar:**
- Ornekleme fazlasiyla yeterli: 6 senaryonun 6'sinda da IS n>=150 (Guclu esigi), en dar OOS
  bile (L5, n=162) yorumlanabilir sinirin cok uzerinde.
- Muhendis metodolojik olarak titiz: on-kontrol 1-3 (DST, coklu-karsilastirma-resmi, gercekci-
  maliyet-erken-kontrol) sirayla uygulanmis; fiziksel-tutarlilik kontrolu (slipaj<=spread,
  tick-zaman-uyusmazligi reddi=0) gecilmis; bu turde tespit edilen bir verimlilik sorunu
  (cifte run_scenario cagrisi) sonucu/mantigi degistirmeden duzeltilmis.
- Bu turde TAM islem loglari (6 senaryo, 17.361 islem) saglandigi icin PF/WR/gross-kar-zarar,
  max ardisik seri ve kar-konsantrasyonu BAGIMSIZ VE TAM olarak yeniden hesaplandi — tum
  capraz kontroller Muhendis'in rakamlariyla birebir eslesti, veri butunlugu yuksek.
- Kar konsantrasyonu 6 senaryonun 6'sinda da saglikli (en iyi-3 orani %0,4-3,7 araliginda,
  %20 esiginin cok altinda) — sonuc birkac buyuk islemden degil, genel bir zarar deseninden.
- STREAK_LENGTHS (2-5) taramasinin TUMUNDE tutarli negatif olmasi, "sansli bir esik noktasina
  rastlama" (curve-fit) ihtimalini zayiflatiyor.
- Klasik "IS'te ezberleyip OOS'ta cakma" (overfitting) deseni YOK (PF bozulmasi 6 senaryonun
  6'sinda da 1,6 esiginin altinda) — sorun overfitting degil, daha temel bir edge-yoklugu.

**Zayif Yanlar / Riskler:**
- **6 senaryo x [tum-donem+IS+OOS+6-WF+4-rejim] = 66 ayri kesitin 66'sinda da profit factor
  1'in altinda** (araligi 0,303-0,652) — istisna YOK. Bu, Hipotez 1 ve Hipotez 2'den bile daha
  genis kapsamli ve tutarli bir olumsuz sonuc.
- **Bagimsiz Monte Carlo (6 senaryo, 500-shuffle her biri): tum senaryolarda 500 shuffle'in
  TAMAMI, birbirine son derece yakin, devasa (yuzlerce-binlerce R) drawdown ile sonucleniyor**
  — sonuc pratik olarak deterministik kotu, "sansli sira" ihtimali yok denecek kadar dusuk.
- **6 senaryonun 6'sinda da gercek max ardisik kayip, teorik/iid beklentinin 1,3-3,1 kati** —
  kumelenme normalden fazla, negatif-edge ile tutarli.
- **Gercek-hayat duzeltmesi (psikoloji/uygulama payi) durumu daha da kotulestiriyor** — 6
  senaryonun 6'sinda da duzeltilmis PF (0,419-0,518), ham PF'nin altinda.
- STREAK-FADE L4'te IS-OOS sapmasi (0,501->0,333) digerlerine gore goreceli genis (n=305 OOS,
  tek basina karar dayanagi degil, ama not edilmeli).
- Maliyet/ATR orani (ortalama toplam maliyet ATR'nin ~%15-19'u, SL mesafesinin ~%28-34'u) M1
  scalping'in yapisal olarak yuksek goreceli maliyet-yuku tasidigini gosteriyor — fiziksel
  olarak imkansiz degil ama yapisal bir dezavantaj.
- ATR_FRACTION/RR_RATIO/BIGBAR_MULT/N_BARS_TIME hic degistirilmedi (bilincli guvenlik-agi
  karari, ama hassasiyet bilinmiyor); SL/TP semasi (ATR14x0,5, RR1:1) H1/H2'den tasindi,
  Stratejist onayi bekliyor.
- Saat-esleme/DST belirsizligi (H1/H2/H3-precheck ile ayni bulgu, 4. kez bagimsiz dogrulandi)
  devam ediyor — kis aylarinda 15-18 seans filtresi fiilen kaymis olabilir.
- Justin projesi icin HEDEF_PF/HEDEF_WR/HEDEF_DD ve kasa buyuklugu/risk parametreleri **ucuncu
  ardisik turde de** tanimlanmamis.
- **UC ARDISIK hipotez (Hipotez 1: mean-reversion, Hipotez 2: buyuk-bar-fade, Hipotez 3:
  rejimden-bagimsiz-uniform-fade), UC farkli mekanizma, HEPSI ayni patern ile RED oldu**
  (aggregate/on-kontrolde istatistiksel olarak "anlamli" ama gercek islem kosullarinda tutarli
  PF<1/negatif) — Stratejist'in v3/v4 raporlarinda ONCEDEN tanimladigi Madde-7 tetikleyici
  kosulu (bkz. Karar Gerekce) simdi ACIKCA karsilaniyor.

---

## --- KARAR GEREKCE ---

Hipotez 3'un 6 sinyal-ailesi/varyantinin (GENEL-FADE, STREAK-FADE L2-L5, BIGBAR-FADE)
TAMAMINDA, tum-donem/IS/OOS/6-pencere-walk-forward/4-rejim-post-hoc dahil **66 ayri kesitin
66'sinda da profit factor 1'in altinda** kalmistir — istisna yok, hicbir konfigurasyon veya
rejim segmentinde bir edge bulunamamistir. Bagimsiz olarak (tam islem loglari uzerinden, 6
senaryo icin ayri ayri) yeniden calistirilan Monte Carlo simulasyonlari, her senaryoda 500
shuffle'in tamaminin birbirine son derece yakin, devasa buyuklukte drawdown urettigini
gostermistir — yani sonucun kotulugu "sanssiz bir sira" degil, gross-loss'un gross-profit'in
sistematik olarak ~2 kati olmasindan kaynaklanan yapisal/deterministik bir sonuctur. Gercek-hayat
duzeltmesi (psikoloji/uygulama payi) durumu 6 senaryonun 6'sinda da daha da kotulestirmistir.
Klasik overfitting deseni (IS'te iyi, OOS'ta cokme) yok olsa da bu bir teselli degildir — cunku
IS zaten <1'dir; sorun bir egitim/test ayrimi sorunu degil, hipotezin temel mekanizmasinin (bar-
sonrasi fade/donus) bu enstruman/zaman-dilimi/filtre kombinasyonunda gercek bir edge saglamadigi
gercegidir. Proje-ozel bir HEDEF_PF tanimlanmamis olsa da, PF<1 evrensel olarak zarar eden bir
sistem anlamina gelir ve tek basina RED icin yeterlidir; bu durumda 66/66 kesitte istisnasiz
tekrarlanmasi, kararı guclendirmekten baska bir sey yapmaz.

**Ayrica onemli bir surec notu:** Stratejist, v4 raporunun Bolum 4'unde ("Madde-7 On-Karari"),
Hipotez 3 de Backtest Muhendisi'nin tam testinde H1/H2 ile ayni paternle (aggregate/on-kontrolde
"anlamli" ama gercek kosullarda tutarli-negatif) RED cikarsa, bunun **otomatik olarak Madde-7'yi
tetikleyecegini** ve bir sonraki Stratejist turunun bunu yeniden tartismaya gerek kalmadan
dogrudan Ertan'a sunmasi gerektigini ONCEDEN karara baglamisti. Bu rapor, tam da o kosulu
karsilamaktadir: uc ardisik hipotez, uc farkli mekanizma, hepsi ayni sonuc. Bu, Risk Analisti'nin
kendi karari degil, Stratejist'in kendi onceki turunde birakmis oldugu kosullu bir karari
tetikleyen bir GOZLEMdir — Orkestrator'a ve bir sonraki Stratejist turuna aynen iletilmelidir.

---

## --- STRATEJISTE GERI BiLDiRIM ---

Bu hipotez (Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali, HIPOTEZ 3, 6 varyant) mevcut
haliyle gercek/demo hesaba hazir DEGILDIR. Somut noktalar:

1. **v4 raporunuzun Bolum 4'unde onceden tanimladiginiz Madde-7 kosulu SIMDI TETIKLENDI.** Uc
   ardisik hipotez (mean-reversion, buyuk-bar-fade, rejimden-bagimsiz-uniform-fade), uc farkli
   mekanizma, hepsi "aggregate/on-kontrolde istatistiksel olarak anlamli, ama gercek islem
   kosullarinda (walk-forward/OOS/gercekci-maliyet) tutarli PF<1/negatif" paterniyle RED oldu.
   Kendi onceden verdiginiz karara gore bu, bir sonraki turde dogrudan Ertan'a: (a) Arastirmaci
   asamasina genis capli bir yontem-degisikligi (kural-tabanli disi, orn. ML/feature-tabanli
   veya farkli veri/timeframe kombinasyonu) ONERISI, VEYA (b) bu alt-hedefin (Gold Scalping,
   kural-tabanli fiyat-aksiyonu ailesi) durdurulup Justin'in kaynaklarinin farkli bir yaklasima
   yonlendirilmesi SECENEGI olarak sunulmalidir. Sizin de belirttiginiz gibi bu asamada
   "hicbir sey yapmadan devam etmek" secenegi masada olmamalidir.
2. **Rejimden-bagimsizlik hipotezi (Bolum 1, v4) DOGRULANDI ama olumsuz yonde** — rejim
   ayristirmasi (VOL/TREND, 24 hucre) hicbir segmentte PF'yi 1'in uzerine tasimadi; "uniform"
   olan sey rejimden bagimsiz bir zarar. Bu, rejim-etiketli bir revizyonun (farkli VOL/TREND
   esikleri, farkli pencere genisligi) sonucu kurtarma ihtimalinin dusuk oldugunu gosteriyor —
   herhangi bir yeniden tasarimdan once temel fade/donus mekanizmasinin kendisi sorgulanmali.
3. **SL/TP semasi (ATR14x0,5, RR=1:1) Muhendis tarafindan H1/H2'den DOGRUDAN TASINDI, sizin
   Hipotez-3'e ozel bir deger belirtmemeniz nedeniyle** — bu bir muhendislik karari olarak
   isaretlendi, ayrica onayinizi/reddinizi bekliyor (surec/governance kaydi icin, sonucu
   degistirmesi olasi degil ama kayit altina alinmali).
4. **Justin icin proje-ozel "gecmis calisma" dosyasi hala olusturulmadi** — HEDEF_PF/HEDEF_WR/
   HEDEF_DD ve risk parametreleri (kasa buyuklugu, islem basina risk, lot buyuklugu) UCUNCU
   ardisik turde de tanimsiz kaldi. Madde-1 (yontem-degisikligi) veya Madde-1(b) (proje durdurma)
   secenegi ne olursa olsun, gelecekteki turlerin KONTROL 4/8'i tam yapabilmesi icin bu netlestirilmeli.
5. **Saat-esleme/DST bulgusu** (H1/H2/H3-precheck ile ayni, 4. kez bagimsiz dogrulandi) hala
   cozulmemis — VPS'in gercek DST davranisi, Justin'deki tum saat-bazli filtreler icin gecerli
   bir risk olarak netlestirilmeli (bu turde veri araligi yaz-donemi-ici oldugu icin gozlenmedi,
   ama kis-donemi genislemelerinde onemli).

---

## --- KULLANICIYA ---

Justin projesinin ucuncu Gold Scalping stratejisi ("kucuk fiyat hareketlerinden sonra fiyatin
geri donecegini/devam edecegini varsayan, piyasa kosuluna gore degil her kosulda gecerli olmasi
umulan bir sinyal") 6 farkli varyantiyla test edildi ve sonuc yine olumsuz — bu kez daha da
genis kapsamli bir olumsuzluk cikti. Test edilen 6 varyantin 6'sinda da, bakilan HER acidan
(egitim donemi, gorulmemis/test donemi, gecmisin 6 esit dilimi, 4 farkli piyasa kosulu segmenti)
strateji para kaybetti — toplam 66 ayri olcumun tek bir istisnasi bile yok. Ayrica, "sansli bir
sira mi yakaladik" sorusunu test eden bin'lerce olasi farkli-sirali senaryo her varyant icin
bagimsiz olarak denendi ve hepsi benzer buyuklukte, neredeyse degismez agir bir zarara gotürdu —
yani kotu sonuc sans eseri degil, yapisal. Bu nedenle bu hipotezi de RED (reddedildi) olarak
degerlendiriyorum; canli/demo hesapta denenmemeli. Daha onemlisi: bu, Justin'in Gold Scalping
projesinde arka arkaya denenen UCUNCU farkli fikrin de ayni sekilde basarisiz olmasi demek —
Stratejist onceden, boyle bir durumda ("uc arka arkaya hipotez, ayni olumsuz patern") otomatik
olarak Ertan'a iki secenek sunulmasi gerektigine karar vermisti: ya tamamen farkli bir yontemle
(orn. makine ogrenmesi tabanli) bastan baslamak, ya da bu alt-projeyi (kisa-vadeli/scalping
fiyat-aksiyonu fikirleri) durdurup Justin'in kaynaklarini baska bir yaklasima yonlendirmek. Bu
karar noktasi simdi tetiklendi ve bir sonraki adimda size somut olarak sunulacak.

---

## --- BAGIMSIZ DOGRULAMA NOTU (metodoloji seffafligi) ---

Bu raporda asagidaki hesaplamalar Muhendis'in JSON ciktisindan (`backtest_hipotez3_output.json`,
`senaryolar.{GENEL_FADE,STREAK_FADE.L2..L5,BIGBAR_FADE}.islem_logu_tam`, toplam 17.361 kayit)
BAGIMSIZ olarak (ayri bir Python script'i ile) yeniden turetildi ve Muhendis'in ozet
rakamlariyla capraz kontrol edildi (hepsi eslesti):
- Her 6 senaryo icin: toplam islem, kazanma orani, profit factor, gross profit/loss
- Her 6 senaryo icin: max ardisik kazanc/kayip serisi
- Her 6 senaryo icin: en iyi 3/10 islemin brut-kara orani
- Her 6 senaryo icin: PF bozulmasi (IS/OOS), WR farki, DD-orani (islem-basi normalize)
- Her 6 senaryo icin: teorik-vs-gercek max ardisik kayip orani
- Her 6 senaryo icin: 500-shuffle Monte Carlo simulasyonu (R-katlari cinsinden, kasa buyuklugu
  tanimsiz oldugu icin oransal risk-birimi metodolojisiyle — Hipotez 2'de kurulan adaptasyonla
  ayni yontem)
- Her 6 senaryo icin: gercek-hayat duzeltmesi sonrasi PF (psikoloji/uygulama payi %12,5,
  slipaj cift-sayilmadan)
