# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — HIPOTEZ 3

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: 3/4 (Backtest Muhendisi) — ANA TEST, 2. TUR (devam turu)
Tarih: 11 Temmuz 2026
Girdi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md (HIPOTEZ 3, Bolum 5)
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)
On-kontrol kodu/ciktisi: backtest_hipotez3_precheck.py / backtest_hipotez3_precheck_output.json (bu turde DEGISTIRILMEDI)
Ana test kodu: C:\MilaYatirim\Justin\backtest_hipotez3_main.py
Ham cikti (tam detay, tum senaryolar + tam islem loglari): C:\MilaYatirim\Justin\backtest_hipotez3_output.json

---

## 0) BU TURUN OZETI (dongu notu)

Bu, ayni "Hipotez 3 — Ana Test" adiminin **2. ardisik "hata"-sonrasi devam turudur**:
- 1. tekrar (gorev_id: backtest_muhendisi_20260710_2202): script yazildi/on-kontroller
  tamamlandi ama ANA TEST hic calistirilamadan kredi kesintisi ("Credit balance is too
  low") nedeniyle tur kapandi.
- 2. tekrar (gorev_id: backtest_muhendisi_20260711_0012): ~6-7 dakika calisti ama
  Write/rapor asamasina ulasamadan "hata" ile kapandi — kesin sebep bilinmiyor.

Bu turde (3. gecis) SIFIRDAN BASLANMADI. Orkestrator'un main.py incelemesinde buldugu
somut verimsizlik (STREAK-FADE senaryosunda ayni 4 streak uzunlugu icin `run_scenario`
GEREKSIZ YERE IKI KEZ cagriliyordu — birincisi ozet/IS-OOS/walk-forward/rejim istatistikleri
icin, ikincisi sirf `islem_logu_tam` alanini doldurmak icin) duzeltildi, script yeniden
calistirildi ve bu turde rapor tamamlandi.

**Onemli gozlem (Orkestrator'un olasi-timeout hipotezine iliskin):** Duzeltilmis script bu
turde MT5 baglantisindan itibaren JSON'a yazana kadar **cok kisa surede** (gozlemlenen komut
suresi dakikalar degil, saniyeler-birkac-on-saniye mertebesinde) tamamlandi — toplam 12.441
tick sorgusu (4.920'si cache-hit) dahil. Bu, bir onceki (2.) turdeki basarisizligin script'in
UZUN CALISMA SURESI/timeout'a takilmasindan kaynaklanmis olma ihtimalini ZAYIFLATIYOR (script
zaten hizli calisiyor, duzeltmeden ONCE de muhtemelen birkac dakikadan fazla surmezdi) —
kesin degil, ama bu bilgi Orkestrator'un ileride benzer bir "sebepsiz hata" ile karsilasirsa
degerlendirmesine yardimci olabilir. Bu turde herhangi bir hata OLUSMADI, dolayisiyla ayri bir
`backtest_hipotez3_hata_notu.txt` birakilmadi.

---

## 1) ON-KONTROL 1-3 SONUCLARI (AYRIK, precheck_output.json'dan tasindi — bu turde tekrar test edilmedi)

**On-Kontrol 1 — Saat-esleme/DST bagimsiz dogrulama:** TAMAMLANDI (prosedurel, 4. kez
bagimsiz dogrulandi). Canli-an capraz kontrolu: epoch-UTC-okuma 2026-07-10 22:09:16 / VPS
yerel simdi 2026-07-10 22:09:17,23 (fark 1,23 sn) → su anki (Temmuz/yaz) offset GMT+3
dogrulandi. Hafta-sonu/DST gecis taramasi (M1, 14 gecis) 2026-03-29 gecisinde acik kayma
GOSTERMEDI (M1 verisi bu donum noktasinin cogunu icermiyor, sadece 2026-03-29 sonrasi 3
kapanis saati 23 olarak goruldu) — **sonuc notu, precheck'ten degistirilmeden tasindi:** bu
bir RED/PASS esigi degil, zorunlu prosedurel dogrulamadir; SESSION_PRIMARY=15-18 filtresi kis
aylarinda fiilen 1 saat kaymis olabilir, asagidaki tum PC3/ana-test sonuclari bu bilinen
belirsizlikle birlikte yorumlanmalidir.

**On-Kontrol 2 — Coklu-karsilastirma duzeltmesi (RESMI, IS-donem verisinde bagimsiz
hesaplandi):** 48 test (BULGU3-genel 8 + BULGU3-streak 32 + BULGU4 8) uzerinde Bonferroni
(esik=0,0010417) ile **14**, FDR/Benjamini-Hochberg (tercih edilen) ile **25** hucre hayatta
kaldi. GECTI (ana teste devam icin yeterli hayatta kalan hucre var).

**On-Kontrol 3 — Gercekci-maliyet/seans-filtresi erken kontrolu:** Seans-filtreli (15-18)
IS-donem alt-orneklem testinde nihai olarak **11 hucre** hayatta kaldi, TUMU M1 (M5'te SIFIR
hucre hayatta kaldi — gorev kapsaminin "M1 birincil" beklentisiyle tutarli, M5 ana testte
KURULMADI). Hayatta kalan hucreler:
`BULGU3_genel|M1|VOL|genis`, `BULGU3_genel|M1|VOL|dar`, `BULGU3_streak|M1|VOL|genis|L5`,
`BULGU4|M1|VOL|genis`, `BULGU4|M1|VOL|dar`, `BULGU3_genel|M1|TREND|trend`,
`BULGU3_genel|M1|TREND|range`, `BULGU3_streak|M1|TREND|trend|L4`,
`BULGU3_streak|M1|TREND|trend|L5`, `BULGU4|M1|TREND|trend`, `BULGU4|M1|TREND|range`.
GECTI.

**On-Kontrol 4 — MAX_TICK_MISMATCH_SEC=60:** standart olarak kullanildi (v3 Bolum 4'te
onaylanmis deger, degistirilmedi).

**On-kontrol ozet karari (precheck_output.json):** `"ANA_TESTE_GECILEBILIR"` — bu nedenle
asagidaki ana test yurutuldu.

---

## 2) KOD DUZELTME NOTU (bu tur eklendi — Orkestrator'un verimsizlik bulgusu uygulandi)

`backtest_hipotez3_main.py` satir ~503-513'te STREAK-FADE senaryosu icin `run_scenario(...)`
ilk dongude (satir ~432-445) zaten hesaplaniyordu (`tr` degiskeni, ozet/IS-OOS/walk-forward/
rejim istatistiklerinde kullanildi) ama bu tam islem listesi ATILIYOR, dosyanin sonunda AYNI 4
streak uzunlugu (L2-5) icin `run_scenario` **ikinci kez** cagrilarak sirf `islem_logu_tam`
alani dolduruluyordu. Bu ikinci gecis mantik/sonuc acisindan GEREKSIZDI (TICK_QUOTE_CACHE
sayesinde tick-sorgu maliyeti buyuk olcude cache-hit olsa da, `simulate_trade` dongusunun
tamami Python seviyesinde tekrar calistiriliyordu).

**Uygulanan duzeltme:** ilk dongudeki `tr` listesi dogrudan `streak_results[f"L{L}"]
["islem_logu_tam"] = tr` olarak saklandi; dosyanin sonundaki ikinci `run_scenario` cagri
blogu (eski satir 503-513) tamamen SILINDI. Sinyal tanimlari, ATR/RR/oturum filtresi, maliyet
modeli veya HERHANGI bir sonuc/mantik DEGISTIRILMEDI — bu SADECE bir hiz/verimlilik
duzeltmesidir. `py_compile` ile sozdizimsel dogrulama yapildi, script sorunsuz calisti (bkz.
Bolum 0).

---

## 3) ANA TEST TASARIMI / YONTEM (degistirilmedi — main.py'nin kendi tasarimi, Stratejist'in
Hipotez 3 tanimina dayanir)

