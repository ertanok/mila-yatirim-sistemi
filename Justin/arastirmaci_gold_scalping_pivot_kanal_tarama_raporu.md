# ARASTIRMACI RAPORU — Justin / Gold Scalping — Strateji Ailesi Plani, ADIM 0 EK TARAMA (PIVOT/KANAL)

Tarih: 14 Temmuz 2026
Tetikleyici: Ertan'in Adim 0 raporuna (`arastirmaci_gold_scalping_adim0_tarama_raporu.md`)
Soru 2 + Soru 3 geri bildirimi, Orkestrator degerlendirmesi
(`orkestrator_yanit_3soru_justin_20260714.md`, Bolum 2).
Kapsam: **Tam Yol1 pipeline turu DEGIL.** Arastirmaci-duzeyi, dar kapsamli EK on-tarama.
Hipotez/model uretilmemistir, Stratejist'e devir yoktur — sonuc dogrudan Orkestrator'a
raporlanmaktadir. Adim 0 ile AYNI statu, Adim 0'in bar-bar bulgularini GECERSIZ KILMAZ —
Adim 0'in TEST ETMEDIGI farkli/tamamlayici bir mekanizmayi (yapisal/kanal-tabanli
sureklilik) ayrica sinar.
Veri kaynagi: XM/MT5, dogrudan `MetaTrader5` kutuphanesi, sembol GOLD, sunucu saati (GMT+3,
DST bu turde bagimsiz dogrulanmadi — bkz. Sinirlamalar).
Script'ler: `arastirmaci_gold_scalping_pivot_kanal_tarama.py` (ana tarama) → cikti:
`arastirmaci_gold_scalping_pivot_kanal_tarama_output.json`;
`arastirmaci_gold_scalping_pivot_kanal_tarama_cnotu.py` (C-Notu, ayni algoritma tekrar
calistirilarak kirilim-sonrasi gozlem) → cikti:
`arastirmaci_gold_scalping_pivot_kanal_tarama_cnotu_output.json` (tum ham sayilar bu iki
dosyada).

---

## OZET

1. **Veri araligi 4 ufukta da FARKLI donemleri kapsiyor** (MT5 terminal `maxbars=100000`
   siniri): H1 ~25 yil (2001-2026, 81.250 bar), M30 ~8,5 yil (2018-2026, 99.999 bar), M15
   ~4,25 yil (2022-2026, 99.999 bar — Adim 0 ile ayni), M5 ~1,4 yil / ~17 ay (2025-02-11 →
   2026-07-13, 99.999 bar — bu turde ILK KEZ olculdu). M5'in cok kisa/yakin-donem kapsami,
   asagidaki M5-giris bulgularinin genellenebilirligini ciddi sekilde sinirlar (bkz.
   Sinirlamalar).
2. **Pivot/kanal (>=3 dokunus + EMA50/EMA200 + MACD 12/26/9 teyidi) tanimiyla, H1/M30'da
   GERCEKTEN HAFTALARCA suren yapisal trendler tespit edildi** — bu, Ertan'in tarif ettigi
   mekanizmayla (bar-bar istatistik DEGIL) DOGRUDAN uyumlu bir olcum sonucudur: onaylanmis
   kanallarin medyan omru (onay→kirilim) H1'de ~28,5-35,5 gun, M30'da ~21,6-24,8 gun (detay
   asagida). Bu, Adim 0'in bar-bar bulgularinin (surekliligi DEGIL hafif tersine-donus
   isareti) ayni veri uzerinde farkli bir mekanizmaya bakildiginda cok farkli bir sure
   olcegi ortaya cikardigini gosterir — iki bulgu CELISMIYOR, farkli seyler olcuyor.
3. **Onay-sonrasi trend-yonunde-devam orani KARISIK/TUTARSIZ** — 1/3/7/14 gunluk ufuklarda
   %13-80 arasinda degisiyor, monotonik bir patern YOK (bazi ufuklarda %50 altina da
   iniyor). Orneklem kucuk (n=15-39 kanal) — bu bulgu "yapisal trend her zaman guvenle
   devam eder" seklinde OKUNAMAZ.
