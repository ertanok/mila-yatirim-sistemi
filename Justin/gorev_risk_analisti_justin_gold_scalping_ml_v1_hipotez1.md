=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 14:20
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 1 (LightGBM ikili yon-tahmini, N=16/k=1,5xATR14-M15)
                      Pipeline adimi: 4/4 (son adim) — Yol1 metodolojisi (Arastirmaci→Stratejist→
                      Backtest Muhendisi→Risk Analisti; bu sira atlanamaz)

GOREV              : Backtest Muhendisi'nin HIPOTEZ 1 (Ana Test) dogrulama raporunu degerlendir,
                      ONAYLI/KOSULLU/RED karari ver. Kendi sistem promptundaki 8 kontrolu
                      (istatistiksel anlamlilik, IS/OOS bozulma, Monte Carlo, pes-pese kayip, kar
                      konsantrasyonu, kirilim analizi, parametre hassasiyeti, gercek-hayat
                      duzeltmesi) sirasiyla uygula ve kendi "Rapor Formati" sablonuna gore rapor
                      uret.

                      Bu, ML/feature-tabanli ailenin (kural-tabanli H1/H2/H3 ailesinden AYRI, yeni
                      bir metodoloji) ILK Risk Analisti turudur.

DONGU/GOREV-TAKIP NOTU (onemli, kendi bagimsiz kararini yonlendirmesin diye ayrica belirtiliyor):
- `backtest_muhendisi_20260712_1708` gorev-durum dosyasi "durum": "hata" olarak isaretlenmisti.
  Orkestrator raporun tamamini okudu: rapor icerigi eksiksiz, tutarli ve nihai (KARAR: RED,
  gerekce tam acilanmis). Bu "hata" etiketinin rapor icerigiyle degil, gorev-takip harness'inin
  kendi basari-kriteri tespitiyle ilgili oldugu degerlendirildi (rapor Bolum 0'da, bu turden once
  1. turun de benzer bir durum-etiketleme belirsizligi yasandigi belgeleniyor). Bu senin kendi
  bagimsiz degerlendirmeni etkilememeli — raporun ICERIGINE gore karar ver, durum-etiketine gore
  degil.
- Rapor, script'in İKİ KEZ (tur 2 + tani-blogu ile 3. calistirma) calistirildigini ve HER
  IKISINDE de BIREBIR AYNI (deterministik) sonuclar urettigini belgeliyor — tekrar-uretilebilirlik
  acisindan olumlu bir isaret, kendi degerlendirmene dahil edebilirsin.

ON-GOZLEM (Orkestrator'un okumasi, senin bagimsiz kararini yonlendirmesin diye ayrica
belirtiliyor — kendi 8 kontrolunu yine de tam ve bagimsiz uygula):
- Walk-forward AUC (4 fold, purged/embargolu): ortalama=0,5075 (std=0,0122, min=0,4938,
  max=0,5251) — rassal-seviyeye cok yakin.
- Final model TEST (tek-kez, n=17.833) AUC=0,5170 — yine rassala yakin; egitim ve test AUC'leri
  birbirine yakin (buyuk IS/OOS sapma yok — klasik overfitting deseni degil, TUTARLI ZAYIFLIK).
- Final model `best_iteration=1` (erken durma sadece 1 boosting turunda) — feature-onem tablosunda
  ATR/trend/confluence gibi ana gruplar neredeyse hic agirlik almiyor.
