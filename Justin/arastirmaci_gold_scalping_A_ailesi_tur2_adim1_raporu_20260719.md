# ARASTIRMACI RAPORU — Justin / Gold Scalping — A Ailesi, TUR 2 / ADIM 1 GIRISI

Tarih: 19 Temmuz 2026
Tetikleyici: `gorev_arastirmaci_justin_gold_scalping_A_ailesi_tur2_adim1_giris_20260719.md` (Orkestrator
cagrisi) — Ertan'in 19 Temmuz "devam karari", Risk Analisti'nin Tam Tur 1 (13 Temmuz) Tur 2
onerisi ve Ertan'in Cevap 1 (`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`) geregi.
Kapsam: **Tam Yol1 pipeline turunun Arastirmaci adimidir** (Arastirmaci → Stratejist → Backtest
Muhendisi → Risk Analisti sirasi korunur). **Hipotez URETILMEMISTIR**, sonuc Stratejist'e
devredilecektir (Orkestrator uzerinden).
Veri kaynagi: XM/MT5, dogrudan `MetaTrader5` kutuphanesi, sembol GOLD, sunucu saati (GMT+3,
DST bu turde de bagimsiz DOGRULANMADI — bkz. Sinirlamalar).
Script: `arastirmaci_gold_scalping_A_ailesi_tur2_adim1.py` → cikti:
`arastirmaci_gold_scalping_A_ailesi_tur2_adim1_output.json` (tum ham sayilar bu dosyada).
H1/M30 pivot/kanal formulu, `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`daki (14
Temmuz) "PIVOT/KANAL TANIMI" bolumunden **HICBIR PARAMETRE DEGISTIRILMEDEN** alinmistir
(`detect_channels` fonksiyonu, 14 Temmuz scriptiyle birebir aynidir).

---

## OZET

