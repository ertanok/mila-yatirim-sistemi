# GOREV TANIMI — Orkestrator → Risk Analisti

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: 4/4 (son adim) — Risk Analisti (Yol1 metodolojisi: Arastirmaci → Stratejist →
  Backtest Muhendisi → Risk Analisti; bu sira atlanamaz)
- Tarih: 11 Temmuz 2026 (VPS-yerel)
- Gorevlendiren: Orkestrator
- Dongu bilgisi: Bu, HIPOTEZ 2 (Buyuk-Bar Ters-Yon/Fade) icin ILK Risk Analisti turudur.
  Hipotez 1 (Seans-Filtreli Asimetrik Mean-Reversion) daha once bu ekip tarafindan RED edilmis
  (bkz. risk_analisti_raporu_justin_gold_scalping_hipotez1_20260710.md) — bu gorev Hipotez 1 ile
  ilgili degildir, yalniz Hipotez 2'nin yeni backtest sonucunu degerlendir.

## Amac
Backtest Muhendisi'nin HIPOTEZ 2 dogrulama raporunu degerlendir, ONAYLI/KOSULLU/RED karari ver.
Kendi sistem promptundaki 8 kontrolu (istatistiksel anlamlilik, IS/OOS bozulma, Monte Carlo,
pes-pese kayip, kar konsantrasyonu, kirilim analizi, parametre hassasiyeti, gercek-hayat
duzeltmesi) sirasiyla uygula ve raporunu kendi "Rapor Formati" sablonuna gore uret.

DIKKAT (Orkestrator'un on-gozlemi, senin bagimsiz kararini yonlendirmesin diye ayrica
belirtiliyor — kendi 8 kontrolunu yine de tam ve bagimsiz uygula):
- Ana konfigurasyon PF=0,558 (tum-donem), IS PF=0,517, OOS PF=0,623 — hepsi 1'in altinda.
- TUM kirilim taramalarinda (teyit-ufku t+1/t+2/t+3, cikis-yontemi zaman-N1/N2/N3/ATR-only/
  combined, seans-filtresi filtresiz/15-18) tum-donem PF 1'in altinda kalmis; en iyisi bile
  (yalniz-zaman-N3) PF=0,912.
- 6 walk-forward penceresinin 6'si da PF<1 (araligi 0,401-0,782) — tutarli negatif, tek donem
  carpitmasi yok.
- ONCE-KONTROL/istatistiksel anlamlilik: fiilen islem edilen alt-orneklemde (M5, seans 15-18)
  ters-yon orani %48,86, binom p=0,2234 — 0,50'den ANLAMLI SEKILDE SAPMIYOR. Global M5 (%50,94,
  p=0,0288) ve M1'de (%53,15, p<0,001) anlamli sapma var ama bu, fiilen islem edilen dar seans
  penceresinde kayboluyor.
- Bu turde ayrica bir KOD HATASI duzeltmesi var: tick-bazli slipaj hesaplamasi "soguk baslangic"
  durumunda yanlis-donemli tick donduruyordu (fiziksel olarak imkansiz slipaj/ATR orani ~6x).
  Duzeltme sonrasi PF DAHA DA KOTULESTI (0,867→0,558) — yani onceki hatali sayi hipotezi
  oldugundan iyi gosteriyordu. Muhendis'in raporu (bolum 2) bu duzeltmeyi ayrintili belgeliyor.
- Muhendis, MAX_TICK_MISMATCH_SEC=60 parametresini bu turde kendisi ekledi (Stratejist tarafindan
  belirlenmedi) — kendi raporunda bunu ayrica onaylanmasi gereken bir muhendislik karari olarak
  isaretledi. Etkisi kucuk gorunuyor (12.210 tick sorgusundan yalniz 2'si reddedildi, ~%0,016) ama
  degerlendirmene dahil et / gerekirse Stratejist'e iletilmek uzere not dus.
- Bu on-gozlem senin icin bir sonuc degil, sadece dikkat cekmek icindir; kendi bagimsiz 8
  kontrolunu tam uygula.

## VERI IZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN)
- Tek veri kaynagi: XM/MT5 fiyat verisi (Backtest Muhendisi zaten dogrudan MT5'ten cekti).
- MilaGold/Lisa/Signal GPT'ye ait hicbir dosyaya (signal.json, milagold_trades.json,
  lisa_performance.json, positions_status.json, stratejici_gold_gecmis_calisma.md vb.) erisme/
  atif yok.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz.

## GECMIS CALISMA/CERCEVE DOSYASI
Yok — Justin icin proje-ozel bir "gecmis calisma" dosyasi (Gold'daki
stratejici_gold_gecmis_calisma.md benzeri) henuz olusturulmadi; dolayisiyla proje-ozel
HEDEF_PF/HEDEF_WR/HEDEF_DD veya risk parametreleri (kasa buyuklugu, islem basina risk) onceden
tanimlanmamis. Justin'in canli hesabi da henuz yok (CLAUDE.md, PROJE 2 durumu "Gelistirme —
Beklemede"). Hipotez 1 turunde oldugu gibi: KESIN olarak proje-ozel bir hedef/kasa buyuklugu
gerekiyorsa bunu acikca "eksik/istenen bilgi" olarak raporunda belirt (Orkestrator'a/Ertan'a
iletilecek); ancak kendi promptundaki genel/varsayilan kirmizi-bayrak esiklerini ve oransal
(yuzde-bazli) analizi kullanarak degerlendirmeye devam edebilirsin — dolar-bazli KONTROL 4/8
hesaplarini yalniz ORANSAL olarak raporla, varsayilan bir dolar rakami uydurma.

## ONCEKI ADIMIN CIKTISI
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez2_20260711.md
(JSON rapor + Risk Analistine Iletim ozeti, bolum 3 ve 6)
Ham detay: C:\MilaYatirim\Justin\backtest_hipotez2_output.json

## BEKLENEN CIKTI
C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_hipotez2_20260711.md
- Kendi sistem promptundaki "Rapor Formati" sablonuna gore tam rapor (KARAR: ONAYLI/KOSULLU/RED
  + 8 kontrol + Stratejiste geri bildirim + kullaniciya ozet).

## ONAY NOKTASI
Bilgi notu — Ertan'in onayina gerek yok. Bu adim salt-okunur/analitik bir degerlendirmedir
(gecmis backtest ciktisi uzerinde), canli sisteme (MilaGold/uretim veya Justin canli hesabi —
zaten yok) hicbir dokunusu yoktur, Justin demo/arastirma asamasindadir. START/CHANGE kapsamina
girmez (Mimari Boyutlar B/E). Sonuc uretildiginde Ertan'a Telegram bilgi notu gonderilecek +
Orkestrator_Loglar'a kayit dusulecek (CLAUDE.md C-boyutu, "Agent gorevlendirme/sonuc bildirimi",
10 Temmuz KESiN). NOT: Risk Analisti RED kararina varirsa, bu da salt bir bilgi/analiz sonucudur
(pipeline'in dogal ciktisi) — START/CHANGE sayilmaz; olasi bir "Stratejist'e yeni hipotez uret"
adimi ayri bir cagriyla degerlendirilecek.
