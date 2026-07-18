=== RISK ANALIZI RAPORU ===
Hipotez        : HIPOTEZ 1 (LightGBM Ikili + Grup B/Pivot-S-R) VE HIPOTEZ 2 (LightGBM 3-Sinifli/
                 Deadzone + Grup B) — BIRLIKTE, TEK TUR DEGERLENDIRME (v2/ML Tam Tur 2)
Yaklasim Turu  : Makine Ogrenmesi — Gradient Boosting (LightGBM binary + LightGBM multiclass)
Tarih          : 2026-07-12
KARAR          : RED (her iki hipotez de, kendi bagimsiz gerekceleriyle)

---

## ON-NOT — KAPSAM VE BAGIMSIZ DOGRULAMA

Bu degerlendirme, Orkestrator'un acik talimati geregi Hipotez 1 (v2) ve Hipotez 2 (v2) raporlarini
TEK bir turda, BIRLIKTE ele alir (S3 governance notu geregi — Stratejist raporu Madde 10). Hipotez 3
(v2, Grup D/mikro-yapi kisitli pilot) bu gorev anında rapor olarak HAZIR DEGIL (script/ciktisi
olabilir ama backtest_muhendisi_raporu...hipotez3_20260712.md dosyasi mevcut degil, dogrulandi) —
Stratejist'in kendi notuyla Hipotez 3 zaten ana karar agirligini TASIMIYOR (ONCELIK 3-Dusuk,
"sonuc SADECE bir on-gozlem, tek basina DAYANAK OLAMAZ"). Bu rapor, talimat geregi BEKLEMEDEN,
SADECE Hipotez 1/2 uzerinden nihai karari verir.

Iki Backtest Muhendisi raporu (`..._hipotez1_20260712.md`, `..._hipotez2_20260712.md`) ile
kendi ic-tutarlilik kontrolleri (Bolum 5-6/7'deki sayisal tablolar, Hipotez1-vs-Hipotez2
karsilastirma tablosu, RISK ANALiSTiNE ILETIM bloklari) karsilastirmali okundu. Ham JSON
dosyalarina (`backtest_ml_v2_hipotez1_output.json`, `backtest_ml_v2_hipotez2_output.json`)
bu turda ayrica satir-satir erisilmedi — rapor ici cok sayida capraz-referans (S1 oranlarinin
iki hipotezde BIREBIR ayni cikmasi, DST sonucunun tutarli olmasi, Tur1 sayilarinin dogru
tasinmasi) kendi icinde tutarli oldugu icin raporlar guvenilir birincil kaynak olarak kabul
edildi. Asagidaki 8 kontrol bagimsiz yorumumla, RED-varsayimi ilkesiyle uygulanmistir.

Hedef kriterler (kaynak: `justin_gecmis_calisma.md`): **HEDEF_PF=1,5 | HEDEF_WR=%60,0 (RR=1:1) |
HEDEF_DD=%20 kumulatif | kasa=2.000 USD | islem-basi risk=%1 ust sinir (20 USD baslangicta) |
lot=0,01 (sabit, taban)**. S2 protokolu geregi **MIN_SAMPLE=30** islem, orneklem yeterliligi icin
proje-ozel bagimsiz bir esik olarak ayrica dikkate alinmistir (bu kontrol listesindeki genel
"<15 anlamsiz" kuralindan DAHA SIKI, proje kendi esigini belirlemis — daha siki olan gecerlidir).

---

## --- KONTROLLER (HER IKI HIPOTEZ, YAN YANA) ---

**[1] Istatistiksel Anlamlilik**