- **Populasyon:** M1, seans 15-18 (sunucu saati) — PC3'un dogruladigi TEK alt-orneklem,
  M5 kurulmadi (PC3'u gecen M5 hucresi yok).
- **3 sinyal ailesi**, HER BIRI icin TEK bir pozisyon-yonetimli (cakisan sinyal atlanir)
  simulasyon; rejim (VOL/TREND) IKINCIL/post-hoc filtre olarak AYNI islem seti uzerinde
  uygulaniyor (ayri simulasyon degil):
  1. **GENEL-FADE:** BULGU3-genel'in tradeable hali — dogu-olmayan HER barin yonune fade,
     t+1 giris (teyitsiz).
  2. **STREAK-FADE:** BULGU3-streak'in tradeable hali — N ardisik ayni-yonlu bar (N=2,3,4,5,
     Arastirmaci'nin onceden belirledigi dar tarama) sonrasi fade, t+1 giris.
  3. **BIGBAR-FADE:** BULGU4'un tradeable hali — buyuk bar (range > 1,5x causal-rolling-
     20-bar ortalama, LOOK-AHEAD YOK — istatistiksel testte kullanilan IS-subset/tam-veri
     ortalamasindan FARKLI, sadece gercek-zamanli/causal ortalama kullanildi) sonrasi fade,
     t+1 giris.
