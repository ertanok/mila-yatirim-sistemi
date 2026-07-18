=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 14:10
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 1 (LightGBM ikili yon-tahmini, N=16/k=1,5xATR14-M15), 2. TUR
                      (on-kosul/kutuphane + on-kontroller + walk-forward + esik-kalibrasyonu +
                      final model egitimi zaten TAMAMLANMIS gorunuyor — bu tur SADECE
                      test-seti simulasyonunu tamamlama + rapor icindir)

GOREV              : Onceki tur (gorev_id: backtest_muhendisi_20260712_1640) "hata" ile
                      sonuclandi. Durum dosyasindaki rapor_yolu (C:\MilaYatirim\Justin\
                      _patch2.py) INCELENDI — bu dosya diskte MEVCUT DEGIL (Orkestrator
                      tarafindan dogrulandi). Yani onceki tur, beklenen nihai raporu
                      (backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md)
                      URETEMEDEN, muhtemelen script'te bir hatayi "patch" ile duzeltmeye
                      calisirken (isim sirasi _patch2 -> en az bir onceki patch denemesi
                      daha oldugunu dusundurur) turn/zaman tukenerek sona ermis.

                      Orkestrator (ben) su tespitleri yaptim (BULGU, asagida):
                      1. backtest_ml_v1_hipotez1.py dosyasi INCELENDI — sozdizimsel/yapisal
                         olarak TAM gorunuyor (bastan sona, mt5.shutdown() ile duzgun bitiyor,
                         kesinti/truncation belirtisi YOK). PRIMARY ve SUPPLEMENTARY test-seti
                         simulasyon bloklari ve nihai "hipotez_ozet" (PF/WR/HEDEF_PF
                         karsilastirmasi) script icinde MEVCUT.
                      2. Ancak backtest_ml_v1_hipotez1_output.json (diskteki mevcut hali)
                         SADECE "final_model_egitimi" asamasina kadar olan ARA KAYITLARI
                         iceriyor (DST/S1/feature-seti/etiket-dagilimi/walk-forward/
                         esik-kalibrasyonu/final-model-egitimi) — PRIMARY/SUPPLEMENTARY
                         test-seti islem simulasyonu, islem_logu, ve hipotez_ozet BOLUMLERI
                         YOK. Bu, script'in ilerledigi ama test-seti simulasyon asamasinda
                         (satir ~745-990 civari: get_tick_quote/simulate_trade/PRIMARY veya
                         SUPPLEMENTARY blogu) bir hatayla KARSILASTIGINI/DURDUGUNU
                         gosteriyor — script'in KENDISI degil, CALISTIRILMASI/tamamlanmasi
                         yarim kalmis.
                      3. Walk-forward CV sonuclari (4 fold, AUC ort.=0,5075, std=0,0122,
                         min=0,4938/max=0,5251) neredeyse RASSAL seviyede — bu, Hipotez 1'in
                         nihai testte HEDEF_PF=1,5'i karsilamasinin ZOR olacagina dair erken
                         bir isaret, ama bu tek basina RED KARARI ICIN YETERLI DEGIL: S2
                         protokolu geregi nihai PF/WR karari SADECE test-seti simulasyonu
                         (adim 5, asagida) tamamlandiktan sonra verilebilir — walk-forward
                         AUC'ye bakarak simulasyonu ATLAMA.

                      YAPMAN GEREKEN:
                      1. backtest_ml_v1_hipotez1.py'yi ONCE incele (degistirmeden) — script
                         yapisal olarak tam gorundugu icin SIFIRDAN YENIDEN YAZMA. Sadece
                         calistirdiginda test-seti simulasyon asamasinda (PRIMARY/
                         SUPPLEMENTARY, satir ~745-990 civari) ne tur bir hatayla
                         karsilasildigini TESPIT ET (orn. get_tick_quote/simulate_trade'de
                         bir index/veri hatasi, MT5 tick sorgusunda zaman asimi, bellek/
                         performans sorunu vb.).
                      2. Tespit ettigin somut hatayi DUZELT (mumkun oldugunca dar/minimal
                         degisiklik — sinyal tanimlari, ATR/RR/esik degerleri, maliyet modeli
                         DEGISMEYECEK, sadece calisma-zamani hatasini giderecek duzeltme).
                      3. Script'i CALISTIR (py komutu, Bash araciligiyla). Test-seti
                         simulasyonu binlerce bar icin tick-bazli maliyet sorgusu yapabilir,
                         UZUN surebilir — cömert bir timeout ver (en az 5-8 dakika/
                         300000-480000ms), varsayilan kisa timeout'a GUVENME.
                      4. backtest_ml_v1_hipotez1_output.json'un artik
                         test_trade_simulasyonu_PRIMARY, test_trade_simulasyonu_SUPPLEMENTARY_
                         hicbiri_dahil, islem_logu_PRIMARY_tam/SUPPLEMENTARY_tam ve
                         hipotez_ozet bolumlerini icerdigini DOGRULA.
                      5. Nihai raporu yaz — orijinal gorev dosyasindaki (gorev_backtest_
                         muhendisi_justin_gold_scalping_ml_v1_hipotez1.md) BEKLENEN CIKTI
                         bolum yapisinin AYNISI (Kutuphane On-Kosulu Sonucu, On-Kontrol
                         Sonuclari [S1 stres-testi + DST], Ana Test Tasarimi/Yontem, Sonuclar
                         [walk-forward, esik-kalibrasyonu, PRIMARY+SUPPLEMENTARY PF/WR/islem
                         sayisi, HEDEF_PF/WR/DD karsilastirmasi, GECTI/RED karari], Hipotez 2
                         durumu, Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi). Walk-
                         forward AUC'nin rassala yakin oldugunu (madde 3, yukarida) ACIKCA
                         belirt, ama nihai GECTI/RED kararini test-seti simulasyon
                         sonuclarina gore ver.
                      6. Diskte kalmis olabilecek "_patch*.py" gibi gecici/yarim dosyalari
                         (varsa) temizle veya en azindan raporda ne oldugunu kisaca not et.
                      7. EGER BU TUR DA (2. tur) nihai raporu URETEMEDEN hata ile sonuclanirsa:
                         3. bir turu KENDIN baslatma/onerme — bunun yerine calisma
                         dizininde NEDEN'i (hangi adimda, hangi hata mesaji/belirti)
                         mumkun oldugunca net aciklayan kisa bir not dosyasi birak (orn.
                         backtest_ml_v1_hipotez1_hata_notu_tur2.txt). Ayni adimda art arda
                         2. kez teshis edilemeyen hata potansiyel bir altyapi sorunu
                         isaretidir, Orkestrator bu durumda Ertan'a dogrudan bilgi
                         verecektir.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\gorev_backtest_muhendisi_justin_gold_scalping_ml_v1_hipotez1.md
  (1. tur gorev dosyasi — kapsam maddeleri hala gecerli)
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (S2)
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md (S1 + DST)
- C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1.py (mevcut, yapisal tam — sadece calisma-
  zamani hatasini duzelt, sifirdan yeniden yazma)
- C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1_output.json (mevcut, ARA KAYIT — final
  test-seti bolumleri eksik)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md

BEKLENEN CIKTI     : C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
                      + guncellenmis C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1_output.json
                      (test-seti simulasyon bolumleri dahil)

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait
hicbir dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini
yalniz C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): ML ailesinde 2 tam tur (Arastirmaci→Stratejist→
Backtest Muhendisi→Risk Analisti zincirinin Risk Analisti KARARIYLA sonuclanmasi = 1 tam tur)
ayni olumsuz paternle sonuclanirsa Orkestrator Ertan'a onay sorusu yoneltir. Bu zincirin ILK
turudur — sayac henuz islemiyor. (Bu gorevin kendisi bir "tur" degil, teknik bir yeniden-
deneme/tamamlamadir — RED/GECTI karari henuz verilmedi.)

ONAY NOKTASI       : Bilgi notu — salt-okunur/analitik/offline backtest calismasinin teknik
tamamlanmasi, canli sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap
yok). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi
konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi,
Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar
kaydi Orkestrator tarafindan dusulecektir.
