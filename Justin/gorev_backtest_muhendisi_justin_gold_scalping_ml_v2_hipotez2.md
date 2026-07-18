=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 15:30
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v2
                      (ML Tam Tur 2), HIPOTEZ 2 (ETIKET-IZOLE, PARALEL HIPOTEZ: LightGBM
                      3-sinifli/deadzone + Hipotez 1 ile BIREBIR AYNI feature seti, N=16/
                      k_risk=1,5xATR14-M15)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md,
                      Bolum "HIPOTEZ 2") tanimladigi 3-sinifli deadzone modelini dogrula. Bu
                      gorev, HIPOTEZ 1 (LightGBM ikili) icin ayni anda calisan Backtest gorevini
                      BEKLEMEDEN, ONA PARALEL calistirilmaktadir (Stratejist'in kendi onerisi:
                      "ek hesaplama maliyeti feature-pipeline paylasildigi icin kucuktur").

                      Sira / kapsam:
                      1. **On-kosul:** Kutuphane kurulumu Hipotez 1 ile paylasilir (pandas/
                         lightgbm/scikit-learn) — versiyon teyidi yeterli, ayri kurulum
                         GEREKMEZ.
                      2. **S1 — Maliyet-orani stres testi:** k_risk=1,5xATR14 Hipotez 1 ile AYNI
                         oldugu icin cost-ratio sonucunu Hipotez 1 raporundan (veya Tur 1'den)
                         DEVRAL, referans ver.
                      3. **DST/saat-eslesme dogrulamasi:** Hipotez 1 ile AYNI feature pipeline'i
                         (Grup B dahil, ayni saat/oturum ve gun/hafta sinirlari) kullanildigi icin
                         Hipotez 1'in DST dogrulama sonucunu DEVRALABILIRSIN (ayni ML/v2 ailesi
                         icinde, ayni script/feature-uretim kodu — H1/H2/H3 kural-tabanli
                         aileden devralma degildir, bu bir istisna degil ayni-aile-ici paylasimdir).
                      4. **Etiket uretimi — KRITIK, Stratejist'in acikca vurguladigi nokta:**
                         3-sinif etiket: "yukari" (N=16-bar ileri getiri > k_label x ATR14),
                         "asagi" (< -k_label x ATR14), "notr" (arada). k_label=0,3xATR14
                         BASLANGIC noktasi (Arastirmaci BULGU 10'dan devralinan oran, N=8 icin
                         olculmustu) — **N=16 icin dagilimi (%yukari/%asagi/%notr) YENIDEN
                         HESAPLA**, N=8 sonuclariyla (%43,9/%40,5/%15,6) BIREBIR karsilastirma
                         YAPMA (bu bir yeniden-olcum, Stratejist Karar 2'deki sayisal-tutarlilik
                         notu). Dagilim cok dengesiz cikarsa (orn. "notr" >%40 veya <%5),
                         k_label'i egitimden ONCE, test setine BAKMADAN 0,15-0,5 araliginda ayarla
                         (S2 Madde 4).
                      5. **IKI FARKLI k — KARISTIRILMAMALI (Stratejist'in ozel uyarisi):**
                         `k_label=0,3xATR14` SADECE egitim etiketini/sinifini belirlemek icindir.
                         `k_risk=1,5xATR14` GERCEK SL/TP mesafesidir (Hipotez 1 ile AYNI,
                         k_label'dan tamamen BAGIMSIZ). Kod duzeyinde bu iki degisken AYRI, acikca
                         isimlendirilmis olmali — bu, sessiz-hata riski tasidigi icin kod
                         incelemesinde ozellikle kontrol edilmeli.
                      6. **Ana test:** LightGBM multiclass classifier (`objective=multiclass`,
                         `num_class=3`), Hipotez 1 ile BIREBIR AYNI feature seti (~22-28 sutun,
                         Grup B dahil), dar hiperparametre araligi (multiclass'a gecisin kendisi
                         bir karmasiklik artisi oldugu icin hiperparametre aramasi AYRICA
                         genisletilmemeli). Karar kurali (baslangic): en yuksek olasilikli sinif
                         "yukari" VE P_yukari>=0,45 → LONG; "asagi" icin simetrik → SHORT; "notr"
                         en yuksekse veya hicbir sinif esigi asamiyorsa → ISLEM YOK. SL/TP:
                         k_risk=1,5xATR14 (Hipotez 1 ile AYNI), N=16, RR=1:1.
                      7. **Raporlama — ZORUNLU ek olcumler:** confusion-matrix ve multiclass-
                         log-loss (P&L'e dogrudan donusmeyen ama modelin ayirt-ediciligini
                         gosteren olcumler olarak ayrica raporla). Hipotez 1 vs Hipotez 2
                         karsilastirma tablosu (OOS PF/WR/islem-sayisi/feature-onem) YAN YANA
                         sunulmali — amac "etiket degisikligi feature-onem paternini/performansi
                         DEGISTIRDI mi" sorusuna cevap vermek.
                      8. Lot/risk: Hipotez 1 ile AYNI (`justin_gecmis_calisma.md`).

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md (HIPOTEZ 2
  tanimi, Karar 2 — k_label/k_risk ayrimi)
- Hipotez 1 icin paralel calisan Backtest gorevinin ciktisi (tamamlaninca, karsilastirma icin
  referans alinabilir; BEKLEMEK ZORUNLU DEGIL, iki gorev bagimsiz ilerleyebilir)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez2_20260712.md
(bolum yapisi Hipotez 1 raporuyla paralel: On-Kontrol Sonuclari [S1/DST — Hipotez 1'den
devralindi, gerekcesiyle], k_label Yeniden-Hesaplama Sonucu [N=16 dagilimi], Ana Test Tasarimi,
Sonuclar [confusion-matrix/multiclass-log-loss dahil], Hipotez 1 vs Hipotez 2 Karsilastirma
Tablosu, Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi) + ham veri/script dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): S3 sayaci su an 1/2. Hipotez 1 ve Hipotez 2, Tam Tur
2'nin tek bir Risk Analisti degerlendirmesiyle birlikte ele alinacaktir (ikisi de ayni Stratejist
raporundan/ayni Arastirmaci girdisinden turemis, karsilastirmali bir cift) — sayac islemesi Risk
Analisti asamasinda Orkestrator tarafindan degerlendirilecektir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