- **SL/TP:** ATR(14, M1, causal) × 0,5 (ATR_FRACTION), RR=1:1 — H1/H2 semasindan DEVAM
  ETTIRILDI (Stratejist Hipotez 3 icin yeni bir deger belirtmedi; bu bir muhendislik karari
  olarak isaretlenmistir, **Stratejist onayi gerektirir**).
- **Cikis:** "combined" (ATR TP/SL VEYA N=1 bar zaman-asimi, hangisi once) — H1/H2 ile ayni.
  Ayni barda hem SL hem TP araligina girilmisse muhafazakar varsayimla SL vuruldu sayildi.
- **Maliyet:** tick-bazli gercek bid/ask (giris) + giris-spread'inin yarisi (cikis varsayimi),
  MAX_TICK_MISMATCH_SEC=60 kontrolu dahili (H1/H2'deki kok-neden duzeltmesi zaten script
  icinde mevcuttu — bkz. Bolum 7).
- **Veri bolumu:** IS = ilk %70 (bar-index 0-69998, ~2026-03-31 → ~2026-06-10), OOS = son
  %30 (bar-index 69999-99998, ~2026-06-10 → ~2026-07-10); ayrica 6 esit-uzunlukta
  walk-forward penceresi.
- **Veri:** MT5/XM, GOLD sembolu, M1, `copy_rates_from_pos`, son 99.999 bar
  (2026-03-31 → 2026-07-10).

---

## 4) JSON OZET RAPORU

