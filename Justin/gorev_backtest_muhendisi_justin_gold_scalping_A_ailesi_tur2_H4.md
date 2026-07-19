=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-19 09:20
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
                      Kural-Tabanli, TUR 2 / ADIM 2, HIPOTEZ H4 ("Momentum-Esikli Teyit")

GOREV              : Stratejist'in Tur 2 raporundaki H4 hipotezini dogrula: H1/M30 yapisal kanal
                      (>=3 dokunus + EMA50/200 + MACD teyitli, aktif/kirilmamis) rejim/giris-
                      filtresi altinda, dokunus barindan SONRAKI barin (i+1) hem trend yonunde
                      kapanmasi HEM DE |kapanis[i+1]-acilis[i+1]|/ATR14(i+1) >= k (govde/ATR
                      conviction esigi) sarti. Sira/kapsam:
                      1. On-kontrol standardini (`justin_backtest_onkontrol_standardi.md`)
                         TAMAMEN uygula: (a) DST/saat-eslesme BAGIMSIZ dogrulamasi (Madde 1) —
                         Tam Tur 1'den DEVRALINMAZ, yeniden yapilmali; (b) S1 maliyet-orani
                         GERCEK SL/TP mesafeleriyle yeniden hesapla (Madde 2) — >=15-20x
                         saglanmazsa H4 ana teste GECMEDEN elenir; (c) SL/TP katsayilari H4'e
                         OZEL kalibre et, Tam Tur 1'den (H1/H2/H3) HICBIR SL/TP otomatik
                         TASINMAZ (Madde 3).
                      2. **Look-ahead bias kontrolu (KRITIK, Tam Tur 1'den degismedi):** kanal/
                         pivot tanimi ayni (N=5 sag-pencereli fraktal); confirmed kanal/dokunus
                         5-bar-GECIKMELI olarak modellenmeli, ayri/acik bir bolumde raporlanmali.
                      3. **Birincil test:** M15 giris, H1 ve M30 HTF (HER IKI yon), **k=1,0x ATR14**
                         esigiyle. Bu kombinasyon, Tam Tur 1'in en genis-orneklemli/en net RED
                         aldigi H2 (M15-giris) ile DOGRUDAN karsilastirilabilir olacak sekilde
                         bilincli secildi — raporda bu paralellik acikca vurgulanmali ("mekanizma
                         degisince sonuc gercekten degisiyor mu" karsilastirmasi).
                      4. **Duyarlilik/ek hucre:** k=0,5x ATR14 ile ayni mekanizma icinde
                         karsilastirma (ayri hipotez degil, tek raporda iki k-degeri).
                      5. **Ikincil/capraz-kontrol:** M5 giris (Arastirmaci'nin en belirgin
                         hizlanma bulgusu M5'teydi, ama M5'in bagimsiz kanal sayisi M15'ten kucuk
                         [2-8 vs 6-18] — sonuc M15'e gore daha kirilgan kabul edilmeli, ayri
                         belirtilmeli). M1 KULLANILMIYOR (Stratejist'in gerekcesi: en kirilgan
                         veri parcasi, birincil test icin yeterli temel degil).
                      6. Giris: tetik (yon + govde/ATR esigi) olustugunda i+1 barinin kapanisinda.
                         Cikis, uc kosuldan ilk gerceklesen: (i) SL ATR14(ltf)-bazli dar mesafe,
                         (ii) TP bu YENI (kucultulmus) olay kumesinin kendi N-bar-ileri medyan
                         hareket olcumune gore (Tam Tur 1 TP degerleri OTOMATIK TASINMAZ),
                         (iii) kirilim-bazli erken cikis (kanal pozisyon acikken KIRILIRSA SL/TP
                         beklenmeden kapat — bu Tam Tur 1'in AYNI kurali, H5'in "kanala-geri-
                         donus" kuraliyla KARISTIRILMAMALI).
                      7. Walk-forward (train/validation/test), purged/embargolu, test seti TEK
                         KEZ kullanilir — Tam Tur 1 H1/H2'nin split metodolojisiyle tutarli.
                      8. **Orneklem kuculmesi UYARISI (KRITIK):** momentum k=1,0 esigi olay
                         sayisini baseline'a gore ~%87-90 azaltiyor (orn. M15 H1-alcalan:
                         20.599->2.235). Bagimsiz kanal temeli (6-18) DEGISMEZ ama tetik-basi
                         olay sayisi ciddi kuculur — n kucukse guven araligi genis raporlanmali,
                         "yeterli n" varsayilmamali.
                      9. Islem frekansini (gerceklesen ay/yil bazinda islem sayisi) ayrica
                         raporla — scalping beklentisiyle (sik islem) gerilim Risk Analisti icin
                         somut sayiyla belgelenmeli.
                      10. Lot/risk: `justin_gecmis_calisma.md` geregi islem-basi risk kasa x %1
                          (ust sinir), taban 0,01 lot, her 2.000 USD kasa = +0,01 lot, kasa=2.000
                          USD.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md
- C:\MilaYatirim\Justin\backtest_A_ailesi_H2.py (yapi/kapsam referansi — FAZ 0-9, Tam Tur 1'in
  en genis-orneklemli varyanti, karsilastirma tabani)

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md
  (HIPOTEZ H4 bolumu + "BACKTEST MUHENDISI ICIN NOTLAR" 1-10 — bu gorevin dogrudan kaynagi;
  H5/H6 bolumleriyle KARISTIRILMAMASI gerekir, bu gorev SADECE H4'u kapsar)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_tur2_H4_20260719.md
(bolum yapisi: On-Kontrol Sonuclari [DST bagimsiz + S1 gercek-SL/TP, gecti/gecmedi ayrimi],
Look-Ahead Bias Dogrulamasi [ayri, acik bolum], Ana Test Tasarimi/Yontem [k=1,0 birincil, k=0,5
duyarlilik], Sonuclar [walk-forward, tum-donem/IS/OOS, PF/WR/islem sayisi, H2-ile-karsilastirma],
Orneklem Buyuklugu/Guven Araligi Notu, Islem Frekansi, Risk Analistine Iletim, Izolasyon Notu,
Onay Noktasi) + varsa ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin TUR 2'sidir (Tam Tur 1, 13-14 Temmuz, 3/3 RED
sonuclanmisti; gunluk tam-tur sayaci 1/5'ten devam eder, bu backtest adimi sayaci DEGISTIRMEZ —
sayaci degistiren Risk Analisti'nin nihai/turu-kapatan karari). H5 (on-tarama sartiyla) PARALEL
gorevlendirildi — H4'un H5'i BEKLEMESINE gerek yok, ikisi bagimsiz ilerleyebilir. H6 (hibrit,
dusuk oncelik) bu asamada gorevlendirilmiyor — Stratejist'in acik onerisi geregi H4/H5'in
BAGIMSIZ sonuclari alinmadan baslatilmamali.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap henuz baglanmadi). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
