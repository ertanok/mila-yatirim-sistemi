=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 14:20
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 2 (XGBoost kiyaslama — ayni tasarim, ayni feature/label/N/k,
                      N=16/k=1,5xATR14-M15)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md,
                      Bolum "HIPOTEZ 2") tanimladigi XGBoost kiyaslama modelini dogrula. Bu gorev,
                      HIPOTEZ 1 (LightGBM) icin az once tamamlanan Risk Analisti degerlendirmesini
                      BEKLEMEDEN, ONA PARALEL calistirilmaktadir — Stratejist'in kendi
                      gerekcesiyle tutarli ("Hipotez 2, Hipotez 1'i DOGRULAYAN/CAPRAZ-KONTROL EDEN
                      bagimsiz bir ikinci olcumdur", sinyalin model-secimine mi yoksa veri/sinyale
                      mi bagli oldugunu ayristirmak icin onemlidir, HIPOTEZ 1'in sonucundan
                      bagimsiz olarak degerlidir).

                      Sira / kapsam:
                      1. **On-kosul:** Kutuphane kurulumu (pandas/lightgbm/xgboost/scikit-learn)
                         Hipotez 1 turunde zaten dogrulanmisti/kuruluydu — bu turde SADECE
                         xgboost'un kurulu oldugunu tekrar dogrula, yeniden kurulum GEREKMEZ
                         (Hipotez 1 raporu Bolum 1'e bak).
                      2. **S1 — Maliyet-orani stres testi:** Hipotez 1 ile AYNI barrier tasarimi
                         (N=16/k=1,5) kullanildigi icin cost-ratio sonucu (medyan 15,97x GECTI,
                         P90-stres 11,91x KAYBEDILDI) AYNI KALIR — bu S1 hesaplamasini TEKRAR
                         calistirmana gerek yok, Hipotez 1 raporundaki sonucu (Bolum 2.2) referans
                         ver ve aynen gecerli oldugunu belirt.
                      3. **DST/saat-eslesme dogrulamasi:** Hipotez 1 ile AYNI feature pipeline'i
                         (ayni saat/oturum feature'lari) kullanildigi icin Hipotez 1'in DST
                         dogrulama sonucunu (Bolum 2.1, GECTI) DEVRALABILIRSIN — bu, "onceki
                         AILEDEN devralinamaz" kuralinin bir istisnasidir CUNKU bu AYNI ML/v1
                         ailesi icinde, AYNI script/feature-uretim koduna dayanan bir kiyaslama
                         modelidir (H1/H2/H3 kural-tabanli aileden devralma degildir).
                      4. **S2 — Anti-overfitting protokolu (TAMAMI ZORUNLU, Hipotez 1 ile AYNI
                         disiplin):** AYNI purged/embargolu walk-forward bolmesi (mumkunse ayni
                         fold sinirlari, dogrudan karsilastirilabilirlik icin), test-seti TEK KEZ
                         kullanim, ayni feature-sizinti kontrol listesi, ayni basari kriterleri
                         (HEDEF_PF=1,5, HEDEF_WR=%60,0, HEDEF_DD=%20).
                      5. **Ana test:** XGBoost binary classifier (`objective=binary:logistic`),
                         Hipotez 1 ile BIREBIR AYNI feature seti (~18-22 sutun, Stratejist Karar 3
                         ZORUNLU gruplari), AYNI etiket semasi (Karar 2, ikili, "hicbiri" disarida),
                         AYNI N=16/k=1,5 barrier, AYNI SL/TP (simetrik 1,5xATR14, RR=1:1), dar
                         hiperparametre araligi (grid-search YAPMA, S2 geregi).
                      6. **Karsilastirma (ZORUNLU):** Raporunda Hipotez 1 (LightGBM) ve Hipotez 2
                         (XGBoost) sonuclarini YAN YANA sun: walk-forward AUC, final model TEST
                         AUC, p-dagilimi (esige ulasip ulasmadigi), esik-asan islem sayisi,
                         PRIMARY/SUPPLEMENTARY PF/WR/islem-sayisi. Hipotez 1'in TEST setinde 0
                         islem urettigi (rassal-seviye AUC nedeniyle) bilgin dahilinde — XGBoost'un
                         benzer mi yoksa farkli bir sonuc mu uretecegi acik bir soru, ONCEDEN
                         VARSAYIMDA BULUNMA, bagimsiz calistir ve gozlemle.
                      7. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1,
                         taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000 USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md (HIPOTEZ 2 tanimi)
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
  (karsilastirma referansi icin — Hipotez 1'in tam sonuclari)
- Script referansi (yapi/kutuphane-kullanimi icin, DEGISTIRMEDEN kopyalama degil, aynı egitim/
  test/embargo iskeletini yeniden kullanabilirsin): C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1.py

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez2_20260712.md
(bolum yapisi Hipotez 1 raporuyla paralel: On-Kontrol Sonuclari [S1/DST — Hipotez 1'den
devralindi, gerekcesiyle], Ana Test Tasarimi, Sonuclar, Hipotez 1 vs Hipotez 2 Karsilastirma
Tablosu, Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi)
+ ham veri/script dosyalari (orn. backtest_ml_v1_hipotez2_output.json)

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESiN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): Hipotez 2, Hipotez 1'in Risk Analisti karariyla
birlikte ayni "tam tur" sayilir (ikisi de Stratejist'in tek bir raporundan/tek bir Arastirmaci
girdisinden turemis, karsilastirmali bir cift). Sayac islemesi/gorunurlugu Orkestrator tarafindan
Risk Analisti asamasinda degerlendirilecektir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