```json
{
  "hipotez_adi": "Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali - HIPOTEZ 3",
  "yaklasim_turu": "kural-tabanli (fade/ters-yon, ATR-bazli risk, rejim ikincil-filtre)",
  "test_tarihi": "2026-07-11",
  "parametreler": {
    "atr_periyodu": 14,
    "atr_fraction": 0.5,
    "rr_orani": 1.0,
    "n_bars_time": 1,
    "bigbar_carpani": 1.5,
    "range_penceresi": 20,
    "streak_uzunluklari": [2, 3, 4, 5],
    "seans_filtresi": "sunucu saati 15-18 (birincil, TEK populasyon)",
    "max_tick_mismatch_sec": 60,
    "is_fraction": 0.7,
    "walk_forward_pencere_sayisi": 6
  },
  "veri": {
    "kaynak": "MT5/XM, GOLD sembolu, copy_rates_from_pos M1",
    "baslangic": "2026-03-31",
    "bitis": "2026-07-10",
    "toplam_ornek": 99999,
    "bolum_bilgisi": "IS = ilk %70 (~2026-03-31/2026-06-10), OOS = son %30 (~2026-06-10/2026-07-10); ayrica 6 esit walk-forward penceresi"
  },
  "sonuclar_ozet": {
    "GENEL_FADE": {"toplam_islem": 7825, "win_rate": 0.4686, "profit_factor": 0.488, "net_profit_pts": -432411.09, "max_drawdown_pts": -432975.06},
    "STREAK_FADE_L2": {"toplam_islem": 4116, "win_rate": 0.4572, "profit_factor": 0.488, "net_profit_pts": -230001.80},
    "STREAK_FADE_L3": {"toplam_islem": 2140, "win_rate": 0.4659, "profit_factor": 0.483, "net_profit_pts": -120498.36},
    "STREAK_FADE_L4": {"toplam_islem": 1040, "win_rate": 0.4558, "profit_factor": 0.448, "net_profit_pts": -65000.97},
    "STREAK_FADE_L5": {"toplam_islem": 494, "win_rate": 0.4838, "profit_factor": 0.548, "net_profit_pts": -23509.93},
    "BIGBAR_FADE": {"toplam_islem": 1746, "win_rate": 0.4559, "profit_factor": 0.472, "net_profit_pts": -103134.70, "max_drawdown_pts": -102932.69}
  },
  "gorulmemis_veri_sonuclari": {
    "GENEL_FADE": {"IS_pf": 0.505, "OOS_pf": 0.447, "IS_n": 5459, "OOS_n": 2366},
    "STREAK_FADE_L2": {"IS_pf": 0.499, "OOS_pf": 0.461, "IS_n": 2881, "OOS_n": 1235},
    "STREAK_FADE_L3": {"IS_pf": 0.505, "OOS_pf": 0.429, "IS_n": 1506, "OOS_n": 634},
    "STREAK_FADE_L4": {"IS_pf": 0.501, "OOS_pf": 0.333, "IS_n": 735, "OOS_n": 305},
    "STREAK_FADE_L5": {"IS_pf": 0.580, "OOS_pf": 0.478, "IS_n": 332, "OOS_n": 162},
    "BIGBAR_FADE": {"IS_pf": 0.455, "OOS_pf": 0.517, "IS_n": 1226, "OOS_n": 520}
  },
  "kirilim_analizi": "Bolum 5'e bakiniz (walk-forward 6 pencere + rejim post-hoc VOL/TREND, her 6 senaryo icin ayri)",
  "islem_logu": "Tam log JSON dosyasinda mevcut - backtest_hipotez3_output.json -> senaryolar.{GENEL_FADE,STREAK_FADE.L2..L5,BIGBAR_FADE}.islem_logu_tam (TUM islemler, ornek degil)",
  "uyarilar": [
    "TUM_KONFIGURASYONLARDA_PROFIT_FACTOR_1_ALTINDA: 6 sinyal-ailesi/varyanti (GENEL-FADE, STREAK-FADE L2-5, BIGBAR-FADE) icin tum-donem/IS/OOS/6-pencere-walk-forward/4-rejim-post-hoc-dilimi TAMAMINDA (36+ ayri kesit) PF<1 - istisna YOK.",
    "SL_MESAFESINE_GORE_MALIYET_ORANI: ortalama toplam maliyet (~51-56 pts) ATR-bazli SL mesafesinin (0,5xATR, ortalama ~165 pts) yaklasik %31-34'u - M1 zaman diliminde tick-spread'in mutlak buyuklugu M5'e gore degismedigi icin (~51-52 pts sabit), M1'in daha kucuk ATR'si karsisinda orani yukseliyor (bkz. Bolum 6, Fiziksel Tutarlilik Notu).",
    "STREAK_L4_IS_OOS_SAPMASI: L4'te IS PF=0,501 / OOS PF=0,333 - digerlerine (L2/L3/L5, fark 0,04-0,10) gore goreceli daha genis bir IS-OOS sapmasi (0,168); n=305 OOS orneklem yorumlanabilir ama tek basina karar dayanagi degil. Yine de IS zaten <1 oldugu icin bu bir 'karli-gorunup-sonra-cakma' overfitting deseni DEGIL, mevcut olumsuz sonucun pekismesidir.",
    "SAAT_ESLEME_UYARISI: precheck'teki DST bulgusu (kis aylarinda 15-18 filtresi fiilen 1 saat kaymis olabilir) bu ana testte de gecerlidir, ayrica tekrarlanmadi.",
    "MALIYET_SIMULASYONU_SINIRI: giris tarafi gercek tick (bid/ask), cikis tarafi giris-spread'inin yarisi varsayimi - tam cift-tarafli tick simulasyonu degil (H1/H2 ile ayni sinir)."
  ]
}
```

---

## 5) DETAYLI KIRILIM TABLOLARI

### 5.1 Tum-Donem / IS / OOS Ozeti (6 senaryo)

| Senaryo | Islem (tum) | Win% (tum) | PF (tum) | IS n/PF | OOS n/PF |
|---|---|---|---|---|---|
| GENEL-FADE | 7825 | 46,86 | 0,488 | 5459 / 0,505 | 2366 / 0,447 |
| STREAK-FADE L2 | 4116 | 45,72 | 0,488 | 2881 / 0,499 | 1235 / 0,461 |
| STREAK-FADE L3 | 2140 | 46,59 | 0,483 | 1506 / 0,505 | 634 / 0,429 |
| STREAK-FADE L4 | 1040 | 45,58 | 0,448 | 735 / 0,501 | 305 / 0,333 |
| STREAK-FADE L5 | 494 | 48,38 | 0,548 | 332 / 0,580 | 162 / 0,478 |
| BIGBAR-FADE | 1746 | 45,59 | 0,472 | 1226 / 0,455 | 520 / 0,517 |

