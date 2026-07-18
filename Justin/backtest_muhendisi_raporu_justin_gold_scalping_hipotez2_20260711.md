# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — HIPOTEZ 2

Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
Pipeline adimi: 3/4 (Backtest Muhendisi)
Tarih: 11 Temmuz 2026
Girdi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260711.md (HIPOTEZ 2, satir 60-119 ve 186-209)
Calisma dizini: yalniz C:\MilaYatirim\Justin\ (okuma/yazma)
Kod: C:\MilaYatirim\Justin\backtest_hipotez2.py
Ham cikti (tam detay, tum senaryolar): C:\MilaYatirim\Justin\backtest_hipotez2_output.json

Dongu notu: Bu, onceki turun (gorev_id: backtest_muhendisi_20260710_2021) "hata" ile
kapanmasinin ardindan AYNI HIPOTEZ 2 calismasini TAMAMLAYAN devam turudur. Onceki turde
script yazilip calistirilmis, ham JSON uretilmis ancak nihai rapor asamasina ulasilamadan
tur turn-sinirina takilmisti. Bu turde SIFIRDAN BASLANMADI — mevcut script okunup yalniz
Orkestrator'in sundugu supheli-bulgu (asagida bkz. bolum 2) dogrulanip duzeltildi, script
yeniden calistirildi ve nihai rapor bu turde tamamlandi.

---

## 0) SAAT ESLEME DOGRULAMASI (gorev Kapsam madde 1 — ZORUNLU, ONCE yapildi)

Bu turde de (onceki turdeki sonuc kopyalanmadan) iki bagimsiz kontrol tekrarlandi:

**(a) Canli-an capraz kontrolu:**
- Epoch-UTC-okuma: 2026-07-10 20:54:17
- VPS yerel simdi: 2026-07-10 20:54:17,53
- Fark: 0,53 saniye → su anki (Temmuz, yaz/DST donemi) offset = GMT+3 dogrulanmistir.

**(b) Hafta sonu gecis (DST) kontrolu:** Veri araligi (2025-02-11 → 2026-07-10, toplam 75
hafta-sonu gecisi) icinde 3 DST donum noktasi incelendi:

| Gecis Tarihi | Once (Cuma kapanis saati) | Sonra (Cuma kapanis saati) | Kayma Tespit Edildi mi? |
|---|---|---|---|
| 2025-03-30 | 22 (sabit) | 23 (sabit) | **EVET** |
| 2025-10-26 | 23 (sabit) | 22/23 (karisik) | Belirsiz (US-DST farkli tarihte gectigi icin karisik) |
| 2026-03-29 | 22 (sabit) | 23 (sabit) | **EVET** |

**SONUC (Hipotez 1'deki bulguyla tutarli, bagimsiz dogrulandi):** Sunucu yil boyunca sabit
GMT+3 calismiyor; AB/Kibris DST takvimini izleyen bir offset kullaniyor (yaz GMT+3, kis
muhtemelen GMT+2). Bu backtest'teki SESSION_PRIMARY=15-18 filtresi bu nedenle mevsime gore
fiilen GMT+3 (yaz) veya GMT+2 (kis) sunucu saatine denk geliyor olabilir — dogrulanmamis
varsayim, Risk Analisti'ne ayrica iletiliyor (bkz. bolum 6).

---

## 1) YONTEM / MUHENDISLIK VARSAYIMLARI (degistirilmedi — Stratejist'in tasarimi)

- **Buyuk-bar tanimi:** M5 bar range'i (high-low), oncesindeki 20 barin (bar i HARIC,
  nedensel) ortalama range'inin 1,5 katindan (BIGBAR_MULT) buyukse "buyuk bar" sayilir.
  Yon dogi degilse fade yonu belirlenir (yukari kapanan buyuk bar → SHORT fade, asagi
  kapanan → LONG fade).
- **Teyit ufku (confirm_horizon):** t+1 (teyitsiz, ana konfigurasyon), t+2 (1-bar ters-yon
  teyidi), t+3 (2-bar ters-yon teyidi) — dar tarama, esik carpani (1,5x) SABIT tutuldu
  (gorev Kapsam madde 6, overfitting guvenlik agi).
