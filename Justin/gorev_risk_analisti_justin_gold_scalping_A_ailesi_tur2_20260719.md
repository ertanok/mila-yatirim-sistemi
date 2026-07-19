=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-19 09:38
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi, Tur 2

GOREV              : Backtest Muhendisi'nin Tur 2'de urettigi iki hipotezi (H4 "Momentum-Esikli
                      Teyit", H5 "Kanal-Disi Kirilim Girisi") BIRLIKTE degerlendir ve A ailesi
                      Tur 2 icin nihai karari ver: her iki hipotez de HICBIR split'te
                      (Train/Validation/Test/Tam-Donem) PF>=1'e ulasmadi — bu net bir RED
                      goruntusu, ama iki hipotez BAGIMSIZ mekanizmalar oldugu icin ayri ayri
                      "neden RED" degerlendirilmeli (Stratejist raporunun ayirdigi mantikla
                      tutarli, biri RED gelirse otomatik olarak "A ailesi olu" ima etmez).
                      Ayrica H4'un H2 (Tam Tur 1) ile dogrudan karsilastirmasinin (ayni
                      HTF/LTF/orneklem tabani) getirdigi "mekanizma degisince PF gercekten
                      degisiyor mu" sorusuna nihai/toparlayici bir yorum ekle. Gunluk pipeline
                      tur-sayacini (1/5'ten) Tur 2'nin KAPANMASIYLA guncelle ve Tur 3'un
                      gerekip gerekmedigine dair bir on-gorus bildir (nihai "Tur 3 baslasin mi"
                      karari Orkestrator'a aittir, Risk Analisti sadece tavsiye eder).

                      ONEMLI EK DEGERLENDIRME MADDESI (H5'e ozel): H5 raporu, gorevin
                      "birincil kaynagi" sayilan Stratejist dosyasini
                      (stratejici_raporu_..._tur2_adim1_20260719.md, H5 bolumu + "Backtest
                      Muhendisi icin Notlar 1-10") bulamadigini, ve "Kanal Genisligi/Dis Sinir"
                      tanimini kaynak eksikligi nedeniyle SIFIRDAN/onaysiz bir varsayim olarak
                      kendisinin tasarladigini acikca bildiriyor. Risk Analisti bu durumu
                      degerlendirirken iki soruyu ayirt etsin: (a) H5'in PF sonucu (RED, tum
                      splitlerde <1) bu varsayimdan BAGIMSIZ olarak zaten yeterince net mi
                      (yani sonucu degistirme ihtimali dusuk mu), (b) yoksa nihai karardan once
                      Stratejist'in bu varsayimi (Dis Sinir tanimi) gozden gecirip
                      onaylamasi/reddetmesi bekleniyor mu (bu durumda Risk Analisti raporunda
                      bunu acik bir devir-notu olarak Stratejist'e yonlendirmeli, kendisi
                      kesin/nihai bir "mekanizma gecerli/gecersiz" hukmu vermeden).

GECMIS CALISMA/CERCEVE DOSYASI: C:\MilaYatirim\Justin\justin_gecmis_calisma.md,
                      C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md,
                      C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
  - Backtest Muhendisi raporu H4 (Momentum-Esikli Teyit, uc kombinasyon: M15 k=1,0 BIRINCIL,
    M15 k=0,5 duyarlilik, M5 k=1,0 capraz-kontrol):
    C:\MilaYatirim\mila-yatirim-sistemi\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_tur2_H4_20260719.md
  - Backtest Muhendisi raporu H5 (Kanal-Disi Kirilim Girisi):
    C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_tur2_H5_20260719.md

  Not (agent'lar-arasi sayisal tutarlilik, CLAUDE.md 10 Temmuz kurali): H4 ve H5 farkli
  mekanizma/orneklem/split-uzunluklarina sahiptir (H4: M15/M5 giris, uc alt-kombinasyon;
  H5: M15 birincil, kanal-disi-kirilim tetigi, ayrica bir ADIM-0 on-tarama asamasi var) —
  karsilastirma yaparken PF/n sayilarini es-tabanliymis gibi birbirinin dogrudan/bagimsiz
  dogrulamasi olarak SUNMA. H4'un H2 (Tam Tur 1) ile karsilastirmasi ise BILINCLI olarak
  ayni tabanda tutulmustur (H4 raporu Bolum 4.4) — bu karsilastirma dogrudan kullanilabilir.

BEKLENEN CIKTI     : risk_analisti_raporu_justin_gold_scalping_A_ailesi_tur2_20260719.md
                      (kaydedilecek klasor: C:\MilaYatirim\Justin\)

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik degerlendirmedir, canli sisteme
                      hicbir dokunus yoktur (Justin arastirma asamasinda, canli/demo hesap
                      henuz baglanmadi). Ertan'a Telegram bilgi notu gider, onay GEREKMEZ
                      (STOP-genis/bilgi-notu kategorisi). Istisna: eger Risk Analisti herhangi
                      bir hipotezi "demo/canli hesaba baglanmaya hazir" olarak tavsiye ederse
                      (bu turde PF sonuclarina gore beklenmiyor, ikisi de RED), o GECIS
                      ADIMININ KENDISI ayrica ve acikca Ertan onayi gerektirir — bu rapor o
                      onayi kendiliginden vermez, sadece tavsiye eder.
