=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 15:55
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping, ML/Feature-Tabanli Aile v2 — ML Ailesi TAM TUR 2)

GOREV              : Hipotez 1 (v2, LightGBM ikili + Grup B pivot/S-R feature'lari) ve Hipotez 2
                      (v2, LightGBM 3-sinifli/deadzone + Grup B) backtest raporlarini BIRLIKTE,
                      TEK bir degerlendirme turunda incele ve Tur 2 icin nihai KABUL/RED karari
                      ver (S3 governance notu geregi — Stratejist raporu, "Governance (S3,
                      bilgi amacli)" maddesi).

                      Ayrica ACIKCA degerlendir: bu turun sonucu, Tur 1'in RED paterniyle
                      (rassal-seviye AUC + NEREDEYSE-SIFIR feature-onem + esik-kalibrasyonunda
                      0-islem) AYNI PATERNDE mi, yoksa farkli mi? Bu ayrim onemli çünkü S3
                      sayacinin 1/2 -> 2/2 gecip gecmeyecegini belirliyor (nihai karar
                      Orkestrator'a ait, ama Risk Analisti'nin bu karsilastirmayi acikca
                      raporlamasi gerekiyor). Dikkat: ham veriye gore Hipotez 1 (v2) rassal-
                      seviye AUC ve 0-islem uretti (Tur1 ile bu yonde benzer) AMA feature-onem
                      Tur1'in aksine NEREDEYSE SIFIR degil, Grup B feature'larina BELIRGIN
                      sekilde yogunlasti; Hipotez 2 (v2) ise Tur1'in hicbirinde gorulmeyen
                      sekilde FIILEN ISLEM URETTI (15 LONG, PF=0,781, hedefin altinda,
                      orneklem yetersiz). Bu farklarin "ayni patern" sayilip sayilmayacagina
                      kendi uzmanliginla karar ver, gerekcelendir.

                      Ek olarak ozellikle degerlendirilmesi istenen iki bulgu (Backtest
                      Muhendisi'nin Risk Analisti'ne iletim bolumlerinde acikca isaretledi):
                      1) ATR tutarsizligi: k_risk icin BASIT/rolling-ortalama ATR, k_label icin
                         Wilder-smoothed ATR kullanildi (Stratejist notu "Wilder=v1 ile tutarli"
                         idi ama v1'in fiili kodu BASIT ATR — bu bir terminoloji karisikligi/
                         varsayim hatasi olabilir, k_risk mekanizmasi etkilenmedi).
                      2) Hipotez 2'nin orneklem yetersizligi (n=15 < MIN_SAMPLE=30) — PF/WR tek
                         basina karar dayanagi olamaz.

                      Hipotez 3 (v2, dusuk oncelik/kisitli pilot) bu gorev anında henuz
                      tamamlanmamis olabilir (script/ciktisi var ama rapor yok) — Stratejist'in
                      kendi notuyla Hipotez 3 ana karar agirligini TASIMAZ, tamamlayici/on-
                      gozlem niteligindedir. Raporu hazirsa tamamlayici gozlem olarak dahil et;
                      hazir degilse BEKLEMEDEN Hipotez 1/2 uzerinden karar ver.

GECMIS CALISMA/CERCEVE DOSYASI: C:\MilaYatirim\Justin\justin_gecmis_calisma.md,
                      C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (S2),
                      C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md (S1),
                      C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md
                      (S3 governance notu, "Governance (S3, bilgi amacli)" maddesi)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez1_20260712.md
                      C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez2_20260712.md
                      (varsa, tamamlayici) C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez3_20260712.md

BEKLENEN CIKTI     : risk_analisti_raporu_justin_gold_scalping_ml_v2_tur2_20260712.md
                      (C:\MilaYatirim\Justin\ klasorune kaydedilecek)

ONAY NOKTASI       : Bilgi notu — bu adimin kendisi salt-okunur/analitik degerlendirmedir, canli
                      sisteme/hesaba hicbir etkisi yoktur (Justin arastirma/demo-oncesi asamada,
                      gercek hesap yok). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali
                      etki yok, tespit gecikmesi konusu degil, etki alani dar (yalniz Justin
                      klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi bu adim icin
                      GEREKMEZ. NOT (Orkestrator'a hatirlatma): karar RED ve Risk Analisti'nin
                      degerlendirmesiyle Tur 1 ile AYNI patern kabul edilirse, S3 sayaci 2/2'ye
                      ulasir ve Orkestrator BIR SONRAKI Arastirmaci turunu Ertan onayi olmadan
                      baslatmaz (bu, bu gorevin degil, bu goreve verilecek YANITIN sonucudur).
