# ARASTIRMACI RAPORU — Justin / Gold Scalping — Strateji Ailesi Plani, ADIM 0 EK TARAMA
# M5-DONEM DOGRULAMASI

Tarih: 16 Temmuz 2026
Tetikleyici: `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (14 Temmuz), "Onerilen
Sonraki Adim" bolumu, madde 3 — Arastirmaci'nin o raporda BIZZAT KENDISININ onerdigi
dogrulama adimi.
Kapsam: **Bu bir tam Yol1 pipeline turu DEGILDIR** (Adim 0 / Adim 0 EK Tarama gibi).
Arastirmaci-duzeyinde, dar kapsamli bir DOGRULAMA gorevidir — hipotez uretilmemistir,
Stratejist'e devir yoktur, sonuc DOGRUDAN Orkestrator'a raporlanmaktadir.
Veri kaynagi: XM/MT5, dogrudan `MetaTrader5` kutuphanesi, hesap #1301560935 (Demo, sunucu
"XMGlobal-MT5 6"), sunucu saati (GMT+3, UTC donusumleri bu turde `datetime.fromtimestamp(...,
tz=timezone.utc)` ile yapilmistir — DST bagimsiz dogrulanmasi bu tur icin de YAPILMAMISTIR,
bkz. Sinirlamalar).
Script: `arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama.py` → cikti:
`arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_output.json` (tum ham sayilar bu
dosyada).

---

## OZET

1. **Daha genis/farkli bir M5 GOLD donemi bu MT5 kurulumundan ELDE EDILEMEDI.** GOLD
   sembolu icin M5 verisinin gercek/toplam derinligi 100.000 bar ile SINIRLI ve 2025-02-17
   05:20:00'da (sunucu saati) BASLIYOR — bu, 14 Temmuz raporundaki ~17 aylik (2025-02-11/17
   → 2026-07-13) donemle AYNI baslangic noktasidir, sadece pencere birkac gun ileri kaymistir
   (script bu turde 2026-07-16'da calistirildi).
2. **Bu sinirin `copy_rates_from_pos`'un cagri-basina (`maxbars`) siniri DEGIL, terminal/
   hesabin GERCEK M5 gecmis derinligi oldugu DOGRUDAN OLCULEREK teyit edildi** (asagida
   Yontem/Sonuclar bolumu, "position-sayfalama testi") — 14 Temmuz raporunun bu ikisini
   ayirt edememesi bu turde giderildi.
3. **`copy_rates_range`/`copy_rates_from` ile 2025-02-17 oncesi tarih araliklari istendiginde,
   3 farkli eski donem (2010, 2019, 2024) icin, her biri 3 kez ve denemeler arasi 5 saniye
   bekleyerek test edildi — hepsinde TUTARLI sekilde sadece TEK bir bar (2025-02-17 05:20:00,
   yani gercek ilk M5 bari) donuyor.** Asenkron sunucu-indirme (retry ile veri artmasi)
   gozlenmedi.
4. **Bu M5-derinlik siniri sadece GOLD'a ozgu degil** — ayni brokerdaki farkli bir XAU-cross
   sembolu (XAUEUR) da M5'te neredeyse AYNI baslangic tarihine (2025-02-17 04:15) sahip;
   diger iki XAU-cross (XAUCNH, XAUJPY) ise daha da KISA (2025-09-17 baslangicli) M5
   gecmisine sahip. Bu, sinirin sembole ozgu bir veri sorunu degil, hesap/sunucu-genelinde
   bir M5 gecmis-senkronizasyon siniri oldugunu DUSUNDURUYOR (kanit, kesin teshis degil).
5. **Bu brokerde GOLD/USD'nin alternatif bir sembol adi (orn. "XAUUSD") YOK** — sadece "GOLD"
   mevcut; XAU-cross'lar (EUR/CNH/JPY) FARKLI enstrumanlardir (ikame degil).
6. **Sonuc:** Gorev tanimindaki 2-5. adimlar (ayni pivot/kanal metodolojisini farkli/daha
   genis bir M5 donemde tekrar calistirip S1-gecis suresini karsilastirmak) bu MT5
   kurulumuyla **YAPILAMAMAKTADIR** — veri yok. Bu, gorev tanimindaki acik talimat geregi
   ("veri yok, olcum yapilamiyor" gecerli bir arastirma sonucudur) bir BULGU olarak
   raporlanmaktadir; konu (orn. harici/farkli bir veri saglayicisi entegrasyonu) bu turde
   GENISLETILMEMISTIR.

---

## VERI DONEMI TESPITI

### a) `maxbars` terminal ayari vs gercek veri derinligi

- `mt5.terminal_info().maxbars = 100000` — bu, `copy_rates_from_pos` gibi fonksiyonlarin
  TEK BIR CAGRIDA donebilecegi azami bar sayisidir (terminal-genelinde bir ayar, sembole/
  zaman dilimine ozel degil).
- Bu turde **position-sayfalama testi** yapildi: `copy_rates_from_pos(SYMBOL, M5, 0, 99999)`
  ile en yakin 99.999 bar cekildikten SONRA, `copy_rates_from_pos(SYMBOL, M5, 99999, 99999)`
  cagrisiyla (yani "99.999 bar once"den itibaren BIR DAHA 99.999 bar iste) pencerenin
  OTESINE gecmise gidilmeye calisildi:
  - Sonuc: sadece **2 bar** donuyor (2025-02-17 05:20:00 ve 05:25:00) — 99.999 degil.
  - `pos=99998, count=5` cagrisi 3 bar donuyor (05:20, 05:25, 05:30) — yine sinirli.
  - `pos=100000, count=100` cagrisi TAMAMEN BASARISIZ oluyor (`mt5.last_error() = (-1,
    "Terminal: Call failed")`) — yani 100.000. bar ile terminal/hesabin M5 gecmisi
    TAMAMEN BITIYOR.
  - **Yorum:** eger sinir sadece `maxbars` (cagri-basina 100.000) olsaydi, position offset
    ile geriye sayfalama YAPILDIGINDA daha fazla bar donmesi BEKLENIRDI (cunku her sayfalama
    cagrisi kendi 100.000 sinirina sahip, farkli bir zaman penceresini kapsar). Bunun yerine
    tam olarak 100.000. bardan sonra veri TUKENIYOR — bu, `maxbars`in DEGIL, terminal/hesabin
    GERCEK M5 veri derinliginin (2025-02-17'den bugune, tesadufen ~100.000 bara denk gelen)
    baglayici sinir oldugunu gosteriyor.

### b) `copy_rates_range` ile eski tarih araliklari + retry/delay

- 3 eski donem test edildi: 2010-01→2010-03, 2019-01→2019-02, 2024-01→2024-03 (M5,
  `copy_rates_range`). Her biri 3 kez, denemeler arasi 5 saniye bekleyerek cagrildi (olasi
  asenkron sunucu-indirme sansi vermek icin).
- **Tum 9 denemede** (3 aralik x 3 tekrar) donen sonuc AYNI: `n_bar=1`, tek bar
  `2025-02-17 05:20:00` (yani istenen araligin ICINDE DEGIL, gercek ilk M5 barinin
  kendisi — MT5 kutuphanesinin "araliktan once veri yok" durumunda fallback olarak ilk
  mevcut bari dondurdugu gorulmustur). `mt5.last_error()` her seferinde `(1, "Success")` —
  hata koduyla degil, sessizce "en yakin/ilk veri" ile yanit veriyor.
- **Kontrol:** ayni mekanizmanin H1'de GENEL OLARAK CALISTIGI dogrulandi —
  `copy_rates_range(GOLD, H1, 2005-01-01, 2005-03-01)` 41 bar donduruyor, ilk bar
  `2005-01-03`. Yani `copy_rates_range` fonksiyonunun kendisi eski tarihlerde CALISIYOR;
  M5'e ozgu olan sey fonksiyon davranisi degil, GOLD M5 icin gercekten o kadar eski veri
  OLMAMASI.

### c) Alternatif semboller (bilgi amacli, ikame DEGIL)

| Sembol  | M5 baslangic (sunucu saati) | M5 bitis | n_bar |
|---|---|---|---|
| GOLD    | 2025-02-17 05:30:00 (bu tur, pos0 penceresi) | 2026-07-16 23:40:00 | 99.999 |
| XAUEUR  | 2025-02-17 04:15:00 | 2026-07-16 23:40:00 | 99.999 |
| XAUCNH  | 2025-09-17 11:00:00 | 2026-07-16 23:40:00 | 58.375 |
| XAUJPY  | 2025-09-17 11:10:00 | 2026-07-16 23:40:00 | 58.415 |

BAGLAM: GOLD ve XAUEUR'un M5 baslangic tarihleri BIRBIRINE COK YAKIN (ayni gun, birkac saat
fark) — bu, sinirin GOLD sembolune OZGU bir veri eksikligi degil, hesap/sunucu genelinde
paylasilan bir M5 gecmis-senkronizasyon siniri olabilecegini DUSUNDURUYOR (kesin teshis
degil, sadece gozlem). XAUCNH/XAUJPY DAHA DA KISA bir M5 gecmisine sahip (Eylul 2025), bu da
"tum XAU sembolleri ayni gunde senkronize olmus" varsayimini TAM DESTEKLEMIYOR — sembole
gore bir miktar degiskenlik var. Broker sembol listesinde GOLD/USD icin baska bir isim
(orn. "XAUUSD", "GOLD.m" vb.) YOK; sadece "GOLD" mevcut (tam liste JSON'da).

---

## YONTEM

Bu tur, 14 Temmuz raporundaki pivot/kanal + M15/M5-giris metodolojisini (swing N=5 fraktal,
>=3 dokunus, EMA50/EMA200 + MACD 12/26/9 teyidi, 0,5xATR14 tolerans) **DEGISTIRMEDEN farkli
bir M5 donem uzerinde TEKRAR CALISTIRMAYI** hedefliyordu (gorev tanimi, madde 2). Ancak madde
1'deki veri-donemi-genisletme denemesi BASARISIZ oldugu icin (yukaridaki bulgular), bu adim
**UYGULANAMADI** — mevcut M5 donemi (2025-02-17 → bugun) disinda test edilecek "farkli/daha
genis" bir M5 veri seti YOKTUR. Gorev tanimindaki acik talimat geregi ("teknik olarak
elde edilemiyorsa ... konuyu genisletme") bu asamada durulmus, harici/farkli bir veri
saglayicisi arastirmasina GIRILMEMISTIR.

---

## SONUCLAR

- **M5-donem karsilastirmasi yapilamadi** — karsilastirilacak "yeni/genis donem" verisi
  MT5 uzerinden elde edilemedi. 14 Temmuz raporundaki S1-gecis sureleri (H1→M5 ve M30→M5,
  0,9-3,7 saat araligi) bu turde ne DOGRULANDI ne de CURUTULDU — sadece bu bulgunun
  dayandigi veri donemini GENISLETME denemesinin SONUCSUZ kaldigi tespit edildi.
- **Kirilganlik notu HALA GECERLI, DEGISMEDI:** 14 Temmuz raporunun isaretledigi kirilganlik
  (M5-giris bulgusunun sadece ~17 aylik/birkac trend-epizoduna dayanmasi) bu turde
  AZALTILAMADI — ayni veri seti (essasen ayni donem, sadece birkac gun ileri kaymis pencere)
  disinda bir alternatif YOKTUR bu MT5 kurulumunda.
- **Netlesen tek sey teshis:** 14 Temmuz raporunun ayirt edemedigi "`maxbars` cagri-basina
  siniri mi, yoksa gercek veri derinligi mi" sorusu bu turde CEVAPLANDI — GERCEK VERI
  DERINLIGI baglayici sinirdir (position-sayfalama testiyle dogrudan olculdu, madde a).
  Bu, "M5 verisi genisletilebilir mi" sorusuna olumsuz ama KESIN bir yanit saglar (bir
  sonraki tur icin ayni denemenin tekrarlanmasina GEREK YOKTUR, MT5 uzerinden bu hesap/
  sunucu ile M5 GOLD gecmisi 2025-02-17 oncesine GENISLETILEMEZ).

---

## SINIRLAMALAR

- **Bu bir "celiski cozuldu/cozulmedi" KARARI DEGILDIR** — sadece dogrulama-denemesi
  sonucunu ham olarak raporlamaktadir. 14 Temmuz raporundaki kirilganlik uyarisi (dar
  orneklem, ~17 ay/2-8 kanal) OLDUGU GIBI GECERLIDIR.
- **"Call failed" teshisi (pos=100000) MT5 API'sinin dokumante edilmemis bir davranisidir**
  — bu, resmi MetaTrader5 belgelerinde acikca "veri sinirina ulasildi" olarak
  tanimlanmamistir, bu turde GOZLEMLENEN bir davranistir (tutarli, 1 kez test edildi).
- **Terminal-seviyesi bir mudahale (orn. terminal ayarlarindan "grafiklerde maksimum bar
  sayisi"nin artirilmasi, terminal yeniden baslatilmasi, veya MT5 GUI'de GOLD M5 grafiginin
  manuel olarak cok geriye kaydirilip sunucudan ek gecmis indirilmesi TETIKLENMESI) bu turde
  BILEREK DENENMEDI** — bu MT5 terminal ornegi, MilaGold'un canli/demo trading agent'lari
  (`milagold_mt5_agent.py` vb.) tarafindan da AYNI ANDA kullanilmaktadir; terminal
  yeniden baslatma veya ayar degisikligi bu agent'larin calismasini KESINTIYE UGRATABILIR.
  Bu risk nedeniyle sadece salt-okunur API cagrilariyla sinirli kalinmistir. Bu, denenmemis
  ama potansiyel olarak farkli sonuc verebilecek bir yol olarak NOT EDILMEKTEDIR (Orkestrator
  karar verirse, MilaGold'dan bagimsiz ayri bir MT5 terminal ornegi/portable kurulumla
  ayrica denenebilir — bu ayri bir gorev/karar gerektirir).
- **Retry testi sadece 3 tekrar x 5 saniye (toplam ~15 sn/aralik) ile sinirlidir** — cok daha
  uzun bekleme sureleri (dakikalar/saatler) veya terminal-ici manuel grafik-kaydirma teorik
  olarak farkli sonuc verebilir; bu turde bu daha uzun/manuel yontemler test EDILMEMISTIR.
- **Hesap/sunucu-genelinde M5 senkronizasyon siniri hipotezi (GOLD + XAUEUR'un yakin
  baslangic tarihleri) KESIN TESHIS DEGILDIR** — sadece 4 sembol test edildi (GOLD, XAUEUR,
  XAUCNH, XAUJPY), farkli sonuclar (XAUCNH/XAUJPY daha kisa) bu hipotezi TAM
  DOGRULAMAMAKTADIR; kok neden (hesap olusturma tarihi, broker-sunucu veri politikasi, veya
  baska bir sebep) bu turde ARASTIRILMAMISTIR (kapsam-disi, gorev tanimi geregi
  "konuyu genisletme").
- **DST/saat-eslesme dogrulamasi bu turde YAPILMADI** (Adim 0 ve Adim 0 EK Tarama'daki ayni
  not, `justin_backtest_onkontrol_standardi.md` Madde 1 geregi tam backtest turunde ayrica
  gereklidir).

---

## IZOLASYON NOTU

Bu rapor ve uretilen script yalnizca `C:\MilaYatirim\Justin\` klasoru icinde calisilmis, tek
veri kaynagi olarak dogrudan MT5/`MetaTrader5` kutuphanesinden GOLD (ve bilgi amacli
XAUEUR/XAUCNH/XAUJPY) sembollerinin ham OHLCV/veri-varligi bilgisi kullanilmistir.
MilaGold/Lisa/Signal GPT'ye ait hicbir dosya, bulgu, deger veya format/sablon referans olarak
ACILMAMISTIR. Script yapisi, 14 Temmuz'daki ayni proje-ici script (`arastirmaci_gold_
scalping_pivot_kanal_tarama.py`) ile TUTARLI tutulmustur (karsilastirilabilirlik amacli, ayni
proje-ici metodolojik tutarlilik izolasyon ihlali degildir).