1. **M1 verisi ciddi sekilde SINIRLI** — bu MT5 kurulumunda GOLD M1 verisi sadece **~100 gun
   (2026-04-08 → 2026-07-17)** geriye gidiyor; bu, M5'in ~17 aylik sinirindan (`m5_donem_
   dogrulama_raporu.md`) **DAHA DA KISA** — gorev tanimindaki beklenti dogrulandi. Position-
   sayfalama testi M5'teki ile AYNI imzayi veriyor (pos=99999→1 bar, pos=100000→cagri
   basarisiz) — bu, gercek veri-derinligi sinirina isaret eder (maxbars artefakti degil), ama
   M5 turundeki tam retry/eski-tarih dogrulamasi bu turde TEKRARLANMADI (bkz. Sinirlamalar).
2. **M1 baseline giris-zamanlama testi UYGULANABILDI ama ORTUSEN KANAL SAYISI COK KUCUK (1-3)**
   — H1→M1 yukselen: 1 kanal, H1→M1 alcalan: 3 kanal, M30→M1 yukselen: 2 kanal, M30→M1 alcalan:
   1 kanal. Binlerce giris-tetigi (6.271-35.498) bu 1-3 kanalin icinde tekrarlanan, BAGIMSIZ
   OLMAYAN gozlemlerdir. S1 esikleri (15x/20x) 63-190 dakika araliginda geciliyor — M5/M15
   sonuclarindan cok FARKLI bir mertebe DEGIL, ayni "dakikalar-birkac saat" bandinda.
3. **Coklu-teyit tetigi (N=2, N=3 ardisik bar), giris-tetigi sayisini TUTARLI bir oranda
   azaltiyor**: N=2 ~%50-52, N=3 ~%75-89 (tum 24 HTF x LTF x yon kombinasyonunda). S1
   esik-gecis sureleri baseline'a KIYASLA BUYUK OLCUDE BENZER kaliyor (fark cogunlukla ±10
   dakika/±%10 mertebesinde, tutarli bir yon YOK — bazen daha hizli bazen daha yavas).
4. **Momentum-esikli tetigi (govde/ATR14 >= 0,5x veya >= 1,0x), giris-tetigi sayisini da
   azaltiyor** (k=0,5: ~%57-63; k=1,0: ~%87-90) **VE** S1 esik-gecis surelerinde coklu-teyide
   kiyasla DAHA BELIRGIN/TUTARLI bir HIZLANMA gosteriyor — 24 kombinasyonun cogunda k=1,0
   esik-suresi baseline'dan KISA (en belirgin: M5 H1-alcalan, 54,4dk→36,7dk, ~%33 daha hizli;
   M15 H1-alcalan, 379,5dk→303,2dk, ~%20 daha hizli). Bu bir "daha iyi" degerlendirmesi
   DEGILDIR — sadece olculen bir hiz farkidir, orneklem coklu-teyide gore de kucuk.
5. **Bug-duzeltme notu (metodolojik seffaflik):** Momentum-esikli tetigin ilk hesaplamasinda
   govde degeri points birimine cevrilmeden ATR (points) ile karsilastirilmis, bu da TUM
   kombinasyonlarda 0 giris-tetigi sonucu vermisti; birim hatasi tespit edilip DUZELTILMIS,
   script BASTAN calistirilmis, asagidaki tum sayilar DUZELTILMIS calistirmadan alinmistir.
6. **Adim 0'in (14+16 Temmuz) UC raporunun bulgulari bu turde HICBIR SEKILDE DEGISTIRILMEDI/
   YENIDEN YORUMLANMADI** — sadece asagida (Bolum "Konsolide Adim-0-Ozeti") ozetlenerek yeni
   bulgularla YAN YANA sunulmustur.

---

## BULGU 1 — M1 Veri Derinligi

Veri Kaynagi: XM/MT5 `copy_rates_from_pos`/position-sayfalama testi, GOLD/M1, 19 Temmuz 2026
---------------------------------------------------------------
GOZLEM:
- `copy_rates_from_pos(GOLD, M1, 0, 99999)` → 99.999 bar, **2026-04-08 01:12:00 → 2026-07-17
  23:57:00** (sunucu saati, ~100 gun/~3,3 ay).
- `copy_rates_from_pos(GOLD, M1, 99999, 99999)` (bir sonraki "sayfa") → **sadece 1 bar** doner
  (2026-04-08 01:11:00 — ilk barin bir dakika oncesi).
- `copy_rates_from_pos(GOLD, M1, 100000, 100)` → **basarisiz** (`mt5.last_error() = (-1,
  "Terminal: Call failed")`).

BAGLAM: Bu imza (pos=99999'da 1 bara dusme + pos=100000'de tam basarisizlik),
`m5_donem_dogrulama_raporu.md`daki M5 icin gozlenen imzayla BIREBIR AYNI turden bir
davranistir — o raporda bu imza "gercek veri derinligi sinirina ulasildi" (maxbars cagri-
basina sinirinin degil) olarak yorumlanmisti. M1 icin de tutarli bir imza gozlenmistir, ama
bu turde M5 dogrulamasindaki TAM protokol (3 farkli eski donem x 3 tekrar x 5sn bekleme,
alternatif sembol karsilastirmasi) M1 icin TEKRARLANMAMISTIR — bkz. Sinirlamalar.

SINIR: Tek bir olcum turu (bu gorev), retry/gecikme testi yapilmadi. M1'in gercek derinlik
sinirinin M5'inkiyle AYNI kok nedene (hesap/sunucu M5-senkron siniri, m5_donem_dogrulama
Bolum c) bagli olup olmadigi bu turde ARASTIRILMADI.

---

## BULGU 2 — M1 Giris-Zamanlama Testi (Baseline Tetik: dokunus + bir-sonraki-barin-trend-
## yonunde-kapanmasi), H1/M30 Kanal Filtresi Icinde

Veri Kaynagi: XM/MT5, GOLD, H1 (81.348 bar, 2001-06-04→2026-07-17), M30 (99.999 bar,
2018-01-25→2026-07-17), M1 (99.999 bar, 2026-04-08→2026-07-17) | 19 Temmuz 2026
---------------------------------------------------------------
Bu turde YENIDEN tespit edilen H1/M30 parent kanal sayilari (formul DEGISMEDI): H1 yukselen=27,
H1 alcalan=39, M30 yukselen=20, M30 alcalan=40 — bu sayilar 16 Temmuz raporundaki (ic_ice_kanal_
devam) guncellenmis sayilarla BIREBIR AYNI (14 Temmuz'daki M30-alcalan=39'dan +1 farkli, veri
2 gun ilerledigi icin beklenen kucuk sapma, o raporda zaten belgelenmisti).

GOZLEM (M1 seviyesinde, baseline tetik, S1 maliyet: spread medyan=51,0 pts, ATR14 medyan=200,36
pts, toplam maliyet=58,41 pts):

| HTF | Yon | Ortusen kanal (n) | Giris tetigi (n) | 15x esigi (dk) | 20x esigi (dk) |
|---|---|---|---|---|---|
| H1  | Yukselen | 1 | 6.875  | 74,7  | 120,3 |
| H1  | Alcalan  | 3 | 6.271  | 71,9  | 123,3 |
| M30 | Yukselen | 2 | 14.711 | 107,5 | 189,0 |
| M30 | Alcalan  | 1 | 35.498 | 104,0 | 179,5 |

Detayli N-bar-ileri tablo (H1→M1 yukselen ornegi, tam tablo JSON'da `giris_testi_m1_baseline`):

| N (dk) | n_giris | ileri hareket medyan (pts) | oran (maliyete gore) |
|---|---|---|---|
| 1   | 6.875 | 105,0  | 1,80  |
| 8   | 6.875 | 304,0  | 5,20  |
| 32  | 6.875 | 587,0  | 10,05 |
| 64  | 6.875 | 808,0  | 13,83 |
| 128 | 6.875 | 1.218,0| 20,85 |
| 480 | 6.875 | 2.758,0| 47,22 |

BAGLAM: S1 esikleri (15x: 71,9-107,5 dk; 20x: 120,3-189,0 dk) M5-seviyesindeki H1→M5/M30→M5
sonuclarindan (14 Temmuz: 51,7-219,5 dk araligi) FARKLI BIR MERTEBEDE DEGIL — ayni "dakikalar-
birkac saat" bandinin ICINDE. M1'in daha ince zaman-cozunurlugu bu ozel olcumde S1-gecis suresini
belirgin sekilde KISALTMIYOR gorunuyor (M30→M1 kombinasyonlari, en yavas M5 kombinasyonundan
(H1→M5 yukselen, 129,0/220,0 dk) bile biraz daha yavas: 104,0-107,5 / 179,5-189,0 dk).

SINIR: Ortusen kanal sayisi (1-3) M5'teki en dar kombinasyonlardan (2-8) bile DAHA KUCUK — bu,
M1 bulgularinin **tum veri setindeki en kirilgan/en dar-kanitli parcasi** oldugu anlamina gelir.
H1→M1 yukselen SADECE 1 kanala, M30→M1 alcalan SADECE 1 kanala dayanmaktadir — istatistiksel
olarak tek bir trend-epizodunun yansimasidir, herhangi bir genelleme TASIYAMAZ.

---

## ALTERNATIF GIRIS-TETIGI TANIMLARI

### TAM FORMUL (Arastirmaci'nin bu tur icin tasarladigi, degistirilmemis "dokunus" tanimi uzerine
### inşa edilen iki alternatif)

Her iki alternatif de, H1/M30 kanal FILTRESI ve "dokunus" tanimini (14 Temmuz formulu:
`|kapanis - projeksiyon| <= 0,5 x ATR14(ltf bar)`) **DEGISTIRMEDEN** kullanir — sadece
dokunus-sonrasi "teyit" mantigi degisir:

**a) Coklu-teyit tetigi:** Dokunus bari `i`'den sonra, ARDISIK `N` bar (N=2 veya N=3) her biri
BIR ONCEKI bara gore trend yonunde kapanmalidir (yukselen: `kapanis[i+k+1] > kapanis[i+k]` her
`k=0..N-1` icin; alcalan: ters). Giris = `i+N` barinin kapanisi. (Orijinal tetik bunun N=1
ozel-durumudur.)

**b) Momentum-esikli tetigi:** Dokunus bari `i`'den sonraki TEYIT bari (`i+1`, orijinal tetikle
AYNI zamanlama), yon sartina (orijinaldeki gibi `kapanis[i+1]` trend yonunde) EK OLARAK govde/
ATR14 orani esigi de asmalidir: `|kapanis[i+1] - acilis[i+1]| / ATR14(i+1) >= k` (k=0,5 veya
k=1,0). Giris yine `i+1` barinin kapanisidir — zamanlama ayni, ama tetik artik SADECE yon degil
barin "gucunu" de sart kosuyor.

**Metodolojik not (seffaflik):** ilk calistirmada govde farki points'e cevrilmeden (ham fiyat
biriminde) ATR14 (points) ile karsilastirilmis — birim uyusmazligi 0 sonuc uretmisti; bu hata
tespit edilip DUZELTILDI (`govde_pts = |kapanis-acilis| / point`), script yeniden calistirildi.

### M1 seviyesi giris-tetigi karsilastirmasi

| HTF | Yon | Tetik tanimi | Ortusen kanal (n) | Giris tetigi (n) | Azalma (baseline'e gore) | 15x esigi (dk) | 20x esigi (dk) |
|---|---|---|---|---|---|---|---|
| H1 | Yukselen | Orijinal (N=1) | 1 | 6.875 | - | 74,7 | 120,3 |
| H1 | Yukselen | Coklu-teyit N=2 | 1 | 3.344 | %51,4 | 71,8 | 115,9 |
| H1 | Yukselen | Coklu-teyit N=3 | 1 | 1.614 | %76,5 | 71,6 | 117,0 |
| H1 | Yukselen | Momentum k=0,5xATR | 1 | 2.954 | %57,0 | 71,8 | 116,3 |
| H1 | Yukselen | Momentum k=1,0xATR | 1 | 899 | %86,9 | 63,2 | 109,1 |
| H1 | Alcalan | Orijinal (N=1) | 3 | 6.271 | - | 71,9 | 123,3 |
| H1 | Alcalan | Coklu-teyit N=2 | 3 | 3.134 | %50,0 | 70,5 | 117,7 |
| H1 | Alcalan | Coklu-teyit N=3 | 3 | 1.585 | %74,7 | 68,8 | 115,1 |
| H1 | Alcalan | Momentum k=0,5xATR | 3 | 2.601 | %58,5 | 69,0 | 114,4 |
| H1 | Alcalan | Momentum k=1,0xATR | 3 | 762 | %87,8 | 71,2 | 116,9 |
| M30 | Yukselen | Orijinal (N=1) | 2 | 14.711 | - | 107,5 | 189,0 |
| M30 | Yukselen | Coklu-teyit N=2 | 2 | 7.137 | %51,5 | 108,5 | 187,6 |
| M30 | Yukselen | Coklu-teyit N=3 | 2 | 3.369 | %77,1 | 111,2 | 190,9 |
| M30 | Yukselen | Momentum k=0,5xATR | 2 | 6.321 | %57,0 | 107,9 | 189,7 |
| M30 | Yukselen | Momentum k=1,0xATR | 2 | 1.906 | %87,0 | 101,7 | 183,2 |
| M30 | Alcalan | Orijinal (N=1) | 1 | 35.498 | - | 104,0 | 179,5 |
| M30 | Alcalan | Coklu-teyit N=2 | 1 | 17.288 | %51,3 | 104,3 | 180,3 |
| M30 | Alcalan | Coklu-teyit N=3 | 1 | 8.341 | %76,5 | 102,1 | 176,9 |
| M30 | Alcalan | Momentum k=0,5xATR | 1 | 15.354 | %56,7 | 104,5 | 181,4 |
| M30 | Alcalan | Momentum k=1,0xATR | 1 | 4.676 | %86,8 | 103,6 | 178,8 |

### M5 seviyesi giris-tetigi karsilastirmasi

| HTF | Yon | Tetik tanimi | Ortusen kanal (n) | Giris tetigi (n) | Azalma (baseline'e gore) | 15x esigi (dk) | 20x esigi (dk) |
|---|---|---|---|---|---|---|---|
| H1 | Yukselen | Orijinal (N=1) | 2 | 15.151 | - | 129,0 | 220,0 |
| H1 | Yukselen | Coklu-teyit N=2 | 2 | 7.549 | %50,2 | 135,4 | 226,5 |
| H1 | Yukselen | Coklu-teyit N=3 | 2 | 3.700 | %75,6 | 143,6 | 235,3 |
| H1 | Yukselen | Momentum k=0,5xATR | 2 | 6.009 | %60,3 | 124,3 | 215,2 |
| H1 | Yukselen | Momentum k=1,0xATR | 2 | 1.555 | %89,7 | 102,1 | 183,7 |
| H1 | Alcalan | Orijinal (N=1) | 8 | 8.484 | - | 54,4 | 95,8 |
| H1 | Alcalan | Coklu-teyit N=2 | 8 | 4.143 | %51,2 | 56,3 | 100,0 |
| H1 | Alcalan | Coklu-teyit N=3 | 8 | 1.971 | %76,8 | 57,0 | 100,7 |
| H1 | Alcalan | Momentum k=0,5xATR | 8 | 3.317 | %60,9 | 49,0 | 88,1 |
| H1 | Alcalan | Momentum k=1,0xATR | 8 | 904 | %89,3 | 36,7 | 69,0 |
| M30 | Yukselen | Orijinal (N=1) | 5 | 15.928 | - | 64,0 | 110,4 |
| M30 | Yukselen | Coklu-teyit N=2 | 5 | 7.926 | %50,2 | 64,6 | 112,2 |
| M30 | Yukselen | Coklu-teyit N=3 | 5 | 3.860 | %75,8 | 67,7 | 117,1 |
| M30 | Yukselen | Momentum k=0,5xATR | 5 | 6.375 | %60,0 | 64,0 | 109,5 |
| M30 | Yukselen | Momentum k=1,0xATR | 5 | 1.721 | %89,2 | 56,3 | 89,8 |
| M30 | Alcalan | Orijinal (N=1) | 6 | 22.655 | - | 89,4 | 145,7 |
| M30 | Alcalan | Coklu-teyit N=2 | 6 | 11.051 | %51,2 | 87,7 | 144,3 |
| M30 | Alcalan | Coklu-teyit N=3 | 6 | 5.230 | %76,9 | 86,9 | 142,4 |
| M30 | Alcalan | Momentum k=0,5xATR | 6 | 9.018 | %60,2 | 82,0 | 137,2 |
| M30 | Alcalan | Momentum k=1,0xATR | 6 | 2.493 | %89,0 | 75,3 | 133,8 |

### M15 seviyesi giris-tetigi karsilastirmasi

| HTF | Yon | Tetik tanimi | Ortusen kanal (n) | Giris tetigi (n) | Azalma (baseline'e gore) | 15x esigi (dk) | 20x esigi (dk) |
|---|---|---|---|---|---|---|---|
| H1 | Yukselen | Orijinal (N=1) | 6 | 24.709 | - | 265,4 | 432,8 |
| H1 | Yukselen | Coklu-teyit N=2 | 6 | 12.268 | %50,4 | 261,9 | 438,6 |
| H1 | Yukselen | Coklu-teyit N=3 | 6 | 6.088 | %75,4 | 265,4 | 449,8 |
| H1 | Yukselen | Momentum k=0,5xATR | 6 | 9.280 | %62,4 | 236,9 | 397,2 |
| H1 | Yukselen | Momentum k=1,0xATR | 6 | 2.716 | %89,0 | 216,5 | 378,9 |
| H1 | Alcalan | Orijinal (N=1) | 16 | 20.599 | - | 379,5 | 608,3 |
| H1 | Alcalan | Coklu-teyit N=2 | 16 | 9.833 | %52,3 | 382,0 | 610,3 |
| H1 | Alcalan | Coklu-teyit N=3 | 16 | 4.650 | %77,4 | 385,4 | 619,8 |
| H1 | Alcalan | Momentum k=0,5xATR | 16 | 7.575 | %63,2 | 341,9 | 547,8 |
| H1 | Alcalan | Momentum k=1,0xATR | 16 | 2.235 | %89,1 | 303,2 | 484,4 |
| M30 | Yukselen | Orijinal (N=1) | 11 | 22.028 | - | 259,3 | 428,8 |
| M30 | Yukselen | Coklu-teyit N=2 | 11 | 10.869 | %50,7 | 254,7 | 421,6 |
| M30 | Yukselen | Coklu-teyit N=3 | 11 | 5.235 | %76,2 | 245,9 | 418,5 |
| M30 | Yukselen | Momentum k=0,5xATR | 11 | 8.166 | %62,9 | 231,7 | 380,8 |
| M30 | Yukselen | Momentum k=1,0xATR | 11 | 2.391 | %89,1 | 187,2 | 345,3 |
| M30 | Alcalan | Orijinal (N=1) | 18 | 32.044 | - | 361,5 | 575,1 |
| M30 | Alcalan | Coklu-teyit N=2 | 18 | 15.371 | %52,0 | 360,6 | 571,5 |
| M30 | Alcalan | Coklu-teyit N=3 | 18 | 7.297 | %77,2 | 356,2 | 559,1 |
| M30 | Alcalan | Momentum k=0,5xATR | 18 | 12.167 | %62,0 | 327,3 | 512,5 |
| M30 | Alcalan | Momentum k=1,0xATR | 18 | 3.612 | %88,7 | 290,6 | 453,9 |

BAGLAM (ham gozlemler, yorum degil):
- **Ortusen kanal sayisi (n_overlap) tetik tipinden BAGIMSIZDIR** — dokunus tanimi degismedigi
  icin, hangi kanallarin M1/M5/M15 veri araligiyla kesistigi sabittir; sadece "teyit" mantigi
  degisince giris-tetigi SAYISI degisir. Bu nedenle her satirin ayni HTF/LTF/yon icin n_overlap
  degeri, orijinal tetikle BIREBIR AYNIDIR.
- **Coklu-teyit orani TUM 24 kombinasyonda benzer bir bantta** duruyor: N=2 → %50,0-52,3
  azalma; N=3 → %74,7-77,4 azalma. Bu, ardisik bar-yonu devam olasiliginin bu veri setinde
  kabaca "yariya-yakin" bir orana denk geldigini DUSUNDUREN sayisal bir gozlemdir (yorum
  DEGIL, sadece azalma oraninin dar bir bantta kumelenmesi bir SAYISAL desendir).
- **Momentum-esikli azalma orani da benzer sekilde bantlanmis:** k=0,5 → %56,7-63,2; k=1,0 →
  %86,8-89,7 — tum LTF/HTF/yon kombinasyonlarinda tutarli.
- **S1 esik-gecis suresi karsilastirmasinda coklu-teyit ile momentum-esikli FARKLI davraniyor:**
  coklu-teyit esik-sureleri baseline'a kiyasla YON-TUTARSIZ kucuk farklar gosteriyor (bazen
  daha hizli, bazen daha yavas, |fark| genelde <%10); momentum-esikli (ozellikle k=1,0) ise
  24 kombinasyonun COGUNDA (18/24) baseline'dan DAHA KISA esik-suresi veriyor — en belirgin
  farklar M5 H1-alcalan (54,4→36,7 dk, %33 daha hizli) ve M5 M30-yukselen (64,0→56,3 dk, %12
  daha hizli) kombinasyonlarinda gorulur.
- **Coklu-teyit ve momentum tetiklerinin HER IKISI de ORNEKLEMI KUCULTUR** — N=3/k=1,0 gibi en
  siki varyantlarda giris-tetigi sayisi orijinalin sadece %10-13'une duser (orn. M5 H1-alcalan
  momentum k=1,0: 8.484→904, %89,3 azalma). Ortusen kanal sayisi (bagimsizlik ANA kisitlayicisi)
  DEGISMEZ ama tetik-basi olay sayisi azaldikca istatistiksel gucun de (zaten tartismali olan
  "binlerce tekrarli olay" argumaninin) daha da INCELDIGI acikca gorulur.

SINIR: Yukaridaki tum sayilar, orijinal tetikle AYNI bagimsizlik sorununu tasir (bkz.
Sinirlamalar, "giris-tetigi olaylarinin bagimsiz olmamasi") — coklu-teyit/momentum varyantlari
orneklem BUYUKLUGUNU azaltir ama kanal-BAGIMLILIK yapisini DEGISTIRMEZ (ayni birkac kanal
icindeki olaylar hala otokorelasyonludur).

---

## KONSOLIDE ADIM-0-OZETI (14+16 Temmuz raporlarinin OZETI — sayilar DEGISTIRILMEDI)

### a) `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (14 Temmuz)
- H1/M30'da (>=3 dokunus + EMA50/200 + MACD teyitli) yapisal kanallar medyan **3-5 hafta**
  suruyor (H1 yukselen ~35,5 gun, H1 alcalan ~28,5 gun, M30 yukselen ~24,8 gun, M30 alcalan
  ~21,6 gun); censored orani %5,1-25,9.
