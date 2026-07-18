# STRATEJIST RAPORU — Justin / Gold Scalping Hipotezleri (RAFINE — v2)

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: Yol1 dongusu 2 — Risk Analisti RED karari sonrasi Stratejist rafine turu
Tarih: 11 Temmuz 2026
Girdi:
  - Kendi onceki raporum: stratejici_raporu_justin_gold_scalping_20260710.md
  - Risk Analisti raporu: risk_analisti_raporu_justin_gold_scalping_hipotez1_20260710.md (KARAR: RED)
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)

---

## OTURUM OZETI

Risk Analisti, HIPOTEZ 1'i (Seans-Filtreli Asimetrik Ortalamaya-Donus) RED karariyla sonuclandirdi.
Gerekce saglam: ana konfigurasyonda ve k/giris/cikis/detrend taramasinin neredeyse tamaminda PF<1,
VE 6 walk-forward penceresinin 6'sinda da PF<1 (0,684-0,993 araligi). ZORUNLU detrend testi bile
(17 aylik yon-onyargisi cikarildiktan sonra) edge'i pozitife donduremedi. Bu, esik-ayari degil temel
mantik sorunu oldugu icin, bu turda kucuk revizyonlarla (R:R degisikligi, parametre kaydirma) kurtarma
girisimi YAPILMIYOR — Risk Analisti'nin kendi geri bildirimi de (madde 1-2) yeni bir filtre eklenirse
TAM pipeline'in (Arastirmaci→Stratejist→Backtest→Risk) yeniden gerekecegini, sadece parametre
kaydirmanin yeterli olmayacagini belirtiyor. Asagida bu karari isliyorum: Hipotez 1 kapatiliyor,
Hipotez 2 bir sonraki Backtest Muhendisi hedefi olarak teyit ediliyor, N-bar-zaman-cikis varyanti
icin ayri bir karar veriliyor, ve Justin icin ilk "gecmis calisma/cerceve" taslagi baslatiliyor.

Izolasyon kontrolu: Bu oturumda da stratejici_gold_gecmis_calisma.md veya herhangi bir MilaGold/Lisa/
Signal GPT dosyasi ACILMADI/referans ALINMADI. Sadece kendi onceki raporum ve Risk Analisti'nin Justin'e
ozel raporu girdi olarak kullanildi.

---

## 1) HIPOTEZ 1 — KAPANIS (Seans-Filtreli Asimetrik Ortalamaya-Donus)

**DURUM: KAPANDI — RED, canli/demo hesapta denenmeyecek, bu haliyle yeniden gundeme getirilmeyecek.**

