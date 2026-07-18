# GOREV TANIMI — Orkestrator → Arastirmaci (ML/Feature-Tabanli Gold Scalping, v2 — ML Ailesi TAM TUR 2)

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi, ML/feature-tabanli aile)
- Pipeline adimi: 1/4 (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti, sira
  sabit, atlanamaz)
- Tarih: 12 Temmuz 2026 (VPS-yerel, Orkestrator ground-truth log saatine gore)
- Kaynak/tetikleyici: `risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez3_20260712.md`
  (gorev_id risk_analisti_20260712_1748, tamamlanma 2026-07-12T14:52:05Z) — ML ailesinin TAM TUR
  1'inin (Hipotez 1: LightGBM k=1,5; Hipotez 2: XGBoost k=1,5; Hipotez 3: LightGBM k=2,0) UCUNUN
  DE RED sonuclanmasi uzerine.
- Onceki asama: Faz 1/Stratejist v6 (TAMAMLANDI) + Faz 2/ML v1 tam turu (TAMAMLANDI, 3 hipotez,
  UCU DE RED). Bu gorev, ML ailesinin **TAM TUR 2**'sinin ilk adimidir.

## GOVERNANCE DURUMU — S3 SAYACI (ONEMLI, Arastirmaci'nin bilmesi gereken)
`justin_gold_scalping_karar_ve_governance_20260714.md` Bolum 2 (S3) geregi: ML ailesinde **2 tam
tur** ayni olumsuz paternle (aggregate/on-kontrolde "anlamli" gorunen bir sinyal/model, tam testte
tutarli PF<1/sistematik RED veya bu turdeki gibi 0-islem/AUC~rassal) RED olursa, Orkestrator
otomatik olarak Ertan'a onay sorusu yoneltir (varsayilan oneri: alt-hedefi durdurma).

- **Bu gorev TAM TUR 2'dir.** Tam Tur 1 (ML v1, 3 hipotez) RED sonuclanmistir — ayni patern:
  AUC~0,50-0,52 (rassal-seviyeye yakin), ZORUNLU feature gruplari (ATR/trend/confluence) sifira
  yakin agirlik, TEST'te 0 islem (esik-kalibrasyonu hangi kaynaktan yapilirsa yapilsin).
- **Eger bu tam tur (tur 2) de AYNI patern ile RED sonuclanirsa, Orkestrator pipeline'i
  otomatik olarak durdurur ve Ertan'a onay sorusu gonderir** — bir sonraki Arastirmaci turu
  Orkestrator tarafindan onaysiz baslatilmaz. Bu esik bilgi amaclidir, sizin gorev tanimini
  degistirmez, ama neden bu turde ozellikle FARKLI/YENI bir yaklasim istendigini acikliyor.

## Amac — NEDEN FARKLI FEATURE AILELERI/ETIKET TANIMLARI ISTENIYOR

Tam Tur 1'in Risk Analisti raporu (hipotez 1/2/3, ucu de BAGIMSIZ) su sonuca ulasti: "sorun
model-secimine (LightGBM vs XGBoost) veya barrier-genisligine (k=1,5 vs k=2,0) degil, mevcut
23-feature setinin/etiket tasariminin kendisine bagli." Acik geri-bildirim (Stratejiste Geri
Bildirim, Madde 1 ve 4): bir sonraki tur, AYNI feature ailelerini (coklu-TF confluence, ATR/
volatilite, hacim/tick-yogunlugu, oturum/gun-ici konum, RSI/MACD/lag-return, spread) farkli
parametrelerle tekrar denemek yerine, **GERCEKTEN FARKLI/EK feature aileleri VE/VEYA farkli bir
etiket tanimi** aramalidir.

**Bu turde ZORUNLU: en az 2 tanesi Tam Tur 1'de KULLANILMAMIS feature ailesi/yontem
denenmelidir.** Baslangic noktasi olarak asagidakiler oneriliyor (kapali liste degil, siz
genisletebilir/degistirebilirsiniz, gerekceyle):

