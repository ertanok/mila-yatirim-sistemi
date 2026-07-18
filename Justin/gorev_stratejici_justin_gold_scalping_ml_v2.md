# GOREV TANIMI — Orkestrator → Stratejist (ML/Feature-Tabanli Gold Scalping, v2 — ML Ailesi TAM TUR 2)

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
- Pipeline adimi: 2/4 (Arastirmaci → **Stratejist** → Backtest Muhendisi → Risk Analisti, sira
  sabit, atlanamaz — Backtest Muhendisi'ne dogrudan gecilmez)
- Tarih: 12 Temmuz 2026 (VPS-yerel)
- Onceki asama: Arastirmaci (ML ailesi Tam Tur 2, 1/4, gorev_id arastirmaci_20260712_1758) —
  TAMAMLANDI. Rapor tam ve BEKLENEN CIKTI spesifikasyonundaki tum bolumleri (Ozet, Gozlemler,
  Onerilen Feature Seti ve Label Tanimi, En Az 1 Somut ML Tasarim Onerisi, Riskler/
  Sinirlamalar, Acik Sorular, Izolasyon Notu) icermektedir.

## Governance Durumu — S3 Sayaci (ONEMLI)
`justin_gold_scalping_karar_ve_governance_20260714.md` Bolum 2 (S3) geregi: ML ailesinde 2 tam
tur ayni olumsuz paternle RED olursa Orkestrator otomatik olarak Ertan'a onay sorusu yoneltir
(varsayilan oneri: alt-hedefi durdurma). Tam Tur 1 (H1: LightGBM k=1,5; H2: XGBoost k=1,5; H3:
LightGBM k=2,0) UCUNUN DE RED sonuclanmasiyla sayac su an **1/2**. Bu gorev (Stratejist, Tam Tur
2'nin 2. adimi) bir Risk Analisti KARARI uretmedigi icin S3 sayaci bu asamada islemez — sadece
bilgi amaclidir. Tur 2'nin nihai Risk Analisti karari RED ve AYNI patern ile sonuclanirsa sayac
2/2'ye ulasir ve Orkestrator bir sonraki Arastirmaci turunu onaysiz baslatmaz.

Not (tarih tutarliligi, bilgi amacli): governance dosyasi ic-metninde "14 Temmuz 2026" tasiyor,
ancak ground-truth Orkestrator log kayitlari zincirin 12 Temmuz icinde tutarli sekilde
gerceklestigini gosteriyor — bu daha once (cagri_20260712_1758_arastirmaci.md) not edilmis bir
sayisal/tarihsel tutarsizliktir, karari ETKILEMEZ, tekrar not dusulur.

## Amac
Arastirmaci'nin v2 raporuna (BULGU 1-11, asagida) dayanarak, Tam Tur 1'in RED gerekcesine
("sorun model-secimi/barrier-genisligi degil, feature seti/etiket tasariminin kendisi") somut
karsilik veren, EN AZ 2 YENI feature ailesi iceren 2-3 hipotez uret. Bu bir "yeniden arastirma"
turu degildir — Arastirmaci'nin BULGU'larini ham girdi olarak kullanip karar/sentezi sizin
yapmaniz beklenir.

## Karar Vermeniz Beklenen Ozel Noktalar (Arastirmaci v2 raporundan devralinan acik sorular)
1. **Feature grubu secimi/onceligi (Grup A-D):** Arastirmaci Grup A (ADX/rejim — SADECE
   buyukluk/volatilite bilgisi tasir, BULGU 2 geregi yon-tahmin-edici DEGIL), Grup B (pivot/
   gorece S-R — BULGU 5'e gore digerlerinden goreceli daha guclu bir aday), Grup C (DXY —
   es-zamanli guclu ama ongorucu/lead-lag ~sifir, BULGU 6, DUSUK ONCELIK onerildi, veri kaynagi
   da SUPHELI/dogrulanmamis), Grup D (mikro-yapi/tick-proxy — SINIRLI 20-gunluk pencere,
   olceklenebilirlik COZULMEMIS, Acik Soru 1) onerdi. Hangilerini bu turun ZORUNLU feature
   setine dahil edeceginizi, hangilerini disarida birakacaginizi (veya kosullu/opsiyonel
   yapacaginizi) gerekceyle belirleyin.
2. **Etiket semasi:** Tam Tur 1'de ikili (TP-once/SL-once, "hicbiri" filtrelenmis, N=16/k=1,5)
   kullanildi ve RED sonuclandi. Arastirmaci bu turde alternatif olarak **3-sinifli deadzone**
   etiketi (BULGU 10, triple-barrier'DAN FARKLI yontem, k=0,3xATR14 civari orta-dengeli dagilim)
   onerdi; **regresyon-hedefini (BULGU 11) ONERMEDI** (sinyal/gurultu orani ~74x, cok dusuk).
   Ayni ikili semayi farkli feature'larla mi tekrar deneyeceginizi, yoksa 3-sinifli semaya mi
   gececeginizi (veya ikisini paralel mi test ettireceginizi) KESIN olarak belirleyin.
3. **N/k (zaman-dilimi/tutma-suresi) — degistirilecek mi, korunacak mi:** Tam Tur 1'in
   Stratejist karari N=16 (4 saat)/k=1,5xATR14 idi (+ k=2,0 duyarlilik varyanti); Risk
   Analisti'nin RED gerekcesi bunu degil feature/etiket tasarimini hedef aliyordu. Arastirmaci
   v2 raporu bu turde N/k'yi YENIDEN OLCMEDI (BULGU'lar gozlem icin N=8/2-saat penceresi
   kullandi, bu bir olcum penceresidir, N/k karari degildir). Ayni N=16/k=1,5 tasarimini
   koruyup KORUYUP korumayacaginiza (yoksa Grup B/D'nin farkli bir ufuk gerektirip
   gerektirmedigine) karar verin.
4. **Grup D (mikro-yapi) olceklenebilirlik sorusu (Acik Soru 1):** Arastirmaci uc secenek
   sundu — (a) yalniz son N-ay/yil icin egitim+test, (b) M1-bar-tabanli daha kaba proxy'ye
   indirgeme, (c) bu turde tamamen ELEME. Hangisini secip Backtest Muhendisi'ne
   devredeceginizi belirleyin (Grup D'yi ilk hipoteze DAHIL ETMEMEK de gecerli bir karardir).
5. **DXY veri kaynagi guveni (Acik Soru 2, bilgi amacli):** USDX-SEP26 sembolunun 4,2 yillik
   gecmisinin surekli-kontrat/splice olabilecegi SUPHESI dogrulanmadi. Grup C'yi dahil
   ederseniz, Backtest Muhendisi'nin S2 feature-sizinti kontrol listesi kapsaminda bu seriyi
   (roll-over sicramalari vb.) BAGIMSIZ dogrulamasi gerektigini gorev tanimina acikca isleyin.

## Zaman-Dilimi / Tutma-Suresi (mevcut durum, siz kesinlestirin)
M15+ karari (S1 maliyet-orani gerekcesiyle) sabit — degistirilmiyor, sadece feature/etiket
tarafinin nasil degisecegine (ve N/k'nin AYNEN korunup korunmayacagina, Madde 3) siz karar
verirsiniz.

## Zorunlu Protokol (S2 — ML Anti-Overfitting, degismedi)
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md` — purged/embargolu walk-forward,
test-seti tek-kullanim, feature sizinti kontrol listesi, basari kriterleri onceden sabit. Grup
B/D icin ozellikle ileri-bakis (look-ahead) riski ayrica vurgulanmali (rolling pivot/S-R'in
dogru gun/hafta sinirinda kesildigi, tick-agregasyonlarinin nedensel oldugu).

## On-Kontrol Hatirlatmasi (S1 — Maliyet-Orani, degismedi)
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` Madde 2 — Tam Tur 1'den bilinen:
k=1,5 → 15,97x (esik alt sinirinda), k=2,0 → 21,29x (esigi rahatca asiyor). N/k degismezse bu
oranlar gecerliligini korur; degisirse yeniden hesaplanmali.

## Gecmis Calisma / Cerceve Dosyasi (zorunlu referans, degismedi)
`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — HEDEF_PF=1,5; HEDEF_DD=%20 (kumulatif/toplam
donem, gunluk degil); kasa=2.000 USD; islem-basi risk=%1 (ust sinir); lot 0,01 sabit baslangic,
her 2.000 USD kasa=0,01 lot; HEDEF_WR R:R'ye gore turetilir (1:1→%60,0; 1:2→%42,9; 2:1→%75,0).

## VERI IZOLASYONU — ZORUNLU KISIT (degismedi)
Baska bir dahili sistemin (MilaGold/Lisa/Signal GPT) bulgu/veri/parametresine erisim veya atif
YOK — ne veri/parametre kopyalama ne de format/sablon referansi icin acma. Calisma dizini yalniz
`C:\MilaYatirim\Justin\` altinda.

## ONCEKI ADIMIN CIKTISI (referans)
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_ml_v2_raporu.md` — bu turun girdisi (BULGU
  1-11, Onerilen Feature Seti/Label Tanimi, ML Tasarim Onerisi, Riskler, Acik Sorular,
  Stratejist'e Not).
- `C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v1_20260712.md` — Tam Tur
  1'in Stratejist karari (N=16/k=1,5 birincil + k=2,0 duyarlilik, ikili etiket, Feature Grup
  1-5/6 onceligi) — bu turde neyin KORUNDUGU/neyin DEGISTIGI acikca isaretlenmeli.
- Tam Tur 1'in Risk Analisti raporlari (`risk_analisti_raporu_justin_gold_scalping_ml_v1_
  hipotez1/2/3_20260712.md`) — RED gerekceleri ve Stratejiste Geri Bildirim bolumleri.

## BEKLENEN CIKTI
`C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md`
- Oturum ozeti (Arastirmaci v2 raporundan hangi bulgulari girdi olarak aldiginizin ozeti +
  Tam Tur 1'den neyin devraldiginiz/degistirdiginiz)
- Yukaridaki "Karar Vermeniz Beklenen Ozel Noktalar" 1-5 maddelerine acik yanit
- 2-3 somut hipotez (stratejici_system_prompt.md formatinda: HIPOTEZ ADI, YAKLASIM TURU,
  MANTIK, YONTEM DETAYI, GIRIS/CIKIS MEKANIZMASI, SL/TP veya RISK YONETIMI, DOGRULAMA IHTIYACI,
  RISKLER, ONCELIK)
- Backtest Muhendisi icin Notlar (S1/S2 protokollerinin nasil uygulanmasi gerektigi, Grup D
  olceklenebilirlik karari, DXY veri-kaynagi dogrulama ihtiyaci varsa dahil)
- Izolasyon teyidi

## Sonraki Adim
Rapor tamamlaninca Orkestrator, Backtest Muhendisi'ni bu raporla gorevlendirecek (pipeline
sirasi geregi Risk Analisti'ne dogrudan atlanmaz).

## ONAY NOKTASI
Bilgi notu — bu adim (Stratejist, ML ailesi Tam Tur 2/2. adim) hipotez/tasarim niteliginde,
canli sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali
etki yok (Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu degil, etki
alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez.
Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator
tarafindan dusulecek.

**Onemli hatirlatma (S3):** Bu tam turun (tur 2) Risk Analisti karari RED ve AYNI patern ile
sonuclanirsa, Orkestrator bir sonraki Arastirmaci turunu OTOMATIK BASLATMAZ — Ertan'a onay
sorusu gonderir. Bu, sizin (Stratejist) is akisinizi degistirmez, ama Backtest Muhendisi/Risk
Analisti asamalarinda bu esigin farkinda olunmasi gerekir.
