# JUSTIN / GOLD SCALPING — ORKESTRATOR BAGIMSIZ GORUS VE PLAN TASLAGI

Tarih: 12 Temmuz 2026 (dosya adi gorev talimatindaki tarihle uyumlu)
Olusturan: Orkestrator (bu gorev icin Fable 5'e yukseltilmis — Ertan'in acik talimati)
Gorev kaynagi: Ertan + Claude (Arayuz) ortak degerlendirmesi — justin_strateji_ailesi_
siniflandirma_20260712.md dosyasina verilen cevap uzerine bagimsiz gorus/plan istegi.
Statu: **GORUS/PLAN TASLAGI — HICBIR KARAR ICERMEZ, HICBIR AGENT TETIKLENMEMISTIR.**
Bu dosyadaki hicbir adim uygulanmamistir; Faz 1 / yeni Stratejist turu icin ayri ve acik
gorevlendirme gerekir (bkz. justin_gold_scalping_karar_ve_governance_20260714.md, Bolum 3).

Izolasyon notu: Bu dosya hazirlanirken yalniz C:\MilaYatirim\Justin\ ici dosyalar
(salt-okunur) kullanilmistir. Ertan'in mesajinda gecen "sistemdeki baska bir breakout
yaklasimi" hakkinda hicbir arastirma/sorgulama yapilmamistir (bilincli izolasyon karari);
Bolum 5'teki cevap tamamen kavramsal/metodolojiktir.

---

## 1) GENEL DEGERLENDIRME — KATILDIGIM VE NUANS EKLEDIGIM NOKTALAR

Ertan + Claude degerlendirmesinin ana hatlarina **katiliyorum**: B kapanir, A merkeze
alinir, C ve N acik kalir, J belirsiz statusunde kalir, "ML bir yontem, aile degil"
cercevesi dogru. Asagida aile aile bagimsiz gorusum ve nuanslar:

### 1.1 KAPANAN aileler — gorusum

| Aile | Ertan/Claude karari | Bagimsiz gorusum |
|---|---|---|
| **B (Ortalamaya-Donus)** | KAPANDI | **Katiliyorum.** H1/H2/H3 uc bagimsiz varyant, uc tam-pipeline RED, ayni yapisal imza (aggregate'te anlamli gorunen sinyalin tam testte PF<1'e dusmesi). Madde-7 zaten tetiklenmisti. Bu kapanis saglam kanita dayaniyor. Sayisal tutarlilik notu icin bkz. Bolum 2.1 ("5 yontem" ifadesi). |
| **D (Volatilite)** | KAPANDI | Katiliyorum — saf turleri opsiyon/varyans verisi gerektirir (kapsamda yok). **Nuans:** vol-hedefleme (vol-targeting) bir alfa ailesi degil BOYUTLANDIRMA katmanidir; D'nin kapanmasi, ileride herhangi bir stratejinin ustune vol-bazli pozisyon-boyutlandirma eklenmesini YASAKLAMAMALI. Kapanan sey "volatilitenin kendisi uzerine alfa", risk-modeli bileseni degil. |
| **E (Arbitraj)** | KAPANDI | Katiliyorum — yapisal kisit (tek enstruman), tercih degil. |
| **F (Market-Making)** | KAPANDI | Katiliyorum — retail CFD erisiminde yapisal olarak uygulanamaz. |
| **G (Mikro-yapi)** | KAPANDI (veri yok) | Katiliyorum — L2 verisi yok. **Kayit nuansi:** Tur 2 Hipotez 3 pilotu (tick-imbalance proxy, 90 gun) SONUCSUZ kaldi, RED degil. Kapanis gerekcesi "veri kisiti" olarak kayda gecmeli; o pilot ileride ne lehte ne aleyhte kanit olarak kullanilmamali. |
| **H (Olay/Takvim)** | KAPANDI (zaten filtre) | Katiliyorum, bir ayrimla: H **sinyal ailesi** olarak kapaniyor; **koruyucu filtre** rolu (olay penceresinde islem almamak) sistem duzeyinde zaten ayri bir mekanizma ve Justin'in gelecekteki her stratejisi icin gecerli kalmali. Filtre-rolu ile sinyal-rolu ayni sey degil — kapanan yalniz ikincisi. |
| **I (Sentiment)** | KAPANDI | Katiliyorum — veri kapsaminda yok. |
| **K (Carry)** | KAPANDI | Katiliyorum — forex'e ozgu deme gerekcesine ek olarak: altin tarafinda da vade-yapisi sinyali icin guvenilir vadeli-veri kaynagi dogrulanamadi (Tur 2'de USDX serisi bile supheli cikmisti). |
| **L (Capraz-Varlik)** | KAPANDI (ongoru degeri yok) | Katiliyorum, epistemik bir notla: eldeki kanit TEK olcum + SUPHELI veri kaynagi (USDX-SEP26 proxy, lead-lag ~0). Bu, "aile backtest'te RED" gucunde bir kanit degil. Kapanis yine de savunulabilir cunku asil gerekce veri-kalitesi/kapsam kisiti; ama kayitta "olculdu-elendi + veri kisiti" olarak durmali, "test edildi-calismadi" olarak degil. |
| **M (Temel/Makro)** | KAPANDI | Katiliyorum — olcek ve veri uyumsuz. |

