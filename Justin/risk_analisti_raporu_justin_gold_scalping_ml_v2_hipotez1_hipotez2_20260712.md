# RiSK ANALiZi RAPORU — Justin / Gold Scalping, ML/Feature-Tabanli Aile v2 (ML Tam Tur 2)
## HIPOTEZ 1 (Ikili/Barrier-Touch, Grup B eklenmis) + HIPOTEZ 2 (3-Sinifli/Deadzone, Grup B eklenmis) — BiRLiKTE, TEK DEGERLENDIRME TURU

Hipotez         : HIPOTEZ 1 — LightGBM Ikili + Grup B (Pivot/S-R) | HIPOTEZ 2 — LightGBM 3-Sinifli (Deadzone) + Grup B
Yaklasim Turu   : Makine Ogrenmesi — Gradient Boosting (LightGBM), sirasiyla binary / multiclass
Tarih           : 2026-07-12
KARAR HIPOTEZ 1 : **RED**
KARAR HIPOTEZ 2 : **RED**
TAM TUR 2 GENEL SONUC (S3): **RED / Tur 1 ile AYNI patern — S3 sayaci 2/2'ye ulasti (Orkestrator bilgisine)**

Girdi dosyalari:
- `backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez1_20260712.md` + `backtest_ml_v2_hipotez1_output.json`
- `backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez2_20260712.md` + `backtest_ml_v2_hipotez2_output.json` (islem_logu_tam uzerinde bagimsiz Monte Carlo/kar-konsantrasyonu/risk-yuzdesi yeniden hesaplandi — asagida)
- `stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md`
- `justin_gecmis_calisma.md` (HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 kumulatif / kasa=2.000 USD / risk-basi %1 UST SINIR)
- `justin_ml_anti_overfitting_protokolu.md` (S2), `justin_backtest_onkontrol_standardi.md` (S1+DST)

---

# BOLUM A — HIPOTEZ 1 (Ikili/Barrier-Touch, Feature-Izole)

## KARAR: RED

### KONTROLLER

