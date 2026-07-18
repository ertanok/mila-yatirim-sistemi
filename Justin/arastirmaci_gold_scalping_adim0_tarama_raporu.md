# ARASTIRMACI RAPORU — Justin / Gold Scalping — Strateji Ailesi Plani, ADIM 0 (ON-TARAMA)

Tarih: 14 Temmuz 2026
Kapsam: **Tam Yol1 pipeline turu DEGIL.** Arastirmaci-duzeyi, dar kapsamli iki parcali
on-tarama (A-Taramasi + J-Taramasi). Hipotez/model uretilmemistir, Stratejist'e devir
yoktur — sonuc dogrudan Orkestrator'a raporlanmaktadir.
Veri kaynagi: XM/MT5, dogrudan `MetaTrader5` kutuphanesi, sembol GOLD, sunucu saati
(GMT+3, DST bu turde bagimsiz dogrulanmadi — bkz. Sinirlamalar).
Script: `arastirmaci_gold_scalping_adim0_tarama.py` → cikti: `arastirmaci_gold_scalping_
adim0_tarama_output.json` (tum ham sayilar orada).

---

## OZET

1. **Veri araligi TF'ler arasinda ESIT DEGIL** (MT5 terminal `maxbars=100000` siniri):
   M15 sadece 2022-04-18 → 2026-07-13 (~4,25 yil, 99.999 bar); H1 ve H4 ise 2001-06-04 →
   2026-07-13 (~25 yil, sirasiyla 81.236 ve 23.434 bar). Bu asimetri asagidaki tum
   karsilastirmalarin bir sinirlamasi olarak okunmalidir (bkz. Sinirlamalar).
2. **Otokorelasyon/varyans-orani/N-bar-devam-orani bulgularinin agirligi "surekliligi"
   degil, hafif ve kisa-vadeli TERSINE-DONUS (mean-reversion benzeri) isareti gosteriyor**
   — ozellikle M15 ve H1'de VR(q)<1 (istatistiksel anlamli, q=4,8,16) ve N-bar-streak
   sonrasi "ayni yon" oranlari cogunlukla %50 null-orninin ALTINDA (~%45-50). Bu, "A
   (Momentum) ailesi" varsayimiyla dogrudan uyumlu bir on-isaret DEGILDIR — sadece
   gozlemdir, karar degildir.
3. **S1 on-kontrolu (maliyet/hedef >= 15-20x):** Her uc ufukta da esik, YALNIZCA
   N-bar-ileri gerceklesen hareketin **birkac saat ila ~1-2 gun** mertebesindeki tutma
   sureleriyle asiliyor (M15: ~5,3-8,3 saat; H1: ~15,8-25,9 saat; H4: ~24,6-40,8 saat —
   interpolasyonla, asagida detay).
4. **CELISKI BULGUSU (zorunlu bolum, asagida detayli):** S1'i saglayan EN IYI/EN KISA
   ufuk-parametre bolgesi (M15, ~5-8 saat tutma) dahi, Ertan'in "dakikalar-birkac-saat
   mertebesinde tutma, gun/hafta mertebesinde DEGIL" tanimiyla GERGIN/sinirda bir bolgede
   duruyor — 5-8 saat "birkac saat" ile "gunun buyuk kismi" arasinda bir sinirda. Bu bir
   karar degil, acik bir bulgu olarak isaretleniyor.
5. **J-Taramasi'nda iki bulgu, Bonferroni duzeltmesi SONRASI da anlamli kaliyor:**
   (a) sunucu saati 01:00 civari (rollover/dusuk-likidite penceresi) belirgin pozitif
   ortalama getiri, (b) Cuma gunu belirgin pozitif ortalama getiri. Ikisi de guclu ve
   duzeltme-sonrasi anlamli — "hipoteze yukseltilebilir" olarak isaretleniyor (ama J'nin
   Adim 0 kapsaminda ayri bir pipeline turu ONERILMIYOR, sadece bulgu raporlaniyor).

---

## A-TARAMASI BULGULARI

### A.0 — Veri Araligi (kaynak: script cikisi)

| Ufuk | Bar sayisi | Baslangic (sunucu saati) | Bitis (sunucu saati) |
|---|---|---|---|
| M15 | 99.999 | 2022-04-18 06:30 | 2026-07-13 03:30 |
| H1  | 81.236 | 2001-06-04 01:00 | 2026-07-13 03:00 |
| H4  | 23.434 | 2001-06-04 00:00 | 2026-07-13 00:00 |

