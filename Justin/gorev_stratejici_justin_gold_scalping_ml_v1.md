# GOREV TANIMI — Orkestrator → Stratejist (ML/Feature-Tabanli Gold Scalping, v1 — Faz 2)

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
- Pipeline adimi: 2/4 (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti, sira
  sabit, atlanamaz — Backtest Muhendisi'ne dogrudan gecilmez)
- Tarih: 12 Temmuz 2026 (VPS-yerel)
- Onceki asama: Arastirmaci (Faz 2, 1/4) — TAMAMLANDI. Rapor tam ve BEKLENEN CIKTI
  spesifikasyonundaki tum bolumleri (Ozet, Gozlemler, Onerilen Feature Seti ve Label Tanimi, En
  Az 1 Somut ML Tasarim Onerisi, Riskler/Sinirlamalar, Acik Sorular, Izolasyon Notu) icermektedir.
  **Not (gorev-takip sistemi, bilgi amacli):** Bu Arastirmaci gorevinin durum dosyasi "hata"
  olarak isaretlendi; inceleme sonucu bunun rapor icerigiyle ilgili olmadigi, muhtemelen
  `agent_calistir_worker.mjs`'nin basari kriterinin (SDK sonuc mesaji subtype='success' VE
  Write cagrisi tespit edilmis olmasi) bu oturumda saglanmadigi (orn. maxTurns=30 siniri, rapor
  yazildiktan sonraki ek turlarda kutuphane kisiti nedeniyle tuketilmis olabilir) bir harness
  sinifllandirma sorunu oldugu degerlendirildi — rapor dosyasinin kendisi eksiksiz/tutarli.
  Bu, canli sisteme etkisi olmayan, dusuk riskli (geri donulebilir, dar etki alani) bir durum
  oldugu icin Orkestrator STOP-genis/bilgi-notu yetkisiyle pipeline'i durdurmadan devam
  ettirmeye karar verdi. Tekrarlarsa (orn. Backtest Muhendisi gibi daha uzun/script-agir
  adimlarda da gorulurse) maxTurns limitinin arttirilmasi bir CHANGE olarak Ertan'a ayrica
  onaya sunulmali — bu turda sadece gozlem olarak not edildi.

## Amac
Arastirmaci'nin M15+ ML/feature-tabanli Gold Scalping raporuna (asagida) dayanarak, bu
yaklasima OZEL SL/TP/ATR katsayisini (k) ve tutma-suresini (N) belirle; LightGBM (birincil
aday) ve opsiyonel XGBoost (kiyaslama) icin Backtest Muhendisi'nin dogrulayabilecegi 2-3 somut
hipotez uret. Bu bir "yeniden arastirma" turu degil — Arastirmaci'nin BULGU 10/11'deki
N/k degis-tokusu ve maliyet-orani sayilarini ham girdi olarak kullanip karar/sentezini sizin
yapmaniz beklenir.

## Karar Vermeniz Beklenen Ozel Noktalar (Arastirmaci raporundan devralinan acik sorular)
1. **N/k secimi (BULGU 10-11):** Arastirmaci, k>=1,5 (tercihen ~2,0) araligini S1 maliyet-orani
   esigini (~15-20x) gecebilmek icin onermis, ancak k=2,0'da N=8'de "hicbiri" orani %48,64'e
   cikiyor (sinif dengesizligi riski). N=16/k=1,5 kombinasyonu (TP %44,45, SL %42,47, hicbiri
   %13,07) hem sinif dengesi hem maliyet-orani acisindan daha elverisli gorunuyor — bu
   degis-tokusu siz degerlendirip N ve k'yi kesin belirleyin (gerekceyle).
2. **Etiket semasi:** Ikili (TP-once vs SL-once, "hicbiri" disarida) mi yoksa 3-sinifli
   (TP/SL/hicbiri) mi kullanilacak — Arastirmaci karar vermedi, sizin belirlemeniz gerekiyor.
3. **Feature onceligi:** Arastirmaci'nin 6 feature grubundan (Volatilite, Coklu-TF Confluence,
   Hacim/Tick-Yogunlugu, Oturum/Gun-Ici Konum, Fiyat Yapisi/Momentum, Maliyet/Likidite) hangileri
   ilk hipotez turunde ZORUNLU, hangileri opsiyonel/ikinci tur olacak.
