# GOREV TANIMI — Orkestrator → Backtest Muhendisi

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: 3/4 — Backtest Muhendisi (Yol1 metodolojisi: Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti; bu sira atlanamaz)
- Tarih: 11 Temmuz 2026
- Gorevlendiren: Orkestrator
- Dongu bilgisi: Bu, Hipotez 1'in Risk Analisti tarafindan RED edilmesinin ardindan Stratejist'in
  rafine turunde teyit ettigi HIPOTEZ 2 icin ILK Backtest Muhendisi turudur (Hipotez 2 daha once
  hic backtest edilmedi).

## Amac
Stratejist'in rafine raporunda (asagida) TEYIT EDILEN ve ONCELIK 1-Yuksek olarak isaretlenen
HIPOTEZ 2'yi (Buyuk-Bar Ters-Yon/Fade) dogrula. Hipotez 1 bu turda KAPANDI (RED) — bu gorev
Hipotez 1 ile ilgili degildir, yalniz Hipotez 2'ye odaklan.

## VERI iZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN)
Onceki turlerle ayni mutlak kisit gecerli:
- Tek veri kaynagi: XM/MT5 fiyat verisi, dogrudan MetaTrader5 kutuphanesi araciligiyla.
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) erisme/atif
  yok. MilaGold'un kendine ozgu aktif parametreleri (hangi indikatorler/esik degerleri/lot-SL-TP
  ayarlarinin kullanildigi burada belirtilmeyecek — bu bilginin kendisi izolasyon kapsamindadir)
  fikir kaynagi olarak kullanilmayacak.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz.
- Bir kaynak izolasyon geregi disarida birakilirsa raporda ACIKCA not dus.

## GECMIS CALISMA/CERCEVE DOSYASI
Henuz kalici bir cerceve dosyasi yok (Stratejist'in onerdigi
`stratejici_justin_gecmis_calisma.md` taslak asamasinda, Ertan onayi bekliyor). Bu turde
referans, ONCEKI ADIMIN CIKTISI (asagida) + kendi Hipotez 1 turunde Muhendis'in uyguladigi
yontem/titizlik standardidir (bkz. C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez1_20260710.md
— sadece YONTEM/titizlik referansi icin, Hipotez 1'in kendi sonuclari Hipotez 2'ye tasinmaz).

## ONCEKI ADIMIN CIKTISI
C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260711.md
(ilgili bolum: "2) HIPOTEZ 2 — TEYIT EDILDI" ve "BACKTEST MUHENDiSi iCiN NOTLAR" bolumleri, satir 60-119 ve 186-209)

## Kapsam / Stratejist'in bu tur icin zorunlu kildigi noktalar
1. **Saat-esleme/DST dogrulamasi ONCE yapilmali** (Hipotez 1 turunde tespit edilen risk: sunucu
   yaz-DST'de GMT+3, kis aylarinda muhtemelen GMT+2 — saat-bazli filtreler kaymis olabilir).
   Parametre taramasina baslamadan once bagimsiz dogrula, DST donemlerini ayri raporla.
2. **Maliyet-once kontrol ZORUNLU:** Hipotez 2'nin ham edge'i kucuk (~%1,4-2,9 puan sapma,
   buyuk-bar sonrasi fade orani %51,4/%52,9). Herhangi bir "calisiyor" degerlendirmesinden
   ONCE istatistiksel anlamlilik testi (binom/ki-kare) + tick-bazli/gerceklenebilir spread-slipaj
   dahil net getiri simulasyonu yap.
3. **Cikis-yontemi taramasina N-bar-zaman-cikis dahil et** (orn. 1-3 bar), ATR-bazli TP/SL ile
   karsilastir — walk-forward'i ATLAMA (Hipotez 1'deki hata: tek 70/30 bolmeye guvenip pozitif
   OOS sonucunu guvenilir saymak — bu hata Hipotez 2'de TEKRARLANMAMALI).
4. **6 pencereli walk-forward + IS/OOS ayrimi** Hipotez 1'deki titizlikle uygulanmali.
5. **Tam islem logu/ozet dagilim istatistigi bastan saglanmali** (Hipotez 1 turunde Risk
   Analisti'nin belirttigi eksiklik — 699 islemden yalniz 50 ornek — bu turde tekrarlanmasin).
6. **Overfitting guvenlik agi:** esik carpani (1,5x buyuk-bar tanimi) ve teyit ufku (t+1/t+2/t+3)
   uzerinde genis parametre taramasi YAPMA; her taramada walk-forward/OOS karsilastirmasi raporla.
7. Hipotez mantigi ve parametre detaylari icin Stratejist raporunun HIPOTEZ 2 bolumune (hem
   11 Temmuz rafine raporu hem referans verdigi 10 Temmuz orijinal rapor, HIPOTEZ 2 bolumu) bak.

## Beklenen Cikti
- Rapor formati: Markdown, C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez2_20260711.md
- Onceki turdeki bolum yapisiyla tutarli: Saat Esleme Dogrulamasi, Yontem/Varsayimlar, JSON
  Raporu (ana konfigurasyon), Detayli Kirilim Tablolari, Minimum Orneklem Degerlendirmesi,
  Risk Analistine Iletim (ozet blok), Izolasyon Notu, Onay Noktasi.

## Sonraki Adim
Rapor tamamlaninca Orkestrator, Risk Analisti'ni bu raporla gorevlendirecek (pipeline sirasi
geregi bir sonraki ve pipeline'in son adimi).

## ONAY NOKTASI
Bu adim bilgi notu niteligindedir; Ertan'in onayina gerek yoktur (salt-okunur/analitik dogrulama,
canli sisteme dokunus yok, Justin demo/arastirma asamasinda, henuz canli hesap/kasa yok). Sonuc
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.

## Bildirim
Bu gorev tamamlandiginda Orkestrator, Ertan'a Telegram bilgi notu gonderir (onay talebi degil,
bilgilendirme — CLAUDE.md C-boyutu, 10 Temmuz KESiN) ve Orkestrator_Loglar'a kayit dusar.