BAGLAM: M15 verisi MT5 `copy_rates_from_pos` + terminal `maxbars=100000` sinirindan
dolayi yalnizca son ~4,25 yili kapsiyor; H1/H4 ayni sinira ragmen daha genis takvim
araligina yayiliyor (bar sayisi/zaman orani daha dusuk oldugu icin). Uc ufuk FARKLI
donemleri temsil ediyor — dogrudan "hangi ufuk daha iyi" karsilastirmasi bu asimetriyi
tasir (bkz. Sinirlamalar).

### A.1 — Otokorelasyon (log-getiri, lag 1-10)

Yontem: `corrcoef(r_t, r_{t+lag})`, yaklasik SE = 1/sqrt(n), |z|>1,96 = "anlamli" (basit
2-sigma isareti, coklu-test duzeltmesi UYGULANMADI — bu A-taramasinin bir parcasi,
J-taramasindaki duzeltme kurali burada gecerli degil, gorev tanimi geregi yalniz basit
isaret araniyor).

| Ufuk | Anlamli (|z|>1,96) lag'lar ve katsayilar |
|---|---|
| M15 | lag3: -0,0131 (z=-4,16); lag4: -0,0142 (z=-4,49); lag5: +0,0065 (z=2,05); lag6: -0,0064 (z=-2,02) |
| H1  | lag1: -0,0110 (z=-3,13); lag4: +0,0090 (z=2,57); **lag6: -0,0293 (z=-8,35, en guclu tekil isaret)**; lag7: -0,0078 (z=-2,21); lag8: +0,0092 (z=2,62) |
| H4  | **lag6: -0,0357 (z=-5,46, en guclu tekil isaret)**; lag7: -0,0131 (z=-2,01) |

BAGLAM: Katsayi buyuklukleri cok kucuk (mutlak deger ~0,006-0,036). n≈23.000-100.000
oldugu icin bu kucuk katsayilar bile |z|>1,96 esigini asabiliyor — bu, istatistiksel
anlamliligin katsayi buyuklugunden ayri okunmasi gerektigine dair bir olcum notudur.
Not: lag-6 negatif otokorelasyon hem H1 hem H4'te en guclu tekil isaret olarak
tekrarlaniyor (H1'de 6 saat, H4'te 24 saat = 1 gun dongusune denk geliyor) — bu bir
gozlemdir, donguselligin kaynagi/nedeni bu turde arastirilmamistir.

### A.2 — Varyans-Orani (basit, non-overlapping blok, Lo-MacKinlay homoskedastik SE)

VR(q) = Var(q-bar toplam getiri) / (q x Var(1-bar getiri)). VR<1 → kisa-vadeli
tersine-donus isareti; VR>1 → surekliligi/trend isareti; VR≈1 → rastgele-yuruyus-benzeri.

| Ufuk | q=2 | q=4 | q=8 | q=16 |
|---|---|---|---|---|
| M15 | 0,9981 (z=-0,61) | **0,9419 (z=-9,82)** | **0,9450 (z=-5,88)** | **0,9597 (z=-2,90)** |
| H1  | **0,9888 (z=-3,20)** | **0,9849 (z=-2,30)** | 0,9885 (z=-1,10) | **0,9601 (z=-2,59)** |
| H4  | 0,9947 (z=-0,81) | 0,9962 (z=-0,31) | 1,0196 (z=1,01) | 0,9804 (z=-0,68) |

(Koyu = |z|>1,96 anlamli.)

BAGLAM: M15'te q=4,8,16'da, H1'de q=2,4,16'da anlamli VR<1 (tersine-donus isareti).
H4'te hicbir q'da anlamli sapma yok (n_blocks daha kucuk oldugu icin istatistiksel guc
de daha dusuk — bu bir olcum sinirlamasidir, "H4'te etki yok" sonucuna esit degildir).

### A.3 — N-Bar-Devam Orani (streak sonrasi, "kapanis yonu" tanimi: close vs open)

Baseline: bagimsizlik-altinda beklenen "ayni yon" orani = p_up^2+(1-p_up)^2 (p_up =
empirik yukari-kapanan bar orani). Her ufukta p_up ≈ %50,7-51,9 → null ≈ %50,0-50,1.

