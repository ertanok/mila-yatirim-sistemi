# BACKTEST MUHENDiSi RAPORU — Justin / Gold Scalping — ML/Feature-Tabanli Aile v1 — HIPOTEZ 2
## XGBoost Kiyaslama (Ayni Tasarim, Ayni Feature/Label/N/k=1,5xATR14-M15)

Tarih: 2026-07-12
Hipotez adi: XGBoost Kiyaslama — HIPOTEZ 2
Yaklasim turu: Makine Ogrenmesi — Gradient Boosting (XGBoost, binary:logistic classifier)
Girdi: `stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md` (Karar 1-4, Hipotez 2)
Script: `backtest_ml_v1_hipotez2.py` | Ham veri: `backtest_ml_v1_hipotez2_output.json`
Kiyaslama referansi: `backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md` (LightGBM,
ayni tur, PARALEL calistirildi — Risk Analisti'nin Hipotez 1 degerlendirmesi BEKLENMEDEN)

---

## 0) BU GOREVIN CERCEVESI (Orkestrator gorev talimati ozeti)

Bu gorev, Hipotez 1'in (LightGBM) Risk Analisti degerlendirmesine PARALEL calistirilmistir —
Stratejist'in kendi gerekcesiyle tutarli: Hipotez 2, Hipotez 1'i DOGRULAYAN/CAPRAZ-KONTROL EDEN
bagimsiz bir ikinci olcumdur, sinyalin model-secimine mi yoksa veri/sinyale mi bagli oldugunu
ayristirmak icin degerlidir, Hipotez 1'in sonucundan BAGIMSIZ olarak calistirilmistir (onceden
"Hipotez 1 RED cikti, o zaman Hipotez 2 de RED cikar" varsayimi YAPILMADAN, gercekten calistirilip
gozlemlenmistir).

---

## 1) KUTUPHANE ON-KOSULU SONUCU

Gorev talimati geregi bu turde SADECE `xgboost`'un kurulu oldugu tekrar dogrulandi (Hipotez 1
turunde zaten kurulmustu), yeniden kurulum YAPILMADI:

| Kutuphane   | Surum   | Durum |
|---|---|---|
| pandas      | 3.0.3   | Kurulu (dogrulandi) |
| xgboost     | 3.3.0   | Kurulu (dogrulandi) |
| scikit-learn| 1.9.0   | Kurulu (dogrulandi) |
| numpy       | 2.5.0   | Kurulu (dogrulandi) |
| lightgbm    | 4.6.0   | Kurulu (bu turde kullanilmadi, Hipotez 1 raporunda kayitli) |

Dogrulama komutu ciktisi: `xgboost 3.3.0 pandas 3.0.3 sklearn 1.9.0 numpy 2.5.0` — hepsi mevcut,
hicbir kurulum adimi calistirilmadi.

---

## 2) ON-KONTROL SONUCLARI (S1 stres-testi + DST) — HIPOTEZ 1'DEN DEVRALINDI (gerekceli)

### 2.1 DST/Saat-Eslesme Dogrulamasi (Standart Madde 1) — **HIPOTEZ 1'DEN DEVRALINDI, GECTI**

