=== RISK ANALIZI RAPORU ===
Hipotez        : LightGBM Ikili Yon-Tahmini Modeli (N=16 M15-bar / k=2,0xATR14-M15) — HIPOTEZ 3
                 (Hipotez 1'in guvenlik-marji/duyarlilik varyanti, DUZELTILMIS esik-kalibrasyon
                 yontemiyle)
Yaklasim Turu  : Makine Ogrenmesi — Gradient Boosting (LightGBM, binary classifier) — Justin/ML
                 ailesinin Risk Analisti tarafindan degerlendirilen 3. hipotezi
Tarih          : 2026-07-12
KARAR          : RED

---

## ON-NOT — BAGIMSIZ DOGRULAMA

Backtest Muhendisi'nin raporu (`backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez3_
20260712.md`) ile ham cikti dosyasi (`backtest_ml_v1_hipotez3_output.json`) satir satir
karsilastirildi: walk-forward AUC degerleri (fold 1-4: 0,4965/0,5149/0,4973/0,5209,
ortalama=0,5074/std=0,0107), final model ic-validasyon AUC'u (0,5209, best_iteration=1), TEST
AUC'u (0,5211), esik-kalibrasyonu aday tablosu (0,60/0,40, 0,575/0,425, 0,55/0,45 — UCUNDE de
long_n=short_n=0), S1 oranlari (medyan 21,29x / P90 15,88x) ve PRIMARY/SUPPLEMENTARY islem
sayilari (ikisi de 0) — HAM JSON ile RAPOR arasinda hicbir sayisal tutarsizlik bulunamadi. Rapor
guvenilir kaynak olarak kabul edildi; asagidaki 8 kontrol kendi bagimsiz yorumumla, Hipotez 1/2
degerlendirmelerimden BAGIMSIZ olarak (onlarin RED sonucu bu turun kararini yonlendirmeden)
uygulanmistir.

**Esik-kalibrasyon duzeltmesinin ayrica dogrulanmasi (gorev talimati geregi, Kontrol [7] altinda
detaylandirilmistir):** JSON'daki `esik_kalibrasyonu_yontemi_duzeltmesi` ve `esik_kalibrasyonu`
bloklari teyit edildi — kalibrasyon kaynagi artik SADECE `final_innerval_idx` (n=12.219, final
model tarafindan gradyan-guncellemesi icin degil sadece early-stopping eval_set olarak
kullanilan kesit), 4-fold havuzlanmis OOF HICBIR yerde kullanilmiyor. Bu, Hipotez 1 raporundaki
Geri Bildirim Madde 1 talebimin dogru sekilde uygulandigini gosterir.

Hedef kriterler (kaynak: `justin_gecmis_calisma.md`, Hipotez 1/2 ile AYNI proje/kasa):
HEDEF_PF=1,5 | HEDEF_WR=%60,0 (RR=1:1) | HEDEF_DD=%20 kumulatif | kasa=2.000 USD | islem-basi
risk=%1 ust sinir | lot=0,01 baslangic. Stratejist'in Hipotez 3 tanimi (`stratejici_raporu_
justin_gold_scalping_ml_v1_20260712.md`, Bolum "HIPOTEZ 3") bu hedeflerin Hipotez 1 ile AYNI
kaldigini (RR degismedigi icin) teyit ediyor.

Governance notu: Orkestrator'un gorev talimatindaki S3 aciklamasi (bu tur gunluk pipeline dongu
sayacini AYRICA artirmaz, ayni "tam tur"un 3. hipotez adimidir) Orkestrator'un yetki alanidir, bu
degerlendirmenin kararini etkilemez — kayit amacli burada da tekrarlanir.

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik : KIRMIZI** → Gorulmemis veri (TEST, tek-kez, n=15.237 ikili-
etiketli ornek) icinde tetiklenen islem sayisi = **0**, hem PRIMARY hem SUPPLEMENTARY
simulasyonda. Bu, "OOS islem sayisi < 15 ise sonuc anlamsiz" esiginin cok altinda — otomatik
anlamsiz/olculemez sonuc, Hipotez 1/2 ile AYNI. Bu turde esik-kalibrasyon kaynagi TEK bir kesit
(final_innerval_idx, n=12.219) oldugu icin Hipotez 1/2'deki "OOF-havuzunda X aday-islem var ama
final modelde yok" karsitligi burada YOK — kalibrasyon kaynaginin kendisi de UC adayin ucunde de
n=0 uretti (asagida Kontrol [7]). Ek olarak (model-tabanli ozel not, Hipotez 1/2 ile AYNI): tek
random_state (42) kullanildi, coklu-seed tekrarlama yapilmadi — sonuc zaten rassal-sinira bu
kadar yakinken tek-seed sonucuna guvenmek riskli olmaya devam ediyor.

**[2] Egitim/Gorulmemis Bozulma : KIRMIZI** → Klasik PF Bozulmasi/WR Farki hesaplanamiyor (her
iki tarafta da gercek PF/WR "tanimsiz", trade yok). AUC uzerinden bakildiginda: walk-forward ort.
AUC=0,5074 vs final model ic-validasyon AUC=0,5209 vs TEST AUC=0,5211 — uc deger de birbirine
yakin ve rassal-seviyeye (0,50) cok yakin, klasik "egitimde iyi/testte kotu" ezberleme
(overfitting) DESENI YOK; Muhendis'in "TUTARLI ZAYIFLIK" tanimlamasina katiliyorum. Ancak bu iyi
haber degil — model hicbir donemde (ne walk-forward'da ne ic-validasyonda ne TEST'te) anlamli bir
yon-tahmin sinyali tasimiyor demektir. Karar Cercevesi'ndeki en agir RED durumuna ("gorulmemis
veri PF hedefin cok altinda") burada da ulasiliyor — PF hedefin altinda degil, PF hic
OLCULEMIYOR. Feature-onem tablosu (JSON `feature_importance_gain_split`) Hipotez 1 ile BIREBIR
AYNI paterni tekrarliyor: `atr14_m15=0, m15_trend=0, confluence_flag=0, h1_trend_aligned=0` —
Stratejist'in "ZORUNLU" isaretledigi ana feature gruplari yine ~sifir agirlikli; en yuksek
degerler bu turde `atr14_h1_aligned=8` ve `macd_line=7` (Hipotez 1'de `atr14_h1_aligned=10` ve
`dow=6`) — sira kucuk farklarla degisti ama buyukluk mertebesi (tek haneli, 500 boosting-turu
icinde onemsiz) ayni kaldi. best_iteration=1 (Hipotez 1/2 ile AYNI) bunu dogruluyor: model
pratikte tek bir sig agac, anlamli hicbir iliski ogrenmemis.

**[3] Monte Carlo (%5 DD) : KIRMIZI** → Uygulanamadi (`islem_logu_PRIMARY_tam` ve
`islem_logu_SUPPLEMENTARY_tam` JSON'da ikisi de bos dizi `[]`, n=0). Monte Carlo'nun kendisi
degil, YAPILAMAMASININ NEDENI (hic islem yok) burada kirmizi bayrak — "olcum yoklugu", "dusuk
risk" ile karistirilmamali. Hipotez 1/2 ile AYNI durum.

**[4] Pes Pese Kayip : KIRMIZI** → Ayni nedenle hesaplanamadi (n=0 islem, ne gercek ne teorik
pes-pese kayip serisi kurulabilir). Kasa/risk parametreleri (2.000 USD, %1) bu asamada
uygulanamaz durumda.

**[5] Kar Konsantrasyonu : KIRMIZI** → Ayni nedenle hesaplanamadi (0 islem → "en iyi 3/10 islem"
tanimsiz). Not: bu, "dagilim saglikli" anlamina GELMEZ — olcumun kendisi yok.

**[6] Kirilim Analizi : N/A** → Rapor bu hipotez turu icin seans/gun/kosul bazli bir kirilim
tablosu icermiyor (0 islem oldugu icin zaten kirilim de anlamli olamazdi). Hipotez 1/2 ile AYNI
durum. N/A olarak isaretleniyor, atlanmiyor.

**[7] Parametre/Model Hassasiyeti : KIRMIZI** → Bu kontrol, gorev talimatinin ozel istegi geregi
esik-kalibrasyon DUZELTMESININ dogru uygulanip uygulanmadigini da kapsayacak sekilde genisletildi:

*(a) Duzeltmenin dogru uygulandigi teyidi:* JSON'daki `esik_kalibrasyonu_yontemi_duzeltmesi`
blogu ve `esik_kalibrasyonu.kalibrasyon_kaynagi_n=12219` alani, kalibrasyonun ARTIK SADECE
`final_innerval_idx` uzerinden yapildigini, 4-fold havuzlanmis OOF'un hicbir yerde
kullanilmadigini teyit ediyor — bu, Hipotez 1 raporumdaki Geri Bildirim Madde 1'in DOGRU
uygulanmasidir. Ayrica bu kaynagin final modelle iliskisi (sadece early-stopping eval_set,
gradyan guncellemesi yok) dogru sekilde tasarlanmis: fold'larin kendi val setleriyle iliskisiyle
AYNI karakterde, yani S2 protokolunun "final modelle ayni egitim-boyutu/karakterdeki tek bir
fold" sartini karsiliyor.

*(b) Yine de not edilmesi gereken ince bir nuans:* `final_innerval_idx`, final modelin
best_iteration'inin (=1) BELIRLENMESINDE (early-stopping karari) zaten kullanilmis bir kesittir —
simdi AYNI kesit esik-kalibrasyonu icin de kullaniliyor. Bu, gradyan-sizintisi degildir (S2
Madde3 feature-sizinti kontrolu bunu kapsamaz, ayri bir konu) ve fold-metodolojisiyle tutarlidir,
ancak "ayni veri iki farkli karar icin kullanildi" (model-karmasikligi secimi + esik secimi)
teknik olarak bagimsiz bir ikinci-katman risktir — pratikte SONUCU DEGISTIRMEDI (kaynak zaten
n=0 uretti, yani bu ikili-kullanimin esik SECIMINE hicbir yanlis-iyimser katkisi olmadi) ama
ilerideki bir turde (ornegin daha genis egitim n'i olan bir varyantta) bu ikili-kullanimin farkli
sonuclanabilecegi Stratejist'e not edilmelidir.

*(c) Esas hassasiyet bulgusu:* UC farkli esik adayinin (0,60/0,40 — en genis/en kolay gecilebilir
aday dahil) UCU DE sifir ornek uretti. Bu, sadece "kalibrasyon kaynagi kucuk" degil, modelin
TEST'teki olasilik dagiliminin (p_test max=0,5280, std=0,0067) o kadar dar oldugunu gosteriyor ki
esik ne kadar genisletilirse genisletilsin (0,55'ten 0,60'a) model hicbir zaman bu bandin disina
cikamiyor — bu, MIN_SAMPLE parametresinin degil, modelin kendi ayirt-edicilik gucunun
(best_iteration=1, AUC~0,50-0,52) kokten yetersiz oldugunun bir baska kanitidir. Ayrica S2
protokolu geregi hiperparametre grid-search bilincli yapilmadi (dar/sabit aralik) — bu dogru bir
tercih ama `best_iteration=1` (pratikte tek agac) hala test edilmemis bir kirilganlik: farkli
learning_rate/early_stopping ayari sonucu degistirebilirdi mi, bilinmiyor.

**[8] Gercek Hayat Duzeltmesi : KIRMIZI** → 0 islem uzerinden slipaj/psikoloji duzeltmesi
uygulanacak bir Net Kar/PF yok (Duzeltilmis Net Kar = 0 - 0 - 0 = 0, anlamli bir duzeltme degil).
Gercek hesapta bu hipotezin MEVCUT esik/model haliyle hicbir islem uretmeyecegi, dolayisiyla ne
kar ne zarar getirmeyecegi (firsat maliyeti haric) anlamina gelir. Hipotez 1/2 ile AYNI.

---

## --- OZET ---

**Guclu Yanlar:**
- Esik-kalibrasyon yontemi DUZELTMESI dogru uygulandi ve bagimsiz olarak dogrulandi (Kontrol [7]a)
  — Hipotez 1'deki OOF-havuz/final-model tutarsizligi bu turde YOK, sonuc artik metodolojik
  olarak temiz (kalibrasyon kaynagi ile TEST tutarli sekilde ayni sinyal-yoklugunu gosteriyor).
- S1 maliyet-orani P90-stres testi bu k'da (2,0) GECILDI (15,88x >= 15,0x) — Hipotez 1'in
  kaybettigi yerde (11,91x). Guvenlik-marji tasarim amaci ampirik olarak dogrulandi.
- Metodoloji saglam: purged/embargolu walk-forward (4 fold, artik sadece diagnostik amacli
  dogru sekilde ayristirilmis), test-seti tek-kullanim kurali, feature-sizinti kontrol listesi
  tam teyit edilmis, DST/saat-eslesme bagimsiz yeniden dogrulanmis.
- Egitim(walk-forward), ic-validasyon ve TEST AUC'leri birbirine yakin — klasik "egitimde
  ezberleme" (overfitting) DESENI yok; asagidaki zayiflik "sahte basari" degil durust/tutarli bir
  basarisizlik olarak raporlanmis.
- Uc BAGIMSIZ ML hipotezinin (LightGBM k=1,5, XGBoost k=1,5, LightGBM k=2,0) UCU DE ayni
  sinyal-yoklugu sonucuna ulasmasi, sorunun model-secimi veya barrier-genisligi degil feature-
  seti/etiket tasarimi oldugu yonundeki bulguyu guclendiriyor.

**Zayif Yanlar / Riskler:**
- Modelin ayirt edici gucu (AUC~0,50-0,52) neredeyse tam rassal — hem walk-forward'da hem
  ic-validasyonda hem TEST'te.
- Final model pratik olarak tek agac (best_iteration=1), feature-onem tablosunda ana feature
  gruplari (ATR/trend/confluence) Hipotez 1 ile BIREBIR AYNI sekilde sifira yakin agirlikta.
- UC esik adayinin da (en genisi dahil) sifir ornek uretmesi — modelin olasilik dagilimi o kadar
  dar ki esigi genisletmek bile sonucu degistirmiyor (Kontrol [7]c).
- Kalibrasyon kaynaginin (final_innerval_idx) ayni zamanda early-stopping karari icin de
  kullanilmis olmasi, sonucu degistirmese de teknik olarak ikinci bir kullanim katmanidir —
  ilerideki turlerde izlenmeli (Kontrol [7]b).
- Sonuc olarak 0 islem: PF/WR/DD olculemedi, hedef karsilandi/karsilanmadi denemez.
- Hicbir Monte Carlo/pes-pese-kayip/kar-konsantrasyonu olcumu YAPILAMADI — bu kontrollerin
  "GECTI" cikmasi degil, hic yapilamamis olmasi ayri bir risk katmanidir.
- Daha genis barrier (k=2,0) daha az efektif islem frekansi anlamina gelir (hicbiri orani
  %13,07→%24,92) — Stratejist'in kendi raporunda isaretledigi risk (T=500 varsayimina ulasma
  suresinin uzamasi), model calissaydi bile gecerli kalirdi.

---

## --- KARAR GEREKCE ---

Bu hipotez de (Hipotez 1/2 gibi) HEDEF_PF/HEDEF_WR/HEDEF_DD kriterlerinin hicbirine gore
"karsiladi/karsilamadi" diye degerlendirilemez — TEST setinde tek bir islem bile tetiklenmemistir
(n=0), ve bu bir kod/veri hatasi degil, esik-kalibrasyon yontemi DUZELTILDIKTEN SONRA da ayni
sekilde gozlemlenen, modelin dogrulanmis/tutarli davranisidir (raw JSON capraz kontrolu dahil
teyit edildi). Bagimsiz kontrol listemin 8 maddesinden 7'si (1,2,3,4,5,7,8) dogrudan olcum-
yoklugu veya modelin kendi olcum yetersizligi nedeniyle KIRMIZI, 6. madde N/A'dir. Karar
Cercevesi'ndeki RED kriterlerinden en az ikisi acikca saglaniyor: "gorulmemis veri PF/WR/DD,
hedefin cok altinda/olculemez" ve "modelin AUC'u rassal-seviye, feature-onem tablosu anlamli
sinyal gostermiyor". Esik-kalibrasyon duzeltmesinin BASARIYLA uygulanmis olmasi (Hipotez 1'deki
yontemsel soru isaretini ortadan kaldirmasi) bu RED kararini DAHA GUVENILIR kiliyor — artik
0-islem sonucunun "duzeltilseydi belki islem cikardi" gibi bir belirsizligi yok, sonuc net bir
sinyal-yoklugudur.

---

## --- HIPOTEZ 1/2 vs HIPOTEZ 3 — RISK ANALISTI SEVIYESI TUTARLILIK DEGERLENDIRMESI ---

- **Karar:** Ucu de RED — BAGIMSIZ ulasilan AYNI sonuc (bu degerlendirme, Hipotez 1/2'nin RED
  kararindan etkilenmeden, kendi ham JSON'u uzerinden yapildi).
- **Kontrol bazinda tutarlilik:** 8 kontrolun 7'si (1,2,3,4,5,7,8) her uc hipotezde de AYNI yonde
  (KIRMIZI) sonuclandi, 6. kontrol ucunde de N/A. Hicbir kontrolde Hipotez 3 ile Hipotez 1/2
  arasinda YON farkliligi yoktur.
- **Esik-kalibrasyon duzeltmesinin etkisi (bu turun asil metodolojik farki):** Hipotez 1/2'de
  esik-kalibrasyonu 4-fold havuzlanmis OOF'tan yapilmisti ve bu havuzda onemli sayida aday-islem
  (H1: 210, H2: 622) goruluyordu — ama bu, final modelin GERCEKTE hicbir zaman ulasamayacagi bir
  esik uretiyordu (yontemsel bir CELISKI, Kontrol [7]'de KIRMIZI gerekcesiydi). Hipotez 3'te bu
  duzeltildi: kalibrasyon kaynagi SADECE final modelin kendi ic-validasyonu, ve bu kaynak da
  UCUNDE de n=0 uretti — yani artik OOF-havuzu ile final-model arasinda bir CELISKI YOK, ikisi de
  (kalibrasyon kaynagi + TEST) TUTARLI sekilde sinyal-yoklugu gosteriyor. Sonuc: 0-islem cikisi
  artik bir "yontem artefakti olabilir mi" sorusu tasimiyor, dogrudan modelin gercek davranisidir.
  Bu, karari DEGISTIRMEDI (RED zaten Hipotez 1/2'de de dogruydu) ama kararin GUVENILIRLIGINI
  artirdi.
- **S1 P90-stres testindeki fark:** Hipotez 1/2'de (k=1,5) P90-stres testi KAYBEDILMISTI (11,91x
  < 15,0x); Hipotez 3'te (k=2,0) bu test GECILDI (15,88x >= 15,0x). Bu, Hipotez 3'un tasarim
  amacini (guvenlik-marji genisletme) basariyla dogruluyor, ANCAK 8-kontrol cercevesinde bu
  dogrudan bir madde degil (S1, Muhendis'in on-kontrolu, Risk Analisti'nin 8 kontrolune Kontrol
  [8] "Gercek Hayat Duzeltmesi" baglaminda dolayli girer) — ve zaten 0 islem oldugu icin
  maliyet-orani marjinin genisligi PRATIKTE hicbir sonuca donusmuyor. Bu yuzden bu fark, RED
  kararini DEGISTIRMEZ.
- **Feature-onem paterni:** Hipotez 3'te (k=2,0), ana feature gruplarinin (ATR/trend/confluence)
  ~sifir agirlik alma paterni Hipotez 1 ile BIREBIR AYNI kaldi — barrier genisliginin
  degistirilmesi modelin ogrenme kapasitesini/feature-kullanim paternini ANLAMLI OLCUDE
  DEGISTIRMEDI. Bu, sorunun barrier genisligi/k-parametresi degil, feature setinin (mevcut
  haliyle) fiyat yonunu tahmin etmeye YETERSIZ olmasindan kaynaklandigi bulgusunu (Hipotez 1/2
  raporlarimda da belirtilen) bu ucuncu, BAGIMSIZ varyantla bir kez daha PEKISTIRIYOR.
- **Sonuc:** Uc-yonlu capraz-kontrol tasariminin (LightGBM k=1,5, XGBoost k=1,5, LightGBM k=2,0)
  amaci basariyla gerceklesti — sorunun model-secimine (LightGBM vs XGBoost) veya barrier-
  genisligine (k=1,5 vs k=2,0) degil, mevcut 23-feature setinin/etiket tasariminin kendisine
  bagli oldugu artik UC BAGIMSIZ kanitla desteklenmis durumdadir.

---

## --- STRATEJISTE GERI BILDIRIM ---

1. **ML/v1 hattinin bu tasarimla devam ettirilmesi onerilmiyor:** Uc BAGIMSIZ hipotez (2 model
   ailesi x 2 barrier-genisligi kombinasyonu) ayni feature seti/etiket tasarimiyla ayni sinyal-
   yoklugu sonucuna ulasti. Barrier genisligini (k) veya model ailesini degistirmeye devam etmek
   (dorduncu bir k veya ucuncu bir model ailesi denemek) dusuk getiri beklentili bir sonraki
   adimdir — bu, gorev kapsaminda degil ama kayit icin belirtilir: bir sonraki tur once
   Arastirmaci'dan farkli/ek feature aileleri (mikro-yapi, farkli zaman pencereleri, farkli
   etiket tanimlari) istemeyi onceliklendirmeli.
2. **Esik-kalibrasyon duzeltmesi basariyla dogrulandi, ancak ince bir ikinci-katman risk not
   edildi:** `final_innerval_idx`'in hem early-stopping karari HEM DE esik-kalibrasyonu icin
   kullanilmasi bu turde sonucu degistirmedi (kaynak zaten n=0 uretti) ama daha genis bir egitim
   n'i olan gelecekteki bir varyantta bu ikili-kullanimin farkli sonuclanip sonuclanmayacagi
   izlenmelidir — ideal olarak final_train_idx icinde ayrica bir ucuncu kesit (early-stopping
   icin) ile kalibrasyon kesiti birbirinden ayrilabilir, ama bu S2 protokolunun mevcut orneklem
   kisitlarinda kucuk bir iyilestirme olur, zorunlu degil.
3. **Opsiyonel 3-sinifli alt-varyant (Stratejist raporunda takdire birakilmisti) simdi daha
   anlamli hale geldi:** k=2,0'da "hicbiri" orani %24,92'ye cikti; bu, ikili semanin "hicbiri az"
   varsayimindan uzaklasiyor. Eger ML/v1 hatti farkli bir feature setiyle tekrar denenirse, bu
   3-sinifli alt-varyant o zaman ayrica calistirilabilir — ama mevcut feature seti zaten sinyal
   tasimadigi icin, bu varyanti SU AN calistirmak (Muhendis'in dogru tespit ettigi gibi) oncelikli
   degildir.
4. **Arastirmaci'ya geri-bildirim onerisi (Hipotez 1/2'de de tekrarlanan, simdi UC kanitla
   guclenen bir oneri):** AUC'nin (~0,50-0,52) ve feature-onem tablosunun (ana gruplar sifira
   yakin, UC hipotezde de BIREBIR AYNI) birlikte gosterdigi tablo, mevcut feature setinin
   (BULGU 1-9) yeterli sinyal tasimadigi izlenimini guclu sekilde destekliyor. Bir sonraki
   arastirma turunde farkli/ek feature aileleri dusunulmesi tavsiye edilir.

---

## --- KULLANICIYA ---

Justin projesinin ucuncu yapay-zeka denemesi (ayni yontem, LightGBM, ama bu kez fiyat hedefi/
zarar-durdur mesafesi daha genis tutularak — modelin daha az ama daha "guvenli" sinyal uretmesi
umuduyla) incelendi ve onaylanamadi (KARAR: RED) — tipki ilk iki denemedeki gibi. Bu turde ayrica
onceki denememde tespit ettigim bir teknik eksikligin (esik belirleme yonteminin, gercekte
kullanilacak modelden farkli bir kaynaktan yapilmasi) duzeltilip duzeltilmedigini de kontrol
ettim — DUZELTILDIGINI dogruladim, bu iyi bir adim. Ancak duzeltme yapildiktan sonra bile sonuc
degismedi: model, hic gormedigi (gelecege benzer) veri uzerinde yine yazi-tura atmakla ayni
seviyede kaldi ve test doneminde hicbir zaman islem acacak kadar "kendinden emin" olmadi
(0 islem) — bu sefer bu sonucun bir teknik hata olmadigindan da eminim. Artik uc farkli deneme
(iki farkli yapay-zeka kutuphanesi, iki farkli risk-mesafesi ayari) ayni sonuca ulasti: sorun
kullanilan araclarda veya ayarlarda degil, modele verilen "ipuclarinin" (fiyat verisinden turetilen
ozellikler) kendisinde. Ozetle: bu ucuncu deneme de mevcut haliyle canliya/ilerki asamaya gecmeye
hazir degil; bir sonraki adimin ayni yontemi baska bir ayarla tekrar denemek yerine, modele
verilen ipuclarinin kokten degistirilmesi (Arastirmaci'nin yeni bir arastirma turu yapmasi)
olmasi gerektigi yonunde net bir sinyal var.