| Ufuk | Streak uzunlugu | Olay sayisi | Sonraki 1 bar ayni yon | Sonraki 2 bar | Sonraki 3 bar |
|---|---|---|---|---|---|
| M15 | 2 | 25.046 | 0,4892 | 0,4878 | 0,4984 |
| M15 | 3 | 12.252 | 0,4691 | 0,5031 | 0,4967 |
| M15 | 4 | 5.747  | 0,4956 | 0,5008 | 0,4913 |
| M15 | 5 | 2.848  | 0,4786 | 0,4863 | 0,4940 |
| M15 | 8 | 307    | 0,4821 | 0,4528 | 0,5309 |
| H1  | 2 | 20.489 | 0,4772 | 0,4936 | 0,5040 |
| H1  | 3 | 9.778  | 0,4730 | 0,4936 | 0,5016 |
| H1  | 4 | 4.625  | 0,4724 | 0,5001 | 0,4938 |
| H1  | 5 | 2.185  | 0,4746 | 0,4892 | 0,5002 |
| H1  | 8 | 219    | 0,4475 | 0,5068 | 0,4749 |
| H4  | 2 | 5.931  | 0,4885 | 0,4932 | 0,4904 |
| H4  | 3 | 2.897  | 0,4926 | 0,4769 | 0,4817 |
| H4  | 4 | 1.427  | 0,4569 | 0,4744 | 0,5053 |
| H4  | 5 | 652    | 0,4632 | 0,5015 | 0,4893 |
| H4  | 8 | 71     | 0,5493 | 0,4507 | 0,5211 |

BAGLAM: Neredeyse tum hucrelerde "sonraki 1 bar ayni yon" orani null-degerin (~0,50)
ALTINDA (~0,45-0,49) — yani N-bar ayni-yonlu kapanis sonrasi bir sonraki tek bar,
istatistiksel bagimsizlik varsayimindan BEKLENENDEN DAHA AZ ayni yonde kapaniyor.
Streak=8 hucreleri kucuk orneklem (n=71-307), yorumda temkin gerektirir.

### A.4 — MA-Durum Ileri Dogruluk (SMA10/SMA30 durumu, ileri N bar)

"Bull durum" = SMA10>SMA30; ileri N bar sonra fiyat yukarida mi (dogruluk), "bear durum"
icin asagida mi. Kosulsuz karsilastirma = tum ornekte ileri-yukari orani.

| Ufuk | Ileri N | Bull durum n | Bull→yukari orani | Bear durum n | Bear→asagi orani | Kosulsuz yukari orani |
|---|---|---|---|---|---|---|
| M15 | 1 | 52.089 | 0,5052 | 47.878 | 0,4911 | 0,5056 |
| M15 | 8 | 52.089 | 0,5166 | 47.871 | 0,4837 | 0,5159 |
| H1  | 1 | 42.355 | 0,5014 | 38.851 | 0,4866 | 0,5058 |
| H1  | 8 | 42.355 | 0,5077 | 38.844 | 0,4768 | 0,5148 |
| H4  | 1 | 12.550 | 0,5205 | 10.854 | 0,4907 | 0,5148 |
| H4  | 8 | 12.550 | 0,5328 | 10.847 | 0,4717 | 0,5306 |

(Tam N=1,2,4,8 tablosu JSON ciktisinda.)

BAGLAM: Bull-durum ileri-yukari orani, kosulsuz orana yakin veya hafif altinda (M15/H1);
H4'te bull-durum kosulsuza gore hafif ustunde (orn. N=8: 0,5328 vs 0,5306 — fark ~0,002).
Bear-durum ileri-asagi orani TUM ufuklarda ve tum N'lerde 0,50'nin belirgin ALTINDA
(0,47-0,49) — yani "bear MA durumunda" asagi devam, yukari devamdan daha az goruluyor
degil, asil goze carpan bear-durumun kendisinin asagi-devam orani dusuk (hafif ters
sinyal). Bu asimetri (bull tarafi ~notr, bear tarafi sistematik dusuk) A.3 ve A.5'teki
asagi-yonlu zayifligina paralel.

### A.5 — Kirilim (Donchian, N=20) Notu — C'nin A icindeki katkisi (ayri hipotez DEGIL)