- Gerekce (Orkestrator gorev talimati Madde 3'te acikca istisna tanimlanmis): Hipotez 2, Hipotez
  1 ile **AYNI feature-uretim kodu** (ayni saat/oturum blogu, ayni script iskeleti) kullanir. Bu,
  "onceki AILEDEN devralinamaz" kuralinin (H1/H2/H3 kural-tabanli aileden ML'e devir) bir
  ISTISNASIDIR — burada AYNI ML/v1 ailesi icinde, AYNI koda dayanan bir kiyaslama modeli soz
  konusudur, BAGIMSIZ bir yeniden-implementasyon degildir.
- Hipotez 1 sonucu (aynen gecerli): 8/8 bilinen DST gecisinde piyasa-acilis saati 1 SAAT KAYDI
  gozlendi → MT5 sunucusu DST'yi TAKIP EDIYOR. Saat-bazli feature'lar (hour_sin/cos,
  session_asia/london/ny, dow) sunucu-yerel zamana gore TUTARLI.
- Referans: `backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md`, Bolum 2.1.

### 2.2 S1 — Maliyet-Orani Stres Testi (Standart Madde 2) — AYNI BARRIER TASARIMI, TUTARLILIK TEYIT EDILDI

Gorev talimati geregi bu S1 hesaplamasi TEKRAR calistirilmasi gerekmiyordu (Hipotez 1 ile ayni
N=16/k=1,5 barrier tasarimi, model mimarisinden bagimsiz); yine de script bu hesaplamayi tekrar
uretti (ayni ATR/spread dagilimi uzerinden calistigi icin) ve **Hipotez 1 raporundaki sonuc
BIREBIR TEYIT EDILDI**:

| Olcum | Deger | Hipotez 1'deki deger |
|---|---|---|
| ATR14(M15) medyan | 287,43 pts | 287,43 pts (AYNI) |
| Spread medyan | 27,0 pts | 27,0 pts (AYNI) |
| Spread P90 | 36,2 pts | 36,2 pts (AYNI) |
| **Oran — medyan-spread** | **15,97x** | **15,97x (AYNI)** |
| **Oran — P90-spread STRES TESTI** | **11,91x** | **11,91x (AYNI)** |
| Esik alt sinir | 15,0x | 15,0x |
| Medyan uzerinden GECTI mi | EVET | EVET |
| **P90 STRES TESTI GECTI mi** | **HAYIR** | **HAYIR** |

Degerlendirme: Sonuc, Hipotez 1 raporuyla (Bolum 2.2) tam olarak tutarlidir — bu BEKLENEN bir
sonuctur, cunku maliyet-orani sadece ATR/spread dagilimina baglidir, model-secimine (LightGBM vs
XGBoost) bagli DEGILDIR. P90-stres testinde esik yine KAYBEDILIYOR (11,91x < 15,0x). Gorev
talimati geregi bu esik kaybi ana testi DURDURMADI — Hipotez 2 asagida yine de calistirildi.

---

## 3) ANA TEST TASARIMI / YONTEM

- **Model:** XGBoost ikili siniflandirici (`objective="binary:logistic"`), sabit/dar
  hiperparametreler (grid-search YAPILMADI — S2 geregi):
  `max_depth=6, learning_rate=0.05, n_estimators=500, min_child_weight=50, subsample=0.8,
  colsample_bytree=0.8, reg_lambda=1.0, random_state=42, early_stopping_rounds=30,
  eval_metric="auc"`.
- **Hipotez 1 (LightGBM) ile parametre-eslesme notu (SEFFAFLIK icin):** Iki kutuphane FARKLI
  parametrelemeler kullanir, bu yuzden BIREBIR ayni isim/deger seti YOKTUR — asagidaki eslesme
  "AYNI karmasiklik disiplinini" (dar aralik, ONCEDEN sabit) hedefler, degerlerin matematiksel
  ozdesligini degil:
  - `num_leaves=31` (yaprak-bazli buyume sinirlamasi) ↔ XGBoost'ta dogrudan karsiligi YOK
    (derinlik-bazli buyur); `max_depth=6` HER IKI modelde de AYNI DEGER/AYNI ISIMLE kullanildi.
  - `min_child_samples=50` (yaprak basina minimum ORNEK SAYISI) ↔ `min_child_weight=50`
    (yaprak basina minimum HESSIAN TOPLAMI — ikili siniflandirmada bu bir orneklem-sayisi degil,
    agirlikli bir esiktir; SAYISAL olarak 50 verildi ama METRIK FARKLIDIR, bu bilinen bir sinirdir).
  - `learning_rate, n_estimators, subsample, colsample_bytree, reg_lambda, random_state`: HER IKI
    modelde AYNI ISIM/AYNI DEGER.
  - Erken durma sabri: LightGBM `early_stopping(30)` ↔ XGBoost `early_stopping_rounds=30` — AYNI.
- **Feature seti:** Hipotez 1 ile BIREBIR AYNI 23 sutun (5 grup: Volatilite[3], MTF-Confluence[4],
  Hacim[3], Oturum/Gun-Ici[6], Fiyat-Yapisi/Momentum[7]).
- **Etiket:** Hipotez 1 ile BIREBIR AYNI — Triple-barrier, N=16 M15-bar (4 saat) zaman-bariyeri,
  SL=TP=1,5xATR14(M15) (RR=1:1). `hicbiri` (zaman-asimi) egitim/PRIMARY-test disi tutuldu.
- **Veri bolumu (kronolojik, karistirilmadi, Hipotez 1 ile AYNI sinirlar):** toplam 99.999 M15 bar
  (2022-04-18 → 2026-07-10). TRAINVAL: ilk %80 (n=68.785 ikili-etiketli). PURGE: `i+N<=trainval_end_bar`.
  EMBARGO: 24 bar (6 saat). TEST: son dilim (n=17.833 ikili-etiketli), **TEK KEZ** kullanildi.
- **Walk-forward:** TRAINVAL icinde 5 esit segment → 4 purged/embargolu fold, Hipotez 1 ile AYNI
  segment sinirlari (dogrudan karsilastirilabilirlik icin, Orkestrator gorev talimati Madde 4).
- **Esik-kalibrasyonu:** SADECE out-of-fold (walk-forward) tahminleri uzerinde precision-proxy(WR)
  taramasi — TEST SETINE BAKILMADI (S2 Madde2), Hipotez 1 ile AYNI aday esikleri/skorlama kurali.
- **Feature-sizinti kontrol listesi (S2 Madde3):** tum maddeler teyit edildi (ileri-bakan bilgi
  yok, normalizasyon sadece egitim setinden, MACD HAM DEGER kullanildi — isaret degil, ayni
  feature-uretim kodu kullanildigi icin Hipotez 1'deki teyit gecerliligini korur).
- **Basari kriterleri (egitimden ONCE sabitlendi, S2 Madde4):** HEDEF_PF=1,5, HEDEF_WR=%60,0
  (RR=1:1 icin, `justin_gecmis_calisma.md`), HEDEF_DD=%20 kumulatif — Hipotez 1 ile AYNI.
- **Maliyet modeli:** tick-bazli gercek maliyet (Justin ailesi standardi) — Hipotez 1 ile AYNI.
- **Lot/risk:** `justin_gecmis_calisma.md` geregi kasa=2.000 USD, lot=0,01 (sabit), risk-basi =
  kasa x %1 ust sinir — Hipotez 1 ile AYNI.
- **Calistirma:** `py backtest_ml_v1_hipotez2.py` (timeout: 480.000 ms). Script BASTAN SONA,
  HICBIR HATA VERMEDEN, EXIT_CODE=0 ile tamamlandi. Kod uzerinde hicbir "duzeltme"/mudahale
  gerekmedi (parametre/mantik degisikligi YOK, tek calistirma yeterli oldu).

---

## 4) SONUCLAR

### 4.1 Walk-Forward (Purged/Embargolu, 4 fold) — Model Ayirt Edicilik Onbulgusu

| Fold | Train n | Val n | Val AUC | best_iteration (0-indeksli) | Agac sayisi kullanilan |
|---|---|---|---|---|---|
| 1 | 13.666 | 13.547 | 0,5074 | 3 | 4 |
| 2 | 27.240 | 13.693 | 0,5190 | 6 | 7 |
| 3 | 40.972 | 13.653 | 0,5066 | 22 | 23 |
| 4 | 54.654 | 14.105 | 0,5174 | 0 | 1 |

**AUC ozet: ortalama=0,5126, std=0,0056, min=0,5066, max=0,5190.**

> Bu sonuc, Hipotez 1'in walk-forward AUC ozetiyle (ortalama=0,5075, std=0,0122) AYNI
> KATEGORIDEDIR — **neredeyse RASSAL (coin-flip) seviyesinde**, ancak XGBoost'un ortalamasi
> Hipotez 1'e gore hafifce daha yuksek (0,5126 vs 0,5075) ve daha DUSUK varyansli (std=0,0056 vs
> 0,0122) — bu fark KUCUKTUR ve pratik anlamda "anlamli sinyal ogrenildi" seklinde
> YORUMLANAMAZ (her iki model de 0,50 rassal-cizgisine cok yakin kalmistir).

### 4.2 Esik-Kalibrasyonu (Out-of-Fold, TEST SETINE BAKILMADAN)

| Esik (Long/Short) | Long n | Long WR-proxy | Short n | Short WR-proxy | Toplam n | Kapsama | Skor |
|---|---|---|---|---|---|---|---|
| 0,60 / 0,40 | 202 | 0,5842 | 0 (yetersiz n) | - | 202 | %0,37 | 0,5842 |
| **0,575 / 0,425 (SECILEN)** | 590 | 0,5458 | 32 | 0,6250 | 622 | %1,13 | **0,5854** |
| 0,55 / 0,45 | 1288 | 0,5489 | 184 | 0,4130 | 1472 | %2,68 | 0,4810 |

**SECILEN ESIK: LONG>=0,575 / SHORT<=0,425** (her iki taraf da MIN_SAMPLE>=30 esigini gecti,
fallback UYGULANMADI). Not: Hipotez 1'de secilen esik 0,55/0,45 idi — burada FARKLI bir esik
(0,575/0,425) secildi, cunku esik-skor kurali (MIN_SAMPLE'i gecen taraflarin ortalama WR-proxy'si)
BU MODELIN kendi OOF-dagilimina gore hesaplandi; bu, iki modelin farkli olasilik dagilimlarina
sahip olmasinin DOGAL bir sonucudur, bir tutarsizlik/hata DEGILDIR.

### 4.3 Final Model Egitimi

- Egitim n=54.654, ic-validasyon n=14.105, ic-validasyon AUC=**0,5174** (rassal-seviyeye yakin,
  ama Hipotez 1'in 0,4990'undan bir miktar yuksek), `best_iteration=0` (0-indeksli) → **1 agac
  kullanildi** — Hipotez 1'deki `best_iteration=1` (1 boosting turu) ile AYNI karakterde: erken
  durma cok erken devreye girmis, model pratikte tek bir sig agactir.
- Feature-onem tablosu (XGBoost `feature_importances_`, **normalize edilmis GAIN** — Hipotez 1'in
  LightGBM `feature_importances_`'i split-SAYISI tabanlidir, FARKLI metrik, sadece GORELI siralama
  karsilastirilabilir): en yuksek degerler `dow`=0,0715, `hour_cos`=0,0601, `h4_trend_aligned`=0,0588,
  `session_ny`=0,0569, `session_asia`=0,0566 — en dusuk `session_london`=0,0 (hic kullanilmamis).
  **Onemli gozlem:** Hipotez 1'de ATR/trend/confluence gibi ana gruplar NEREDEYSE HIC agirlik
  almiyordu (`atr14_m15`=0, `confluence_flag`=0); Hipotez 2'de (XGBoost, normalize-gain metriginde)
  TUM feature'lar goreli olarak DAHA DENGELI bir dagilima sahip (en dusuk sifir-olmayan deger
  `directional_streak`=0,023, en yuksegi 0,0715 — yaklasik 3 kat fark, LightGBM'deki (0 ile 10
  arasindaki, pratik olarak sonsuz oranli) FARKTAN cok daha kucuk). **Ancak bu fark, importance
  metriginin FARKLI olcegi (split-sayisi vs normalize-gain) nedeniyle DOGRUDAN "XGBoost daha
  fazla feature kullaniyor" seklinde yorumLANAMAZ** — her iki modelin de TEST AUC'u rassal-seviyede
  oldugu icin, hicbir feature-onem tablosu (hangi metrikle olculurse olculsun) anlamli/genellenebilir
  bir sinyal ogrenildigine kanit TESKIL ETMEZ.