- **Hipotez 1 : KIRMIZI** → TEST setinde (n=17.833 siniflandirma ornegi, tek-kez) tetiklenen
  islem sayisi = **0** (hem PRIMARY hem SUPPLEMENTARY). Kontrol listesindeki "OOS islem sayisi
  <15 ise anlamsiz" esiginin cok altinda — otomatik anlamsiz. Esik-kalibrasyonu OOF-havuzunda
  n=209 aday (SADECE LONG, SHORT tarafi MIN_SAMPLE'i hicbir esikte gecemedi) var ama bu 4 FARKLI
  fold-modelinin (best_iteration 1/3/10/3) havuzlanmis tahminidir, final modelin (best_iteration=3)
  gercek davranisini temsil etmez (asagida Kontrol 7).
- **Hipotez 2 : KIRMIZI** → TEST setinde tetiklenen islem sayisi = **15 (hepsi LONG, SHORT=0)**.
  Bu, genel kontrol-listesi esiginin (< 15 anlamsiz) TAM SINIRINDA ama projenin KENDI S2
  standardindaki **MIN_SAMPLE=30**'un ACIKCA ALTINDA — Backtest Muhendisi'nin kendisi de bunu
  "YETERSIZ ORNEKLEM UYARISI" olarak isaretlemis. PF/WR tek basina bu n ile karar dayanagi
  OLAMAZ. Ek olarak: egitim tarafinda model, TEST doneminde "notr" sinifini HICBIR ZAMAN
  secmedi (asagida Kontrol 2/7) — bu, egitimde gorulen sinif dagiliminin (%11 notr) test
  doneminde fiilen kaybolmasi, orneklem temsiliyetine dair ayri bir isaret.

**[2] Egitim/Gorulmemis Bozulma**

- **Hipotez 1 : KIRMIZI** → PF/WR bozulmasi klasik anlamda hesaplanamiyor (0 islem, tanimsiz).
  AUC uzerinden: walk-forward ort=0,5098 vs TEST=0,5190 (fark +0,009, ihmal edilebilir) — klasik
  "egitimde iyi/testte kotu" (overfitting) deseni YOK, ama bu iyi haber degil: rassal-seviyeye
  (0,50) bu kadar yakinken model hicbir donemde yon-sinyali tasimiyor demektir. Karar
  Cercevesi'nin en agir RED durumu ("PF hic olculemiyor") burada da gecerli — otomatik KIRMIZI.
- **Hipotez 2 : KIRMIZI** → TEST PF=**0,781**, HEDEF_PF=1,5'in **~%52'si** — "hedefin cok
  altinda" RED kriterinin (hedefin ~%65'inden az) ACIKCA ALTINDA. Ic-validasyon accuracy
  (0,4755) vs TEST accuracy (0,4218) arasinda fark var, ama bu klasik IS>>OOS overfitting
  paterninden cok, TEST doneminin (2025-09→2026-07) TRIVIAL "her-zaman-yukari-tahmin-et"
  taban cizgisinin (%46,96) DAHI ALTINDA (%42,18) kalmasidir — yani model, test doneminde
  en basit sabit-tahmin stratejisinden bile ZAYIF. Bu, salt "sinyal yok" degil, aktif olarak
  yanlis-yonlu bir siniflandirma paterni riski tasir. Otomatik KIRMIZI (PF hedefin cok altinda).

**[3] Monte Carlo (%5 DD)**

- **Hipotez 1 : KIRMIZI** → Uygulanamadi (n=0 islem, islem logu bos). Olcum yoklugu, "dusuk
  risk" degil.
- **Hipotez 2 : KIRMIZI** → Raporda Monte Carlo calistirilmamis/paylasilmamis; n=15 zaten
  500-kez-karistirma testi icin ANLAMLI bir sonuc uretemeyecek kadar kucuk bir islem logu
  (permutasyonlarin buyuk kismi birbirine cok benzer kalir, tail-risk tahmini guvenilmez olur).
  Bu bir "GECTI" degil — hem hesaplanmamis olmasi hem de hesaplansa bile guvenilir
  olmayacagi birlikte KIRMIZI olarak isaretleniyor.

**[4] Pes Pese Kayip**

- **Hipotez 1 : KIRMIZI** → n=0, ne gercek ne teorik seri kurulabilir.
- **Hipotez 2 : KIRMIZI/veri eksik** → Raporda islem-bazli kayip dizisi (hangi islemin
  kazandigi/kaybettigi sirasiyla) verilmemis, sadece toplam WR/PF/net paylasilmis. Teorik
  beklenti WR=%66,67 uzerinden hesaplanabilir: teorik_max ≈ ln(0,05)/ln(1-0,6667) ≈ **2,7 ≈ 3
  islem**. GP/GL'yi PF ve net kardan geriye tureterek (PF=0,781, Net=-32,57 USD →
  GrossProfit≈116,16 USD, GrossLoss≈148,73 USD, 5 kayip islem uzerinden ortalama kayip
  ≈**29,75 USD/islem**, bu benim tarafimdan raporlanan PF/WR/Net degerlerinden matematiksel
  olarak geriye turetilmis bir yaklasik degerdir, Muhendis'in dogrudan verdigi bir sayi
  DEGILDIR): 3 pes pese kayipla kasa etkisi ≈ 3×29,75=89,25 USD (kasa 2.000 USD'nin **%4,46'si**)
  — TEK BASINA kucuk bir etki, ANCAK gercek pes-pese-kayip dizisi (islem logu olmadan) BAGIMSIZ
  DOGRULANAMADI; bu, n=15'in zaten yetersizligiyle BIRLIKTE degerlendirilince ayri bir kirmizi
  bayrak DEGIL ama bir VERI EKSIKLIGI olarak isaretleniyor (Backtest Muhendisi'nden islem-bazli
  log istenmeli, eger hipotez ilerlerse).

