=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 15:48
HEDEF AGENT        : Risk Analisti
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\risk_analisti_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v2
                      (ML Tam Tur 2), HIPOTEZ 1 + HIPOTEZ 2 — BIRLIKTE, TEK DEGERLENDIRME TURU
                      Pipeline adimi: 4/4 (son adim) — Yol1 metodolojisi (Arastirmaci→Stratejist→
                      Backtest Muhendisi→Risk Analisti; bu sira atlanamaz)

GOREV              : Backtest Muhendisi'nin Hipotez 1 (v2, ikili/barrier-touch) VE Hipotez 2 (v2,
                      3-sinifli/deadzone) dogrulama raporlarini BIRLIKTE, TEK bir degerlendirme
                      turunda incele — Hipotez 2 raporunun kendi Bolum 8'inde acikca istedigi
                      gibi ("Risk Analisti, bu raporu Hipotez 1 (v2) raporuyla BIRLIKTE inceleyip
                      nihai KABUL/RED kararini verecektir"). Kendi sistem promptundaki 8 kontrolu
                      HER IKI hipotez icin de (ayri ayri veya ortak bulgulari tek yerde toplayarak,
                      kendi taktir yetkinde) uygula, HER IKISI icin de acik bir KARAR (ONAYLI/
                      KOSULLU/RED) uret, ayrica bu Tam Tur 2'nin GENEL sonucunu (S3 governance
                      sayaci acisindan) tek bir cumleyle ozetle.

                      Hipotez 3 (v2, olceklenebilirlik pilotu, dusuk oncelik) bu turun kararina
                      HENUZ dahil DEGIL — kendi gorev talimatinda ("Stratejist'in kendi tanimiyla
                      ana karar agirligini TASIMAMALI") acikca tamamlayici/on-gozlem olarak
                      isaretlenmis, ayri/paralel calisiyor, sonucu hazir olmadigi icin bu
                      degerlendirmeyi BEKLEMEZ. Hipotez 3 sonucu geldiginde ayri bir Orkestrator
                      cagrisiyla (gerekirse bu karara ek bilgi olarak) degerlendirilecek.

DONGU/GOREV-TAKIP NOTU: Her iki gorev-durum dosyasi da "durum": "tamamlandi" olarak isaretliydi
(backtest_muhendisi_20260712_1832 → Hipotez 2; Hipotez 1 (v2) raporu daha once tamamlanmis ve
zaten karsilastirma tablosunda Hipotez 2 raporu tarafindan referans alinmis durumda). Orkestrator
her iki raporu da tam okudu, ozetleri asagida.

ORKESTRATOR ON-GOZLEMI (senin bagimsiz kararini yonlendirmesin diye ayrica belirtiliyor — kendi
8 kontrolunu HER IKI hipotez icin tam ve bagimsiz uygula, asagidaki sayilari HAM JSON'larla
capraz dogrula):

--- HIPOTEZ 1 (v2, ikili/barrier-touch, Grup B feature'lari eklenmis) ---
- Walk-forward OOS: AUC ortalama 0,5098 (std 0,0142) — rassal-seviye.
- Final TEST (tek-kez, n=17.833) AUC=0,5190 (Tur 1: 0,5170 — fark +0,002, PRATIKTE AYNI/rassal).
- IS (0,5098) ile OOS (0,5190) arasinda BUYUK sapma YOK — klasik overfitting deseni degil, ama
  bu "iyi" degil, "tutarli zayiflik" anlamina geliyor (Tur 1 ile ayni yorum).
- Esik-kalibrasyonu (OOF): PRIMARY ve SUPPLEMENTARY simulasyonlarin IKISINDE de tetiklenen islem
  sayisi = 0 (SIFIR) — Tur 1 ile BIREBIR AYNI sonuc.
- Feature-onem paterni Tur 1'e gore DEGISTI (Grup B / dist_weekly_pivot_pts, atr14_h1_aligned,
  dist_roll20_low_pts on siraya cikti) ama bu degisim TEST AUC'sinde veya islem sayisinda OLCULEBILIR
  hicbir etki YARATMADI — Muhendis'in kendi vurgusu.
- S1 P90-stres testi KAYBEDILDI (11,91x < 15,0x esigi), medyan uzerinden GECTI (15,97x).

--- HIPOTEZ 2 (v2, 3-sinifli/deadzone, Grup B feature'lari eklenmis) ---
- Walk-forward OOS: logloss ort. 0,9598 (std 0,0088), accuracy ort. 0,4594 (std 0,0163).
- Final TEST (tek-kez, n=19.960): logloss 0,9578, accuracy 0,4218 — **TRIVIAL "her-zaman-yukari-
  tahmin-et" tabaninin (0,4696) ALTINDA.**
- Confusion matrix: "notr" sinifi argmax'ta HICBIR ZAMAN secilmedi (model fiilen 2-sinifli
  davraniyor, egitimde %11 agirlikla gordugu sinifi test'te hic tahmin etmiyor).
- Esik-kalibrasyonu (OOF): hicbir esik adayinda long/short WR-proxy anlamli sekilde %50
  rastgele-tabanini ASMADI (en yuksek esikte bile short-proxy 0,3756 < 0,50).
- Trade sim (0,50/0,50 esigi): 15 PRIMARY islem (hepsi LONG, SHORT=0 — hicbir bar esik_asagi+
  argmax==asagi kosulunu saglamadi), WR %66,67, **PF=0,781 (HEDEF 1,5 KARSILANMADI)**, net
  -32,57 USD, n=15 < MIN_SAMPLE(30) — **ORNEKLEM YETERSIZ, tek basina karar dayanagi OLAMAZ.**
- Feature seti Hipotez 1 (v2) ile BIREBIR AYNI DEGIL (27 vs 29 sutun — paralel/bagimsiz gelistirme
  sonucu 2 sutunluk fark, Muhendis'in kendi ACIKCA isaretledigi bir kisit) — "etiket etkisi izole
  edildi mi" karsilastirmasi %100 saf degil.
- ATR TUTARSIZLIGI (Muhendis'in kendi bulgusu, Risk Analisti degerlendirmesi bekleniyor):
  Stratejist notu "Wilder=v1 ile tutarli" dedi ama v1'in fiili ATR fonksiyonu BASIT rolling-
  ortalama. Muhendis k_risk icin BASIT ATR (Hipotez 1 ile ayni SL/TP), k_label icin Stratejist'in
  yazili talimati harfiyen uygulayarak WILDER ATR kullandi — bu kendi basina bir karar/varsayim,
  senin degerlendirmen gerekiyor.
- S1 P90-stres testi Hipotez 1 ile AYNI (11,91x < 15,0x, mekanizma ortak/model-secimden bagimsiz).

**Governance (S3, KRITIK — kendi bagimsiz karar surecini degistirmemeli, ama karar sonrasi
Orkestrator'un bir sonraki adimini belirleyecek):** S3 sayaci su an 1/2 (Tur 1'in ucu de RED
sonuclanmisti — rassal-seviye AUC, sifira yakin feature-onem, 0-islem esik-kalibrasyonu ile
AYNI patern). Stratejist'in kendi raporunda acikca belirttigi gibi: "Bu turun (Tur 2) Risk
Analisti karari RED ve Tur 1 ile AYNI paternde sonuclanirsa, S3 governance esigi (2/2) tetiklenir
— Orkestrator bir sonraki Arastirmaci turunu Ertan onayi olmadan baslatmaz." Yukaridaki sayilara
bakildiginda (Hipotez 1: 0 islem/rassal AUC — Tur 1 ile birebir ayni patern; Hipotez 2: trivial-
taban-altinda accuracy + PF hedefin altinda + yetersiz orneklem) bu paternin tekrarlanmis
olabilecegi ON-GOZLEMLENIYOR — ancak nihai KARAR (RED/KOSULLU/ONAYLI, HER IKI hipotez icin ayri
ayri) TAMAMEN sana ait, kendi 8 kontrolunu bagimsiz uygulayarak ver. Kararin RED cikarsa ve Tur 1
ile ayni patern oldugunu teyit edersen, bunu raporunda ACIKCA belirt (Orkestrator bu bilgiyi
S3 sayacini 2/2'ye tasima ve Ertan'a onay sorusu yoneltme kararinda kullanacak).

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
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez1_20260712.md
  (Ham veri: backtest_ml_v2_hipotez1_output.json)
- C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez2_20260712.md
  (Ham veri: backtest_ml_v2_hipotez2_output.json — Bolum 5'te Hipotez1 vs Hipotez2 karsilastirma
  tablosunu da icerir)
- Stratejist'in tanimi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md
  (Karar 1-5, Hipotez 1/2 tanimlari + S3 governance notlari)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_ml_v2_hipotez1_hipotez2_20260712.md
- Kendi sistem promptundaki "Rapor Formati" sablonuna gore, HER IKI hipotez icin ayri KARAR
  (ONAYLI/KOSULLU/RED) + 8 kontrol + Stratejiste geri bildirim + kullaniciya ozet + Tam Tur 2'nin
  GENEL/birlesik sonucu (S3 acisindan) tek paragrafla.

ONAY NOKTASI       : Bilgi notu — Ertan'in onayina gerek yok. Bu adim salt-okunur/analitik bir
degerlendirmedir (gecmis backtest ciktisi uzerinde), canli sisteme (Justin canli hesabi zaten yok)
hicbir dokunusu yoktur, Justin demo/arastirma asamasindadir. START/CHANGE kapsamina girmez
(Mimari Boyutlar B/E). Sonuc uretildiginde Ertan'a Telegram bilgi notu gonderilecek +
Orkestrator_Loglar'a kayit dusulecek. NOT: Eger senin kararin S3 esigini (2/2) tetiklerse, bir
sonraki Arastirmaci turunu BASLATMA karari senin degil Orkestrator'undur — Orkestrator bu durumda
Ertan'a somut bir onay sorusu yoneltecektir (bu senin rapor kapsaminin disinda, Orkestrator'un
sorumlulugu).
