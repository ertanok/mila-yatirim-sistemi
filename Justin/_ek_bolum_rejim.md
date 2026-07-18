# ARASTIRMACI RAPORU — Hipotez 3 On-Kosul: Rejim-Segmentli Ek Analiz (BULGU 3/4)

Proje          : PROJE 2 - Justin Stratejisi (Gold Scalping alt-hedefi)
Gorev kaynagi  : stratejici_raporu_justin_gold_scalping_20260712.md, Bolum 6 talebi
Tarih          : 12 Temmuz 2026 (rapor tamamlama turu; sayisal calisma 10 Temmuz 2026'da bitmisti)
Script/veri    : C:\MilaYatirim\Justin\research_scalping_rejim.py
                 C:\MilaYatirim\Justin\research_scalping_rejim_output.json
                 (bu turde script YENIDEN CALISTIRILMADI, MT5'e yeniden baglanilmadi -
                 mevcut JSON ciktisi markdown'a donusturuldu)
Veri kaynagi   : XM MT5, GOLD, M1 ve M5, mt5.copy_rates_from_pos ile son 99.999 bar
                 (research_scalping.py ile ayni pencere/esik)

Not (gecmis calisma durumu): Onceki tur (arastirmaci_20260710_2127) sayisal calismayi
(script + JSON) tamamlamis ama bu markdown raporu yazmadan kendini "tamamlandi" olarak
isaretlemisti. Bu tur yalniz bu eksik rapor asamasini tamamlar; analiz sifirdan
tekrarlanmamistir.

---

## 1) YONTEM OZETI

Rejim etiketleme nedensel (causal) / ileri-bakissizdir — her bar yalniz kendisi ve
GECMISI kullanilarak etiketlenir, hicbir noktada gelecek bar bilgisi kullanilmaz.

- **VOL (volatilite genisligi) etiketi:** ATR(14), bar i icin bar(i-13..i) kullanilarak
  hesaplanir (causal). ATR14[i], KENDI trailing 100-bar penceresinin (i-99..i) medyaniyla
  kiyaslanir: ATR14[i] > trailing medyan -> "genis", degilse -> "dar".
- **TREND etiketi:** Kaufman Efficiency Ratio, 20-bar — ER20[i] = |close[i]-close[i-20]| /
  toplam-mutlak-bar-degisimi(i-19..i). ER20[i], KENDI trailing 100-bar penceresinin
  medyaniyla kiyaslanir: ER20[i] > trailing medyan -> "trend", degilse -> "range".
- Esikler (ATR ve ER trailing medyanlari) SABIT/GLOBAL bir deger DEGILDIR — her bar kendi
  anlik trailing penceresinden turetilir (bkz. Bolum 7, SINIR).
- Rejim etiketi bar i'ye atanir; BULGU3/4'un orijinal mantigiyla ayni sekilde bar (i+1)'in
  yonunu tahmin etmek icin kullanilir ("bar i'de bilinen bilgiyle bar i+1 ne yapar").
- **Istatistiksel anlamlilik testi:** scipy.stats.binomtest (iki-yonlu, H0: p=0,5) +
  ki-kare uygunluk testi (df=1), alpha=0,05 — Risk Analisti'nin Hipotez 2'de uyguladigi
  yontemle AYNI.
- BULGU4 icin "buyuk bar" esigi degismedi: bar range > 1,5 x tum-orneklem ortalama range
  (research_scalping.py ile ayni tanim, degistirilmedi).

---

## 2) REJIM ETIKET DAGILIMI

### M1 (toplam 99.999 bar)
| Etiket grubu | Etiketli bar | Deger 1 | Deger 2 |
|---|---|---|---|
| VOL | 99.887 | genis: 45.564 (%45,6) | dar: 54.323 (%54,4) |
| TREND | 99.880 | trend: 49.451 (%49,5) | range: 50.429 (%50,5) |

### M5 (toplam 99.999 bar)
| Etiket grubu | Etiketli bar | Deger 1 | Deger 2 |
|---|---|---|---|
| VOL | 99.887 | genis: 50.032 (%50,0) | dar: 49.855 (%50,0) |
| TREND | 99.880 | trend: 49.392 (%49,4) | range: 50.488 (%50,6) |

GOZLEM: Her iki zaman diliminde de VOL ve TREND etiketleri kabaca yari-yariya dagiliyor
(M1 VOL'de hafif dar-agirlikli, %54,4 dar). Etiketlenemeyen bar sayisi (trailing pencere
icin yetersiz gecmis, ilk ~100-120 bar) her iki serride de ihmal edilebilir duzeyde
(99.880-99.887 / 99.999).

---

## 3) BULGU 3 — ARDISIK BAR YON DEVAMI, REJIM-SEGMENTLI

### 3.1 Genel ardisik-ikili (bar k-1 -> bar k) devam orani, rejim = bar (k-1) etiketi

| TF | Rejim grubu | Rejim | n | Ayni-yon orani | binom p | anlamli mi (a=0,05) |
|---|---|---|---|---|---|---|
| M1 | VOL | genis | 45.333 | 0,487 | 1,47e-08 | EVET |
| M1 | VOL | dar | 53.922 | 0,486 | 1,60e-10 | EVET |
| M1 | TREND | trend | 49.137 | 0,483 | 5,25e-14 | EVET |
| M1 | TREND | range | 50.111 | 0,490 | 4,98e-06 | EVET |
| M5 | VOL | genis | 49.858 | 0,494 | 0,00903 | EVET |
| M5 | VOL | dar | 49.604 | 0,492 | 0,00082 | EVET |
| M5 | TREND | trend | 49.194 | 0,493 | 0,00111 | EVET |
| M5 | TREND | range | 50.261 | 0,494 | 0,00706 | EVET |

GOZLEM: 8 rejim-segmentinin TAMAMINDA (M1+M5 x VOL-genis/dar x TREND-trend/range) ayni-yon
orani %50'nin altinda (0,483-0,494 araliginda) ve binom testine gore anlamli. Yani genel
ardisik-bar-devam-orani-%50-altinda-kalma bulgusu (BULGU3'un orijinal olcumu) her rejim
alt-kumesinde AYRI AYRI da anlamli cikiyor.

### 3.2 Streak-sonrasi devam orani (streak uzunlugu 2,3,4,5), rejim-segmentli

**M1 — VOL**
| Rejim | streak=2 | streak=3 | streak=4 | streak=5 |
|---|---|---|---|---|
| genis | n=11.429, 0,490, p=0,0300, EVET | n=5.607, 0,472, p=3,88e-05, EVET | n=2.670, 0,476, p=0,0155, EVET | n=1.308, 0,462, p=0,0062, EVET |
| dar | n=13.745, 0,480, p=3,47e-06, EVET | n=6.590, 0,477, p=1,55e-04, EVET | n=3.120, 0,487, p=0,1680, **HAYIR** | n=1.485, 0,459, p=0,0018, EVET |

**M1 — TREND**
| Rejim | streak=2 | streak=3 | streak=4 | streak=5 |
|---|---|---|---|---|
| trend | n=12.212, 0,485, p=0,0013, EVET | n=6.106, 0,466, p=9,37e-08, EVET | n=2.989, 0,472, p=0,0021, EVET | n=1.592, 0,462, p=0,0024, EVET |
| range | n=12.959, 0,484, p=2,24e-04, EVET | n=6.090, 0,484, p=0,0116, EVET | n=2.801, 0,494, p=0,5206, **HAYIR** | n=1.201, 0,459, p=0,0047, EVET |

**M5 — VOL**
| Rejim | streak=2 | streak=3 | streak=4 | streak=5 |
|---|---|---|---|---|
| genis | n=12.534, 0,492, p=0,0847, **HAYIR** | n=6.234, 0,487, p=0,0440, EVET | n=3.077, 0,467, p=3,10e-04, EVET | n=1.458, 0,503, p=0,8137, **HAYIR** |
| dar | n=12.854, 0,481, p=2,79e-05, EVET | n=6.125, 0,480, p=0,0020, EVET | n=2.901, 0,463, p=7,04e-05, EVET | n=1.323, 0,484, p=0,2482, **HAYIR** |

**M5 — TREND**
| Rejim | streak=2 | streak=3 | streak=4 | streak=5 |
|---|---|---|---|---|
| trend | n=12.293, 0,486, p=0,0015, EVET | n=6.160, 0,486, p=0,0313, EVET | n=3.164, 0,459, p=4,09e-06, EVET | n=1.585, 0,498, p=0,8802, **HAYIR** |
| range | n=13.092, 0,488, p=0,0059, EVET | n=6.198, 0,481, p=0,0033, EVET | n=2.814, 0,472, p=0,0035, EVET | n=1.196, 0,489, p=0,4698, **HAYIR** |

GOZLEM: 32 streak-alt-orneklem hucresinden (4 rejim-segmenti x 4 streak-uzunlugu x 2 TF)
7 tanesi anlamli DEGIL: M1-VOL-dar-streak4, M1-TREND-range-streak4, M5-VOL-genis-streak2,
M5-VOL-genis-streak5, M5-VOL-dar-streak5, M5-TREND-trend-streak5, M5-TREND-range-streak5.
Anlamsiz cikan 7 hucrenin 4'u streak=5 (en kucuk n) ve M5'te toplam 5 hucre anlamsiz iken
M1'de yalniz 2 hucre anlamsiz.

---

## 4) BULGU 4 — BUYUK-BAR SONRASI YON, REJIM-SEGMENTLI

| TF | Rejim grubu | Rejim | Buyuk bar (rejimde) | Yonlu cift n | Ayni-yon orani | binom p | anlamli mi |
|---|---|---|---|---|---|---|---|
| M1 | VOL | genis | 11.260 | 11.238 | 0,475 | 1,48e-07 | EVET |
| M1 | VOL | dar | 4.427 | 4.420 | 0,463 | 7,39e-07 | EVET |
| M1 | TREND | trend | 8.713 | 8.696 | 0,470 | 1,39e-08 | EVET |
| M1 | TREND | range | 6.974 | 6.962 | 0,474 | 1,87e-05 | EVET |
| M5 | VOL | genis | 11.982 | 11.974 | 0,487 | 0,00502 | EVET |
| M5 | VOL | dar | 4.503 | 4.499 | 0,485 | 0,0396 | EVET |
| M5 | TREND | trend | 9.177 | 9.171 | 0,490 | 0,0547 | **HAYIR** |
| M5 | TREND | range | 7.308 | 7.302 | 0,482 | 0,00225 | EVET |

GOZLEM: 8 rejim-segmentinden 7'sinde ayni-yon orani %50'nin altinda (0,463-0,490) ve
anlamli. Tek istisna: M5 TREND-trend rejimi (oran 0,490, p=0,0547) — alpha=0,05 esiginin
hemen ustunde, anlamli DEGIL.

---

## 5) ALT-ORNEKLEM BUYUKLUKLERI — OZET TABLO

| TF | Analiz | n araligi (4 rejim-segmenti icinde) |
|---|---|---|
| M1 | BULGU3 genel (ardisik-ikili) | 45.333 - 53.922 |
| M1 | BULGU3 streak=2 | 11.429 - 13.745 |
| M1 | BULGU3 streak=3 | 5.607 - 6.590 |
| M1 | BULGU3 streak=4 | 2.670 - 3.120 |
| M1 | BULGU3 streak=5 | 1.201 - 1.592 |
| M5 | BULGU3 genel (ardisik-ikili) | 49.194 - 50.261 |
| M5 | BULGU3 streak=2 | 12.293 - 13.092 |
| M5 | BULGU3 streak=3 | 6.090 - 6.234 |
| M5 | BULGU3 streak=4 | 2.814 - 3.164 |
| M5 | BULGU3 streak=5 | 1.196 - 1.585 |
| M1 | BULGU4 (yonlu cift n) | 4.420 - 11.238 |
| M5 | BULGU4 (yonlu cift n) | 4.499 - 11.974 |

GOZLEM: Rejim ayrimi, genel (rejimsiz) ornek buyuklugunu kabaca YARIYA indiriyor (orn. M1
toplam 99.999 bar -> VOL genis/dar alt-kumeleri 45.333/53.922). Streak uzunlugu arttikca
(2->5) n hizla kucaliyor: M1'de streak=5 n araligi 1.201-1.592, M5'te 1.196-1.585 — bu,
streak=5 hucrelerinin Bolum 3.2'deki 7 anlamsiz sonucun 4'unu olusturmasiyla ortusuyor.

---

## 6) SONUC/OZET (ham bulgu — karar degil)

- BULGU3 genel ardisik-yon-devam olcumu: 8/8 rejim-segmentinde (M1+M5, VOL-genis/dar,
  TREND-trend/range) anlamli sapma VAR (oran %50'nin altinda, p<0,05).
- BULGU3 streak-sonrasi olcum: 32 hucreden 25'inde anlamli sapma VAR, 7'sinde YOK
  (7'nin 4'u streak=5, 5'i M5'e ait).
- BULGU4 buyuk-bar-sonrasi-yon olcumu: 8 rejim-segmentinden 7'sinde anlamli sapma VAR,
  1'inde (M5 TREND-trend) YOK.
- Ozetle: olculen 3 analiz grubunun (BULGU3-genel, BULGU3-streak, BULGU4) HER BIRINDE en
  az bir rejim alt-kumesinde anlamli sapma bulundu; cogunlukta (BULGU3-genel 8/8, BULGU4
  7/8) sapma TEK bir rejime ozgu degil, olculen rejim alt-kumelerinin NEREDEYSE TAMAMINA
  yayilmis durumda.

Bu bulgunun Stratejist'in Bolum 3'teki karar noktasini ("rejim bazinda en az bir
alt-kumede anlamli sapma var mi") hangi yonde (Backtest Muhendisi'ne gecis / Hipotez 3'un
erken kapanisi) etkiledigine karar vermek Stratejist'e aittir — bu rapor yalniz olculen
sayilari raporlar.

---

## 7) SINIR

- Veri araligi: MT5 copy_rates_from_pos ile cekilen son 99.999 M1 ve son 99.999 M5 bar
  (research_scalping.py ile ayni pencere); ayrica bir tarih filtresi uygulanmadi, araligin
  takvim baslangic/bitis tarihleri script tarafinda kayitli degil.
- Rejim esikleri (ATR/ER trailing-100 medyan) SABIT degil, zamanla kayan bir esiktir — ayni
  "genis/dar" veya "trend/range" etiketi farkli donemlerde farkli mutlak ATR/ER degerlerine
  karsilik gelebilir (rolatif esik, mutlak esik degil).
- **Coklu-karsilastirma duzeltmesi (orn. Bonferroni/FDR) UYGULANMADI.** Bu turde 4 analiz
  grubu x 4-8 rejim-segmenti x (streak analizinde) 4 streak-uzunlugu olmak uzere COK
  sayida (40'in uzerinde) hipotez testi calistirildi; duzeltme yapilmadan alpha=0,05
  kullanmak, coklu-test etkisiyle bazi "anlamli" sonuclarin sans eseri anlamli cikma
  olasiligini artirir.
- Streak=5 ve bazi VOL/TREND kesisimlerinde n kuculmesi (1.196-1.592 araligi) istatistiksel
  guc kaybina yol acar; bu hucrelerdeki "anlamli degil" sonucu "gercekten fark yok" ile
  "n yetersiz, tespit edilemedi" arasinda ayrim yapmaz.
- Bu analiz yalniz GOLD (XM) M1/M5 verisine dayanmaktadir, baska sembol/timeframe'e
  genellenemez.
- **Izolasyon notu:** Bu script/analiz MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi
  okumaz/kullanmaz. Sadece ham OHLCV veri MT5'ten (dogrudan MetaTrader5 kutuphanesi)
  cekilmistir. Yeni veri kaynagi aranmamistir — ayni GOLD M1/M5 serisi, ayni pencere/esik
  (99.999 bar, 1,5x carpan) korunmustur.

---

## ARASTIRMA BOSLUKLARI (henuz bilinmeyenler)

- Coklu-test duzeltmesi yapilmamis ham p-degerleri raporlandi — duzeltilmis (orn.
  Bonferroni/FDR) sonuclarin kac hucrenin anlamliligini degistirecegi olculmedi.
- Rejim etiketleme icin alternatif esik/pencere (orn. TRAIL_WINDOW=100 disinda farkli bir
  trailing pencere, veya ATR/ER disinda farkli bir rejim gostergesi) denenmedi.
- Rejim GECISLERININ (bir rejimden digerine gecis anindaki) davranisi ayrica olculmedi —
  sadece rejim-ICI davranis raporlandi.

---

## STRATEJIST'E NOT

Bu rapordaki hicbir bulgu "Backtest Muhendisi'ne gec" veya "Hipotez 3'u kapat" demez.
Yukaridaki sayilar (8/8, 25/32, 7/8 anlamli hucre) ham gozlemdir; Stratejist Bolum 3'teki
kendi karar kuralini ("en az bir alt-kumede anlamli sapma var mi") bu sayilara uygulayarak
karar verir.