### 1.2 ACIK aileler — gorusum

**A (Momentum/Trend-Takibi) — merkeze alinmasina katiliyorum.** Gerekceler:
1. Birincil sinyal mantigi olarak HIC denenmedi (siniflandirma dosyasi, Bolum 4).
2. B'nin uc kez ayni paternle basarisiz olmasi, A'nin calisacaginin kaniti DEGILDIR (bu
   hataya dusmemeliyiz); ama arastirma-ekonomisi acisindan hic-denenmemis en buyuk aile
   olmasi onu dogal ilk aday yapar.
3. **Kritik nuans — "A hic denenmedi" ifadesinin siniri:** Momentum BILGISI (RSI/MACD,
   HH/LL streak, 20-gun-yuksek yakinligi) ML Tur 1-2'de feature olarak girdi ve modeller
   icinde ~sifir agirlik aldi / islem uretemedi. Bu, "M15 giris + ~4 saat tutma + o feature
   setiyle klasik ML" kombinasyonuna karsi ZAYIF bir olumsuz kanittir. Yani A'yi merkeze
   alirken, ML Tur 1-2'nin kurulumunu tekrarlamak en dusuk-beklentili yol olur. A'ya
   YENI bir acidan yaklasilmali: once kural-tabanli/teori-gudumlu basit baseline, farkli
   (muhtemelen daha uzun) zaman ufku (bkz. Bolum 3, Adim 1 ve Bolum 2.3).

**C (Breakout) — acik kalmasina katiliyorum.** Momentumla akraba ama tetigi farkli
(sikismadan cikis ani). ML/RL ile "hangi seviye gercek" filtreleme fikri makul fakat
AGIR bir kurulum — once kural-tabanli baseline'in (Donchian/ORB) yasayip yasamadigi
gorulmeli, ML katmani ancak baseline kismi yasam belirtisi gosterirse eklenmelidir.
(Izolasyon sorusunun cevabi: Bolum 5.)