4. **S1 on-kontrolu (maliyet/hedef >= 15-20x), bu yeni yapisal+M15/M5-giris kombinasyonunda
   Adim 0'a gore COK DAHA KISA tutma sureleriyle asiliyor** — 8 kombinasyonun (2 ufuk x 2
   giris-TF x 2 yon) TAMAMI 15x esigini 52 dakika–6,4 saat arasinda, 20x esigini 92 dakika–
   10,3 saat arasinda geciyor (Adim 0'in en iyi adayi olan M15'in 5,3-8,3 saatine kiyasla
   M5-girisli kombinasyonlar acikca DAHA IYI, M15-girisli kombinasyonlar BENZER/SINIRDA).
5. **CELISKI BULGUSU (kismi cozum, tam degil):** M5-seviyesi girisler (H1→M5 ve M30→M5,
   her iki yon) S1'i net bir "dakikalar-birkac saat" penceresinde (0,86-3,7 saat) geciyor —
   Adim 0'daki gerilimi BU ALT-KUME icin buyuk olcude gideriyor GORUNUYOR. Ancak bu sonucun
   dayandigi bagimsiz yapisal-kanal sayisi COK KUCUK (2-8 kanal) ve M5 verisi sadece ~17
   aylik yakin donemi kapsiyor — bu, "celiski cozuldu" seklinde bir KARAR DEGIL, dar
   kanitli/kirilgan bir bulgu. M15-seviyesi girisler ise Adim 0'daki sinir-bolgesi
   durumunu buyuk olcude TEKRARLIYOR (4,4-10,3 saat).
6. **C-Notu (gozlemsel):** Kanal kirilimi sonrasi tersine-donus orani ufuklar arasi
   TUTARSIZ (%13-63), ayri bir hipotez/patern KURULMAMISTIR.

---

## PIVOT/KANAL TANIMI (TAM FORMUL — yeniden-uretilebilir)

Bu bir on-tarama, optimizasyon DEGILDIR — asagidaki parametreler standart/makul baslangic
degerleridir, tarama bu degerler uzerinde optimize edilmeye CALISILMAMISTIR.

1. **Pivot (swing) tanimi — fraktal, N=5:** bar `i`, `high[i] == max(high[i-5:i+6])` ise
   "swing high"; `low[i] == min(low[i-5:i+6])` ise "swing low" (5 bar sol + 5 bar sag
   penceresinde lokal ekstremum).
2. **Kanal cizgisi:** anchor (1. swing noktasi) ile trend yonunde ILK sonraki swing (2.
   nokta) arasindan gecen DOGRUSAL cizgi — 2 nokta ile tanimlanir, sonradan REFIT
   EDILMEZ (sabit egim, deterministik).
3. **Dokunus toleransi:** `tol(i) = 0.5 x ATR14(i)` (o bardaki ATR14, points cinsinden,
   14-bar hareketli ortalama True Range).
4. **Dokunus:** bir sonraki swing noktasi, cizginin projeksiyonuna `|fiyat - projeksiyon|
   <= tol(i)` ise "dokunus" sayilir ve dokunus sayacina eklenir.
5. **Kirilim (gecerlilik-oncesi, swing taramasi sirasinda):** bir swing noktasi
   projeksiyonu trend-aleyhine `tol(i)`den fazla asarsa (yukselen kanal: fiyat <
   projeksiyon - tol; alcalan kanal: fiyat > projeksiyon + tol), bu aday anchor
   TERK EDILIR (gecerli kanal olarak SAYILMAZ).
6. **Gecerlilik esigi: >=3 dokunus** (anchor + en az 2 ek dokunus — gorev tanimindaki
   "ilk olusum + en az 2 ek dokunus" kriteri). 3. dokunusun olustugu bar "ONAY (confirm)
   bari" olarak isaretlenir.