**[5] Kar Konsantrasyonu**

- **Hipotez 1 : KIRMIZI** → n=0, tanimsiz.
- **Hipotez 2 : KIRMIZI/veri eksik** → Islem-bazli kar/zarar dagilimi (en iyi 3/10 islem)
  raporda YOK — sadece agregat PF/WR/Net verilmis. n=15 gibi kucuk bir kumede kar
  konsantrasyonu riski TIPIK OLARAK YUKSEKTIR (birkac buyuk kazanc/kayip toplam sonucu
  kolayca domine eder) — bu risk, veri saglanmadigi icin NE DOGRULANDI NE DE EKARTE EDILDI,
  bu da bagimsiz bir eksiklik olarak isaretleniyor.

**[6] Kirilim Analizi : N/A (her iki hipotez icin de)** → Raporlarda seans/gun/kosul bazli
kirilim tablosu yok (0 veya 15 islemlik ornekle zaten anlamli bir kirilim kurulamazdi).

**[7] Parametre/Model Hassasiyeti**

- **Hipotez 1 : KIRMIZI** → S2 geregi genis grid-search bilincli yapilmadi (dogru bir tercih,
  overfitting riskini sinirlar) — ama Tur 1 Risk Analisti raporunun (`risk_analisti_raporu_
  ..._ml_v1_hipotez1_20260712.md`, STRATEJISTE GERI BILDIRIM Madde 1) ACIKCA yazdigi bir
  duzeltme talebi ("kalibrasyon SADECE final modelin kendi OOF tahminlerinden yapilmali, 4
  FARKLI-karmasiklikta fold-modelinin HAVUZLANMIS tahminlerinden DEGIL") bu turde de AYNEN
  tekrarlanmis gorunuyor: esik-kalibrasyonu yine walk-forward'un 4 fold'unun (best_iteration
  1/3/10/3 — birbirinden farkli karmasiklikta) HAVUZLANMIS OOF tahminlerinden yapildi, final
  model (best_iteration=3) ile ayni karakterde bir alt-kumeden DEGIL. Bu, Tur 1'de tam olarak
  "esigin final modelde hicbir zaman asilamamasinin kok-nedeni" olarak tespit edilmisti ve bu
  turde de p_test max=0,5515, esik=0,575 — 0,0235 puan farkla YINE ALTINDA KALDI. **Bu, Tur 1'in
  Risk Analisti'nin yazili geri bildiriminin bu turde metodolojik olarak duzeltilmedigi
  anlamina gelir** — bu basli basina bir KIRMIZI bayrak (bilinen bir yontemsel kusurun
  tekrarlanmasi).
- **Hipotez 2 : KIRMIZI** → Multiclass'a gecisin kendisi zaten bir karmasiklik artisidir (S2
  geregi hiperparametre araligi genisletilmedi, dogru). Ancak model TEST'te "notr" sinifini
  HICBIR ZAMAN secmedi (argmax'ta notr=0) — bu, modelin egitimde gordugu 3. sinifi (%11
  agirlikla) fiilen OGRENEMEDIGINI, 2-sinifli bir siniflandiriciya COKTUGUNU gosterir; bu
  DOGRUDAN GOZLEMLENMIS bir ogrenme-basarisizligi paternidir, hipotetik bir hassasiyet
  sorusu degil. Ayrica: **k_label icin Wilder-smoothed ATR kullanimi Stratejist'in "v1 ile
  tutarlilik" varsayimina DAYANIYORDU ama bu varsayim Backtest Muhendisi'nin kod-incelemesiyle
  YANLIS cikti (v1 fiilen BASIT ATR kullaniyor)** — yani k_label esigi (0,3xATR14), Stratejist'in
  ZIHNINDEKI referans noktasindan (v1'in BASIT ATR'siyle hesaplanan bir 0,3xATR degeri) FARKLI
  bir sayisal degere karsilik geliyor olabilir (Wilder ATR genelde daha yumusatilmis/farkli
  buyuklukte). Backtest Muhendisi bunu ACIKCA raporlamis (dogru davranis) ve notr_oran (%11,0)
  kabul edilebilir aralikta ciktigi icin k_label degistirilmedi — ANCAK "k_label BASIT ATR ile
  hesaplansaydi sonuc nasil degisirdi" sorusu HIC TEST EDILMEDI. Bu, tam da bu kontrolun sordugu
  "esik degerine cok yakin bir kirilgan nokta mi" sorusudur ve yaniti YOK — KIRMIZI.

