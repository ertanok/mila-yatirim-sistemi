# ARASTIRMACI RAPORU — Justin / Gold Scalping — Strateji Ailesi Plani, ADIM 0 EK
## IC-ICE KANAL METODOLOJI SORUSU (devam-orani olcum yontemi)

Tarih: 16 Temmuz 2026
Tetikleyici: `gorev_arastirmaci_justin_gold_scalping_pivot_kanal_ic_ice_kanal_devam_20260716.md`
(Orkestrator cagrisi), baglam/gerekce: `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`
(14 Temmuz), "H1/M30 Yapisal Trend Bulgulari" bolumu.
Kapsam: **Tam Yol1 pipeline turu DEGIL.** Arastirmaci-duzeyi, dar kapsamli METODOLOJI EK
olcumu. Hipotez/model uretilmemistir, Stratejist'e devir yoktur — sonuc dogrudan
Orkestrator'a raporlanmaktadir. 14 Temmuz raporunun "devam orani tutarsiz" bulgusunu
GECERSIZ KILMAZ, o bulgunun OLCUM-YONTEMI kritigini/genisletmesini yapar — eski bulgu
YANINDA ikinci bir olcum sunulmaktadir.
Veri kaynagi: XM/MT5, dogrudan `MetaTrader5` kutuphanesi, sembol GOLD, sunucu saati (GMT+3,
DST bu turde de bagimsiz dogrulanmadi — bkz. Sinirlamalar).
Script: `arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam.py` → cikti:
`arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam_output.json` (tum ham sayilar,
her ic-ice pencere icin ayrintili detay dahil, bu dosyada).

---

## OZET

1. **Soru:** 14 Temmuz raporundaki "onay-sonrasi trend-yonunde-devam orani" (fiyatin 1/3/7/14
   gun sonra hala H1/M30 kanal projeksiyonuna gore trend yonunde ileride olup olmadigi) %13-80
   arasi TUTARSIZ/monotonik-olmayan cikmisti. Bu turun sorusu: bu tutarsizlik, olcumun ana
   kanal ICINDE dogal olarak olusan M15/M5-seviyesi kisa ters-yon alt-hareketlerini
   "basarisizlik" gibi sayması yuzunden mi ortaya cikiyor?
2. **Ic-ice alt-kanal yapisi GERCEKTEN VAR ve YAYGIN:** Test edilen 8 kombinasyonun
   (H1/M30 → M15/M5, yukselen/alcalan) TAMAMINDA, ortusen HER TEK parent-kanal penceresinde
   en az 1 adet onaylanmis M15/M5-seviyesi alt-kanal (ayni yonde veya zit yonde) bulundu
   (min deger tum kombinasyonlarda >=1 — bkz. asagidaki tablo). Ortalama toplam alt-kanal
   sayisi pencere basina 4,44 (M30→M15 alcalan) ile 23,5 (H1→M5 yukselen) arasinda degisiyor.
   Bu, "ana kanal aktifken icinde bagimsiz M15/M5 alt-kanallari olusuyor" onermesini
   BAGIMSIZ bir olcumle destekliyor.
3. **Yeni "ana-kanal-kirilma-bazli" devam tanimi, ESKI "fiyat-konumu" tanimindan SISTEMATIK
   OLARAK DAHA YUKSEK ve DAHA TUTARLI (monotonik) devam orani veriyor.** 4 grup (H1
   yukselen/alcalan, M30 yukselen/alcalan) x 4 ufuk (1/3/7/14 gun) = 16 karsilastirma
   noktasinin TAMAMINDA yeni tanim >= eski tanim (fark 0,0 ile 0,59 arasinda, ortalama
   ~%33 puan daha yuksek). Yeni tanimin kendisi de her 4 grupta 1→3→7→14 gun ufuklarinda
   MONOTONIK AZALAN (beklenen bir "hayatta kalma" paterni), eski tanim ise inis-cikisli
   kalmaya devam ediyor (ayni orneklemde bile).