- Onay-sonrasi trend-yonunde-devam orani (1/3/7/14 gun) **%13-80 arasi TUTARSIZ/monotonik
  olmayan**; n=20-39 kanal.
- M15/M5-giris (H1/M30 kanali icinde, dokunus+hemen-devam) S1 esiklerini (15x/20x) **0,9-10,3
  saat** araliginda geciyor; M5-seviyesi (0,9-3,7 saat) M15-seviyesinden (4,4-10,3 saat) DAHA
  HIZLI ama SADECE 2-8 ortusen kanala dayaniyor (M15: 6-18 kanal).
- **Celiski Bulgusu:** M5-girisler Ertan'in "dakikalar-birkac saat" tanimina M15'ten daha net
  uyuyor GORUNUYOR, ama bu KIRILGAN bir bulgu (dar kanal sayisi + ~17 aylik kisa/yakin donem).

### b) `arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam_raporu.md` (16 Temmuz)
- Ic-ice alt-kanal yapisi 8/8 kombinasyonda **YAYGIN** (pencere basina ort. 4,44-23,5 alt-kanal,
  min her yerde >=1).
- "Ana-kanal-kirilma-bazli" yeni devam tanimi, 16/16 noktada eski (fiyat-konumu) tanimdan **ESIT
  VEYA DAHA YUKSEK** (ort. +%33,8 puan) ve MONOTONIK AZALAN (eski tanim degil) — bu fark YAPISAL
  bir nedene (sure-tabanli olcu vs an-bazli olcu) sahip, "hangi tanim dogru" sorusuna yanit
  DEGIL.