4. **Kutuphane bagimliligi (Arastirmaci Riskler Madde 1):** Bu arastirma ortaminda pandas/
   lightgbm/xgboost/scikit-learn KURULU DEGIL — Arastirmaci gercek model egitimi yapmadi, sadece
   numpy ile dagilim olcumu yapti. Hipotezinizde, Backtest Muhendisi asamasinda bu kutuphanelerin
   hangi ortamda kurulacagi konusunda bir varsayim/istek belirtin (bu sizin karar alaniniz
   disinda olabilir ama gorev tanimina not dusulmesi Backtest Muhendisi'ne yardimci olur).

## Zorunlu Protokol (S2 — ML Anti-Overfitting) — DEVAM EDIYOR
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md` — Arastirmaci asamasindan beri
gecerli, hipotez tasariminda (train/test/embargo mantigi, feature-sizinti kontrol listesi,
basari kriterlerinin onceden sabitlenmesi) bu protokole uyulmali.

## On-Kontrol Hatirlatmasi (S1 — Maliyet-Orani)
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` — belirleyeceginiz k katsayisi,
Arastirmaci'nin BULGU 11'deki maliyet-orani on-tahminini (medyan spread uzerinden) karsilamali;
P90/max spread ile stres-testi Backtest Muhendisi asamasinda ayrica yapilacak, siz medyan
uzerinden makul bir k secin yeterli.

## Governance Esigi (S3 — bilgi amacli, degismedi)
ML ailesinde 2 tam tur (bu, ilk turdur) ayni olumsuz paternle (PF<1/sistematik RED)
sonuclanirsa Orkestrator Ertan'a onay sorusu yoneltir. Bu tur henuz Risk Analisti karari
uretmedigi icin sayac islemiyor.

## Gecmis Calisma / Cerceve Dosyasi (zorunlu referans)
`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — HEDEF_PF=1,5; HEDEF_DD=%20 (kumulatif);
kasa=2.000 USD; islem-basi risk=%1 (ust sinir); lot 0,01 sabit baslangic, her 2.000 USD
kasa=0,01 lot; HEDEF_WR R:R'ye gore turetilir (1:1→%60,0; 1:2→%42,9; 2:1→%75,0).

## VERI IZOLASYONU — ZORUNLU KISIT
Baska bir dahili sistemin (MilaGold/Lisa/Signal GPT) bulgu/veri/parametresine erisim veya
atif YOK — ne veri/parametre kopyalama ne de format/sablon referansi icin acma. Calisma dizini
yalniz `C:\MilaYatirim\Justin\` altinda.

## ONCEKI ADIMIN CIKTISI (referans)
`C:\MilaYatirim\Justin\arastirmaci_gold_scalping_ml_raporu.md` — Arastirmaci'nin M15+ ML/
feature-tabanli Gold Scalping raporu (BULGU 1-11, Onerilen Feature Seti/Label Tanimi, En Az 1
Somut ML Tasarim Onerisi, Riskler, Acik Sorular).

## BEKLENEN CIKTI
`C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md`
- Oturum ozeti (Arastirmaci'nin ML raporundan hangi bulgulari girdi olarak aldiginizin ozeti)
- 2-3 somut hipotez (stratejici_system_prompt.md formatinda: HIPOTEZ ADI, YAKLASIM TURU,
  MANTIK, YONTEM DETAYI, GIRIS/CIKIS MEKANIZMASI, SL/TP veya RISK YONETIMI — burada N/k kesin
  degeriniz, DOGRULAMA IHTIYACI, RISKLER, ONCELIK)
- Yukaridaki "Karar Vermeniz Beklenen Ozel Noktalar" 1-4 maddelerine acik yanit
- Backtest Muhendisi icin Notlar (S1/S2 protokollerinin nasil uygulanmasi gerektigi dahil)
- Izolasyon teyidi

## ONAY NOKTASI
Bilgi notu — bu adim (Stratejist, Faz 2/2. adim) hipotez/tasarim niteliginde, canli sisteme/
hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok
(Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu degil, etki alani dar
(yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecek.
