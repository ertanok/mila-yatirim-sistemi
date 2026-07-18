# GOREV TANIMI — Orkestrator → Stratejist (v6, FAZ 1)

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: Yol1 disi ozel tur — bu bir "yeni hipotez uret" veya "governance/karar-sunum"
  turu DEGIL; **Faz 1 — Stratejist v6 turu**dur (bkz. asagida Amac).
- Tarih: 12 Temmuz 2026 (VPS-yerel)
- Gorevlendiren: Orkestrator, Ertan'in acik bildirimi uzerine ("(a) onaylandi, uc sertlestirmeyle
  ... Faz 1'e gec")
- Onceki asama: Faz 0 — TAMAMLANDI (tum 4 madde), bkz. `justin_gold_scalping_karar_ve_governance_
  20260714.md`, Bolum 3.

## Amac — FAZ 1: Bolum 2 Cercevesini Somut Arastirmaci Gorev Tanimina Cevirme

Ertan, Stratejist'in v5 raporundaki (Bolum 3) **(a) — genis-kapsamli yontem-degisikligi**
secenegini, Orkestrator'un onerdigi **UC SERTLESTIRME (S1, S2, S3) ile birlikte** onaylamistir
(bkz. `justin_gold_scalping_karar_ve_governance_20260714.md`, Bolum 1).

Onaylanan (a)'nin tanimi — **"ve/veya" DEGIL "VE"** (zaman-ufku degisikligi OPSIYONEL degil
ZORUNLU bir bilesen):

> Arastirmaci'ya, kural-tabanli fiyat-aksiyonu yerine ozellik-tabanli klasik ML (orn.
> LightGBM/XGBoost), daha zengin bir veri/ozellik seti **VE** daha genis bir zaman-dilimi/
> tutma-suresi ile YENI bir Gold Scalping yaklasimi arastirma gorevi verilecek.

**Sizden istenen (bu turun TEK isi):** Yukaridaki genis-kapsamli cerceveyi (orkestrator_
degerlendirme_madde7_gold_scalping_20260714.md, Bolum 2'de detaylandirilan analiz — "maliyet
duvari" ayristirmasi, zaman-ufku degisikliginin neden zorunlu oldugu) somut, tek ve calistirilabilir
bir **Arastirmaci gorev tanimina** cevirmeniz. Bu bir hipotez uretme turu degil, bir sonraki
Arastirmaci turunun gorev tanimini yazma turudur. Asagidaki alanlari acikca doldurmaniz beklenir:

- **YAKLASIM TURU:** ML/hibrit (aday: LightGBM/XGBoost — kesin degil, siz teyit/degistirebilirsiniz,
  gerekceyle)
- **ZAMAN-DILIMI:** M15+ VEYA M1-giris + genis-ATR-hedef (iki alt-secenekten hangisinin/hangi
  kombinasyonun Arastirmaci'ya verilecegine siz karar verin, gerekceyle — Bolum 2'deki maliyet/ATR
  yapisal dezavantajini hafifletme mantigina uygun olmali)
- **VERI/FEATURE IHTIYACI:** Arastirmaci'nin toplayacagi/uretecegi ozellik seti (coklu-timeframe
  confluence, hacim/tick-yogunlugu, oturum/gun-ici konum vb. — kapali bir liste degil, siz uygun
  gordugunuzu belirleyin)
- **RISKLER:** overfitting, veri sizintisi, canliya-gecebilirlik (MT5 agent icinde gercek-zamanli
  cikarim suresi, model dagitim sekli) dahil

## RESMI OLARAK YURURLUKTEKI UC SERTLESTIRME — Arastirmaci Gorev Tanimina AYNEN Islenecek

Asagidaki uc madde, governance kaydinda ("kalici governance kaydi") zaten kesinlesmis durumda;
sizden bunlari kendi ifadenizle tekrar tartismaniz degil, yazacaginiz Arastirmaci gorev tanimina
**aynen/dogru referanslarla** islemeniz beklenir:

**S1 — Maliyet-orani zorunlulugu:** Yeni yaklasimin hedef islem-basi brut kazanci, tahmini
maliyetin en az ~15-20 kati olmali. Bu, Backtest Muhendisi'nin kalici on-kontrol standardina
zaten islenmis durumda — Arastirmaci gorev tanimina, tasarimin bu on-kontrolden GECMESI
GEREKTIGI acikca yazilmali. Referans: `justin_backtest_onkontrol_standardi.md`, Madde 2.

**S2 — ML anti-overfitting protokolu:** Purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri egitimden once sabit. Bu protokol Arastirmaci
gorev tanimina **BASTAN (ilk turden itibaren)** yazilmalidir — sonradan eklenecek bir kontrol
degildir. Arastirmaci gorev tanimina, protokol dosyasinin kendi "Uygulama Notu" bolumunde
belirttigi asagidaki satiri aynen ekleyin:
`C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md (ML/hibrit yaklasimlar icin
ZORUNLU anti-overfitting protokolu — purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri onceden sabit)`

**S3 — On-taahhutlu gunbatimi maddesi (RESMI GOVERNANCE KAYDI, Arastirmaci gorev tanimina AYNEN
islenecek):**

> ML ailesinde 2 tam tur ayni olumsuz paternle RED olursa, otomatik olarak Ertan'a yeniden
> cikilir, varsayilan oneri (b) [alt-hedefi durdurma] olur.

Uygulama detaylari (gorev tanimina aynen tasinacak):
- "Tam tur" = bir Stratejist cagrisi (Arastirmaci → Stratejist → Backtest Muhendisi → Risk
  Analisti zincirinin bir Risk Analisti KARARI ile sonuclanmasi).
- "Ayni olumsuz patern" = H1/H2/H3'te gorulenle ayni imza: aggregate/on-kontrolde "anlamli"
  gorunen bir sinyal/model, Backtest Muhendisi'nin tam testinde tutarli sekilde PF<1 veya benzeri
  sistematik RED sonucu vermesi. Farkli bir basarisizlik modu (veri/altyapi hatasi, on-kontrolde
  elenme) bu sayaca DAHIL DEGIL.
- Sayac Faz 1'in ILK Arastirmaci/Stratejist turunden itibaren SIFIRDAN baslar (H1/H2/H3'un
  kural-tabanli-aile sayaci bu yeni ML-ailesi sayacina DEVREDILMEZ).
- 2. tam turun RED sonucu netlestigi anda Orkestrator, Ertan'a **onay sorusu** (bilgi notu DEGIL)
  gonderecek — bu, sizin gorev tanimini yazma isinizin disinda, Orkestrator'un kendi sorumlulugu;
  ama gorev tanimina bu esigin var oldugunu Arastirmaci ve ileride Backtest Muhendisi'nin
  bilecegi sekilde yazmaniz gerekiyor.
- Gunluk pipeline dongu siniri (5/gun, CLAUDE.md) bu sayactan BAGIMSIZ, PARALEL olarak aynen
  gecerliligini korur.

Referans: `justin_gold_scalping_karar_ve_governance_20260714.md`, Bolum 2 (S3 tam metni).

## GECMIS CALISMA/CERCEVE DOSYASI — ZORUNLU REFERANS

`C:\MilaYatirim\Justin\justin_gecmis_calisma.md` — Faz 0/Madde 1 kapsaminda tamamlandi, Justin'in
kalici cerceve dosyasidir. Yazacaginiz Arastirmaci gorev tanimina, asagidaki sabitleri (veya bu
dosyaya acik bir referansi) mutlaka isleyin — bunlar Arastirmaci'nin/Backtest Muhendisi'nin
ileride "gecmis calisma dosyasi yok" diyerek eksik birakamayacagi degerlerdir:

- **HEDEF_PF = 1,5**
- **HEDEF_DD = %20 — KUMULATIF/TOPLAM DONEM BAZINDA, GUNLUK DEGIL** (MilaGold'un gunluk emniyet-
  stopuyla KARISTIRILMAMALI — farkli olcum birimi)