| Ufuk | Ileri N | Yukari kirilim n | Yukari devam orani | Asagi kirilim n | Asagi devam orani |
|---|---|---|---|---|---|
| M15 | 1 | 6.205 | 0,4833 | 4.782 | 0,4410 |
| M15 | 4 | 6.205 | 0,4936 | 4.782 | 0,4534 |
| H1  | 1 | 4.608 | 0,4844 | 3.478 | 0,4477 |
| H1  | 4 | 4.608 | 0,5022 | 3.478 | 0,4592 |
| H4  | 1 | 1.610 | 0,5311 | 1.039 | 0,4408 |
| H4  | 4 | 1.610 | 0,5466 | 1.039 | 0,4475 |

BAGLAM (gozlemsel not, C alt-bileseni): Yukari kirilim devam orani ufuklar arasinda
degisken (0,48-0,55, H4'te en yuksek); asagi kirilim devam orani TUM ufuklarda ve tum
ileri-N'lerde belirgin dusuk (0,44-0,46) — yani asagi-yonlu kirilimlar, yukari-yonlu
kirilimlara gore daha az "devam ediyor" (daha reversal-egilimli). Bu asimetri, A.4'teki
bear-durum bulgusuyla ayni yonde (asagi-yonlu sinyallerin surekliligi, yukari-yonluye
gore daha zayif). MA-kesisim-tipi (A.4) devam oranlariyla kaba karsilastirma: kirilim-tipi
giris (Donchian) ile MA-durum-tipi giris arasinda buyuk/sistematik bir fark
gozlenmiyor — ikisi de benzer yon-asimetrisini tasiyor.

### A.6 — S1 Maliyet On-Kontrolu (zorunlu)

Yontem: cost_pts = spread_median_pts + slippage_tahmini (ATR14_median x 0,037 — S1
standardinin kendi kalibrasyon notu, Justin'in H2 kesitinden). hedef_pts = N-bar-ileri
|kapanis farki| medyani (gercek, olculmus deger — varsayimsal ATR-carpani DEGIL).
oran = hedef_pts / cost_pts.

| Ufuk | Spread medyan (pts) | ATR14 medyan (pts) | Maliyet toplam (pts) | Maliyet/ATR% |
|---|---|---|---|---|
| M15 | 27,0 | 287,5 | 37,64 | %13,09 |
| H1  | 30,0 | 382,5 | 44,15 | %11,54 |
| H4  | 27,0 | 797,36 | 56,50 | %7,09 |

Ufuk tablosu (N bar ileri, gercek sure, oran=hedef-medyan/maliyet):

| Ufuk | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 |
|---|---|---|---|---|---|---|
| M15 (dk) | 15dk: 2,95 | 30dk: 4,17 | 60dk: 5,98 | 120dk: 8,61 | 240dk: 12,75 | 480dk: **19,50** |
| H1 (dk)  | 60dk: 3,01 | 120dk: 4,37 | 240dk: 6,52 | 480dk: 9,81 | 960dk: **15,17** | 1920dk: **22,97** |
| H4 (dk)  | 240dk: 5,04 | 480dk: 7,59 | 960dk: 11,79 | 1920dk: **17,78** | 3840dk: **25,88** | 7680dk: 37,49 |

(Koyu = 15x esigini asan ilk olculen nokta.)

**S1 esigine (15x / 20x) ulasan interpolasyonlu tutma-suresi (komsu iki olculen nokta
arasinda dogrusal interpolasyon — bu bir OLCUM DEGIL, iki olculen nokta arasi TAHMINDIR,
ayrica belirtilir):**

| Ufuk | 15x esigi (~saat) | 20x esigi (~saat) |
|---|---|---|
| M15 | ~5,3 saat (N≈21 bar) | ~8,3 saat (N≈33 bar) |
| H1  | ~15,8 saat (N≈16 bar) | ~25,9 saat (N≈26 bar) |
| H4  | ~24,6 saat / ~1,0 gun (N≈6 bar) | ~40,8 saat / ~1,7 gun (N≈10 bar) |

BAGLAM: Uc ufukta da S1 esigi ancak coklu-saat (M15: en iyi durumda ~5-8 saat) ila
coklu-gun (H4: ~1-1,7 gun) mertebesindeki tutma sureleriyle asiliyor. En kisa/en iyi aday
M15'tir, ama bu ufuk 2022-2026 donemine ait (bkz. A.0/Sinirlamalar) — H1/H4'un daha uzun
(2001-2026) donemiyle DOGRUDAN karsilastirilamaz; M15'in daha iyi gorunmesi kismen
donem farkindan (2022-2026'da altin fiyati ve volatilitesi tarihsel olarak yuksek)
kaynaklanabilir, bu turde ayristirilamamistir.

---

## CELISKI BULGUSU (S1 vs Scalping-Uyumlu SL/TP) — ZORUNLU BOLUM

**Bulgu:** S1 on-kontrolunu (maliyet/hedef >= 15-20x) gecen TEK ufuk/parametre bolgesi
(en iyi aday: M15, N≈21-33 bar) yaklasik **5,3-8,3 saat** tutma suresi gerektiriyor.
Diger ufuklarda bu sure daha da uzuyor (H1: ~15,8-25,9 saat; H4: ~24,6-40,8 saat, yani
~1-1,7 gun).

**Ertan'in acik talimati** (`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`,
Cevap 3): SL/TP mesafeleri "dakikalar-birkac-saat mertebesinde tutma, gun/hafta
mertebesinde DEGIL" olmali; "gun/hafta" mertebesine kaymasi Gold Scalping alt-hedefinin
kapsaminda degil.

**Gerilim:** En iyi aday olan M15/~5,3-8,3 saatlik tutma suresi, "birkac saat" ile
"gunun buyuk kismi" arasinda bir sinir bolgesinde duruyor — acikca "dakikalar" degil,
"birkac saat" tanimina siki siki uyup uymadigi YORUMA acik (5,3 saat "birkac saat"
sayilabilir; 8,3 saat bu tanimin daha da geriliminde). H1 ve H4'teki sonuclar ise (~16
saatten ~1,7 gune kadar) tanima ACIKCA UYMUYOR ("gun mertebesi"ne giriyor).

**Bu bir hangi-ufku-seceyim KARARI DEGILDIR — bir CELISKI BULGUSUDUR:**
- S1'i (maliyet-orani) TAM ANLAMIYLA rahat/net bir marjla gecen VE ayni anda acikca
  "dakikalar-birkac-saat" tanimina (orn. <2-3 saat) net bir marjla uyan bir ufuk/parametre
  bolgesi, bu taramada BULUNAMAMISTIR.
- En yakin/en az gerilimli aday M15'tir (~5,3 saatte S1-15x'i geciyor), ama bu net bir
  "uyum" degil, bir SINIR-BOLGESI durumudur; ayrica M15'in veri donemi (2022-2026)
  digerlerinden farkli oldugu icin bu sonucun kismen donem-etkisi tasiyip tasimadigi
  bu turde ayristirilamamistir (bkz. A.6 sonu, Sinirlamalar).
