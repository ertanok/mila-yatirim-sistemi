# STRATEJICI RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following), TUR 2 / ADIM 1

Tarih: 19 Temmuz 2026
Gorev kaynagi: Orkestrator cagrisi (19 Temmuz 09:07) — Tam Yol1 pipeline turunun Stratejici
adimidir (Arastirmaci → Stratejici → Backtest Muhendisi → Risk Analisti sirasi korunur; bir
sonraki adim Backtest Muhendisi'dir). Bu cagriyla birlikte A-ailesi gunluk tam-tur sayaci
BASLAR (Tur 2 — Tam Tur 1, 13-14 Temmuz, 3/3 RED sonuclanmisti; sayac 1/5'ten devam).

Girdi olarak kullanilan dosyalar:
- `arastirmaci_gold_scalping_A_ailesi_tur2_adim1_raporu_20260719.md` (bu turun TEK girdisi —
  M1 baseline + coklu-teyit/momentum-esikli 24-kombinasyon ham tablolari, hipotez URETMEDI)
- `justin_gecmis_calisma.md` (kasa/risk/DD cercevesi — HEDEF_PF=1,5, HEDEF_DD=%20 kumulatif,
  kasa 2.000 USD, islem-basi risk ust siniri %1, taban lot 0,01 + her 2.000 USD=+0,01 lot)
- `justin_strateji_ailesi_plani_ertan_kararlari_20260714.md` (Cevap 1 — Onceki-Turden-Ayrisma-
  Teyidi ZORUNLULUGU; Cevap 3 — scalping SL/TP korunmali, S1-vs-dar/hizli-SL/TP gerilimi;
  Cevap 4 — range rejiminde islem yok; A/C duzeltmesi — C, A'nin ICINDE kirilim-noktalarini
  degerlendirmek icin kullanilabilecek bir EK ARAC, ayri aile DEGIL)
- `stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md` (Tam Tur 1'in tam
  mekanizma tanimi — asagidaki ayrisma-teyidi bolumlerinin karsilastirma referansi)
- `risk_analisti_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260713.md` (Tam Tur 1 RED
  gerekcesi — H2'nin genis-orneklemli/tum-alt-kirilimlerde-tutarli RED'i, "dokunus+hemen-devam"
  mekanizmasinin KENDISI hakkinda en guclu negatif kanit; Tur 2 onerisi: giris tetigini
  "gecikmeli teyit, momentum-esikli kirilim, veya kanal-ici degil kanal-disi bir tetik" gibi
  farkli bir mantiga degistirmek)
- `justin_backtest_onkontrol_standardi.md` (kalici on-kontrol: DST, S1 maliyet-orani, SL/TP-
  ozel-belirleme — hicbiri otomatik tasima)

**Izolasyon notu (onemli):** `Agentlar\stratejici_gold_gecmis_calisma.md` dosyasi bu gorev icin
ACILMIS ama ICERIGI KULLANILMAMISTIR — o dosya kendi basligindaki notta acikca belirttigi gibi
aslen MilaGold/XAUUSD cercevesidir (dolar-bazli TP, 200 USD kasa vb.), Justin'e ait DEGILDIR;
Justin'in kendi kalici cercevesi `justin_gecmis_calisma.md`dir ve bu raporun TUM kasa/risk
degerleri sadece o dosyadan alinmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir sayi, format
veya sablon bu rapora TASINMAMISTIR.

---

## OTURUM OZETI

Arastirmaci bu turde HICBIR tetigi onermedi/secmedi — sadece (a) M1 giris-zamanlama baseline'ini
(1-3 ortusen kanal, cok kirilgan) ve (b) iki alternatif mekanizmayi (coklu-teyit N=2/3,
momentum-esikli k=0,5/1,0) M1/M5/M15 x H1/M30 x yon (24 kombinasyon) uzerinde ham sayilarla
sundu. Hipotez uretme sorumlulugu bu raporla yerine getiriliyor.

Ertan'in Cevap 1 geregi zorunlu kontrol uygulandi: her aday, Tam Tur 1'in "dokunus+hemen-devam"
giris-tetiginden (H1/M30 kanal filtresi + kanal cizgisine dokunus + BIR SONRAKI barin trend
yonunde kapanmasi — 3/3 RED) MEKANIZMA DUZEYINDE gercekten ayrisip ayrismadigi tek tek test
edildi. Bu test **UC adaydan birini (coklu-teyit) ELEDI** — Arastirmaci'nin kendi raporunda
acikca belirttigi gibi "orijinal tetik [coklu-teyidin] N=1 ozel-durumudur"; yani coklu-teyit,
Tam Tur 1'in AYNI formul ailesinin (ardisik bar sayisi N) bir parametre uzantisidir, YENI bir
mekanizma degildir. Bu aday hipotez OLARAK URETILMEDI, asagida acik bir soru olarak Orkestrator'a
bildiriliyor (bkz. "ELENEN ADAY" bolumu).

Geriye kalan iki tasarim, biri Arastirmaci'nin ham malzemesinden (momentum-esikli) turetilmis,
digeri (kanal-disi kirilim girisi) Arastirmaci'nin bu turde HIC olcmedigi ama Risk Analisti'nin
Tur 2 onerisinin 3. maddesiyle ("kanal-ici degil kanal-disi bir tetik") ve Ertan'in A/C
duzeltmesiyle ("C, A'nin icinde kirilim noktalarini degerlendirmek icin kullanilabilecek bir ek
arac") acikca desteklenen, tamamen Stratejici tarafindan tasarlanmis yeni bir mekanizmadir.
Asagida iki hipotez (H4, H5 — numaralandirma Tam Tur 1'in H1/H2/H3'unden AYRI tutuluyor, atif
karisikligini onlemek icin) + bir dusuk-oncelikli hibrit varyant (H6) sunuluyor.

---

## ELENEN ADAY — Coklu-Teyit Tetigi (N=2/3 Ardisik Bar) — AYRISMA TESTINI GECEMEDI

**Neden hipotez olarak URETILMEDI:** Arastirmaci'nin formul tanimi ("Dokunus bari i'den sonra,
ARDISIK N bar her biri trend yonunde kapanmali... Orijinal tetik bunun N=1 ozel-durumudur")
coklu-teyidi, Tam Tur 1'in tetigiyle AYNI temel kurala (ardisik-bar-yon-devami) baglar; degisen
tek sey N parametresidir (1→2→3). Ertan'in Cevap 1'deki kisit acik: "sadece bir parametre/ufuk
degisikligi... YETERLI SAYILMAZ." N, tam olarak boyle bir parametredir — mekanizma AYNI
(bir onceki bara gore yon-devami), sadece kac bar istendigi degisiyor. Bu nedenle coklu-teyit
mekanizma-duzeyinde gercekten ayristigini TEYIT EDEMEDIGIM icin hipotez olarak sunulmuyor.

**Orkestrator'a acik soru:** Coklu-teyit fikri tamamen terk mi edilmeli, yoksa farkli bir
tasarimla (orn. "N bar ic ice degil, N bar icinde herhangi bir ANI kirilim + geri-cekilmeme"
gibi ardisik-kapanis disi bir olcut) yeniden ele alinip mekanizma-duzeyinde ayristirilarak mi
denenmeli? Bu turde bu ikinci yol TASARLANMADI (zaman/kapsam nedeniyle iki digeri onceliklendi)
— eger Orkestrator/Ertan bu yonde bir tur daha isterse, ayri bir Stratejici gorevlendirmesiyle
ele alinabilir.

---

## HIPOTEZ H4 — "MOMENTUM-ESIKLI TEYIT" (Yon + Govde/ATR Conviction Esigi, Kanal-Ici Dokunus Korunuyor)

**YAKLASIM TURU:** Kural-tabanli.

**MANTIK:** Tam Tur 1'in tetigi (ozellikle en genis orneklemli/en net RED alan H2 varyanti,
M15-giris) YALNIZCA YON kosulu ariyordu — dokunus sonrasi bir sonraki barin, ne kadar KUCUK
olursa olsun, trend yonunde kapanmasi yeterliydi. Risk Analisti'nin H2 icin gerekcesi acikti:
"bu spesifik giris mekanizmasinin (kanal-onay + dokunus-devam girisi) bu haliyle pozitif bir
edge uretmedigi" — 12 hucrelik grid'in TAMAMI PF<1 verdi, HICBIR alt-kirilimde (tf-kaynagi, yon)
kurtarilamadi. Bu, "herhangi bir yon-devami rastgele gurultu olabilir mi" sorusunu gundeme
getiriyor. Momentum-esikli tetik, YON kosuluna EK OLARAK bir BUYUKLUK/GUC (conviction) sarti
getirerek FARKLI bir sinyali test ediyor: sadece "fiyat bir sonraki barda ayni yonde kapandi mi"
degil, "fiyat bir sonraki barda ATR-olcekli GUCLU bir itki (govde/ATR14 >= 1,0x) ile mi hareket
etti" sorusunu soruyor. Arastirmaci'nin bu turdeki bulgusu (momentum k=1,0 esigi, 24
kombinasyonun 18'inde S1 esik-gecis suresini coklu-teyide gore daha TUTARLI kisaltiyor —
en belirgin M5 H1-alcalan %33, M5 M30-yukselen %12) bu yeni sinyalin en azindan HIZ boyutunda
olculebilir/tutarli bir farklilik tasidigini gosteriyor (bu bir "calisir" iddiasi degil, sadece
test etmeye deger bir ayrisma isareti).

**MEKANIZMA-DUZEYINDE FARK (ozet):** Tam Tur 1 "yon-devami YETERLI" varsayimini test etti ve
REDDETTI (ozellikle H2). H4 "yon-devami YETERLI DEGIL, GUC/conviction de gerekli" farkli bir
varsayimi test ediyor — sinyalin ARADIGI olay TURU degisiyor (rastgele/zayif devam vs ATR-
olcekli guclu itki), bu N gibi bir sayma-parametresi degil, YENI bir olcut TURU (buyukluk).

**YONTEM DETAYI:**
- Rejim/giris-filtresi: Tam Tur 1 ile AYNI — H1 veya M30'da onaylanmis (>=3 dokunus + EMA50>
  EMA200 [yukselen] veya EMA50<EMA200 [alcalan] + MACD yon-uyumlu) aktif/kirilmamis kanal.
  (Bu filtre degismiyor cunku ayrisma testi GIRIS TETIGINI hedefliyor, rejim-filtresini degil —
  ayni zamanda Ertan'in Cevap 4'unu (range'de islem yok) zaten yapisal olarak koruyor.)
- Dokunus tanimi: AYNI — kanal cizgisi projeksiyonuna |kapanis-projeksiyon| <= 0,5xATR14(ltf).
- Teyit/tetik (DEGISEN kisim): dokunus barindan SONRAKI bar (i+1), (a) trend yonunde kapanmali
  VE (b) |kapanis[i+1]-acilis[i+1]| / ATR14(i+1) >= k. **Birincil k = 1,0x ATR14** (Arastirmaci
  bulgusundaki daha tutarli hizlanma esigi); k=0,5x, Backtest Muhendisi tarafindan bir
  DUYARLILIK/karsilastirma hucresi olarak (ayni mekanizma icinde, ayri bir hipotez degil) ek
  test edilebilir.
- LTF/HTF: **Birincil M15 giris, H1 ve M30 HTF, HER IKI yon (simetrik)** — Tam Tur 1'in en
  genis-orneklemli/en kesin-RED aldigi kombinasyonla (H2, M15-giris) DOGRUDAN karsilastirilabilir
  olmasi icin bilincli secim (ayni orneklem tabani uzerinde "mekanizma degisince sonuc degisiyor
  mu" sorusuna netlik kazandirir). **Ikincil/capraz-kontrol: M5 giris** (Arastirmaci'nin en
  belirgin hizlanma bulgusu M5'te gorulmustu, ama M5'in ortusen kanal sayisi M15'ten kucuk
  [2-8 vs 6-18] — bu nedenle M5 sonucu M15'e gore daha kirilgan kabul edilmeli). **M1 bu
  hipotezde KULLANILMIYOR** — Arastirmaci'nin M1 bulgusu 1-3 ortusen kanala dayaniyor, tum
  veri setinin en kirilgan parcasi, birincil test icin yeterli temel degil.

**GIRIS/CIKIS MEKANIZMASI:**
- Giris: yukaridaki tetik (yon + govde/ATR esigi) olustugunda, i+1 barinin kapanisinda.
- Cikis: Tam Tur 1 ile AYNI uc-kosullu cerceve (mekanizma farki giriste, cikiste degil):
  (1) SL, ATR14(ltf) bazli dar mesafe; (2) TP, bu YENI (kucultulmus) olay kumesinin kendi
  N-bar-ileri medyan hareket olcumune gore (Tam Tur 1'in TP degerleri OTOMATIK TASINMAZ — bkz.
  `justin_backtest_onkontrol_standardi.md` Madde 3); (3) kirilim-bazli erken cikis — kanal,
  pozisyon acikken kirilirsa SL/TP beklenmeden kapatilir (ayni gerekce: "onaylanmis kanal =
  guvenli devam" varsayimi Tam Tur 1'de desteklenmedi, bu risk H4 icin de gecerli kabul edilir).

**SL/TP veya RISK YONETIMI:** Dinamik, ATR14(M15, birincil) bazli + kirilim-bazli erken cikis.
Kesin katsayilar burada BELIRLENMIYOR (asiri optimize etmeme ilkesi) — Backtest Muhendisi walk-
forward asamasinda, bu YENI (daha kucuk) olay kumesi uzerinde ayrica kalibre eder. Kasa/lot/
risk cercevesi `justin_gecmis_calisma.md`den degismeden gelir (kasa 2.000 USD, islem-basi risk
ust siniri %1, taban lot 0,01 + her 2.000 USD=+0,01 lot).

**DOGRULAMA IHTIYACI:**
- Walk-forward (train/validation/test — Tam Tur 1 H1/H2'nin split metodolojisiyle tutarli,
  karsilastirilabilirlik icin).
- S1 (maliyet-orani, >=15-20x) GERCEK SL/TP mesafeleriyle yeniden hesaplanmali (Madde 2) —
  Arastirmaci'nin S1 esik-gecis sureleri proxy/ust-sinirdir, gercek SL/TP ile FARKLI cikabilir.
- DST/saat-eslesme dogrulamasi BAGIMSIZ yapilmali (Madde 1, onceki turden devralinmaz).
- **KRITIK:** momentum k=1,0 esigi olay sayisini baseline'a gore ~%87-90 azaltiyor (orn. M15
  H1-alcalan: 20.599→2.235). Bu, zaten kucuk olan bagimsiz kanal temelini (6-18) DEGISTIRMEZ
  (Arastirmaci'nin acikca belirttigi gibi ortusen kanal sayisi tetik tipinden bagimsizdir) ama
  tetik-basi olay sayisini ciddi kucultur — istatistiksel guc Tam Tur 1'e gore daha ZAYIF
  olabilir, Backtest Muhendisi bunu acikca raporlamali (n kucukse guven araligi genis
  raporlanmali, "yeterli n" varsayilmamali).
- 5-bar-gecikmeli swing-onayi (pivot tanimi ileri-bakisli, Tam Tur 1'de tespit edilen sinirlama)
  AYNEN gecerli — backtest'te dogru modellenmezse look-ahead bias.
- k=0,5 ile k=1,0 karsilastirmasi (ayni mekanizma icinde duyarlilik testi) raporlanmali.

**RISKLER:**
- **Orneklem kuculmesi (en onemli risk):** momentum esigi olay sayisini agresif sekilde
  (%87-90) azaltiyor; H4'un istatistiksel temeli Tam Tur 1'in H2'sinden (ayni kanal sayisi,
  cok daha az tetik-basi olay) daha ZAYIF olabilir — bu bir "daha az gurultu" avantaji da
  olabilir (daha secici sinyal) ama Backtest Muhendisi ikisini ayirt EDEMEZ, sadece olcer.
- Look-ahead bias (kanal/pivot tanimi degismedigi icin ayni sinirlama devam ediyor).
- **Islem frekansi/scalping-gerilimi:** M15-giris zaten Tam Tur 1'de "birkac saat" ile "gunun
  buyuk kismi" sinirinda tutma suresi tasiyordu (4,4-10,3 saat); momentum-esikli tetik daha az
  ama muhtemelen benzer-sureli islem uretir — Ertan'in Cevap 3 (scalping karakteri KESIN)
  kisitiyla gerilim Risk Analisti asamasinda AYRICA degerlendirilmeli, "cozuldu" varsayilmamali.
- Canliya gecebilirlik: govde/ATR orani hesaplamasi basit/hizli (ek gecikme riski dusuk); ana
  risk yine kanal/pivot hesaplamasinin gercek-zamanli MT5 agent icinde 5-bar-gecikmeli confirm
  mantigiyla dogru calisip calismayacagi (Tam Tur 1'den devralinan, cozulmemis sinirlama).
- Overfitting riski goreceli DUSUK: k=1,0/0,5 standart/yuvarlak esikler, Arastirmaci'nin ince
  ayar YAPMADAN test ettigi degerler; asiri ince-ayarlanmis bir parametre degil.

**ONCELIK: 1-Yuksek** — Arastirmaci'nin somut, olculmus (24 kombinasyon) bulgusuna dayaniyor;
Tam Tur 1'in en kesin RED aldigi kombinasyonla (H2/M15) dogrudan karsilastirilabilir tasarlandi
— bu, "mekanizma degisince sonuc gercekten degisiyor mu" sorusuna en temiz cevabi verecek aday.

---

## HIPOTEZ H5 — "KANAL-DISI KIRILIM GIRISI" (Dokunus-Ici-Sekme Yerine Sinir-Otesi Kirilim-Devami)

**YAKLASIM TURU:** Kural-tabanli (kirilim/momentum tetigi — Ertan'in A/C duzeltmesi geregi
"C'nin A icinde bir ek arac olarak kullanilmasi" cercevesinde, AYRI bir aile DEGIL).

**MANTIK:** Tam Tur 1'in UC varyanti da (H1/H2/H3) AYNI GEOMETRIYI paylasiyordu: fiyat kanal
cizgisine (ic sinira/destek-direnc hattina) DOKUNUR ve kanalin ICINDE kalarak trend yonunde
"sekip devam eder" (pullback-continuation / destek-direnc sekme mantigi). Risk Analisti'nin
Tur 2 onerisinin 3. maddesi acikca "kanal-ici degil kanal-disi bir tetik" oneriyordu; Ertan'in
A/C duzeltmesi de bunu destekliyor: "C (Breakout), A'nin ICINDE yer yer kullanilabilecek bir EK
ARAC — trend takip ederken kirilim noktalarini degerlendirmek icin." H5 bu yonu somutlastiriyor:
fiyatin kanal cizgisine DOKUNUP GERI SEKMESI yerine, kanalin DIS SINIRINI (trendin ilerledigi
yondeki karsi sinir — yukselen kanalda UST/direnc hatti, alcalan kanalda ALT/destek hatti)
KAPANISLA ASMASI (yapisal sinirin OTESINE ivmeli bir hareket) giris tetigidir. Bu, "trend zaten
kurulu yapinin ICINDE nefes aliyor" varsayimini degil, "trend kurulu yapiyi ASIYOR/hizlaniyor"
varsayimini test eder — TAMAMEN farkli bir piyasa-mikroyapisi hipotezidir (sekme/mean-reversion-
within-trend vs. ivme/structural-breakout), ayni formulun bir parametre varyanti DEGILDIR.

**MEKANIZMA-DUZEYINDE FARK (ozet):** (a) Geometri farkli — dokunus+ic-sekme yerine sinir-disina-
kirilim; fiyatin kanala gore KONUMU (ici vs disi) ters. (b) Zamanlama-yapisi farkli — Tam Tur 1
IKI bar gerektirir (dokunus bari + teyit bari), H5 TEK barin kapanisiyla (kirilim bari) tetiklenir
— ek bir "bir sonraki bar" beklemez. (c) Cikis mantigi da ters cevrilmis bir simetriye sahip
(asagida) — Tam Tur 1'de kanalin KIRILMASI erken-cikis nedeniyken, H5'te pozisyon zaten kirilim
UZERINE acilir, kanala GERI-DONUS erken-cikis nedenidir. Bu ucu birlikte, N-gibi bir sayma
parametresinden cok daha derin bir tasarim farkidir.

**YONTEM DETAYI:**
- Rejim/giris-filtresi: AYNI kanal-onay tanimi (>=3 dokunus + EMA50/200 + MACD teyitli, aktif/
  kirilmamis kanal, H1 veya M30 ufkunda) — bu, Ertan'in Cevap 4'unu (range'de islem yok) burada
  da yapisal olarak koruyor.
- Giris tetigi (YENI): kanalin trend-yonundeki DIS sinir projeksiyonuna (yukselen kanalda UST
  sinir, alcalan kanalda ALT sinir) bir LTF barinin kapanisi, kanalin ICINDEN DISINA, trend
  yonunde, en az 0,5xATR14(ltf) mesafede TASMALIDIR: yukselen icin `kapanis[i] - ust_sinir_
  projeksiyon[i] >= 0,5xATR14(i)`; alcalan icin ters isaret. (Esik 0,5x, Tam Tur 1'in dokunus-
  toleransiyla AYNI olcekte tutuldu — karsilastirilabilirlik icin, optimize edilmedi.)
- Yon: HER IKI yon (simetrik, yukselen kanal ust-kirilim→BUY, alcalan kanal alt-kirilim→SELL).
- LTF/HTF: **Birincil M15, H1/M30 HTF** (ayni gerekce: buyuk orneklem tabani, Tam Tur 1 H2 ile
  karsilastirilabilirlik). M5 ikincil/capraz-kontrol. M1 KULLANILMIYOR (H4 ile ayni gerekce).

**GIRIS/CIKIS MEKANIZMASI:**
- Giris: kirilim barinin KENDI kapanisinda (TEK bar tetigi — ek teyit bari beklenmez; bu,
  ivmenin ANINDA yakalanmasi gerektigi varsayimina dayanir, Backtest Muhendisi isterse bir
  "kirilim + bir sonraki barin da ayni yonde kapanmasi" varyantini duyarlilik testi olarak
  ekleyebilir, ama BIRINCIL tasarim tek-bar tetigidir).
- Cikis, Tam Tur 1'in cercevesine BENZER ama TERS-CEVRILMIS bir kirilim mantigiyla:
  (1) SL: kirilan sinirin GERISINE (kanalin ICINE dogru), orn. ~0,3-0,5xATR14 mesafede — false-
      breakout durumunda hizli cikis;
  (2) TP: ATR14 bazli dinamik hedef, bu YENI olay kumesinin kendi N-bar-ileri medyan hareket
      olcumune gore (Backtest Muhendisi'nde ayrica hesaplanacak — Arastirmaci bu turde bu olay
      TURUNU HIC OLCMEDI, bkz. Dogrulama Ihtiyaci);
  (3) **Kanala-geri-donus erken cikisi (H5'e ozel, Tam Tur 1'in "kirilim-bazli erken cikis"
      kuralinin AYNASI):** fiyat, pozisyon acikken kanalin ICINE GERI DONERSE (kirilim
      gecersizlesirse), SL/TP beklenmeden pozisyon KAPATILIR.

**SL/TP veya RISK YONETIMI:** Dinamik, ATR14(M15, birincil) bazli + kanala-geri-donus erken
cikis kurali. Kesin katsayilar BELIRLENMIYOR (Madde 3 geregi, otomatik tasima yok). Kasa/risk/
lot cercevesi `justin_gecmis_calisma.md`den degismeden gelir.

**DOGRULAMA IHTIYACI:**
- **ON-ADIM (bu mekanizma icin ozel, ZORUNLU):** Arastirmaci bu olay TURUNU (kanal-disi kirilim)
  bu turde HIC OLCMEDI — Backtest Muhendisi, tam walk-forward'a gecmeden ONCE basit bir olay-
  sayimi/S1-proxy ON-TARAMASI yapmalidir (kac kirilim olayi var, hangi HTF/LTF/yon
  kombinasyonunda kac tane, cok kucukse [orn. tek haneli] bu da H1(Tam Tur 1)'in kaderini
  paylasabilir — dar-kanit riski onceden GORULMELI, kor bir sekilde tam backtest'e girilmemeli).
- Walk-forward (train/validation/test), S1 maliyet-orani gercek SL/TP ile hesaplanmali (Madde 2).
- DST dogrulamasi BAGIMSIZ (Madde 1).
- 5-bar-gecikmeli swing-onayi (kanal/pivot tanimi degismedigi icin AYNI sinirlama) burada da
  gecerli — kirilim ANI'nin kendisi de swing-benzeri bir "confirmed mi" sorusu tasiyabilir,
  Backtest Muhendisi bu noktayi ayrica netlestirmeli (kirilim bari GERCEK-ZAMANLI olarak ANINDA
  mi tespit ediliyor, yoksa kanal cizgisinin kendisi zaten 5-bar-gecikmeli mi olusuyor — ikinci
  durumda gecikme MODELLENMELI).
- **A/C sinir netligi:** bu tetigin raporlarda/kodda daima "A ailesi ICINDE kirilim-tabanli bir
  giris varyanti" olarak adlandirilmasi, "C ailesinin canlanmasi" gibi okunmamasi icin Backtest
  Muhendisi/Risk Analisti raporlarinda ACIKCA belirtilmeli (Ertan'in A/C duzeltmesi geregi).

**RISKLER:**
- **Olcum-oncesi belirsizlik (en yuksek risk, H4'ten farkli olarak):** bu, Arastirmaci'nin ham
  sayilarla desteklemedigi, tamamen yeni tasarlanmis bir mekanizma — olay sayisi/orneklem
  buyuklugu SIFIRDAN olculecek, cok kucuk cikma riski (H1/Tam-Tur-1'in 1-8 kanalla yasadigi
  kirilganlik) bastan BILINMIYOR. On-tarama zorunlulugu bu yuzden eklendi.
- Look-ahead bias (ayni kanal/pivot sinirlama, Tam Tur 1'den devralinan).
- False-breakout riski: kirilimlarin bir kismi gecici olabilir (fiyat kanala geri doner) —
  kanala-geri-donus erken cikisi bunu kismen telafi eder ama SL'e daha sik takilma riski
  (kucuk kayip sikligi) Backtest Muhendisi tarafindan ayrica olculmeli.
- Islem frekansi: kirilim olaylari, dokunus olaylarindan (Tam Tur 1) DAHA SEYREK olabilir
  (yapisal olarak trend zaten "ilerlemis" bir noktada tetiklenir) — scalping beklenen islem
  sikligi ile gerilim riski, H4'ten de yuksek olabilir, Risk Analisti asamasinda somut
  islem/ay sayisiyla degerlendirilmeli.
- **A/C karistirma riski:** bu tetigin "C ailesinin arka kapidan geri getirilmesi" olarak
  yanlis okunma riski var (Ertan'in A/C duzeltmesindeki hassasiyet geregi) — Backtest
  Muhendisi/Risk Analisti raporlarinda A-icinde-ek-arac cercevesi acikca korunmali.
  Governance notu: Ertan'in Adim 2 icin ayirdigi acik soru ("A olu cikarsa C ayri mi denenir")
  bu hipotezle KARISTIRILMAMALI — H5, C'yi ayri bir aile olarak canlandirmiyor, A'nin kendi
  giris-tetigi tasarim uzayinin bir parcasi olarak sunuluyor.
- Canliya gecebilirlik: sinir-asma kontrolu hesapca basit (dokunus kontrolunden farksiz
  karmasiklikta); ana risk yine kanal/pivot hesaplamasinin gercek-zamanli tespiti (Tam Tur 1'den
  devralinan, cozulmemis sinirlama).
- Overfitting riski: esik (0,5xATR) Tam Tur 1'in dokunus-toleransiyla AYNI deger tutuldu (ince-
  ayarlanmadi), bu acidan dusuk; ama olay sayisi kucukse SL/TP kalibrasyonu kolayca asiri-uyuma
  kayabilir — Backtest Muhendisi'nin walk-forward disipliniyle SINIRLANMALI.

**ONCELIK: 1-Yuksek, ama ON-TARAMA SARTIYLA** — mekanizma-duzeyinde en net ayrisan aday (geometri
+ zamanlama-yapisi + cikis-mantigi UCU de ters cevrilmis), Risk Analisti'nin somut onerisi ve
Ertan'in A/C duzeltmesiyle dogrudan hizalanmis; ancak Arastirmaci tarafindan hic olculmedigi
icin "hemen tam walk-forward'a gec" ONERILMIYOR — once basit bir on-tarama (olay sayisi) ile
H1(Tam Tur 1)'in yasadigi dar-kanit riskinin burada da gecerli olup olmadigi GORULMELI.

---

## HIPOTEZ H6 (DUSUK ONCELIK, KOSULLU) — "GUCLU KIRILIM" (H4 + H5 Hibriti)

**YAKLASIM TURU:** Kural-tabanli (hibrit — iki bagimsiz mekanizmanin AYNI ANDA sart kosulmasi).

**MANTIK:** H4 (conviction/buyukluk esigi) ve H5 (kanal-disi kirilim geometrisi) birbirinden
bagimsiz iki farkli ayrisma boyutu sunuyor. Bu ikisinin AYNI ANDA gerceklestigi olaylar (kanalin
DISINA, GUCLU/ATR-esikli bir barla kirilma) teorik olarak en yuksek-conviction/en dusuk-frekans
sinyali temsil eder. Bu, Arastirmaci'nin "coklu-teyit + momentum-esikli BIRLESIMI bu turde
olculmedi" seklinde isaretledigi arastirma bosluguna BENZER bir mantikla, ama coklu-teyit yerine
H5'in kirilim-geometrisiyle kombine edilmis YENI bir onerme.

**YONTEM DETAYI / GIRIS-CIKIS:** H5'in kirilim tetigi + H4'un govde/ATR14>=1,0 esigi AYNI ANDA
sart kosulur (kirilim barinin KENDISI ayni zamanda govde/ATR>=1,0 esigini de asmali). Cikis
cercevesi H5 ile ayni (SL/TP/kanala-geri-donus erken cikisi).

**SL/TP veya RISK YONETIMI:** H5 ile ayni cerceve, kesin katsayilar Backtest Muhendisi'nde.

**DOGRULAMA IHTIYACI:** H5'in on-tarama zorunlulugu burada DAHA DA KRITIK — iki filtrenin
CARPIMSAL etkisi (H4'un tek basina %87-90 azaltmasi + H5'in kendi olay sayisi bilinmiyor) olay
sayisini cok kucuk bir sayiya (muhtemelen tek haneli/hic) dusurebilir. Bu nedenle H6, H4 ve H5
BAGIMSIZ olarak test EDILMEDEN, ya da en azindan H5'in on-taramasi tamamlanmadan
BASLATILMAMALIDIR.

**RISKLER:** **Sade-tutma ilkesiyle en dogrudan gerilim tasiyan aday** — iki YENI/dogrulanmamis
mekanizmayi ayni anda istifleme, "gorevin gerektirdiginden fazla karmasiklik" riskini tasir
(sistem promptu, "Sade Tut" ilkesi). Ayrica en yuksek olası orneklem-kuculmesi riski (H4 ve
H5'in ayri ayri risklerinin TOPLAMI). Overfitting riski en yuksek uc hipotez arasinda.

**ONCELIK: 3-Dusuk, KOSULLU** — Backtest Muhendisi'nin zamanini H4/H5'in bagimsiz sonuclarindan
ONCE bu hibride harcamasi ONERILMEZ. H4 VE H5'in ikisi de en azindan "olculebilir, tek haneli-
olmayan orneklem" seviyesinde cikarsa, H6 bir SONRAKI adim olarak (bu turun degil, muhtemelen
Tur 3'un) degerlendirilebilir. Bu turde Backtest Muhendisi'ne ONCELIKLI teslim EDILMIYOR, sadece
kayit altina aliniyor.

---

## RANGE-REJIMI NOTU (degismedi)

Ertan'in Cevap 4'u (KABUL — range rejiminde islem acilmaz) H4/H5/H6'nin UCUNE de Tam Tur 1'deki
gibi YAPISAL olarak islenmistir: her tetik, YALNIZCA onaylanmis/aktif bir kanal VARKEN devreye
girer; kanal yoksa (range/belirsiz rejim) islem yoktur. Bu turde ayrica bir degisiklik
YAPILMAMISTIR.

---

## ONCEKI-TURDEN-AYRISMA-TEYIDI (Ertan'in Cevap 1 geregi — her aday icin ayri, zorunlu)

**H4 — Momentum-Esikli Teyit:** Tam Tur 1'in giris-tetigi SADECE yon kosulu ariyordu (dokunus
sonrasi bir sonraki barin trend yonunde kapanmasi, buyukluk/guc olcusu YOKTU). H4, ayni yon
kosuluna YENI BIR OLCUT TURU (govde/ATR14 conviction esigi) ekliyor — bu bir N-sayma-parametresi
DEGIL, Tam Tur 1'in hic sormadigi bir soruyu (hareketin GUCU ne kadar) soran farkli bir kriter
sinifidir. Sadece SL/TP yeniden-kalibrasyonu veya farkli bir ufuk secimi DEGILDIR (ayni HTF/LTF
kombinasyonlari, ayni kanal filtresi kullaniliyor — degisen SADECE teyit-kriterinin TURUdur).
Teyit: GECTI.

**H5 — Kanal-Disi Kirilim Girisi:** Tam Tur 1'in UC varyanti da fiyatin kanalin ICINDE kalarak
sekmesine dayaniyordu (destek/direnc-sekme geometrisi). H5, fiyatin kanalin DISINA (yapisal
sinirin otesine) kirilmasini arar — konum (ic vs dis), zamanlama-yapisi (iki-bar vs tek-bar
tetik) ve cikis-mantigi (kirilim=cikis-nedeni vs kanala-donus=cikis-nedeni) UCU de ters
cevrilmistir. Bu, parametre/ufuk degisikligi degil, GEOMETRIK ve YAPISAL bir mekanizma
degisikligidir. Teyit: GECTI.

**H6 — Guclu Kirilim (Hibrit):** H4 ve H5'in HER IKISININ DE bagimsiz olarak ayrisma testinden
GECTIGI zaten yukarida gosterildi; H6 bunlarin BIRLESIMIDIR, dolayisiyla mekanizma-duzeyinde
ayrisma otomatik olarak GECERLIDIR (bilesenlerinin ikisi de ayri ayri gecti). Ancak H6'nin
KENDISI yeni bir "birlesim" tasarimi oldugu icin, Sade-Tut ilkesi geregi kosullu/dusuk oncelikli
tutuluyor (asiri karmasiklik riski, ayrisma-gecersizligi degil).

**Elenen aday (Coklu-Teyit):** Teyit: GECEMEDI (yukarida "ELENEN ADAY" bolumunde gerekcelendi) —
hipotez olarak URETILMEDI, acik soru olarak Orkestrator'a birakildi.

---

## BACKTEST MUHENDISI ICIN NOTLAR

1. **DST/saat-eslesme dogrulamasi (ZORUNLU, Madde 1):** onceki turden devralinmaz, H4/H5/H6'nin
   HER BIRI icin (test edilirse) bagimsiz dogrulanmali.
2. **Maliyet-orani (S1) on-kontrolu (Madde 2):** her hipotez icin GERCEK SL/TP mesafeleriyle
   ayri ayri hesaplanmali. Arastirmaci'nin bu rapordaki S1 esik-gecis sureleri proxy'dir, GERCEK
   deger degildir; orani karsilamayan varyant ana teste GECMEDEN elenmelidir.
3. **SL/TP — otomatik tasima YOK (Madde 3):** H4/H5/H6 arasinda, ve Tam Tur 1'in H1/H2/H3'unden,
   HICBIR SL/TP katsayisi otomatik tasinmaz; her biri kendi olay kumesi uzerinde ayrica kalibre
   edilmeli.
4. **H5/H6 icin ON-TARAMA ONCELIKLI:** H5 (ve onu iceren H6), Arastirmaci tarafindan hic
   olculmemis bir olay turudur — tam walk-forward'a girmeden once basit bir olay-sayimi/S1-proxy
   ON-TARAMASI yapilmali (kac kirilim olayi, hangi kombinasyonda). Cok kucuk cikarsa (H1/Tam Tur
   1'in 1-8 kanal kirilganligina benzer), bu durum Backtest Muhendisi tarafindan erken
   raporlanmali, kor bicimde tam teste devam EDILMEMELI.
5. **Look-ahead bias / 5-bar-gecikmeli swing-onayi (KRITIK, TUM adaylar icin ortak):** kanal/
   pivot tanimi Tam Tur 1'den DEGISMEDI (H1/M30 kanal formulu birebir ayni) — bu nedenle ayni
   ileri-bakis sinirlamasi (N=5 sag-pencereli fraktal pivot) tum H4/H5/H6 icin de gecerlidir;
   backtest'te 5-bar gecikme MUTLAKA modellenmelidir.
6. **Islem frekansi olcumu:** her hipotez icin gerceklesen ayda/yilda islem sayisi ayrica
   raporlanmali — H4/H5'in olay-azaltici etkisi (H4: %87-90 azalma; H5: bilinmiyor, muhtemelen
   benzer/daha fazla) canli sistemde scalping beklentisiyle (sik islem) gerilim yaratabilir; Risk
   Analisti asamasinda somut sayilarla degerlendirilmeli.
7. **A/C sinir netligi (H5/H6 icin ozel):** raporlarda bu tetiklerin "A ailesi icinde kirilim-
   tabanli bir giris varyanti" oldugu, C ailesinin ayri/bagimsiz olarak canlandirilmadigi acikca
   belirtilmeli (Ertan'in A/C duzeltmesi geregi, governance karisikligini onlemek icin).
8. **Kirilim-bazli/kanala-donus-bazli erken-cikis mantiginin dogru implementasyonu:** H4'te
   "kanal kirilirsa cik", H5/H6'da "kanala geri donulurse cik" — bu IKI FARKLI kural birbirine
   KARISTIRILMAMALI (biri Tam Tur 1'in mantigi, digeri H5'in TERS-CEVRILMIS versiyonu); backtest
   motorunda ayri ayri dogru test edilmeli.
9. **Karsilastirma cercevesi:** H4 ve H5, Tam Tur 1'in H2'siyle (M15-giris, en genis orneklem,
   en net RED) AYNI HTF/LTF/orneklem tabaninda tasarlandi — bu, "sadece mekanizma degisince
   sonuc degisiyor mu" sorusuna Risk Analisti asamasinda en temiz cevabi verecek karsilastirma
   olanagini sunar; Backtest Muhendisi raporunda bu paralelligi acikca vurgulamalidir.
10. **Oncelik sirasi (Muhendis'in zamanini israf etmemek icin):** H4 ve H5 PARALEL/es-oncelikli
    test edilebilir (H5 icin once on-tarama sarti); H6, H4 ve H5'in bagimsiz sonuclari
    ALINMADAN baslatilmamali.

---

## SINIRLAMALAR

- Bu rapor, Arastirmaci'nin raporundaki TUM sinirlamalarini (M1/M5 orneklem kirilganligi, giris-
  tetigi olaylarinin bagimsiz olmamasi, S1'in proxy niteligi, 5-bar-gecikmeli pivot, DST
  dogrulanmamasi, kucuk parent-kanal orneklemi/sag-sansur, rejim-degisikligi riski) DEVRALIR —
  bu rapor bu sinirlamalari COZMEZ, sadece onlari goz onunde bulundurarak tasarim yapar.
- Hicbir hipotez henuz backtest EDILMEMISTIR — bu rapor hipotez uretimidir, "calisir" iddiasi
  YOKTUR.
- H5/H6'nin olay sayisi/orneklem buyuklugu bu rapor yazilirken BILINMIYOR (Arastirmaci hic
  olcmedi) — bu, H4'e gore daha yuksek bir belirsizlik tasir; on-tarama zorunlulugu bu yuzden
  eklendi.
- SL/TP kesin katsayilari kasitli olarak BELIRLENMEDI (asiri optimize etmeme ilkesi) —
  Backtest Muhendisi'nin walk-forward asamasinda dolduracagi bir bosluktur.
- Coklu-teyit adayinin elenmesi KESIN bir "bu fikir hicbir sekilde islenemez" hukmu DEGILDIR —
  sadece BU turde, bu haliyle (ardisik-bar-sayisi parametresi olarak) sunulan versiyonunun
  ayrisma testini gecemedigi anlamina gelir (bkz. "ELENEN ADAY" bolumundeki acik soru).

---

## IZOLASYON NOTU

Bu rapor yalniz `C:\MilaYatirim\mila-yatirim-sistemi\Justin\` klasoru icindeki dosyalar
kullanilarak hazirlanmistir. `Agentlar\stratejici_gold_gecmis_calisma.md` ACILMIS ama ICERIGI
KULLANILMAMISTIR (yukaridaki Izolasyon Notu'nda gerekcelendirildi — o dosya MilaGold'a aittir).
MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu, deger veya format/sablon bu rapora
TASINMAMISTIR. Kullanilan sablon (HIPOTEZ ADI/YAKLASIM TURU/MANTIK/... basliklari) Stratejici
sistem promptunun kendi kalici sablonundan turetilmistir.