- **TEST SETI (tek-kez) siniflandirma AUC'u: 0,5228** — Hipotez 1'in 0,5170'ine yakin, yine
  rassala yakin.

### 4.4 TANI: TEST Setinde Olasilik Dagilimi

| Istatistik | Deger (Hipotez 2 / XGBoost) | Hipotez 1 (LightGBM) |
|---|---|---|
| p_test min | 0,5053 | 0,5037 |
| p_test max | 0,5241 | 0,5304 |
| p_test ortalama | 0,5085 | 0,5089 |
| p_test std | 0,0041 | 0,0047 |
| Esik LONG (>=0,575) asan bar sayisi | **0** | (Hipotez 1'in esigi 0,55'ti, orada da 0) |
| Esik SHORT (<=0,425) asan bar sayisi | **0** | (Hipotez 1'in esigi 0,45'ti, orada da 0) |

Final modelin TEST setindeki en yuksek olasiligi (0,5241) kalibre edilmis 0,575 esiginin
ALTINDA kaliyor — Hipotez 1'deki AYNI DESEN (final modelin TEST doneminde OOF-kalibrasyonunun
ulastigi guven bandina HICBIR ZAMAN ulasamamasi) burada da GOZLEMLENDI. Bu, hem PRIMARY hem
SUPPLEMENTARY simulasyonda 0 islem tetiklenmesinin dogrulanmis/beklenen nedenidir — kod/veri
hatasi DEGILDIR.

