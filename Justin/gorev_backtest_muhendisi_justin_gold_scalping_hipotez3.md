=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-10 19:00
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — HIPOTEZ 3, Asama 1/2 (kural-tabanli)

GOREV              : Hipotez 3'u ("Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali", eski adi
"Rejim-Farkinda Hibrit") test et. Kapsam, Stratejist'in v4 raporunun Bolum 5'inde tanimlandigi
gibi v3'e gore SIKILASTIRILMIS/odak-degistirilmis: hipotez "trend'de bir kural, range'de baska
bir kural" degil; rejimden BAGIMSIZ, uniform, zayif bir sinyaldir. Rejim etiketleri (VOL:
ATR14/trailing-100-medyan; TREND: ER20/trailing-100-medyan — research_scalping_rejim.py
tanimiyla AYNEN) birincil sinyal DEGIL, IKINCIL bir filtre/dogrulayici olarak test edilecek
(sinyal + belirli-rejimde-miyiz kombinasyonunun PF'yi iyilestirip iyilestirmedigi).

TIMEFRAME ONCELIGI: M1 BIRINCIL odak (Stratejist'in kaba Bonferroni yeniden-okumasinda M1
sonuclari buyuk olcude dayanikli cikti). M5 IKINCIL/exploratory kalmali, uzerinde fazla
kaynak/zaman harcanmamali — M5 bulgularinin cogu coklu-test duzeltmesiyle anlamliligini
kaybediyor (8/8→5/8, 25/32→~9/32, 7/8→4/8, M5 tarafi buyuk olcude dayanaksiz).

SIRALI ON-KONTROLLER (tam walk-forward/OOS baslamadan ONCE, bu sirayla; herhangi biri
gecilemezse ana teste GECILMEDEN Hipotez 3 bu asamada RED sonuclandirilir — bkz. rapor Bolum 4
madde-7 kosullu karari):
1. Saat-esleme/DST bagimsiz dogrulama — 4. kez tekrar, atlanmamali.
2. Coklu-karsilastirma duzeltmesi (Bonferroni veya tercihen FDR/Benjamini-Hochberg) kendi
   IS-donem verisinde RESMI olarak uygulanmali ve hangi rejim-segmentlerinin/streak-hucrelerinin
   gercekten hayatta kaldigi raporlanmali. Stratejist'in kaba Bonferroni yeniden-okumasi sadece
   bir on-isaret, resmi degil.
3. Gercekci-maliyet/seans-filtresi erken kontrolu (spread, slipaj, Justin'in olasi seans/saat
   kisitlari) — on-kontrol 1-2'yi gecen segmentler icin ham devam/donus oraninin hala %50'den
   anlamli sapip sapmadigi kontrol edilmeli. H1 ve H2 tam bu adimda ("aggregate'te anlamli,
   fiilen-islem-edilen altkumede anlamsiz") RED cikmisti; bu riski erken elemek/onaylamak icin.
4. MAX_TICK_MISMATCH_SEC=60 standart olarak kullanilir (v3 Bolum 4'te onaylandi, degismedi).

ANA TEST (on-kontroller 1-3 gecilirse): Kural-tabanli Asama 1/2 versiyonun (M1 birincil, M5
ikincil) walk-forward/OOS testi, PF/WR kirilma-noktasi karsilastirmasi, en az 6 pencere/18 ay
standardi (H1/H2'de kullanilan standart) korunarak.

ASAMA SIRASI/ML KAPISI (degismedi): Kural-tabanli Asama 1/2 kendi basina (walk-forward/OOS'ta
PF>=1, tercihen kirilma-noktasinin uzerinde) pozitif sonuc vermeden ML Asama 3'e (LightGBM vb.)
GECILMEYECEK.

OVERFITTING GUVENLIK AGI (degismedi): Rejim tanimindaki esik degerleri (ATR/ER trailing pencere
genisligi) genis araliklarda TARANMAYACAK; her taramada walk-forward/OOS raporlanacak.

ALT-ORNEKLEM KUCULMESI: Arastirmaci'nin raporladigi n degerleri (rejim ayrimi sonrasi ~yariya,
streak=5'te 1.196-1.592 araligina kadar dusuyor) IS/OOS bolme kararinda baslangic noktasi olarak
kullanilmali — kucuk alt-orneklemlerde OOS'un pratik olarak anlamli kalabilmesi icin pencere
sayisi/genisligi buna gore ayarlanmali.

TAM ISLEM LOGU: H1/H2 standardi korunur — Risk Analisti'nin bagimsiz tam dogrulama yapabilmesi
icin tam islem logu bastan saglanir.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md (bu gorevin dogrudan
  kaynagi — Bolum 5, GOREV TANIMI birebir gecerli)
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260712.md (v3 — karar kurali ve
  orijinal notlar; v4 tarafindan GUNCELLENDI/SIKILASTIRILDI, yerine gecmedi)
- C:\MilaYatirim\Justin\_ek_bolum_rejim.md (Arastirmaci'nin rejim-segmentli ek-veri raporu:
  BULGU3/4, VOL/TREND rejim etiketleri, anlamlilik testleri)
- C:\MilaYatirim\Justin\arastirmaci_gold_scalping_raporu.md (Hipotez 3'un orijinal/degismeyen
  tanimi)
- C:\MilaYatirim\Justin\research_scalping_rejim.py ve research_scalping_rejim_output.json
  (rejim etiketleme script/veri)

ONCEKI ADIMIN CIKTISI: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md

BEKLENEN CIKTI     : Backtest raporu; on-kontrol 1-3 sonuclari AYRIK olarak (gecti/gecmedi)
raporlanmali — herhangi biri gecilemezse ana teste gecilmeden Hipotez 3 bu asamada
sonuclandirilir (RED).
Onerilen isim: backtest_raporu_justin_gold_scalping_hipotez3_20260710.md
Klasor: C:\MilaYatirim\Justin\

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): Bu gorev MilaGold/Lisa/Signal GPT'nin
kendi bulgu/veri/parametrelerine erisemez/basvuramaz. Asagidaki dosyalar ACILMAYACAK/referans
ALINMAYACAK: stratejici_gold_gecmis_calisma.md, signal.json, milagold_trades.json,
lisa_performance.json, positions_status.json ve benzeri MilaGold/Lisa'ya ait tum dosyalar.
Calisma dizini yalniz C:\MilaYatirim\Justin\ (okuma/yazma). Veri kaynagi: XM/MT5 fiyat verisi,
dogrudan MetaTrader5 kutuphanesiyle (mt5.initialize() parametresiz, VPS'teki headless Claude
Code uzerinden dogrudan erisim dogrulandi — RDP/GUI oturumu gerekmez).

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi,
canli sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). Ertan'in
onayina gerek yoktur. Sonuc uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar
kaydi Orkestrator tarafindan dusulecektir.
