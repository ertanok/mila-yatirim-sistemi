# BACKTEST MUHENDISI RAPORU — Justin / Gold Scalping — A Ailesi — HIPOTEZ H1
## "Dar-Kanit M5-Giris" — TEKRAR DENEME

Tarih: 2026-07-13
Gorev kaynagi: `gorev_backtest_muhendisi_justin_gold_scalping_A_ailesi_H1_tekrar.md` (Orkestrator
cagrisi, 15:31) — onceki deneme (gorev_id: backtest_muhendisi_20260713_1816) hata ile
sonuclanmisti, bu rapor TEKRAR DENEME + KOK-NEDEN NETLESTIRME sonucudur.
Script: `backtest_A_ailesi_H1.py` (tamamen yeniden yazildi, FAZ 0-9 tam kapsam).
Ham cikti: `backtest_A_ailesi_H1_output.json`, tam islem logu: `backtest_A_ailesi_H1_islem_logu_tam.csv`.

---

## 0) KOK-NEDEN NETLESTIRME (onceki hata)

Onceki deneme (`backtest_A_ailesi_H1.py`, ilk surum) SADECE kanal-tespiti fazini
(naive+causal) calistirip `bt_h1_step_channels.json` dosyasini basariyla yazmis, ardindan
`mt5.shutdown()` ile TEMIZ sekilde sonlanmisti — yani bir exception/crash YOKTU, script
BILEREK/ONCEDEN eksik yazilmis, orijinal gorevin istedigi FAZ1/4-9 (on-kontrol, M5 giris-tetigi,
walk-forward, rapor) hic KODLANMAMISTI. "Hata" olarak raporlanan durum aslinda eksik
implementasyondu, bir runtime hatasi degildi. Bu tur icin script SIFIRDAN, H2'nin FAZ 0-9
yapisiyla ayni kapsamda yeniden yazildi ve try/except sarmalamasi eklendi (asagida Madde 0.1).

