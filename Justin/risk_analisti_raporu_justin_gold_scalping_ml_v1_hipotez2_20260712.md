=== RiSK ANALiZi RAPORU ===
Hipotez        : XGBoost Kiyaslama (Ayni Tasarim, Ayni Feature/Label/N/k=1,5xATR14-M15) — HIPOTEZ 2
Yaklasim Turu  : Makine Ogrenmesi — Gradient Boosting (XGBoost, binary:logistic classifier) —
                 Justin/ML ailesinin Risk Analisti tarafindan degerlendirilen 2. hipotezi
Tarih          : 2026-07-12
KARAR          : RED

---

## ON-NOT — BAGIMSIZ DOGRULAMA

Bu degerlendirme oncesinde Backtest Muhendisi'nin raporu (`backtest_muhendisi_raporu_
justin_gold_scalping_ml_v1_hipotez2_20260712.md`) ile ham cikti dosyasi (`backtest_ml_v1_
hipotez2_output.json`) satir satir karsilastirildi: walk-forward AUC degerleri (fold 1-4:
0,5074/0,5190/0,5066/0,5174, ortalama=0,5126/std=0,0056), esik-kalibrasyonu aday tablosu
(0,575/0,425 icin LONG n=590/WR-proxy=0,5458, SHORT n=32/WR-proxy=0,6250), final model
ic-validasyon AUC'u (0,5174, best_iteration=0 → 1 agac), TEST AUC'u (0,5228), p_test dagilimi
(min=0,5053/max=0,5241/ort=0,5085), S1 oranlari (medyan 15,97x / P90 11,91x — Hipotez 1 ile
BIREBIR AYNI, beklenen) ve PRIMARY/SUPPLEMENTARY islem sayilari (ikisi de 0) — HAM JSON ile
RAPOR arasinda hicbir sayisal tutarsizlik bulunamadi. Rapor guvenilir kaynak olarak kabul
edildi; asagidaki 8 kontrol kendi bagimsiz yorumumla, Hipotez 1 degerlendirmemden BAGIMSIZ
olarak uygulanmistir (on-gozlemin sundugu sentez oldugu gibi kabul edilmemistir).

Hedef kriterler (kaynak: `justin_gecmis_calisma.md`, Hipotez 1 ile AYNI proje/kasa): HEDEF_PF=1,5
| HEDEF_WR=%60,0 (RR=1:1) | HEDEF_DD=%20 kumulatif | kasa=2.000 USD | islem-basi risk=%1 ust
sinir | lot=0,01 baslangic.

Governance notu: Orkestrator'un gorev talimatindaki S3 aciklamasi (Hipotez 2, Hipotez 1 ile AYNI
"tam tur" sayilir, gunluk pipeline dongu sayacini AYRICA artirmaz) dogrudan Orkestrator'un yetki
alanidir, bu degerlendirmenin kararini etkilemez — sadece kayit amacli burada da tekrarlanir.

---

## --- KONTROLLER ---

**[1] Istatistiksel Anlamlilik : KIRMIZI** → Gorulmemis veri (TEST, tek-kez, n=17.833
siniflandirma ornegi) icinde tetiklenen islem sayisi = **0**, PRIMARY ve SUPPLEMENTARY
simulasyonlarinin ikisinde de. Bu, "OOS islem sayisi < 15 ise sonuc anlamsiz" esiginin cok
altinda — otomatik anlamsiz/olculemez sonuc, Hipotez 1 ile AYNI. Esik-kalibrasyonu OOF-havuzunda
n=622 aday-islem (590 long + 32 short) var, ama bu da Hipotez 1'deki gibi TEK bir modelin degil
4 FARKLI modelin (bu turde best_iteration 3/6/22/0, agac-sayisi 4/7/23/1 — Hipotez 1'in 1/6/4/1
agac-sayisindan bile daha genis bir yayilim) havuzlanmis tahminlerini temsil ediyor; klasik
"egitim islem sayisi" tablosuna dogrudan uygulanamaz. Tek random_state (42) kullanildi, coklu-seed
tekrari yok — sonuc zaten rassal-sinira yakinken bu ek bir guven-zayifligidir.

**[2] Egitim/Gorulmemis Bozulma : KIRMIZI** → Klasik PF Bozulmasi/WR Farki hesaplanamiyor (n=0
trade, PF/WR tanimsiz). AUC uzerinden bakildiginda: walk-forward ort. AUC=0,5126 vs final model
ic-validasyon AUC=0,5174 vs TEST AUC=0,5228 — uc deger de birbirine yakin, klasik "egitimde
iyi/testte kotu" ezberleme (overfitting) DESENI YOK; Muhendis'in "TUTARLI ZAYIFLIK" tanimina
katiliyorum. Ancak bu iyi haber degildir: her uc olcum de 0,50 rassal-cizgisine bu kadar
yakinken, model hicbir donemde anlamli bir yon-sinyali tasimiyor demektir. Feature-onem tablosu
bu turde (normalize-gain metriginde) daha "dengeli" gorunuyor (en dusuk sifir-olmayan
`directional_streak`=0,023, en yuksek `dow`=0,0715 — yaklasik 3 kat fark), Hipotez 1'deki
neredeyse-sifir agirlikli ana feature gruplarindan (atr14_m15=0, m15_trend=0, confluence_flag=0)
FARKLI bir goruntu veriyor — ama Muhendis'in de dogru vurguladigi gibi bu dogrudan "XGBoost daha
iyi/daha fazla ogreniyor" seklinde YORUMLANAMAZ: TEST AUC'u (0,5228) zaten rassal-seviyede oldugu
icin, hangi metrikle olculurse olculsun HICBIR feature-onem dagilimi anlamli/genellenebilir bir
sinyalin KANITI olamaz — bir "dengesiz" model kadar bir "dengeli-gorunumlu ama rassal" model de
gucsuzdur, aradaki fark istatistiksel gurultu olabilir (tek-seed, dar hiperparametre araligi).
Karar Cercevesi'ndeki en agir RED durumuna (PF olculemiyor) burada da ulasiliyor — otomatik
KIRMIZI.

**[3] Monte Carlo (%5 DD) : KIRMIZI** → Uygulanamadi (islem_logu_PRIMARY_tam ve
islem_logu_SUPPLEMENTARY_tam ikisi de bos dizi, n=0). Ayni Hipotez 1'deki gibi: bu "dusuk risk"
degil "olcum yoklugu" anlamina gelen bir kirmizi bayraktir.

**[4] Pes Pese Kayip : KIRMIZI** → Ayni nedenle hesaplanamadi (n=0 islem). Kasa/risk
parametreleri (2.000 USD, %1) bu asamada uygulanamaz durumda.

**[5] Kar Konsantrasyonu : KIRMIZI** → Ayni nedenle hesaplanamadi (0 islem → "en iyi 3/10
islem" tanimsiz). Dagilimin saglikli oldugu anlamina GELMEZ, olcumun kendisi yok.

**[6] Kirilim Analizi : N/A** → Rapor bu hipotez turu icin seans/gun/kosul bazli bir kirilim
tablosu icermiyor (0 islem oldugu icin zaten kirilim de anlamsiz olurdu). Hipotez 1 ile AYNI
durum.

**[7] Parametre/Model Hassasiyeti : KIRMIZI** → S2 protokolu geregi hiperparametre grid-search
BILINCLI yapilmadi (dar/sabit aralik) — bu tercih dogru, ama iki somut, dogrulanmis risk
birakiyor: (a) `best_iteration=0` (0-indeksli) → final model pratikte **TEK bir agac** — Hipotez
1'deki `best_iteration=1` (1 boosting turu) ile AYNI kirilgan karakter, erken durma bu turde de
neredeyse ANINDA devreye girmis. (b) Esik-kalibrasyonu OOF-havuz/final-model dagilim uyusmazligi
bu turde de AYNEN gozlemleniyor, hatta fold-arasi agac-sayisi yayilimi (4/7/23/1) Hipotez 1'den
(2/7/5/2 — best_iteration 1/6/4/1 karsiligi) DAHA GENIS: esik, en karmasik fold modelinin (fold
3, 23 agac) katkida bulundugu bir OOF havuzundan secilirken, final model (1 agac) bu fold'lardan
en basitiyle (fold 4, 1 agac) ayni karakterde — final modelin TEST'te p_test max=0,5241 ile
kalibre esigin (0,575) HICBIR ZAMAN altina bile yaklasamamasi bu yapisal uyumsuzlugun dogrudan
sonucudur. Bu bir "hipotetik hassasiyet sorusu" degil, HAM JSON'DA DOGRUDAN GOZLEMLENEN bir
tasarim kusurudur (fold agac-sayilari 4/7/23/1 vs final agac-sayisi 1) — bu yuzden "TEST YOK"
degil KIRMIZI olarak isaretliyorum, Hipotez 1'deki degerlendirmemle tutarli.

**[8] Gercek Hayat Duzeltmesi : KIRMIZI** → 0 islem uzerinden slipaj/psikoloji duzeltmesi
uygulanacak bir Net Kar/PF yok (Duzeltilmis Net Kar = 0 - 0 - 0 = 0). Gercek hesapta bu hipotezin
MEVCUT esik/model haliyle hicbir islem uretmeyecegi, dolayisiyla ne kar ne zarar getirmeyecegi
(firsat maliyeti haric) anlamina gelir — Hipotez 1 ile AYNI sonuc.

---

## --- OZET ---

**Guclu Yanlar:**
- Metodoloji Hipotez 1 ile AYNI saglamlikta: purged/embargolu walk-forward (4 fold), test-seti
  tek-kullanim kurali, feature-sizinti kontrol listesi tam teyit edilmis (DST dogrulamasi Hipotez
  1'den dogru gerekceyle devralinmis — AYNI feature-uretim kodu, ayri bir ML/kural-tabanli aile
  gecisi degil).
- Cift-model capraz-kontrol tasarimi (LightGBM vs XGBoost) metodolojik olarak DEGERLI: iki
  BAGIMSIZ gradient-boosting mimarisi, ayni feature/etiket/barrier uzerinde ayri ayri egitilmis
  ve BAGIMSIZ olarak ayni (zayif) sonuca ulasmis — bu, sonucun "LightGBM'in idiosinkrazisi"
  olmadigini gosterme cabasi olarak dogru bir adimdir.
- Egitim(walk-forward) ve TEST AUC'leri birbirine yakin (0,5126 vs 0,5228) — "sahte basari"
  (egitimde ezberleyip testte cokme) deseni yok, durust bir basarisizlik.

**Zayif Yanlar / Riskler:**
- Modelin ayirt edici gucu (AUC~0,51-0,52) neredeyse tam rassal — Hipotez 1 ile ayni kategoride.
- Final model pratikte tek agac (best_iteration=0/0-indeksli) — Hipotez 1'deki tek-agac
  kirilganligiyla AYNI.
- Esik-kalibrasyonu (OOF-havuz, 4 farkli-karmasiklikta modelin karisimi) ile final model (1 agac)
  arasindaki dagilim uyusmazligi bu turde de gozlemlendi — final model TEST'te kalibre esige
  (0,575/0,425) HICBIR ZAMAN ulasamiyor (p_test max=0,5241).
- Sonuc olarak 0 islem (hem PRIMARY hem SUPPLEMENTARY): PF/WR/DD olculemedi, hedef
  karsilandi/karsilanmadi denemez.
- S1 maliyet-orani P90-stres testinde esik kaybediliyor (11,91x < 15,0x) — Hipotez 1 ile AYNI,
  barrier tasarimindan kaynaklanir, model calissaydi bile yuksek-spread anlarinda marj dar.
- Hicbir Monte Carlo/pes-pese-kayip/kar-konsantrasyonu olcumu YAPILAMADI — ayri bir risk
  katmanidir, "GECTI" anlamina gelmez.
- Feature-onem tablosunun "daha dengeli" gorunmesi (Hipotez 1'e kiyasla) yaniltici bir guven
  kaynagi olmamali — TEST AUC'u rassal-seviyede oldugu surece bu gozlem karari degistirmez.

---

## --- KARAR GEREKCE ---

Bu hipotez de (Hipotez 1 gibi) HEDEF_PF/HEDEF_WR/HEDEF_DD kriterlerinin hicbirine gore
"karsiladi/karsilamadi" diye degerlendirilemez — TEST setinde tek bir islem bile tetiklenmemistir
(n=0), ve bu bir kod/veri hatasi degil, modelin (rassal-seviye AUC + kalibre esige hicbir zaman
ulasmayan bir olasilik dagilimi) dogrulanmis/deterministik davranisidir (raw JSON capraz kontrolu
dahil teyit edildi). Bagimsiz kontrol listemin 8 maddesinden 7'si (1,2,3,4,5,7,8) dogrudan
olcum-yoklugu veya HAM JSON'da gozlemlenen bir yapisal tutarsizlik (esik-kalibrasyonu OOF-havuz
vs final-model uyumsuzlugu) nedeniyle KIRMIZI, 6. madde N/A'dir. Karar Cercevesi'ndeki RED
kriterlerinden en az ikisi acikca saglaniyor: "gorulmemis veri PF/WR/DD, hedefin cok
altinda/olculemez" ve "modelin AUC'u rassal-seviye". Bu, Backtest Muhendisi'nin RED kararini
bagimsiz olarak DOGRULAR.

---

## --- HIPOTEZ 1 vs HIPOTEZ 2 — RISK ANALISTI SEVIYESI TUTARLILIK DEGERLENDIRMESI ---

- **Karar:** Ikisi de RED — BAGIMSIZ ulasilan AYNI sonuc (Hipotez 2 degerlendirmesi Hipotez 1'in
  kararindan etkilenmeden, kendi ham JSON'u uzerinden yapildi).
- **Kontrol bazinda tutarlilik:** 8 kontrolun 7'si (1,2,3,4,5,7,8) HER IKI hipotezde de AYNI
  yonde (KIRMIZI) sonuclandi, 6. kontrol her ikisinde de N/A. Hicbir kontrolde Hipotez 1 ile
  Hipotez 2 arasinda YON farkliligi (biri KIRMIZI/digeri GECTI gibi) yoktur.
- **Farklilik gozlemlenen noktalar (yon degil, DETAY):**
  - AUC degerleri kucuk farklarla farklidir (walk-forward ort. 0,5075→0,5126, TEST AUC
    0,5170→0,5228) ama HER IKISI DE ayni kategoride (rassal-seviyeye yakin) kalmistir.
  - Esik-kalibrasyonu FARKLI degerler secmistir (0,55/0,45 → 0,575/0,425) — bu, iki modelin
    farkli OOF olasilik-dagilimlarindan kaynaklanan BEKLENEN bir fark, degerlendirmeyi
    etkilemez.
  - Feature-onem tablosu FARKLI metrik/goruntu sunar (LightGBM'de ana feature gruplari
    ~sifir agirlikli; XGBoost'ta goreli daha dengeli) — ancak [2] nolu kontrolde acikladigim
    gibi, TEST AUC'u rassal-seviyede oldugu surece bu farklilik BASKA BIR SONUCA ISARET ETMEZ,
    salt gozlemsel bir nottur.
  - Hipotez 2'de fold-arasi agac-sayisi yayilimi (4/7/23/1) Hipotez 1'e (2/7/5/2) gore biraz
    daha genis — [7] nolu kontroldeki OOF-havuz/final-model uyumsuzlugu riskini HAFIFCE daha
    belirgin kilar, ama karari degistirmez (zaten Hipotez 1'de de KIRMIZI idi).
- **Sonuc:** Capraz-kontrol tasariminin amaci (sinyal zayifliginin model-secimine mi yoksa
  veri/etikete mi bagli oldugunu ayirt etmek) basariyla gerceklesmistir — Risk Analisti
  seviyesinde de iki BAGIMSIZ degerlendirme AYNI karara ve neredeyse AYNI kontrol profiline
  ulasarak, sorunun XGBoost/LightGBM secimiyle degil feature-seti/etiket (N=16/k=1,5) tasarimiyla
  ilgili oldugu yonundeki Muhendis sentezini DOGRULAR.

---

## --- STRATEJISTE GERI BILDIRIM ---

1. **Esik-kalibrasyon yontemi HER IKI model icin de duzeltilmeli:** Kalibrasyon SADECE final
   modelin kendi OOF tahminlerinden (ya da final modelle AYNI egitim-boyutu/karakterdeki bir
   fold'dan) yapilmali — 4 FARKLI karmasiklikta modelin (bu turde agac-sayisi 4/7/23/1) havuzlanmis
   tahminleri uzerinden esik secmek, final modelin (1 agac) gercekte hicbir zaman ulasamayacagi
   bir esik uretebiliyor; bu, iki hipotezde de (LightGBM ve XGBoost) BAGIMSIZ olarak
   gozlemlenmistir — govde/yontemsel bir sorun, model-secimine ozgu degil.
2. **Capraz-dogrulanmis bulgu kabul edilmeli:** Iki bagimsiz gradient-boosting mimarisi, ayni
   feature/etiket/barrier tasariminda, ikisi de rassal-seviyede AUC uretti (Hipotez 1: ~0,51,
   Hipotez 2: ~0,51-0,52) ve ikisi de TEST'te 0 islem uretti. Bu, mevcut N=16/k=1,5xATR14-M15
   etiket tasariminin ve/veya 23-sutunluk feature setinin (Karar 3) bu iki model ailesi icin
   ayirt edici bir sinyal TASIMADIGINA isaret eder — bir sonraki tur, model mimarisini
   degistirmek yerine (ucuncu bir model ailesi denemek) feature-seti/etiket tanimini sorgulamaya
   ONCELIK vermelidir.
3. **Hipotez 3 (k=2,0) ve/veya yeni feature aileleri degerlendirilmeli:** Stratejist'in kendi
   raporunda onerdigi Hipotez 3 (k=2,0, cost-ratio 21,29x, daha genis maliyet marji) veya
   Arastirmaci'ya farkli/ek feature aileleri (mikro-yapi, farkli zaman pencereleri) icin geri
   bildirim onerisi bir sonraki tur icin oncelikli degerlendirilmelidir — mevcut ikili
   cross-check (Hipotez 1/2) bu yonde bir ihtiyaci GUCLENDIRMISTIR.
4. **S1 P90-stres testi hatirlatmasi (her iki hipotezde AYNI):** k=1,5 medyan-spread'de esigi
   zar-zor geciyor (15,97x) ama P90-stres testinde kaybediyor (11,91x<15,0x) — bir sonraki
   varyantta bu marj genisletilmelidir.

---

## --- KULLANICIYA ---

Justin projesinin ikinci yapay-zeka denemesi (farkli bir makine ogrenmesi kutuphanesi, XGBoost,
birinci denemeyle -LightGBM- ayni tasarimda calistirilan bir kiyaslama) incelendi ve
onaylanamadi (KARAR: RED) — tipki birincisi gibi. Bu iki modeli birbirinden bagimsiz test etmenin
amaci sunu anlamakti: "sorun belirli bir yapay-zeka kutuphanesinden mi kaynaklaniyor, yoksa
kullanilan veri/sinyal tanimindan mi?" Sonuc net: iki farkli model de, hic gormedigi (gelecege
benzer) veri uzerinde neredeyse yazi-tura atmakla ayni seviyede kaldi ve ikisi de test
doneminde hicbir zaman islem acacak kadar "kendinden emin" olmadi (0 islem). Bu, sorunun
kullanilan yapay-zeka aracinda degil, verinin/sinyal tanimin kendisinde oldugunu gosteren
guclu bir isarettir — yani bir sonraki denemede farkli bir yapay-zeka kutuphanesi denemek yerine,
kullanilan veri ozelliklerinin (feature'lar) veya "basarili islem" tanimin degistirilmesi
gerekiyor. Ozetle: bu ikinci deneme de mevcut haliyle canliya/ilerki asamaya gecmeye hazir degil,
ama iki bagimsiz test birbirini dogruladigi icin artik neyin duzeltilmesi gerektigi konusunda
daha net bir yon var. Stratejist'e somut oneriler iletildi (esik-kalibrasyon yonteminin
duzeltilmesi, farkli parametre varyanti veya yeni veri ozellikleri denenmesi).