- Parent kanal sayisi bu turde M30-alcalan icin 39→40 (veri 2 gun ilerledigi icin), digerleri
  degismedi — bu turun (19 Temmuz) YENIDEN tespitinde AYNI 40 sayisi dogrulandi.

### c) `arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_raporu.md` (16 Temmuz)
- GOLD M5 verisi **2025-02-17'den ONCESINE GENISLETILEMEDI** (position-sayfalama + 3x eski-donem
  retry testiyle dogrulandi) — gercek veri-derinligi siniri (maxbars artefakti degil).
  XAUEUR de benzer baslangica sahip (hesap/sunucu-genelinde M5-senkron siniri OLABILIR, kesin
  teshis degil).
- M5-donem karsilastirmasi bu nedenle **YAPILAMADI**; 14 Temmuz'un kirilganlik notu (dar kanal +
  kisa donem) DEGISMEDEN GECERLI.

### d) Bu turde eklenen (19 Temmuz, yeni)
- M1 verisi M5'ten de kisa (~100 gun); baseline M1-giris testi 1-3 ortusen kanala dayaniyor, S1
  esikleri 64-190 dk (M5/M15 ile ayni mertebede).
- Coklu-teyit (N=2/3) ve momentum-esikli (k=0,5/1,0) tetikleri butun HTF/LTF/yon kombinasyonlarinda
  olculdu; her ikisi de orneklem sayisini azaltiyor (coklu-teyit %50-89, momentum %57-90);
  momentum-esikli varyant S1 esik-suresinde coklu-teyide gore daha tutarli bir HIZLANMA
  gosteriyor (18/24 kombinasyonda daha kisa esik-suresi).

