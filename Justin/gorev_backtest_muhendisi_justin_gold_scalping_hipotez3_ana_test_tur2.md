=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-11 00:20
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — HIPOTEZ 3, ANA TEST, 2. TUR
                      (on-kontroller 1-3 zaten GECILDI/TAMAM, main.py zaten yazilmis ve
                      sozdizimsel tam — bu tur SADECE calistirma+onarim+rapor icindir)

GOREV              : Onceki tur (gorev_id: backtest_muhendisi_20260711_0012) "hata" ile
                      sonuclandi — rapor_yolu bos, hicbir Write cagrisi/rapor uretilmedi.
                      Bir onceki turdan (backtest_muhendisi_20260710_2202) FARKLI bir hata
                      imzasi: o turde 3 deneme de ANINDA ("Credit balance is too low",
                      1 turn'de) dusmustu; bu tur ~6-7 dakika calisti (agent_cagir'in
                      cagrildigi 00:12 ile durum dosyasinin yazildigi 00:19 arasi), yani
                      gercekten bir sey calisti ama Write/rapor asamasina ULASAMADI.
                      Kesin sebep bilinmiyor (worker sureci stdout/stderr loglamiyor,
                      dogrudan gozlem yok) — ama en olasi iki aday:
                      (a) backtest_hipotez3_main.py'nin calistirilmasi (Bash araciligiyla)
                          varsayilan/kisa bir timeout'a takildi (script uzun surebilir —
                          asagidaki BULGU'ya bak), agent bu yuzden turn/zaman tukendi ve
                          hicbir rapor yazamadan oturum "hata" ile kapandi;
                      (b) yine gecici bir Anthropic API/kredi kesintisi (bu ihtimal
                          disariya kapatilamaz ama bir onceki turden FARKLI sure imzasi
                          bunu daha az olasi kiliyor).

                      BEN (Orkestrator) main.py'yi tekrar okudum ve SOMUT bir verimsizlik
                      buldum (BULGU, asagida) — bu, script'i gereksiz yere yavaslatip
                      olasi bir timeout riskini artiriyor olabilir. Bunu düzelt, ayrica
                      calistirma adiminda cömert bir timeout kullan.

                      BULGU (main.py, satir ~503-513): STREAK-FADE senaryosu icin
                      streak_results sozlugu ilk dongude (satir ~432-445) zaten
                      run_scenario(...) ile hesaplaniyor (tr degiskeni), ama bu tam
                      islem listesi ATILIYOR (sadece ozet/IS-OOS/walk-forward/rejim
                      istatistikleri sakla niyor). Sonra dosyanin sonunda (satir 507-511)
                      AYNI 4 streak uzunlugu (L2-5) icin run_scenario AYNEN TEKRAR
                      cagriliyor, sirf islem_logu_tam alanini doldurmak icin. Bu ikinci
                      gecis GEREKSIZ — ilk dongudeki tr listesini dogrudan sakla
                      (streak_results[f"L{L}"]["islem_logu_tam"] = tr), ikinci
                      run_scenario cagrisini SIL. TICK_QUOTE_CACHE sayesinde ikinci
                      gecis byte-hesap acisindan cogunlukla cache-hit olsa da, yine de
                      tum simulate_trade dongusunu (Python seviyesinde binlerce ihtimal)
                      bastan sona tekrar calistiriyor — gereksiz sure/turn maliyeti.
                      Bu KESIN bir "hata" degil ama net bir verimsizlik; asil calisma
                      mantigini/sonuclarini DEGISTIRMEZ, sadece hizlandirir. Duzelt.

                      YAPMAN GEREKEN:
                      1. main.py'deki yukaridaki BULGU'yu duzelt (satir 503-513'u kaldir,
                         ilk dongudeki tr'yi doğrudan sakla). Baska HICBIR mantik/parametre
                         degistirme (sinyal tanimlari, ATR/RR/oturum filtresi, maliyet
                         modeli AYNEN kalacak).
                      2. backtest_hipotez3_output.json HALA yoksa: duzeltilmis script'i
                         CALISTIR (py komutu). Bash tool cagrisinda script MT5'ten
                         ~binlerce M1 bar + tick-bazli maliyet sorgusu yaptigi icin
                         UZUN surebilir — Bash cagrisina cömert bir timeout ver (en az
                         5-8 dakika/300-480000ms), varsayilan kisa timeout'a GUVENME.
                      3. Cikan JSON'daki buyukluklerin fiziksel tutarli oldugunu dogrula
                         (slipaj/maliyet ATR'nin kucuk bir kesri olmali, H2 tur2'deki
                         gibi ATR'nin kat kat uzeri DEGIL).
                      4. Nihai raporu yaz (on-kontrol 1-3 + ana test sonuclari, orijinal
                         gorev tanimindaki tum bolum basliklarinin AYNISI).
                      5. Eger bu turda da script calisirken/calistiktan sonra rapor
                         yazamadan bir hata ile karsilasirsan, elinden geldigince NEDEN
                         net bir sekilde (hangi adimda, ne hata mesaji) not et — rapor
                         uretemesen bile bu bilgi Orkestrator'un bir sonraki karari icin
                         onemli (durum dosyasi rapor_yolu alanina bunu koyamazsin ama en
                         azindan calisma dizininde kisa bir not dosyasi birakabilirsin,
                         orn. backtest_hipotez3_hata_notu.txt).

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\gorev_backtest_muhendisi_justin_gold_scalping_hipotez3_ana_test.md
  (bir onceki turun gorev dosyasi — kapsam maddeleri hala gecerli)
- C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json (on-kontrol sonuclari,
  TAMAM — dokunma)
- C:\MilaYatirim\Justin\backtest_hipotez3_main.py (yukaridaki BULGU disinda sozdizimsel
  tam — sadece BULGU'yu duzelt, sifirdan yeniden yazma)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json

BEKLENEN CIKTI     : C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez3_20260711.md
                      + C:\MilaYatirim\Justin\backtest_hipotez3_output.json

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait
hicbir dosya acilmayacak/referans alinmayacak. Calisma dizini yalniz C:\MilaYatirim\Justin\.

ONAY NOKTASI       : Bilgi notu — salt-okunur/analitik/offline backtest, canli sisteme
dokunus yok, Justin demo/arastirma asamasinda. Ertan'in onayina gerek yoktur. NOT:
Bu, ayni hipotez-3-ana-test adiminin 2. ardisik "hata" tekrarıdır (1. tekrar: kredi
kesintisi, ONAYLANMIS/bilinen sebep; bu 2.: sebep belirsiz). Eger bu 2. tur da
rapor uretmeden hata ile sonuclanirsa, Orkestrator bir 3. turu otomatik baslatmayacak —
bunun yerine Ertan'a somut bir bilgi notu/dikkat cekme yapacak (art arda ayni adimda
tekrarlayan, teshis edilemeyen hata potansiyel bir altyapi sorunu isareti olabilir).
