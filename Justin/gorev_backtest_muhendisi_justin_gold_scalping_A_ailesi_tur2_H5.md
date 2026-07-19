=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-19 09:20
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following)
                      icinde kirilim-tabanli bir giris varyanti (Ertan'in A/C duzeltmesi geregi
                      C ailesinin ayri/bagimsiz canlanmasi DEGIL), TUR 2 / ADIM 2, HIPOTEZ H5
                      ("Kanal-Disi Kirilim Girisi")

GOREV              : Stratejist'in Tur 2 raporundaki H5 hipotezini dogrula. Bu hipotez
                      Arastirmaci tarafindan bu turde HIC OLCULMEDI — asagidaki ON-TARAMA adimi
                      ZORUNLU ilk adimdir, sonucu olumluysa ana teste gecilir.

                      **ADIM 0 — ON-TARAMA (ZORUNLU, ana testten ONCE):** basit bir olay-sayimi/
                      S1-proxy taramasi yap: H1/M30'da onaylanmis (>=3 dokunus + EMA50/200 +
                      MACD teyitli, aktif/kirilmamis) kanal varken, kanalin trend-yonundeki DIS
                      sinir projeksiyonuna (yukselen kanalda UST, alcalan kanalda ALT) bir M15
                      barinin kapanisinin, kanalin ICINDEN DISINA, trend yonunde, en az
                      0,5xATR14(M15) mesafede tasma olayi kac kez gerceklesiyor — hangi HTF/LTF/
                      yon kombinasyonunda kac tane. **Eger olay sayisi cok kucukse (orn. tek
                      haneli, Tam Tur 1'in H1'inin 1-8 kanalla yasadigi kirilganliga benzer),
                      bunu ACIKCA raporla ve ana teste GECME — bu durumu erken bildir, Risk
                      Analisti/Orkestrator'un karar vermesini bekle.** Yeterli (tek haneli
                      olmayan) sayida olay varsa ADIM 1'e gec.

                      **ADIM 1 — ON-KONTROL STANDARDI** (`justin_backtest_onkontrol_standardi.md`):
                      (a) DST/saat-eslesme BAGIMSIZ dogrulamasi (Madde 1); (b) S1 maliyet-orani
                      GERCEK SL/TP mesafeleriyle (Madde 2) — >=15-20x saglanmazsa H5 ana teste
                      GECMEDEN elenir; (c) SL/TP katsayilari H5'e OZEL kalibre et, otomatik tasima
                      YOK (Madde 3).

                      **ADIM 2 — LOOK-AHEAD BIAS:** kanal/pivot tanimi Tam Tur 1'den degismedi
                      (N=5 sag-pencereli fraktal); AYRICA kirilim ANI'nin kendisinin gercek-
                      zamanli ANINDA mi tespit edildigi, yoksa kanal cizgisinin kendisinin zaten
                      5-bar-gecikmeli mi olustugu netlestirilmeli (ikinci durumda gecikme
                      MODELLENMELI) — bu H5'e ozel ek bir netlik sorusudur.

                      **ADIM 3 — ANA TEST (on-tarama + on-kontrol GECERSE):**
                      - Birincil: M15 giris, H1/M30 HTF, HER IKI yon (simetrik). M5 ikincil/
                        capraz-kontrol. M1 KULLANILMIYOR.
                      - Giris: kirilim barinin KENDI kapanisinda (TEK bar tetigi, ek teyit bari
                        BEKLENMEZ — bu birincil tasarimdir; isterse "kirilim + bir sonraki barin
                        da ayni yonde kapanmasi" varyanti duyarlilik testi olarak eklenebilir).
                      - Cikis, uc kosuldan ilk gerceklesen: (i) SL kirilan sinirin GERISINE
                        (~0,3-0,5xATR14, false-breakout icin hizli cikis), (ii) TP ATR14-bazli
                        dinamik hedef, bu YENI olay kumesinin kendi N-bar-ileri medyan hareket
                        olcumune gore (Arastirmaci bu olay TURUNU hic olcmedi, sifirdan hesapla),
                        (iii) **kanala-geri-donus erken cikis** (H5'e ozel — fiyat pozisyon
                        acikken kanalin ICINE GERI DONERSE SL/TP beklenmeden kapat; bu H4'un
                        "kanal kirilirsa cik" kuralinin TERS-CEVRILMISIDIR, IKISI KARISTIRILMAMALI).
                      - Walk-forward (train/validation/test), purged/embargolu, test seti TEK KEZ.
                      - False-breakout sikligi (SL'e takilma orani) ayrica olculmeli.
                      - Islem frekansi (ay/yil bazinda) ayrica raporlanmali — kirilim olaylari
                        dokunus olaylarindan daha seyrek olabilir, scalping beklentisiyle gerilim
                        H4'ten de yuksek olabilir.
                      - Lot/risk: `justin_gecmis_calisma.md` geregi (kasa 2.000 USD, islem-basi
                        risk ust siniri %1, taban lot 0,01 + her 2.000 USD=+0,01 lot).

                      **A/C SINIR NETLIGI (ZORUNLU):** raporda bu tetigin daima "A ailesi ICINDE
                      kirilim-tabanli bir giris varyanti" olarak adlandirilmasi, "C ailesinin
                      canlanmasi" gibi okunmamasi gerekir (Ertan'in A/C duzeltmesi geregi).

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md
- C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md
- C:\MilaYatirim\Justin\backtest_A_ailesi_H2.py (yapi/kapsam referansi — FAZ 0-9)

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md
  (HIPOTEZ H5 bolumu + "BACKTEST MUHENDISI ICIN NOTLAR" 1-10 — bu gorevin dogrudan kaynagi;
  H4/H6 bolumleriyle KARISTIRILMAMASI gerekir, bu gorev SADECE H5'i kapsar)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_A_ailesi_tur2_H5_20260719.md
(bolum yapisi: On-Tarama Sonucu [olay sayisi/kombinasyon, devam/dur karari ve gerekcesi],
[eger devam edildiyse] On-Kontrol Sonuclari, Look-Ahead Bias Dogrulamasi, Ana Test Tasarimi/
Yontem, Sonuclar [walk-forward, tum-donem/IS/OOS, PF/WR/islem sayisi, false-breakout sikligi],
Islem Frekansi, A/C Sinir Netligi Notu, Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi)
+ varsa ham veri/script dosyalari. **On-tarama olumsuz cikarsa** (olay sayisi cok kucuk): sadece
on-tarama bolumu + kisa gerekce yeterli, ana teste GECME.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI: Bu, A ailesinin TUR 2'sidir (gunluk tam-tur sayaci 1/5'ten devam eder,
bu backtest adimi sayaci DEGISTIRMEZ). H4 PARALEL gorevlendirildi — H5'in H4'u BEKLEMESINE gerek
yok. H6 (hibrit, dusuk oncelik) bu asamada gorevlendirilmiyor — Stratejist'in acik onerisi geregi
H4/H5'in BAGIMSIZ sonuclari alinmadan baslatilmamali. Bu hipotez A ailesinin bir giris-tetigi
varyanti olarak ele alinir, C (Breakout Order, Proje 9) ile karistirilmamalidir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi (on-
tarama dahil), canli sisteme dokunus yok, Justin arastirma asamasinda (canli/demo hesap henuz
baglanmadi). 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi
konusu degil, etki alani dar (yalniz Justin klasoru) -> STOP-genis/bilgi-notu kategorisi, Ertan
onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.