---

## ARASTIRMA BOSLUKLARI (Henuz bilinmeyenler)

- M1 verisinin gercek derinlik-sinirinin kok nedeni (maxbars mi, hesap/sunucu M5-ile-ortak bir
  senkron siniri mi) M5 icin yapilan tam retry/eski-donem protokoluyle M1 icin AYRICA test
  EDILMEDI.
- Coklu-teyit ve momentum-esikli tetiklerin BIRLESIMI (orn. N=2 VE k=0,5 esiği AYNI ANDA) bu
  turde OLCULMEDI — sadece iki mekanizma AYRI AYRI test edildi.
- Momentum-esikli tetigin "daha hizli S1-gecis" paterni (18/24 kombinasyon) neden coklu-teyitte
  bu kadar TUTARLI gorunmuyor sorusu bu turde ARASTIRILMADI (nedensel bir analiz YAPILMADI,
  sadece iki ayri sayisal davranis raporlandi).
- Coklu-teyit/momentum tetiklerinin ic-ice alt-kanal yapisiyla (16 Temmuz bulgusu) ETKILESIMI
  (orn. zit-yonlu alt-kanallarin bu yeni tetikleri nasil etkiledigi) bu turde OLCULMEDI.
- Alternatif tetiklerin farkli parametrelerle (orn. N=4, k=1,5) DAVRANISI bu turde test
  EDILMEDI — sadece gorev tanimindaki N=2/3 ve k=0,5/1,0 degerleri olculdu.