- Ek not: A.2-A.5'teki bulgular (VR<1, streak-sonrasi <0,50, bear/asagi-kirilim
  devam-oraninin dusuklugu) kisa-vadeli SURDURMEYI degil hafif TERSINE-DONUSU isaret
  ediyor — bu, S1'in gerektirdigi coklu-saat tutma penceresinde "momentum devami"
  varsayimina dayanan bir A1 hipotezinin (bkz. plan taslagi Adim 1) ayrica sinanmasi
  gereken bir on-kosul oldugunu gosteriyor; bu da ayri bir gozlemdir, S1-vs-SL/TP
  celiskisinin bir parcasi degildir ama Stratejist'in Adim 1 tasarimi icin ilgili baglam
  tasir.

Karar Arastirmaci'ya ait degildir; bu bulgu Orkestrator'a/Ertan'a raporlanmaktadir.

---

## J-TARAMASI BULGULARI (Coklu-Test Duzeltmeli, H1 verisi, 2001-2026)

Yontem: her saat/gun/session icin bar-ici log-getiri (log(close/open)) ortalamasinin
sifirdan farkli olup olmadigi, tek-orneklem t-testi (buyuk n icin normal yaklasimla
p-degeri). Bonferroni duzeltmesi: alpha=0,05/(test sayisi), ayri aile basina.

### J.1 — Saat Bazinda (24 test, alpha_bonferroni=0,00208)

| Saat (sunucu, GMT+3) | n | Ort. log-getiri | t | p (ham) | Duzeltme-sonrasi anlamli mi |
|---|---|---|---|---|---|
| 00 | 3.417 | +0,000400 | 2,126 | 0,0335 | Hayir |
| **01** | 3.720 | **+0,000467** | **8,842** | **~0,0000** | **EVET** |
| 02-23 | (tumu) | -0,00008..+0,00006 | \|t\|<2,2 | >0,05 | Hayir |