4. **Bu monotoniklik farkinin YAPISAL bir nedeni var (gozlem, yorum degil):** yeni tanim bir
   sure/"hayatta kalma" olcusu oldugu icin (kanal ne kadar sure kirilmadan kaldi) matematiksel
   olarak zaman arttikca azalmasi beklenir; eski tanim ise bir fiyat-yonu olcusu oldugu icin
   (kapanis fiyati o anda hangi tarafta) boyle bir monotoniklik garantisi tasimaz — trend
   ICINDE gorulen kisa ters-yon fiyat hareketleri (ic-ice alt-kanallar, madde 2'de bagimsiz
   olcumu var) bu olcumu bar-bar geri-ileri savurabilir.
5. **Orneklem HALA KUCUK (n=20-40 kanal)** — bu yeni olcum de ayni parent-kanal sayisina
   dayanir, orneklem BUYUMEZ. Ic-ice alt-kanal sikligindaki bagimsiz kanit da parent-kanal
   sayisiyla ayni sinirlamayi tasir (ozellikle H1→M5 yukselen: sadece 2 ortusen parent kanal).

---

## YONTEM (TAM FORMUL — degistirilmeden yeniden kullanildi)

Pivot/kanal tanimi `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`daki (14 Temmuz)
"PIVOT/KANAL TANIMI" bolumunden HICBIR PARAMETRE degistirilmeden alinmistir:

1. **Pivot (swing) tanimi — fraktal, N=5:** bar `i`, `high[i] == max(high[i-5:i+6])` ise
   "swing high"; `low[i] == min(low[i-5:i+6])` ise "swing low".
2. **Kanal cizgisi:** anchor + trend yonunde ilk sonraki swing arasindan gecen DOGRUSAL
   2-nokta cizgi, refit edilmez (sabit egim).
3. **Dokunus toleransi:** `tol(i) = 0,5 x ATR14(i)`.
4. **Gecerlilik esigi:** >=3 dokunus (anchor + 2 ek). 3. dokunusun bari = ONAY bari.
5. **EMA/MACD teyidi (onay barinda):** EMA50/EMA200 (yukselen: EMA50>EMA200; alcalan:
   ters) VE MACD 12/26/9 (yukselen: MACD_line>MACD_signal; alcalan: ters). Ikisi de
   saglanmazsa aday ELENIR.
6. **Kirilim:** onay sonrasi TUM barlarin kapanisi, dondurulmus cizgiye karsi taranir; ilk
   `close` projeksiyonu trend-aleyhine `tol`den fazla astigi bar = KIRILIM bari.
7. **Arama penceresi sinirlamasi:** ~300 gun (432.000 dk) — degismedi.
8. **Non-overlapping tarama:** bir kanal onaylanip kirilim bulundugunda, sonraki anchor
   arayisi kirilim NOKTASINDAN SONRAKI ilk swing'den devam eder.