7. **EMA/MACD teyidi (ONAY barinda kontrol edilir, standart parametreler):**
   - EMA50 / EMA200 (kapanis fiyati uzerinden, ussel hareketli ortalama): yukselen kanal
     icin `EMA50 > EMA200`; alcalan kanal icin `EMA50 < EMA200`.
   - MACD (12,26,9 standart): yukselen kanal icin `MACD_line > MACD_signal`; alcalan
     kanal icin `MACD_line < MACD_signal`.
   - Ikisi de saglanmazsa aday, geometrik olarak 3-dokunus sartini gecse bile,
     **onaylanmis yapisal kanal SAYILMAZ** (elenir, bir sonraki anchor denenir).
8. **Onay sonrasi tam kirilim noktasi:** onay barindan itibaren artik SADECE swing
   noktalari degil TUM barlarin KAPANIS fiyati taranir; cizgi onay anindaki 2-nokta
   egimiyle DONDURULMUS olarak kullanilir (yeniden fit edilmez). Ilk `close[i]` projeksiyonu
   trend-aleyhine `tol(i)`den fazla astigi bar, kanalin KIRILIM (break) bari sayilir.
9. **Arama penceresi sinirlamasi (hesaplama pratikligi, optimizasyon DEGIL):** anchor'dan
   itibaren ~300 gun (432.000 dakika) gercek-zaman penceresi asilirsa aday/kanal terk
   edilir/sinirlanir (bu sinira dayanan kanallar "censored" olarak isaretlenir, bkz.
   asagida).
10. **Non-overlapping tarama:** bir kanal onaylanip kirilim noktasi bulundugunda, bir
    sonraki anchor arayisi kirilim noktasindan SONRAKI ilk swing noktasindan devam eder
    (kanal araliklari CAKISMAZ, tekrarli sayim onlenir).
11. **M15/M5 giris tetigi (H1/M30 kanali icinde):** onaylanmis H1/M30 kanalinin cizgisi,
    zaman damgasi uzerinden M15/M5 barlarina PROJEKSIYONLA aktarilir (dakika-bazli egim).
    Kanalin aktif penceresinde (onay→kirilim, M15/M5 veri araligiyla kesisen kisim), bir
    M15/M5 bari `|kapanis - projeksiyon| <= 0.5 x ATR14_M15veyaM5(bar)` ise "dokunus"; bir
    SONRAKI M15/M5 barinin kapanisi trend yonunde ilerlerse (yukselen: kapanis artan;
    alcalan: kapanis azalan) bu, GIRIS TETIGI olarak isaretlenir (giris = o bir-sonraki
    barin kapanisi). Not: birden fazla nitelikli dokunus-sicramasi ayni kanal icinde
    BAGIMSIZ olay olarak sayilir (gercek bir islem-sirasi DEGIL, istatistiksel bir olay
    kumesi — bkz. Sinirlamalar, bagimsizlik notu).

---

## H1/M30 YAPISAL TREND BULGULARI (siklik / sure / devam-orani)

Kaynak: `arastirmaci_gold_scalping_pivot_kanal_tarama_output.json`,
`h1_m30_yapisal_kanal_ozet`. Swing sayilari (N=5 fraktal): H1 swing-high=5.050,
swing-low=5.151; M30 swing-high=6.180, swing-low=6.261.

| Ufuk | Yon | Onaylanmis kanal (n) | Kanal basina ort. bar | Yillik kanal (yaklasik) | Sure (onay→kirilim) medyan | Veri-sonu censored orani |
|---|---|---|---|---|---|---|
| H1  | Yukselen  | 27 | 3.009,3 | ~2,91/yil | 852 saat (~35,5 gun) | %25,9 |
| H1  | Alcalan   | 39 | 2.083,3 | ~4,21/yil | 684 saat (~28,5 gun) | %10,3 |
| M30 | Yukselen  | 20 | 4.999,9 | ~3,51/yil | 594,2 saat (~24,8 gun) | %25,0 |
| M30 | Alcalan   | 39 | 2.564,1 | ~6,84/yil | 518,5 saat (~21,6 gun) | %5,1 |