(Tam 24 saatlik tablo JSON ciktisinda; saat 01 disinda hicbir saat ham p-degerinde bile
guclu bir sinyal gostermiyor.)

BAGLAM: Sunucu saati 01:00 (GMT+3) bari, 24 saatlik ailede tek basina Bonferroni
esigini rahat asan (t=8,84) tek saattir. Bu saat, asagidaki J.3 "Dusuk-likidite/rollover
(23-03)" session penceresinin icindedir — iki bulgu BAGIMSIZ DEGILDIR, ayni alt-donemin
farkli gruplamalarda tekrar gorunmesi olabilir (bkz. Sinirlamalar).

### J.2 — Gun Bazinda (5 test, alpha_bonferroni=0,01)

| Gun | n | Ort. log-getiri | t | p (ham) | Duzeltme-sonrasi anlamli mi |
|---|---|---|---|---|---|
| Pazartesi | 16.055 | -0,0000004 | -0,017 | 0,986 | Hayir |
| Sali | 16.438 | +0,0000150 | 0,623 | 0,533 | Hayir |
| Carsamba | 16.353 | +0,0000459 | 1,920 | 0,055 | Hayir |
| Persembe | 16.331 | +0,0000267 | 1,106 | 0,269 | Hayir |
| **Cuma** | 16.032 | **+0,0001075** | **4,352** | **0,0000135** | **EVET** |

BAGLAM: Cuma, 5 gunluk ailede Bonferroni-duzeltmesi sonrasi da anlamli kalan tek gundur.

### J.3 — Session Bazinda (yaklasik, 4 test, alpha_bonferroni=0,0125)

Session sinirlari yaklasik/varsayimsaldir (sunucu saati GMT+3 uzerinden kabaca
Asya/Avrupa/ABD/dusuk-likidite ayrimi) — DST dogrulamasi bu turde yapilmamistir.

| Session (yaklasik saat araligi) | n | Ort. log-getiri | t | p (ham) | Duzeltme-sonrasi anlamli mi |
|---|---|---|---|---|---|
| Asya (03-10) | 23.709 | +0,0000100 | 0,891 | 0,373 | Hayir |
| Avrupa (10-16) | 20.394 | -0,0000104 | -0,683 | 0,495 | Hayir |
| ABD (16-23) | 23.523 | -0,0000049 | -0,313 | 0,754 | Hayir |
| **Dusuk-likidite/rollover (23-03)** | 13.610 | **+0,0002388** | **4,774** | **0,0000018** | **EVET** |

### J.4 — Degerlendirme (gorev talimati Madde 3 geregi)

Iki bulgu (saat=01 ve Cuma) GUCLU ve coklu-test-duzeltmesi-sonrasi anlamli — bu nedenle
"hipoteze yukseltilebilir" olarak ISARETLENIYOR. Session-bazli "dusuk-likidite/rollover"
bulgusu, saat=01 bulgusuyla orneklem cakismasi tasidigi icin BAGIMSIZ UCUNCU bir kanit
olarak SAYILMAMALIDIR (ayni alt-pencerenin iki farkli gruplamada gorunmesi). Asya/
Avrupa/ABD session'larinin hicbirinde ham p-degeri bile anlamli degil. Gorev talimati
geregi J icin ayri bir hipotez/pipeline turu ONERILMIYOR — bu iki bulgu (rollover-
penceresi ve Cuma) baska ailelerin (A) filtresi/feature'i olarak degerlendirilebilecek
adaylar olarak raporlanmaktadir; nihai karar Stratejist'e aittir.

---

## ONERILEN SONRAKI ADIM (Aday Listesi — KARAR DEGIL)

Stratejist'in degerlendirecegi, bu taramadan cikan aday ufuk/parametre bolgeleri:

1. **M15, ~4-8 saat tutma penceresi**: S1'e en yakin/en dusuk gerilimli ufuk, ama
   Celiski Bulgusu'ndaki sinir-bolgesi durumu nedeniyle Ertan'in netlestirmesini
   gerektirebilir (5-8 saat "birkac saat" sayilir mi).
2. **H1, ~16-26 saat tutma penceresi**: S1'i daha rahat marjla geciyor (22,97x @ 32 bar)
   ama "gun mertebesi"ne daha yakin — Celiski Bulgusu kapsaminda.