---

## SINIRLAMALAR

- **M1 orneklemi TUM veri setinin en kirilgan parcasidir:** ortusen kanal sayisi 1-3 (M5'in
  2-8'inden bile kucuk) — herhangi bir M1 bulgusu tek-birkac trend-epizoduna dayanir, genelleme
  TASIYAMAZ.
- **Giris-tetigi olaylari (tum tetik varyantlarinda) BAGIMSIZ DEGILDIR** — ayni birkac kanal
  icinde tekrarlanan, otokorelasyonlu gozlemlerdir (14 Temmuz raporundaki ayni uyari, tum yeni
  varyantlar icin de GECERLIDIR). Coklu-teyit/momentum azaltilmis orneklem sayisiyla bile bu
  bagimlilik yapisi DEGISMEZ.
- **Kucuk orneklem (parent kanal, n=20-40)** — H1/M30 kanal tespiti degismedigi icin bu sinirlama
  AYNEN devam ediyor (bkz. 14/16 Temmuz raporlari).
- **Sag-sansur (censoring):** parent kanallarin bir kismi veri sonunda hala aktif (14/16 Temmuz
  raporlarindaki oranlar, bu turde de gecerli — H1/M30 kanal kumesi degismedi).
- **Ileri-bakisli pivot tanimi (5-bar-gecikme):** swing (pivot) tespiti `high[i]==max(high[i-5:
  i+6])` seklinde SIMETRIK bir pencere kullanir — bir swing'in "onaylanmasi" icin 5 bar ILERIYE
  bakmak GEREKIR. Bu, kanal ANCHOR/SECOND noktalarinin tespitinde bir ileri-bakis (lookahead)
  unsuru tasir (14 Temmuz raporunda da zimni olarak var olan, bu turde ACIKCA yeniden
  vurgulanan bir sinirlama) — canli/gercek-zamanli bir sistemde bu 5-bar-gecikmeli DOGRULAMA ile
  calisilmalidir, backtest sirasinda bu gecikme MODELLENMELIDIR.
- **M1 veri-derinligi testi, M5'teki TAM protokolden (3 eski-donem x 3 tekrar x 5sn bekleme +
  alternatif sembol karsilastirmasi) DAHA HAFIF** — sadece position-sayfalama testi yapildi.