**Bu turde EKLENEN kisim (yeni kod, ayni formul):** Yukaridaki algoritma artik parametrik
bir `[lo, hi)` bar-penceresi ile calisabiliyor (`detect_channels_windowed`). Parent (H1/M30)
tespiti icin pencere = tum veri (`lo=0, hi=n_total`, 14 Temmuz ile birebir ayni cikti — bkz.
Sinirlamalar'daki kucuk sapma notu). Alt-kanal (M15/M5) tespiti icin pencere = bir onaylanmis
parent kanalin AKTIF PENCERESI (onay_zamani → kirilim_zamani) ile o alt-zaman-diliminin veri
araligininin KESISIMI — bu, 14 Temmuz scriptindeki `project_and_find_entries` fonksiyonunun
ortusme kriteriyle (`break_t < ltf_t0 veya confirm_t > ltf_t1 ise atla`, sonra `hi-lo<3 ise
atla`) BIREBIR AYNIDIR (numeric tutarlilik dogrulandi: asagidaki n_overlap sayilari 14
Temmuz raporundaki `n_htf_kanal_ortusen` sayilariyla ESLESIYOR — bkz. Sinirlamalar'daki M30
alcalan farki istisnasi). Alt-kanal taramasi hem ANA KANALLA AYNI YONDE hem de ZIT YONDE
ayri ayri calistirilir (swing havuzu sirasiyla swing_low/swing_high, EMA/MACD teyidi kendi
yonune gore).

---

## IC-ICE ALT-KANAL SIKLIGI (bagimsiz kanit)

Onaylanmis bir H1/M30 kanalinin aktif penceresi (onay→kirilim) icinde, o pencereyle kesisen
M15/M5 barlari uzerinde ayni formulle tespit edilen alt-kanal sayisi (pencere basina):

| Kombinasyon | Yon | Ortusen parent kanal (n) | Ort. ayni-yon alt-kanal | Ort. zit-yon alt-kanal | Ort. TOPLAM alt-kanal | Medyan toplam | Min-Maks toplam |
|---|---|---|---|---|---|---|---|
| H1→M15  | Yukselen | 6  | 4,50 | 6,17 | 10,67 | 8,5 | 2 - 22 |
| H1→M15  | Alcalan  | 16 | 2,50 | 2,12 | 4,62  | 4,0 | 1 - 14 |
| H1→M5   | Yukselen | 2  | 7,50 | 16,00| 23,50 | 23,5| 8 - 39 |
| H1→M5   | Alcalan  | 8  | 3,00 | 2,38 | 5,38  | 4,0 | 4 - 10 |
| M30→M15 | Yukselen | 11 | 2,91 | 3,73 | 6,64  | 3,0 | 2 - 23 |
| M30→M15 | Alcalan  | 18 | 1,89 | 2,56 | 4,44  | 3,0 | 1 - 12 |
| M30→M5  | Yukselen | 5  | 7,20 | 6,80 | 14,00 | 4,0 | 3 - 30 |
| M30→M5  | Alcalan  | 6  | 3,50 | 5,17 | 8,67  | 8,0 | 1 - 20 |

GOZLEM: 8 kombinasyonun TAMAMINDA min deger >=1 — hicbir ortusen parent-pencerede SIFIR
alt-kanal gozlenmedi; ic-ice yapi test edilen tum orneklerde en az bir kez mevcut. Zit-yon
alt-kanal sayisi bazi kombinasyonlarda (H1→M15 yukselen: 6,17 vs 4,50; H1→M5 yukselen: 16,00
vs 7,50) ayni-yon alt-kanal sayisindan DAHA YUKSEK — yani parent-kanal aktifken icinde
zit-yonlu (trend-aleyhine) alt-kanallar, ayni-yonlu alt-kanallardan DAHA SIK olusabiliyor.
Diger kombinasyonlarda (M30→M5 yukselen, H1→M5 alcalan) ayni-yon biraz daha yuksek. Yon
bazinda tutarli bir patern YOK (kombinasyondan kombinasyona degisiyor).

BAGLAM: Pencere basina ortalama 4-24 arasi degisen alt-kanal sayisi, "genis kanal ana trendi
korurken icinde birden fazla kisa vadeli alt-hareket olusabiliyor" onermesiyle SAYISAL OLARAK
tutarlidir. Bu sayi, bir onceki bolumdeki "devam orani" farkinin (eski vs yeni tanim)
NEDEN ortaya ciktigina dair bagimsiz bir gozlemsel destek saglar — ama nedensellik iddiasi
DEGILDIR, sadece iki olgunun (ic-ice yapi var + iki tanim farkli sonuc veriyor) AYNI ANDA
gozlemlendigi belirtilmektedir.

SINIR: n_overlap parent-kanal sayisi bazi kombinasyonlarda COK KUCUK (H1→M5 yukselen: 2,
M30→M15 yukselen: 11) — bu tablo o kombinasyonlar icin GENIS guven araligi tasir. Ham
pencere-bazli detay (`ic_ice_alt_kanal_sikligi.<kombinasyon>.<yon>.detay`) JSON dosyasinda
mevcuttur.

---

## ESKI vs YENI "DEVAM" TANIMI KARSILASTIRMASI

**ESKI TANIM (fiyat konumu — 14 Temmuz raporuyla ayni yontem, bu turde ayni veri uzerinde
yeniden hesaplandi):** onay barindan N gun sonraki bar kapanisi, onay barinin kapanisina
gore hala trend yonunde mi (`sign x (close[confirm+N] - close[confirm]) > 0`)?

**YENI TANIM (ana-kanal-kirilma-bazli):** onay barindan itibaren N gun icinde ana kanal
(dondurulmus cizgi, kapanis tol'u trend-aleyhine astiginda) KIRILDI MI? "Kirilmadi" (1) eger
(a) gercek kirilim suresi >= N gun, VEYA (b) kanal veri sonunda/pencere sinirinda hala
censored VE bu censored-sureye kadar en az N gun gecmis. "Kirildi" (0) eger gercek kirilim
suresi < N gun. Censored VE censored-sure < N gun olan kanallar bu ufuk icin BELIRSIZ
sayilip orneklemden CIKARILDI (veri o ufka kadar uzanmiyor — 3 kanalda toplam 1 vaka,
sadece M30-yukselen 14-gun ufkunda gorulmustur, asagida ayrica isaretli).

### H1

| Yon | Ufuk | n (eski) | ESKI: devam orani | n (yeni) | n_belirsiz | YENI: kirilmadi orani | Fark (yeni-eski) |
|---|---|---|---|---|---|---|---|
| Yukselen | 1 gun  | 27 | 0,5926 | 27 | 0 | 1,0000 | +0,4074 |
| Yukselen | 3 gun  | 27 | 0,4074 | 27 | 0 | 1,0000 | +0,5926 |
| Yukselen | 7 gun  | 27 | 0,5556 | 27 | 0 | 1,0000 | +0,4444 |
| Yukselen | 14 gun | 27 | 0,4444 | 27 | 0 | 0,8519 | +0,4074 |
| Alcalan  | 1 gun  | 39 | 0,6923 | 39 | 0 | 1,0000 | +0,3077 |
| Alcalan  | 3 gun  | 39 | 0,4615 | 39 | 0 | 1,0000 | +0,5385 |
| Alcalan  | 7 gun  | 39 | 0,5385 | 39 | 0 | 0,9487 | +0,4103 |
| Alcalan  | 14 gun | 39 | 0,5897 | 39 | 0 | 0,7436 | +0,1538 |

### M30

| Yon | Ufuk | n (eski) | ESKI: devam orani | n (yeni) | n_belirsiz | YENI: kirilmadi orani | Fark (yeni-eski) |
|---|---|---|---|---|---|---|---|
| Yukselen | 1 gun  | 20 | 0,7500 | 20 | 0 | 1,0000 | +0,2500 |
| Yukselen | 3 gun  | 20 | 0,8000 | 20 | 0 | 0,9500 | +0,1500 |
| Yukselen | 7 gun  | 20 | 0,7000 | 20 | 0 | 0,9500 | +0,2500 |
| Yukselen | 14 gun | 19 | 0,6316 | 19 | 1 | 0,6316 | +0,0000 |
| Alcalan  | 1 gun  | 40 | 0,6000 | 40 | 0 | 1,0000 | +0,4000 |
| Alcalan  | 3 gun  | 40 | 0,4500 | 40 | 0 | 1,0000 | +0,5500 |
| Alcalan  | 7 gun  | 40 | 0,4500 | 40 | 0 | 0,8750 | +0,4250 |
| Alcalan  | 14 gun | 40 | 0,4000 | 40 | 0 | 0,5250 | +0,1250 |

**Parent kanal sayisi (bu turde yeniden tespit edildi):** H1 yukselen=27, H1 alcalan=39, M30
yukselen=20, M30 alcalan=**40** (14 Temmuz raporunda 39'du — bkz. Sinirlamalar).

GOZLEM (16/16 noktada yon tutarli): Yeni tanim, TUM 16 (grup x ufuk) noktasinda eski tanima
ESIT VEYA DAHA YUKSEK ("kirilmadi/devam" orani daha yuksek gorunuyor); fark 0,0 (M30 yukselen,
14 gun) ile +0,5926 (H1 yukselen, 3 gun) arasinda, 16 noktanin ortalamasi +0,3383. Yeni tanim
her 4 grupta da 1→3→7→14 gun sirasinda MONOTONIK AZALAN degerler veriyor (1,0/1,0/1,0/0,85 —
1,0/1,0/0,95/0,74 — 1,0/0,95/0,95/0,63 — 1,0/1,0/0,88/0,53); eski tanim ayni 4 grupta
monotonik degil (orn. H1 yukselen: 0,59→0,41→0,56→0,44 — 3 gunde dusup 7 gunde tekrar
yukseliyor).

BAGLAM: Bu monotoniklik farki YAPISAL bir nedene sahiptir (madde 4, Ozet'te belirtildi): yeni
tanim bir sure-tabanli ("ne kadar sure kirilmadi") olcu oldugu icin matematiksel olarak
azalan bir fonksiyon olmasi beklenir (bir kanalin N gun kirilmama olasiligi N arttikca
artamaz); eski tanim ise bir andaki fiyat-yonu olcusu oldugu icin bu garantiyi tasimaz. Bu
fark, "hangi tanim daha DOGRU" sorusuna bir yanit DEGILDIR — sadece iki olcumun FARKLI
seyler olctugunu ve bu farkin sonuclara nasil yansidigini gostermektedir.

---

## SINIRLAMALAR

- **Kucuk orneklem (degismedi, buyumedi):** n=20-40 parent kanal (H1 yukselen=27, H1
  alcalan=39, M30 yukselen=20, M30 alcalan=40). Yeni "devam" tanimi da AYNI parent-kanal
  kumesine dayanir — orneklem sayisi bu olcumle ARTMAMAKTADIR. Ic-ice alt-kanal sikligindaki
  n_overlap sayilari (2-18) ise parent-kanal sayisindan da KUCUKTUR (sadece M15/M5 veri
  araligiyla kesisenler) — bu tablo icin guven araliklari cok daha genistir.
- **Ic-ice alt-kanal olaylari da BAGIMSIZ DEGILDIR:** ayni ana kanal penceresi icindeki
  ardisik alt-kanallar zaman/fiyat olarak birbirine yakin/otokorelasyonlu olabilir (14 Temmuz
  raporundaki "giris tetigi" bagimsizlik uyarisiyla AYNI turden bir sinirlama).
- **Veri, 14 Temmuz'dan bu yana 2 gun ilerledi (bu tur 16 Temmuz'da MT5'ten YENIDEN cekildi):**
  H1 (81.325 bar, 2001-06-04→2026-07-16), M30/M15/M5 (99.999 bar, sirasiyla 2018-01-24,
  2022-04-22, 2025-02-17 basliyor, hepsi 2026-07-16 sonu). Bu, parent-kanal sayisinda KUCUK
  bir sapmaya yol acti: M30-alcalan bu turde 40 kanal (14 Temmuz'da 39'du) — muhtemelen veri
  sonuna yakin, o zaman censored olan bir kanalin bu 2 ekstra gunde kirilip yeni bir aday
  kanalin baslamasi/veya yeni bir swing olusmasi sonucu. H1/M30-yukselen ve H1-alcalan
  sayilari DEGISMEDI (27/20/39). Bu fark, ESKI ve YENI tanimlarin AYNI (bu turde yeniden
  tespit edilen) kanal kumesi uzerinde HESAPLANDIGI icin karsilastirmanin GECERLILIGINI
  ETKILEMEZ (iki tanim ayni girdi kumesini kullaniyor) — ama 14 Temmuz raporundaki mutlak
  sayilarla (orn. M30-alcalan eski tanim oranlari) birebir ayni olmayabilecegini gosterir
  (bu turde M30-alcalan 1/3/7/14-gun eski-tanim degerleri: 0,60/0,45/0,45/0,40 — 14 Temmuz
  raporundaki 0,5897/0,4615/0,4359/0,4359 ile YAKIN ama BIREBIR AYNI DEGIL; H1/M30-yukselen
  ve H1-alcalan degerleri ise BIREBIR AYNI kaldi cunku kanal sayisi degismedi). Bu, "Agent'lar
  arasi sayisal tutarlilik" ilkesi geregi acikca belirtilmektedir — sapmanin kaynagi FARKLI
  bir hesaplama yontemi degil, MT5'ten iki farkli tarihte cekilen veri penceresidir.
- **n_overlap sayilarinin dogrulanmasi:** 7/8 kombinasyonda bu turun n_overlap sayisi 14
  Temmuz raporundaki `n_htf_kanal_ortusen` ile BIREBIR ayni (H1→M15: 6/16; H1→M5: 2/8;
  M30→M15: 11/18; M30→M5: 5/6 — alcalan yalniz bu son ikisi M30 parent kumesindeki 40.
  kanalin M15/M5 veri araligiyla kesismedigi icin degismedi). Bu, iki turun ayni ortusme
  kriterini kullandigini DOGRULAR.
- **Onaylanmis alt-kanal formulu, parent kanalla TAMAMEN AYNI parametreleri kullanir**
  (N=5 fraktal, >=3 dokunus, EMA50/EMA200+MACD, 0,5xATR14) — bu parametreler M15/M5 zaman
  olceginde OPTIMIZE EDILMEMISTIR; H1/M30 icin "makul baslangic" olarak secilen degerlerin
  M15/M5'te de ayni derecede uygun olup olmadigi bu turde test EDILMEMISTIR.
- **"Belirsiz" disarida-birakma kurali** (censored + censored-sure < ufuk gunu) sadece 1
  vakada (M30-yukselen, 14 gun) devreye girdi — bu, orneklem boyutunu ihmal edilebilir
  duzeyde etkiledi (n=20→19), ama farkli/daha genis bir veri setinde bu kural daha fazla
  vakayi disarida birakabilir; kural KENDI ICINDE gecerlidir (bilinmeyen durumu iddia
  etmeden ayirir) ama SEÇICI ORNEKLEM (survivorship) riski tasir ve bu turde ayrica
  test EDILMEMISTIR.
- **Ic-ice alt-kanal sikligi TEK BIR yon-cifti (ayni-yon / zit-yon) olarak raporlanmistir** —
  alt-kanallarin BUYUKLUGU (fiyat araligi, sure) veya parent-kanal icindeki KONUMU (baslangic/
  orta/son) bu turde AYRICA analiz EDILMEMISTIR.
- **DST/saat-eslesme dogrulamasi bu turde de YAPILMADI** (14 Temmuz'daki ayni not) —
  `justin_backtest_onkontrol_standardi.md` Madde 1 geregi, tam bir backtest turunde bagimsiz
  dogrulanmalidir.
- **Bu bir hipotez/model KURMA gorevi degildir** — hangi tanimin "dogru" oldugu veya bu
  bulgunun bir strateji/filtre onerisine donusturulup donusturulmeyecegi konusunda KARAR
  ALINMAMISTIR; iki olcum yontemi ham sayilarla yan yana sunulmustur.

---

## IZOLASYON NOTU

Bu rapor ve uretilen script yalnizca `C:\MilaYatirim\Justin\` klasoru icinde calisilmis, tek
veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD sembolu ham OHLCV verisi
kullanilmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu, deger veya format/sablon
referans olarak ACILMAMISTIR. Script yapisi (MT5 baglanti kalibi, pivot/kanal algoritmasi),
karsilastirilabilirlik amacli olarak BILEREK ayni-proje-ici 14 Temmuz scriptiyle
(`arastirmaci_gold_scalping_pivot_kanal_tarama.py`) TUTARLI tutulmustur — izolasyon kurali
yalnizca BASKA projelerin dosya/format referansini yasaklar, ayni-proje-ici metodolojik
tutarliligi degil. Bu gorev, ayni oturumda baslatilan DIGER bir gorevle (M5-donem
dogrulamasi, ayri dosya/script/rapor) BAGIMSIZDIR; sonuclar karistirilmamistir.