3. Momentum/surekliligi test edecek herhangi bir A1 hipotezinin, A.2-A.5'teki hafif
   tersine-donus isaretini (surekliligi degil) goz onunde bulundurmasi faydali olabilir
   — bu bir on-kosul gozlemidir, model tasarim karari degildir.
4. J-taramasindan iki aday feature/filtre: (a) sunucu saati ~01:00 rollover penceresi,
   (b) Cuma gunu — ikisi de ayri hipotez degil, olasi filtre/feature girdisi olarak.
5. Donchian-tipi kirilim (C) ile MA-durum-tipi (A) giris arasinda buyuk sistematik fark
   gozlenmedi (A.5) — ikisinin ayni yon-asimetrisini tasidigi not edildi.

---

## SINIRLAMALAR

- **Veri araligi asimetrisi (kritik):** M15 (2022-2026, ~4,25 yil) ile H1/H4 (2001-2026,
  ~25 yil) FARKLI donemleri kapsiyor; MT5 terminal `maxbars=100000` sinirindan
  kaynaklaniyor. Ufuklar-arasi tum karsilastirmalar (ozellikle S1/Celiski Bulgusu'ndaki
  "M15 en iyi aday" gozlemi) bu donem-farkindan etkilenmis olabilir; bu turde
  ayristirilamamistir.
- **DST/saat-eslesme dogrulamasi bu turde YAPILMADI.** `justin_backtest_onkontrol_
  standardi.md` Madde 1 geregi bu, tam bir backtest turunde ZORUNLUDUR; bu tur tam bir
  backtest turu olmadigi icin (Arastirmaci-duzeyi on-tarama) atlanmistir, ama J-Taramasi
  session/saat bulgulari icin bir acik dogrulama-ihtiyaci olarak kayda gecirilmelidir —
  Adim 1/full-backtest asamasinda BAGIMSIZ olarak dogrulanmalidir.
- **Otokorelasyon/VR/streak testleri basit, "model kurmayan" olcumlerdir** — walk-forward,
  islem maliyeti, gercekci fill/slipaj UYGULANMAMISTIR. Bu sayilar "isaret var mi/yok mu"
  sorusuna cevap verir, bir stratejinin PF/DD performansini ONGORMEZ.
- **S1 hedef-hesaplamasi bir PROXY'dir:** gercek bir SL/TP semasi tasarlanmadi; "hedef"
  olarak N-bar-ileri gerceklesen |kapanis farki| medyani kullanildi (yon dogrulugu
  varsayilmadan). Gercek bir stratejinin net edge'i, bu proxy'den daha dusuk olabilir
  (cunku yon her zaman doğru tahmin edilmez) — bu sayilar UST SINIR niteligindedir.
- **Slipaj tahmini** (ATR x %3,7) `justin_backtest_onkontrol_standardi.md`'deki tek bir
  gecmis kalibrasyon noktasina (H2/M5 kesiti) dayanir; M15/H1/H4 icin bagimsiz olarak
  yeniden olculmemistir — bir varsayimdir, olcum degil.
- **J-Taramasi session sinirlari yaklasiktir**, DST/gercek seans-saatleri dogrulamasi
  yapilmadan tanimlanmistir (yukaridaki DST notuyla birlikte okunmalidir).
- **25 yillik H1/H4 orneklemi rejim-degisikligi riski tasir** (2001-2026 arasi altin
  piyasasinin yapisi/volatilite rejimi degismis olabilir); bu turde alt-donem kirilimi
  yapilmamistir, tum donem tek blok olarak analiz edilmistir.
- Otokorelasyon/VR z-degerleri buyuk n nedeniyle kucuk katsayilarda bile "anlamli"
  cikabilir — bu istatistiksel anlamliligin ekonomik/islem-edilebilir anlamlilikla ES
  OLMADIGINI hatirlatir (yorum degil, metodolojik not).

---

## IZOLASYON NOTU

Bu rapor ve uretilen script yalnizca `C:\MilaYatirim\Justin\` klasoru icinde calisilmis,
tek veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD sembolu ham
OHLCV verisi kullanilmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu, deger
veya format/sablon referans olarak ACILMAMISTIR. Script yapisi, ayni proje icindeki
onceki Justin scriptiyle (`research_scalping.py`) benzer genel iskeleti (MT5 baglanti/
veri-cekme kalibi) paylasir — bu ayni-proje-ici bir kod-tekrari olup izolasyon ihlali
DEGILDIR (izolasyon kurali yalnizca BASKA projelerin dosya/format referansini yasaklar).
