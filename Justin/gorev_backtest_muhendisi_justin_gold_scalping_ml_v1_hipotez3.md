=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 17:25
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 3 (LightGBM, N=16/k=2,0xATR14-M15 — Hipotez 1'in guvenlik-marji/
                      duyarlilik varyanti)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md,
                      Bolum "HIPOTEZ 3") tanimladigi k=2,0 varyantini dogrula. AYNI feature seti/
                      model ailesi (LightGBM)/etiket semasi (ikili, "hicbiri" disarida) — SADECE
                      barrier k=1,5 yerine k=2,0.

                      **ONEMLI — Hipotez 1'in Risk Analisti raporundan (risk_analisti_raporu_
                      justin_gold_scalping_ml_v1_hipotez1_20260712.md) devralinan ZORUNLU DUZELTME:**
                      Hipotez 1'de esik-kalibrasyonu 4 FARKLI fold modelinin (best_iteration 1/6/4/1)
                      HAVUZLANMIS OOF tahminleri uzerinden yapilmisti; bu, final modelin (tek model,
                      kendi best_iteration'i) gercekte hicbir zaman ulasamayacagi bir esik uretti ve
                      TEST'te 0 islemle sonuclandi (Risk Analisti Kontrol [7] ve Geri Bildirim
                      Madde 1). **Bu turde esik-kalibrasyonu SADECE final modelin KENDI OOF
                      tahminlerinden (ya da final modelle AYNI egitim-boyutu/karakterdeki TEK bir
                      fold'dan) yapilmalidir — 4 farkli modelin havuzlanmis tahminleri KULLANILMAMALI.**
                      Bu duzeltme yapilmadan rapor teslim edilirse Risk Analisti asamasinda ayni
                      nedenle tekrar KIRMIZI/RED beklenmelidir — bu adimi ATLAMA.

                      Sira / kapsam:
                      1. **On-kosul:** Kutuphane kurulumu (pandas/lightgbm) Hipotez 1/2 turlerinde
                         zaten dogrulanmisti — yeniden kurulum GEREKMEZ.
                      2. **S1 — Maliyet-orani on-kontrolu:** k=2,0 icin cost-ratio ZATEN
                         Arastirmaci/Stratejist tarafindan hesaplanmis (medyan 21,29x — esigi
                         (~15-20x) medyanda RAHATCA karsiliyor, Hipotez 1'in k=1,5/15,97x'ine gore
                         daha genis marj). Yine de P90/max spread stres-testini bu k degeri icin
                         AYRICA calistir (Hipotez 1'in P90 sonucu, k=1,5'e ozel oldugu icin
                         DEVRALINAMAZ, k=2,0 icin yeniden hesaplanmali).
                      3. **DST/saat-eslesme dogrulamasi:** Hipotez 1/2 ile AYNI feature pipeline'i
                         (ayni saat/oturum feature'lari) kullanildigi icin Hipotez 1'in DST
                         dogrulama sonucunu (GECTI) DEVRALABILIRSIN.
                      4. **S2 — Anti-overfitting protokolu (TAMAMI ZORUNLU):** Purged/embargolu
                         walk-forward (N=16-bar + ek embargo), test-seti TEK KEZ kullanim,
                         feature-sizinti kontrol listesi (MACD ham-deger kurali dahil), basari
                         kriterleri (HEDEF_PF=1,5, HEDEF_WR=%60,0, HEDEF_DD=%20) EGITIMDEN ONCE
                         sabitlenmis olmali.
                      5. **Ana test:** LightGBM binary classifier, Hipotez 1 ile BIREBIR AYNI
                         feature seti (~18-22 sutun), etiket semasi ikili (yukari-bariyer-once/
                         asagi-bariyer-once, "hicbiri" disarida — bu k'da hicbiri orani ~%24,92
                         beklenir, Hipotez 1'e gore ~1,9 kat daha yuksek, bu beklenen bir
                         degis-tokus, hata degil), N=16/k=2,0xATR14(M15) barrier, SL=TP=2,0xATR
                         (RR=1:1).
                      6. **Model ogrenme kapasitesi — ozel gozlem istegi:** Hipotez 1'de final
                         model pratikte tek-agac kalmis (best_iteration=1) ve ATR/trend/confluence
                         gibi ZORUNLU feature gruplari sifira yakin agirlik almisti (model anlamli
                         sinyal ogrenmemis gorunuyordu). Bu turde feature-onem tablosunu ve
                         best_iteration degerini ACIKCA raporla — k degismesinin (daha genis
                         barrier, farkli sinif dengesi) modelin ogrenme kapasitesini degistirip
                         degistirmedigi (once-onemsiz feature'lar bu turde anlamli agirlik aliyor
                         mu) Risk Analisti icin onemli bir gozlemdir.
                      7. **Karsilastirma (ZORUNLU):** Raporunda Hipotez 1 (k=1,5) ile Hipotez 3
                         (k=2,0) sonuclarini YAN YANA sun: walk-forward AUC, final model TEST AUC,
                         best_iteration, feature-onem tablosu, esik-kalibre p-dagilimi (esige
                         ulasip ulasmadigi — bu turde DUZELTILMIS yontemle), esik-asan islem
                         sayisi, PRIMARY/SUPPLEMENTARY PF/WR/islem-sayisi, P90-stres testi sonucu.
                      8. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1,
                         taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000 USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md (HIPOTEZ 3 tanimi)
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
  (karsilastirma referansi icin)
- C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
  (ZORUNLU duzeltme — esik-kalibrasyon yontemi, yukarida ozetlendi, rapor Kontrol [7] ve
  Geri Bildirim Madde 1'de tam detay)
- Script referansi (yapi/kutuphane-kullanimi icin, kopyalama degil): C:\MilaYatirim\Justin\
  backtest_ml_v1_hipotez1.py

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez3_20260712.md
(bolum yapisi Hipotez 1 raporuyla paralel, ek olarak "Esik-Kalibrasyon Yontemi Duzeltmesi" bolumu
— nasil duzeltildigi acikca aciklanmali) + ham veri/script dosyalari (backtest_ml_v1_hipotez3_
output.json)

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESiN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): Hipotez 3, Hipotez 1/2 ile birlikte ayni Stratejist
raporundan/ayni "tam tur"dan turemistir (Stratejist raporu, Bolum 3, oncelik-3/dusuk ama Hipotez
1/2 ile paralel calistirilabilir olarak isaretlemisti). Bugun (12 Temmuz) bu proje icin gunluk
tam-tur sayaci 2 (kural-tabanli hat 1 + ML/v1 hat 1) — 5 esiginin altinda, otomatik devam.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
