=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-13 15:15
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
                      Kural-Tabanli, Tam Tur 1, HIPOTEZ H3 ("M30-Yukselen Odakli Asimetrik
                      Filtre")

GOREV              : Stratejist'in Tam Tur 1 raporundaki H3 hipotezini dogrula: SADECE M30'da
                      onaylanmis (>=3 dokunus + EMA50>EMA200 + MACD_line>MACD_signal) YUKSELEN
                      kanal aktifken, M15 giris-zamanlamasiyla, YALNIZCA UZUN/BUY (asimetrik,
                      alcalan kanal/SELL tarafi bu hipotezde YOK). Sira/kapsam:
                      1. On-kontrol standardini (`justin_backtest_onkontrol_standardi.md`)
                         TAMAMEN uygula: (a) DST/saat-eslesme BAGIMSIZ dogrulamasi (Madde 1); (b)
                         S1 maliyet-orani GERCEK SL/TP mesafeleriyle yeniden hesapla (Madde 2) —
                         >=15-20x saglanmazsa H3 ana teste GECMEDEN elenir (alt-kumeye ozel S1:
                         M30->M15 yukselen icin 15x=~4,4 saat, 20x=~7,2 saat referans, ama GERCEK
                         SL/TP ile dogrula); (c) SL/TP katsayilari bu alt-kumeye OZEL kalibre et,
                         H2'nin genel TP kalibrasyonundan farkli olabilir, otomatik tasima YOK
                         (Madde 3).
                      2. **Look-ahead bias kontrolu (KRITIK, H1/H2 ile ortak gerekce):**
                         Pivot/swing tanimi ileri-bakislidir; confirmed kanal 5-bar-GECIKMELI
                         olarak modellenmelidir. Ayri, acik bir bolumde raporla.
                      3. Ana test: giris mekanigi H2 ile AYNI (M30->M15, kanal cizgisine M15
                         dokunusu + bir sonraki M15 barinin yukari kapanmasi), ama SADECE yukselen
                         kanal + BUY yonunde uygulanir. Cikis H2 ile ayni uc-kosullu sema (SL / TP
                         / kirilim-bazli erken-cikis, ATR14_M15 bazli), TP mesafesini bu alt-kume
                         icin AYRI kalibre edebilirsin (devam-orani bu alt-kumede daha tutarli
                         gozlemlendigi icin).
                      4. **Out-of-sample/walk-forward standardi digerlerinden DAHA SIKI
                         uygulanmali (Stratejist'in acik talebi):** bu hipotezin dayandigi
                         devam-orani (%63-80) / tersine-donus-orani (%13-33) bulgusu n=15-20
                         KUCUK orneklemden geliyor — in-sample gorunen oranin out-of-sample'da
                         tekrar edip etmedigini ozellikle sinamali, tek bir train/test bolunmesine
                         guvenme, purged/embargolu CAPRAZ dogrulama (birden fazla fold) tercih et.
                      5. Islem frekansini (gerceklesen ay/yil bazinda islem sayisi) ayrica
                         raporla — bu, uc varyant arasinda EN DUSUK islem frekansina sahip olma
                         ihtimali yuksek (sadece yukselen-M30 + uzun taraf alt-kumesi); scalping
                         beklenen islem sikligiyla uyumu Risk Analisti'nin degerlendirebilmesi
                         icin somut sayi sart.
                      6. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                         (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                         USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md
  (H3 bolumu + "Backtest Muhendisi'ne Devir Notlari" 1-8, ozellikle Madde 6 — bu gorevin
  dogrudan kaynagi; H1/H2 bolumleriyle KARISTIRILMAMASI gerekir, bu gorev SADECE H3'u kapsar)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H3_20260713.md
(bolum yapisi: On-Kontrol Sonuclari [DST bagimsiz + S1 gercek-SL/TP], Look-Ahead Bias
Dogrulamasi, Ana Test Tasarimi/Yontem, Sonuclar [SIKI out-of-sample/cok-fold walk-forward,
PF/WR/islem sayisi, in-sample vs out-of-sample devam-orani karsilastirmasi], Islem Frekansi,
Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi) + varsa ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin Tam Tur 1'idir (gunluk pipeline sayaci 1/5) — bu
backtest adimi sayaci DEGISTIRMEZ. H3, H1/H2'ye gore daha dusuk guven duzeyiyle (ONCELIK:
2-Orta) test ediliyor; RED gelirse bu "asimetrik filtre fikri calismiyor" olarak okunmali, "A
ailesi olu" olarak DEGIL (H1/H2 ile karistirilmamali — Stratejist'in atif-netligi notu, raporunda
bu ayrimi acikca yap). "Onceki-Tur-Ayrisma-Teyidi" bu turde N/A'dir (A ailesinin ilk tam turu).

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap henuz baglanmadi). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