**[8] Gercek Hayat Duzeltmesi**

- **Hipotez 1 : KIRMIZI** → 0 islem uzerinden duzeltilecek bir Net Kar/PF yok; gercek hesapta
  bu model mevcut haliyle hicbir islem acmaz (ne kar ne zarar, sadece firsat maliyeti).
- **Hipotez 2 : KIRMIZI** → Maliyet modeli zaten tick-bazli gercek bid/ask + slipaj + spread/2
  olarak net_pts'e uygulanmis (Backtest Muhendisi'nin standart yontemi) — bu nedenle EK bir
  islem-basi slipaj duzeltmesi burada **UYGULANMADI (cift-sayimdan kacinmak icin, protokol
  geregi acikca boyle isaretleniyor)**. Sadece muhafazakar psikoloji/uygulama payi (%10-15
  varsayim araliginin ORTASI, %12,5 — bu ACIKCA bir VARSAYIMDIR, projeden/raporda verilmis
  bir deger DEGIL) uygulandi: Duzeltilmis Net Kar = -32,57 - (-32,57×0,125) ≈ **-28,50 USD**.
  Bu hesap zaten NEGATIF bir sonucu marjinal olarak degistiriyor (yon-mantiksal olarak,
  "psikoloji payi" formulu kaybi buyutmek icin tasarlanmis degil, kazanci kirpmak icin
  tasarlanmis — zaten kayipta olan bir sonucta bu formulun ANLAMI SINIRLIDIR). Asil ve
  degismeyen sonuc: **duzeltmeden ONCE bile PF=0,781, HEDEF_PF=1,5'in cok altinda** — gercek
  hayat duzeltmesi sonucu DEGISTIRMEZ, sadece zaten-basarisiz bir sonucu teyit eder. KIRMIZI.

---

## --- OZET ---

**Guclu Yanlar:**
- Metodoloji her iki hipotezde de S2/S1 standartlarina saglam sekilde uyuyor: purged/embargolu
  walk-forward, test-seti tek-kullanim, feature-sizinti kontrol listesi (Grup B icin 5 ayri
  BAGIMSIZ kod-incelemesi kontrolu dahil — shift(1) assert, ilk-gun/hafta NaN assert, 3-ornek
  spot-check, 20-gun pencere sinir kontrolu, DST-anomali taramasi, HEPSI GECTI) tam teyit edildi.
- DST/saat-eslesme bagimsiz iki kez (H1 ve H2 ayri ayri) yeniden dogrulandi, tutarli sonuc.
- Backtest Muhendisi, ATR-tanimi tutarsizligini (Wilder vs BASIT) VE feature-seti farkliligini
  (29 vs 27 sutun, paralel calisma sonucu) SESSIZCE COZMEDEN ACIKCA raporladi — bu seffaflik
  degerlidir ve Risk Analisti'nin bu bulgulari degerlendirebilmesini SAGLADI.
- Hipotez 1'in Grup B feature'lara agirlik vermesi (ozellikle dist_weekly_pivot_pts) ve Hipotez
  2'nin fiilen islem uretmesi, Tur 1'e kiyasla modelin en azindan FARKLI bir davranis
  sergiledigini gosteriyor — "hicbir sey degismiyor" seklinde otomatik/kor bir tekrar degil,
  gercek bir izole-degisken testi yapilmis.

**Zayif Yanlar / Riskler:**
- Hipotez 1: TEST AUC (0,5190) hala rassal-seviyede, 0 islem — Grup B'nin feature-onem agirligi
  kazanmasi (~%40) TEST performansina veya tetiklenme davranisina HICBIR OLCULEBILIR ETKI
  yapmadi.