Not: 6 senaryonun TAMAMINDA hem tum-donem hem IS hem OOS PF **1'in altinda** (araligi
0,333-0,580). BIGBAR-FADE'de OOS>IS (0,517>0,455) haric tum senaryolarda OOS<IS (hafif
kotulesme) — ama IS zaten <1 oldugu icin bu bir "IS'te karli, OOS'ta cakiyor" deseni degil.

### 5.2 Walk-Forward (6 esit pencere, ~2,8-3 hafta/pencere — populasyon M1/seans-15-18-
filtreli oldugu icin toplam donem 2026-03-31→2026-07-10 gibi H1/H2'den daha kisa; pencere
sayisi Stratejist/onceki-turlerin standardiyla ayni tutuldu, WF_FOLDS=6)

**GENEL-FADE:**

| Pencere | Tarih | Islem | Win% | PF | Net (pts) |
|---|---|---|---|---|---|
| 1 | 2026-03-31 / 2026-04-17 | 1277 | 48,71 | 0,597 | -60.472,53 |
| 2 | 2026-04-17 / 2026-05-05 | 1288 | 45,57 | 0,469 | -76.084,53 |
| 3 | 2026-05-05 / 2026-05-21 | 1295 | 47,41 | 0,483 | -71.533,27 |
| 4 | 2026-05-21 / 2026-06-08 | 1280 | 46,17 | 0,447 | -70.011,57 |
| 5 | 2026-06-08 / 2026-06-24 | 1370 | 47,88 | 0,473 | -78.808,95 |
| 6 | 2026-06-24 / 2026-07-10 | 1315 | 45,40 | 0,446 | -75.500,24 |

**BIGBAR-FADE:**

| Pencere | Tarih | Islem | Win% | PF | Net (pts) |
|---|---|---|---|---|---|
| 1 | 2026-03-31 / 2026-04-17 | 291 | 48,11 | 0,567 | -15.020,54 |
| 2 | 2026-04-17 / 2026-05-05 | 272 | 46,32 | 0,464 | -16.472,67 |
| 3 | 2026-05-05 / 2026-05-21 | 284 | 42,25 | 0,373 | -21.869,72 |
| 4 | 2026-05-21 / 2026-06-08 | 309 | 42,39 | 0,407 | -19.755,07 |
| 5 | 2026-06-08 / 2026-06-24 | 300 | 48,00 | 0,512 | -15.970,49 |
| 6 | 2026-06-24 / 2026-07-10 | 290 | 46,55 | 0,516 | -14.046,21 |

**STREAK-FADE (L2-L5, PF per pencere):**

| Pencere | L2 (n/PF) | L3 (n/PF) | L4 (n/PF) | L5 (n/PF) |
|---|---|---|---|---|
| 1 | 687 / 0,627 | 362 / 0,615 | 162 / 0,611 | 77 / 0,624 |
| 2 | 703 / 0,468 | 374 / 0,592 | 178 / 0,481 | 78 / 0,596 |
| 3 | 664 / 0,467 | 341 / 0,380 | 177 / 0,442 | 77 / 0,622 |
| 4 | 663 / 0,419 | 339 / 0,415 | 170 / 0,403 | 81 / 0,526 |
| 5 | 718 / 0,514 | 367 / 0,547 | 167 / 0,465 | 82 / 0,492 |
| 6 | 681 / 0,417 | 357 / 0,354 | 186 / 0,303 | 99 / 0,446 |

Not: **36 walk-forward pencere-sonucunun TAMAMINDA (6 senaryo x 6 pencere) PF<1** —
en iyi tekil pencere dahi (GENEL-FADE pencere-1, PF=0,597) 1'in altinda kaliyor. Tek-donem
carpitmasi/anlik sansli pencere yok; sonuc zaman ustunde tutarli.

### 5.3 Rejim Kirilimi (POST-HOC — AYNI islem seti, ikincil filtre olarak)

| Senaryo | VOL-genis (n/PF) | VOL-dar (n/PF) | TREND-trend (n/PF) | TREND-range (n/PF) |
|---|---|---|---|---|
| GENEL-FADE | 4543 / 0,524 | 3282 / 0,428 | 3834 / 0,472 | 3991 / 0,504 |
| STREAK-FADE L2 | 2369 / 0,527 | 1747 / 0,425 | 1937 / 0,506 | 2179 / 0,472 |
| STREAK-FADE L3 | 1253 / 0,526 | 887 / 0,412 | 1074 / 0,458 | 1066 / 0,511 |
| STREAK-FADE L4 | 616 / 0,487 | 424 / 0,379 | 555 / 0,422 | 485 / 0,480 |
| STREAK-FADE L5 | 301 / 0,652 | 193 / 0,377 | 297 / 0,531 | 197 / 0,573 |
| BIGBAR-FADE | 1182 / 0,486 | 564 / 0,437 | 983 / 0,464 | 763 / 0,483 |

