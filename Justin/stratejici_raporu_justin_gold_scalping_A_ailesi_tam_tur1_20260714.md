# STRATEJICI RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following), TAM TUR 1

Tarih: 14 Temmuz 2026
Gorev kaynagi: Orkestrator cagrisi (15:05), hedef: A ailesi icin 3 kural-tabanli varyant (H1,
H2, H3) — Ertan'in Cevap 2 karari geregi ayristirilmis format, "5" gibi birlesik sayi YOK.
Bu, Justin/A-ailesi hattinin **Tam Tur 1**'idir (gunluk pipeline sayaci: 1/5).

Girdi olarak kullanilan gecmis calisma dosyalari:
- `arastirmaci_gold_scalping_adim0_tarama_raporu.md` (Adim 0 — bar-bar otokorelasyon/VR/
  streak + S1)
- `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (ek on-tarama — yapisal kanal +
  M15/M5 giris-zamanlama + S1, Celiski Bulgusu kismi/kirilgan cozum)
- `justin_strateji_ailesi_plani_ertan_kararlari_20260714.md` (Ertan'in 5 cevabi + A/C
  duzeltmesi — governance)
- `orkestrator_yanit_3soru_justin_20260714.md` (S1 esiginin degismeme gerekcesi)
- `orkestrator_gorus_strateji_ailesi_plani_20260712.md` (orijinal plan taslagi)
- `justin_backtest_onkontrol_standardi.md` (kalici on-kontrol standardi — DST, maliyet-orani,
  SL/TP-ozel-belirleme)

Izolasyon: Bu rapor yalniz yukaridaki `C:\MilaYatirim\Justin\` ici dosyalar kullanilarak
hazirlanmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, deger veya format/sablon
referans olarak ACILMAMISTIR.

---

## OZET

Adim 0 (bar-bar istatistik) ve ek pivot/kanal taramasi (yapisal-kanal istatistigi) BIRLIKTE
su tabloyu birakti: bar-bar otokorelasyon/VR/streak bulgulari hafif TERSINE-DONUS isareti
gosterirken, >=3-dokunuslu + EMA50/200 + MACD teyitli yapisal kanallar H1/M30'da GERCEKTEN
haftalarca suren trendler ortaya cikardi (medyan omur ~3-5 hafta). Ancak onay-sonrasi
"trend yonunde devam" orani (1/3/7/14 gun) TUTARSIZ ve monotonik degil (%13-80 arasi,
n=15-39 kucuk orneklem) — yani "yapisal trend onaylandi = guvenle devam eder" varsayimi bu
veri setinde DESTEKLENMIYOR. S1 (maliyet/hedef>=15-20x) bu yapisal-kanal + M15/M5-giris
kombinasyonlarinda Adim 0'a gore cok daha kisa surelerde asiliyor (M5-giris: 0,9-3,7 saat;
M15-giris: 4,4-10,3 saat) — ama M5-giris bulgusu SADECE 2-8 bagimsiz kanala ve ~17 aylik dar
veri donemine dayaniyor (Orkestrator'un acikca "celiski cozuldu SAYILMAMALI" dedigi nokta).

Bu bilgiler isiginda, asagidaki 3 varyant TEK bir mekanizmaya (ornegin sadece M5-giris)
yatirim yapmiyor; ucu de ayni pivot/kanal-onay mantigini (giris/rejim-filtresi olarak)
KULLANIYOR ama farkli giris-ufku ve farkli yon-simetrisi ile ayrisiyor — boylece Backtest
Muhendisi'ne hem kirilgan/dar-kanitli aday (H1) hem daha genis-orneklemli aday (H2) hem de
en tutarli alt-kumeye odakli asimetrik aday (H3) birlikte, birbirinin dogrulamasi/kontrolu
olarak sunuluyor.

**Onemli metodolojik uyari (tum varyantlar icin gecerli, RISKLER'de tekrarlaniyor):**
Arastirmaci'nin pivot/swing tanimi ("bar i, high[i]==max(high[i-5:i+6])") ILERI-BAKISLIDIR —
bir barin "swing" oldugu ancak 5 bar SONRA kesinlesir. Bu, gercek-zamanli bir sistemde kanal
cizgisinin/dokunus sayaci nin 5-bar GECIKMELI olustugu anlamina gelir. Backtest Muhendisi bu
gecikmeyi ACIKCA modellemezse (yani "confirmed" bir swing/kanal'i olustugu andan degil, 5 bar
SONRA mevcutmus gibi kullanirsa), bu bir LOOK-AHEAD BIAS kaynagi olur. Bu, asagidaki her
varyantin DOGRULAMA IHTIYACI ve RISKLER bolumlerinde ayrica belirtiliyor.

---

## H1 — "DAR-KANIT M5-GIRIS" (H1/M30 Yapisal Kanal + M5 Giris-Zamanlama, Simetrik Iki Yon)

**YAKLASIM TURU:** Kural-tabanli.

**MANTIK:** Pivot/kanal tarama raporunun Celiski Bulgusu'ndaki EN scalping-uyumlu alt-kume
budur: H1 veya M30'da onaylanmis (>=3 dokunus + EMA50/200 + MACD teyitli) bir yapisal kanal
aktifken, kanal cizgisinin M5 barlarina projeksiyonuna bir M5 barinin dokunmasi ve BIR SONRAKI
M5 barinin trend yonunde kapanmasi giris tetigidir. Bu kombinasyon (H1→M5 ve M30→M5, her iki
yon) S1 esigini 0,9-3,7 saatte geciyor — Adim 0'in en iyi adayindan (M15, 5,3-8,3 saat) daha
NET bir sekilde Ertan'in "dakikalar-birkac saat" (Cevap 3, KESIN) tanimina uyuyor. Orkestrator
bu bulguyu "ADAY yon" olarak degerlendirip en az bir varyantin bu mekanizmayla kurulup genis-
orneklem/farkli-donem dogrulamasina birakilmasini ONERMISTI (Onerilen Sonraki Adim, madde 1/3)
— H1 bu oneriyi karsiliyor.

**YONTEM DETAYI:**
- Rejim/giris-filtresi: H1 veya M30'da >=3 dokunuslu + EMA50>EMA200 (yukselen) veya
  EMA50<EMA200 (alcalan) + MACD(12,26,9) yon-uyumlu onaylanmis kanal AKTIF olmali (kirilmamis).
- Giris tetigi: kanal cizgisinin M5 projeksiyonuna bir M5 barinin |kapanis-projeksiyon| <=
  0,5xATR14_M5 ile dokunmasi + bir SONRAKI M5 barinin trend yonunde kapanmasi.
- Yon: HER IKI yon de (yukselen kanal→BUY, alcalan kanal→SELL) — simetrik, tek yone
  onyargili degil (H3'ten farki budur).

**GIRIS/CIKIS MEKANIZMASI:**
- Giris: yukaridaki tetik olustugunda, tetigi olusturan M5 barinin kapanisinda.
- Cikis: UC kosuldan HANGISI ONCE gerceklesirse:
  (1) SL (ATR14_M5 bazli, dar — orn. ~0,5x ATR14_M5, kesin katsayi Backtest Muhendisi'nin
      walk-forward'da kalibre edecegi bir parametre, burada dayatilmiyor);
  (2) TP (S1-esigini gecen N-bar ufkundaki gozlemlenen medyan hareket mesafesine yakin bir
      hedef — yaklasik olcek: H1→M5 alcalan icin ~700 puan mertebesi, diger kombinasyonlar
      icin tabloya gore degisir; kesin deger yine Backtest Muhendisi'nde kalibre edilir);
  (3) **Kirilim-bazli erken cikis:** kanal, pozisyon acikken KIRILIRSA (Ertan'in "onaylanmis
      kanal = guvenli devam" varsayiminin bu veride desteklenmedigi bulgusu geregi), SL/TP
      beklenmeden pozisyon KAPATILIR. Bu, sabit bir "N saat/gun sonra kapat" kuralindan
      kacinmak icin bilincli bir tasarim tercihidir.

**SL/TP veya RISK YONETIMI:** Dinamik, ATR14_M5 bazli (sabit puan degil) + yukaridaki
kirilim-bazli erken-cikis kurali. Kesin SL/TP katsayilari burada BELIRLENMIYOR (asiri
optimize etmemek icin) — Backtest Muhendisi'nin walk-forward asamasinda kalibre edecegi
parametreler olarak birakiliyor; standart geregi (`justin_backtest_onkontrol_standardi.md`
Madde 3) bu deger onceki hipotezden otomatik TASINMAYACAK.

**DOGRULAMA IHTIYACI:** Walk-forward (train/test/validation ayrimi), S1'in gercek SL/TP
mesafeleriyle (proxy degil) yeniden hesaplanmasi. **KRITIK EK IHTIYAC:** bu kombinasyon
sadece 2-8 bagimsiz kanala ve ~17 aylik (2025-02→2026-07) dar veri donemine dayaniyor —
Backtest Muhendisi mumkunse farkli/daha genis bir M5 veri donemi veya farkli broker/veri
kaynagi ile bu bulgunun donem-etkisi mi yoksa kalici bir ozellik mi oldugunu ayrica
sinamalidir. Ayrica 5-bar-gecikmeli swing-onayi (yukaridaki Onemli Uyari) backtest'te
DOGRU modellenmelidir (look-ahead bias kontrolu).

**RISKLER:**
- **Dar orneklem/kirilganlik (en yuksek risk):** 2-8 kanal, ~17 aylik veri — Orkestrator'un
  acikca belirttigi gibi bu "celiski cozuldu" degil, kirilgan bir bulgudur.
- **Look-ahead bias:** pivot tanimi ileri-bakisli (N=5 sag pencere); backtest'te 5-bar
  gecikme modellenmezse sonuclar yapay derecede iyi cikabilir.
- **Dusuk islem frekansi/uzun bekleme donemleri:** H1'de ~2,9-4,2 kanal/yil, M30'da ~3,5-6,8
  kanal/yil — kanal SAYISI dusuk (giris-tetigi sayisi yuksek olsa da bunlar birkac kanal
  icinde tekrarlanan olaylardir). Canli sistemde bu, kanal-arasi uzun "islem yok" donemleri
  yaratabilir; scalping beklentisi (sik islem) ile potansiyel gerilim, ayrica izlenmeli.
  M5-giris frekansi kanal AKTIFKEN yuksek olabilir (binlerce dokunus), ama kanal sayisi az.
- **Canliya gecebilirlik:** kanal onayi (fraktal pivot + line projection + touch/dokunus
  sayaci) gercek zamanli bir MT5 agent icinde HER YENI BAR icin hesaplanabilir olmali; 5-bar
  gecikmeli confirm mantigi gercek-zamanli implementasyonda ayri bir muhendislik konusudur,
  bu turde test EDILMEMISTIR.
- Overfitting riski goreceli DUSUK (kanal parametreleri — N=5 fraktal, 0,5xATR tolerans,
  EMA50/200, MACD 12/26/9 — standart/optimize-edilmemis degerler), ama SL/TP kalibrasyonu
  walk-forward disi yapilirsa overfitting riski yeniden dogar.

**ONCELIK: 1-Yuksek** — Ertan'in Cevap 3 (scalping karakteri KESIN) kisitina EN net uyan
aday oldugu icin test onceligi yuksek; ancak aym nedenle (en dar kanit) dogrulanmadan
guvenilmemeli — oncelik "hemen test et", "hemen guven" degil.

---

## H2 — "GENIS-ORNEKLEM M15-GIRIS" (H1/M30 Yapisal Kanal + M15 Giris-Zamanlama, Simetrik Iki Yon)

**YAKLASIM TURU:** Kural-tabanli.

**MANTIK:** Ayni kanal-onay mekanizmasi, ama M15 giris-zamanlamasi kullanan alt-kume —
istatistiksel olarak daha saglam (6-18 ortusen kanal, H1'e gore M5-girisin 2-8'ine kiyasla).
S1 esigi 4,4-10,3 saatte geciyor; bu, Adim 0'in M15 bulgusuyla (5,3-8,3 saat) BENZER
mertebede ama biraz daha genis orneklemle destekleniyor. Bu, Adim 0'daki "S1 vs
scalping-uyumlu SL/TP" sinir-bolgesi gerilimini BUYUK OLCUDE TEKRARLIYOR — bu acikca
kabul ediliyor, "cozuldu" olarak SUNULMUYOR.

**YONTEM DETAYI:**
- Rejim/giris-filtresi: H1 tanimi ile ayni (>=3 dokunus + EMA50/200 + MACD teyitli
  onaylanmis, aktif/kirilmamis kanal, H1 veya M30 ufkunda).
- Giris tetigi: kanal cizgisinin M15 projeksiyonuna bir M15 barinin |kapanis-projeksiyon|
  <= 0,5xATR14_M15 ile dokunmasi + bir SONRAKI M15 barinin trend yonunde kapanmasi.
- Yon: HER IKI yon (simetrik).

**GIRIS/CIKIS MEKANIZMASI:** H1 ile ayni uc-kosullu cikis semasi (SL / TP / kirilim-bazli
erken-cikis), ATR14_M15 bazli, farkli ufuk/mesafe olcegiyle. Kirilim-bazli erken-cikis kurali
burada da AYNI GEREKCEYLE (devam-oraninin tutarsizligi) korunuyor.

**SL/TP veya RISK YONETIMI:** Dinamik, ATR14_M15 bazli + kirilim-bazli erken cikis. Kesin
katsayilar Backtest Muhendisi'nde kalibre edilir (H1'deki gerekceyle ayni — otomatik
tasima yok).

**DOGRULAMA IHTIYACI:** Walk-forward, S1'in gercek SL/TP ile yeniden hesaplanmasi. Bu varyant
H1'e gore daha genis kanal sayisina (6-18) dayandigi icin orneklem-kirilganligi riski daha
DUSUK, ama tutma-suresinin (4,4-10,3 saat) scalping tanimina uyup uymadigi Backtest
Muhendisi/Risk Analisti asamasinda ACIKCA sinir-bolgesi olarak isaretlenmeli — otomatik
"scalping-uyumlu" kabul EDILMEMELI. 5-bar-gecikmeli swing-onayi (Onemli Uyari) burada da
gecerli.

**RISKLER:**
- **Scalping-tanimi gerilimi (Cevap 3 ile en dogrudan gerilim tasiyan varyant):** 4,4-10,3
  saatlik tutma suresi "birkac saat" ile "gunun buyuk kismi" sinirinda; Risk Analisti/Ertan'a
  bu gerilim acikca raporlanmali, sonuc RED gelirse bu "aile olu" degil "scalping-tanimi
  gerilimi" olarak yorumlanmali (atif netligi).
- Look-ahead bias riski (H1 ile ayni gerekce — pivot tanimi ileri-bakisli).
- Dusuk kanal-sayisi/islem-frekansi riski (H1'deki ayni not, yillik kanal sayisi ayni kaynaktan).
- Onay-sonrasi devam-oraninin tutarsizligi (H1/M30 kombinasyonlarinin tumu icin gecerli genel
  bulgu) — kirilim-bazli erken-cikis bunu kismen telafi ediyor ama garanti degil.
- Canliya gecebilirlik riski H1 ile ayni (fraktal pivot + kanal hesaplama gercek-zamanli MT5
  agent icinde test edilmedi).

**ONCELIK: 1-Yuksek** — istatistiksel olarak en saglam temel (en genis kanal sayisi), H1 ile
PARALEL test edilmesi oneriliyor (H1'in dar-kanit riskine karsi bir capraz-kontrol islevi
gorur — ikisi ayni yonde/tutarli sonuc verirse bu, mekanizmanin kendisi icin daha guclu bir
kanit olur).

---

## H3 — "M30-YUKSELEN ODAKLI ASIMETRIK FILTRE" (M30 Yukselen Kanal + M15 Giris, YALNIZCA UZUN)

**YAKLASIM TURU:** Kural-tabanli (yon-asimetrik filtre eklenmis).

**MANTIK:** Pivot/kanal taramasinin en tutarli tekil bulgusu M30-yukselen kanallarin devam
oranidir (%63-80, TUM ufuklarda %50 ustunde — diger tum ufuk/yon kombinasyonlarinin aksine)
VE kirilim-sonrasi tersine-donus orani en dusuk olan da yine M30-yukselen'dir (%13-33,
C-Notu). Bu, Onerilen Sonraki Adim'in 4. maddesinde acikca "ayrica incelenebilecek bir
gozlem" olarak isaretlenmisti (n=20, kucuk orneklem, teyide muhtac). H1/H2'nin simetrik
(iki-yonlu) tasariminin aksine, H3 BILINCLI olarak sadece bu en-tutarli alt-kumeyi (M30
yukselen, uzun/BUY tarafi) hedefliyor ve alcalan kanallari/SELL tarafini bu varyantta
DENEMIYOR — mekanizma farki budur (H1/H2'den ayrisan tasarim karari, sadece parametre
degisikligi degil).

**YONTEM DETAYI:**
- Rejim/giris-filtresi: SADECE M30'da onaylanmis (>=3 dokunus + EMA50>EMA200 + MACD_line>
  MACD_signal) YUKSELEN kanal aktifken islem dusunulur. Alcalan kanal/SELL tarafi bu
  varyantta YOK.
- Giris tetigi: M30→M15 giris-zamanlama tanimi (H2 ile ayni mekanik, ama sadece yukselen
  kanal + BUY yonunde uygulanir): M15 barinin kanal cizgisine dokunmasi + bir sonraki M15
  barinin yukari kapanmasi.
- Yon: SADECE BUY/uzun (asimetrik — H1/H2'den mekanizma farki).

**GIRIS/CIKIS MEKANIZMASI:** Giris H2 ile ayni mekanik (sadece yon kisitli). Cikis: ayni
uc-kosullu sema (SL / TP / kirilim-bazli erken cikis, ATR14_M15 bazli) — ama devam-orani
bu alt-kumede daha tutarli oldugu icin TP mesafesi Backtest Muhendisi tarafindan bu alt-kume
icin AYRI kalibre edilebilir (H2'nin genel TP kalibrasyonundan farkli olabilir, otomatik
tasima yapilmiyor).

**SL/TP veya RISK YONETIMI:** Dinamik, ATR14_M15 bazli + kirilim-bazli erken cikis (H2 ile
ayni cerceve, M30-yukselen alt-kumesine ozel kalibre edilecek). Kesin katsayilar Backtest
Muhendisi'nde belirlenir.

**DOGRULAMA IHTIYACI:** Walk-forward, ozellikle bu varyant icin OUT-OF-SAMPLE dogrulama
kritik — devam-orani/tersine-donus-orani bulgusu n=15-20 KUCUK orneklemden geliyor, in-sample
gorunen %63-80 devam oraninin out-of-sample'da tekrar edip etmedigi ayrica test edilmeli.
S1'in bu alt-kume icin (M30→M15 yukselen: 15x=~4,4 saat, 20x=~7,2 saat) gercek SL/TP ile
yeniden hesaplanmasi. 5-bar-gecikmeli swing-onayi (Onemli Uyari) burada da gecerli.

**RISKLER:**
- **En kucuk orneklem/en yuksek overfitting riski uc varyant arasinda:** n=20 kanal (devam-
  orani) / n=15 kanal (C-Notu tersine-donus) — bu, "M30-yukselen en tutarli" bulgusunun kendisi
  kucuk-orneklem gurultusu olabilecegi anlamina gelir; bu sadece bir GOZLEM, bir kanitlanmis
  patern degil (Arastirmaci raporu bunu acikca boyle isaretledi).
  Bu varyant Backtest Muhendisi tarafindan digerlerinden daha SIKI bir out-of-sample
  standardiyla degerlendirilmelidir.
- Look-ahead bias riski (ayni gerekce, H1/H2 ile ortak).
- **Islem frekansi en dusuk uc varyant arasinda olabilir** (sadece yukselen-M30 + uzun taraf,
  ~3,5/yil kanal orani icinde bir alt-kume) — canli sistemde scalping beklenen islem
  sikligini karsilamayabilir; bu Risk Analisti asamasinda somut islem/ay sayisiyla
  degerlendirilmeli.
- Canliya gecebilirlik riski H1/H2 ile ayni (kanal hesaplama gercek-zamanli test edilmedi).

**ONCELIK: 2-Orta** — mekanizma olarak ilginc/farkli bir asimetri denemesi, ama n=15-20
kucuk orneklem nedeniyle H1/H2'ye gore daha dusuk guven duzeyiyle test edilmeli; RED
gelirse "asimetrik filtre fikri calismiyor" olarak okunmali, "A ailesi olu" olarak DEGIL
(H1/H2 ile karistirilmamali — atif netligi).

---

## RANGE-REJIMI FILTRE NOTU

Ertan'in Cevap 4 (KABUL — range rejiminde net trend olusana kadar islem acilmaz) her ucu
varyantin giris mekanizmasina ZATEN YAPISAL olarak islenmistir: her uc varyantta islem,
YALNIZCA >=3-dokunuslu + EMA50/200 + MACD-teyitli bir yapisal kanal AKTIFKEN acilabilir. Bu,
"net trend yok/belirsiz" durumun (henuz onaylanmis kanal olusmamis veya kanal kirilmis) kendi
basina bir islem-yok rejimi olarak davranmasini saglar — ayri bir rejim-katmani (Adim 3, N
ailesi) eklenmeden once bile. Adim 3'un rejim ust-katmani bu ucune, ileride, ek bir
boyutlandirma/filtre katmani olarak eklenebilir; bu turde uygulama etkisi yoktur (Ertan'in
Cevap 4'teki notuyla tutarli).

---

## ONCEKI-TUR-AYRISMA-TEYIDI

**N/A — bu turde GECERLI DEGIL.** Gerekce: `justin_strateji_ailesi_plani_ertan_kararlari_
20260714.md` (Cevap 1, Uygulama Notu) geregi bu kontrol maddesi Adim 1/Tur 2'den itibaren
zorunludur; bu rapor A ailesinin **ILK tam turudur** (Tam Tur 1), karsilastirilacak onceki bir
A-ailesi kural-tabanli turu yoktur. Bu madde Tur 2'den itibaren (bir sonraki A-ailesi
gorevlendirmesinde) bu raporun H1/H2/H3'unden ACIKCA mekanizma-duzeyinde ayrismasi teyit
edilerek doldurulacaktir.

---

## BACKTEST MUHENDISI'NE DEVIR NOTLARI

1. **DST/saat-eslesme dogrulamasi (ZORUNLU on-kosul, Adim 0'da da bu ek turde de
   YAPILMADI):** `justin_backtest_onkontrol_standardi.md` Madde 1 geregi, VPS'in gercek saat
   dilimi davranisi (GMT+3, DST gecisleri dahil) bu turde BAGIMSIZ olarak dogrulanmalidir —
   Stratejici bunu kendisi hesaplamamis, acikca Backtest Muhendisi'ne devretmektedir. M15/M5
   zaman-projeksiyonu (H1/M30 kanal cizgisinin dakika-bazli aktarilmasi) ozellikle bu
   dogrulamadan etkilenebilir bir islemdir.
2. **Look-ahead bias kontrolu (KRITIK, ucu de varyant icin ortak):** pivot/swing tanimi
   (N=5 fraktal, sag pencereli) ileri-bakislidir; backtest'te 5-bar gecikmeli confirm mantigi
   dogru modellenmezse yapay olarak iyi sonuclar cikabilir. Bu, on-kontrol asamasinda
   ACIKCA kontrol edilmeli.
3. **Maliyet-orani (S1) on-kontrolu:** Her varyantin GERCEK SL/TP mesafeleriyle (bu raporda
   verilen proxy-hedef degil) maliyet/hedef oraninin >= 15-20x oldugu yeniden hesaplanmali
   (`justin_backtest_onkontrol_standardi.md` Madde 2). Orani karsilamayan varyant on-kontrolde
   ELENIR, ana teste gecilmez.
4. **SL/TP — otomatik tasima yok:** her varyant icin SL/TP, bu raporda verilen ATR-bazli
   CERCEVE icinde, o varyanta OZEL kalibre edilmeli (Madde 3). H1/H2/H3 arasinda ayni SL/TP
   katsayisi varsayilmamalidir.
5. **H1 icin ek dogrulama:** dar orneklem (2-8 kanal) + kisa veri donemi (~17 ay) nedeniyle,
   mumkunse farkli/genis M5 veri donemi veya farkli veri kaynagiyla robustluk testi
   ONERILIYOR (KARAR degil, oneri — Orkestrator'un Onerilen Sonraki Adim madde 3'u ile
   tutarli).
6. **H3 icin ek dogrulama:** en kucuk orneklem (n=15-20); out-of-sample/walk-forward
   standardinin diger ikisine gore daha SIKI uygulanmasi oneriliyor.
7. **Islem frekansi olcumu:** her varyant icin gerceklesen ayda/yilda islem sayisi ayrica
   raporlanmali — kanal-sayisi dusuklugu (yiliik ~2,9-6,8 kanal) nedeniyle canli sistemde
   beklenen islem sikligi ile scalping beklentisi arasindaki uyum Risk Analisti asamasinda
   somut sayilarla degerlendirilmelidir.
8. **Kirilim-bazli erken-cikis mantiginin dogru implementasyonu:** ucu de varyantta, kanal
   kirilirsa SL/TP beklenmeden pozisyon kapatilir kurali backtest motorunda ayrica test
   edilmeli (bu, sabit sureli cikistan farkli bir mekanizma, yanlis implement edilirse
   sonuclari onemli olcude etkiler).

---

## SINIRLAMALAR

- Bu rapor, Arastirmaci'nin iki on-tarama raporundaki TUM sinirlamalarini (veri araligi
  asimetrisi, DST dogrulanmamasi, S1'in UST SINIR proxy niteligi, kucuk orneklem/sag-sansur,
  giris-tetigi olaylarinin bagimsiz olmamasi) DEVRALIR — bu rapor bu sinirlamalari COZMEZ,
  sadece onlari hesaba katan bir tasarim yapmaya calisir.
- Hicbir varyant henuz backtest EDILMEMISTIR — bu rapor hipotez uretimidir, "calisir" iddiasi
  YOKTUR.
- SL/TP kesin katsayilari kasitli olarak BELIRLENMEDI (asiri optimize etmeme ilkesi) — bu,
  Backtest Muhendisi'nin walk-forward asamasinda dolduracagi bir bosluktur, bir eksiklik
  degildir.
- H3'un "M30-yukselen en tutarli" bulgusu n=15-20 kucuk orneklemden gelir; bu rapor bu
  bulguyu bir TASARIM GEREKCESI olarak kullanir, ama bulgunun kendisinin dogrulugu icin
  kanit sunmaz (bu dogrulama Backtest Muhendisi'ne aittir).

---

## IZOLASYON NOTU

Bu rapor yalniz `C:\MilaYatirim\Justin\` ici dosyalar (Arastirmaci'nin iki on-tarama raporu +
Ertan'in governance kararlari + S1 standardi) kullanilarak hazirlanmistir. MilaGold/Lisa/
Signal GPT'ye ait hicbir dosya, bulgu, deger veya format/sablon referans olarak ACILMAMISTIR;
kullanilan sablon (HIPOTEZ ADI / YAKLASIM TURU / MANTIK / ... basliklari) Stratejici sistem
promptunun kendi kalici sablonundan turetilmistir, baska bir projeye ait dosyaya bakilarak
degil.