- Hipotez 2: PF=0,781 (hedefin ~%52'si), n=15 (MIN_SAMPLE=30'un altinda), TEST accuracy trivial
  taban cizgisinin ALTINDA, model "notr" sinifini hic ogrenemedi (fiilen 2-sinifli davraniyor).
- Tur 1'de Risk Analisti'nin yazili olarak talep ettigi esik-kalibrasyon duzeltmesi (final
  modelle AYNI karakterdeki OOF'tan kalibrasyon) bu turde de UYGULANMADI — bilinen bir
  yontemsel kusur tekrarlaniyor.
- k_label (Wilder ATR) ile Stratejist'in zihnindeki "v1 ile tutarlilik" niyeti (fiilen BASIT
  ATR) arasindaki fark, k_label'in sensitivity'sinin hic test edilmemesiyle birlesince,
  Hipotez 2 sonucunun ne kadar bu spesifik ATR seciminden kaynaklandigi BELIRSIZ.
- Islem-bazli log (pes-pese-kayip, kar-konsantrasyonu) Hipotez 2 icin raporda YOK — n=15 zaten
  yetersizken bu ek bir gorunmezlik katmani yaratiyor.

---

## --- KARAR GEREKCE ---

Hipotez 1, Karar Cercevesi'nin en agir RED durumuna (gorulmemis veride PF/WR/DD hic
olculemiyor, 0 islem) ulasir — 8 kontrolden 7'si (6. N/A) KIRMIZI. Hipotez 2, ayri ve BAGIMSIZ
bir gerekceyle RED'dir: PF=0,781 HEDEF_PF=1,5'in cok altinda (RED kriteri "hedefin ~%65'inden
az" ACIKCA saglaniyor), TEST siniflandirma performansi trivial taban cizgisinin altinda, ve
n=15 MIN_SAMPLE=30'un altinda oldugu icin zaten "tek basina karar dayanagi olamaz" statusunde.
Iki hipotez de kendi bagimsiz RED gerekcesiyle KARAR Cercevesi'ndeki esikleri asiyor — birlikte
degerlendirildiginde Tur 2'nin nihai sonucu **RED**'dir.

---

## --- TUR 1 iLE PATERN KARSILASTIRMASI (S3 Governance icin ozel bolum) ---

Orkestrator'un ozellikle istedigi karsilastirma: Tur 1'in RED paterni **UC PARCALI** bir
imzaydi — (a) model AUC rassal-seviye, (b) ANA feature gruplarinin (ATR/trend/confluence)
onem agirligi NEREDEYSE SIFIR, (c) esik-kalibrasyonunda TUM adaylar 0-islem uretti.

**Bu turde (Tur 2) bu ucu parcanin durumu:**

| Parca | Hipotez 1 (v2) | Hipotez 2 (v2) | Tur 1 ile ayni mi? |
|---|---|---|---|
| (a) AUC/ayirt-edicilik rassal-seviye | EVET (TEST AUC=0,5190) | KISMEN FARKLI OLCUM — accuracy trivial-tabanin ALTINDA (bu "rassal" degil, "rassaldan da kotu" bir bulgu, farkli nitelikte bir zayiflik) | Kismen — H1 ayni, H2 farkli/daha agir |
| (b) Ana feature-onem NEREDEYSE SIFIR | **HAYIR — TERSI GOZLEMLENDI.** Grup B feature'lari (~%40 agirlik, dist_weekly_pivot_pts tek basina en yuksek) BASKIN. Yakinlik-bayraklari (0 agirlik) ve bazi Grup1/2 feature'lari hala sifir ama GENEL BASKIN PATERN artik "her sey sifir" degil, "Grup B'ye yogunlasma" | **HAYIR — TERSI GOZLEMLENDI.** Grup B (roll20_low/high, weekly_pivot) split-sayisi Hipotez1'den bile DAHA YUKSEK (79/53/47) | **BELIRGIN FARKLI — bu parca Tur1'de KIRILDI** |
| (c) 0-islem esik-kalibrasyonu | EVET (0 islem, Tur1 ile ayni) | **HAYIR — TERSI GOZLEMLENDI.** 15 islem uretildi (n<MIN_SAMPLE ama SIFIR DEGIL) | **H2'de bu parca da KIRILDI** |

**Benim degerlendirmem (Risk Analisti gorusu, nihai governance karari Orkestrator'a aittir):**
Bu turun sonucu Tur 1 ile **AYNI PATERN DEGILDIR** — sadece nihai KARAR (RED) ayni, ama RED'e
goturen TANI IMZASI (signature) belirgin sekilde degisti. Ucu parcali orijinal patern'in
UCUNCU parcasinin (b, feature-onem) HER IKI hipotezde de, ve IKINCI parcasinin (c, 0-islem)
Hipotez 2'de ACIKCA KIRILDIGINI goruyorum:
- Hipotez 1'in "model farkli feature'lara agirlik veriyor ama performans/tetiklenme AYNI kaliyor"
  bulgusu, Tur 1'in "hicbir feature'a bakmiyor" bulgusundan NITEL olarak FARKLI bir ara-durumdur
  (Backtest Muhendisi'nin kendi ifadesiyle: "feature-agirlik-degisimi vs performans-degisimi"
  ayrimi, bu ayrimin KENDISI Tur 1'de YOKTU cunku o zaman ayirt edilecek bir agirlik-degisimi
  bile yoktu).
- Hipotez 2'nin **15 gercek islem uretmesi** (PF=0,781 ile basarisiz olsa da), Tur 1'in HICBIR
  hipotezinde (H1/H2/H3, ucu de 0 islem) GORULMEMIS bir davranistir — bu, "esik-kalibrasyonu
  hicbir zaman asilamiyor" seklindeki Tur 1 paterninin en azindan BIR degiskende (3-sinifli
  etiket) kirildigini gosterir.
- Ancak: bu farkliliklarin HICBIRI, nihai PRATIK sonucu (RED, hedefe ulasamama) DEGISTIRMEDI —
  Hipotez 1 hala kullanilamaz (0 islem), Hipotez 2 hala kullanilamaz (yetersiz n + hedefin
  altinda PF + trivial-tabanin altinda accuracy + notr-cokmesi). Yani: **RED KARARI Tur 1 ile
  AYNI, ama bu RED'in ALTINDA YATAN SEBEP artik "model hicbir sey ogrenmiyor" degil, "model bir
  seyler ogreniyor (Grup B'ye yogunlasiyor, bazi islemler uretiyor) ama ogrendigi sey pratikte
  kullanilabilir/karli bir sinyale DONUSMUYOR."** Bu, arastirma yonu acisindan ONEMLI bir ayrimdir
  — Tur 1'in "feature seti/etiket TASARIMININ KENDISI yetersiz, hicbir sinyal yok" sonucundan
  daha ince/farkli bir teshise isaret eder: "Grup B GERCEKTEN bir seyler 'yakaliyor' olabilir,
  ama mevcut model/esik/hedef-tanimi bunu KARLI bir islem akisina cevirecek kadar GUCLU/TEMIZ
  degil."

**Sonuc olarak S3 sayaci konusundaki gorusum:** Bu turun sonucu Orkestrator'un aradigi
"AYNI PATERN" tanimini (rassal AUC + neredeyse-sifir feature-onem + 0-islem) **TAM OLARAK
KARSILAMIYOR** — ikinci ve ucuncu parca en az bir hipotezde acikca kirilmis durumda. RED
kararinin kendisi degismez, ama bu bulgunun Tur 1 ile "birebir ayni tekrar" olarak
degerlendirilip S3 sayacinin otomatik 2/2'ye gecirilmesi, bence teknik olarak tartismalidir —
nihai governance yorumu ve karari Orkestrator'a aittir, ben sadece bu ayrimi acikca
raporluyorum.

---

## --- STRATEJISTE GERI BILDIRIM ---

1. **Esik-kalibrasyon metodolojisi HALA duzeltilmedi (tekrar, ONCELIKLI):** Tur 1'de yazili
   olarak talep edilen duzeltme ("kalibrasyon final modelle AYNI karakterdeki fold'dan/kendi
   OOF'undan yapilmali, farkli-karmasiklikta 4 fold'un HAVUZLANMIS tahminlerinden DEGIL") bu
   turde de uygulanmadi — Hipotez 1'de yine ayni yapisal sonuc (kalibre esik final modelde
   HICBIR ZAMAN asilamiyor) gozlendi. Bir sonraki tur ONCE bu metodolojik duzeltmeyi
   uygulamali, yoksa esik-kalibrasyonu her seferinde yaniltici kalabilir.
2. **ATR tanimi (Wilder vs BASIT) netlestirilmeli ve sensitivity test edilmeli:** k_label icin
   Wilder ATR kullanimi, Stratejist'in "v1 ile tutarlilik" niyetiyle FIILEN ORTUSMUYOR (v1 BASIT
   ATR kullaniyor). Bu, kotu bir uygulama degil ama TEST EDILMEMIS bir varsayim biriktiriyor —
   bir sonraki turde k_label'in BASIT ATR ile hesaplanmasi durumunda notr_oran/sonuc nasil
   degisir, bu ayrica denenmeli (S2 Madde4 geregi, egitimden once, test setine bakmadan).
3. **Hipotez 2'nin "notr" sinifini hic ogrenmemesi ayri bir tasarim sorunu olarak ele
   alinmali:** Model TEST'te argmax olarak notr'u HICBIR ZAMAN secmedi — bu, 3-sinifli
   deadzone yaklasiminin, en azindan mevcut k_label/feature/hiperparametre kombinasyonuyla,
   ORTA bandi ayirt edemedigini gosteriyor. Bir sonraki turde class-weight dengeleme, farkli
   k_label degeri veya notr'a ozel bir esik/karar kurali denenebilir.
4. **Grup B "bir seyler yakaliyor olabilir" sinyali daha temiz bir tasarimla yeniden test
   edilmeli:** Feature-onem agirliginin Grup B'ye kaymasi (iki hipotezde de) ve Hipotez 2'nin
   (basarisiz olsa da) fiilen islem uretmesi, Grup B'nin TAMAMEN degersiz olmadigina isaret
   eder. Ancak mevcut kurulum (N=16/k=1,5, ikili veya 3-sinif) bunu karli bir sinyale
   cevirmiyor. Onerilen yon: Grup B'yi TEK BASINA (Grup 1-5 olmadan) veya farkli bir N/ufuk
   ile izole test etmek, "Grup B'nin katkisi digerlerinin gurultusune mi gomuluyor" sorusuna
   yanit verebilir.
5. **Hipotez 2 icin islem-bazli log talep edilmeli:** Eger Grup B/3-sinif kombinasyonu bir
   sonraki turde tekrar denenirse, Backtest Muhendisi'nden pes-pese-kayip ve kar-konsantrasyonu
   hesaplanabilecek TAM islem logu (sadece agregat degil) istenmeli — bu turde bu detay
   eksikti.
6. **S1 P90-stres testi hatirlatmasi (her iki hipotezde AYNI, Tur1'den devam eden risk):**
   k_risk=1,5xATR14 medyan-spread'de esigi geciyor (15,97x) ama P90 stres testinde kaybediyor
   (11,91x<15,0x) — bu HALA cozulmedi, bir sonraki tur bu barrier genisligini (veya farkli bir
   risk parametresini) yeniden gozden gecirmeli.

---

## --- KULLANICIYA ---

Justin projesinin makine ogrenmesi denemesinin ikinci turu (feature listesine "fiyatin son
gunlere gore nerede oldugu" bilgisini ekleyen ve ayrica "kesin yon" yerine "yukari/asagi/notr"
seklinde 3 secenekli bir tahmin deneyen iki farkli tasarim) incelendi. Sonuc yine
onaylanamadi (KARAR: RED), ama bu sefer nedeni biraz farkli: birinci tasarim (ikili tahmin)
yine hicbir islem acacak kadar kendinden emin olmadi (0 islem) — ancak bu sefer model, en
azindan HANGI bilgiye baktigini degistirdi (yeni eklenen "fiyat-konumu" bilgisine agirlik
verdi), sadece bu degisiklik sonucu iyilestirmedi. Ikinci tasarim (3 secenekli tahmin) ise
ilk kez GERCEKTEN islem acti (15 islem) ama bu islemler toplamda zarar etti (kazandigindan
fazlasini kaybetti) ve zaten cok az sayida islem oldugu icin bu sonuca guvenilemez — ayrica
model, kendisine ogretilen "orta/belirsiz" secenegini test doneminde hic kullanmadi, bu da
tasarimin tam calismadigini gosteriyor. Ozetle: bu ikinci deneme bir onceki turden biraz farkli
davransa da (tamamen kor bir tekrar degil), hala gercek hesaba/ilerki asamaya hazir degil.
Stratejist'e somut, onceki turden devraln bir metodolojik eksiklik dahil, alti maddelik somut
duzeltme/arastirma onerisi iletildi.
