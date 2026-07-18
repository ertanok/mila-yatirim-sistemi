# GOREV TANIMI — Orkestrator → Stratejist

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: Yol1 dongusu 5, Stratejist turu (v5) — bu bir "yeni hipotez uret" turu DEGIL,
  onceden kosullu olarak tanimlanmis bir GOVERNANCE/KARAR-SUNUM turudur (bkz. asagida).
- Tarih: 11 Temmuz 2026 (VPS-yerel)
- Gorevlendiren: Orkestrator
- Tetikleyici: Risk Analisti'nin Hipotez 3 raporu (risk_analisti_raporu_justin_gold_scalping_hipotez3_20260711.md),
  KARAR: RED.

## Amac — MADDE-7 TETIKLENDI
Kendi v4 raporunuzda (stratejici_raporu_justin_gold_scalping_20260713.md, Bolum 4 "Madde-7
On-Karari") onceden tanimladiginiz kosul simdi ACIKCA karsilaniyor:

- Hipotez 3, Backtest Muhendisi'nin tam testinde (walk-forward/OOS/gercekci-maliyet), H1 ve H2
  ile AYNI paternle RED oldu: aggregate/on-kontrolde istatistiksel olarak "anlamli" gorunen bir
  sinyal, gercek islem kosullarinda (66/66 kesit: tum-donem+IS+OOS+6-WF+4-rejim, 6 senaryo)
  tutarli sekilde PF<1 cikti. Bagimsiz Monte Carlo (500-shuffle x 6 senaryo) sonucun "sansli
  sira" degil yapisal/deterministik oldugunu dogruladi.
- Bu, arka arkaya UCUNCU hipotezdir (H1: seans-filtreli ortalamaya-donus, H2: buyuk-bar-fade,
  H3: rejimden-bagimsiz-uniform-fade) — UC farkli mekanizma, HEPSI ayni RED paterni.

Kendi v4 raporunuzdaki karara gore (Bolum 4), bu turde sizden istenen: Hipotez 4 URETMEK DEGIL,
dogrudan Ertan'a iki somut secenegi sunmak:
  (a) Arastirmaci asamasina GENIS CAPLI yontem-degisikligi onerisi (kural-tabanli disi bir
      yaklasim — orn. klasik ML/feature-tabanli, veya farkli veri/timeframe kombinasyonu), VEYA
  (b) Bu alt-hedefin (Gold Scalping, kural-tabanli fiyat-aksiyonu ailesi) durdurulup Justin'in
      kaynaklarinin farkli bir yaklasima yonlendirilmesi.
Kendi notunuzda da belirttiginiz gibi: **"hicbir sey yapmadan devam etmek" bu turde secenek
DEGILDIR.** Iki secenek arasindaki tercihi siz onceden vermediniz ("Backtest Muhendisi'nin RED
gerekcesinin detayina bagli olacak" demistiniz) — simdi elinizde tam gerekce var (Risk Analisti
raporu, Bolum "Karar Gerekce" ve "Stratejiste Geri Bildirim"), bu turde net bir tercih/oneri
yapmaniz beklenir.

## Ayrica bu turde ele alinmasi istenen ac maddeler (Risk Analisti'nin geri bildirimi)
1. SL/TP semasi (ATR14x0,5, RR=1:1) Muhendis tarafindan H1/H2'den DOGRUDAN TASINDI (siz
   Hipotez-3'e ozel bir deger belirtmediginiz icin) — bu muhendislik kararini onaylayin/reddedin
   (surec/governance kaydi icin, secenek (a)/(b) kararini etkilemez ama kayda gecmeli).
2. Justin icin proje-ozel "gecmis calisma" dosyasi (HEDEF_PF/HEDEF_WR/HEDEF_DD, kasa buyuklugu,
   islem-basi-risk, lot buyuklugu) UCUNCU ardisik turde de tanimsiz kaldi — secenek (a) veya (b)
   ne olursa olsun, gelecekteki turler icin bunun ne zaman/nasil netlesecegine dair bir notunuzu
   isteriz (zorunlu degil, ama faydali).
3. Saat-esleme/DST bulgusu (H1/H2/H3'te 4 kez bagimsiz dogrulandi, hep ayni sonuc) — secenek (a)
   secilirse (yeni yontem/ML), bu riskin yeni yaklasimda da gecerli olup olmadigini belirtin.

## VERI IZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN)
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) erisim/
  atif yok.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz.

## GECMIS CALISMA/CERCEVE DOSYASI
Yok (bkz. onceki turlerdeki ayni not) — Justin icin proje-ozel "gecmis calisma" dosyasi henuz
olusturulmadi.

## ONCEKI ADIMIN CIKTISI
- C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_hipotez3_20260711.md (KARAR: RED,
  bkz. "Karar Gerekce" + "Stratejiste Geri Bildirim" bolumleri)
- Kendi onceki raporunuz: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md
  (v4, Bolum 4 — Madde-7 On-Karari, bu turun kosulunu onceden tanimladiginiz yer)
- Gerekirse referans: risk_analisti_raporu_justin_gold_scalping_hipotez1_20260710.md,
  risk_analisti_raporu_justin_gold_scalping_hipotez2_20260711.md (H1/H2 RED gerekceleri, ayni
  patern)

## BEKLENEN CIKTI
C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260714.md (v5)
- Madde-7 tetiklenme teyidi ve gerekcesi
- Somut tercih/oneri: secenek (a) mi (b) mi, gerekceli — Ertan'a sunulacak net bir karar sorusu
  formatinda (iki secenek de acikca yazilmali, "hicbir sey yapma" secenegi sunulmamali)
- Yukaridaki ac-madde geri bildirimlere (SL/TP onayi, gecmis-calisma-dosyasi, DST) kisa yanit

## ONAY NOKTASI
Bilgi notu — bu turun kendisi Ertan'in onayini gerektirmez (CLAUDE.md, Bolum E, "3 ardisik RED
esigi" netlestirmesi, 10 Temmuz: Madde-7 tetiklenip Stratejist'e genis-capli yaklasim degisikligi
onerisi sunulmasi hala arastirma/backtest asamasi sayilir, canli hesaba hicbir etkisi olmadigi
surece bilgi notu yeterlidir). Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar
kaydi Orkestrator tarafindan dusulecek — ANCAK bu bilgi notunda, Stratejist'in sundugu (a)/(b)
secenekleri Ertan'a acikca, secim yapmasi icin bir karar sorusu olarak iletilecek (bu, projenin
gelecek yonunu belirleyen bir kaynak-tahsisi karari; bilgi-notu kategorisinde kalsa da Ertan'in
fiilen bir tercih yapmasi beklenir — sonraki Arastirmaci/pipeline turu bu tercihe gore
sekillenecek, tercih netlesmeden Arastirmaci'ya yeni bir gorev VERILMEYECEK).
