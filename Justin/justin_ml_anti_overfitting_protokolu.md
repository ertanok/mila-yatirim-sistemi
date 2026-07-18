# JUSTIN — ML AILESI ANTI-OVERFITTING PROTOKOLU (S2)

Statu: KALICI/STANDART — yalniz ML/hibrit yaklasimlar icin gecerli (kural-tabanli fiyat-
aksiyonu hipotezleri icin zorunlu degil, ama zarari olmaz).
Olusturulma: Orkestrator, Faz 0 (Ertan'in (a) + 3-sertlestirme onayi, 14 Temmuz 2026),
kaynak: orkestrator_degerlendirme_madde7_gold_scalping_20260714.md, Bolum 4 (S2) + Bolum 5
(Faz 0, madde 3).

Gerekce: Uc kural-tabanli hipotezde (H1/H2/H3) yalanci-pozitif riski goreceli dusuktu (az
parametre, dar arama uzayi). ML/feature-tabanli yaklasimda arama uzayi (feature sayisi,
hiperparametre, model secimi) cok daha genis oldugundan yalanci-pozitif/overfitting riski
ONEMLI OLCUDE yuksek. Bu protokol, Justin'in ML ailesine gecisiyle birlikte, Arastirmaci ve
Backtest Muhendisi gorev tanimlarina BASTAN (ilk turden itibaren) yazilmalidir — sonradan
eklenecek bir kontrol degil.

---

## 1) Purged / Embargolu Walk-Forward

- Standart walk-forward'a ek olarak, egitim ve test pencereleri arasinda **purge** (orneklerin
  arasindaki bilgi sizintisini onlemek icin sinir bolgesindeki gozlemlerin cikarilmasi) ve
  **embargo** (test penceresinden hemen once/sonraki bir zaman araligini egitime dahil etmeme)
  uygulanmali.
- Gerekce: finansal zaman serilerinde ardisik gozlemler arasinda otokorelasyon/ozellik-sizintisi
  (orn. bir feature'in ileri-bakan bir pencereden hesaplanmasi) standart k-fold veya naif
  walk-forward'da tespit edilemeyen sahte performans yaratabilir.

## 2) Test-Seti Tek-Kullanim Kurali

- Nihai/rezerve edilmis test seti (OOS) **sadece bir kez**, tum model secimi/hiperparametre
  ayari/feature secimi TAMAMLANDIKTAN SONRA calistirilir.
- Test setinde alinan bir sonuc "beklenenden kotu" cikti diye modele geri donup yeniden ayarlama
  (test setine gore iteratif ince ayar) YAPILAMAZ — bu, test setini fiilen bir validation setine
  cevirir ve raporlanan performansi gecersiz kilar. Boyle bir ihtiyac dogarsa, bu acikca
  raporda belirtilmeli ve YENI, daha once hic gorulmemis bir test seti kullanilmalidir.

## 3) Feature Sizinti Kontrol Listesi

Her yeni feature seti icin, ana teste gecmeden once asagidakiler kontrol edilmeli ve raporda
madde madde teyit edilmeli:
- Feature, hesaplandigi zaman noktasinda gercekten mevcut olan bilgiyi mi kullaniyor (ileri-
  bakan/look-ahead bias yok)?
- Feature, hedef degiskenin (label) hesaplanmasinda kullanilan herhangi bir veriyi dolayli
  olarak iceriyor mu (orn. gelecekteki fiyat hareketinden turetilmis bir normalize edici)?
- Feature normalizasyonu/olceklendirme istatistikleri (ortalama, std, min/max) SADECE egitim
  setinden mi hesaplaniyor (test/OOS setinden sizinti yok)?
- Zaman-bazli feature'lar (session/gun-ici konum vb.) DST/saat-eslesme dogrulamasindan gecti mi
  (bkz. justin_backtest_onkontrol_standardi.md, Madde 1)?

## 4) Basari Kriterlerinin Egitimden ONCE Sabitlenmesi

- HEDEF_PF, HEDEF_WR, HEDEF_DD gibi basari esikleri (bkz. justin_gecmis_calisma.md — henuz
  olusturulmadi, Faz 0 madde 1 bekliyor) model egitilmeden/test edilmeden ONCE yazili olarak
  sabitlenmeli.
- Egitim/test sonrasi "sonuca gore" esik gevsetme veya "bu kadari da iyi sayilir" seklinde
  post-hoc kriter degisikligi YAPILAMAZ. Sonuc esigi karsilamiyorsa RED olarak raporlanir;
  esik degisikligi ayri ve acik bir Stratejist/Ertan karari gerektirir.

---

## Uygulama Notu

Bu protokol, Justin'in ML/hibrit ailesine gecisiyle (Faz 1 — Stratejist v6 turu, HENUZ
BASLATILMADI) birlikte devreye girer. Faz 1 tetiklendiginde, Arastirmaci ve Backtest Muhendisi
gorev tanimlarinin "GECMIS CALISMA/CERCEVE DOSYASI" bolumune su satir eklenmelidir:
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (ML/hibrit yaklasimlar icin
ZORUNLU anti-overfitting protokolu — purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri onceden sabit)`