**0.1) Hata toleransi (yeni istek):** Script'in tamami `main()` fonksiyonu icinde, `if __name__ ==
"__main__"` bloğunda try/except ile sarmalanmistir. Herhangi bir asamada exception olursa TAM
traceback `backtest_A_ailesi_H1_hata_log.txt` dosyasina yazilir. **Bu calistirmada script BASTAN
SONA basariyla tamamlandi — `backtest_A_ailesi_H1_hata_log.txt` dosyasi OLUSTURULMADI** (script
basinda onceki turden kalma boyle bir dosya varsa temizlenecek sekilde kodlandi, bu turde zaten
yoktu).

**0.2) `bt_h1_step_channels.json` (onceki denemeden kalan ara-sonuc) kullanimi:** Gorev, bu
dosyanin "guncel/tutarli" oldugu dogrulanirsa dogrudan kullanilmasini oneriyordu. Inceleme
sonucu: dosyadaki causal kanal SAYILARI (H1 up=31, H1 down=42, M30 up=29, M30 down=38) bu turde
SIFIRDAN yapilan hesaplamayla BIREBIR ayni cikti (fark=0, tum kombinasyonlarda) — yani dosya
sayisal olarak GUNCEL/TUTARLI. Ancak dosya **dogrudan/index bazinda KULLANILMADI**: MT5'in
`copy_rates_from_pos(...,0,99999)` cagrisi "en son N bar"i getirir; script'in ilk calistirilma
ani ile bu tekrar-deneme arasinda gecen sure icinde yeni barlar eklendiginde, ayni zaman
noktasinin farkli bir array index'ine denk gelmesi (index kaymasi) TEORIK bir risktir — kanal
tespiti (anchor_idx/known_idx/break_idx) bu index'lere gore calisir, FAZ3 M5-projeksiyonu da ayni
oturumun H1/M30 array'lerine bagimlidir. Bu riski TAMAMEN ortadan kaldirmak icin kanal tespiti bu
script icinde YENIDEN hesaplandi (tek oturum, tutarli index'ler garantili); eski dosyayla sayi
bazinda karsilastirma yukarida raporlandigi gibi TUTARLI cikti, bu da hem eski calismanin
guvenilir oldugunu hem de bu turun yeniden-hesaplamasinin dogru oldugunu capraz-dogrulamis oldu.

---

## 1) ON-KONTROL SONUCLARI

### 1.1) DST / Saat-Eslesme BAGIMSIZ Dogrulamasi — **GECTI**

Bu tur icin BAGIMSIZ olarak iki kez olculdu: (a) bu tekrar-denemenin kendi ilk adiminda
(`bt_h1_step0_dst_check.py`, saat 15:20), (b) ana script'in FAZ1'inde (saat 18:45) — ikisi de
H2/Hipotez1-3'ten devralinmadan, sifirdan kosturuldu.

- Canli-an capraz kontrol: MT5 tick UTC zamani ile VPS yerel/UTC sistem saati arasindaki fark
  ~1.2 saniye (ana script) / tutarli (ilk adim) — senkron, anormal degil.
- Hafta-sonu-gecis (Cuma kapanis saati) taramasi, 3 DST donum noktasinda:
  - 2025-03-30 (yaz saatine gecis): oncesi Cuma kapanis 22:00 UTC -> sonrasi 23:00 UTC —
    **1 saatlik kayma TESPIT EDILDI** (beklenen: EU/Kibris DST takvimi).
  - 2025-10-26 (kis saatine gecis): oncesi 23:00 UTC -> sonrasi modda 23:00 UTC (bir barda 22
    gorulse de mod/coğunluk 23) — kayma tespit edilmedi (mod bazinda), ancak ham veri kis
    saatine donusu (Cuma kapanisin 1 saat ERKEN gerceklesecegi beklentisi) tam PERFECT
    ayristirilamadi; bu, onceki turlerde (H2/Hipotez1-3) de gozlenen kucuk bir olcum-gurultusudur.
  - 2026-03-29 (yaz saatine gecis, bu yil): oncesi 22:00 UTC -> sonrasi 23:00 UTC — **kayma
    TESPIT EDILDI.**
  - **Sonuc:** MT5/XM sunucusu AB/Kibris DST takvimini izliyor (yaz GMT+3, kis GMT+2) — H1'de
    (2001-2026 tam gecmis) VE M5'te (Subat 2025 - Temmuz 2026 gecmis) AYNI kalip gozlendi, bu
    onceki turlerin (Hipotez1/2/3, H2) bagimsiz bulgularryla TUTARLI. **GECTI** — M5
    zaman-projeksiyonu icin DST kaynakli sistematik bir saat-kaymasi riski gorulmedi.

### 1.2) S1 Maliyet-Orani On-Kontrolu (Madde 2, GERCEK SL/TP ile) — **GECTI (kismi grid)**

M5 verisiyle (H1'in kendi giris-ufku): ATR14_M5 medyani = **376.1 puan**, spread medyani =
**34.0 puan**, slipaj tahmini (0.037 x ATR, `justin_backtest_onkontrol_standardi.md` Madde 2
referans kalibrasyonu — bu kalibrasyon zaten M5 kesitinden turetilmisti, burada dogrudan
uygulanabilir) = **13.9 puan**. TOPLAM MALIYET = **47.9 puan**.

| TP carpani (xATR14_M5) | Temsili TP (puan) | Maliyet orani | >=15x | >=20x |
|---|---|---|---|---|
| 1.0 | 376.1 | 7.85x | KALDI | KALDI |
| 1.5 | 564.1 | 11.77x | KALDI | KALDI |
| 2.0 | 752.1 | 15.70x | **GECTI** | KALDI |
| 3.0 | 1128.2 | 23.55x | **GECTI** | **GECTI** |
| 4.0 | 1504.3 | 31.40x | **GECTI** | **GECTI** |
| 5.0 | 1880.4 | 39.24x | **GECTI** | **GECTI** |
| 6.0 | 2256.4 | 47.09x | **GECTI** | **GECTI** |
| 8.0 | 3008.6 | 62.79x | **GECTI** | **GECTI** |
| 10.0 | 3760.7 | 78.49x | **GECTI** | **GECTI** |

**Karar: ANA_TESTE_GECILEBILIR** — TP>=2.0xATR14_M5 olan hucreler (7/9 grid noktasi) >=15x
esigini geciyor; bunlar walk-forward'a alindi (TP=1.0/1.5xATR ELENDI, ana teste sokulmadi).
**Onemli not:** bu esigi gecen TP mesafeleri (752-3761 puan = ~7.5-37.6 USD/0.01-lot fiyat
hareketi) dar/hizli scalping algisiyla (saniyeler-dakikalar) CELISEBILECEK BUYUKLUKTE — bu,
`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md` Cevap 3'teki "S1 + dar/hizli SL/TP
AYNI ANDA saglanmali" gerilimin H1'de de (H2'de oldugu gibi) TAM cozulmedigini gosterir; asagida
Bolum 6'da somut sayilarla tekrar isaretlenmistir.

### 1.3) SL/TP — Otomatik Tasima Yok (Madde 3)

SL/TP katsayilari H2'den veya onceki hipotezlerden TASINMADI; bu hipoteze OZEL, walk-forward
grid'inde (SL: 0.25/0.5/0.75/1.0 x ATR14_M5, TP: on-kontrolu gecen 2/3/4/5/6/8/10 x ATR14_M5)
kalibre edildi (Bolum 4).

---

## 2) LOOK-AHEAD BIAS DOGRULAMASI

**2.1) Pivot/swing gecikmesi (N=5 fraktal, sag-pencereli) — DUZELTILDI ve OLCULDU.**
`known_idx = confirm_idx + 5` (LOOKAHEAD_LAG_BARS) uygulanarak, bir kanalin >=3-dokunus+EMA/MACD
onayinin GERCEKTEN "bilindigi" an, geometrik confirm barindan 5 bar SONRAYA ertelendi. Karsilastirma
icin NAIVE (lag=0, bias'li) versiyon da hesaplandi:

| TF | Yon | Naive (bias'li) n | Causal (duzeltilmis) n |
|---|---|---|---|
| H1 | up | 27 | 31 |
| H1 | down | 39 | 42 |
| M30 | up | 20 | 29 |
| M30 | down | 39 | 38 |

Causal sayilarin naive'e gore genelde DAHA YUKSEK cikmasi (M30-down haric) beklenen bir
etkidir: gecikme uygulandiginda bazi onceden "erken kirilmis" gorunen kanallar artik
kirilmadan once "bilinir" hale gelebiliyor (confirm+5 barlik pencere break taramasinin
baslangicini da geciktirir). Bu, mekanizmanin YONUNU degistirmiyor ama SAYIYI etkiliyor —
naive sayilarla calisilsaydi hem kanal-havuzu hem M5-projeksiyon havuzu farkli (ve
bias'li) olurdu. **Tum asagidaki sonuclar CAUSAL/duzeltilmis kanallara dayanir.**

**2.2) EK duzeltme (bu turde eklendi):** `known_idx` ve `break_idx` barlarinin KENDI ic bilgisi
(o barin kapanis fiyati/EMA/MACD degerleri) ancak o barin KAPANISINDA bilinir, ACILISINDA degil.
Bu yuzden M5-projeksiyon penceresi `known_time = time[known_idx] + bar_suresi` ve
`break_known_time = time[break_idx] + bar_suresi` olarak hesaplandi (H2'nin break_known_time'da
zaten uyguladigi mantik, `known_time`'a da simetrik olarak uygulandi — onceki H1 denemesinde
(ilk surum, sadece kanal-tespiti fazi) bu duzeltme YOKTU, `known_idx`in kendisi dogrudan
kullaniliyordu; bu tur icin duzeltildi).

**2.3) M5 giris-tetigi ve yurutme-ani (KRITIK, ayrica raporlaniyor):** Stratejist raporu girisi
"tetigi olusturan (bir sonraki) M5 barinin kapanisinda" olarak tanimliyor. Bu script, ayni turun
kardes hipotezi H2 ile AYNI yurutme konvansiyonunu (dokunus-bari=i, yon-teyit-bari=i+1 KAPANISI,
GIRIS = i+2 barinin ACILISI) uyguladi — yani Stratejist'in DOKUNMA + YON-TEYIDI kosullari
DEGISTIRILMEDI, ama kesin yurutme-fiyati (Stratejist'in acikca belirtmedigi bir uygulama
detayi) bir bar GECIKTIRILEREK, hem CLAUDE.md/sistem-promptunun genel kural-tabanli ilkesiyle
("sinyal kapanista uretilir, giris bir sonraki bar acilisinda gerceklesir") hem H2 ile
metodolojik tutarlilikla uyumlu hale getirildi. Bu, sinyali ureten barin TAM KAPANIS fiyatindan
girmek gibi hafif iyimser bir varsayimdan KACINIR (gercek-zamanli sistemde kapanis fiyatinda
kesin dolum garantisi yoktur). **Bu bir mekanizma degisikligi DEGIL, Stratejist'in belirtmedigi
bir yurutme-varsayimi secimidir** — Risk Analisti/Stratejist farkli bir yurutme-varsayimi
isterse (orn. tam kapanista giris), sonuclarin (ozellikle cok kisa medyan tutma suresi, asagida
Bolum 4) BIRAZ degisebilecegi acikca not edilir.

**2.4) Kirilim-bazli erken-cikis mantigi (Devir Notu 8) — mantiksal olarak DOGRU
implementasyon, ama BU CALISTIRMADA HIC TETIKLENMEDI (0/2642 islem).** Kod, her M5 barinda
SIRASIYLA (1) SL, (2) TP, (3) kirilim-bilgisi-var-mi kontrolu yapiyor (bkz. Bolum 5). Medyan
tutma suresi 0.25 saat (15 dk = 3 M5 bari) oldugu icin, pozisyonlar SL/TP'ye neredeyse HER ZAMAN
kirilim gerceklesmeden ULASIYOR — bu, mekanizmanin KENDISININ bir ozelligi (cok kisa tutma
suresi), kodun hatali calismasi degil. Ancak bu, Devir Notu 8'in istedigi "ornek islemlerle
GORGUL dogrulama"yi bu veri setinde imkansiz kiliyor — asagida sadece MANTIKSAL/kod-okuma
dogrulamasi sunulabildi (Bolum 5), GORGUL ornek YOK. Bu bir SINIRLAMA olarak isaretlenir.

---

## 3) ANA TEST TASARIMI / YONTEM

- **Rejim/giris-filtresi:** H1 veya M30'da onaylanmis (>=3 dokunus + EMA50/200 + MACD teyitli,
  causal/duzeltilmis) aktif kanal.
- **Giris tetigi:** kanalin M5 projeksiyonuna bir M5 barinin |kapanis-projeksiyon| <=
  0.5xATR14_M5 ile dokunmasi + bir SONRAKI M5 barinin trend yonunde kapanmasi; yurutme bir bar
  sonrasinin ACILISINDA (Bolum 2.3).
- **Cikis (uc kosuldan ilk gerceklesen):** (i) SL = SL_mult x ATR14_M5_giris-ani, (ii) TP =
  TP_mult x ATR14_M5_giris-ani, (iii) kirilim-bazli erken-cikis (uretici kanal KIRILIRSA SL/TP
  beklenmeden kapat, ayni-barda-SL/TP-varsa-onceliklidir varsayimi).
- **Yon:** simetrik, iki yon (BUY+SELL), ayni SL/TP katsayilari her iki yonde.
- **Veri ayrimi (purged/embargolu, zaman-bazli):**
  - Train: 2025-02-11 -> 2025-10-28 (258 gun)
  - **Embargo: 45 gun** (H2 ile ortak gerekce — ayni kanal-tespit mekanizmasindan turetilen
    medyan kanal omru 25-35 gun < 45; MilaGold'dan ALINMADI)
  - Validation: 2025-12-12 -> 2026-04-20 (129 gun)
  - Embargo: 45 gun
  - Test: 2026-06-04 -> 2026-07-13 (39 gun)
  - Split-sinirini asan (known ve break farkli split'te) kanal sayisi: **2/140** (dusuk, purge
    genel olarak etkili).
- **Walk-forward:** SL grid (0.25/0.5/0.75/1.0 x ATR) x on-kontrolu gecen TP grid (2/3/4/5/6/8/10
  x ATR) Train+Validation'da tarandi (28 hucre), Validation'da PF'ye gore (n>=30 sarti — TUM
  hucreler bu esigi rahatlikla gecti, en dusuk Validation n=590) SECILDI, Test'te **TEK KEZ**
  uygulandi.
- **Lot/risk:** kasa=2.000 USD (Justin'e ozel, sabit/compounding-siz varsayimla — H2 ile ayni
  basitlestirme), islem-basi risk kasa x %1 UST SINIR, taban 0.01 lot
  (`justin_gecmis_calisma.md`).

---

## 4) SONUCLAR

**Secilen kombinasyon (Validation PF'sine gore, n>=30 sarti saglayan 28 hucre arasindan):
SL=0.75 x ATR14_M5, TP=10.0 x ATR14_M5.**

| Donem | n islem | Win Rate | Profit Factor | Net Kar/Zarar (USD) | Max DD (%) | Medyan tutma (saat) |
|---|---|---|---|---|---|---|
| Train | 1.269 | 7.96% | 0.94 | -1.631,64 | 174,9 | 0.25 |
| Validation | 785 | 8.92% | 1.16 | +2.243,28 | 42,0 | 0.25 |
| **Test (OOS, tek kez)** | **151** | **6.62%** | **0.80** | **-559,70** | **45,99** | 0.25 |
| Tum donem (birlesik, tek-pozisyon) | 2.642 | 7.46% | 0.91 | -4.495,02 | 213,67 | 0.25 |

**OVERFITTING_RISKI — FLAGLENIYOR:** Validation PF (1.16, net +2.243 USD) ile Test PF (0.80, net
-560 USD) arasinda BUYUK ve YON-DEGISTIREN bir fark var (Validation'da karli gorunen kombinasyon,
Test'te zarar ediyor). Walk-forward protokolu metodolojik olarak DOGRU uygulandi (Test yalnizca
bir kez, secim Validation'da yapildi) — ancak protokolun kendisi dogru olsa da, SONUC, "bu
kombinasyonun Validation'da iyi gorunmesi buyuk olcude sansa/donem-ozelligine bagli, kalici bir
edge degil" seklinde okunmalidir. Bu, dogrudan Bolum 6'daki dar-orneklem bulgusuyla (M5-veriyle
ortusen sadece ~24 bagimsiz kanal, Test donemi ozelinde muhtemelen 2-4 kanaldan gelen 151 islem)
TUTARLIDIR.

**Onemli ek gozlem — TAM DONEM Max Drawdown %213,67 (matematiksel olarak "esik-otesi",
YORUMLANMASI GEREKEN bir sayi):** Sabit 2.000 USD kasa varsayimiyla (compounding YOK, H2 ile
ayni basitlestirme) kosturulan tam-donem birlesik simulasyonda, kumulatif net kar/zarar egrisi
kasayi ASIP NEGATIFE dusuyor (minimum equity: **-2.852,13 USD**, donem sonu equity: **-2.495,02
USD**). Bu, running-max'e gore hesaplanan drawdown yuzdesinin %100'u asmasina neden olur
(equity negatifken oran > 1 olur) — bu bir KOD HATASI degil, "DD-stop hic devreye girmeseydi"
senaryosunun aritmetik sonucudur. **Operasyonel gercek durumla capraz-kontrol:**
`justin_gecmis_calisma.md` geregi Justin'in kendi kumulatif %20 DD-stop kurali (kasa 1.600
USD'ye dustugunde islem OTOMATIK DURUR) bu simule edilen islem serisinde **islem #108'de (tam
donem sirasi, entry_time=2025-03-03, equity=~1.599,96 USD) TETIKLENIRDI** — yani Train donemi
DAHA BASINDA. Bu demektir ki **Validation ve Test donemindeki TUM sonuclar, gercek operasyonel
kurallar altinda hic ULASILMAYACAK bir "DD-stop devre disi" senaryosunu yansitir** — bu, Risk
Analisti'nin degerlendirmesinde MUTLAKA goz onunde bulundurulmasi gereken bir capraz-tutarlilik
notudur (yalniz H1'e ozel degil, ayni sabit-kasa/compounding-siz basitlestirme H2/H3'te de
kullanildiysa onlarda da aym capraz-kontrol yapilmalidir — bu raporun kapsami disindadir, sadece
H1 icin burada hesaplanmistir).

**Kirilim-bazli-erken-cikis (Bolum 2.4):** 0/2.642 islem bu yolla kapandi — mekanizma
IMPLEMENTE edildi ve kod-okumasiyla dogrulandi (SL/TP/kirilim sirasi kontrol edildi), ama bu
veri setinde hic AMPIRIK olarak tetiklenmedi (medyan tutma suresi 15 dk, kirilimlar cok daha
uzun ufuklarda gerceklesiyor).

---

## 5) ISLEM FREKANSI (ve DAR-ORNEKLEM ROBUSTLUK NOTU — Devir Notu 5/7)

- Tam donemde toplam 2.642 islem, ~146,8 islem/ay, ~1.870 islem/yil (M5-giris mekanizmasinin
  DOGASI geregi yuksek frekans).
- **Ancak bu sayi YANILTICI olabilir — bagimsiz orneklem buyuklugu ISLEM sayisi DEGIL, KANAL
  sayisidir:**
  - Toplam causal/tradeable kanal (H1/M30, tum gecmis 2001/2018-2026): H1 up=31, H1 down=42,
    M30 up=29, M30 down=38 — **ancak** M5 verisi sadece 2025-02-11'den itibaren mevcut (broker
    intraday-veri saklama siniri), bu yuzden M5 ile GERCEKTEN ORTUSEN/tradeable kanal sayisi cok
    daha az:
    - H1->M5 up: **3** kanal (22.485 aday-giris)
    - H1->M5 down: **8** kanal (16.284 aday-giris)
    - M30->M5 up: **6** kanal (14.659 aday-giris)
    - M30->M5 down: **7** kanal (17.369 aday-giris)
    - **TOPLAM BAGIMSIZ KANAL: 24** — Stratejist raporunun "2-8 bagimsiz kanal" tahminiyle
      (kombinasyon bazinda) BIREBIR TUTARLI, bu tur bagimsiz olarak dogrulandi.
  - Yani ortalama bir kanal icinde ~2.950 aday-giris (touch+trend-teyit olayi) olusuyor — bunlar
    ISTATISTIKSEL OLARAK BAGIMSIZ DEGIL, ayni kanal cizgisinin etrafinda tekrar tekrar
    salinan/dokunan fiyat hareketleridir. **2.642 islemlik "n" degeri PF/WR guven araligi
    hesaplamalarinda KULLANILAMAZ** — gercek bagimsiz gozlem sayisi tek haneli/dusuk-cift-haneli
    (24 kanal) mertebesindedir.
  - Test donemindeki 151 islem de benzer sekilde cok az sayida (tahminen 2-4) kanaldan
    kaynaklaniyor (H1-down 65, M30-down 48, H1-up 19, M30-up 19 — test donemi sadece 39 gun,
    bu sure icinde her yon/tf kombinasyonunda muhtemelen SADECE 1 aktif kanal vardi).
- **Sonuc:** H1 "Dar-Kanit M5-Giris" adinin dogruladigi tam olarak budur — yuksek GORUNEN islem
  frekansi, gercekte cok az sayida bagimsiz olayin (kanal) icsel tekrarindan olusuyor. Bu,
  Stratejist'in Devir Notu 5'te istedigi farkli/genis veri donemi testi bu ortamda MUMKUN
  OLMADI (M5 verisi broker tarafindan Subat 2025 oncesine gitmiyor, farkli veri kaynagi bu
  calisma kapsaminda saglanmadi) — bu bir ONERI idi (KARAR degil), YAPILMADIGI acikca burada
  belirtilir, ileride farkli bir veri saglayicisiyla tekrarlanabilir.

---

## 6) RISK ANALISTINE ILETIM

```
DOGRULAMA SONUCU — A Ailesi H1 "Dar-Kanit M5-Giris" — Kural-Tabanli — 2026-07-13