- **Giris:** teyit tamamlaninca bir sonraki bar acilisinda (look-ahead yok).
- **SL/TP:** ATR(14,M5) sinyal barindaki degeri × 0,5 (ATR_FRACTION), RR=1:1. Ayni barda
  hem SL hem TP araligina girilirse muhafazakar varsayimla SL vuruldu sayildi.
- **Cikis taramasi (gorev Kapsam madde 3):** yalniz-zaman (N=1/2/3 bar), yalniz-ATR-TP/SL
  (20-bar zorla-kapatma muhendislik siniri), combined (ATR TP/SL VEYA N=1 bar, hangisi once —
  ana konfigurasyon).
- **Seans filtresi:** birincil 15-18 (sunucu saati) vs filtresiz karsilastirmasi ayrica
  raporlandi.
- **Pozisyon yonetimi:** tek pozisyon, cakisan sinyaller atlanir (743 cakisma-atlanan, ana
  konfigurasyon).
- **Veri bolumu:** IS = ilk %70 (bar-index), OOS = son %30; ayrica 6 esit-uzunlukta
  walk-forward penceresi (~2,8 ay/pencere) — walk-forward Hipotez 1'deki hatanin
  (tek 70/30 bolmeye guvenmek) tekrarlanmamasi icin HER senaryoda kosturuldu.
- **Istatistiksel anlamlilik (gorev Kapsam madde 2, ONCE yapildi):** binom test + ki-kare
  uygunluk testi, BULGU4'un bagimsiz dogrulamasi olarak. Sonuc: M5 global reversal orani
  %50,94 (p=0,0288, anlamli), M1 global %53,15 (p<0,001, anlamli), AMA fiilen islem edilen
  alt-orneklem olan **M5 seans-15-18'de reversal orani %48,86 ve istatistiksel olarak
  ANLAMSIZ (p=0,223)** — yani nihai islem edilen populasyonda BULGU4'un ham edge'i zaten
  0,50'den anlamli sekilde sapmiyor. Bu, asagidaki net-getiri sonuclarinin neden negatif
  ciktigini once-kontrol asamasinda isaret ediyor.
- **1,0 standart lot varsayimi:** "net_profit_usd_per_lot" degerleri yalniz KIYASLAMA
  amaclidir (point=0,01, contract_size=100 → 1 puan = 1 USD/lot); gercek pozisyon
  boyutlandirma bu raporun kapsami disindadir.

---

## 2) SLIPAJ / TICK-ESLESME DUZELTME NOTU (bu tur eklendi — Orkestrator'in bulgusu dogrulandi)

**Orkestrator'in supheli-bulgu tespiti:** Onceki turun ham ciktisinda
`ANA_KONFIGURASYON.tum_donem.ortalama_giris_slipaj_pts` ≈ 3.845,76 puan olcculmustu — ayni
senaryonun `ortalama_atr_entry_pts` (≈627,71) degerinin ~6 kati; ayrica `max_drawdown_pts`
≈ -9.165.679 ve `net_profit_pts` ≈ -8.635.697 gibi fiziksel olarak imkansiz buyuklukte toplam
rakamlar (2203 islem, ortalama islem basina ~-3920 puan). Bu, tick-bazli slipajin ATR'nin
kucuk bir kesri olmasi gerektigi gercegiyle celisiyordu.

**Dogrulama (madde 1):** `get_tick_quote()` fonksiyonu incelendi. Fonksiyon
`mt5.copy_ticks_from(SYMBOL, bar_epoch, 3, mt5.COPY_TICKS_ALL)` cagirip donen ILK TICK'I
(`ticks[0]`) HICBIR ZAMAN DAMGASI KONTROLU YAPMADAN dogrudan bid/ask kaynagi olarak
kullaniyordu. Onceki turun ham log kayitlarindan (script yeniden calistirilmadan once, bu
turun basinda) alinan somut kanit:

- Islem 1 (big_bar_idx=152, entry_idx=153, **tarih 2025-02-11**, LONG, giris_teo=2886,64):
  `giris_slipaj_pts` = **156.360,0** → ima edilen "gerceklesen" ask fiyati =
  2886,64 + 156.360×0,01 = **4.450,24**. Bu fiyat seviyesi 2025-02-11'in GOLD fiyatiyla
  (~2886) degil, script'in calistirildigi ANIN (2026 Temmuz, GOLD ~4.100-4.450 araligi —
  ayni oturumda dogrudan MT5'ten okunan canli fiyatla capraz kontrol edildi: 2026-07-09
  17:49 UTC'de bid≈4.120,27) fiyat seviyesiyle tutarli.
- Islem 2 (big_bar_idx=156, entry_idx=157, ayni tarih, SHORT, giris_teo=2888,42):
  `giris_slipaj_pts` = **-156.117,0** → ima edilen bid = 2888,42 - (-156.117)×0,01 =
  **4.449,59** — yine ~2026-guncel fiyat seviyesiyle tutarli, 2025-02-11 seviyesiyle degil.

**Kok neden (dogrulandi):** `copy_ticks_from()`, script'in MT5'e YENI BAGLANDIGI/ilgili
sembolun tick gecmisinin henuz tam senkronize olmadigi "soguk baslangic" durumunda, eski
tarihli (2025-02-11) bir `from` epoch'u ile cagrildiginda GUNCEL/FARKLI-DONEMLI bir tick
donduruyor — donen tick'in KENDI zaman damgasi istenen bar anindan tutarsiz. Bu, gercek
slipaj DEGIL, bir veri-yoklugu/soguk-baslangic artefaktidir. (Not: bu turde script'i
tekrar calistirdigimda ayni cagrilar artik DOGRU tarihli tick donduruyordu — muhtemelen
onceki turlerdeki tekrarli calismalar MT5 terminalinin yerel tick onbellegini bu tarih
araligi icin isitmisti; bu YENIDEN-ORTAYA-CIKMA olasiligi nedeniyle asagidaki kalici
kod-duzeltmesi onemlidir, tek seferlik "bu turde rastlamadik" degerlendirmesi yeterli
degildir.)

**Uygulanan duzeltme:** `get_tick_quote()` artik donen ilk tick'in KENDI zaman damgasini
(`ticks[0]['time']`) istenen `bar_epoch` ile karsilastiriyor. Fark 60 saniyeyi (MAX_TICK_
MISMATCH_SEC — M5 bar genisliginin/300sn'nin beste biri, GOLD'un aktif piyasada tick
frekansi bunun cok altinda oldugu icin gercek bir tick'i reddetmeyecek kadar gevsek ama
gozlemlenen ay/yil mertebesindeki artefakti kesin yakalayacak kadar siki bir esik) asarsa
(veya negatifse) tick REDDEDiLiR, islem "tick_verisi_yok" olarak isaretlenir/disarida
birakilir (var olan `quote is None` yolu, sadece eslesme kontrolu eklendi).

**Duzeltme sonrasi dogrulama (ANA_KONFIGURASYON, tum_donem):**

| Metrik | ONCEKI (hatali) | DUZELTiLMiS |
|---|---|---|
| ortalama_giris_slipaj_pts | 3.845,76 | **23,50** |
| ortalama_atr_entry_pts | 627,71 | 627,71 |
| slipaj / ATR orani | ~6,13x (imkansiz) | **~0,037 (ATR'nin ~%3,7'si — fiziksel olarak tutarli)** |
| ortalama_toplam_maliyet_pts (spread/2 + slipaj) | 3.875,69 | **45,99** |
| net_profit_pts (2203 islem) | -8.635.697,95 | **-198.879,95** |
| max_drawdown_pts | -9.165.679,0 | **-199.059,56** |
| profit_factor | 0,867 | **0,558** |