Gerekce (Risk Analisti'nin bulgularini aynen kabul ediyorum, kendi yargimla teyit ediyorum):

- Ana konfigurasyon + genis parametre taramasi (k=1,5/2,0/2,5; giris next_open/close; cikis
  N-bar/ATR-TP-SL/combined; detrend ham/long/simetrik) neredeyse tamaminda PF<1. Sonucun DAR bir
  esige degil GENIS bir bolgeye yayilmis olmasi, bunun bir "sansli/sanssiz esik noktasi" (curve-fit)
  sorunu degil, mean-reversion hipotezinin bu enstrumanda/zaman diliminde bu haliyle gecerli bir edge
  saglamadigi anlamina geldigini gosteriyor.
- 6/6 walk-forward penceresi PF<1 (~17 ay) — tek donemlik carpitma degil, sistematik.
- ZORUNLU detrend testi (BULGU 6'nin 17 aylik yon-onyargisini fiyattan cikarma) edge'i pozitife
  DONDURMEDI — yani sorun sadece drift-onyargisindan da kaynaklanmiyor, mean-reversion mantiginin
  kendisi zayif.
- Gercek-hayat duzeltmesi (KONTROL 8) durumu daha da kotulestiriyor (~PF 0,75-0,80 bandina inme
  ihtimali).

Karar: Kucuk revizyon (R:R degisikligi, k kaydirma, farkli SMA/ATR periyodu) ile kurtarma
GIRISILMIYOR — bu, Risk Analisti'nin de belirttigi gibi yeni bir "yeniden pipeline'a sokma" isi
olur ve mevcut kanit, sorunun parametre degil mantik seviyesinde oldugunu gosteriyor. SMA20 +/- k*std
sapma-donus fikri bu proje/veri kombinasyonu icin **kapatilan bir hipotez** olarak isaretleniyor.
Ilerideki bir turda ayni fikir yeniden gundeme gelirse (orn. farkli bir enstruman/timeframe/rejim
filtresiyle), bu, mevcut Hipotez 1'in devami degil YENI bir hipotez olarak ele alinmali (kendi
Arastirmaci bulgusu + tam pipeline).

---

## 2) HIPOTEZ 2 — TEYIT EDILDI, ONCELIK YUKSELTILDI (Buyuk-Bar Ters-Yon/Fade)

**DURUM: bir sonraki Backtest Muhendisi hedefi olarak TEYIT EDILDI. Oncelik 2-Orta → 1-Yuksek
(Hipotez 1 kapandigi icin artik tek aktif/bagimsiz aday).**

Mantik ve yontem detayi degismedi (onceki rapor, HIPOTEZ 2 bolumu aynen gecerli — BULGU 4'e dayanan
buyuk-bar sonrasi hafif fade egilimi, %51,4/%52,9 ters yon orani). Risk Analisti'nin Hipotez 1
uzerindeki gozlemlerinden Hipotez 2'ye tasinan iki somut nokta var:

1. **Saat-esleme/DST riski Hipotez 2'ye de gecerli.** Onceki raporda Hipotez 2 icin "sunucu saati
   15-18 bandinda test edilmesi onerilir" demistim. Risk Analisti, Hipotez 1'de bu bandin DST
   donemlerinde kaymis olabilecegini bagimsiz dogrulayarak raporladi (sonucu degistirmedi cunku
   Hipotez 1 zaten PF<1'di, ama metodolojik risk gecerliligini koruyor). Hipotez 2 icin de
   Backtest Muhendisi ayni saat-esleme dogrulamasini (DST donemi/donemleri ayri raporlanarak)
   yapmadan once calismaya BASLAMAMALI — bu, asagidaki "DOGRULAMA IHTIYACI"na madde olarak eklendi.
2. **Metodoloji guveni artti.** Risk Analisti, Backtest Muhendisi'nin Hipotez 1'de ZORUNLU detrend
   testi, 6-pencereli walk-forward ve DST kontrolunu gerektigi gibi uyguladigini teyit etti. Bu,
   Hipotez 2 icin de ayni titizlik seviyesinin (ozellikle maliyet-dahil tick-bazli simulasyon ve
   istatistiksel anlamlilik testi) beklenebilecegi anlamina geliyor — asagida degismeden korundu.

Kucuk bir revizyon: Onceki raporda "cikis — kisa vadeli sabit bar sayisi (orn. 1-3 bar) veya ATR-bazli
TP/SL" deniyordu. Asagidaki madde 3'te (N-bar-zaman-cikis karari) belirtildigi gibi, zaman-bazli cikis
mekanizmasi Hipotez 1'den ayri dogrulanmamis bir bulgu olarak elenmedi, bunun yerine **Hipotez 2'nin
kendi cikis-yontemi taramasina bir secenek olarak dahil edilmesi** onerildi (asagida gerekce).

Guncellenmis ONCELIK: **1-Yuksek** — Hipotez 1 kapandigi icin sirali onceligin bir sonraki dogal
adimi; istatistiksel olarak ilginc (n cok buyuk, %51,4/%52,9), hizli test edilebilir (basit kural,
dusuk hesaplama maliyeti), ancak DOGRULAMA IHTIYACI'ndaki maliyet-once kontrolu (madde 2) GECILMEDEN
"canliya hazir" degerlendirmesi yapilamaz — bu sinirlama aynen korunuyor.

---

## 3) N-BAR-ZAMAN-BAZLI-CIKIS VARYANTI — KARAR: AYRI HIPOTEZ OLARAK ELENDI, MEKANIZMA OLARAK Hipotez 2'YE TASINDI

Risk Analisti'nin madde 3 onerisi iki secenek sunuyordu: (a) ayri bir hipotez olarak walk-forward ile
yeniden test ettirmek, veya (b) guvenilmez oldugu icin tamamen elemek. Kendi yargim:

**Ayri, bagimsiz bir Backtest Muhendisi turu olarak ELENDI** — asagidaki gerekcelerle:

1. Bu varyant, Hipotez 1'in **ayni mean-reversion giris mantigi** (SMA20 +/- k*std) uzerine kurulu,
   sadece cikis yontemi degistirilmis bir kombinasyon. Giris mantigi zaten genis bir bolgede (k,
   giris yontemi, detrend) tutarli sekilde basarisiz oldugu icin, yalniz cikis'i degistirip ayni
   girisi yeniden test etmek fiilen "parametre/mekanizma kaydirma" kategorisine giriyor — Risk
   Analisti'nin kendi geri bildirim madde 1-2'sinde tam olarak bundan kacinilmasi gerektigi
   soyleniyor (kucuk revizyonla kurtarma girisimi onerilmiyor).
2. Istatistiksel olarak da zayif: OOS PF=1,238 tek bir 70/30 bolmeye dayaniyor (walk-forward YOK),
   kendi IS'i (0,79) hala <1, ve tum-donem PF'si (0,953) yine de 1'in altinda. Normal beklenen
   overfitting paterni (IS iyi/OOS kotu) yerine TERSI (IS kotu/OOS "iyi") gorulmesi, bunun genellikle
   bir gercek edge'den cok ORNEKLEM SANSI (test penceresinin rastgele elverisli cikmasi) oldugunu
   dusundurur — ayri bir dogrulama turunu hak edecek kadar guclu bir sinyal degil.
3. Ayri bir Backtest Muhendisi turu acmanin firsat maliyeti var: Hipotez 2 zaten sirada, kaynak
   (Muhendis zamani) buraya ayrilirsa Hipotez 2'nin test hizini yavaslatir.

**Ancak** zaman-bazli cikis KAVRAMININ KENDISI (N bar sonra pozisyonu kapatma) tamamen degersiz
degil — bu, ozellikle kisa-vadeli/scalp tarzi bir sinyal olan Hipotez 2 icin makul bir cikis
secenegi. Bu yuzden N-bar-zaman-cikis, **Hipotez 2'nin kendi GIRIS/CIKIS taramasinda zaten var olan
bir secenek olarak korunuyor** (onceki raporda Hipotez 2 icin "cikis — kisa vadeli sabit bar sayisi
(orn. 1-3 bar)" zaten belirtilmisti). Backtest Muhendisi, Hipotez 2'de bu cikis secenegini ATR-bazli
TP/SL ile karsilastirirken walk-forward'i atlamamali — yani ayni hata (tek 70/30 bolmeye guvenip
walk-forward'i atlamak) Hipotez 2'de tekrarlanmayacak.

---

## 4) JUSTIN iCiN GECMIS CALISMA/CERCEVE ONERISI (TASLAK — Ertan onayina acik)

Justin'in henuz canli hesabi/kasa buyuklugu yok (CLAUDE.md: "Gelistirme — Beklemede"), bu yuzden
asagidaki hedefler **dolar-bazli degil oransal/yuzde-bazli** olarak onerilmistir. Bunlar KESIN degil,
Ertan onayi bekleyen baslangic degerleridir; canli hesap acildiginda kasa buyuklugune gore dolar-bazli
karsiliklarina cevrilebilir.

- **HEDEF_PF (oneri): >= 1,3** — PF>1 teknik olarak "kazanan" demek ama gercek-hayat duzeltmesi
  (spread/slipaj/psikoloji payi, Risk Analisti'nin KONTROL 8'i) ve canli/demo gecisindeki ek
  bozulma payi icin bir guvenlik marji gerekiyor. 1,3 esigi, hem MilaGold'un kendi operasyonel
  deneyiminde (gapli acilis/SL calismama gibi ongorulemeyen maliyetler oldugu bilindiginden — bu
  Justin'in kendi verisine dayanmiyor, sadece genel bir temkin ilkesi) hem literaturdeki genel
  scalping/kisa-vadeli sistem pratiginde makul kabul edilen bir alt sinir. Justin icin bu bir
  ONERI'dir, Ertan'in proje hedeflerine gore degistirilebilir.
- **HEDEF_WR (oneri): sabit bir yuzde yerine R:R'a bagli asgari WR formulu** — R:R orani ne olursa
  olsun, kirilma noktasi WR = 1/(1+RR). Ornegin R:R=1:1 icin asgari ~%50, R:R=1:1,5 icin asgari
  ~%40 WR gerekir (maliyet oncesi); gercek pozitif PF icin bunun bir miktar UZERINDE olmasi
  onerilir (orn. kirilma noktasindan +5-8 puan pay). Sabit bir WR hedefi (orn. "%55") yerine bu
  formul onerilmesinin sebebi: Hipotez 1'de goruldugu gibi WR ve R:R birlikte degerlendirilmeden
  tek basina WR hedefi yaniltici olabilir (WR %47-49 olsa da R:R yeterince iyiyse PF>1 olabilirdi,
  olmadi cunku R:R 1:1 sabitti).
- **HEDEF_DD (oneri): yuzde-bazli max drawdown <= %15-20 (hesap buyuklugunun)** — bu MilaGold'un
  kendi guvenlik-stopu esigiyle (gunluk %20) KARISTIRILMAMALI, o MilaGold'a ozel gunluk bir
  operasyonel esik; burada onerilen Justin icin BAGIMSIZ ve genel bir max-drawdown (toplam donem
  bazinda, gunluk degil) hedefidir. %15-20 araligi, kisa-vadeli/scalp tarzi stratejilerde yaygin
  kabul goren bir ust sinir; kesin rakam Ertan'in risk istahina gore ayarlanmali.
- **Ek oneri — istatistiksel esikler:** Risk Analisti'nin bu turda kullandigi esikler (IS n>=150
  "guclu" kategori, OOS n>=15 anlamlilik esigi, walk-forward >=6 pencere) Justin projesi icin de
  standart olarak benimsenmesi onerilir — bu esikler zaten Risk Analisti'nin sistem promptunda
  tanimli, Justin'e ozel bir degisiklik gerekmiyor, sadece bu cerceve dosyasinda ACIKCA referans
  olarak kayit altina alinmasi oneriliyor.

**Not:** Bu bolum bir TASLAKTIR. Ertan onayladiginda, bagimsiz bir dosya olarak
`C:\MilaYatirim\Justin\stratejici_justin_gecmis_calisma.md` adiyla ayristirilip (Gold projesindeki
`stratejici_gold_gecmis_calisma.md` ile ayni isimlendirme deseninde) Justin'in tum gelecek Stratejist/
Backtest/Risk turlarinin referans aldigi kalici cerceve dosyasi haline getirilmesi onerilir. O ana
kadar sonraki turlarda bu bolum, bu rapor uzerinden referans alinabilir.

---

## 5) SAAT-BAZLI FILTRE RISKI — TUM AKTIF HIPOTEZLERE UYGULANAN NOT

Risk Analisti'nin DST/saat-esleme belirsizligi (kis aylarinda MT5 sunucu saatinin GMT+3'e tam esit
olmayabilecegi, bu yuzden 15-18 gibi bantlarin fiilen kaymis olabilecegi) Hipotez 1'in RED kararini
degistirmedi (zaten PF<1'di) ama **Hipotez 2 ve gelecekteki Hipotez 3 icin gecerliligini koruyor.**
Bu, Backtest Muhendisi icin asagidaki notlarda tekrar madde olarak vurgulanmistir — her yeni hipotez
calismaya baslamadan once (parametre taramasindan ONCE) bu varsayim bagimsiz dogrulanmali, aksi
takdirde saat-bazli filtrelerin tamami (seans filtresi, gece/hafta-sonu disi tutma) yanlis pencerede
calisiyor olabilir.

---

## GUNCEL HIPOTEZ DURUMU OZETI

| Hipotez | Durum | Oncelik |
|---|---|---|
| 1 — Seans-Filtreli Ortalamaya-Donus | **KAPANDI (RED)** | — |
| 1b — N-bar-zaman-cikis varyanti | **AYRI HIPOTEZ OLARAK ELENDI**, mekanizma Hipotez 2'ye tasindi | — |
| 2 — Buyuk-Bar Ters-Yon (Fade) | **AKTIF — sirada** | 1-Yuksek (yukseltildi) |
| 3 — Rejim-Farkinda Hibrit | Degismedi, gelecek tur | 3-Dusuk |

---

## BACKTEST MUHENDiSi iCiN NOTLAR (bu tur icin guncel)

1. **Sirada olan tek hipotez: HIPOTEZ 2.** Hipotez 1 kapandi, Hipotez 3 hala erken (Hipotez 2
   sonuclarindan feature besleyecegi icin sirada degil). Bir sonraki Backtest Muhendisi turu
   dogrudan Hipotez 2 uzerine odaklanmali.
2. **Saat-esleme/DST dogrulamasi ONCE yapilmali** (madde 5, yukarida) — Hipotez 1 turunde
   Muhendis'in bunu bagimsiz dogruladigi bilgisi var, ayni titizlik Hipotez 2'de de tekrarlanmali,
   atlanmamali.
3. **Maliyet-once kontrol ZORUNLU (degismedi):** Hipotez 2'nin ham edge'i kucuk (~%1,4-2,9 puan
   sapma) — istatistiksel anlamlilik (binom/ki-kare) testi + tick-bazli spread/slipaj dahil net
   getiri simulasyonu, herhangi bir "calisiyor" degerlendirmesinden ONCE yapilmali.
4. **N-bar-zaman-cikis, Hipotez 2'nin cikis-yontemi taramasinda bir secenek olarak dahil edilsin**
   (madde 3, yukarida) — ATR-bazli TP/SL ile karsilastirilirken walk-forward ATLANMAMALI (Hipotez
   1'deki hatanin tekrari onlenmeli: tek 70/30 bolmeye guvenip pozitif sonucu guvenilir saymak).
5. **Tam islem logu bu turde bastan saglansin:** Risk Analisti'nin Hipotez 1 turunde raporladigi
   eksiklik (699 islemden yalniz 50 ornek, Monte Carlo/kar-konsantrasyonu tam hesaplanamadi) Hipotez
   2 turunde TEKRARLANMAMALI — tam islem logu (veya en azindan ozetlenmis tam dagilim istatistigi)
   bastan Risk Analisti'ne iletilecek sekilde hazirlanmali.
6. **Overfitting guvenlik agi (degismedi):** esik carpani (1,5x buyuk-bar tanimi) ve teyit ufku
   (t+1/t+2/t+3) uzerinde genis arama yapilmamali; her taramada walk-forward/OOS karsilastirmasi
   raporlanmali.
7. Sonuclar geldiginde Stratejist yine bu rapor uzerine (ayni dosya adi + tarih artimi) rafine
   edecek. Bu rapor + Hipotez 2 sonuclari, onceki turde planlandigi gibi Justin'in kalici
   "gecmis calisma/cerceve" dosyasinin (bolum 4, yukarida) cekirdegini olusturabilir.

---

## iZOLASYON NOTU

- Bu oturumda da MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (stratejici_gold_gecmis_calisma.md,
  signal.json, milagold_trades.json, lisa_performance.json, positions_status.json vb.) ACILMADI
  veya referans ALINMADI.
- Yukaridaki HEDEF_PF/WR/DD onerileri MilaGold'un kendi parametrelerinden (0,01 lot, 5$/3$/5$/8$
  SL/TP, gunluk %20 guvenlik-stopu) TUREMEDI — MilaGold'un gunluk %20 esigi acikca ayri tutuldu
  (bolum 4), Justin'in oneri degerleri bagimsiz/genel ilkelerden (R:R-WR kirilma noktasi formulu,
  genel scalping/kisa-vadeli sistem pratigi) turetildi.
- Calisma yalnizca C:\MilaYatirim\Justin\ dizininde yapildi (girdi: kendi onceki raporum +
  risk_analisti_raporu_justin_gold_scalping_hipotez1_20260710.md; cikti: bu dosya).

---

## ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik rafine adimi,
canli sisteme dokunus yok, Justin demo/arastirma asamasinda, henuz canli hesabi yok). Bolum 4'teki
"gecmis calisma/cerceve" onerisi ise ayrica ISARETLENMISTIR — bu, kalici bir dosya haline
getirilmeden once Ertan'in gozden gecirmesi/onaylamasi FAYDALI olur (HEDEF_PF/WR/DD rakamlari kesin
degil, oneri niteliginde). Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
