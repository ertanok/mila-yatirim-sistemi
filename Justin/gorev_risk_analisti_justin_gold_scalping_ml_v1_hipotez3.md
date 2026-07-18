=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 14:46
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v1,
                      HIPOTEZ 3 (LightGBM, N=16/k=2,0xATR14-M15 — Hipotez 1'in guvenlik-marji/
                      duyarlilik varyanti; esik-kalibrasyon yontemi DUZELTILMIS hali ile)
                      Pipeline adimi: 4/4 (son adim) — Yol1 metodolojisi (Arastirmaci→Stratejist→
                      Backtest Muhendisi→Risk Analisti; bu sira atlanamaz)

GOREV              : Backtest Muhendisi'nin HIPOTEZ 3 dogrulama raporunu degerlendir, ONAYLI/
                      KOSULLU/RED karari ver. Kendi sistem promptundaki 8 kontrolu (istatistiksel
                      anlamlilik, IS/OOS bozulma, Monte Carlo, pes-pese kayip, kar konsantrasyonu,
                      kirilim analizi, parametre hassasiyeti, gercek-hayat duzeltmesi) sirasiyla
                      uygula ve kendi "Rapor Formati" sablonuna gore rapor uret.

DONGU/GOREV-TAKIP NOTU:
- Bu, ML/feature-tabanli ailenin Risk Analisti tarafindan degerlendirilen 3. hipotezidir (Hipotez
  1/LightGBM-k1,5: RED, Hipotez 2/XGBoost-k1,5: RED — bkz. ilgili risk_analisti raporlari,
  20260712).
- Hipotez 3, Hipotez 1/2'nin AYNI Stratejist raporundan/AYNI "tam tur"dan tureyen ucuncu varyantidir
  (parallel cross-check degil, Hipotez 1'in guvenlik-marji/k-duyarlilik varyanti). Bu degerlendirme
  GUNLUK PIPELINE DONGU SAYACINI (CLAUDE.md, Boyut C) ARTIRMAZ — bugunku (12 Temmuz) Justin ML/v1
  hatti icin sayac zaten 2'de sabit (Backtest Muhendisi'nin kendi gorev dosyasinda teyit edildi),
  bu sadece o turun uçuncu hipotezinin degerlendirme adimidir.
- ONEMLI FARK — Hipotez 1/2'den: Backtest Muhendisi bu turde esik-kalibrasyon yontemini
  DUZELTEREK calistirdi (Risk Analisti'nin Hipotez 1 raporundaki Geri Bildirim Madde 1 talebi
  uzerine) — kalibrasyon artik SADECE final modelin kendi ic-validasyonundan (`final_innerval_idx`,
  n=12.219) yapiliyor, 4-fold havuzlanmis OOF KULLANILMADI. Bu duzeltmenin kendisinin dogru
  uygulanip uygulanmadigini da degerlendirmene dahil et (Kontrol [7] altinda uygun).
- Kendi bagimsiz kararini onceki hipotezlerin RED sonucu yonlendirmesin — kendi 8 kontrolunu tam ve
  bagimsiz uygula (ozellikle ham JSON ciktisiyla capraz kontrol, esik-kalibrasyon duzeltmesinin
  raporda iddia edildigi gibi gercekten uygulandigini teyit et).