### 4.5 PRIMARY Test-Seti Simulasyonu (hicbiri-haric, Karar-2-literal)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate | tanimsiz (n=0) |
| Profit Factor | tanimsiz (n=0) |
| Net kar (USD, 0,01 lot) | 0,0 |
| Max Drawdown | tanimsiz (n=0) |

### 4.6 SUPPLEMENTARY Test-Seti Simulasyonu (hicbiri-dahil, canliya-yakin capraz kontrol)

| Metrik | Deger |
|---|---|
| Toplam islem | **0** |
| Win Rate / PF / Net kar / Max DD | tumu tanimsiz (n=0) |

### 4.7 HEDEF_PF/HEDEF_WR/HEDEF_DD Karsilastirmasi ve GECTI/RED Karari

| Kriter | Hedef | Gozlemlenen (PRIMARY) | Gozlemlenen (SUPPLEMENTARY) |
|---|---|---|---|
| PF | >=1,5 | tanimsiz (n=0) | tanimsiz (n=0) |
| WR (RR=1:1) | >=%60,0 | tanimsiz (n=0) | tanimsiz (n=0) |
| DD | <=%20 kumulatif | tanimsiz (n=0) | tanimsiz (n=0) |

**KARAR: RED.** Gerekce (yorum degil, protokol-uygulamasi — Hipotez 1 ile AYNI mantik): Ortak
Ilkeler'deki "Minimum orneklem uyarisi" geregi, test edilen kumede HICBIR islem yoksa sonuc
anlamli/olculebilir DEGILDIR; S2 Madde4 altinda bir kriterin "olculemedi" cikmasi, o kriterin
KARSILANDIGININ iddia edilemeyecegi anlamina gelir — dolayisiyla protokol geregi varsayilan sonuc
RED'dir. Walk-forward AUC'sinin (~0,51, rassal-seviye) ve final-model TEST AUC'sinin (0,523)
zaten isaret ettigi zayifligin, test doneminde MODELIN KENDI KALIBRE ETTIGI ESIGE HIC
ULASAMAMASIYLA sonuclandigini gosteriyor.