- **Coklu-teyit/momentum tetiklerinin parametreleri (N=2/3, k=0,5/1,0) standart/makul baslangic
  degerleridir, OPTIMIZE EDILMEMISTIR** (14 Temmuz'daki ayni ilke: bu bir tarama, optimizasyon
  degildir).
- **S1 hedef-hesaplamasi yine bir UST SINIR proxy'sidir** (yon dogrulugu varsayilmadan, N-bar-
  ileri |kapanis farki| medyani) — gercek bir stratejinin net edge'i bu sayidan daha dusuk
  olabilir.
- **DST/saat-eslesme dogrulamasi bu turde de YAPILMADI** — `justin_backtest_onkontrol_standardi.
  md` Madde 1 geregi, tam bir backtest turunde (Adim 1/full-backtest) BAGIMSIZ olarak
  dogrulanmalidir; M1/M5/M15 zaman-projeksiyonu bu dogrulamadan ETKILENEBILIR.
- **25 yillik H1/8,5 yillik M30 orneklemi rejim-degisikligi riski tasir** (alt-donem kirilimi bu
  turde de YAPILMADI).
- **Bu turde YENIDEN hesaplanan M5/M15 baseline sayilari, 14 Temmuz raporundakiyle YAKIN ama
  BIREBIR AYNI DEGIL** (orn. H1→M5 yukselen: 14 Temmuz 15.259 giris/128,3dk-15x → bu tur 15.151
  giris/129,0dk-15x) — 5 gunluk ek veri nedeniyle beklenen kucuk sapma (16 Temmuz raporundaki
  ayni turden tutarlilik notuyla PARALEL), YONTEM DEGISIKLIGI DEGILDIR.