ON-GOZLEM (Orkestrator'un okumasi — Backtest Muhendisi raporundan):
- Walk-forward AUC (4 fold, purged/embargolu, SADECE diagnostik): ortalama=0,5074 (std=0,0107,
  min=0,4965, max=0,5209) — Hipotez 1'in 0,5075'i ile pratikte AYNI, rassal-seviyeye yakin.
- Final model ic-validasyon AUC=0,5209, best_iteration=1 (tek agac) — Hipotez 1 ile AYNI kirilgan
  karakter.
- Esik-kalibrasyonu (DUZELTILMIS yontem, final_innerval_idx uzerinden): UC adayin da (0,60/0,40 /
  0,575/0,425 / 0,55/0,45) long_n=short_n=0 — HICBIRI MIN_SAMPLE(>=30) esigini gecmedi, fallback
  (0,60/0,40) + YETERSIZ_ORNEKLEM_FALLBACK_UYGULANDI=True.
- TEST AUC (tek-kez, n=15.237)=0,5211 — rassala yakin; p_test max=0,5280, kalibre esige (0,60)
  hicbir zaman ulasmiyor.
- PRIMARY ve SUPPLEMENTARY simulasyonlarinin ikisinde de 0 (sifir) islem tetiklendi.
- S1 maliyet-orani: medyan 21,29x GECTI, P90-stres 15,88x GECTI (Hipotez 1'in kaybettigi yerde,
  11,91x<15,0x) — k=2,0'nin guvenlik-marji amaci ampirik olarak dogrulandi.
- Feature-onem: ATR/trend/confluence gruplari yine ~sifir agirlikli (Hipotez 1 ile birebir ayni
  patern) — Muhendis'e gore k'nin genisletilmesi modelin ogrenme kapasitesini degistirmedi.
- Muhendis'in KARARI: RED (olcum yoksa hedefin karsilandigi iddia edilemez — S2 Madde4). Muhendis
  ayrica bu turde 0-islem sonucunun artik "yontemsel artefakt" degil modelin tutarli/gercek
  davranisi oldugunu vurguluyor (kalibrasyon kaynagi duzeltildikten sonra da ayni sonuc).
- Bu on-gozlem bir sonuc degil; kendi bagimsiz 8 kontrolunu tam uygula.

VERI IZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN):
- Tek veri kaynagi: XM/MT5 fiyat verisi (Backtest Muhendisi zaten dogrudan MT5'ten cekti).
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya erisme/atif yok — format/sablon referansi dahil.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v1_hipotez3_20260712.md
  (Rapor + Risk Analistine Iletim ozeti, Bolum 7 ve 9; Hipotez 1 vs Hipotez 3 karsilastirma tablosu
  Bolum 5'te)
- Ham veri: C:\MilaYatirim\Justin\backtest_ml_v1_hipotez3_output.json
- Karsilastirma referansi: C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md
  (senin kendi onceki Hipotez 1 karari/gerekcen — tutarlilik icin referans al, ama bu turu BAGIMSIZ
  degerlendir; Hipotez 2 raporunu da (risk_analisti_raporu_..._hipotez2_20260712.md) istersen ikinci
  bir referans olarak kullanabilirsin)
- Stratejist'in Hipotez 3 tanimi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md
  (Bolum "HIPOTEZLER", Hipotez 3)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez3_20260712.md
- Kendi sistem promptundaki "Rapor Formati" sablonuna gore tam rapor (KARAR: ONAYLI/KOSULLU/RED
  + 8 kontrol + Stratejiste geri bildirim + kullaniciya ozet). Raporunda ayrica Hipotez 1/2 ile
  Hipotez 3 arasindaki Risk-Analisti-seviyesi tutarliligi (ayni karara mi ulasildi, esik-kalibrasyon
  duzeltmesinin etkisi, S1 P90-stres testindeki fark) kisaca degerlendir.

ONAY NOKTASI       : Bilgi notu — Ertan'in onayina gerek yok. Bu adim salt-okunur/analitik bir
degerlendirmedir (gecmis backtest ciktisi uzerinde), canli sisteme (MilaGold/uretim veya Justin
canli hesabi — zaten yok) hicbir dokunusu yoktur, Justin demo/arastirma asamasindadir. START/
CHANGE kapsamina girmez (Mimari Boyutlar B/E). Sonuc uretildiginde Ertan'a Telegram bilgi notu
gonderilecek + Orkestrator_Loglar'a kayit dusulecek. Risk Analisti RED kararina varirsa bu da
salt bir bilgi/analiz sonucudur — ML/v1 hattinin uc hipotezinin de (1,2,3) RED cikmasi durumunda
"Arastirmaci'ya feature-seti/etiket tasarimi icin yeni girdi" onerisi ayri bir cagriyla
degerlendirilecektir, bu gorev kapsaminda degildir.