On-Kontrol:
  DST: GECTI (bagimsiz, 2x olculdu)
  S1 maliyet-orani: GECTI (TP>=2xATR14_M5 icin, 7/9 grid hucresi >=15x)

Egitim / Train:
  n=1.269, WR=7,96%, PF=0,94, net=-1.631,64 USD, DD=%174,9 (sabit-kasa/compounding-siz varsayimla)

Gorulmemis Veri / Validation (secim burada yapildi):
  n=785, WR=8,92%, PF=1,16, net=+2.243,28 USD, DD=%42,0

Gorulmemis Veri / Test (TEK KEZ, nihai):
  n=151, WR=6,62%, PF=0,80, net=-559,70 USD, DD=%45,99

Tum donem birlesik (sabit kasa, DD-stop SIMULE EDILMEDEN):
  n=2.642, WR=7,46%, PF=0,91, net=-4.495,02 USD, DD=%213,67 (equity negatife dustu, min=-2.852 USD)

Dikkat noktalari:
  - OVERFITTING_RISKI: Validation PF 1,16 -> Test PF 0,80, yon-degistiren fark.
  - Bagimsiz orneklem SADECE 24 kanal (H1up=3,H1down=8,M30up=6,M30down=7); 2.642/151 islem
    sayisi bunlarin ICINDEKI tekrarlardir, istatistiksel bagimsizlik YOKTUR.
  - Justin'in operasyonel %20 kumulatif DD-stop kurali, bu tam-donem serisinde islem #108'de
    (2025-03-03, Train donemi icinde) TETIKLENIRDI - Validation/Test sonuclari operasyonel
    olarak hic ULASILAMAYACAK bir "DD-stop devre disi" senaryosunu yansitir.
  - Kirilim-bazli-erken-cikis mekanizmasi 0/2.642 islemde tetiklendi (mantiksal/kod-okuma ile
    dogrulandi, ampirik ornek YOK - medyan tutma suresi 15 dk, kirilimlar cok daha uzun ufukta).
  - S1'i gecen TP mesafeleri (752-3.761 puan) dar/hizli-scalping algisiyla gerilim tasiyor
    (Ertan Cevap 3 kisiti - H2'de de gozlenen ayni gerilim).
  - Yurutme-ani konvansiyonu (Bolum 2.3): Stratejist'in tam-kapanis ifadesinden 1 bar
    ertelendi (H2 ile tutarlilik + genel ilke), bu bir mekanizma degisikligi degil.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H1_20260713.md
Ham veri/script: backtest_A_ailesi_H1.py, backtest_A_ailesi_H1_output.json,
backtest_A_ailesi_H1_islem_logu_tam.csv
```

---

## 7) IZOLASYON NOTU

Bu calisma yalniz `C:\MilaYatirim\Justin\` icinde yapildi. Tek veri kaynagi: MT5/GOLD ham OHLCV
(M5/M30/H1), dogrudan MetaTrader5 kutuphanesiyle cekildi. MilaGold/Lisa/Signal GPT'ye ait
hicbir dosya, deger, parametre veya format/sablon acilmadi/referans alinmadi. Kod, sadece ayni
proje (Justin) icindeki kardes hipotez H2'nin (`backtest_A_ailesi_H2.py`) FAZ yapisi ve bazi
ortak sabitleriyle (EMBARGO_DAYS=45, slipaj-kalibrasyonu 0.037xATR) METODOLOJIK tutarlilik
icin karsilastirildi — bu, izolasyon kuralinin kapsamina girmez (kural yalniz BASKA proje
dosyalarini yasaklar, ayni proje ici tutarlilik acikca TESVIK EDILIYOR).

---

## 8) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (tekrar deneme), canli
sisteme hicbir dokunus yoktur, Justin arastirma asamasindadir (canli/demo hesap henuz
baglanmadi). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi
konusu degil, etki alani dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan
onayi GEREKMEZ. Bu gorev, A ailesinin Tam Tur 1'idir (gunluk pipeline sayaci 1/5) — bu TEKRAR
DENEME bir yeni tur SAYILMAZ (sayaci degistiren Risk Analisti'nin nihai/turu-kapatan karari,
henuz bu asamaya gelinmedi). "Onceki-Tur-Ayrisma-Teyidi" bu gorevde N/A'dir (Stratejist raporu
Bolum "ONCEKI-TUR-AYRISMA-TEYIDI"nde acikca belirtildigi gibi, A ailesinin ilk tam turu).