BAGLAM: Medyan omurler (onay→kirilim) 3-5 hafta mertebesinde — Ertan'in "haftalarca
surebilen" tanimiyla DOGRUDAN uyumlu bir olcum. "Censored" (veri sonunda hala aktif/kirilma
gozlemlenemeyen) kanallar bu medyanlari HAFIFCE dusuk gosteriyor olabilir (sag-sansurlu
veri — gercek omur, olculenden daha uzun olabilir, bkz. Sinirlamalar). Anchor→kirilim
(onay-oncesi olusum surecini de iceren) toplam yasam suresi daha da uzun: H1 yukselen
medyan 946 saat (~39,4 gun), H1 alcalan 728 saat (~30,3 gun), M30 yukselen 1.213,5 bar
(~606,8 saat/~25,3 gun), M30 alcalan 1.063 bar (~531,5 saat/~22,2 gun) (tam sayilar
JSON'da).

### Onay-sonrasi trend-yonunde-devam orani (1/3/7/14 gun sonra fiyat hala trend yonunde ileride mi)

| Ufuk | Yon | n | 1 gun | 3 gun | 7 gun | 14 gun |
|---|---|---|---|---|---|---|
| H1  | Yukselen | 27 | 0,5926 | 0,4074 | 0,5556 | 0,4444 |
| H1  | Alcalan  | 39 | 0,6923 | 0,4615 | 0,5385 | 0,5789 |
| M30 | Yukselen | 20 | 0,7500 | 0,8000 | 0,7368 | 0,6316 |
| M30 | Alcalan  | 39 | 0,5897 | 0,4615 | 0,4359 | 0,4359 |

BAGLAM: Patern MONOTONIK DEGIL ve ufuklar arasi TUTARSIZ. M30-yukselen en guclu/en tutarli
devam sinyalini gosteriyor (%63-80 arasi, tum ufuklarda %50 ustunde); H1-yukselen ve
M30-alcalan ise 3/7/14 gun ufuklarinda sik sik %50'nin ALTINA duşuyor (Adim 0'daki hafif
tersine-donus bulgusuyla kismen paralel bir gozlem, ama burada orneklem cok daha kucuk —
n=20-39 — ve tek bir yon icin bile ufuklar arasi tutarli degil). Kucuk orneklem nedeniyle
guven araliklari genistir; bu tablo "yapisal trend guvenle devam eder" sonucunu
DESTEKLEMEMEKTEDIR, sadece ham orani raporlamaktadir.

---

## M15/M5 GIRIS-ZAMANLAMA BULGULARI