Not: **rejim-post-hoc kirilimindaki 24 hucrenin (6 senaryo x 4 rejim-etiketi) TAMAMINDA
PF<1**, en iyisi bile (STREAK-FADE L5, VOL-genis, PF=0,652, n=301) 1'in altinda. Bu, Hipotez
3'un temel iddiasiyla ("sinyal rejimden bagimsiz/uniform") YON olarak tutarli — sinyal HERHANGI
bir rejim segmentinde de karli hale gelmiyor, tek bir rejime ozgu bir "gizli edge" de yok;
ancak "uniform" olan sey burada uniform bir ZARARDIR (POST-HOC rejim filtresi, hicbir
segmentte PF'yi 1'in uzerine tasimiyor).

### 5.4 Ardisik Kazanc/Kayip Serileri

| Senaryo | Max Ardisik Kazanc | Max Ardisik Kayip |
|---|---|---|
| GENEL-FADE | 11 | 12 |
| STREAK-FADE L2 | 9 | 14 |
| STREAK-FADE L3 | 9 | 15 |
| STREAK-FADE L4 | 11 | 9 |
| STREAK-FADE L5 | 7 | 6 |
| BIGBAR-FADE | 11 | 10 |

### 5.5 Meta Atlanma Nedenleri (ozet)

| Senaryo | Seans-disi atlanan | Cakisma-atlanan |
|---|---|---|
| GENEL-FADE | 82.152 | 9.705 |
| STREAK-FADE L2 | 20.850 | 238 |
| STREAK-FADE L3 | 10.072 | 0 |
| STREAK-FADE L4 | 4.755 | 0 |
| STREAK-FADE L5 | 2.300 | 0 |
| BIGBAR-FADE | 11.175 | 452 |

("atr_yok"/"veri_sinirinda"/"tick_verisi_yok" nedenleriyle atlanan islem 0 — tam liste
`backtest_hipotez3_output.json` -> ilgili senaryo -> `meta_atlanma_nedenleri`.)

---

## 6) FIZIKSEL TUTARLILIK KONTROLU NOTU (gorev madde 3 — bu kontrolu gecmeden "calisiyor"
degerlendirmesi yapilmadi)

Ornek islem kayitlari (GENEL-FADE, ilk 3 islem) dogrudan incelendi:

```
{signal_idx: 830, atr_entry_pts: 357.71, tick_spread_pts: 52.0, giris_slipaj_pts: 0.0, toplam_maliyet_pts: 26.0, net_pts: -204.86}
{signal_idx: 833, atr_entry_pts: 321.64, tick_spread_pts: 51.0, giris_slipaj_pts: 0.0, toplam_maliyet_pts: 25.5, net_pts: 135.32}
{signal_idx: 835, atr_entry_pts: 319.36, tick_spread_pts: 52.0, giris_slipaj_pts: 52.0, toplam_maliyet_pts: 78.0, net_pts: 81.68}
```

