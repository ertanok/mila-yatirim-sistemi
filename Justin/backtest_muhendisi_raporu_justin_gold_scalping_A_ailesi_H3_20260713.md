# BACKTEST MUHENDISI RAPORU — Justin / Gold Scalping — A Ailesi (Momentum/Trend-Following) — HIPOTEZ H3

Proje: PROJE 4 kapsaminda degil — Justin (Gold Scalping alt-hedefi), A Ailesi, Tam Tur 1
Hipotez: **H3 — "M30-Yukselen Odakli Asimetrik Filtre"** (SADECE M30 yukselen kanal, M15 giris,
YALNIZCA BUY/uzun)
Tarih: 13 Temmuz 2026
Gorev kaynagi: `gorev_backtest_muhendisi_justin_gold_scalping_A_ailesi_H3.md` (Orkestrator
cagrisi, 15:15)
Girdi: `stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md` (H3 bolumu + Backtest
Muhendisi'ne Devir Notlari 1-8, ozellikle Madde 6) — **SADECE H3 kapsanmistir, H1/H2
bolumleriyle karistirilmamalidir** (bu ikisi ayri backtest turlerinde, paralel olarak
calisilmaktadir; bu raporda H1/H2 sonuclarina ATIF YAPILMAZ, karsilastirma yapilmamistir).
Calisma dizini: yalniz `C:\MilaYatirim\Justin\` (okuma/yazma)
Kod: `bt_h3_step0_dst_check.py` (bagimsiz DST dogrulamasi), `backtest_A_ailesi_H3.py` (ana test)
Ham cikti: `bt_h3_step0_dst_check_output.json`, `backtest_A_ailesi_H3_output.json`,
`backtest_A_ailesi_H3_islem_logu_oos.csv` (havuzlanmis out-of-sample tam islem logu),
`backtest_A_ailesi_H3_islem_logu_train_foldlar.csv` (fold-bazinda train/in-sample tam islem logu)

**ONEMLI CERCEVE NOTU (Stratejist'in gorev tanimindaki gorev madde 5, governance hatirlatmasi):**
Bu rapor SADECE sayisal bulgulari sunar; hicbir bulgu "iyi/kotu/basarili/basarisiz" olarak
etiketlenmemistir — yorum ve karar Risk Analisti'ne aittir.

---

## 0) ON-KONTROL SONUCLARI (justin_backtest_onkontrol_standardi.md — TAMAMI uygulandi)

### 0a) DST / Saat-Esleme — BAGIMSIZ Dogrulama (Madde 1)

H1/H2 turlerinden **HICBIR sonuc devralinmadi** — bu tur icin ayri bir script
(`bt_h3_step0_dst_check.py`) sifirdan yazilip calistirildi, M30 ve M15 (H3'un fiilen kullandigi
iki zaman dilimi) uzerinde bagimsiz kontrol yapildi.

**(a) Canli-an capraz kontrolu:**
- Tick zamani (epoch, UTC): 2026-07-13 18:20:18 UTC
- Python sistemi (UTC): 2026-07-13 15:20:18,77 UTC → **fark: -10799,2 saniye (~ -3 saat)**
- VPS yerel sistem saati: 2026-07-13 18:20:18,77 → VPS'in isletim-sistemi saati zaten UTC+3'te
  sabit (Turkiye/TST, 2016'dan beri DST uygulanmiyor); bu, MT5 SUNUCUSUNUN da sabit oldugu
  anlamina GELMEZ — asagidaki hafta-sonu-gecis testi sunucu davranisini ayrica olcer.

**(b) Hafta-sonu-gecis (DST donum noktasi) taramasi — M30 ve M15, BAGIMSIZ tekrarlandi:**

| Gecis Tarihi | Aciklama | M30 — Once/Sonra (Cuma kapanis saati) | M30 Kayma | M15 — Once/Sonra | M15 Kayma |
|---|---|---|---|---|---|
| 2025-03-30 | AB/Kibris yaz-saatine gecis | 22 → 23 | **EVET** | 22 → 23 | **EVET** |
| 2025-10-26 | AB/Kibris kis-saatine gecis | 23 → 22/23 (karisik) | Hayir* | 23 → 22/23 (karisik) | Hayir* |
| 2026-03-29 | AB/Kibris yaz-saatine gecis (bu yil) | 22 → 23 | **EVET** | 22 → 23 | **EVET** |

*Ekim gecisinde "sonrasi" penceresinde hem 22 hem 23 saati gozlemlenmis (karisik/mod
belirsizligi) — algoritma bu durumda "kayma yok" olarak isaretliyor (en sik gorulen deger ayni
kaliyor), ama bu KESIN "kayma yok" anlamina gelmez, olcum belirsizligi olarak okunmalidir.

**SONUC (H1/H2'deki bagimsiz bulgularla TUTARLI):** MT5/XM sunucusu yil boyunca sabit bir offset
kullanmiyor, AB/Kibris DST takvimini izliyor gorunuyor (yaz GMT+3, kis GMT+2 civarinda, Ekim
gecisinde tam netlik yok). **KRITIK METODOLOJIK NOT (H3'e ozel):** asagidaki M30→M15 kanal
projeksiyonu ve tum zaman hesaplari `rates['time']` alanindaki **UTC epoch saniyeleri**
uzerinden yapilir — DST kaymasi insan-okunur SAAT ETIKETINI (orn. "Cuma kapanisi 22 mi 23 mu")
etkiler, ama epoch-farki tabanli hesaplamayi ETKILEMEZ. H3'te (H1/H2'nin aksine) herhangi bir
gun-ici-saat/seans filtresi KULLANILMADIGI icin, bu DST kaymasinin trade sinyaline dogrudan bir
etkisi YOKTUR — ama bu bir "DST yok" sonucu degildir, sadece "bu ozel mekanizma DST'ye karsi
bagisik" bulgusudur. Bagimsiz kontrolun TAM ham ciktisi: `bt_h3_step0_dst_check_output.json`.

### 0b) S1 Maliyet-Orani On-Kontrolu — GERCEK SL/TP Mesafeleriyle (Madde 2, H3'e OZEL)

M15 global maliyet bileseni (H1/H2 ile ayni formul, GERCEK/guncel veriden yeniden hesaplandi):

| Bilesen | Deger (puan) |
|---|---|
| Spread (medyan) | 27,00 |
| ATR14_M15 (medyan) | 287,71 |
| Slipaj tahmini (0,037 × ATR medyan) | 10,65 |
| **TOPLAM MALIYET** | **37,65** |

GERCEK TP mesafeleri (temsili, ATR-carpani × medyan-ATR) ile maliyet orani:

| TP carpani (×ATR14_M15) | Temsili TP (puan) | Maliyet Orani | >=15x | >=20x |
|---|---|---|---|---|
| 1,0 | 287,7 | 7,64x | Hayir | Hayir |
| 1,5 | 431,6 | 11,46x | Hayir | Hayir |
| 2,0 | 575,4 | 15,29x | **Evet** | Hayir |
| 2,5 | 719,3 | 19,11x | **Evet** | Hayir |
| 3,0 | 863,1 | 22,93x | **Evet** | **Evet** |
| 4,0 | 1150,9 | 30,57x | **Evet** | **Evet** |
| 5,0 | 1438,6 | 38,21x | **Evet** | **Evet** |

**On-kontrol karari: ANA TESTE GECILEBILIR** — TP>=2,0xATR carpanlarinin tamami (2,0/2,5/3,0/4,0/
5,0) >=15x esigini gecti. Stratejist'in bu alt-kume icin verdigi tahmini referans (M30→M15
yukselen: 15x=~4,4 saat / 20x=~7,2 saat, **interpolasyon, olcum degil**) burada GERCEK SL/TP
mesafeleriyle dogrulanmistir — asagidaki FAZ 7'de secilen konfigurasyonun (TP=5,0xATR) medyan
tutma suresi (bkz. bolum 3) bu tahminle karsilastirilabilir. **SL/TP grid'i H2'den OTOMATIK
TASINMADI** — TP grid'ine H3'e ozel olarak 5,0xATR ucu da eklendi (asagida FAZ 7'de gorulecegi
gibi grid'in TAMAMI 5,0xATR'yi secti — bu bir SINIRLAMA olarak bolum 3'te ayrica isaretlenmistir).

---

## 1) LOOK-AHEAD BIAS DOGRULAMASI

Arastirmaci'nin pivot/swing tanimi (`high[i]==max(high[i-5:i+6])`, N=5 fraktal, SAG-PENCERELI)
ileri-bakislidir — bir barin "swing" oldugu ancak **5 bar SONRA** kesinlesir. Bu script'te (H1/H2
ile AYNI gerekce ve yontem):

- 3. dokunusun geometrik olarak olustugu bar (`confirm_idx_ham`) ile kanalin **gercek-zamanli
  olarak bilindigi/kullanilabildigi bar** (`confirmed_active_idx = confirm_idx_ham + 5`)
  ACIKCA AYRISTIRILDI.
- EMA50/EMA200 ve MACD teyidi `confirmed_active_idx` barinda kontrol edilir (ham confirm
  barinda DEGIL).
- M15 giris-projeksiyonu (FAZ 3) SADECE `confirmed_active_time`'dan (M15 verisiyle kesisen kisim)
  itibaren baslar — kanalin gecmise donuk "bilinmeden once" hicbir M15 barinda giris uretilmesine
  IZIN VERILMEMISTIR.
- Kirilim (break) bilgisi de ayni sekilde `break_known_time = break_idx_zamani + bar_suresi`
  olarak MODELLENMISTIR — kirilim-bazli erken-cikis, kirilimin GERCEKTEN bilindigi andan itibaren
  uygulanir (bkz. bolum 3, FAZ 8 dogrulama ornekleri).

**Sonuc:** Look-ahead duzeltmesi kod-seviyesinde uygulanmis ve FAZ 8'deki ornek islemlerle
capraz-dogrulanmistir (bkz. bolum 3). Bu duzeltme OLMADAN calistirilan bir versiyon bu raporda
YOKTUR — yani "duzeltme oncesi vs sonrasi" fark burada raporlanmiyor (H1/H2'de de yapilmadi,
tutarli).

---

## 2) ANA TEST TASARIMI / YONTEM

**Rejim/giris-filtresi:** SADECE M30'da onaylanmis (>=3 dokunus + EMA50>EMA200 + MACD_line>
MACD_signal, onay `confirmed_active_idx` barinda kontrol) **YUKSELEN** kanal aktifken islem
dusunulur. Alcalan kanal/SELL tarafi bu script'te HIC HESAPLANMADI (H1/H2'nin aksine, sadece
"up" yonu calistirildi — mekanizma-duzeyinde asimetri, Stratejist'in tasarimi).

**Giris tetigi (H2 ile AYNI mekanik, sadece M30-yukselen+BUY'a kisitli):** M30 kanal cizgisinin
M15 projeksiyonuna bir M15 barinin kapanisi `<= 0,5xATR14_M15` toleransla dokunmasi + BIR SONRAKI
M15 barinin YUKARI kapanmasi = giris tetigi; giris = TETIKTEN BIR SONRAKI M15 barinin ACILISI
(H2'deki `exec_idx = i+2` kurali AYNEN korunmustur — dokunus barindan iki bar sonraki acilis,
look-ahead-safe).

**Cikis (H2 ile AYNI uc-kosullu sema):** hangisi ONCE gerceklesirse: (1) SL, (2) TP, (3)
kirilim-bazli erken-cikis (kanal `break_known_time`'dan sonraki ilk M15 barinin KAPANISI). Ayni
barda SL+TP AYNI ANDA gecerliyse muhafazakar varsayimla SL kazanir (H1/H2 ile ayni ilke).

**SL/TP kalibrasyonu (H3'e OZEL, H2'den otomatik tasima YOK):** SL grid = [0,5 / 0,75 / 1,0]
xATR14_M15_sinyal-barinda (H2 ile ayni grid); **TP grid H3'e OZEL genisletildi**: [1,0 / 1,5 /
2,0 / 2,5 / 3,0 / 4,0 / **5,0**] xATR — 5,0 ucu, H3'un devam-orani bulgusunun daha genis bir
hareket beklentisine izin verebilecegi dusunulerek EKLENDI (gerekce: Stratejist'in gorev
tanimindaki "TP mesafesini bu alt-kume icin AYRI kalibre edebilirsin" izni).

**Lot/risk (justin_gecmis_calisma.md, degistirilmedi):** kasa=2.000 USD (sabit, backtest boyunca
compounding UYGULANMADI — her islem sabit 2.000 USD referansiyla boyutlandirildi, bkz. bolum 5
sinirlamalar), islem-basi risk UST SINIRI = kasa × %1 = 20 USD, lot = asagi-yuvarlanmis
(20/SL_puan), taban 0,01 lot. Fiili islemlerde gozlenen lot araligi: **0,01–0,25** (SL mesafesi
islem-bazinda ATR'ye gore degistigi icin dinamik).

**COK-FOLD PURGED/EMBARGOLU WALK-FORWARD (Stratejist'in acik talebi, gorev madde 4 — H2'nin TEK
train/val/test bolunmesinden BILEREK FARKLI):**

- M15 verisi (2022-04-18 → 2026-07-13, ~4,25 yil) kronolojik **4 esit-zaman bloguna** ayrildi,
  her blok sinirinda **45 gunluk embargo** (medyan M30-yukselen kanal omru ~24,8 gun < 45,
  H1/H2 ile ayni gerekce) uygulandi:

| Blok | Baslangic | Bitis | Gun |
|---|---|---|---|
| 1 | 2022-04-18 | 2023-04-18 | 364 |
| 2 | 2023-06-02 | 2024-05-08 | 342 |
| 3 | 2024-06-22 | 2025-05-30 | 342 |
| 4 | 2025-07-14 | 2026-07-13 | 364 |

- **3 expanding-window fold** tanimlandi (Train giderek genisler, Test HER ZAMAN gorulmemis/
  sonraki blok):

| Fold | Train (in-sample) | Test (out-of-sample) |
|---|---|---|
| 1 | Blok 1 | Blok 2 |
| 2 | Blok 1+2 | Blok 3 |
| 3 | Blok 1+2+3 | Blok 4 |

- Her fold'da SL/TP **SADECE o fold'un Train blogunda** grid-tarama ile (PF'ye gore, n>=15 islem
  esigi — H2'nin n>=30 esiginden H3'un daha kucuk alt-kume orneklemine ORANTILI olarak
  DUSURULDU, bu ayarlama burada ACIKCA belirtilmistir) secildi, Test'te **TEK KEZ** uygulandi.

---

## 3) SONUCLAR

### 3.0) Onemli orneklem-buyuklugu uyarisi (once okunmali)

- M30-yukselen onaylanmis kanal sayisi (look-ahead-duzeltilmis, TUM ~8,5 yillik M30 tarihcesi):
  **29**.
- Bunlarin M15 veri araligiyla (2022-2026) KESISEN sayisi: **19** — trade-seviyesi backtest
  SADECE bu 19 kanala dayanir.
- Ham "aday-giris" (dokunus+devam) sayisi **23.055**, ama bu sayi (Arastirmaci'nin ayni uyarisiyla
  TUTARLI) **BAGIMSIZ GOZLEM SAYISI DEGILDIR** — ayni 19 kanalin icinde tekrarlanan,
  otokorelasyonlu olaylardir. Tek-pozisyon kurali uygulandiktan sonra fiilen ACILAN islem sayisi
  **2.082**'dir (havuzlanmis out-of-sample) — bu da 19 kanaldan turedigi icin istatistiksel
  bagimsizlik ACISINDAN hala 19 kanal civarinda sinirlidir. **Asagidaki PF/WR sayilari 2.082
  "islem" degil, esasen ~19 bagimsiz yapisal olayin turevleri olarak okunmalidir.**

### 3.1) Fold-bazinda sonuclar (Train=in-sample, Test=out-of-sample, TEK KEZ uygulanan)

| Fold | Train n | Train PF | Train WR | Test n | Test PF | Test WR | Secilen SL/TP |
|---|---|---|---|---|---|---|---|
| 1 | 268 | 0,8513 | 16,79% | 764 | 0,7776 | 16,23% | SL=1,0x / TP=5,0x |
| 2 | 1.032 | 0,7959 | 16,38% | 576 | 1,0340 | 18,92% | SL=1,0x / TP=5,0x |
| 3 | 1.608 | 0,8734 | 17,29% | 742 | 1,0616 | 18,46% | SL=1,0x / TP=5,0x |

**Kritik gozlem — grid-doygunlugu (sinirlama, bolum 5'te tekrarlanacak):** Her 3 fold'da,
Train-grid'deki **TUM 15 (SL×TP) hucresi** PF<1 verdi (en iyi hucre bile PF=0,85-0,87 — tam grid
`backtest_A_ailesi_H3_output.json` → `faz7_fold_sonuclari[*].grid_tarama_train` alaninda). Secim
kriteri "en yuksek PF" oldugu icin sistematik olarak grid'in EN GENIS UCU (SL=1,0x / TP=5,0x,
test edilen en genis TP) her fold'da secildi — yani secim, "karli bir konfigurasyon bulundu"
anlamina GELMEMEKTEDIR, sadece "test edilen hucreler arasinda en az kotu olan" secilmistir. Grid
5,0xATR'nin OTESINDE test EDILMEMISTIR (bkz. bolum 5, sinirlama).

**In-sample vs out-of-sample karsilastirmasi:** Train PF (0,80-0,87) ile Test PF (0,78-1,06)
arasinda BUYUK/tek-yonlu bir cokus GOZLENMEDI (klasik "train'de iyi, test'te coker" overfitting
paterni YOK) — aslinda Fold 2 ve Fold 3'te Test PF, Train PF'den HAFIFCE YUKSEK cikti. Bu,
`OVERFITTING_RISKI` flag'inin (sistem-prompt tanimi geregi) **False** olarak isaretlenmesine yol
acti — ancak bu, "edge dogrulandi" anlamina da GELMEZ: Train'in KENDISI hicbir hucrede PF>1
uretemedigi icin, Test'teki PF~1 civari degerler "zayif ama tutarli negatif/notr edge etrafinda
gurultu" ile de acikca UYUMLUDUR. Bu ayrim Risk Analisti'ne acik bicimde iletilmelidir (bolum 6).

**Fold arasi SL/TP secim tutarliligi:** 3 fold'un UCU DE ayni kombinasyonu (SL=1,0x/TP=5,0x)
secti — ancak bu tutarlilik, yukaridaki grid-doygunlugu nedeniyle **mekanik bir sonuc** olabilir
(grid'in en genis ucu HER ZAMAN en yuksek PF'yi verdigi icin, farkli donemlerde farkli
optimumlar olsa bile grid bunu ayirt edemez). Bu, "3/3 fold ayni sonuca ulasti = robust" seklinde
OKUNMAMALIDIR.

### 3.2) Havuzlanmis Out-of-Sample (3 fold'un test-bloklari birlikte, kronolojik)

| Metrik | Deger |
|---|---|
| Islem sayisi (n) | 2.082 |
| Win rate | %17,77 |
| Profit Factor | 0,9376 |
| Net kar/zarar (USD) | -2.115,56 |
| Net kar/zarar (puan) | -33.244,8 |
| Max Drawdown | **%191,94** |
| Medyan tutma suresi | 1,25 saat |
| Ortalama tutma suresi | 4,83 saat |
| P10-P90 tutma suresi | 0,0 - 14,75 saat |
| Cikis nedeni dagilimi | SL: 1.707 (%82,0) / TP: 365 (%17,5) / KIRILIM_ERKEN_CIKIS: 9 (%0,4) / VERI_SONU_ACIK: 1 |

**Max Drawdown %191,94 — KRITIK UYARI:** Bu deger, sabit 2.000 USD kasa referansiyla (compounding
UYGULANMADAN) hesaplanan running-equity uzerindeki en derin dususu ifade eder. %100'u asan bir
deger, bu islem dizisinin gercek/canli bir hesapta **hesabin sifirlanmasindan/marjin cagrisindan
SONRA da simulasyonun matematiksel olarak devam ettigi** anlamina gelir — yani gercek bir hesapta
bu dizinin tamami hic yasanamazdi (hesap cok daha once biterdi). Bu bir MUHENDISLIK
SINIRLAMASIDIR (bkz. bolum 5), bir "kotu sonuc" yorumu DEGILDIR — ama Risk Analisti'nin bu sayiyi
oldugu gibi degil, bu kisitla birlikte degerlendirmesi gerekir.

### 3.3) Devam-orani (continuation-rate) — In-Sample vs Out-of-Sample Coklu-Blok Karsilastirmasi

Stratejist'in H3'un dayandigi temel bulguya (M30-yukselen devam-orani %63-80, n=15-20) yonelik
acik talebi geregi, bu oran TEK bir train/test bolunmesine guvenilmeden, TUM M30-yukselen kanal
tarihcesi (n=29, M15-kesisimiyle SINIRLI DEGIL — daha genis n icin) 4 kronolojik esit-zaman
blogunda AYRI AYRI olculdu:

| Blok | n (kanal) | 1 gun | 3 gun | 7 gun | 14 gun |
|---|---|---|---|---|---|
| 1 | 4 | 100,0% | 75,0% | 50,0% | 25,0% |
| 2 | 7 | 57,1% | 57,1% | 71,4% | 71,4% |
| 3 | 12 | 66,7% | 66,7% | 75,0% | 66,7% |
| 4 | 6 | 66,7% | 50,0% | 60,0% | 80,0% |

(Tam veri `faz2b_devam_orani_coklu_blok` alaninda, `backtest_A_ailesi_H3_output.json` icinde
mevcuttur.)

**Ilk-yari (Blok 1+2, n=11, "daha eski/discovery-benzeri donem") vs ikinci-yari (Blok 3+4, n=18,
"daha yeni donem") toplu karsilastirma:**

| Ufuk | Ilk yari (n=11) | Ikinci yari (n=18) |
|---|---|---|
| 1 gun | 72,73% | 66,67% |
| 3 gun | 63,64% | 61,11% |
| 7 gun | 63,64% | 70,59% (n=17) |
| 14 gun | 54,55% | 70,59% (n=17) |

**Gozlem (yorum degil, ham bulgu):** Blok-bazinda oranlar %25 ile %100 arasinda genis dalgalanma
gosteriyor (ozellikle n=4 olan Blok 1'de tek bir kanalin sonucu bile oranı 25 puan degistirebilir
— bu n'lerle GUVEN ARALIGI COK GENISTIR). Ancak ilk-yari/ikinci-yari TOPLU karsilastirmasinda
oranlar (61-73% araliginda) Arastirmaci'nin orijinal bulgusuyla (%63-80) KABACA AYNI mertebede
KALIYOR — orijinal bulgunun tek bir donem-spesifik yanilsama OLMADIGINI, ama cok kesin/dar bir
araliga da sabitlenemedigini gosteriyor. **Bu bulgu, bolum 3.1-3.2'deki trade-seviyesi PF
sonuclariyla (PF~0,78-1,06, cogunlukla <=1) DOGRUDAN karsilastirilmamalidir** — devam-orani, M30
kapanis fiyatinin N gun sonraki konumunu (yon dogrulugu, buyukluk degil) olcerken, PF/WR,
M15-seviyesinde gerceklesen ozel bir giris/cikis mekanizmasinin (SL/TP/kirilim) net-maliyet-sonrasi
sonucudur — biri digerini otomatik olarak DOGRULAMAZ/CURUTMEZ, farkli sorular sorarlar.

---

## 4) ISLEM FREKANSI

| Metrik | Deger |
|---|---|
| Islem/ay (havuzlanmis OOS, ~3 yillik test penceresi uzerinden) | 54,79 |
| Islem/yil (havuzlanmis OOS) | 668,82 |
| Toplam islem (havuzlanmis OOS) | 2.082 |

**Stratejist'in beklentisiyle KARSILASTIRMA (gorev madde 5, acik talep):** Stratejist'in Tam Tur
1 raporu, H3'un "uc varyant arasinda EN DUSUK islem frekansina sahip olma ihtimali yuksek"
oldugunu tahmin etmisti (yalniz M30-yukselen + BUY alt-kumesi oldugu icin). **Bu ham islem-sayisi
acisindan DOGRULANMAMISTIR** — 668,82 islem/yil, dusuk bir frekans DEGILDIR (ayda ortalama ~55
islem). Ancak bu, bolum 3.0'daki uyariyla BIRLIKTE okunmalidir: bu 668/yil, sadece **19 bagimsiz
yapisal kanalin** icinde tekrar tekrar tetiklenen dokunus-devam olaylaridir (Arastirmaci'nin
orijinal raporundaki "giris tetigi sayisi istatistiksel guc olcusu degildir" uyarisi burada
DOGRUDAN GECERLIDIR) — YAPISAL OLAY (kanal) SAYISI acisindan H3, 29 M30-yukselen kanal/~8,5 yil
(~3,5/yil) ile digerlerinden DUSUK olabilir (bu rapor H1/H2'nin kanal sayilariyla KARSILASTIRMA
YAPMAMAKTADIR — izolasyon/atif-netligi gerekce), ama ISLEM (execution) sayisi acisindan
Stratejist'in tahmini bu backtest'te DOGRULANMAMISTIR. Bu, gorev tanimindaki "somut sayi sart"
talebine dogrudan yanittir; degerlendirme Risk Analisti'ne aittir.

---

## 5) SINIRLAMALAR (Muhendislik, bu turde COZULMEMIS)

1. **Kasa/lot sabitleme (compounding yok):** Her islemde lot, SABIT 2.000 USD referansiyla
   hesaplandi (equity buyudukce/kuculdukce lot BUYUMEDI/KUCULMEDI). Bu, `justin_gecmis_calisma.md`'
   deki "her 2.000 USD kasa = +0,01 lot" olceklendirme kuralinin **statik/tek-anlik** bir
   uygulamasidir — dinamik/equity-takipli lot olceklendirme bu turde MODELLENMEMISTIR.
2. **Max Drawdown %191,94 gercekci degil:** Yukarida (bolum 3.2) acikca belirtildigi gibi,
   simulasyon hesabin sifirlanmasini/marjin cagrisini MODELLEMEMEKTEDIR — gercek bir hesapta bu
   islem dizisinin tamami YASANAMAZDI. Gercekci bir DD olcumu icin equity-takipli/pozisyon-
   boyutu-guncellemeli bir simulasyon GEREKIR (bu turde yapilmadi).
3. **SL/TP grid'i EN GENIS UCUNDA doydu (5,0xATR):** 3 fold'un UCU DE grid'in en genis TP
   degerini (5,0xATR, ~1.439 puan) secti — daha genis bir TP'nin (6x, 7x, ...) daha iyi/kotu
   sonuc verip vermeyecegi bu turde TEST EDILMEMISTIR. Ayrica bu genis TP, medyan/p90 tutma
   surelerini (bolum 3.2: medyan 1,25 saat ama p90 14,75 saat) YUKARI CEKEREK, H2 icin
   raporlanan "scalping-tanimi gerilimi"ne benzer bir gerilim yaratabilir — bu, Stratejist'in
   gorev tanimindaki maddelerde H3 icin ACIKCA talep EDILMEMISTI, ama grid-sonucu olarak ORTAYA
   CIKTI; Risk Analisti'ne ayrica bildirilmelidir.
4. **Orneklem buyuklugu (tekrar, bolum 3.0):** Trade-seviyesi backtest 19 (M15-kesisen)
   yapisal kanala dayanir; her fold'un Train/Test blogu bunun bir alt-kumesidir (Fold 1 Test
   blogu ornegin sadece birkac kanal icerebilir). Bu, tum PF/WR/istatistik sonuclarinin GENIS
   guven araliklariyla okunmasi gerektigi anlamina gelir.
5. **Kanal cizgisi 2-nokta ile tanimlanip DONDURULMUSTUR** (refit edilmemis, H1/H2/Arastirmaci
   ile AYNI tasarim tercihi) — gercek bir analistin cizecegi esnek/refit-edilen bir trend cizgisi
   farkli sonuc verebilir, bu turde ayristirilamaz.
6. **Cross-split/cross-block kanal sizintisi kontrolu bu turde AYRICA yapilmadi** (H2'nin
   `faz5_cross_split_kanal_uyarisi` benzeri bir kontrol H3'te tekrarlanmadi) — bir kanalin
   `confirmed_active_time` ve `break_known_time`'i farkli bloklara dusuyorsa, o kanalin erken
   girisleri bir fold'un Train'inde, gec girisleri ayni fold'un Test'inde (veya bir sonraki
   fold'un Train'inde) gorunebilir; bu, "bagimsiz" test-blogu varsayimini bir miktar zayiflatan
   bir sizinti riskidir, bu turde SAYISALLASTIRILMADI.
7. **Devam-orani (bolum 3.3) ve PF/WR (bolum 3.1-3.2) FARKLI mekanizmalari olcer** (yon-dogrulugu
   proxy'si vs gercek SL/TP/maliyet-sonrasi net sonuc) — ikisi arasinda dogrudan bir matematiksel
   koprulama (biri digerinden turetilebilir mi) bu turde KURULMADI, ikisi ayri ayri raporlanmistir.
8. **DST kaymasi mekanizmaya etki etmiyor bulgusu, SADECE bu ozel (saat-of-day filtresiz)
   tasarim icin gecerlidir** — eger ileride bu hipoteze bir seans-saati filtresi eklenirse, DST
   kaymasinin o filtreye etkisi AYRICA degerlendirilmelidir.

---

## 6) RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — H3 "M30-Yukselen Odakli Asimetrik Filtre" — Kural-Tabanli — 13 Temmuz 2026

On-kontrol (Madde 1-3, justin_backtest_onkontrol_standardi.md):
  - DST: BAGIMSIZ dogrulandi (M30+M15), H1/H2 ile TUTARLI (DST kaymasi VAR, ama epoch-tabanli
    projeksiyon buna bagisik - saat-of-day filtresi bu hipotezde yok).
  - S1 maliyet-orani (GERCEK SL/TP): TP>=2,0xATR14_M15 tum carpanlari >=15x esigini gecti;
    TP>=3,0x >=20x esigini de gecti -> ANA TESTE GECILDI.
  - SL/TP: H2'den otomatik tasima YOK, H3'e ozel grid (TP ucu 5,0xATR'ye kadar genisletildi).

Egitim / In-Sample (fold-bazinda Train):
  Fold1 n=268 PF=0,8513 WR=%16,79 | Fold2 n=1.032 PF=0,7959 WR=%16,38 | Fold3 n=1.608 PF=0,8734
  WR=%17,29 -> UCU DE fold'ta grid'in HICBIR hucresi PF>1 vermedi (en iyi hucre dahi <1).

Gorulmemis Veri (3-fold expanding-window walk-forward, her Test TEK KEZ kullanildi):
  Fold1 n=764 PF=0,7776 WR=%16,23 | Fold2 n=576 PF=1,0340 WR=%18,92 | Fold3 n=742 PF=1,0616
  WR=%18,46
  Havuzlanmis OOS (3 fold birlikte): n=2.082, WR=%17,77, PF=0,9376, net=-2.115,56 USD,
  Max Drawdown=%191,94 (bkz. sinirlama madde 2 - gercekci degil, hesap sifirlanmasi
  modellenmedi).

Devam-orani (continuation-rate) coklu-blok replikasyonu (M30-yukselen, n=29, M15-kesisimiyle
sinirli degil):
  Ilk-yari (n=11): 1g=%72,7 / 3g=%63,6 / 7g=%63,6 / 14g=%54,5
  Ikinci-yari (n=18): 1g=%66,7 / 3g=%61,1 / 7g=%70,6 / 14g=%70,6
  -> Orijinal bulguyla (%63-80) KABACA AYNI mertebede, ama blok-bazinda (n=4-12) COK GENIS
  dalgalanma (bkz. bolum 3.3 tablosu).

Dikkat noktalari:
  - Orneklem: trade-seviyesi backtest SADECE 19 (M15-kesisen) yapisal kanala dayanir; 2.082
    "islem" bagimsiz gozlem SAYILAMAZ (otokorelasyonlu, ayni ~19 olayin turevi).
  - SL/TP secimi UCU DE fold'da grid'in EN GENIS UCUNU (5,0xATR) sectI - bu "3/3 fold tutarli"
    degil, "grid dogrulugu/saturasyonu" olarak okunmalidir; grid genisletilirse sonuc
    DEGISEBILIR, bu turde test EDILMEDI.
  - Islem frekansi (668,82/yil) Stratejist'in "en dusuk frekans" tahminini raw execution-sayisi
    acisindan DOGRULAMADI (kanal-sayisi acisindan hala dusuk olabilir, bu rapor bunu
    karsilastirmadi - izolasyon/atif-netligi gerekce).
  - Genis TP (5,0xATR, ~1.439 puan) tutma suresini uzatiyor (p90=14,75 saat) - H2 icin
    raporlanmis "scalping-tanimi gerilimi"ne benzer bir gerilim burada da ORTAYA CIKTI (Stratejist
    tarafindan bu hipotez icin ONCEDEN ongorulmemisti).
  - OVERFITTING_RISKI flag: HAYIR (klasik "train iyi, test coker" paterni yok - Train'in KENDISI
    zaten hicbir hucrede PF>1 uretemedi) - ama bu, dogrulanmis bir edge anlamina GELMEZ.

Governance notu: Bu, A ailesinin Tam Tur 1'idir; "Onceki-Tur-Ayrisma-Teyidi" N/A (ilk tur). H3,
H1/H2'ye gore daha dusuk guven duzeyinde (Stratejist ONCELIK: 2-Orta) tasarlanmisti; bu turun
sonucu ne olursa olsun Stratejist'in notu geregi "A ailesi" hakkinda degil, sadece "asimetrik
filtre" mekanizmasi hakkinda okunmalidir (H1/H2 ile karistirilmamali).

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H3_20260713.md
Ham veri/script: backtest_A_ailesi_H3.py, backtest_A_ailesi_H3_output.json,
bt_h3_step0_dst_check.py, bt_h3_step0_dst_check_output.json,
backtest_A_ailesi_H3_islem_logu_oos.csv, backtest_A_ailesi_H3_islem_logu_train_foldlar.csv
```

---

## 7) IZOLASYON NOTU

Bu rapor ve uretilen scriptler (`bt_h3_step0_dst_check.py`, `backtest_A_ailesi_H3.py`) yalnizca
`C:\MilaYatirim\Justin\` klasoru icinde calisilmis, tek veri kaynagi olarak dogrudan MT5/
`MetaTrader5` kutuphanesinden GOLD sembolu ham OHLCV verisi kullanilmistir. MilaGold/Lisa/Signal
GPT'ye ait hicbir dosya, bulgu, deger veya format/sablon referans olarak ACILMAMISTIR. Kanal
tespiti ve trade-simulasyon iskeleti, ayni proje icindeki H2 scriptiyle (`backtest_A_ailesi_H2.py`)
METODOLOJIK OLARAK BILEREK tutarli tutulmustur (karsilastirilabilirlik amacli — izolasyon kurali
yalniz BASKA proje dosyalarini yasaklar, ayni-proje-ici metodolojik tutarliligi degil); ancak DST
kontrolu bu tur icin BAGIMSIZ/SIFIRDAN tekrar calistirilmis, S1/SL-TP kalibrasyonu H3'e OZEL
yapilmis, ve walk-forward semasi H2'nin tek-bolunmesinden BILEREK cok-fold'a genisletilmistir
(Stratejist'in acik talebi).

---

## 8) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir, canli sisteme dokunus
YOKTUR (Justin arastirma asamasinda, canli/demo hesap henuz baglanmadi). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir (bu Backtest Muhendisi'nin gorev kapsami DISINDADIR).