**N (Rejim/Adaptif) — acik kalmasina katiliyorum, SIRALAMA sartiyla.** N bir meta-ailedir:
"rejim X ise strateji-1, degilse strateji-2/bekle" secicisidir. Anahtarlayacak en az BIR
calisan taban stratejisi olmadan N tek basina test edilemez (H3 ve Tur 2 ADX olcumu bunu
zaten gosterdi: rejim etiketi buyukluk bilgisi tasidi, yon bilgisi tasimadi). Bu yuzden
N'yi "A veya C'den biri kismi yasam belirtisi gosterdikten SONRA ust-katman olarak"
planliyorum — ondan once N'ye tam tur harcamak verimsiz. Ara istisna: rejim etiketinin
buyukluk-bilgisi, A/C testlerinde FILTRE/boyutlandirma girdisi olarak dusuk maliyetle
kullanilabilir (bu N'yi "birincil olarak denemek" sayilmaz).

**J (Mevsimsellik) — "belirsiz" statusune katiliyorum.** Birincil sinyal olarak hic test
edilmedi ve testi UCUZDUR (kosulsuz takvim kurali backtest'i, ML gerektirmez). Ama
literatur bu anomalilerin zayifladigini/kaybolabildigini not eder ve tek basina S1
maliyet-orani esigini gecmesi zor. Onerim: tam pipeline turu HARCAMADAN, Arastirmaci
duzeyinde ucuz bir tarama olcumu (gun-ici saat / haftanin-gunu getiri profili, coklu-test
duzeltmesiyle); yalniz tarama guclu bir sey gosterirse hipoteze yukseltilir. Varsayilan
rolu: baska ailelerin filtresi/feature'i olarak kalmak.

### 1.3 "ML bir yontem, aile degil" — cerceve mutabakati

Katiliyorum; bu zaten siniflandirmanin kurucu ilkesiydi (Bolum 1.2). Dogru soru
"hangi aileye hangi yontem" sorusudur. Ek ilkem: **yontem merdiveni** — her ailede once
en basit/teori-gudumlu yontem (kural-tabanli), ancak o kismi sinyal gosterirse klasik ML,
RL ise en sona (bkz. Bolum 3.4). Gerekce: ML Tur 1-2'nin toplu teshisi "sorun model degil,
feature/etiket tasarimi" idi — basit baseline, atif (attribution) sorununu cozer: bir RED
geldiginde "aile mi olu, yontem mi yanlis" sorusuna cevap verebiliriz. Dogrudan ML/RL ile
baslarsak bu ikisi ayirt edilemez ve S3 "ayni patern" tespiti bulaniklasir.

---

## 2) KAYIT/SAYISAL TUTARLILIK NOTLARI (CLAUDE.md, 10 Temmuz kurali geregi)

### 2.1 "B ailesi 5 farkli yontemle test edildi" ifadesi
Benim kayitlarimda B ailesinin **tam-pipeline RED sayisi 3'tur** (H1, H2, H3 — uc bagimsiz
varyant, uc Risk Analisti karari). "5" sayisi muhtemelen su genis sayimdan geliyor olabilir:
H3'un birden fazla backtest turu (ana_test + tur2) ve/veya ML turlarindaki fade-komsu
bilesenler. Hangi tanimla sayildigi teyit edilmeden "5" sayisi baska bir kayda TASINMAMALI
(farkli-ama-kendi-icinde-gecerli sayim kurali). Sonuc her iki sayimda da ayni: B kapanir.
Ama kayitlara gecen sayi, tanimiyla birlikte gecmeli.

### 2.2 S3 sayaci (2/2) ve "ayni patern" tanimi
S3 sayaci 2/2'ye ulasti ve ben Ertan'a onay sorusunu (varsayilan oneri (b)) daha once
ilettim. Ertan'in bu mesaji o soruya fiilen su cevabi veriyor: **duz (b) degil, cerceve
degisikligi** — "ML'yi kapatalim mi" sorusu yanlis cerceve, dogru soru "ML/RL hangi
aileye uygulanacak". Bunu S3 kaydina soyle islemeyi oneririm (KARAR DEGIL, ONERI):
- ML-ailesi-sayaci (2/2) kapanir — cunku "ML ailesi" kavraminin kendisi cerceve olarak
  terk edildi.
- Yerine AILE-BAZLI sayaclar acilir (bkz. Bolum 4.1): her aile icin ayri "2 tam tur ayni
  olumsuz paternle RED → otomatik Ertan'a cikis, varsayilan (b)" gunbatimi maddesi.
- Kayit durustlugu notu: Tur 2'nin basarisizlik modu (test setinde 0 islem / MIN_SAMPLE
  alti 15 islem) ile Tur 1'in modu (AUC rassal, PF<1 imzasi) birebir ayni degildi; S3'un
  "ayni patern" tanimi genis yorumlanarak sayilmisti. Yeni aile-bazli sayaclarda patern
  tanimi BASTAN, dar ve yazili sabitlenmeli ("aggregate anlamli → tam testte sistematik
  RED" VE "islem uretememe" ayri paternler olarak mi sayilacak — Ertan'la netlestirilecek
  acik soru, Bolum 6).