- **Kasa buyuklugu = 2.000 USD** (MilaGold'un 200 USD'sinden bagimsiz)
- **Islem-basi risk yuzdesi = %1 (ust sinir)**
- **Lot/olceklendirme kurali:** baslangic 0,01 lot (sabit), her tam 2.000 USD kasa = 0,01 lot
  (MilaGold'daki "her 200 USD = 0,01 lot" kuralindan bagimsiz)
- HEDEF_WR sabit degil, R:R senaryosuna gore turetilir (Backtest Muhendisi R:R'yi henuz
  secmedi) — 1:1 icin %60,0, 1:2 icin %42,9, 2:1 icin %75,0.

Bu degerlerin tam gerekcesi icin Arastirmaci/Backtest Muhendisi gerekirse `justin_gecmis_
calisma.md`'ye dogrudan basvurabilir; siz gorev tanimina dosyanin yolunu ve yukaridaki ozet
degerleri acikca yazmaniz yeterli.

## VERI IZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN — her zamanki gibi hatirlatiliyor)
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) erisim/
  atif yok — ne veri/parametre kopyalama ne de format/sablon referansi icin acma (14 Temmuz
  netlestirmesi: izolasyon format/cumle-kalibi kopyalamayi da kapsar).
- Calisma dizini: yalniz `C:\MilaYatirim\Justin\` altinda oku/yaz.
- Arastirmaci gorev tanimina yazacaginiz izolasyon hatirlatmasinda da MilaGold/Signal GPT'ye ait
  hicbir sey isimlendirilmeden, sadece "tamamen bagimsiz/orijinal analiz yap" seklinde ifade edin.

## ONCEKI ADIMIN CIKTISI (referans, tekrar hipotez uretmeyin)
- `stratejici_raporu_justin_gold_scalping_20260714.md` (v5) — kendi onceki raporunuz, (a)/(b)
  karar sorusunu sundugunuz tur
- `orkestrator_degerlendirme_madde7_gold_scalping_20260714.md` — Orkestrator'un Bolum 2 analizi
  (maliyet duvari ayristirmasi) ve Bolum 5 plan taslagi (Faz 1 tanimi buradan aliniyor)
- `justin_gold_scalping_karar_ve_governance_20260714.md` — Ertan'in resmi karari + S1/S2/S3
  governance kaydi
- `justin_ml_anti_overfitting_protokolu.md`, `justin_backtest_onkontrol_standardi.md`,
  `justin_gecmis_calisma.md` — kalici standart/cerceve dosyalari (yukarida ozetlendi)

## BEKLENEN CIKTI
`C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260712.md` (v6)
- Oturum ozeti (bu bir hipotez turu degil, Faz 1 gorev-tanimi-yazma turu oldugu acikca belirtilsin)
- Somut Arastirmaci gorev tanimi: YAKLASIM TURU, aday model, zaman-dilimi/tutma-suresi secimi
  (gerekceli), veri/feature ihtiyaci, S1/S2/S3'un gorev tanimina nasil islendiginin ozeti,
  justin_gecmis_calisma.md referansi, izolasyon kisiti
- Riskler (overfitting, veri sizintisi, canliya-gecebilirlik)
- Izolasyon teyidi (her zamanki format)

## ONAY NOKTASI
Bilgi notu — bu Faz 1 turunun kendisi (Arastirmaci'ya henuz gorev verilmiyor, sadece gorev
TANIMI yaziliyor) salt-analiz/dokumantasyon niteliginde, canli sisteme/hesaba hicbir etkisi yok.
4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok (Justin arastirma/demo asamasi,
canli hesap yok), tespit gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-
genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi
notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecek.

**Devam notu (Ertan'in bildirimi):** Faz 1 bu turun (Stratejist v6) TEK adimidir. Devaminda
(Arastirmaci gorevinin fiilen yazilip agent_cagir ile tetiklenmesi, Faz 2) Orkestrator'un otonom
dongusune birakilabilir — sizin raporunuz tamamlandiginda Orkestrator bunu tarama ile yakalayip
kendi karar verecektir, ayrica zorlanmasi gerekmez.