Kaynak: `giris_testi_m15_m5`. Yontem Adim 0 ile TUTARLI: `hedef_pts` = giris barindan N bar
ileri gerceklesen |kapanis farki| medyani (gercek, yon varsayilmadan — Adim 0'daki gibi bir
UST SINIR proxy'sidir); `cost_pts` = spread medyan + 0,037 x ATR14 medyan (o alt-ufuktaki
GLOBAL degerler, Adim 0'daki S1 kalibrasyonuyla ayni formul).

Global maliyet (M15/M5, tum veri):

| Ufuk | Spread medyan (pts) | ATR14 medyan (pts) | Toplam maliyet (pts) |
|---|---|---|---|
| M15 | 27,0 | 287,71 | 37,65 |
| M5  | 34,0 | 376,00 | 47,91 |

Giris-tetigi sayilari ve ORTUSEN yapisal-kanal sayisi (kritik — asagida ayrica
vurgulanmistir):

| Kombinasyon | Yon | Ortusen H1/M30 kanal sayisi (n) | Giris tetigi sayisi |
|---|---|---|---|
| H1→M15  | Yukselen | 6  | 24.801 |
| H1→M15  | Alcalan  | 16 | 20.400 |
| H1→M5   | Yukselen | 2  | 15.259 |
| H1→M5   | Alcalan  | 8  | 8.017  |
| M30→M15 | Yukselen | 11 | 21.871 |
| M30→M15 | Alcalan  | 18 | 31.930 |
| M30→M5  | Yukselen | 5  | 15.344 |
| M30→M5  | Alcalan  | 6  | 22.071 |

BAGLAM (onemli metodolojik uyari): Giris-tetigi sayilari (binlerce) ile ortusen yapisal
kanal sayilari (2-18) arasindaki BUYUK fark, ayni birkac kanal icinde fiyatin cizgiye
defalarca yaklasip-uzaklasmasindan kaynaklanir — bu giris olaylari BIRBIRINDEN BAGIMSIZ
DEGILDIR (ayni birkac trend-epizoduna ait, otokorelasyonlu gozlemlerdir). "Giris tetigi
sayisi" bir istatistiksel guc olcusu olarak DOGRUDAN OKUNMAMALIDIR; asil kisitlayici sayi
"ortusen kanal sayisi"dir (bazi kombinasyonlarda sadece 2-6).

### Ileri-hareket/maliyet orani (N bar ileri, gercek sure) — ozet (tam tablo JSON'da)

| Kombinasyon | Yon | N=1 orani | N=8 orani | N=32 orani | En yakin olculen nokta 15x'i gectigi yer |
|---|---|---|---|---|---|
| H1→M15  | Yukselen | 3,40 (15dk) | 9,72 (120dk) | 21,38 (480dk) | N=16 (240dk): 14,26 → N=32: 21,38 |
| H1→M15  | Alcalan  | 2,74 (15dk) | 7,76 (120dk) | 17,43 (480dk) | N=16 (240dk): 11,37 → N=32: 17,43 |
| H1→M5   | Yukselen | 2,92 (5dk)  | 8,35 (40dk)  | 17,01 (160dk) | N=16 (80dk): 11,94 → N=32: 17,01 |
| H1→M5   | Alcalan  | 4,63 (5dk)  | 13,48 (40dk) | 27,68 (160dk) | N=8 (40dk): 13,48 → N=16: 18,68 |
| M30→M15 | Yukselen | 3,51 (15dk) | 9,75 (120dk) | 21,33 (480dk) | N=16 (240dk): 14,37 → N=32: 21,33 |
| M30→M15 | Alcalan  | 2,79 (15dk) | 7,97 (120dk) | 18,06 (480dk) | N=16 (240dk): 11,77 → N=32: 18,06 |
| M30→M5  | Yukselen | 4,32 (5dk)  | 12,27 (40dk) | 25,36 (160dk) | N=8 (40dk): 12,27 → N=16: 17,22 |
| M30→M5  | Alcalan  | 3,55 (5dk)  | 10,19 (40dk) | 21,44 (160dk) | N=8 (40dk): 10,19 → N=16: 14,30 |

**Interpolasyonlu S1 esigine (15x/20x) ulasan tutma-suresi (iki olculen nokta arasi
dogrusal interpolasyon — bir OLCUM DEGIL, TAHMINDIR):**

| Kombinasyon | Yon | 15x esigi | 20x esigi |
|---|---|---|---|
| H1→M15  | Yukselen | 264,9 dk (~4,4 saat) | 433,5 dk (~7,2 saat) |
| H1→M15  | Alcalan  | 383,8 dk (~6,4 saat) | 617,1 dk (~10,3 saat) |
| H1→M5   | Yukselen | 128,3 dk (~2,1 saat) | 219,5 dk (~3,7 saat) |
| H1→M5   | Alcalan  | **51,7 dk (~0,9 saat)** | **91,7 dk (~1,5 saat)** |
| M30→M15 | Yukselen | 261,7 dk (~4,4 saat) | 434,1 dk (~7,2 saat) |
| M30→M15 | Alcalan  | 363,2 dk (~6,1 saat) | 578,1 dk (~9,6 saat) |
| M30→M5  | Yukselen | 62,1 dk (~1,0 saat) | 107,3 dk (~1,8 saat) |
| M30→M5  | Alcalan  | 87,8 dk (~1,5 saat) | 143,9 dk (~2,4 saat) |

---

## S1 SONUCU

Adim 0'daki en iyi/en kisa aday (M15, kosulsuz/bar-bar) S1-15x'i ~5,3 saatte, S1-20x'i ~8,3
saatte geciyordu. Bu turde, yapisal-kanal + M15/M5-giris kombinasyonlarinin **TAMAMI (8/8)**
Adim 0'in H1/H4 sonuclarindan (16 saat–1,7 gun) COK DAHA HIZLI S1'i geciyor, ve M5-seviyesi
kombinasyonlarin (4/8) TAMAMI Adim 0'in en iyi M15 adayindan da DAHA HIZLI (0,9-3,7 saat
araliginda 15x/20x'e ulasiyor). M15-seviyesi kombinasyonlar (4/8) ise Adim 0'in M15
bulgusuyla KABACA AYNI mertebede (4,4-10,3 saat).

---

## CELISKI BULGUSU (S1 vs Scalping-Uyumlu SL/TP) — kismi/kirilgan cozum

**Bulgu:** M5-seviyesi girisler (H1→M5 ve M30→M5, her iki yon) S1 esigini 0,9-3,7 saat
araliginda geciyor — Ertan'in "dakikalar-birkac saat mertebesinde tutma"
(`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`, Cevap 3) tanimina Adim 0'daki
en iyi adaydan (M15, 5,3-8,3 saat, "sinir-bolgesi") daha NET bir sekilde uyuyor gibi
gorunuyor — ozellikle H1→M5 alcalan (0,9-1,5 saat) acikca "birkac saat" icinde.

**Ancak bu bir "celiski cozuldu" KARARI DEGILDIR — kirilgan/dar-kanitli bir bulgudur:**
- Bu sonucun dayandigi ORTUSEN yapisal kanal sayisi cok kucuktur: H1→M5 yukselen icin
  sadece **2 kanal**, M30→M5 yukselen icin **5 kanal**, M30→M5 alcalan icin **6 kanal**,
  H1→M5 alcalan icin **8 kanal**. Binlerce "giris tetigi" bu birkac kanalin ICINDE
  tekrarlanan, birbirinden BAGIMSIZ OLMAYAN gozlemlerdir (bkz. M15/M5 bolumundeki
  metodolojik uyari).
- M5 verisi sadece ~17 aylik (2025-02→2026-07) bir donemi kapsiyor — H1'in 25 yillik veya
  M30'un 8,5 yillik gecmisinin cok kucuk/en-yakin bir dilimidir. Bu bulgu, sadece bu yakin
  donemin (ve o donemdeki 2-8 trend-epizodunun) bir yansimasi olabilir; farkli bir
  donemde/rejimde tekrarlanip tekrarlanmayacagi bu turde test EDILMEMISTIR.
- M15-seviyesi girisler (H1→M15, M30→M15, her iki yon: 4,4-10,3 saat), Adim 0'daki
  sinir-bolgesi gerilimini BUYUK OLCUDE TEKRARLIYOR — ozellikle alcalan yon (6,1-10,3 saat)
  "birkac saat" ile "gunun buyuk kismi" sinirinda kaliyor, Adim 0'daki ayni dilde
  gerilim devam ediyor.
- **Sonuc:** M5-seviyesi giris kombinasyonlari (4/8), Ertan'in Cevap 3 kisitiyla S1'i AYNI
  ANDA saglayan bir aday BOLGESI olarak ISARETLENEBILIR, ama bu isaretleme dar orneklem
  (2-8 kanal) ve kisa/yakin veri donemi (~17 ay) nedeniyle **DOGRULAMA GEREKTIRIR** —
  Stratejist/Backtest Muhendisi asamasinda daha genis orneklemle (orn. farkli M5 veri
  kaynagi/donemi veya walk-forward) ayrica sinanmadan "celiski cozuldu" sonucuna
  VARILMAMALIDIR. M15-seviyesi kombinasyonlar icin gerilim biraz azalmis olsa da buyuk
  olcude DEVAM ETMEKTEDIR.

Karar Arastirmaci'ya ait degildir; bu bulgu Orkestrator'a/Ertan'a raporlanmaktadir.

---

## C-NOTU (opsiyonel, gozlemsel — ayri hipotez/model KURULMAMISTIR)

Kaynak: `arastirmaci_gold_scalping_pivot_kanal_tarama_cnotu_output.json`. Kanal kirilimi
(yapisal trendin bozulmasi) sonrasi 1/3/7 gun icinde fiyatin TREND-ALEYHINE (tersine-donus)
hareket etme orani:

| Ufuk | Yon | n (censored olmayan kirilim) | 1 gun | 3 gun | 7 gun |
|---|---|---|---|---|---|
| H1  | Yukselen | 20 | 0,5500 | 0,5500 | 0,5500 |
| H1  | Alcalan  | 35 | 0,4000 | 0,6286 | 0,5429 |
| M30 | Yukselen | 15 | 0,1333 | 0,3333 | 0,2000 |
| M30 | Alcalan  | 37 | 0,5676 | 0,4324 | 0,6216 |

BAGLAM: Oranlar ufuklar/yonler arasi TUTARSIZ (%13-63) ve monotonik degil. M30-yukselen
kirilimlarinda tersine-donus orani belirgin dusuk (%13-33) — bu, M30-yukselen kanallarinin
zaten en yuksek devam-oranina (yukaridaki tabloda %63-80) sahip olmasiyla PARALEL bir
gozlem (kirilim bile olsa fiyat cogunlukla trend yonunde ilerlemeye devam ediyor
gorunuyor) — ama n=15 kucuk orneklem, bir patern/model iddia edilmemektedir.

---

## ONERILEN SONRAKI ADIM (Aday Listesi — KARAR DEGIL)

1. **H1/M30→M5 kombinasyonlari (ozellikle alcalan yon, ~0,9-1,5 saatte S1-geçen):** en
   dar/en scalping-uyumlu aday, ama sadece 2-8 kanal + ~17 aylik veriye dayaniyor —
   Stratejist'e sunulacaksa bu kirilganlik ACIKCA belirtilmelidir.
2. **H1/M30→M15 kombinasyonlari (~4,4-10,3 saat):** Adim 0'in M15 bulgusuyla benzer
   mertebede, daha genis kanal sayisina (6-18) dayaniyor — istatistiksel olarak biraz daha
   saglam ama scalping-geriliminde Adim 0'a benzer sinirda.
3. M5 verisinin farkli/daha genis bir donemde (mumkunse broker/veri kaynagi degistirilerek
   veya ileri tarihte tekrar) DOGRULANMASI, M5-giris bulgusunun donem-etkisi mi yoksa
   kalici bir ozellik mi oldugunu ayirt etmek icin faydali olabilir.
4. M30-yukselen kanallarinin (devam orani %63-80, kirilim-sonrasi tersine-donus orani
   dusuk) diger kombinasyonlara gore GORECE daha tutarli gorunmesi, ayrica incelenebilecek
   bir gozlemdir (n=20, kucuk orneklem, teyide muhtactir).
5. Onay-sonrasi devam-oraninin (H1/M30 tum kombinasyonlar) genel olarak TUTARSIZ/monotonik
   olmayan yapisi, "yapisal trend onaylandi = guvenli devam" varsayiminin bu veri setinde
   DESTEKLENMEDIGINI gosteriyor — herhangi bir A1 hipotezi bu riski goz onunde
   bulundurmalidir (on-kosul gozlemi, model tasarim karari degil).

---

## SINIRLAMALAR

- **Veri araligi asimetrisi (kritik, Adim 0'dan daha da belirgin):** H1 (~25 yil), M30
  (~8,5 yil), M15 (~4,25 yil), M5 (~1,4 yil/~17 ay) DORT FARKLI donemi kapsiyor. M5-giris
  bulgulari (Celiski Bulgusu'ndaki en guclu aday) SADECE 2025-02→2026-07 donemine ait
  birkac trend-epizoduna dayanmaktadir — bu, tum bulgu setinin en kirilgan/en dar-kapsamli
  parcasidir.
- **Giris-tetigi olaylari BAGIMSIZ DEGILDIR** (bkz. M15/M5 bolumu metodolojik uyarisi) — ayni
  birkac kanal icinde tekrarlanan, otokorelasyonlu gozlemlerdir. Raporlanan "n_giris" sayilari
  bir istatistiksel guc gostergesi degildir; asil kisitlayici sayi ortusen kanal sayisidir
  (2-18).
- **Sag-sansur (censoring):** kanallarin %5,1-25,9'u veri sonunda hala "aktif" (kirilma
  gozlemlenemedi) olarak isaretlendi — bu kanallarin gercek omru olculenden DAHA UZUN
  olabilir, medyan sure istatistiklerini hafifce ASAGI CEKEBILIR.
- **Kanal cizgisi 2-nokta ile tanimlanip DONDURULMUSTUR, refit edilmemistir** — bu basit ve
  deterministik bir tercih, gercek trend-cizgisi cizimi (analist gozüyle) daha esnek/refit
  edilen bir cizgi kullanabilir; bu fark sonuclari etkileyebilir, bu turde ayristirilamaz.
  Arama penceresi (~300 gun) ve dokunus toleransi (0,5xATR14) standart baslangic degerleri
  olup OPTIMIZE EDILMEMISTIR.
- **S1 hedef-hesaplamasi yine bir UST SINIR proxy'sidir** (Adim 0'daki ayni sinirlama): yon
  dogrulugu varsayilmadan, N-bar-ileri |kapanis farki| medyani kullanildi. Gercek bir
  stratejinin net edge'i bu sayidan daha dusuk olabilir.
- **DST/saat-eslesme dogrulamasi bu turde YAPILMADI** (Adim 0'daki ayni not) —
  `justin_backtest_onkontrol_standardi.md` Madde 1 geregi, tam bir backtest turunde
  (Adim 1/full-backtest) BAGIMSIZ olarak dogrulanmalidir; M15/M5 zaman-projeksiyonu
  (H1/M30 cizgisinin dakika-bazli aktarilmasi) bu dogrulamadan ETKILENEBILIR bir islemdir,
  bu nedenle bu hatirlatma ozellikle bu tur icin de gecerlidir.
- **Onay-sonrasi devam-orani ve kirilim-sonrasi tersine-donus orani KUCUK ORNEKLEM**
  tasir (n=15-39 kanal) — guven araliklari genistir, bu sayilar KESIN patern iddiasi
  olarak OKUNMAMALIDIR.
- **25 yillik H1 / 8,5 yillik M30 orneklemi rejim-degisikligi riski tasir** (Adim 0'daki
  ayni not) — alt-donem kirilimi bu turde de YAPILMADI.
- Otokorelasyon/VR gibi coklu-test duzeltmesi bu turde soz konusu degildir (bu tur J-Taramasi
  icermez); ancak S1 esik-gecis interpolasyonlari olcum DEGIL TAHMINDIR (iki olculen nokta
  arasi dogrusal interpolasyon).

---

## IZOLASYON NOTU

Bu rapor ve uretilen scriptler yalnizca `C:\MilaYatirim\Justin\` klasoru icinde calisilmis,
tek veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD sembolu ham OHLCV
verisi kullanilmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu, deger veya
format/sablon referans olarak ACILMAMISTIR. Script yapisi ve S1-maliyet-orani yontemi, ayni
proje icindeki bir onceki Adim 0 scriptiyle (`arastirmaci_gold_scalping_adim0_tarama.py`)
BILEREK tutarli tutulmustur (karsilastirilabilirlik amacli, izolasyon kurali yalnizca BASKA
projelerin dosya/format referansini yasaklar, ayni-proje-ici metodolojik tutarliligi degil).