### 2.3 S1 maliyet-orani ile "scalping" adinin gerilimi
Yapisal bulgu: M1'de maliyet/ATR ~%15-19 (SL'in ~%28-34'u). S1 (hedef brut kazanc >=
maliyetin 15-20 kati) bu ufukta fiilen saglanamaz. A ailesi merkeze alindiginda zaman
ufku buyuk olasilikla M15-H1+ ve tutma suresi saatler mertebesine kayar — yani alt-hedefin
adi "Gold Scalping" olsa da icerik intraday/kisa-swing'e evrilir. Bu bir sorun degil,
ama beklenti yonetimi icin acikca kaydedilmeli: **S1'i ciddiye almak, scalping ufkunu
buyuk olcude dislamak demektir.** (H sinyal-ailesi kapali olsa da olay-penceresi
koruyucu filtresi bu ufukta daha da onemli hale gelir — pozisyon tutma suresi uzadikca
duyuru pencerelerine denk gelme olasiligi artar.)

---

## 3) ONERILEN PLAN (taslak — onay ve ayri gorevlendirme gerektirir)

### Adim 0 — Ucuz on-olcumler (tam tur DEGIL, Arastirmaci-duzeyi tarama)
Tam pipeline turu harcamadan, dusuk maliyetli olcumler:
- **A-taramasi:** M15/H1/H4 ufuklarinda getiri otokorelasyonu isareti; basit MA-kesisim /
  N-bar-devam kosullu devam oranlari; S1 on-kontrolu (hangi ufukta maliyet/hedef orani
  1/15-1/20'ye iniyor — muhtemelen giris filtresi buradan cikar).
- **J-taramasi:** gun-ici saat / haftanin-gunu getiri profili, coklu-test duzeltmeli.
  Yalniz guclu sonucta hipoteze yukselir; aksi halde J feature/filtre olarak kalir.
- Amac: H1-H3'te gorulen "aggregate'te anlamli, tam testte olu" tuzagina karsi, hipotez
  kurmadan ONCE ufuk/maliyet matematigini sabitlemek. (justin_backtest_onkontrol_standardi.md
  bu adimin zorunlu girdisidir.)

### Adim 1 — A ailesi, BIRINCIL, kural-tabanli baseline (Tam Tur 1)
- Sinyal mantigi: A1 zaman-serisi momentum (orn. Donchian-yonu / MA-kesisim / N-bar getiri
  isareti — Stratejist secer, ben onceden dayatmam).
- Ufuk: Adim 0'in S1-uyumlu gosterdigi ufuk (beklenti: M15 giris, tutma saatler).
- Yontem: KURAL-TABANLI (ML degil). Gerekce: atif netligi — RED gelirse "aile mi, yontem
  mi" sorusu cevaplanabilir kalir; ML Tur 1-2'nin feature-tabanli momentum denemesi zaten
  zayif olumsuz kanit birakti, ayni kapidan girmek bilgi uretmez.
- S2 protokolu kural-tabanli testte de gecerli (walk-forward, OOS, gercekci maliyet).

### Adim 2 — Kosullu dallanma
- **A baseline kismi yasam belirtisi gosterirse** (RED ama sistematik-olumsuz degil; orn.
  bazi segmentlerde PF>1, ornek yeterli): Tam Tur 2 = A + klasik ML (feature seti A'ya
  odakli, etiket ufku Adim 0'a gore; S2 protokolu tam uygulanir). N-rejim etiketi burada
  boyutlandirma/filtre girdisi olarak eklenebilir (dusuk maliyet, N'yi birincil test etmek
  sayilmaz).
- **A baseline ayni olumsuz paternle olu cikarsa:** A'ya ikinci kural-tabanli varyant
  yerine, Tam Tur 2 = **C ailesi kural-tabanli baseline** (ORB/Donchian kirilimi, kirilim
  YONUNDE giris). Gerekce: A ve C akraba — A'nin tamamen olu ciktigi bir rejimde C'ye
  gecis, ayni bilgiyi farkli tetikle sinamak demektir; ikisi birden olu cikarsa bu, "devam
  ailesi" ust-kumesine dair guclu ortak kanit olur ve N/J degerlendirmesine gecilir.
- **C'de ML/RL "gercek seviye" filtresi:** ancak C kural-tabanli baseline'i kismi yasam
  belirtisi gosterirse (yanlis-kirilim orani yuksek ama kirilim-sonrasi hareket var ise)
  devreye alinir — tam da ML'in katki verebilecegi durum budur.

### Adim 3 — N (rejim ust-katmani)
Yalniz A veya C'den en az biri yasam belirtisi gosterdikten sonra: rejim-anahtarlamali
ust-katman (orn. trend-rejiminde A/C aktif, range-rejiminde islem yok). "Range doneminde
ML/RL ile degerlendirme" fikri (Ertan/Claude notu) bu asamada ele alinir — ama dikkat:
range-rejiminde yon stratejisi calistirmak fiilen B'ye (fade) geri donus riski tasir;
B kapali oldugundan, range-rejimi varsayilan olarak "islem yok" bolgesi olmali, aksi
ancak yeni ve acik bir Ertan karariyla degisir.

### 3.4 Yontem merdiveni (tum adimlar icin ortak ilke)
Kural-tabanli → klasik ML (S2 protokoluyle) → RL en sona. RL'in ertelenme gerekcesi:
odul-tasarimi ve overfitting riski en yuksek yontem; taban sinyal/edge kaniti olmadan RL,
"gurultuye politika ogrenmek" olur. RL ancak bir aile klasik yontemlerle edge gosterirse
"islem yonetimi/zamanlama iyilestirme" katmani olarak degerlendirilmeli.

---

## 4) GOVERNANCE ONERILERI (mevcut kurallarla uyumlu, onay gerektirir)

### 4.1 Aile-bazli gunbatimi (S3'un devami)
- Her aile icin ayri sayac: **"Ayni aile icinde 2 tam tur ayni olumsuz paternle RED →
  otomatik Ertan'a cikis, varsayilan oneri: o aileyi kapatmak."**
- "Ayni patern" tanimi bastan yazili sabitlenir (Bolum 2.2'deki acik soruyla birlikte).
- Kural-tabanli ve ML turlari AYNI aile sayacina yazilir (yontem degil aile sayilir) —
  ama patern farkliysa (orn. biri PF<1, digeri islem-uretememe) bu sayac otomatik
  tetiklenmez, yine de 2. RED'de Ertan'a bilgi notu gider.
- Gunluk pipeline dongu siniri (5/gun) bagimsiz ve paralel olarak aynen devam eder.

### 4.2 Toplam-proje gunbatimi (yeni oneri)
Aile-bazli sayaclarin ustune bir ust-esik oneririm: **A ve C aileleri de (toplamda orn.
4 tam tur) ayni-patern-RED ile kapanirsa**, alt-hedefin kendisi (Gold Scalping/intraday)
icin Ertan'a "alt-hedefi durdurma varsayilan onerisiyle" cikilir — cunku o noktada
denenebilir-ve-veri-kapsaminda-olan ailelerin tamami tuketilmis olur (kalanlar J-birincil
ve N-tek-basina; ikisi de zayif adaylar). Bu, S3'un mantiginin proje olcegine tasinmis hali.

### 4.3 Kapanis kayitlarinin epistemik etiketi
Kapanan her aile icin kapanis gerekcesi TIPIYLE kaydedilmeli: "backtest-RED" (B),
"yapisal kisit" (E, F), "veri kisiti" (D-saf, G, I, K, M), "olcum-elendi + veri suphesi"
(L), "rol-degisimi: sinyal degil filtre" (H). Boylece ileride kosullar degisirse (orn.
yeni veri kaynagi gelirse) hangi kapanisin yeniden acilabilir oldugu okunabilir kalir —
backtest-RED kapanislari kalicidir, kisit-kapanislari kosulludur.

---

## 5) C-AILESI IZOLASYON CERCEVESI (kavramsal/metodolojik cevap)

Soru: Justin'in breakout yaklasimi, sistemde var oldugu belirtilen (ismi/mekanizmasi
bilinmeyen ve BILEREK sorulmayan) baska bir breakout yaklasimindan nasil bagimsiz ve
ayirt edilebilir tutulur? Cevap, genel ilkeler duzeyinde dort katman:

1. **Veri-kaynagi katmani:** Justin'in C-yaklasiminda kullanilan HER seviye (destek/direnc,
   kanal, acilis araligi, pivot), yalniz XM/MT5 fiyat verisinden, YAZILI bir formulle,
   deterministik olarak turetilir (orn. Donchian = son N barin yuksek/dusugu; ORB = seans
   ilk X dakikasinin araligi; pivot = standart formul). Manuel cizilmis, harici analizden
   gelen veya baska bir surecten ithal edilen HICBIR seviye girdiye giremez. Turetilebilirlik
   testi: "bu seviye, Justin'in kendi fiyat gecmisi + yazili formulle yeniden hesaplanabiliyor
   mu?" — hayirsa, girdi degildir.
2. **Parametre-turetimi katmani:** Esikler (N-bar, X-dakika, teyit filtresi, k-katsayilari)
   yalniz Justin'in kendi walk-forward optimizasyonundan, S2 anti-overfitting protokolu
   icinde turetilir. Hicbir esik "hazir deger" olarak disaridan alinmaz — makul gorunse bile.
3. **Surec/dosya katmani:** Calisma dizini yalniz C:\MilaYatirim\Justin\; baska proje
   dosyasi ne veri ne SABLON/FORMAT referansi olarak acilir (14 Temmuz netlestirmesi:
   yapi/kalip kopyalama da izolasyon kapsamindadir). Agent gorev tanimlarinda diger
   yaklasim ISIMLENDIRILMEZ ve tarif edilmez; yalniz "tamamen bagimsiz/orijinal analiz"
   talimati verilir (bilgi sizdirmama kurali).
4. **Ayirt-edilebilirlik/kanit katmani (cakisma sorusuna dogrudan cevap):** Her C-hipotezi
   dosyasina bir "turetim zinciri" bolumu eklenir: kullanilan formul + parametrelerin hangi
   optimizasyon calismasindan ciktigi + veri araligi. Boylece iki yaklasim ayni piyasada
   zaman zaman AYNI sinyali uretse bile (bu kacinilmazdir ve izolasyon ihlali DEGILDIR —
   iki bagimsiz gozlemci ayni kirilimi gorebilir), koken farki belgeyle gosterilebilir.
   Ayirt etme olcutu ciktilarin farkliligi degil, **girdi ve turetim zincirinin
   bagimsizligidir**. Cakisma dogal; kopyalama ihlaldir; fark, turetim zincirinin
   yeniden-uretilebilirligiyle kanitlanir.

---

## 6) ERTAN'A ACIK SORULAR (plan onaylanmadan once netlesmesi gerekenler)

1. **S3 devami:** Bolum 4.1'deki aile-bazli sayac onerisi ve Bolum 4.2'deki toplam-proje
   ust-esigi kabul ediliyor mu? "Ayni patern" tanimina "islem-uretememe" dahil mi?
2. **"5 yontem" sayimi:** Bolum 2.1'deki tanim farki — kayitlara hangi sayim gecsin?
3. **Ufuk beklentisi:** Bolum 2.3 geregi A ailesi buyuk olasilikla scalping'den
   intraday/kisa-swing'e kayacak — alt-hedefin adi/cercevesi bu genislemeyi kapsiyor mu,
   yoksa ufuk sinirlamasi mi konulmali?
4. **Range-rejimi varsayilani:** Adim 3'teki "range = islem yok" varsayilani kabul mu?
   ("Range doneminde ML/RL" fikri B'ye ortuk geri donus riski tasidigi icin acik karar
   istiyorum.)
5. **Siralama onayi:** Adim 0 (ucuz taramalar) → Adim 1 (A kural-tabanli) sirasi ve
   Adim 2'deki kosullu dallanma kabul ediliyor mu?

Bu sorular cevaplanip Faz 1 icin ayri/acik gorevlendirme gelmeden hicbir agent
tetiklenmeyecek, hicbir sayac/kayit degistirilmeyecektir.

---

*Orkestrator — 12 Temmuz 2026. Bu dosya bir gorus/plan taslagidir; karar ve uygulama
yetkisi icermez.*
