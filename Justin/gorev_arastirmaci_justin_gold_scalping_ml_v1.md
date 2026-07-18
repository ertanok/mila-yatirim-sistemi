# GOREV TANIMI — Orkestrator → Arastirmaci (ML/Feature-Tabanli Gold Scalping, v1)

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile —
  kural-tabanli fiyat-aksiyonu ailesi H1/H2/H3 ile Madde-7 tetiklenerek kapatildi)
- Pipeline adimi: 1/4 (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti, sira
  sabit, atlanamaz)
- Tarih: 12 Temmuz 2026 (VPS-yerel)
- Kaynak: Stratejist v6 raporu (`stratejici_raporu_justin_gold_scalping_20260712.md`, Bolum 7),
  Faz 1 ciktisi — bu gorev tanimi o raporun Bolum 7'sinden aynen alinmistir.
- Onceki asama: Faz 0 (TAMAMLANDI) + Faz 1/Stratejist v6 (TAMAMLANDI). Bu gorev, Faz 2'nin ilk
  adimidir.

## Amac
XAUUSD (Gold) uzerinde, **M15 ve uzeri zaman-dilimi/tutma-suresine** dayanan, **ozellik-tabanli
klasik ML (LightGBM birincil aday, XGBoost kiyaslama modeli)** kullanan YENI bir Gold Scalping
yaklasimi icin arastirma/hipotez raporu uret. Bu, M1 kural-tabanli fiyat-aksiyonu ailesinin
(H1/H2/H3, hepsi RED) YERINE gecen, iki bileseni BIRLIKTE ("VE", opsiyonel degil) iceren bir
yon degisikligidir: (i) kural-tabanli yerine ozellik-tabanli ML, (ii) M1 yerine daha genis bir
zaman-dilimi/tutma-suresi.

## Zaman-Dilimi / Tutma-Suresi
- **M15+ birincil/zorunlu tasarim.** Giris sinyali ve tutma-suresi M15 (veya daha genis, orn.
  H1) bazinda kurgulanmali. Kesin bar sayisi onceden sabitlenmiyor — veri gozlemine birakiliyor.
- SL/TP semasi ATR(M15) tabanli olmali (kesin katsayi Stratejist'in bir sonraki turde bu
  yaklasima OZEL belirleyecegi bir deger/aralik olacak — otomatik tasima yok, bkz.
  `justin_backtest_onkontrol_standardi.md`, Madde 3).
- M1-giris+genis-ATR-hedef varyanti ZORUNLU degil; veri kesfinde acik bir on-bulgu varsa
  raporda ikincil/opsiyonel bir bolum olarak sunulabilir, ama ayni maliyet-orani on-kontrolune
  (asagida) tabidir.

## Yaklasim Turu ve Aday Model
- Ozellik-tabanli klasik ML. Birincil aday: **LightGBM**. Ikincil/kiyaslama: **XGBoost** (ayni
  feature seti uzerinde, karsilastirmali sunulmasi onerilir, zorunlu degil).
- Hibrit (eski kural-tabanli sinyalleri on-filtre olarak kullanma) bu turde ONERILMIYOR —
  tamamen bagimsiz/orijinal feature-tabanli analiz yapilmali.
- Derin ogrenme/RL bu ilk turde kapsam DISI (veri hacmi/karmasiklik-overfitting gerekcesiyle);
  ileride ayrica degerlendirilebilir.

## Veri / Feature Ihtiyaci (baslangic noktasi, kapali liste degil)
1. Coklu-zaman-dilimi confluence (M15/H1/H4 trend uyumu)
2. Volatilite ozellikleri (ATR(14) M15, ATR genisleme/daralma orani, bant genisligi)
3. Hacim/tick-yogunlugu (M15 bar basina tick-hacim, hacim momentum/anomali)
4. Oturum/gun-ici konum (Asya/Londra/NY bayraklari, dongusel saat kodlamasi, oturum
   acilis/kapanisina mesafe, haftanin gunu)
