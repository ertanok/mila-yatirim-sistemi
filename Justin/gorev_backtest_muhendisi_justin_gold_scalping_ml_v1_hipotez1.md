=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 13:40
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 1 (ANA HIPOTEZ: LightGBM ikili yon-tahmini, N=16/k=1,5xATR14-M15)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md)
                      HIPOTEZ 1'ini (LightGBM binary classifier) dogrula. Bu, ML ailesinin ILK
                      backtest turudur (S3 governance sayaci henuz islemiyor).

                      Sira / kapsam:
                      1. **On-kosul — kutuphane kontrolu (Stratejist Karar 4):** Calisma
                         ortaminda (VPS uzerinde veya izole bir venv icinde) pandas/lightgbm/
                         xgboost/scikit-learn kurulu mu kontrol et (`pip show lightgbm xgboost
                         scikit-learn pandas` veya esdegeri). Eksikse GORUNUR sekilde raporla ve
                         (izole/venv ortaminda oldugu, geri donulebilir ve dar-etkili oldugu
                         icin) kurulumu kendin yap — ama bu adimi sessizce gecme, raporda acikca
                         "kurulum yapildi: X, Y, Z" seklinde belirt (bu bir bilgi-notu
                         gerektirir, onay degil — STOP-genis/bilgi-notu kategorisi, cunku izole
                         ortam, geri donulebilir, canli sisteme etkisi yok).
                      2. **S1 — Maliyet-orani stres testi (justin_backtest_onkontrol_standardi.md
                         Madde 2):** Stratejist'in medyan-spread uzerinden yaptigi on-tahmini
                         (k=1,5 icin 15,97x, esigin ALT SINIRINDA) P90/max spread ile stres-test
                         et. Esik kaybedilirse acikca belirt (bu durumda Hipotez 3, k=2,0
                         varyanti, bir yedek olarak degerlendirilecek — bu tur kapsaminda DEGIL,
                         ayri bir sonraki tur olur).
                      3. **DST/saat-eslesme dogrulamasi (Backtest standardi Madde 1):** Feature
                         Grubu 4 (saat/oturum) kullanildigi icin BAGIMSIZ olarak yeniden dogrula
                         — onceki H1/H2/H3 (kural-tabanli aile) turlarindan DEVRALINAMAZ, bu ayri
                         bir aile/pipeline.
                      4. **S2 — Anti-overfitting protokolu (TAMAMI ZORUNLU):** Purged/embargolu
                         walk-forward (N=16-bar + makul ek embargo, orn. 4-8 saat), test-seti
                         TEK KEZ kullanim (esik/hiperparametre secimi tamamlandiktan sonra),
                         feature-sizinti kontrol listesi (ozellikle MACD ham-deger kurali —
                         isaret degil ham deger kullanilmali — ve normalizasyon istatistiklerinin
                         SADECE egitim setinden hesaplanmasi), basari kriterlerinin (HEDEF_PF=1,5,
                         HEDEF_WR=%60,0 [RR=1:1 icin], HEDEF_DD=%20 kumulatif) EGITIMDEN ONCE
                         yazili sabitlenmesi.
                      5. **Ana test:** LightGBM binary classifier — feature seti Stratejist Karar
                         3'teki ZORUNLU gruplar (Volatilite, Coklu-TF Confluence, Hacim/Tick-
                         Yogunlugu, Oturum/Gun-Ici Konum-cekirdek, Fiyat Yapisi/Momentum,
                         ~18-22 sutun); etiket Stratejist Karar 2'deki ikili sema (yukari-bariyer-
                         once / asagi-bariyer-once, "hicbiri" egitim/test disi); N=16 M15-bar
                         zaman-bariyeri; SL=TP=1,5xATR14(M15) (RR=1:1); olasilik esigi (baslangic
                         onerisi p>=0,55-0,60 LONG, p<=0,40-0,45 SHORT) egitim/validasyon setinde
                         ROC-AUC + precision-recall ile KALIBRE ET (test setine bakmadan).
                      6. **Opsiyonel/kaynak-izin verirse:** Hipotez 2 (XGBoost, birebir ayni
                         feature/label/N/k) paralel kiyaslama olarak da calistirilabilir — ayni
                         egitim/test/embargo bolmesi, ayni hiperparametre disiplini (dar aralik).
                         Bu ZORUNLU DEGIL; sure/kaynak yetmezse sadece Hipotez 1 ile devam et,
                         raporda acikca belirt (Hipotez 2 bir sonraki tura birakilabilir).
                      7. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                         (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                         USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md (HEDEF_PF/HEDEF_WR/HEDEF_DD/kasa/lot kurallari)
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (S2 protokolu, tam metin)
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md (S1 + DST + SL/TP-ozel on-kontrol
  standardi)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md
(HIPOTEZ 1/2/3, Karar 1-4, Backtest Muhendisi icin Notlar bolumu — bu gorevin dogrudan kaynagi)

BEKLENEN CIKTI     : C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
                      (bolum yapisi: Kutuphane On-Kosulu Sonucu, On-Kontrol Sonuclari [S1 stres-
                      testi + DST, ayrik gecti/gecmedi], Ana Test Tasarimi/Yontem, Sonuclar
                      [tum-donem/IS/OOS/walk-forward, esik-kalibrasyonu, PF/WR/islem sayisi],
                      Hipotez 2 durumu [calistirildi mi/ertelendi mi], Risk Analistine Iletim,
                      Izolasyon Notu, Onay Noktasi)
                      + varsa ham veri/script dosyalari (orn. backtest_ml_v1_hipotez1_output.json)

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): ML ailesinde 2 tam tur (Arastirmaci→Stratejist→
Backtest Muhendisi→Risk Analisti zincirinin Risk Analisti KARARIYLA sonuclanmasi = 1 tam tur)
ayni olumsuz paternle (istatistiksel olarak anlamli gorunen sinyal, tam testte sistematik
PF<1/RED) sonuclanirsa Orkestrator Ertan'a onay sorusu yoneltir. Bu, o zincirin ILK turudur —
sayac henuz islemiyor.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi
(gerekirse izole ortamda kutuphane kurulumu dahil — geri donulebilir, dar etki alanli, mali
etkisi yok), canli sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu
degil, etki alani dar (yalniz Justin klasoru/izole ortam) → STOP-genis/bilgi-notu kategorisi,
Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
