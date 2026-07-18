=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-13 15:15
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
                      Kural-Tabanli, Tam Tur 1, HIPOTEZ H1 ("Dar-Kanit M5-Giris")

GOREV              : Stratejist'in Tam Tur 1 raporundaki H1 hipotezini dogrula: H1/M30 yapisal
                      kanal (>=3 dokunus + EMA50/200 + MACD teyitli) rejim/giris-filtresi altinda,
                      M5 giris-zamanlamasiyla, simetrik iki yon (BUY+SELL). Sira/kapsam:
                      1. On-kontrol standardini (`justin_backtest_onkontrol_standardi.md`)
                         TAMAMEN uygula: (a) DST/saat-eslesme BAGIMSIZ dogrulamasi (Madde 1) —
                         Stratejist bunu bilerek Backtest Muhendisi'ne devretti, Adim 0'da da
                         yapilmadi; (b) S1 maliyet-orani GERCEK SL/TP mesafeleriyle yeniden
                         hesapla (bu raporda verilen proxy-hedef degil, Madde 2) — >=15-20x
                         saglanmazsa H1 ana teste GECMEDEN elenir; (c) SL/TP katsayilari H1'e
                         OZEL kalibre et, otomatik tasima YOK (Madde 3, ATR-bazli cerceve
                         disinda kesin katsayi Stratejist tarafindan verilmedi).
                      2. **Look-ahead bias kontrolu (KRITIK):** Pivot/swing tanimi (N=5 fraktal,
                         sag-pencereli) ileri-bakislidir — bir barin "swing" oldugu ancak 5 bar
                         SONRA kesinlesir. Backtest'te confirmed kanal/dokunus, olustugu andan
                         degil 5-bar-GECIKMELI olarak mevcutmus gibi modellenmelidir. Bu, ayri ve
                         acik bir bolumde dogrulanip raporlanmali.
                      3. Ana test: H1 veya M30'da onaylanmis kanal aktifken, kanalin M5
                         projeksiyonuna bir M5 barinin |kapanis-projeksiyon| <= 0,5xATR14_M5 ile
                         dokunmasi + bir sonraki M5 barinin trend yonunde kapanmasi = giris tetigi
                         (her iki yon: yukselen kanal->BUY, alcalan kanal->SELL). Cikis, uc
                         kosuldan ilk gerceklesen: (i) SL (~0,5xATR14_M5, dar; kesin katsayi
                         walk-forward'da kalibre edilecek), (ii) TP (S1-esigini gecen ufuktaki
                         gozlemlenen medyan hareket mesafesine yakin; kalibre edilecek), (iii)
                         kirilim-bazli erken-cikis (kanal pozisyon acikken KIRILIRSA SL/TP
                         beklenmeden kapat). (iii)'un dogru implement edildigini ayrica test et —
                         bu sabit-sureli cikistan farkli bir mekanizmadir, yanlis implementasyon
                         sonuclari onemli olcude etkiler.
                      4. Walk-forward (train/test/validation ayrimi), purged/embargolu, test seti
                         TEK KEZ kullanilir.
                      5. **Ek robustluk (Stratejist'in ONERISI, KARAR degil):** bu kombinasyon
                         sadece 2-8 bagimsiz kanala ve ~17 aylik (2025-02->2026-07) dar veri
                         donemine dayaniyor — mumkunse farkli/daha genis M5 veri donemi veya
                         farkli veri kaynagiyla bu bulgunun donem-etkisi mi yoksa kalici bir
                         ozellik mi oldugunu ayrica sina.
                      6. Islem frekansini (gerceklesen ay/yil bazinda islem sayisi) ayrica
                         raporla — yillik kanal sayisi dusuk (H1'de ~2,9-4,2/yil); scalping
                         beklentisi (sik islem) ile bu arasindaki gerilim Risk Analisti icin somut
                         sayiyla belgelenmeli.
                      7. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                         (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                         USD (Justin'e ait bagimsiz cerceve, MilaGold'un lot kuralindan farklidir
                         ve ona referansla belirlenmemistir).

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md
  (H1 bolumu + "Backtest Muhendisi'ne Devir Notlari" 1-8 — bu gorevin dogrudan kaynagi; H2/H3
  bolumleriyle KARISTIRILMAMASI gerekir, bu gorev SADECE H1'i kapsar)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_H1_20260713.md
(bolum yapisi: On-Kontrol Sonuclari [DST bagimsiz + S1 gercek-SL/TP, gecti/gecmedi ayrimi],
Look-Ahead Bias Dogrulamasi [ayri, acik bolum], Ana Test Tasarimi/Yontem, Sonuclar [walk-forward,
tum-donem/IS/OOS, PF/WR/islem sayisi], Islem Frekansi, Risk Analistine Iletim, Izolasyon Notu,
Onay Noktasi) + varsa ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin Tam Tur 1'idir (gunluk pipeline sayaci 1/5) — bu
backtest adimi sayaci DEGISTIRMEZ (sayaci degistiren Risk Analisti'nin nihai/turu-kapatan
karari). H2 ile PARALEL calistirilmasi Stratejist tarafindan onerildi (capraz-kontrol iki
varyantin ayni yonde/tutarli sonuc verip vermedigini gormek icin) — H2'yi BEKLEMENE gerek yok,
ama raporunda mumkunse ayni metrik tanimlariyla H2 ile karsilastirmaya hazir sonuc sun.
"Onceki-Tur-Ayrisma-Teyidi" bu turde N/A'dir (A ailesinin ilk tam turu, Stratejist raporu Bolum
"ONCEKI-TUR-AYRISMA-TEYIDI"nde bu acikca belirtildi) — bu kontrol maddesini bu raporda
tekrarlamana gerek yok.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap henuz baglanmadi). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