Agrega (GENEL-FADE, n=7825): slipaj min/max/ortalama = 0,0 / 70,0 / 25,92 pts; spread
min/max/ortalama = 30,0 / 70,0 / 51,94 pts; ATR min/max/ortalama = 76,64 / 1233,36 / 330,13
pts. **Slipaj DAIMA spread'in altinda/esit kaliyor** (beklenen — slipaj, gercek ask/bid ile
teorik giris arasindaki fark, spread'i asamaz), hicbir islemde binlerce/milyonlarca puanlik
imkansiz sicrama (H2 tur2'deki kok-neden hatasindaki gibi) GORULMEDI. `tick_zaman_eslesme_
reddedilen_sayisi = 0` (12.441 sorgunun tamami MAX_TICK_MISMATCH_SEC=60 esigini gecti) —
H2'de bulunan "soguk-baslangic" tick-tarih-uyusmazligi artefakti bu turde HIC GORULMEDI (script
zaten dahili zaman-damgasi kontrolunu barindiriyordu, bu turde ekstra bir kod degisikligi
gerekmedi).

**Tek dikkat noktasi (aninda RED anlamina gelmez, Risk Analisti'ne iletiliyor):** ortalama
toplam maliyet (~51-56 pts, tum senaryolarda benzer) ATR'nin (~280-367 pts araligi, senaryoya
gore) **~%15-19'una**, ATR-bazli SL mesafesinin (0,5×ATR, ~140-185 pts araligi) ise **~%28-
34'une** denk geliyor. Bu oran H2'nin (M5, ATR~628 pts) duzeltilmis-sonrasi %3,7'sinden
belirgin YUKSEK, ama H2 tur2'deki ~6,13x (ATR'nin KAT KATI, imkansiz) buyuklugunden TAMAMEN
FARKLI bir mertebededir — **fiziksel olarak imkansiz DEGIL**, sadece M1 zaman diliminde ATR
mutlak olarak kucuk oldugu icin (tick-spread'in mutlak buyuklugu M1/M5 fark etmeksizin
~50 pts sabit kaliyor), ayni sabit maliyetin ATR'ye orani M1'de dogal olarak daha yuksek
cikiyor. **SONUC: buyuklukler fiziksel olarak TUTARLI** (slipaj≤spread, hicbir asiri/imkansiz
deger yok) — ancak bu yuksek goreceli maliyet orani (SL mesafesinin ~1/3'u) M1 scalping'in
yapisal bir maliyet-yuku ozelligi olarak Risk Analisti'ne ayrica isaretleniyor.

---

## 7) MINIMUM ORNEKLEM DEGERLENDIRMESI

Script'in dahili esik kontrolu (n<30) HICBIR senaryoda/IS-OOS kiriliminda tetiklenmedi
(`minimum_orneklem_uyarilari: []`) — en dar kesit olan STREAK-FADE L5/OOS bile n=162 ile
esigin uzerinde. Ancak rejim-post-hoc kirilimindaki en dar hucreler (orn. STREAK-FADE
L5/VOL-dar, n=193; STREAK-FADE L4/VOL-dar, n=424) goreceli kucuk kalmaya devam ediyor —
yorumlanabilir ama, gorev kapsaminin "alt-orneklem kucculmesi" uyarisiyla tutarli olarak,
tek basina karar dayanagi olarak KULLANILMAMALIDIR.

---

## 8) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali (HIPOTEZ 3) — Kural-tabanli — 2026-07-11

ON-NOT (dongu): Bu, ayni ana-test adiminin 2. ardisik "hata"-sonrasi devam turudur (1.:
kredi kesintisi / 2.: sebep belirsiz, rapor uretilemedi). Bu turde Orkestrator'un bulgusuna
gore main.py'deki GEREKSIZ bir tekrar-hesaplama (STREAK-FADE icin cifte run_scenario cagrisi)
duzeltildi, sonuc/mantik DEGISMEDI. Script bu turde hizli (dakikalar degil) tamamlandi, rapor
basariyla uretildi.

ON-KONTROL 1-3 (ayrik, precheck_output.json'dan): saat-esleme dogrulamasi TAMAMLANDI (4. kez);
coklu-karsilastirma (48 test, IS-donem) Bonferroni ile 14 / FDR ile 25 hucre hayatta kaldi;
seans-filtreli alt-orneklemde nihai 11 hucre hayatta kaldi (TUMU M1). Karar: ANA_TESTE_
GECILEBILIR.

Egitim / In-Sample (ilk %70, ~2026-03-31/2026-06-10):
  GENEL-FADE:      n=5459  PF=0,505
  STREAK-FADE L2:  n=2881  PF=0,499
  STREAK-FADE L3:  n=1506  PF=0,505
  STREAK-FADE L4:  n=735   PF=0,501
  STREAK-FADE L5:  n=332   PF=0,580
  BIGBAR-FADE:     n=1226  PF=0,455

Gorulmemis Veri (OOS, son %30, ~2026-06-10/2026-07-10):
  GENEL-FADE:      n=2366  PF=0,447
  STREAK-FADE L2:  n=1235  PF=0,461
  STREAK-FADE L3:  n=634   PF=0,429
  STREAK-FADE L4:  n=305   PF=0,333
  STREAK-FADE L5:  n=162   PF=0,478
  BIGBAR-FADE:     n=520   PF=0,517

Walk-Forward (6 pencere, ~3,5 ay toplam): 6 senaryo x 6 pencere = 36 kesitin TAMAMINDA
  PF<1 (araligi 0,303-0,627).

Rejim-Post-Hoc (VOL genis/dar, TREND trend/range, AYNI islem seti uzerinde ikincil filtre):
  6 senaryo x 4 rejim-etiketi = 24 hucrenin TAMAMINDA PF<1 (araligi 0,377-0,652).

Dikkat noktalari:
  - TUM KONFIGURASYONLARDA PROFIT FACTOR 1'IN ALTINDA: tum-donem/IS/OOS/walk-forward/
    rejim-post-hoc dahil TOPLAM 60'tan fazla ayri kesitin (6 senaryo x [tum-donem+IS+OOS+
    6-WF+4-rejim]) HICBIRINDE PF>=1 gozlemlenmedi — istisna yok.
  - STREAK_L4_IS_OOS_SAPMASI: L4'te IS PF=0,501 / OOS PF=0,333 (fark 0,168) - digerlerine
    (0,04-0,10 araligi) gore goreceli daha genis; ancak IS zaten <1 oldugu icin bir "karli-
    gorunup-cakma" (klasik overfitting) deseni degil, mevcut olumsuz sonucun pekismesi olarak
    yorumlanmali - n=305 (OOS) tek basina karar dayanagi degil.
  - MALIYET/ATR ORANI: ortalama toplam maliyet ATR'nin ~%15-19'u, ATR-bazli SL mesafesinin
    ~%28-34'u - fiziksel olarak imkansiz DEGIL (slipaj her zaman spread'in altinda kaliyor,
    tick-zaman-uyusmazligi reddi=0) ama M1 scalping'in yapisal olarak yuksek goreceli
    maliyet-yuku tasidigini isaret ediyor (H2/M5'in ~%3,7'sinden belirgin yuksek).
  - SAAT ESLEME: precheck'teki DST bulgusu (kis aylarinda SESSION_PRIMARY=15-18 fiilen 1
    saat kaymis olabilir) bu ana testte de gecerlidir; veri araligi (2026-03-31→2026-07-10)
    zaten yaz/DST-donemi-ici oldugu icin bu turde ek bir DST-gecis-donemi testte
    GOZLEMLENMEDI (ilgisiz), ama gelecekteki kis-donemi genisletmelerinde dikkate alinmali.
  - Maliyet simulasyonu SINIRI: giris tarafi gercek tick (bid/ask), cikis tarafi giris-
    spread'inin yarisi varsayimi (tam cift-tarafli tick simulasyonu degil, H1/H2/H3 ile ayni
    sinir).
  - SL/TP semasi (ATR14x0,5, RR=1:1) Stratejist'in Hipotez-3-ozel bir degeri
    belirtmemesi nedeniyle H1/H2'den TASINDI - bu bir muhendislik karari olarak
    isaretlenmistir, Stratejist onayi gerektirir.
  - Minimum orneklem: dahili n<30 esigi hicbir kesitte tetiklenmedi; en dar rejim-post-hoc
    hucreleri (n=193-424 araligi) yorumlanabilir ama tek basina karar dayanagi degil.

Detay dosya: C:\MilaYatirim\Justin\backtest_hipotez3_output.json (tam senaryo detaylari +
  tum 6 senaryonun islem_logu_tam alanlari - TUM islemler, ornek degil)
Kod: C:\MilaYatirim\Justin\backtest_hipotez3_main.py (+ backtest_hipotez3_precheck.py)
```

---

## 9) IZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, positions_status.json,
  stratejici_gold_gecmis_calisma.md vb.) ACILMADI veya referans ALINMADI.
- MilaGold'un aktif parametreleri (M5 EMA20, EMA100 streak>=13, trailing stop, 0,01 lot,
  5$/3$/5$/8$ SL/TP) hicbir sekilde kullanilmadi; SL/TP tamamen ATR(14,M1)-bazli/dinamik
  olarak Stratejist'in Hipotez 3 tasarimina gore uygulandi.
- Calisma yalniz C:\MilaYatirim\Justin\ dizininde yapildi; veri dogrudan MT5'ten
  (MetaTrader5 python kutuphanesi) cekildi. Bu turde main.py'ye uygulanan tek degisiklik
  Bolum 2'deki verimlilik duzeltmesiydi — hicbir dis/harici veri kaynagi kullanilmadi.

---

## 10) ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik
backtest + kod-verimlilik duzeltmesi, canli sisteme dokunus yok, Justin demo/arastirma
asamasinda, henuz canli hesap/kasa yok). Bu turde rapor BASARIYLA uretildi — 3. bir tur
gerekmiyor. Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