---

## 5) HIPOTEZ 1 (LightGBM) vs HIPOTEZ 2 (XGBoost) KARSILASTIRMA TABLOSU (ZORUNLU, gorev Madde 6)

| Metrik | Hipotez 1 — LightGBM | Hipotez 2 — XGBoost | Fark/Degerlendirme |
|---|---|---|---|
| Walk-forward AUC (ortalama) | 0,5075 | 0,5126 | Kucuk fark (+0,0051), her ikisi de rassal-seviyede |
| Walk-forward AUC (std) | 0,0122 | 0,0056 | XGBoost daha DUSUK varyansli (daha az fold-arasi dalgalanma), ama ikisi de zayif |
| Walk-forward AUC (min/max) | 0,4938 / 0,5251 | 0,5066 / 0,5190 | XGBoost'un araligi biraz DAHA DAR ve biraz DAHA YUKSEK, pratik onemi YOK (ikisi de ~0,50-0,52) |
| Final model ic-validasyon AUC | 0,4990 | 0,5174 | Kucuk fark, ikisi de rassal-seviye |
| Final model best_iteration | 1 (1-indeksli, LightGBM) | 0 (0-indeksli) → 1 agac | AYNI KARAKTER: erken durma HER IKI modelde de cok erken devreye girdi (pratikte tek agac/cok az agac) |
| **Final model TEST AUC** | **0,5170** | **0,5228** | Kucuk fark (+0,0058), ikisi de rassal-seviyeye yakin |
| Esik-kalibrasyonu (OOF, secilen) | LONG>=0,55 / SHORT<=0,45 | LONG>=0,575 / SHORT<=0,425 | FARKLI esik secildi (kendi OOF-dagilimlarina gore) — beklenen bir farklilik, hata degil |
| p_test max (final model, TEST) | 0,5304 | 0,5241 | Ikisi de secilen esigin ALTINDA kaliyor |
| **PRIMARY islem sayisi (TEST)** | **0** | **0** | **AYNI SONUC** |
| **SUPPLEMENTARY islem sayisi (TEST)** | **0** | **0** | **AYNI SONUC** |
| PF/WR/DD (PRIMARY) | tanimsiz (n=0) | tanimsiz (n=0) | AYNI |
| **KARAR** | **RED** | **RED** | **AYNI KARAR, BAGIMSIZ ULASILDI** |
| S1 maliyet-orani (medyan/P90) | 15,97x / 11,91x (P90 KAYBEDILDI) | 15,97x / 11,91x (P90 KAYBEDILDI) | AYNI (barrier tasarimindan kaynaklanir, model-secimine bagli degil) |