Bu turde toplam 12.210 tick sorgusundan (2.203'u yeni cagri, gerisi cache-hit) yalniz
**2 tanesi** zaman-uyusmazligi nedeniyle reddedildi (bar_idx=57021, fark=221 sn;
bar_idx=58541, fark=280 sn — her ikisi de dusuk-likidite saatlerinde/01:05-10:05 UTC
araliginda, buyuklugu (dakikalar mertebesinde) normal bir likidite-bosluguyla tutarli,
YIL mertebesindeki eski artefaktla AYNI TURDEN DEGIL). Tam dagilim: `results.
tick_zaman_eslesme_dogrulama` (backtest_hipotez2_output.json).

**SONUC:** Duzeltme sonrasi slipaj/maliyet buyuklukleri ATR ile FIZIKSEL OLARAK TUTARLI
(ATR'nin kucuk bir kesri mertebesinde, ~%3,7-6 araliginda tum kirilimlarda) — asagidaki
tum sonuclar DUZELTiLMiS/DOGRU hesaplamaya dayanir. **Duzeltme, sonucu "daha iyi" degil
DAHA KOTU gostermistir** (PF 0,867→0,558): onceki hatali buyuk-magnitude slipaj degerleri
rastgele +/- isaretli oldugu icin toplamda kismen birbirini goturuyordu ve profit_factor'u
yapay olarak yukseltiyordu; gercek/dogru hesaplama daha dusuk bir PF ortaya cikarmistir.

---

## 3) JSON RAPORU (ANA KONFIGURASYON — DUZELTiLMiS)

```json
{
  "hipotez_adi": "Buyuk-Bar Ters-Yon/Fade - HIPOTEZ 2",
  "yaklasim_turu": "kural-tabanli (range-esikli buyuk-bar tespiti + ATR-bazli risk)",
  "test_tarihi": "2026-07-11",
  "parametreler": {
    "range_penceresi": 20,
    "bigbar_carpani": 1.5,
    "confirm_horizon": 1,
    "atr_periyodu": 14,
    "atr_fraction": 0.5,
    "rr_orani": 1.0,
    "cikis_yontemi": "combined: ATR TP/SL veya N=1 bar zaman, hangisi once",
    "seans_filtresi": "sunucu saati 15-18 (birincil)",
    "max_tick_mismatch_sec": 60
  },
  "veri": {
    "kaynak": "MT5/XM, GOLD sembolu, copy_rates_from_pos M5 (ana) + M1 (anlamlilik dogrulamasi)",
    "baslangic": "2025-02-11",
    "bitis": "2026-07-10",
    "toplam_ornek": 99999,
    "bolum_bilgisi": "IS = ilk %70 (~2025-02-11/2026-04-17, n=1533), OOS = son %30 (~2026-04-17/2026-07-10, n=670); ayrica 6 esit walk-forward penceresi"
  },
  "sonuclar": {
    "toplam_islem": 2203,
    "win_rate": 0.4103,
    "profit_factor": 0.558,
    "net_profit_usd_per_1_0_lot": -198879.95,
    "max_drawdown_pts": -199059.56,
    "ortalama_atr_entry_pts": 627.71,
    "ortalama_tick_spread_pts": 44.987,
    "ortalama_giris_slipaj_pts": 23.499,
    "ortalama_toplam_maliyet_pts": 45.993,
    "ham_buyuk_bar_sayisi_M5": 13621,
    "seans_disi_nedeniyle_atlanan": 10675,
    "cakisma_nedeniyle_atlanan": 743,
    "max_ardisik_kazanc": 7,
    "max_ardisik_kayip": 14
  },
  "istatistiksel_anlamlilik_once_kontrol": {
    "M5_global_reversal_orani": 0.5094, "M5_global_binom_p": 0.0288,
    "M1_global_reversal_orani": 0.5315, "M1_global_binom_p": 3.89e-13,
    "M5_seans_15_18_reversal_orani": 0.4886, "M5_seans_15_18_binom_p": 0.2234,
    "anlamli_mi_seans_15_18_alpha_0_05": false
  },
  "gorulmemis_veri_sonuclari": {
    "OOS_son_%30": {
      "toplam_islem": 670,
      "win_rate": 0.4224,
      "profit_factor": 0.623,
      "net_profit_usd_per_1_0_lot": -65982.56,
      "max_drawdown_pts": -67978.6
    },
    "walk_forward_6_pencere_profit_factor": [0.404, 0.49, 0.401, 0.555, 0.782, 0.495],
    "walk_forward_6_pencere_net_pts": [-30584.21, -23576.93, -36547.07, -34673.14, -26068.92, -47429.68]
  },
  "kirilim_analizi": {
    "teyit_ufku_PF_tum_donem": {"t+1": 0.558, "t+2": 0.631, "t+3": 0.675},
    "teyit_ufku_PF_IS_OOS": {"t+1": [0.517, 0.623], "t+2": [0.591, 0.69], "t+3": [0.743, 0.59]},
    "cikis_yontemi_PF_tum_donem": {"yalniz_zaman_N1": 0.788, "yalniz_zaman_N2": 0.808, "yalniz_zaman_N3": 0.912, "yalniz_ATR_TP_SL": 0.564, "combined_ana": 0.558},
    "seans_filtresi_PF_tum_donem": {"filtresiz": 0.519, "birincil_15_18": 0.558}
  },
  "islem_logu": "Tam log JSON dosyasinda mevcut - backtest_hipotez2_output.json -> senaryolar.ANA_KONFIGURASYON.islem_logu_tam (2203 islemin TAMAMI, ornek degil)",
  "uyarilar": [
    "SLIPAJ_DUZELTME_UYGULANDI: onceki turdeki tick-zaman-uyusmazligi hatasi duzeltildi (bkz. bolum 2) - bu raporun TUM sayilari duzeltilmis hesaplamaya dayanir.",
    "ISTATISTIKSEL_ANLAMSIZLIK: fiilen islem edilen alt-orneklemde (M5 seans 15-18) buyuk-bar-sonrasi ters-yon orani (%48,86) 0,50'den ISTATISTIKSEL OLARAK ANLAMLI SEKILDE SAPMIYOR (binom p=0,2234) - ham edge, global M5/M1 orneklemde anlamli olsa da, nihai islem edilen populasyonda ZATEN yok.",
    "TUM_KONFIGURASYONLARDA_PROFIT_FACTOR_1_ALTINDA: ana konfigurasyon, tum teyit-ufku/cikis-yontemi/seans-filtresi kirilimlarinin TAMAMINDA (en iyisi bile PF=0,912, yalniz-zaman-N3) tum-donem PF<1.",
    "WALK_FORWARD_TUTARLI_NEGATIF: 6 pencerenin TAMAMI PF<1 (0,401-0,782 araligi) - tek-donem carpitmasi yok, Hipotez 1'deki overfitting hatasindan farkli olarak burada IS/OOS arasinda BUYUK sapma da yok (genel olarak tutarli negatif).",
    "SAAT_ESLEME_UYARISI: DST gecis analizinde 2 net gecis noktasinda 1-saat kayma tespit edildi (Hipotez 1 ile ayni bulgu, bagimsiz dogrulandi) - kis aylarinda 15-18 filtresi fiilen 1 saat kaymis olabilir.",
    "MALIYET_SIMULASYONU_SINIRI: giris tarafi gercek tick (bid/ask) ile hesaplandi, cikis tarafinda ayni-anda tick cekilmedi (giris spread'inin yarisi cikis maliyeti olarak varsayildi) - tam cift-tarafli tick simulasyonu DEGIL.",
    "TICK_ZAMAN_ESLESME_ESIGI_MUHENDISLIK_KARARI: 60 saniyelik esik bu turde eklendi, Stratejist tarafindan belirlenmedi - ayrica onaylanmalidir (gorev prensibi: parametre/tasarim degisikligi Stratejist'e geri bildirilir, kendiliginden kalici sayilmaz)."
  ]
}
```

---

## 4) DETAYLI KIRILIM TABLOLARI

### 4.1 Teyit Ufku Taramasi (t+1/t+2/t+3), esik carpani SABIT (1,5x), session=15-18, exit=combined

| Ufuk | Islem (tum) | Win% | PF (tum) | Net (pts) | IS n / PF | OOS n / PF |
|---|---|---|---|---|---|---|
| t+1 (teyitsiz, ana) | 2203 | 41,03 | 0,558 | -198.879,95 | 1533 / 0,517 | 670 / 0,623 |
| t+2 (1-bar teyit) | 1132 | 43,73 | 0,631 | -80.419,47 | 782 / 0,591 | 350 / 0,690 |
| t+3 (2-bar teyit) | 673 | 44,28 | 0,675 | -41.085,24 | 460 / 0,743 | 213 / 0,590 |

Not: teyit ufku uzadikca PF hafifce iyilesiyor (0,558→0,675) ama TUMU 1'in altinda kaliyor;
islem sayisi da orantili azaliyor (potansiyel secim/orneklem etkisiyle karistirilmamali).

### 4.2 Cikis Yontemi Taramasi, confirm_horizon=1, session=15-18

| Yontem | Islem | Win% | PF (tum) | Net (pts) | IS PF | OOS PF |
|---|---|---|---|---|---|---|
| yalniz N=1 bar zaman | 1884 | 46,07 | 0,788 | -120.774,50 | 0,729 | 0,881 |
| yalniz N=2 bar zaman | 1633 | 49,30 | 0,808 | -111.937,50 | 0,739 | 0,927 |
| yalniz N=3 bar zaman | 1471 | 49,69 | 0,912 | -51.097,50 | 0,903 | 0,924 |
| yalniz ATR TP/SL (20-bar cap) | 2199 | 41,06 | 0,564 | -198.031,45 | 0,522 | 0,631 |
| combined (ana) | 2203 | 41,03 | 0,558 | -198.879,95 | 0,517 | 0,623 |

Not: en iyi kirilim dahi (yalniz-zaman-N3) PF=0,912 ile 1'in altinda kaliyor; N arttikca
PF iyilesme egilimi var ama islem sayisi azaliyor, IS/OOS arasinda buyuk sapma yok
(overfitting isareti gorulmuyor, sadece tutarli negatif/az-negatif sonuc).

### 4.3 Seans Filtresi Karsilastirma (confirm_horizon=1, exit=combined)

| Filtre | Islem | Win% | PF (tum) | Net (pts) |
|---|---|---|---|---|
| filtresiz (tum saatler) | 10402 | 41,63 | 0,519 | -790.248,24 |
| birincil 15-18 (ana) | 2203 | 41,03 | 0,558 | -198.879,95 |

Not: seans filtresi hafif iyilestirme sagliyor (0,519→0,558) ama sonucu 1'in ustune
tasimiyor.

### 4.4 Walk-Forward (6 pencere, ana konfigurasyon)

| Pencere | Tarih | Islem | Win% | PF | Net (pts) |
|---|---|---|---|---|---|
| 1 | 2025-02-11 / 2025-05-07 | 334 | 35,33 | 0,404 | -30.584,21 |
| 2 | 2025-05-07 / 2025-07-31 | 347 | 42,36 | 0,490 | -23.576,93 |
| 3 | 2025-07-31 / 2025-10-23 | 366 | 38,52 | 0,401 | -36.547,07 |
| 4 | 2025-10-23 / 2026-01-21 | 402 | 42,54 | 0,555 | -34.673,14 |
| 5 | 2026-01-21 / 2026-04-17 | 370 | 48,11 | 0,782 | -26.068,92 |
| 6 | 2026-04-17 / 2026-07-10 | 384 | 38,80 | 0,495 | -47.429,68 |

Not: 6 pencerenin TAMAMI PF<1 (0,401-0,782 araligi) — zaman ustunde tutarli sekilde
negatif, tek bir donemin sonucu carpitmasi soz konusu degil. En iyi pencere (5, PF=0,782)
dahi 1'in altinda.

### 4.5 Dagilim Istatistikleri (ana konfigurasyon, net_pts, n=2203)

| Persentil | p1 | p5 | p10 | p25 | p50 (medyan) | p75 | p90 | p95 | p99 |
|---|---|---|---|---|---|---|---|---|---|
| net_pts | -998,39 | -566,81 | -468,72 | -327,30 | -184,46 | 182,55 | 343,63 | 481,86 | 832,30 |

- Max ardisik kazanc: 7 | Max ardisik kayip: 14
- Kar konsantrasyonu: 904 kazanan islemden ilk 10'u toplam brut karin (251.002,11 pts)
  yalniz %6,44'unu (16.152,28 pts) olusturuyor — kar birkac buyuk islemde asiri
  yogunlasmamis (bu acidan saglikli bir dagilim, ama zaten toplam sonuc negatif).

### 4.6 Aylik Kirilim (ozet — ilk 5 / son 5 ay, tam liste JSON'da)

| Ay | Islem | Net (pts) | Win% |
|---|---|---|---|
| 2025-02 | 80 | -8.445,46 | 28,75 |
| 2025-03 | 112 | -8.070,82 | 37,50 |
| 2025-04 | 118 | -10.976,57 | 38,98 |
| 2025-05 | 123 | -10.171,10 | 40,65 |
| 2025-06 | 120 | -11.048,51 | 35,00 |
| ... | ... | ... | ... |
| 2026-03 | 112 | -3.005,03 | 49,11 |
| 2026-04 | 131 | -18.010,21 | 38,17 |
| 2026-05 | 134 | -11.209,61 | 43,28 |
| 2026-06 | 149 | -21.710,86 | 36,24 |
| 2026-07 | 39 | -3.447,43 | 46,15 |

Tam 17 aylik kirilimda pozitif net_pts olan tek bir ay YOK — HIPOTEZ 1'deki gibi tutarli
negatif bir desen.

---

## 5) MINIMUM ORNEKLEM DEGERLENDIRMESI

Tum konfigurasyonlarda islem sayisi 213 (en dar: t+3 OOS) ile 10.402 (filtresiz tum donem)
arasinda degisiyor. Ana konfigurasyonun IS (1533) ve OOS (670) orneklemleri istatistiksel
olarak fazlasiyla yeterli buyuklukte (n>500); "yetersiz veri" uyarisi gerekmiyor. En dar
kirilim olan t+3/OOS (n=213) yine de yorumlanabilir sinirin uzerinde (Hipotez 1'deki en dar
kirilim n=88'den daha genis), ancak tek basina karar dayanagi olarak kullanilmamalidir.
Tick zaman-eslesme reddi (2 ornek, tum 12.210 sorgu icinde ihmal edilebilir orandaki,
~%0,016) sonuc buyukluklerini etkilemeyecek kadar kucuktur.

---

## 6) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — Buyuk-Bar Ters-Yon/Fade (HIPOTEZ 2) — Kural-tabanli — 2026-07-11

ONEMLI ON-NOT: Bu turde onceki (hatali/yarim kalmis) turde tespit edilen bir KOD HATASI
duzeltildi - tick-bazli slipaj hesaplamasi, MT5'in eski tarihli tick sorgularinda "soguk
baslangic" durumunda GUNCEL/YANLIS-DONEMLI tick donebildigini kontrol etmiyordu (bkz.
rapor bolum 2). Duzeltme sonrasi profit_factor 0,867'den 0,558'e DUSTU - yani onceki
(hatali) sayi HIPOTEZi OLDUGUNDAN DAHA IYI GOSTERIYORDU. Asagidaki tum sayilar
DUZELTILMIS/DOGRU hesaplamadir.

Egitim / In-Sample (ilk %70, ~2025-02-11/2026-04-17):
  Islem: 1533 | Win rate: %40,51 | Profit Factor: 0,517 | Net: -132.897,39 puan

Gorulmemis Veri (OOS, son %30, ~2026-04-17/2026-07-10):
  Islem: 670 | Win rate: %42,24 | Profit Factor: 0,623 | Net: -65.982,56 puan

Walk-Forward (6 pencere, ~17 ay): Profit Factor araligi 0,401-0,782, 6 pencerenin
  TAMAMI 1'in altinda (tutarli negatif, tek-donem carpitmasi yok, buyuk IS/OOS sapmasi da
  yok - Hipotez 1'deki overfitting deseninden farkli, burada tutarli/az-negatif bir sonuc).

Dikkat noktalari:
  - ONCE-KONTROL/ISTATISTIKSEL ANLAMLILIK: fiilen islem edilen alt-orneklemde (M5, seans
    15-18) buyuk-bar-sonrasi ters-yon orani %48,86 - 0,50'den ISTATISTIKSEL OLARAK ANLAMLI
    SEKILDE SAPMIYOR (binom p=0,2234). Global (filtresiz) M5 orneklemde (%50,94, p=0,0288)
    ve M1'de (%53,15, p<0,001) anlamli sapma var, ama bu, gercekte islem edilen dar seans
    penceresinde KAYBOLUYOR - yani BULGU4'un ham edge'i, uygulanan seans filtresiyle
    birlikte zaten istatistiksel olarak var olmayabilir.
  - TUM KONFIGURASYONLARDA PROFIT FACTOR 1'IN ALTINDA: ana konfigurasyon + teyit-ufku
    (t+1/t+2/t+3) + cikis-yontemi (zaman-N1/N2/N3, ATR-only, combined) + seans-filtresi
    (filtresiz/15-18) taramalarinin TAMAMINDA tum-donem PF<1 (en iyisi 0,912 -
    yalniz-zaman-N3, yine de <1).
  - SLIPAJ/MALIYET DUZELTMESI: onceki turde tick-zaman-uyusmazligi hatasi nedeniyle
    ortalama giris slipaji ATR'nin ~6 katina (fiziksel olarak imkansiz) sismisti; duzeltme
    sonrasi ATR'nin ~%3,7'sine (627,71 ATR / 23,50 slipaj) dustu - fiziksel olarak tutarli.
    Duzeltme, PF'yi IYILESTIRMEDI, KOTULESTIRDI (0,867->0,558) - onceki hatali buyuk
    rastgele-isaretli slipaj degerleri toplamda birbirini goturup PF'yi yapay sekilde
    yukseltiyordu.
  - SAAT ESLEME: DST gecis analizi (Hipotez 1 ile ayni yontem, bagimsiz tekrarlandi) yine
    2 net gecis noktasinda (2025-03-30, 2026-03-29) 1-saat kayma gosterdi - kis aylarinda
    15-18 seans filtresi fiilen 1 saat kaymis olabilir, bu backtest dogrulanmamis
    GMT+3-sabit varsayimiyla hesaplanmistir.
  - Maliyet simulasyonu SINIRI: giris tarafi gercek tick (bid/ask), cikis tarafi giris-
    spread'inin yarisi varsayimi (tam cift-tarafli tick simulasyonu degil).
  - TICK_ZAMAN_ESLESME_ESIGI (60 sn) bu turde Muhendis tarafindan eklenen bir muhendislik
    parametresidir, Stratejist tarafindan belirlenmedi - ayrica onaylanmalidir.
  - Minimum orneklem: ana IS/OOS fazlasiyla yeterli (n=1533/670); en dar alt-kirilim
    (t+3 OOS, n=213) yorumlanabilir sinirin uzerinde ama tek basina karar dayanagi olamaz.

Detay dosya: C:\MilaYatirim\Justin\backtest_hipotez2_output.json (tam senaryo detaylari +
  tick_zaman_eslesme_dogrulama bolumu + islem_logu_tam - 2203 islemin tamami)
Kod: C:\MilaYatirim\Justin\backtest_hipotez2.py
```

---

## 7) IZOLASYON NOTU

- Bu oturumda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (signal.json,
  milagold_trades.json, lisa_performance.json, positions_status.json,
  stratejici_gold_gecmis_calisma.md vb.) ACILMADI veya referans ALINMADI.
- MilaGold'un aktif parametreleri (M5 EMA20, EMA100 streak>=13, trailing stop, 0,01 lot,
  5$/3$/5$/8$ SL/TP) hicbir sekilde kullanilmadi; SL/TP tamamen ATR(14,M5)-bazli/dinamik
  olarak Stratejist'in HIPOTEZ 2 tasarimina gore uygulandi.
- Calisma yalniz C:\MilaYatirim\Justin\ dizininde yapildi; veri dogrudan MT5'ten
  (MetaTrader5 python kutuphanesi) cekildi. Onceki tur de dahil olmak uzere hicbir dosya
  disi/harici veri kaynagi kullanilmadi.

---

## 8) ONAY NOKTASI

Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik
dogrulama + kod-hata duzeltme, canli sisteme dokunus yok, Justin demo/arastirma
asamasinda, henuz canli hesap/kasa yok). Sonuc uretildiginde Ertan'a Telegram bilgi notu +
Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