- Esik-kalibrasyonu (OOF-havuz, 4 farkli fold modelinin havuzlanmis tahminleri): LONG>=0,55
  (n=132, WR-proxy=%68,9) / SHORT<=0,45 (n=78, WR-proxy=%56,4) — ama TEK final model (best_
  iteration=1, en dar-yayilimli fold'larla ayni karakterde) TEST setinde bu esige HICBIR ZAMAN
  ulasmiyor (p_test max=0,5304 < 0,55). Muhendis bunu bir YONTEMSEL TUTARSIZLIK (OOF-havuz
  kalibrasyonu vs tek-model dagilimi) olarak isaretledi, kendi degistirme yetkisi disinda oldugunu
  belirtti — bu senin degerlendirmene ve/veya Stratejist'e iletilecek bir noktadir.
- Sonuc: hem PRIMARY (hicbiri-haric) hem SUPPLEMENTARY (hicbiri-dahil) test-seti simulasyonunda
  0 (sifir) islem tetiklendi. Muhendis, taninlama (test_p_dagilimi_TANI) ile bunun bir kod/veri
  hatasi degil, modelin dogrulanmis/deterministik bir davranisi oldugunu gosterdi.
- Muhendis'in KARARI: RED (olcum yoksa hedefin karsilandigi iddia edilemez — S2 Madde4 +
  Ortak Ilkeler, "0 islem = anlamli olculemez").
- S1 (maliyet-orani) P90-stres testinde esik KAYBEDILDI (11,91x < 15,0x esik) — medyan-spread
  uzerinden GECTI (15,97x) ama stres testinde kaybediliyor. Muhendis bunu Hipotez 1 RED cikarsa
  Hipotez 3 (k=2,0 varyanti) icin bir gerekce olarak isaretledi.
- Hipotez 2 (XGBoost) bu turda CALISTIRILMADI — Orkestrator ayri/paralel bir cagriyla bunu simdi
  tetikliyor (senin bu Hipotez 1 degerlendirmenle es-zamanli, birbirini beklemiyor).
- Bu ilk tur — S3 governance esigi (2 tam tur ayni olumsuz paternle Risk Analisti KARARIYLA
  sonuclanirsa Ertan onayi) HENUZ ISLEMIYOR; senin bu turdaki RED/ONAYLI/KOSULLU kararin ML
  ailesinin 1. tam-tur sonucu olacak.
- Bu on-gozlem bir sonuc degil, sadece dikkat cekmek icindir; kendi bagimsiz 8 kontrolunu tam
  uygula (ozellikle bagimsiz dogrulama: raporun ham JSON ciktisindan — varsa — kendi hesaplarinla
  capraz kontrol).

VERI IZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN):
- Tek veri kaynagi: XM/MT5 fiyat verisi (Backtest Muhendisi zaten dogrudan MT5'ten cekti).
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) erisme/
  atif yok — format/sablon referansi da dahil.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md (HEDEF_PF=1,5/HEDEF_WR=%60,0/HEDEF_DD=%20/
  kasa=2.000 USD/risk=%1/lot kurallari)
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (S2 protokolu, tam metin)
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md (S1 + DST + SL/TP-ozel on-kontrol)

ONCEKI ADIMIN CIKTISI:
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
(Rapor + Risk Analistine Iletim ozeti, Bolum 4 ve 7)
Ham veri: C:\MilaYatirim\Justin\backtest_ml_v1_hipotez1_output.json
Stratejist'in Hipotez 1 tanimi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md
(Bolum "HIPOTEZLER", Hipotez 1)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
- Kendi sistem promptundaki "Rapor Formati" sablonuna gore tam rapor (KARAR: ONAYLI/KOSULLU/RED
  + 8 kontrol + Stratejiste geri bildirim + kullaniciya ozet).

ONAY NOKTASI       : Bilgi notu — Ertan'in onayina gerek yok. Bu adim salt-okunur/analitik bir
degerlendirmedir (gecmis backtest ciktisi uzerinde), canli sisteme (MilaGold/uretim veya Justin
canli hesabi — zaten yok) hicbir dokunusu yoktur, Justin demo/arastirma asamasindadir. START/
CHANGE kapsamina girmez (Mimari Boyutlar B/E). Sonuc uretildiginde Ertan'a Telegram bilgi notu
gonderilecek + Orkestrator_Loglar'a kayit dusulecek. NOT: Risk Analisti RED kararina varirsa, bu
da salt bir bilgi/analiz sonucudur (pipeline'in dogal ciktisi) — START/CHANGE sayilmaz; olasi bir
"Stratejist'e yeni hipotez/varyant uret" adimi ayri bir cagriyla degerlendirilecektir.
