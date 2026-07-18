# RISK ANALISTI RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following) — TAM TUR 1

Tarih: 2026-07-13
Kapsam: H1 ("Dar-Kanit M5-Giris"), H2 ("Genis-Orneklem M15-Giris"), H3 ("M30-Yukselen Odakli
Asimetrik Filtre") — Stratejist'in Tam Tur 1'de urettigi UC hipotez, BIRLIKTE degerlendirildi.
Girdi: Stratejist raporu + 3 Backtest Muhendisi raporu (bkz. gorev tanimi, dosya yollari orada
listelenmis).

**Hedef kriterler (justin_gecmis_calisma.md'den alindi, uydurulmadi):**
HEDEF_PF = 1,5 | HEDEF_DD = %20 (KUMULATIF/TOPLAM DONEM, gunluk degil) | Kasa = 2.000 USD |
Islem-basi risk ust siniri = %1 | Taban lot 0,01, her 2.000 USD = +0,01 lot.
Varsayilan tolerans (proje ozel bir esik belirtmedigi icin): OOS/Test PF icin hedefin ~%80-85'i
(~1,2-1,275) kabul edilebilir alt sinir; hedefin ~%65'inin (~0,975) altinda RED otomatik. Bu
oran, sistem promptunun "Karar Cercevesi" bolumundeki genel varsayilan tolerans kuralindan
turetilmistir — proje bu orani ayrica belirtmedi.

**Bagimsiz dogrulama notu (onemli):** Asagidaki Monte Carlo, pes-pese-kayip, kar-konsantrasyonu
ve DD-stop-restart-simulasyonu rakamlari, Backtest Muhendisi'nin rakamlarina GUVENILMEDEN, ham
islem loglari (`backtest_A_ailesi_H1/H2/H3_islem_logu_*.csv`) uzerinde bu rapor icin BAGIMSIZ
olarak (Python, 500-shuffle Monte Carlo + kronolojik DD-stop simulasyonu) YENIDEN hesaplanmistir.
Script: `risk_analisti_monte_carlo.py` (bu klasorde).

**Agent'lar-arasi sayisal tutarlilik notu (CLAUDE.md 10 Temmuz kurali uygulanmistir):** H1/H2/H3
farkli zaman-dilimi, farkli orneklem ve farkli split-metodolojisi (H1/H2 tek train/val/test,
H3 3-fold expanding-window) kullaniyor. Asagida hicbir PF/n sayisi "birbirinin bagimsiz
dogrulamasi" olarak sunulmamistir — her hipotez kendi icinde degerlendirilmis, sadece ORTAK
YAPISAL BULGULAR (orn. tum uc varyantta tekrarlanan "touch+devam" girisinin genelinde zayifligi)
ayrica ve acikca boyle isaretlenerek karsilastirilmistir.

---

## H1 — "DAR-KANIT M5-GIRIS"

```
=== RiSK ANALiZi RAPORU ===
Hipotez        : H1 - Dar-Kanit M5-Giris (H1/M30 Yapisal Kanal + M5 Giris-Zamanlama)
Yaklasim Turu  : Kural-tabanli
Tarih          : 2026-07-13
KARAR          : RED
```

**Rakamlar (Backtest Muhendisi'nden):** Train n=1.269 WR=7,96% PF=0,94 net=-1.631,64 USD
DD=%174,9 | Validation n=785 WR=8,92% PF=1,16 net=+2.243,28 USD DD=%42,0 | **Test (OOS, tek
kez)** n=151 WR=6,62% PF=0,80 net=-559,70 USD DD=%45,99 | Tum donem (DD-stop simule edilmeden)
n=2.642 PF=0,91 net=-4.495,02 USD, min equity -2.852 USD.

**Bagimsiz dogrulama (bu rapor):**
- Monte Carlo (Test seti, 500 shuffle, oransal): en kotu %5 DD = **%35,03** → esigin (%35)
  hemen ustunde.
- Gercek max pes-pese-kayip (Test, kronolojik) = 41; teorik beklenti (log(0,05)/log(1-WR)) =
  43,7 — gercek deger teorik beklentinin ALTINDA (anormal degil), ama parasal etki agir: 41 x
  ortalama kayip (-19,54 USD) = **-801 USD / kasanin %40,05'i** — bu TEK BASINA Justin'in %20
  kumulatif DD-stop esiginin 2 KATIDIR.
- Kar konsantrasyonu (Test): en iyi 3 islem toplam karin **%35,09'u**; en iyi 10 islem
  **%100'u** — Test setinde SADECE 10 kazanan islem var (151 islemden), TUM kar bu 10 islemden
  geliyor.
- **DD-stop restart-simulasyonu, Test penceresi TEK BASINA (kasa 2.000 USD'den bu pencerede
  YENIDEN baslatilsaydi bile):** ilk tetiklenme 34. islemde, Test'in 151 islemlik omru
  boyunca **4 kez** tetiklenirdi. Muhendis'in tam-donem bulgusuyla (ilk tetik 108. islem, Train
  icinde) birlikte okundugunda: Validation/Test'teki HERHANGI bir sonuc, operasyonel olarak
  ULASILAMAYACAK bir senaryodur.

**KONTROLLER:**
```
[1] Istatistiksel Anlamlilik      : KIRMIZI → Nominal n (151/785/1.269) yeterli GORUNUYOR, ama
                                     Muhendis'in kendi bulgusu geregi BAGIMSIZ orneklem SADECE
                                     24 kanaldir; Test donemi sadece 2-4 kanaldan geliyor. 151
                                     "islem" istatistiksel bagimsizlik TASIMIYOR.
[2] Egitim/Gorulmemis Bozulma     : KIRMIZI → Train PF 0,94 (zaten <1) → Validation PF 1,16
                                     (yon degistirdi, karli GORUNDU) → Test PF 0,80 (tekrar <1,
                                     yon degistirdi). PF bozulmasi (Val/Test) = 1,45 — YON
                                     DEGISTIREN dengesizlik, klasik "sansa dayali" isareti.
[3] Monte Carlo (%5 DD)           : KIRMIZI → %35,03 (esik %35, hemen ustunde)
[4] Pes Pese Kayip                : UYARI → 41 gercek (teorik 43,7 altinda) ama -801 USD/-%40
                                     kasa parasal etki, DD-stop esiginin 2 katini asiyor.
[5] Kar Konsantrasyonu            : KIRMIZI → En iyi 3: %35,09; en iyi 10: %100 (10/10 kazanan
                                     islem). Tek-nokta-basarisizlik riski maksimum duzeyde.
[6] Kirilim Analizi                : N/A → Raporda tf/yon bazinda ayri PF/WR tablosu verilmedi
                                     (sadece kanal SAYILARI var), sadece kanal-sayisi kirilimi
                                     mevcut (H1↑=3,H1↓=8,M30↑=6,M30↓=7 kanal).
[7] Parametre/Model Hassasiyeti    : KIRMIZI → Muhendis TEST YOK demedi ama secilen TP=10,0xATR,
                                     grid'in TARANAN EN GENIS ucudur (grid: 2/3/4/5/6/8/10) —
                                     bu, H3'te acikca flaglenen "grid-doygunlugu/sinir-secimi"
                                     ile AYNI riski tasir, bu raporun BAGIMSIZ bulgusudur (H1
                                     raporunda bu ayrica isaretlenmemisti).
[8] Gercek Hayat Duzeltmesi       : KIRMIZI → Test net zaten -559,70 USD (negatif); ek
                                     slipaj/psikoloji-payi duzeltmesi sonucu SADECE
                                     kotulestirir. Duzeltilmis PF hedefin (1,5) COK altinda.
```

**KARAR GEREKCE:** H1, nominal islem sayisi disinda hemen her boyutta zayif: gercek bagimsiz
orneklem 24 kanal (Test'te 2-4), Validation→Test PF yon-degistirerek cokuyor (1,16→0,80), Test
karinin tamami sadece 10 islemden geliyor, Monte Carlo en-kotu-%5 DD esigi asiyor, ve secilen
TP parametresi grid'in test edilen en genis ucu (dogrulanmamis bir sinir-secimi). En kritik
nokta: Muhendis'in bulgusu (DD-stop tam donemde Train icinde, 108. islemde tetiklenir) +
bu raporun bagimsiz Test-icinde-4-kez-tetiklenme bulgusu birlikte, Validation'in gosterdigi
tek pozitif sonucun dahi operasyonel olarak hic yasanmayacagini gosteriyor.

---

## H2 — "GENIS-ORNEKLEM M15-GIRIS"

```
=== RiSK ANALiZi RAPORU ===
Hipotez        : H2 - Genis-Orneklem M15-Giris (H1/M30 Yapisal Kanal + M15 Giris-Zamanlama)
Yaklasim Turu  : Kural-tabanli
Tarih          : 2026-07-13
KARAR          : RED
```

**Rakamlar (Backtest Muhendisi'nden):** Train n=6.805 WR=23,75% PF=0,7715 net=-28.157,74 USD |
Validation n=3.079 WR=24,46% PF=0,9205 net=-3.811,86 USD | **Test (OOS, tek kez)** n=2.699
WR=22,56% PF=0,9197 net=-2.982,52 USD | Grid taramasi: **12 SL/TP hucresinin HICBIRI**
Validation'da PF>=1'e ulasmadi (en iyisi 0,9205).

**Bagimsiz dogrulama (bu rapor):**
- Monte Carlo (Test seti, 500 shuffle): en kotu %5 DD = **%136,75** — matematiksel olarak
  kasanin tamamini asan bir kayip; bu, PF<1'in buyuk-orneklemli/tutarli oldugunun dogrudan
  sonucu (rastgele siralama COGUNLUKLA hesabi sifirliyor).
- Gercek max pes-pese-kayip (Test) = 23; teorik beklenti = 11,7 — **gercek deger teorik
  beklentinin ~2 KATI** (kayiplar rastgele-bagimsiz degil, KUMELENIYOR gorunuyor). Parasal
  etki: 23 x -17,76 USD = -408,54 USD (kasanin %20,43'u) — **TEK BASINA DD-stop esigini
  asiyor.**
- Kar konsantrasyonu (Test): en iyi 3 = %1,48; en iyi 10 = %4,18 — SAGLIKLI dagilim (bu, tek
  basina bir sorun degil; PF<1 sorunu zaten baska yerden geliyor).
- **DD-stop restart-simulasyonu, Test penceresi TEK BASINA:** ilk tetik 445. islemde, Test
  boyunca **102 kez** tetiklenirdi, bitis-equity NEGATIF (-982,72 USD, 2.000 USD'lik taze
  baslangictan bile). Muhendis'in tam-donem bulgusuyla (120 tetik, ilki 39. islemde/3. gun)
  BIRLIKTE: bu mekanizma, Justin'in governance kurallari altinda SUREKLI STOP-START dongusu
  yaratirdi.

**KONTROLLER:**
```
[1] Istatistiksel Anlamlilik      : GECTI (kosullu not ile) → n=2.699 (Test) buyuk/GUCLU;
                                     ancak alttaki yapisal-olay sayisi (~140 kanal, kombinasyon
                                     basina 7-19) goreceli kucuk — otokorelasyonlu gozlemler,
                                     ama H1/H3'e gore COK daha genis temelli.
[2] Egitim/Gorulmemis Bozulma     : GECTI (klasik anlamda) → PF Train 0,77 → Test 0,92, yani
                                     Test Train'den DAHA IYI (degradasyon yok, hatta ters yon).
                                     Ancak bu "iyilesme" degil "hep zayif" anlamina gelir — PF
                                     UCUNDE DE 1'in altinda, tutarli sekilde.
[3] Monte Carlo (%5 DD)           : KIRMIZI → %136,75 (kasanin tamamini asan, en agir bulgu)
[4] Pes Pese Kayip                : KIRMIZI → Gercek (23) teorik beklentinin (11,7) ~2 kati;
                                     tek seri DD-stop esigini (%20,43 > %20) TEK BASINA asiyor.
[5] Kar Konsantrasyonu            : GECTI → %1,48/%4,18, saglikli dagilim (bu boyutta sorun
                                     yok, PF<1 baska nedenden).
[6] Kirilim Analizi                : KIRMIZI (bilgilendirici) → H1-kaynakli(PF=0,8806),
                                     M30-kaynakli(PF=0,8751), BUY(PF=0,8987), SELL(PF=0,8556) —
                                     TUMU <1, HICBIR alt-kirilim filtre ile kurtarilamaz;
                                     zayiflik TEK bir segmentten degil, mekanizmanin GENELINDEN.
[7] Parametre/Model Hassasiyeti    : GECTI (test edildi, sonuc tutarli) → 12 hucrelik grid
                                     (SL 0,5/0,75/1,0 x TP 2,0/2,5/3,0/4,0, ORTA-bolgeden
                                     secildi, sinir-degil) TAMAMI PF<1 verdi — dusuk hassasiyet,
                                     ama sonuc HER ZAMAN negatif; parametre secimi sorun degil.
[8] Gercek Hayat Duzeltmesi       : KIRMIZI → Test net zaten -2.982,52 USD; duzeltme sadece
                                     kotulestirir.
```

**KARAR GEREKCE:** H2, UC boyutta da (Train/Validation/Test) PF<1 — buyuk, iyi-guclendirilmis
orneklemle (n binlerce) ve UC alt-kirilimde de (tf-kaynagi, yon) tutarli sekilde. Bu, kucuk-
orneklem gurultusu DEGIL: 12 hucrelik genis bir grid taramasinin HICBIRI PF>=1'e ulasmadi. Buna
ek olarak, operasyonel DD-stop restart-simulasyonu (hem Muhendis'in tam-donem hem bu raporun
Test-ici bagimsiz kontrolu) mekanizmanin gunluk-pipeline governance kurallari altinda SUREKLI
mudahale gerektirecegini gosteriyor. Bu, uc hipotez arasinda EN GUCLU/EN NET RED'dir — "sansa
bagli kucuk-orneklem" degil, "mekanizma bu haliyle calismiyor" sonucudur.

---

## H3 — "M30-YUKSELEN ODAKLI ASIMETRIK FILTRE"

```
=== RiSK ANALiZi RAPORU ===
Hipotez        : H3 - M30-Yukselen Odakli Asimetrik Filtre (SADECE M30 yukselen kanal + M15
                 giris, yalniz BUY/uzun)
Yaklasim Turu  : Kural-tabanli (yon-asimetrik filtre)
Tarih          : 2026-07-13
KARAR          : RED
```

**Rakamlar (Backtest Muhendisi'nden, 3-fold expanding-window):** Fold1 Train n=268 PF=0,8513 /
Test n=764 PF=0,7776 | Fold2 Train n=1.032 PF=0,7959 / Test n=576 PF=1,0340 | Fold3 Train
n=1.608 PF=0,8734 / Test n=742 PF=1,0616 | **Havuzlanmis OOS** n=2.082 WR=17,77% PF=0,9376
net=-2.115,56 USD. Bagimsiz orneklem: sadece **19** M15-kesisen kanal.

**Bagimsiz dogrulama (bu rapor):**
- Monte Carlo (Havuzlanmis OOS, 500 shuffle): en kotu %5 DD = **%104,38** — kasanin tamamini
  asan, H2'ninkine yakin agirlikta bir bulgu.
- Gercek max pes-pese-kayip = 41; teorik beklenti = 15,3 — **gercek deger teorik beklentinin
  ~2,7 KATI**, uc varyant arasinda EN BUYUK sapma. Parasal etki: 41 x -19,82 USD = -812,47 USD
  (kasanin %40,62'si) — DD-stop esiginin 2 katini asiyor.
- Kar konsantrasyonu: en iyi 3 = %2,28; en iyi 10 = %5,44 — saglikli dagilim.
- **DD-stop restart-simulasyonu, Havuzlanmis OOS TEK BASINA:** ilk tetik SADECE **20. islemde**
  (uc varyant arasinda EN ERKEN), 2.082 islemlik pencerede **68 kez** tetiklenirdi, bitis-equity
  hafif negatif (-115,56 USD, taze 2.000 USD baslangictan). **Muhendis bu simulasyonu H3 icin
  yapmamisti — bu raporun doldurdugu bir bosluktur** ve sonuc, uc varyant arasinda en HIZLI
  DD-stop tetiklenmesidir.

**KONTROLLER:**
```
[1] Istatistiksel Anlamlilik      : KIRMIZI → Bagimsiz orneklem SADECE 19 kanal (M15-kesisen);
                                     devam-orani coklu-blok testinde bloklar n=4-12 (COK kucuk,
                                     %25-100 arasi genis salinim). Uc varyant arasinda EN kucuk
                                     bagimsiz temel.
[2] Egitim/Gorulmemis Bozulma     : GECTI (teknik anlamda, ama yaniltici olabilir) → Train PF
                                     hicbir foldda/hucrede 1'i gecemedi (0,80-0,87); Test PF
                                     2/3 foldda hafifce >1 (1,03/1,06) — KLASIK cokme YOK
                                     (Muhendis'in OVERFITTING_RISKI=Hayir bulgusu dogru), AMA
                                     bu "dogrulanmis edge" ANLAMINA GELMEZ — Train'in KENDISI
                                     hicbir zaman PF>1 uretemedigi icin Test'teki ~1 civari
                                     PF, "zayif/notr edge etrafinda gurultu" ile ES DERECEDE
                                     TUTARLIDIR.
[3] Monte Carlo (%5 DD)           : KIRMIZI → %104,38 (kasayi asan)
[4] Pes Pese Kayip                : KIRMIZI → Gercek (41) teorik beklentinin (15,3) ~2,7 kati —
                                     uc varyant arasinda EN BUYUK sapma, kayip-kumelenmesi
                                     riski en yuksek.
[5] Kar Konsantrasyonu            : GECTI → %2,28/%5,44, saglikli.
[6] Kirilim Analizi                : KIRMIZI → Devam-orani blok-bazinda %25-100 arasi genis
                                     salinim (n=4-12); fold-Test PF'leri de (0,78→1,03→1,06)
                                     blok-blok tutarsiz. Trade-PF ile devam-orani DOGRUDAN
                                     karsilastirilamaz (Muhendis'in notu), ama HER IKI olcut
                                     de kucuk-n kaynakli oynaklik gosteriyor.
[7] Parametre/Model Hassasiyeti    : KIRMIZI → Muhendis'in KENDISI acikca flagliyor: UCU DE
                                     fold, grid'in test edilen EN GENIS TP ucunu (5,0xATR)
                                     sectI — "3/3 fold tutarli" degil "grid doygunlugu/sinir-
                                     secimi" olarak okunmali; daha genis TP test EDILMEDI.
[8] Gercek Hayat Duzeltmesi       : KIRMIZI → Havuzlanmis OOS net zaten -2.115,56 USD;
                                     duzeltme sadece kotulestirir.
```

**KARAR GEREKCE:** H3'un temel iddiasi (M30-yukselen'in en tutarli/en az riskli alt-kume
oldugu) kismen dogrulaniyor GORUNSE de (devam-orani orijinal bulguyla kabaca ayni mertebede
kaliyor), trade-seviyesi PF sonucu (Havuzlanmis OOS 0,9376) hedefin (1,5) cok altinda ve HICBIR
foldda Train PF 1'i gecmiyor — yani grid'in "en iyi" secimi bile zayif. Grid'in ucu de
sinirinda doymus olmasi (5,0xATR), secilen parametrenin GERCEK bir optimum degil bir ARTEFAKT
olabilecegini gosteriyor. En kucuk bagimsiz orneklem (19 kanal) + en agir kayip-kumelenmesi
sapmasi (2,7x teorik) + en erken DD-stop tetiklenmesi (20. islemde) bu hipotezi de RED yapiyor.

---

## GENEL SENTEZ — A AILESI TAM TUR 1

### Nihai Karar Tablosu

| Hipotez | Karar | Ana Gerekce (mekanizma-bazinda, BAGIMSIZ) |
|---|---|---|
| H1 — Dar-Kanit M5-Giris | **RED** | Cok kucuk bagimsiz orneklem (24 kanal), Validation→Test PF yon-degistirerek cokuyor, kar %100 oraninda 10 islemde konsantre, operasyonel olarak ulasilamaz sonuc |
| H2 — Genis-Orneklem M15-Giris | **RED** (en net/en guclu) | Buyuk, iyi-guclendirilmis orneklemle UCUNDE de PF<1, TUM alt-kirilimlerde tutarli zayiflik, 12 hucrelik grid'in TAMAMI basarisiz, DD-stop governance altinda surekli mudahale gerektirir |
| H3 — M30-Yukselen Asimetrik Filtre | **RED** | En kucuk bagimsiz orneklem (19 kanal), grid sinirda doymus (gercek optimum degil), en agir kayip-kumelenmesi sapmasi, en erken/en sik DD-stop tetiklenmesi |

**Onemli — Stratejist'in atif-netligi ilkesi geregi (mekanizma bagimsizligi):** Uc RED, UC
FARKLI nedenden geliyor ve birbirinin otomatik dogrulamasi/gucculendirmesi olarak
OKUNMAMALIDIR:
- **H1 RED nedeni** = kirilganlik/kucuk-orneklem + istatistiksel sans (Validation'in tek
  seferlik iyimser gorunumu).
- **H2 RED nedeni** = genis-orneklemli, tutarli, GERCEK edge-yoklugu — bu, "touch+devam-tetigi"
  giris mekanizmasinin KENDISI hakkinda en guclu/en az belirsiz kanittir.
- **H3 RED nedeni** = kucuk-orneklem + grid-artefakti; devam-orani bulgusu kismen dogrulaniyor
  ama trade-PF'ye donusmuyor.

**Ancak bir ORTAK YAPISAL GOZLEM (bu, "A ailesi olu" degil, ODAKLANMIS bir tespit — acikca
boyle isaretleniyor):** H2'nin genis-orneklemli/tum-alt-kirilimlerde-tutarli RED'i, ozellikle
carpici: "H1/M30 yapisal kanal onayi + M5/M15 dokunus-devam girisi" mekanizmasinin KENDISI
(sadece bir parametre/ufuk secimi degil), bu veri setinde ve bu haliyle pozitif bir edge
uretmiyor GORUNUYOR. H1 ve H3'un RED'i kucuk-orneklem/kirilganlik nedeniyle daha az kesin
olsa da, HICBIRI bu tabloyu curutecek GUCLU bir pozitif kanit sunmuyor. Bu gozlem KARAR
DEGILDIR (Risk Analisti'nin gorevi bu degil) — sadece Orkestrator/Stratejist'in Adim 2 acik
sorusunu (C ailesine gecis mi, yoksa A'nin baska bir mekanizma varyanti mi) degerlendirirken
goz onunde bulundurmasi gereken bir BULGUDUR.

### Onceki-Tur-Ayrisma-Teyidi
N/A — Stratejist raporunun da belirttigi gibi bu A ailesinin ILK tam turudur; karsilastirilacak
onceki bir A-ailesi kural-tabanli turu yoktur. Bu madde Tur 2'den itibaren zorunlu olacaktir.

### Gunluk Pipeline Tur-Sayaci
**Tam Tur 1 KAPATILIYOR — sayac: 1/5.** Uc hipotezin UCU de RED; sayac Orkestrator'un
belirledigi 5 tur sinirinin altinda, otomatik devam icin engel yok (bilgi notu yeterli, onay
gerekmez — CLAUDE.md Mimari Boyut E).

### Tur 2 Onerisi (ON-GORUS — nihai karar Orkestrator'a aittir)
Risk Analisti'nin onerisi: Tur 2'ye devam edilebilir (sayac musait), AMA yeni tur, Ertan'in
Cevap-1 kuralina (mekanizma/mantik duzeyinde GERCEK ayrisma, sadece parametre degisikligi
degil) uygun olarak, **"kanal-onayi + dokunus-devam girisi" mekanizmasinin KENDISINI** sorgulayan
farkli bir yaklasim icermelidir — cunku H2'nin genis-orneklemli/tum-alt-kirilimlerde-tutarli
RED'i, bu spesifik giris mekanizmasi hakkinda guclu negatif kanit tasiyor. Salt SL/TP
yeniden-kalibrasyonu veya farkli bir ufuk (H1 veya H3 gibi) secmek, Ertan'in "ayni seyi
yuzeysel farkli tekrar uretme" endisesine (Cevap 1) girebilir. Somut oneriler (Stratejist'e
devir icin, karar degil):
1. Giris tetigini "dokunus + hemen-devam" yerine farkli bir mantiga (orn. gecikmeli teyit,
   momentum-esikli kirilim, veya kanal-ici degil kanal-disi bir tetik) degistirmek.
2. H3'un devam-orani bulgusunu (M30-yukselen'in goreceli tutarliligi) trade-mekanigi DISINDA,
   farkli bir giris-yontemiyle (M15 dokunus-devam disi) yeniden sinamak.
3. Grid'in H1/H3'te sinirda doydugu (TP=10x, TP=5x, test edilen en genis uc) goz onune
   alinarak, eger benzer bir mekanizma tekrar denenecekse grid daha genis ve/veya farkli bir
   ust sinirla test edilmeli — ama bu, yeni turun "mekanizma-duzeyinde farkli" sartini TEK
   BASINA KARSILAMAZ (Ertan'in kuralinin ihlali riski).

---

## STRATEJISTE GERI BILDIRIM

**H1 icin:**
- Bagimsiz orneklem (24 kanal, Test'te 2-4) bu mekanizmayi guvenilir sekilde degerlendirmek
  icin yetersiz. Farkli/genis M5 veri donemi (broker kisitliyor, bu tur icin cozulemedi) hala
  acik bir ihtiyac.
- Kar konsantrasyonunun TEK 10 islemde toplanmasi, bu hipotezi "birkac ozel olayin siz-birakti"
  riskine acik biraliyor — Stratejist farkli bir giris-esigi/tetik dusunurse bu riski
  azaltabilir mi diye degerlendirebilir.

**H2 icin:**
- Grid'in TAMAMININ PF<1 vermesi, bu spesifik giris mekanizmasinin (kanal-onay + M15
  dokunus-devam) bu haliyle terk edilmesi gerektigini gosteriyor — SL/TP yeniden-kalibrasyonu
  degil, mekanizma degisikligi onerilir (bkz. Tur 2 onerisi yukarida).
- Tek-pozisyon muhendislik karari (Backtest Muhendisi'nin kendi engineering karari, Stratejist
  talimat vermemisti) farkli sonuc verebilir — eger bu mekanizma bir sekilde tekrar denenecekse,
  Stratejist pozisyon-yonetim politikasini (tek vs cok-pozisyon) ACIKCA belirtmeli.

**H3 icin:**
- Grid'in sinirda doymus olmasi (TP=5,0xATR, test edilen en genis deger, UCU DE foldda secildi)
  onemli bir metodolojik uyari: eger bu asimetrik-filtre fikri tekrar denenecekse, TP grid'i
  daha genis (6x, 8x, 10x...) test edilmeli — mevcut sonuc "5x en iyisiydi" degil "5x test
  edilen en genisti" anlamina geliyor.
- Devam-orani bulgusu (M30-yukselen'in goreceli tutarliligi) ilginc kalmaya devam ediyor ama
  cok kucuk n (19-29 kanal) ile sinirlanmis kaliyor — bu YAPISAL bulgu (asimetri fikri) farkli
  bir giris-mekanizmasiyla (M15 dokunus-devam DISINDA) ayrica sinanabilir.

---

## KULLANICIYA

Justin projesinin A ailesindeki uc hipotezin (H1, H2, H3) UCU de bu ilk test turunde
REDDEDILDI — hicbiri demo veya canli hesaba baglanmaya hazir degil, bu asamada hicbir sistem
kod veya hesap degisikligi yapilmadi (salt analiz). En net RED, en genis veriyle test edilen
H2'de cikti: bu yontem, farkli zaman dilimlerinde ve farkli alt-gruplarda tutarli sekilde
zarar ediyor, yani "biraz ayarlarsak duzelir" degil "bu fikir bu haliyle calismiyor" sonucuna
isaret ediyor. H1 ve H3 ise daha az kesin sekilde RED — cok az sayida gercek/bagimsiz ornek
(sirasiyla 24 ve 19 "olay") uzerine kurulu olduklari icin sonuclari guvenilir bulunmadi, "kotu"
degil "henuz kanitlanmamis/riskli" durumundalar. Uc yontemde de, eger canli calismis olsaydi,
Justin'in kendi guvenlik kurali (kasa %20 dustugunde islemi otomatik durdurma) cok sik devreye
girerdi — bu da gunluk operasyon acisindan pratik degil. Bugunku gunluk deneme sayaci 1/5'e
ulasti, bu bir sorun degil; ekip farkli bir yeni fikir denemeye devam edebilir, ama tavsiyemiz
aynı giris mantığının (fiyatın bir çizgiye dokunup hemen devam etmesini bekleme) küçük
ayarlarla tekrar denenmesi değil, temelden farklı bir giriş fikri denenmesi yönünde — çünkü en
güvenilir test (H2) tam olarak bu mantığın kendisinin işe yaramadığını gösterdi.

---

## EK — BAGIMSIZ HESAPLAMA DETAYI

Kullanilan script: `C:\MilaYatirim\Justin\risk_analisti_monte_carlo.py` (Monte Carlo %5-DD,
gercek max pes-pese-kayip, kar-konsantrasyonu) + ayri bir DD-stop restart-simulasyon script'i
(bu rapor icin, Test/OOS pencereleri TEK BASINA/taze-2.000-USD varsayimiyla kosturuldu — Tam
donem/Train-dahil simulasyonlari zaten Backtest Muhendisi'nin H1/H2 raporlarinda mevcuttur, bu
rapor sadece Test/OOS-icindeki ek riski ortaya cikarmak icin tamamlayici bir kontrol yapmistir).
Ham CSV kaynaklari: `backtest_A_ailesi_H1_islem_logu_tam.csv`,
`backtest_A_ailesi_H2_islem_logu_tam.csv`, `backtest_A_ailesi_H3_islem_logu_oos.csv`.

Sinirlama: H3 icin TAM-DONEM (Train-dahil, tek sürekli hesap) DD-stop simulasyonu bu raporda
DA yapilamadi — H3'un fold yapisinda Train pencereleri fold'lar arasinda ORTUSUYOR (fold2
Train = blok1+2, fold3 Train = blok1+2+3), bu yuzden tekilleştirilmemiş bir "tek sürekli hesap
gecmisi" turetmek bu veri kumesinden dogrudan mumkun degildi. Bu, Backtest Muhendisi'ne/
Orkestrator'a acik bir bosluk olarak bildirilmelidir — ozellikle H3'un Test-icinde-bile-erken-
tetiklenme (20. islem) bulgusu goz onune alindiginda, Train-dahil tam resmin de muhtemelen
agir olacagi TAHMIN edilebilir ama DOGRULANMADI.

---

## ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik degerlendirmedir, canli sisteme hicbir dokunus
yoktur (Justin arastirma asamasinda, canli/demo hesap henuz baglanmadi). Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir, onay GEREKMEZ
(STOP-genis/bilgi-notu kategorisi). Uc hipotezin UCU de RED oldugu icin, "demo/canli hesaba
baglanmaya hazir" tavsiyesi bu raporda YOKTUR — dolayisiyla ayrica bir gecis-onayi sorusu da
bu asamada gundeme gelmemektedir.