5. Fiyat yapisi/momentum (lag return'ler, RSI, MACD, higher-high/lower-low ardisiklik)
6. Maliyet/likidite gostergesi (ortalama spread, spread volatilitesi)
- **Etiket (label) onerisi:** Triple-barrier yontemi (N-bar ileri TP-once/SL-once/hicbiri).
- Veri kaynagi: M15 OHLCV + tick-hacim, dogrudan MetaTrader5 kutuphanesi; H1/H4 barlari ayni
  ham veriden yeniden ornekleme yoluyla turetilmeli.

## VERI IZOLASYONU — ZORUNLU KISIT
Bu proje kapsaminda baska bir dahili sistemin bulgu/veri/parametresine erisim veya atif YOKTUR;
tamamen bagimsiz/orijinal analiz yapilmalidir. Tek veri kaynagi XM/MT5 fiyat verisidir
(dogrudan MetaTrader5 kutuphanesi araciligiyla). Calisma dizini yalniz
`C:\MilaYatirim\Justin\` altindadir, disina erisim yok (format/sablon referansi icin bile
MilaGold/Lisa/Signal GPT dosyalari acilmaz — 14 Temmuz netlestirmesi).

## Zorunlu Protokol (S2 — ML Anti-Overfitting)
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md` (ML/hibrit yaklasimlar icin
ZORUNLU anti-overfitting protokolu — purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri onceden sabit). Bu protokol Arastirmaci
asamasindan itibaren (feature tasarimi/label tanimi/veri bolme mantiginda) gecerlidir — sonradan
eklenecek bir kontrol degildir.

## On-Kontrol Hatirlatmasi (S1 — Maliyet-Orani, Backtest Muhendisi asamasinda uygulanacak
ama tasarim BUNU DIKKATE ALARAK yapilmali)
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` — tasarimin hedef islem-basi
brut kazanci, tahmini toplam maliyetin (spread+slipaj) en az ~15-20 kati olacak sekilde
kurgulanmis olmali; bunu karsilamayan tasarimlar Muhendis on-kontrolunde otomatik elenir.
Raporunuzda, onerilen zaman-dilimi/hedef buyuklugunun bu orani nasil karsilamasi beklendigine
dair kaba bir on-tahmin (ATR(M15) buyuklugu, tipik spread) sunmaniz faydali olur.

## Governance Esigi (S3 — bilgi amacli, bilmeniz gereken)
ML ailesinde 2 tam tur (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti zinciri,
bir Risk Analisti KARARI ile sonuclanan) ayni olumsuz paternle (aggregate/on-kontrolde
"anlamli" gorunen bir sinyal/model, tam testte tutarli PF<1/sistematik RED) sonuclanirsa,
Orkestrator otomatik olarak Ertan'a onay sorusu yoneltir, varsayilan oneri alt-hedefi
durdurmadir. Sayac bu Faz 1'in ilk turunden sifirdan baslar (H1/H2/H3 sayaci devrolmez).
Gunluk pipeline dongu siniri (5/gun) bu sayactan bagimsiz, paralel gecerlidir.

## Gecmis Calisma / Cerceve Dosyasi (zorunlu referans)
`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — HEDEF_PF=1,5; HEDEF_DD=%20 (kumulatif/toplam
donem, gunluk degil); kasa=2.000 USD; islem-basi risk=%1 (ust sinir); lot 0,01 sabit baslangic,
her 2.000 USD kasa=0,01 lot; HEDEF_WR R:R'ye gore turetilir (1:1→%60,0; 1:2→%42,9; 2:1→%75,0).

## ONCEKI ADIMIN CIKTISI (referans)
- `stratejici_raporu_justin_gold_scalping_20260712.md` (v6, Bolum 1-6 — bu gorev tanimini
  ureten gerekce/karar zinciri)
- `justin_gold_scalping_karar_ve_governance_20260714.md`, `orkestrator_degerlendirme_madde7_
  gold_scalping_20260714.md` — ust-seviye governance/karar kaynaklari

## BEKLENEN CIKTI
- Rapor formati: Markdown, `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_ml_raporu.md`
- Bolumler: Ozet, Gozlemler (M15+ volatilite/hacim/oturum paternleri), Onerilen Feature Seti
  ve Label Tanimi, En Az 1 Somut ML Tasarim Onerisi (model + feature + zaman-dilimi + kaba
  maliyet-orani on-tahmini), Riskler/Sinirlamalar (overfitting, veri sizintisi, canliya-
  gecebilirlik dahil), Acik Sorular, Izolasyon Notu.

## Sonraki Adim
Rapor tamamlaninca Orkestrator, Stratejist'i bu raporla gorevlendirecek (pipeline sirasi geregi
Backtest Muhendisi'ne dogrudan atlanmaz); Stratejist bu asamada yaklasima ozel SL/TP/ATR
katsayisini belirleyecek.

## ONAY NOKTASI
Bilgi notu — bu tur (Arastirmaci, Faz 2 ilk adimi) salt-arastirma/analiz niteliginde, canli
sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki
yok (Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecek.