- Otokorelasyon/coklu-test duzeltmesi bu turde soz konusu degildir (J-Taramasi icermez); S1
  esik-gecis interpolasyonlari OLCUM DEGIL TAHMINDIR (iki olculen nokta arasi dogrusal
  interpolasyon).

---

## IZOLASYON NOTU

Bu rapor ve uretilen script yalnizca `C:\MilaYatirim\mila-yatirim-sistemi\Justin\` klasoru
icinde calisilmis, tek veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD
sembolu ham OHLCV verisi kullanilmistir. MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu,
deger veya format/sablon referans olarak ACILMAMISTIR. Script yapisi (MT5 baglanti kalibi,
pivot/kanal algoritmasi — `detect_channels` fonksiyonu BIREBIR AYNI kod), karsilastirilabilirlik
amacli olarak BILEREK ayni-proje-ici 14/16 Temmuz scriptleriyle TUTARLI tutulmustur (izolasyon
kurali yalnizca BASKA projelerin dosya/format referansini yasaklar, ayni-proje-ici metodolojik
tutarliligi degil).

---

## STRATEJIST'E ILETIM

### OZET BULGULAR (Stratejist icin giris)
--------------------------------------
1. M1 giris-zamanlama testi olculebildi, ama 1-3 ortusen kanala dayaniyor — M1'in "daha hassas
   zamanlama" saglayip saglamadigi sorusuna guclu bir kanit SUNMUYOR (S1 esikleri M5/M15 ile
   ayni mertebede, 64-190 dk).
2. Coklu-teyit (N=2/3) ve momentum-esikli (k=0,5/1,0) tetikleri, "dokunus+hemen-devam" tanimindan
   MEKANIZMA DUZEYINDE farkli iki alternatif olarak M1/M5/M15 x H1/M30 x yukselen/alcalan
   (24 kombinasyon) uzerinde olculdu — ham sayilar yukaridaki tablolarda.
3. Her iki alternatif de giris-tetigi SAYISINI azaltir (coklu-teyit %50-89, momentum %57-90);
   momentum-esikli, S1 esik-gecis suresinde coklu-teyide gore daha tutarli bir hizlanma
   PATERNI gosteriyor (18/24 kombinasyonda kisalma) — bu bir tavsiye DEGIL, ham bir gozlem.
4. Adim 0'in (14+16 Temmuz) UC raporunun ozeti yukarida konsolide edildi — hicbir sayi
   degistirilmedi.

### DETAYLI BULGULAR
-----------------
[BULGU 1] M1 Veri Derinligi (yukarida)
[BULGU 2] M1 Giris-Zamanlama Testi — baseline tetik (yukarida)
[Alternatif Giris-Tetigi Tanimlari — coklu-teyit + momentum-esikli, M1/M5/M15 tablolari]
   (yukarida)
[Konsolide Adim-0-Ozeti] (yukarida)

### ARASTIRMA BOSLUKLARI (Henuz bilinmeyenler)
------------------------------------------
- M1 gercek veri-derinlik kok nedeni test edilmedi.
- Coklu-teyit + momentum-esikli BIRLESIMI olculmedi.
- Momentum-esikli hizlanma paterninin nedeni arastirilmadi (nedensel iddia YOK).
- Alternatif tetiklerin ic-ice alt-kanal yapisiyla etkilesimi olculmedi.
- Farkli N/k parametreleri (N=4, k=1,5 vb.) test edilmedi.

### STRATEJIST'E NOT
-----------------
Bu rapordaki hicbir bulgu "su tetigi kullan" demez. Coklu-teyit ve momentum-esikli tetikleri
sadece ham sayilarla, orijinal (dokunus+hemen-devam) tetikle YAN YANA sunulmustur — hangisinin
(veya ikisinin bir kombinasyonunun, veya baska bir mekanizmanin) Tam-Tur-1'in giris-tetiginden
GERCEKTEN mekanizma-duzeyinde ayrisan bir hipoteze donusturulecegine Stratejist karar verir.
Hatirlatma (Orkestrator'un notu geregi): Stratejist, urettigi her hipotezin Tam-Tur-1'in
"dokunus+hemen-devam" giris-tetiginden mekanizma-duzeyinde GERCEKTEN farkli oldugunu ACIKCA
teyit etmelidir ("Onceki-Turden-Ayrisma-Teyidi" bolumu, Ertan'in Cevap 1 geregi).
