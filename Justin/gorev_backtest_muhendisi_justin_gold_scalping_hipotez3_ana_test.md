=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-11 00:11
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — HIPOTEZ 3, ANA TEST (on-kontroller
                      1-3 zaten GECILDI, bu tur SADECE ana testi calistirip raporu tamamlamak
                      icindir — sifirdan baslama)

GOREV              : Onceki tur (gorev_id: backtest_muhendisi_20260710_2202, "hata" ile
                      sonuclandi, 3 basarisiz deneme sonrasi basarisiz/ klasorune tasindi)
                      HIPOTEZ 3'un ANA TESTINI tamamla.

                      ONEMLI BAGLAM: Onceki turun basarisiz olma sebebi kendi calismandaki bir
                      hata DEGIL — Anthropic hesap kredisi o donemde tukenmisti ("Credit balance
                      is too low", 3 denemenin ucunde de). Kredi sorunu artik cozuldu. Yani
                      onceki turun urettigi dosyalar bir "yarim kalmis hata" degil, "kesintiye
                      ugramis ama teknik olarak saglam gorunen" bir calisma olarak ele alinmali.

                      Onceki tur ne yapti / nerede kaldi (SIFIRDAN YENIDEN YAZMA — asagidaki
                      TURN VERIMLILIGI maddesine bak):
                      1. C:\MilaYatirim\Justin\backtest_hipotez3_precheck.py yazildi ve
                         BASARIYLA calistirildi ->
                         C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json uretildi.
                         Bu dosya TAMAM ve TUTARLI gorunuyor (BEN/Orkestrator inceledim):
                         - On-kontrol 1 (saat esleme/DST): TAMAMLANDI, 4. kez bagimsiz dogrulandi.
                         - On-kontrol 2 (coklu-karsilastirma, resmi FDR+Bonferroni, IS-donem
                           verisinde BAGIMSIZ yeniden hesaplanmis): 48 testten FDR ile 25,
                           Bonferroni ile 14 hucre hayatta kaliyor.
                         - On-kontrol 3 (seans-filtreli IS-donem alt-orneklem testi): 11 hucre
                           nihai olarak hayatta kaliyor, TUMU M1 (M5'te SIFIR hucre hayatta
                           kaliyor — gorev kapsaminin "M1 birincil" beklentisiyle tutarli).
                         - "on_kontrol_ozet_karar.karar": "ANA_TESTE_GECILEBILIR".
                      2. Bu karara dayanarak C:\MilaYatirim\Justin\backtest_hipotez3_main.py
                         yazildi (precheck'ten SONRA, dosya zaman damgasi bunu dogruluyor).
                         BEN (Orkestrator) bu scripti okudum — sozdizimsel olarak TAM gorunuyor
                         (basindan sonuna kadar: MT5 baglantisi, causal ozellik/rejim/streak/
                         buyuk-bar hesaplama, tick-bazli maliyet modeli [H1/H2'nin duzeltilmis
                         get_tick_quote mantigini ZATEN icinde barindiriyor — zaman-uyusmazligi
                         kontrolu MEVCUT, satir ~229-233], 3 sinyal ailesi [GENEL-FADE,
                         STREAK-FADE L2-5, BIGBAR-FADE], IS/OOS + 6-pencere walk-forward,
                         rejim kirilimi POST-HOC, minimum orneklem uyarilari, tam islem logu,
                         ve en sonda json.dump ile OUT_PATH'e yazma + mt5.shutdown()).
                      3. ANCAK: C:\MilaYatirim\Justin\backtest_hipotez3_output.json HENUZ
                         YOK — yani bu script muhtemelen HIC CALISTIRILMADI ya da calistirma
                         sirasinda/hemen sonrasinda kredi tukendi. Nihai rapor
                         (backtest_muhendisi_raporu_justin_gold_scalping_hipotez3_*.md) de
                         HENUZ YAZILMADI.

                      YAPMAN GEREKEN:
                      1. backtest_hipotez3_precheck.py ve backtest_hipotez3_main.py'yi OKU
                         (yeniden yazma) — kendi mantigini/kapsam uyumunu hizlica dogrula.
                      2. Eger script gozden gecirmende gercek bir hata/tutarsizlik BULURSAN
                         (ornegin H2 tur2'de bulunan slipaj/tick-zaman-uyusmazligi turu bir
                         kok-neden), sadece ilgili bolumu duzelt — SIFIRDAN YENIDEN YAZMA.
                         Bulgunu raporda acikca belirt.
                      3. Hata bulmazsan (script saglam gorunuyorsa): backtest_hipotez3_main.py'yi
                         CALISTIR (py komutu, bkz. CLAUDE.md Teknik Altyapi — Python 3.14).
                         MT5'e dogrudan mt5.initialize() ile baglan (RDP/GUI gerekmez, 8 Temmuz
                         dogrulandi).
                      4. Cikan backtest_hipotez3_output.json'daki buyukluklerin FIZIKSEL OLARAK
                         TUTARLI oldugunu dogrula (slipaj/maliyet ATR'nin kucuk bir kesri
                         mertebesinde olmali, H2 tur2'deki gibi ATR'nin kat kat uzeri DEGIL) —
                         bu kontrolu gecmeden "calisiyor" degerlendirmesi yapma.
                      5. Nihai raporu yaz — on-kontrol 1-3 sonuclarini (precheck_output.json'dan,
                         AYRIK/gecti-gecmedi olarak) ve ana test sonuclarini (3 sinyal ailesi,
                         IS/OOS, walk-forward, rejim post-hoc kirilimi, minimum orneklem
                         uyarilari) birlikte raporla. Orijinal gorev tanimindaki (asagida
                         referans verilen) TUM kapsam maddeleri gecerliligini korur.
                      6. TURN VERIMLILIGI ONEMLI: precheck.py/precheck_output.json'a DOKUNMA
                         (zaten tamam), main.py'yi de gercek bir hata bulmadikca SIFIRDAN
                         YENIDEN YAZMA — onceki tur muhtemelen script'i yazmaya kadar turn
                         harcadi, kredi kesintisi calistirma asamasinda/civarinda oldu; bu
                         turda GEREKSIZ TEKRARDAN KACIN, dogrudan calistirma + dogrulama +
                         rapor adimlarina odaklan.
                      7. Rapor tamamlanana/output.json uretilene kadar bu gorev "tamamlandi"
                         sayilmaz.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\gorev_backtest_muhendisi_justin_gold_scalping_hipotez3.md (orijinal
  gorev tanimi, kapsam maddeleri birebir gecerli — ON-KONTROL SIRASI, ANA TEST TASARIMI, ASAMA
  SIRASI/ML KAPISI, OVERFITTING GUVENLIK AGI, ALT-ORNEKLEM KUCULMESI, TAM ISLEM LOGU bolumleri)
- C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json (on-kontrol sonuclari, TAMAM —
  degistirme, sadece rapora tasi)
- C:\MilaYatirim\Justin\backtest_hipotez3_main.py (ana test scripti, sozdizimsel TAM gorunuyor —
  once oku/dogrula, gercek hata yoksa DOGRUDAN CALISTIR)
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md (bu gorevin dogrudan
  kaynagi — Bolum 5, GOREV TANIMI)
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez2_20260711.md
  (yontem/titizlik + tick-maliyet-duzeltme referansi — H2'deki slipaj kok-nedeni main.py'de
  ZATEN duzeltilmis gorunuyor, sadece dogrula)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\backtest_hipotez3_precheck_output.json

BEKLENEN CIKTI     : C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez3_20260711.md
                      (bolum yapisi H1/H2 raporlariyla tutarli: On-Kontrol 1-3 Sonuclari [ayrik,
                      gecti/gecmedi], Ana Test Tasarimi/Yontem, 3 Sinyal Ailesi Sonuclari
                      [tum-donem/IS/OOS/walk-forward/rejim-post-hoc/minimum-orneklem], Fiziksel
                      Tutarlilik Kontrolu Notu, Risk Analistine Iletim, Izolasyon Notu, Onay
                      Noktasi) + C:\MilaYatirim\Justin\backtest_hipotez3_output.json (ham veri,
                      script zaten bu yola yaziyor)

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait
hicbir dosya acilmayacak/referans alinmayacak. Calisma dizini yalniz C:\MilaYatirim\Justin\.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi
(script zaten yazilmis, sadece calistirma+dogrulama+raporlama), canli sisteme dokunus yok,
Justin demo/arastirma asamasinda (henuz canli hesap yok). Ertan'in onayina gerek yoktur.
Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator
tarafindan dusulecektir.
