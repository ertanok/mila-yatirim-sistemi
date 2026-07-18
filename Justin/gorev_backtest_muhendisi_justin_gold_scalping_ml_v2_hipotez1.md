=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 15:30
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v2
                      (ML Tam Tur 2), HIPOTEZ 1 (ANA/FEATURE-IZOLE HIPOTEZ: LightGBM ikili
                      yon-tahmini + Grup B/pivot-S-R feature'i eklenmis, etiket/N/k Tam Tur 1
                      ile AYNI birakilmis, N=16/k=1,5xATR14-M15)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md)
                      HIPOTEZ 1'ini dogrula. Bu, ML ailesinin Tam Tur 2'sinin ILK backtest
                      adimidir (S3 governance sayaci su an 1/2, bu adim sayaci DEGISTIRMEZ).

                      Sira / kapsam:
                      1. **On-kosul — kutuphane kontrolu:** pandas/lightgbm/scikit-learn Tur 1'de
                         zaten kurulup dogrulanmisti (v2 Arastirmaci raporu, "Kutuphane durumu
                         guncellemesi") — sadece versiyonlarin degismedigini teyit et (pandas
                         3.0.3, lightgbm 4.6.0, scikit-learn 1.9.0). XGBoost bu turde ZORUNLU
                         DEGIL (Stratejist Karar/Hipotez 1 gerekcesi: model-secimi ekseni Tur 1'de
                         zaten test edildi, fark yaratmadi).
                      2. **S1 — Maliyet-orani stres testi:** k_risk=1,5xATR14 Tur 1 ile AYNI
                         oldugu icin cost-ratio sonucu (15,97x, esigin ALT SINIRINDA) Tur 1'den
                         DEVRALINABILIR (Stratejist Notu Madde 1) — eger Tur 1'de P90/max-spread
                         stres-testi YAPILMADIYSA bu turde ZORUNLU olarak yap.
                      3. **DST/saat-eslesme dogrulamasi — BAGIMSIZ ZORUNLU:** Grup B (gunluk/
                         haftalik pivot, GUN/HAFTA siniri GMT+3 varsayimina dayanir) bu turde YENI
                         eklendigi icin onceki turden DEVRALINAMAZ (Stratejist Notu Madde 3,
                         `justin_backtest_onkontrol_standardi.md` Madde 1).
                      4. **S2 — Anti-overfitting protokolu (TAMAMI ZORUNLU), ozellikle:**
                         - Purged/embargolu walk-forward (N=16-bar + embargo), test-seti TEK KEZ
                           kullanim, basari kriterleri (HEDEF_PF=1,5, HEDEF_WR=%60,0 [RR=1:1],
                           HEDEF_DD=%20) EGITIMDEN ONCE sabitlenmeli.
                         - **Grup B ileri-bakis kontrolu (KRITIK, Stratejist ozellikle vurguladi):**
                           gunluk/haftalik pivotun ONCEKI TAMAMLANMIS gun/haftadan (nedensel shift)
                           turetildigi, 20-gunluk rolling-high/low'un SADECE t-oncesi 20 gunu
                           kullandigi (ileri-bakis YOK) BAGIMSIZ olarak kod-incelemesiyle
                           dogrulanmali — Arastirmaci'nin kendi ic-mantik kontrolu YETERLI
                           SAYILMAZ.
                      5. **Ana test:** LightGBM binary classifier (`objective=binary`) — feature
                         seti: v1'in ZORUNLU gruplari (1-Volatilite/ATR, 2-MTF Confluence,
                         3-Hacim/Tick-Yogunlugu, 4-Oturum/Gun-Ici cekirdek, 5-Fiyat Yapisi/
                         Momentum, ~18-22 sutun) + YENI Grup B (gunluk/haftalik pivot mesafesi,
                         20-gunluk rolling-high/low mesafesi + yakinlik bayragi, ~4-6 sutun) —
                         toplam ~22-28 sutun. Etiket: Tur 1 ile AYNI ikili sema (yukari-bariyer-
                         once/asagi-bariyer-once, "hicbiri" egitim/test disi) — bu turde
                         DEGISTIRILMIYOR. N=16 M15-bar zaman-bariyeri, SL=TP=1,5xATR14(M15)
                         (RR=1:1). Olasilik esigi (baslangic onerisi p>=0,55-0,60 LONG,
                         p<=0,40-0,45 SHORT) egitim/validasyon setinde KALIBRE ET (test setine
                         bakmadan). Dar hiperparametre araligi (num_leaves ~15-31), genis
                         grid-search YAPMA.
                      6. Hipotez 2 (multiclass/deadzone) AYRI bir gorev dosyasiyla, bu gorevle
                         PARALEL calistirilmaktadir (Stratejist'in kendi onerisi) — birbirini
                         BEKLEMENIZE gerek yok, ama raporunda Hipotez 2 ile karsilastirma
                         yapilabilmesi icin feature-onem tablosunu ACIKCA raporla.
                      7. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                         (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                         USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md (HIPOTEZ 1
  tanimi, Karar 1-4, Backtest Muhendisi icin Notlar bolumu — bu gorevin dogrudan kaynagi)
- C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
  (Tam Tur 1'in RED gerekcesi, karsilastirma/baseline referansi icin)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez1_20260712.md
(bolum yapisi: Kutuphane On-Kosulu Sonucu, On-Kontrol Sonuclari [S1 devir/stres-testi + DST
BAGIMSIZ, ayrik gecti/gecmedi], Grup B Ileri-Bakis Dogrulamasi [ayri, acik bolum], Ana Test
Tasarimi/Yontem, Sonuclar [tum-donem/IS/OOS/walk-forward, esik-kalibrasyonu, feature-onem
tablosu, PF/WR/islem sayisi], Tur 1 Hipotez 1 ile Karsilastirma, Risk Analistine Iletim,
Izolasyon Notu, Onay Noktasi) + varsa ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): S3 sayaci su an 1/2 (Tam Tur 1'in RED sonucuyla). Bu
Backtest adimi sayaci DEGISTIRMEZ (sayaci degistiren Risk Analisti'nin nihai karari). Eger bu
turun (Tur 2) Risk Analisti karari RED ve Tur 1 ile AYNI patern (rassal-seviye AUC, ana
feature'lar ~sifir agirlik, esik-kalibrasyonunda 0 islem) ile sonuclanirsa sayac 2/2'ye ulasir —
bu, Backtest Muhendisi'nin karar SURECINI degistirmez (kriterlere gore objektif raporlamaya
devam et), sadece Orkestrator'un bir sonraki adiminda devreye giren bir esiktir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