**Sentez (yorum degil, gozlem — Risk Analisti'nin yorumlama alanina birakilir):** Iki BAGIMSIZ
model mimarisi (LightGBM ve XGBoost), AYNI feature seti/etiket/barrier tasarimi uzerinde,
BIRBIRINE COK YAKIN ve HER IKISI DE RASSAL-SEVIYEDE walk-forward/TEST AUC uretmistir (~0,50-0,52
araligi), ve TEST doneminde HER IKI MODEL DE kendi kalibre ettigi guven esigine hic
ULASAMAMISTIR (0 islem, 0 islem). Bu, Hipotez 1'in raporunda sorulan soruya ("sinyal
model-secimine mi yoksa veri/sinyale mi bagli?") acik bir yanit verir: **sonuc model-secimine
BAGLI DEGILDIR** — iki farkli gradient-boosting mimarisi de AYNI (zayif/rassal-seviye) sinyali
ogrenmis/ogrenememistir. Bu, mevcut feature setinin (Karar 3, ~18-22/23 sutun) ve/veya N=16/k=1,5
etiket tasariminin, bu iki model ailesi icin ayirt edici bir sinyal TASIMADIGINA isaret eden
CAPRAZ-DOGRULANMIS bir bulgudur.

---

## 6) RISK ANALiSTiNE iLETiM

```
DOGRULAMA SONUCU — XGBoost Kiyaslama (Ayni Tasarim, N=16/k=1,5xATR14-M15) — ML/Gradient Boosting — 2026-07-12

Egitim / Walk-Forward (4 fold, purged+embargolu, TRAINVAL icinde):
  AUC ortalama=0,5126 (std=0,0056, min=0,5066, max=0,5190) — RASSAL SEVIYEYE YAKIN
  (Hipotez 1/LightGBM: ortalama=0,5075, std=0,0122 — AYNI KATEGORIDE, kucuk fark)
  Esik-kalibrasyonu (OOF-havuz): LONG>=0,575 (n=590, WR-proxy=%54,6) / SHORT<=0,425 (n=32, WR-proxy=%62,5)
  Final model ic-validasyon AUC=0,5174, best_iteration=0(0-idx)->1 agac (erken durma - pratikte tek agac,
  Hipotez 1'deki best_iteration=1 ile AYNI karakter)

Gorulmemis Veri (TEST seti, TEK KEZ, 2025-09-04 -> 2026-07-10, n=17.833):
  TEST AUC=0,5228 (rassala yakin, Hipotez 1: 0,5170)
  p_test dagilimi: min=0,5053 max=0,5241 ortalama=0,5085 (kalibre edilen 0,575/0,425 esigine HICBIR ZAMAN ulasmiyor)
  PRIMARY (hicbiri-haric) islem sayisi = 0 -> PF/WR/DD tanimsiz
  SUPPLEMENTARY (hicbiri-dahil, canliya-yakin) islem sayisi = 0 -> PF/WR/DD tanimsiz
  HEDEF_PF=1,5 / HEDEF_WR=%60,0 / HEDEF_DD=%20 -> HICBIRI OLCULEMEDI (n=0)
  KARAR: RED (olcum yoksa hedefin karsilandigi iddia edilemez, S2 Madde4 + Ortak Ilkeler)

Hipotez 1 (LightGBM) vs Hipotez 2 (XGBoost) CAPRAZ-KONTROL SONUCU:
  Iki BAGIMSIZ model mimarisi, AYNI feature/etiket/barrier tasariminda, BIRBIRINE COK YAKIN ve
  HER IKISI DE rassal-seviyede AUC uretti (~0,50-0,52 araligi); TEST doneminde HER IKI MODEL DE
  0 islem uretti (kendi kalibre ettigi esige hic ulasamadi). Sonuc: sinyal zayifligi
  MODEL-SECIMINE BAGLI DEGIL, iki farkli gradient-boosting ailesi de AYNI (zayif) sonucu vermis -
  bu, mevcut feature-seti/etiket-tasariminin ayirt edici sinyal TASIMADIGINA isaret eden
  CAPRAZ-DOGRULANMIS bir bulgudur.

Dikkat noktalari:
  - S1 (maliyet-orani) P90-stres testinde esik kaybediliyor (11,91x < 15,0x, Hipotez 1 ile AYNI -
    barrier tasarimindan kaynaklanir, model-secimine bagli degil).
  - OVERFITTING_RISKI: Hipotez 1'de oldugu gibi, ters yonde bir gozlem var - egitim (walk-forward,
    0,5126) ve test (0,5228) AUC'leri birbirine yakin, BUYUK fark YOK; asiri uyum degil, TUTARLI
    ZAYIFLIK (modelin hicbir donemde ayirt edici gucu olmamasi) gozlemleniyor - Hipotez 1 ile AYNI
    desen, iki modelde de.
  - Esik-kalibrasyonu FARKLI secildi (H1: 0,55/0,45, H2: 0,575/0,425) - bu, iki modelin FARKLI OOF
    olasilik-dagilimina sahip olmasindan kaynaklanir, bir hata/tutarsizlik DEGILDIR; her iki
    esikte de final model TEST doneminde esige ULASAMADI (sonuc degismiyor).
  - Feature-onem tablolari FARKLI metrik kullanir (LightGBM: split-sayisi: XGBoost: normalize-gain)
    - mutlak degerler karsilastirilamaz, sadece goreli siralama; her iki tabloda da HICBIR
    feature grubunun baskin/net bir sinyal tasidigina dair GUCLU bir isaret YOK (TEST AUC zaten
    rassal-seviyede oldugu icin bu tutarli).
  - Hipotez 2, Hipotez 1'in Risk Analisti degerlendirmesiyle birlikte AYNI "tam tur" sayilir
    (Orkestrator gorev talimati, S3 governance notu) - sayac islemesi Orkestrator'un yetkisindedir.

Detay dosya: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez2_20260712.md
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v1_hipotez2_output.json
Kiyaslama referansi: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
```

---

## 7) iZOLASYON NOTU

Bu script ve bu rapor, MilaGold/Lisa/Signal GPT'ye ait HICBIR dosyayi/parametreyi/format-sablonunu
acmadi veya referans almadi. Calisma dizini yalniz `C:\MilaYatirim\Justin\` idi. Veri dogrudan
MT5'ten (MetaTrader5 kutuphanesi, GOLD sembolu M15 OHLCV+tick_volume+spread) cekildi. Script,
Justin'in KENDI onceki turu olan `backtest_ml_v1_hipotez1.py`'nin egitim/test/embargo iskeletini
(izolasyon disi — ayni proje ici sureklilik) yeniden kullandi, SADECE model mimarisini (LightGBM
→ XGBoost) ve buna bagli hiperparametre/importance-metrigi farklarini degistirdi; feature/etiket/
barrier/maliyet-modeli/lot-risk kodu BIREBIR AYNI KALDI. Rapor sablonu da Justin'in kendi onceki
Backtest Muhendisi raporlarindan (Hipotez 1, ayni proje) turetildi — MilaGold'a ait hicbir sablon
acilmadi.

---

## 8) ONAY NOKTASI

Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasidir (script calistirma +
raporlama), canli sisteme dokunus YOK, Justin demo/arastirma asamasindadir (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam (hicbir kalici/geri-donulmez islem
yapilmadi), mali etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru).
→ **STOP-genis/bilgi-notu kategorisi, Ertan onayi GEREKMEZ.** Rapor uretildiginde Ertan'a Telegram
bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
