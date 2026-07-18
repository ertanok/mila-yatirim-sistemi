=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-13 15:31
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
                      Kural-Tabanli, Tam Tur 1, HIPOTEZ H1 ("Dar-Kanit M5-Giris") — TEKRAR
                      DENEME (onceki gorev_id: backtest_muhendisi_20260713_1816, durum: hata)

GOREV              : Onceki H1 denemesi tamamlanmadan HATA ile sonuclandi. Incelemede su
                      goruldu: `C:\MilaYatirim\Justin\backtest_A_ailesi_H1.py` scripti SADECE
                      kanal-tespiti fazini (naive+causal, look-ahead-duzeltmeli known_idx dahil)
                      calistirip `bt_h1_step_channels.json` dosyasini basariyla yazmis ve
                      "KANAL TESPITI TAMAMLANDI" ciktisiyla mt5.shutdown() ile sonlanmis —
                      yani bu kismi calisti/hata vermedi. Ancak orijinal gorevin istedigi
                      TAM kapsam (on-kontrol Madde 1 DST-bagimsiz dogrulama, Madde 2 S1
                      gercek-SL/TP maliyet-orani, M5 giris-tetigi ana test, walk-forward
                      SL/TP kalibrasyonu, kirilim-bazli erken-cikis dogrulamasi, nihai .md
                      raporu) bu scriptte YOK — karsilastirma icin H2'nin tam kapsamli
                      FAZ 0-9 yapisina bak (`backtest_A_ailesi_H2.py`, ayni kaynak rapordan,
                      basariyla tamamlandi/output+csv uretti). H1'in nicin bu noktada
                      durdugu/hata verdigi (ajan sureci mi kesildi, kod mu eksik birakildi,
                      calistirilmamis bir sonraki adimda mi patladi) net degil; bu gorev hem
                      TEKRAR DENEME hem de KOK-NEDEN NETLESTIRME'yi kapsar.

                      Somut istekler:
                      1. Var olan `bt_h1_step_channels.json` (naive+causal kanal listeleri,
                         known_idx/break_idx/tradeable alanlari dahil) YENIDEN HESAPLAMAYA
                         GEREK YOK ise dogrudan kullanilabilir (maliyetli adim zaten tamam) —
                         ama once bu dosyanin guncel/tutarli oldugunu (script parametreleriyle
                         uyumlu) dogrula.
                      2. H2'nin FAZ yapisiyla AYNI KAPSAMDA H1'i tamamla: FAZ1 (DST bagimsiz
                         dogrulama), FAZ4-benzeri (S1 gercek SL/TP ile), FAZ5 (train/val/test
                         purged/embargolu ayrim), FAZ6 (M5 giris-tetigi + uc-kosullu cikis trade
                         simulasyonu — kanal cizgisi M5 projeksiyonuna dokunma + bir sonraki M5
                         barin trend yonunde kapanmasi), FAZ7 (walk-forward SL/TP kalibrasyonu),
                         FAZ8 (kirilim-bazli erken-cikis dogrulama ornekleri), FAZ9 (rapor JSON).
                      3. **Hata toleransi (yeni istek):** script'i try/except ile sarmalayip,
                         herhangi bir asamada exception olursa TAM traceback'i
                         `backtest_A_ailesi_H1_hata_log.txt` dosyasina yaz (once bu turde
                         boyle bir log yoktu — bu yuzden onceki hatanin kok nedeni gorulemedi).
                         Basarili tamamlansa bile bu dosya olusturulmaz/bosaltilir.
                      4. Islem frekansi, dar-orneklem robustluk notu (Devir Notu 5) ve
                         look-ahead bias ayri bolumu de dahil olmak uzere BEKLENEN CIKTI
                         formatini (asagida) uygula.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md
- C:\MilaYatirim\Justin\backtest_A_ailesi_H2.py (yapi/kapsam referansi — FAZ 0-9)
- C:\MilaYatirim\Justin\bt_h1_step_channels.json (onceki denemeden kalan, tekrar kullanilabilir
  ara-sonuc)

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md
  (H1 bolumu + "Backtest Muhendisi'ne Devir Notlari" 1-8 — orijinal gorev degismedi, sadece
  tekrar deneniyor)
- C:\MilaYatirim\Justin\gorev_backtest_muhendisi_justin_gold_scalping_A_ailesi_H1.md (orijinal
  gorev, bu dosya onu GUNCELLEMEZ/DEGISTIRMEZ, ek/tekrar cagridir)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H1_20260713.md
(bolum yapisi: On-Kontrol Sonuclari [DST bagimsiz + S1 gercek-SL/TP, gecti/gecmedi ayrimi],
Look-Ahead Bias Dogrulamasi [ayri, acik bolum], Ana Test Tasarimi/Yontem, Sonuclar [walk-forward,
tum-donem/IS/OOS, PF/WR/islem sayisi], Islem Frekansi, Risk Analistine Iletim, Izolasyon Notu,
Onay Noktasi) + varsa ham veri/script dosyalari. Basarisiz olursa
`backtest_A_ailesi_H1_hata_log.txt` + kisa bir aciklama (rapor yerine) yeterli.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait
hicbir dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin Tam Tur 1'idir (gunluk pipeline sayaci 1/5) — bu
TEKRAR DENEME bir yeni tur SAYILMAZ (sayaci degistiren Risk Analisti'nin nihai/turu-kapatan
karari, henuz o asamaya gelinmedi). H2 (muhtemelen hala calisiyor/rapor asamasinda) ve H3
(henuz baslamadi) bu tekrar denemeyi BEKLEMEZ, paralel/bagimsiz ilerleyebilir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi
(tekrar deneme), canli sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap
henuz baglanmadi). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu
kategorisi, Ertan onayi gerekmez. Rapor (veya hata-log) uretildiginde Ertan'a Telegram bilgi
notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.