1. **Mikro-yapi (microstructure) proxy'leri:** Tick-bazli bid/ask sicrama (bounce) paterni,
   ardisik tick yon-degisim orani (buy/sell baskisi proxy'si — gercek order-flow verisi yoksa
   tick-kural-tabanli bir yaklasim, orn. tick-rule/Lee-Ready benzeri sinif), tick-basina ortalama
   fiyat degisimi varyansi (M15 ic-bar mikro-volatilite, sadece OHLC'den degil).
2. **Rejim/durum (regime) siniflandirmasi ozellikleri:** Trend/yatay(range) rejim etiketi (orn.
   ADX veya benzeri bir trend-gucu olcusu — Tam Tur 1'de KULLANILMADI), rejim-gecis mesafesi
   (son rejim degisiminden bu yana gecen bar sayisi).
3. **Gorece/relative fiyat yapisi:** Gunluk/haftalik pivot noktalarina uzaklik, son N-gunluk
   yuksek/dusuk seviyelerine (support/resistance) uzaklik — Tam Tur 1'in feature setinde YOKTU.
4. **Capraz-piyasa/korelasyon ozelligi (veri erisimi varsa):** DXY (dolar endeksi) veya ABD 10-
   yillik tahvil getirisi ile GOLD'un kisa-donem korelasyon/momentum-uyumu — yalniz MT5 uzerinden
   erisilebilir bir sembol/veri varsa uygulanabilir, yoksa bu maddeyi "veri erisimi yok" diye
   acikca isaretleyip atlayin (MT5 disi harici bir API/kaynak EKLEMEYIN — veri izolasyonu ve
   "yalniz XM/MT5" kurali gecerliligini korur).

**Etiket (label) tanimi icin de alternatif degerlendirin:** Tam Tur 1, ikili (TP-once/SL-once)
triple-barrier kullandi ve "hicbiri" sinifi (%11,5 - %24,9 arasinda k'ya gore) modelin olasilik
dagilimini daraltan bir etken olabilir. Bu turde ek olarak degerlendirin:
- **3-sinifli etiket** (yukari/asagi/notr) — H3'un Stratejiste Geri Bildirim Madde 3'unde
  "simdi daha anlamli hale geldi" denen secenek; ML feature seti degistigi icin tekrar mantikli.
- **Regresyon-tabanli hedef** (N-bar ileri getiri buyuklugu, siniflandirma yerine) — modelin
  "yon" yerine dogrudan "buyukluk+yon" ogrenmesi farkli bir sinyal yakalayabilir.

## Zaman-Dilimi / Tutma-Suresi
Tam Tur 1'deki M15+ karari (zorunlu, S1 maliyet-orani gerekcesiyle) AYNEN GECERLI — bu turde
degistirilmiyor, sadece feature/etiket tarafi degisiyor. M15 (veya H1) giris+tutma-suresi,
ATR(M15)-tabanli SL/TP semasi.

## Yaklasim Turu ve Aday Model
LightGBM birincil aday (Tam Tur 1 ile ayni gerekce: kategorik feature destegi, hiperparametre
maliyeti dusuk) — model AILESI degil, FEATURE/ETIKET tasarimi degisiyor. XGBoost kiyaslama
opsiyonel (zorunlu degil, Tam Tur 1'de zaten iki model ailesi denendi ve fark yaratmadi — bu
turde tek model + farkli feature/etiket kombinasyonlarina odaklanmak daha verimli olabilir, ama
karar Arastirmaci/Stratejist'e birakilir).

## VERI IZOLASYONU — ZORUNLU KISIT (degismedi)
Bu proje kapsaminda baska bir dahili sistemin bulgu/veri/parametresine erisim veya atif YOKTUR;
tamamen bagimsiz/orijinal analiz yapilmalidir. Tek veri kaynagi XM/MT5 fiyat verisidir (dogrudan
MetaTrader5 kutuphanesi araciligiyla). Calisma dizini yalniz `C:\MilaYatirim\Justin\` altindadir,
disina erisim yok (format/sablon referansi icin bile MilaGold/Lisa/Signal GPT dosyalari acilmaz).

## Zorunlu Protokol (S2 — ML Anti-Overfitting, degismedi)
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md` — purged/embargolu walk-forward,
test-seti tek-kullanim, feature sizinti kontrol listesi, basari kriterleri onceden sabit. Coklu-
zaman-dilimi/mikro-yapi feature'lari icin ozellikle ileri-bakis (look-ahead) riski yuksek —
feature hesaplama zaman damgasinin, o M15 aninda GERCEKTEN mevcut olan en son KAPANMIS veriye
dayandigini ayrica teyit edin.

## On-Kontrol Hatirlatmasi (S1 — Maliyet-Orani, degismedi)
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` Madde 2 — hedef islem-basi brut
kazanc, tahmini toplam maliyetin en az ~15-20 kati olmali. Tam Tur 1'den bilinen: k=1,5 → 15,97x
(esik sinirinda), k=2,0 → 21,29x (esigi asiyor). Bu oranlar zaten M15+ tasarimindan geliyor,
bu turde tekrar hesaplanmasina gerek yok, referans olarak kullanilabilir.

## Gecmis Calisma / Cerceve Dosyasi (zorunlu referans, degismedi)
`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — HEDEF_PF=1,5; HEDEF_DD=%20 (kumulatif/toplam
donem, gunluk degil); kasa=2.000 USD; islem-basi risk=%1 (ust sinir); lot 0,01 sabit baslangic,
her 2.000 USD kasa=0,01 lot; HEDEF_WR R:R'ye gore turetilir (1:1→%60,0; 1:2→%42,9; 2:1→%75,0).

## ONCEKI ADIMIN CIKTISI (referans, tekrar hipotez uretmeyin — bu bir arastirma turu, hipotez
uretme Stratejist'in isi)
- `risk_analisti_raporu_justin_gold_scalping_ml_v1_hipotez1_20260712.md`,
  `..._hipotez2_20260712.md`, `..._hipotez3_20260712.md` — Tam Tur 1'in 3 hipotezinin RED
  gerekceleri ve Stratejiste Geri Bildirim bolumleri (feature-onem tablosu, AUC paterni,
  esik-kalibrasyonu bulgulari) — bu turun feature/etiket tasarimini FARKLILASTIRMAK icin
  detayli okunmali.
- `arastirmaci_gold_scalping_ml_raporu.md` (v1) — hangi feature ailelerinin ZATEN denendigi
  (coklu-TF confluence, ATR/volatilite, hacim/tick-yogunlugu, oturum/gun-ici konum, RSI/MACD/
  lag-return, spread) — bunlarin AYNISI degil, EK/FARKLI olanlar bu turde onceliklendirilmeli.

## BEKLENEN CIKTI
- Rapor formati: Markdown, `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_ml_v2_raporu.md`
- Bolumler: Ozet, Gozlemler (yeni feature ailelerine ozel), Onerilen Feature Seti ve Label
  Tanimi (hangilerinin v1'den FARKLI oldugu acikca isaretlenmis), En Az 1 Somut ML Tasarim
  Onerisi (model + feature + zaman-dilimi + kaba maliyet-orani on-tahmini), Riskler/
  Sinirlamalar (overfitting, veri sizintisi, canliya-gecebilirlik dahil), Acik Sorular,
  Izolasyon Notu.

## Sonraki Adim
Rapor tamamlaninca Orkestrator, Stratejist'i bu raporla gorevlendirecek (pipeline sirasi geregi
Backtest Muhendisi'ne dogrudan atlanmaz).

## ONAY NOKTASI
Bilgi notu — bu tur (Arastirmaci, ML ailesi Tam Tur 2'nin ilk adimi) salt-arastirma/analiz
niteliginde, canli sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik
tam, mali etki yok (Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu
degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi
gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator
tarafindan dusulecek.

**Onemli hatirlatma (S3):** Bu tam turun (tur 2) Risk Analisti karari RED ve AYNI patern
(anlamli-gorunen-ama-tam-testte-cokme) ile sonuclanirsa, Orkestrator bir sonraki Arastirmaci
turunu OTOMATIK BASLATMAZ — Ertan'a onay sorusu gonderir. Bu, sizin (Arastirmaci) is akisinizi
degistirmez, ama Stratejist/Backtest Muhendisi/Risk Analisti asamalarinda bu esigin farkinda
olunmasi gerekir.