**[1] Istatistiksel Anlamlilik — KIRMIZI**
Egitim tarafinda klasik "IS islem sayisi" kavramı yok (bu bir siniflandirma modeli, trade-simulasyonu SADECE test setinde calistirildi) — bu basli basina bir metodolojik bosluk: Muhendis IS/trainval uzerinde gercek P&L trade-simulasyonu calistirmadi, sadece OOF esik-kalibrasyon proxy'si (LONG n=209, WR-proxy=%59,8; SHORT hicbir eskikte MIN_SAMPLE(30)'u GECEMEDI: n=0,0,5) uretti. Asil olcum olan **gorulmemis veri (TEST) islem sayisi = 0** — kendi esigimin (<15 → anlamsiz) cok altinda, fiilen "olcum yok" durumu. 17.833 barlik bir test doneminde (~1 yila yakin) TEK BIR sinyal bile tetiklenmedi (kapsama %0,0). Ayrica model tek bir random_state (42) ile egitildi — model-tabanli yontemler icin istenen coklu-seed testi YAPILMADI (LightGBM deterministik oldugu icin tek-seed testi Tur 1'de de yapilmamisti, bu bir tekrarlanan bosluk).

**[2] Egitim/Gorulmemis Bozulma — UYARI (yanitlayici degil)**
PF bozulmasi hesaplanamaz (n=0 her iki tarafta da). AUC uzerinden vekil karsilastirma: Walk-forward ort. 0,5098 vs TEST 0,5190 — **buyuk bir sapma YOK**, ama bu "iyi genelleme" anlamina GELMIYOR: her iki taraf da rassal-seviyeye (0,50) esit derecede yakin. Bu, klasik egitim-ezberleme (overfit) paterni degil, **"tutarli zayiflik"** paternidir — model ne egitimde ne testte hicbir yon-bilgisi ogrenmemis. Teknik olarak "GECTI" (buyuk sapma yok) ama bu bir basari sinyali degil, tam tersi: modelin ogrenecek bir sey bulamadiginin kanitidir.

**[3] Monte Carlo — N/A**
Islem yok (n=0), Monte Carlo shuffle uygulanamaz. Bu, "risk dusuk" anlamina gelmez — "test edilecek bir strateji yok" anlamina gelir.

**[4] Pes Pese Kayip — N/A** (n=0)

**[5] Kar Konsantrasyonu — N/A** (n=0, kar yok)

**[6] Kirilim Analizi — N/A** — rapor kirilim verisi icermiyor.

**[7] Parametre/Model Hassasiyeti — TEST YOK**
Bu tur icinde feature-eklenmesi disinda hicbir hassasiyet testi yapilmadi (S2 geregi dar hiperparametre araligi bilincli tercih — bu kendi basina elestiri konusu degil). Ancak: (a) tek random-seed, (b) esik-kalibrasyonunun kendisinin ne kadar kirilgan oldugu (0,575 esigine 0,0235 puan uzaklikla kalinmasi — esik biraz daha gevsetilseydi ne olurdu, test edilmedi) olculmedi. Tur 1'de model-ailesi (LightGBM/XGBoost) ve barrier-genisligi (k=1,5/2,0) zaten test edilmis ve fark yaratmamisti — bu eksen icin ek test gerekmez, ama bu turde YENI eklenen eksen (Grup B esik-kalibrasyon kirilganligi) hic test edilmedi.

**[8] Gercek Hayat Duzeltmesi — TANIMSIZ (n=0)**
0 islem uzerinden slipaj/psikoloji duzeltmesi yapilamaz. Pratik anlam: bu tasarim canliya alinsa, gecmis ~1 yillik test penceresinde HICBIR ISLEM ACMAYACAKTI — HEDEF_PF/WR/DD karsilanip karsilanmadigi degil, stratejinin fiilen CALISMADIGI sonucuna varilir.

### KARAR GEREKCE
Grup B (pivot/20-gunluk S-R mesafesi) eklenmesi, feature-onem tablosunu belirgin sekilde degistirdi (split-agirliginin ~%40'i Grup B'ye gecti, ozellikle `dist_weekly_pivot_pts`) — ancak bu degisim **TEST AUC'sinde (0,517→0,519, +0,002) veya tetiklenen islem sayisinda (0→0) HICBIR OLCULEBILIR ETKI YARATMADI.** Bu, Stratejist'in "feature seti degisirse model ogrenir mi?" sorusuna net bir yanit verir: HAYIR — model farkli yerlere "bakmayi ogrendi" ama bu, ayirt edici gucu veya islem uretme kapasitesini degistirmedi. S1 P90-stres testi de Tur 1 ile birebir ayni sekilde kaybedildi (11,91x < 15,0x). Kendi kriterlerimde "gorulmemis veri PF hedefin cok altinda" kosulu, PF'nin tanimsiz/olculemez olmasiyla (n=0) esdeger bir RED tetikleyicisidir — S2 Madde 4'un kendi ilkesi geregi ("olculemedi" = "karsilandi" iddia edilemez). **RED.**

---

# BOLUM B — HIPOTEZ 2 (3-Sinifli/Deadzone, Etiket+Feature-Izole)

## KARAR: RED

### KONTROLLER

**[1] Istatistiksel Anlamlilik — KIRMIZI**
OOF/trainval tarafinda esik=0,50/0,50 icin toplam pseudo-orneklem n=8.740 (buyuk) — AMA bu buyuklugun anlamli olmasi icin ONCE bir edge bulunmus olmasi gerekir (asagida [2]'de gorulecegi gibi YOK). **Gorulmemis veri (TEST) fiili islem sayisi = 15** — hem kendi MIN_SAMPLE(30) esiginin ALTINDA hem de genel "60-149 kabul edilebilir" bandinin cok altinda; bu, Muhendis'in kendi raporunda da acikca "YETERSIZ ORNEKLEM, tek basina karar dayanagi OLAMAZ" diye isaretlenmis. SHORT tarafinda test'te SIFIR islem (esik hicbir barda asagi-argmax+P>=0,50 kosulunu saglamadi) — model fiilen tek yonlu (LONG-only) davraniyor. Tek random-seed (yine coklu-seed testi YOK).

**[2] Egitim/Gorulmemis Bozulma — KIRMIZI**
Klasik PF-bazli IS/OOS karsilastirmasi burada da YAPILAMAZ (Muhendis, trainval uzerinde gercek P&L trade-simulasyonu calistirmadi — sadece OOF WR-proxy ve nihai TEST trade-simulasyonu var; bu, Kontrol 2'nin tam uygulanmasini engelleyen bir metodoloji bosluğudur, ayri bir bulgu olarak asagida not edildi). Mevcut veriyle en yakin vekil karsilastirma:
- OOF/trainval ortalama accuracy=%45,94 vs **TEST accuracy=%42,18** — ~3,8 puanlik dusus.
- Cok daha carpici olan: **TEST accuracy (%42,18), "HER ZAMAN YUKARI TAHMIN ET" seklindeki trivial sabit-siniflandiricinin (%46,96) ALTINDA** — model, gormedigi veride en basit sabit-tahmin stratejisinden bile DAHA KOTU performans gosteriyor. Bu, "biraz bozulma" degil, modelin gercek dunyada NEGATIF katma deger urettigi anlamina gelir.
- Confusion matrix: "notr" sinifi test'te argmax'ta HICBIR ZAMAN secilmedi — model egitimde %11 agirlikla gordugu 3. sinifi tamamen "unuttu", fiilen 2-sinifli davraniyor. 3-sinifli deadzone tasariminin temel amaci (orta bandi ayirt etmek) TEST'TE HIC gerceklesmedi.
- OOF WR-proxy (LONG=%49,74 esik=0,50'de) ile fiili TEST WR (%66,67, n=15) arasindaki fark TERS yonde (test daha "iyi" gorunuyor) — bu iyilesme DEGIL, kucuk-orneklem rastlantisidir (n=15'te tek bir buyuk kazanc/kayip sonucu tamamen degistirir, asagida [5]'te gosterildigi gibi).
**Sonuc: KIRMIZI** — hem OOS'ta trivial-taban-alti performans hem de deadzone konseptinin fiilen ogrenilmemis olmasi, bagimsiz iki kirmizi bayrak.

**[3] Monte Carlo — GECTI (sayisal) ama ANLAMSIZ n ile — dikkatli okunmali**
15 islemin gercek `net_usd_0_01_lot` degerleri uzerinde, kasa=2.000 USD referansiyla, 500 shuffle calistirildi (bagimsiz olarak yeniden hesaplandi, Muhendis raporunda bu analiz yoktu):
- Medyan DD: **%5,07**
- En kotu %5 DD: **%4,33** *(dikkat: medyandan DUSUK cikmasi n=15'in shuffle uzayinin cok dar/ayrik olmasindandir — asil "en kotu senaryo" 500 shuffle icindeki mutlak maksimum: %7,37)*
- Aralik: %4,32 – %7,37
Sayisal olarak "Guclu" bandinda (≤%15) GECTI. **ANCAK bu sonuc guven verici DEGIL**: 15 elemanlik bir kumeyi yeniden siralamak, gercek gelecekteki kayip serilerini/ekstrem-ATR olaylarini simule ETMEZ — sadece ELDEKI 15 sayinin farkli dizilimlerini dener. Bu MC testi, asil risk kaynagini (asagida [4]) YAKALAYAMAZ.

**[4] Pes Pese Kayip — UYARI + KRITIK EK BULGU (risk-tavani ihlali)**
Gercek max pes pese kayip = 1 (hicbir zaman ust uste 2 kayip yok) — teorik beklenti log(0,05)/log(1-0,667)=~2,7 ile karsilastirildiginda dusuk/normal gorunuyor, ama n=15 ile bu istatistik guvenilir degil.

**Kritik bulgu (bagimsiz kod/veri incelemesiyle tespit edildi, Muhendis raporunda VURGULANMAMIS):** Islem loguna tek tek bakildiginda, **2/15 islemde (%13,3) fiili islem-basi risk, `justin_gecmis_calisma.md`'nin %1 UST SINIR kuralini ACIKCA ihlal ediyor:**

| Tarih | ATR (giris ani) | risk_pct_of_kasa | %1 sinirina gore |
|---|---|---|---|
| 2026-01-22 | 1.740,5 pts | **%1,305** | 1,3x asim |
| 2026-01-30 | 5.851,3 pts | **%4,389** | **4,4x asim** |

Muhendis raporu SADECE ORTALAMA riski bildirdi ("Ortalama risk/kasa: %0,924, RISK_PCT_CAP %1 SINIRI ICINDE") — bu ortalama dogru olsa da, **tek-tek islem bazinda kurali ihlal eden ornekleri gizliyor.** Sebep yapisal: kasa=2.000 USD icin lot SABIT 0,01'de tutuluyor (gecmis-calisma dosyasindaki "risk-tutarlilik formulu" — lot = (kasa×0,01)/(SL_puan×$/puan) — ATR spike anlarinda GEREKEN kucuk lotu 0,01 TABANININ ALTINA dusuremiyor, taban asiliyor). Gecmis-calisma dosyasi bu asimi SADECE kasa 2.000 USD'nin ALTINA dustugunde ("DD-stop esigine yakin") bekliyordu — ama burada kasa hala baslangic seviyesindeyken (~2.000 USD, hicbir DD-stop yakininda degilken), SADECE ATR'nin olagandisi genislemesi (5.851 puan, medyan 287 puanin ~20 kati) yuzunden asim gerceklesti. **Bu, ML modelinin isabet kalitesinden BAGIMSIZ, saf risk-yonetimi/pozisyon-boyutlandirma tasarim acigidir** ve hem Hipotez 1 hem Hipotez 2'de (ayni k_risk/lot mekanizmasi paylasildigi icin) gecerlidir — Hipotez 1'de fiilen islem uretilmedigi icin bu turde GORULMEDI ama mekanizma orada da AYNIDIR, ileride islem uretilirse ayni risk gecerli olacaktir.

**[5] Kar Konsantrasyonu — KIRMIZI**
En iyi 3 islem / toplam brut kar = (25,18+20,48+15,63)/116,00 = **%52,8** — kirmizi bayrak esiginin (%35) belirgin uzerinde. 15 islemlik orneklemin yarisindan fazlasi UC islemden geliyor; PF=0,781 ve WR=%66,67 gorunumu, bircok kucuk kazanc + birkac buyuk kayiptan degil, aslinda az sayida buyuk kazancla desteklenen kirilgan bir profil. Tek gun/hafta konsantrasyonu: 2026-01-22 gunu 2 islem barindiriyor (biri -26,85 biri +20,48 USD, net -6,37) — tek gun >%40 katkisi yok, ama kar-konsantrasyonu maddesi zaten kirmizi.

**[6] Kirilim Analizi — N/A** — rapor kirilim verisi icermiyor.

**[7] Parametre/Model Hassasiyeti — TEST YOK + acik bir hassasiyet sorusu**
k_label=0,3xATR14-Wilder, notr_orani (%11,0) "dengeli" bant icinde kaldigi icin grid-arama (0,15-0,5) TETIKLENMEDI — yani k_label=0,3 disinda BASKA HICBIR deger denenmedi, secilen deger sadece "dagilim makul gorundugu icin" sabitlendi, performans acisindan sinanmadi. Ayrica **ATR tanim-karisikligi** (k_risk=BASIT rolling-ortalama, k_label=WILDER-smoothed) Muhendis tarafindan seffaf raporlanmis, kod-duzeyinde dogru ayristirilmis (karistirilmamis) — bu KENDI BASINA bir hata degil, ama Stratejist'in "Wilder = v1 ile tutarli" notunun kod-incelemesiyle DOGRULANAMADIGI (v1'in fiili ATR fonksiyonu BASIT'tir, Wilder degil) ortaya cikmis bir terminoloji-karisikligidir. Sonuc degismeyecek kadar kucuk bir etki olabilir ama **test edilmedi** — k_label icin de BASIT ATR kullanilsaydi sonuc nasil degisirdi, bilinmiyor. Bu, KOSULLU'ye giden bir madde olabilirdi ama asagidaki diger kirmizi bayraklar zaten RED'i tek basina gerektiriyor.

**[8] Gercek Hayat Duzeltmesi — KIRMIZI**
Maliyet (spread+slipaj) BACKTESTTE ZATEN tick-bazli gercek kotasyonlarla dahil edilmis (`toplam_maliyet_pts` her islemde ayri raporlanmis, ort. 79,4 puan/islem) — bu yuzden EK bir slipaj duzeltmesi UYGULANMADI (cift sayma riski). Psikoloji/uygulama payi icin proje-ozel bir deger saglanmadigindan **varsayilan %12,5 (aralik %10-15 orta nokta) muhafazakar haircut** brut kara uygulandi (bu ACIKCA bir varsayimdir, gizli degildir):
```
Brut Kar (duzeltilmemis)   = 116,0006 USD
Duzeltilmis Brut Kar       = 116,0006 x (1-0,125) = 101,50 USD
Brut Zarar (degismedi)     = 148,5661 USD
Duzeltilmis PF             ≈ 101,50 / 148,5661 = 0,683
```
Duzeltilmis PF (~0,68), zaten hedefin (1,5) altinda kalan ham PF'yi (0,781) DAHA DA kotulestiriyor — hedefin **~%45,5'i.** Kendi kriterimin "hedefin ~%65'inden az → RED" esigini rahatlikla asıyor (asagida kaliyor, yani RED tetikleyici).

### KARAR GEREKCE
Hipotez 2, Hipotez 1'e gore islem URETME kapasitesi acisindan (0→15) bir farklilik gosterdi — ancak bu, "daha iyi bir strateji" DEGIL. Test performansi trivial-taban-cizgisinin altinda (model gercek dunyada rastgele sabit-tahminden bile kotu), deadzone'un temel amaci olan "notr" sinifi test'te hic secilmedi, PF (0,781, duzeltilmis ~0,68) HEDEF_PF'nin (1,5) belirgin altinda, orneklem (n=15) MIN_SAMPLE'in altinda, kar-konsantrasyonu (%52,8) kirmizi bayrak esiginin uzerinde, ve BAGIMSIZ olarak tespit edilen bir risk-yonetimi tasarim acigi (2 islemde %1 risk tavaninin 1,3x-4,4x asilmasi) ML kalitesinden bagimsiz ek bir ciddi bulgu. Bu kadar cok ve birbirinden bagimsiz kirmizi bayrak birikimi (5+ madde), tek basina herhangi biri KOSULLU sinirinda olsa bile toplamda net bir **RED** gerektirir.

---

# BOLUM C — TAM TUR 2 GENEL SONUC (S3 Governance Acisindan)

**Her iki hipotez de RED sonuclandi ve ikisi de Tur 1'in paternini (rassal-seviye/trivial-taban-alti ayirt edicilik, ana feature gruplarinin/yeni Grup B'nin ölçülebilir edge uretmemesi, esik-kalibrasyonunda anlamli islem hacmi olusmamasi veya olussa bile hedefin cok altinda kalmasi) tekrarliyor — bu, Stratejist'in ozenli izolasyon tasarimina (Hipotez 1=sadece-feature, Hipotez 2=feature+etiket) ragmen, hem feature-eklemenin (Grup B, pivot/S-R) hem de etiket-degisikliginin (3-sinifli deadzone) bu M15/N=16/k=1,5 kurulumunda gercek bir yon-tahmin edge'i URETMEDIGINI gosteriyor; dolayisiyla Risk Analisti karari S3 sayacini **2/2'ye tasir** — Orkestrator'un bir sonraki Arastirmaci turunu Ertan'in acik onayi olmadan baslatmamasi gerektigi (Stratejist/Orkestrator'un onceden belirledigi esik) bu raporla teyit edilmis olur; bu kararin sonraki-adim sorumlulugu Risk Analisti'nde degil Orkestrator'dadir.**

---

# STRATEJISTE GERI BiLDiRiM

**Hipotez 1 icin:**
- Grup B (pivot/S-R) eklenmesi feature-onem paternini degistirdi ama performansi/islem-uretimini degistirmedi — bir SONRAKI turde tek-feature-grubu eklemeleri yerine, sorunun kaynagini (etiket ufku N=16/k=1,5'in KENDISI, ya da M15 gold fiyat-aksiyonunun bu ufukta genel olarak dusuk sinyal/gurultu orani tasimasi) sorgulamak daha verimli olabilir.
- Esik-kalibrasyon kirilganligi (p_test max=0,5515, secilen esik=0,575, sadece 0,0235 puan fark) test edilmeli: esik biraz gevsetilirse (orn. 0,55) ne olurdu, bu ayri bir duyarlilik analizi olarak eklenebilir (ama bu, S2 Madde 2'nin "test setine bakmadan kalibre et" ilkesini ihlal etmeyecek sekilde SADECE OOF uzerinde yapilmali).

**Hipotez 2 icin:**
- k_label=0,3xATR14 disinda BASKA hicbir deger denenmedi (dengeli-bant kosulu grid-aramayi tetiklemedi) — bir sonraki turde bu sabit degerin sonuc uzerindeki etkisi en azindan 2-3 alternatif degerle (orn. 0,2 ve 0,4) OOF uzerinde kiyaslanmali.
- **ONCELIKLI/ACIL:** Position-sizing/lot-kurali gozden gecirilmeli. Sabit 0,01 lot + ATR-olcekli SL/TP kombinasyonu, ATR olagandisi genisledigi zaman (gozlemlenen ornekte medyanin ~20 kati) `justin_gecmis_calisma.md`'nin kendi %1 UST SINIR kuralini kasa DD-stop esiginden BAGIMSIZ olarak ihlal edebiliyor (bu turde 2/15 islemde, biri 4,4x asimla). Bu ML hipotezinin KABUL/RED durumundan BAGIMSIZ, projenin risk-cercevesinde (gecmis-calisma dosyasi) ele alinmasi gereken ayri bir maddedir — ONERI: ya (a) SL puani belirli bir esigi (orn. medyan ATR'nin 3-5 kati) astiginda islem ATLANSIN, ya da (b) lot, taban 0,01'in ALTINA da (kesirli/mikro-lot izin veriliyorsa) inebilsin, ya da (c) mevcut taban korunacaksa bu asim acikca kabul edilen/onaylanan bir istisna olarak Ertan'a bildirilsin.
- Deadzone/3-sinif tasarimi bu turde "notr"u fiilen ogrenemedi — bir sonraki turde bu yaklasima devam edilecekse, notr sinifinin egitimde neden secilmedigi (class-weight, esik, veya feature-yetersizligi) ayrica arastirilmali.

---

# KULLANICIYA

Iki yeni ML denemesi de (biri "yukari mi asagi mi" tahmin eden basit model, digeri "yukari/asagi/notr" olarak uc secenekli tahmin eden model) gecmis veriyle sinandi ve ikisi de **RED** aldi — yani su haliyle canliya/demoya gecmeye hazir degiller. Birinci model, gormedigi ~1 yillik veride TEK BIR islem bile acmadi (fiilen "hicbir zaman sinyal vermeyen" bir sistem oldu). Ikinci model 15 islem uretti ama bu sayi guvenilir bir sonuc cikarmak icin cok az (istatistiksel olarak anlamsiz), kar/zarar orani hedefin (1,5) yaklasik yarisinda (0,78, gercekci maliyetler eklenince ~0,68'e daha da dusuyor), ve kazancin yarisindan fazlasi sadece 3 islemden geliyor — yani "iyi gorunen" sonuc aslinda birkac sansli islemin urunu, kararli bir avantaj degil. Ayrica bagimsiz incelemede onemli bir ayri bulgu ortaya cikti: bu iki modelin de kullandigi risk-hesaplama yontemi, bazen (asiri oynak piyasa anlarinda) tek bir islemde, izin verilen %1'lik risk sinirini 4 katina kadar asabiliyor — bu, modellerin basarili olup olmamasindan bagimsiz, ayrica duzeltilmesi gereken bir risk-yonetimi sorunudur. Ozetle: bu tur da onceki tur gibi "gercek bir tahmin gucu bulunamadi" sonucuna ulasti; sistem artik iki turde de ayni sonuca vardigi icin bir sonraki arastirma adiminin baslatilip baslatilmayacagina Ertan'in karar vermesi gerekecek (bu, Orkestrator tarafindan ayrica sorulacak).
