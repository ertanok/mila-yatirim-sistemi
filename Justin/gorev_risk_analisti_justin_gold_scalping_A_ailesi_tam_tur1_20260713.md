=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-13 15:52
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi, Tam Tur 1

GOREV              : Stratejist'in Tam Tur 1'de urettigi uc hipotezin (H1, H2, H3) UCUNU DE
                      BIRLIKTE degerlendir ve A ailesi Tam Tur 1 icin nihai karari ver:
                      hangi hipotez (varsa) bir sonraki asamaya (demo/canli on-hazirlik) tavsiye
                      ediliyor, hangileri RED, RED ise "mekanizma olarak neden" (H1/H2/H3
                      birbirinden bagimsiz sonuclar, biri RED gelirse bu digerini/"A ailesi
                      olu"yu otomatik ima etmez — Stratejist raporu bunu acikca ayirmis
                      durumda). Ayrica gunluk pipeline tur-sayacina gore Tam Tur 1'i KAPAT
                      (sayac: 1/5) ve Tur 2'nin gerekip gerekmedigine (orn. Stratejist'e yeni
                      varyant/iyilestirme icin devir notu) dair bir on-gorus bildir — nihai
                      "Tur 2 baslasin mi" karari Orkestrator'a aittir, Risk Analisti sadece
                      tavsiye eder.

GECMIS CALISMA/CERCEVE DOSYASI: C:\MilaYatirim\Justin\justin_gecmis_calisma.md,
                      C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md,
                      C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
  - Stratejist raporu (hipotez tanimlari, H1/H2/H3):
    C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md
  - Backtest Muhendisi raporu H1 (tekrar deneme, nihai):
    C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H1_20260713.md
  - Backtest Muhendisi raporu H2:
    C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H2_20260713.md
  - Backtest Muhendisi raporu H3:
    C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H3_20260713.md

  Not (agent'lar-arasi sayisal tutarlilik, CLAUDE.md 10 Temmuz kurali): Her uc rapor kendi
  bagimsiz DST/S1 on-kontrolunu ayri ayri (ortak sonuc TASINMADAN) hesaplamistir, ve H1/H2/H3
  farkli zaman-dilimi/orneklem uzerinde calisir (H1: M5-giris, H2: M15-giris genis-orneklem,
  H3: M15-giris asimetrik-BUY-only alt-kume) — karsilastirma yaparken bu farkli
  orneklem/tanim temellerini goz onunde bulundur, dogrudan PF/n sayilarini es-tabanliymis gibi
  birbirinin "bagimsiz dogrulamasi" olarak SUNMA.

BEKLENEN CIKTI     : risk_analisti_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260713.md
                      (kaydedilecek klasor: C:\MilaYatirim\Justin\)

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik degerlendirmedir, canli sisteme
                      hicbir dokunus yoktur (Justin arastirma asamasinda, canli/demo hesap
                      henuz baglanmadi). Ertan'a Telegram bilgi notu gider, onay GEREKMEZ
                      (STOP-genis/bilgi-notu kategorisi). Istisna: eger Risk Analisti herhangi
                      bir hipotezi "demo/canli hesaba baglanmaya hazir" olarak tavsiye ederse,
                      o GECIS ADIMININ KENDISI (canliya/demoya baglanma) ayrica ve acikca
                      Ertan onayi gerektirir — bu rapor o onayi kendiliginden vermez, sadece
                      tavsiye eder.
