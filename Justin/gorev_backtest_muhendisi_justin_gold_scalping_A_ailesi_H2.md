=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-13 15:15
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
                      Kural-Tabanli, Tam Tur 1, HIPOTEZ H2 ("Genis-Orneklem M15-Giris")

GOREV              : Stratejist'in Tam Tur 1 raporundaki H2 hipotezini dogrula: H1'deki AYNI
                      kanal-onay mekanizmasi (>=3 dokunus + EMA50/200 + MACD teyitli, H1 veya
                      M30 ufkunda), ama M15 giris-zamanlamasiyla, simetrik iki yon (BUY+SELL).
                      Sira/kapsam:
                      1. On-kontrol standardini (`justin_backtest_onkontrol_standardi.md`)
                         TAMAMEN uygula: (a) DST/saat-eslesme BAGIMSIZ dogrulamasi (Madde 1) —
                         H1'den DEVRALINAMAZ, bu ayri bir giris-ufku/zaman-projeksiyonu oldugu
                         icin bagimsiz dogrulanmali; (b) S1 maliyet-orani GERCEK SL/TP
                         mesafeleriyle yeniden hesapla (proxy degil, Madde 2) — >=15-20x
                         saglanmazsa H2 ana teste GECMEDEN elenir; (c) SL/TP katsayilari H2'ye
                         OZEL kalibre et, H1'den OTOMATIK TASIMA YOK (Madde 3).
                      2. **Look-ahead bias kontrolu (KRITIK, H1 ile ayni gerekce):** Pivot/swing
                         tanimi (N=5 fraktal, sag-pencereli) ileri-bakislidir; confirmed kanal
                         5-bar-GECIKMELI olarak modellenmelidir. Ayri, acik bir bolumde raporla.
                      3. Ana test: kanal aktifken, kanalin M15 projeksiyonuna bir M15 barinin
                         |kapanis-projeksiyon| <= 0,5xATR14_M15 ile dokunmasi + bir sonraki M15
                         barinin trend yonunde kapanmasi = giris tetigi (her iki yon). Cikis, H1
                         ile ayni uc-kosullu sema (SL / TP / kirilim-bazli erken-cikis),
                         ATR14_M15 bazli farkli ufuk/mesafe olcegiyle. Kirilim-bazli erken-cikisin
                         dogru implement edildigini ayrica test et.
                      4. Walk-forward (train/test/validation ayrimi), purged/embargolu, test seti
                         TEK KEZ kullanilir.
                      5. **Scalping-tanimi gerilimi (KRITIK, bu hipotez icin en dogrudan
                         gerilim):** Tutma suresi beklentisi 4,4-10,3 saat — Ertan'in Cevap 3
                         (scalping karakteri KESIN, "dakikalar-birkac saat") ile sinir-bolgesinde.
                         Bu gerilimi ACIKCA, ayri bir bolumde raporla; sonuc otomatik
                         "scalping-uyumlu" olarak KABUL EDILMEMELI — Risk Analisti'nin karar
                         verebilmesi icin somut sayi (gerceklesen medyan tutma suresi) sun.
                      6. Islem frekansini (gerceklesen ay/yil bazinda islem sayisi) ayrica
                         raporla — yillik kanal sayisi H1 ile ayni kaynaktan (M30'da ~3,5-6,8/yil).
                      7. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                         (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                         USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md
  (H2 bolumu + "Backtest Muhendisi'ne Devir Notlari" 1-8 — bu gorevin dogrudan kaynagi; H1/H3
  bolumleriyle KARISTIRILMAMASI gerekir, bu gorev SADECE H2'yi kapsar)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H2_20260713.md
(bolum yapisi: On-Kontrol Sonuclari [DST bagimsiz + S1 gercek-SL/TP], Look-Ahead Bias
Dogrulamasi, Ana Test Tasarimi/Yontem, Sonuclar [walk-forward, PF/WR/islem sayisi],
Scalping-Tanimi Gerilimi [ayri, acik bolum — medyan tutma suresi], Islem Frekansi, Risk
Analistine Iletim, Izolasyon Notu, Onay Noktasi) + varsa ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin Tam Tur 1'idir (gunluk pipeline sayaci 1/5) — bu
backtest adimi sayaci DEGISTIRMEZ. H1 ile PARALEL calistirilmasi Stratejist tarafindan onerildi
(capraz-kontrol) — H1'i BEKLEMENE gerek yok, ama raporunda mumkunse ayni metrik tanimlariyla H1
ile karsilastirmaya hazir sonuc sun. Eger H2 RED gelirse bu "A ailesi olu" degil "scalping-tanimi
gerilimi" olarak yorumlanmalidir (Stratejist'in atif-netligi notu) — raporunda bu ayrimi acikca
yap. "Onceki-Tur-Ayrisma-Teyidi" bu turde N/A'dir (A ailesinin ilk tam turu).

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap henuz baglanmadi). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
