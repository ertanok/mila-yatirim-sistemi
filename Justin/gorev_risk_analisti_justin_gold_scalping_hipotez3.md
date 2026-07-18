# GOREV TANIMI — Orkestrator → Risk Analisti

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: 4/4 (son adim) — Risk Analisti (Yol1 metodolojisi: Arastirmaci → Stratejist →
  Backtest Muhendisi → Risk Analisti; bu sira atlanamaz)
- Tarih: 11 Temmuz 2026 (VPS-yerel)
- Gorevlendiren: Orkestrator
- Dongu bilgisi: Bu, HIPOTEZ 3 (Rejimden-Bagimsiz Uniform Zayif Devam/Donus Sinyali) icin ILK
  Risk Analisti turudur. Hipotez 1 ve Hipotez 2 daha once bu ekip tarafindan RED edilmis
  (bkz. risk_analisti_raporu_justin_gold_scalping_hipotez1_20260710.md ve
  risk_analisti_raporu_justin_gold_scalping_hipotez2_20260711.md) — bu gorev onlarla ilgili
  degildir, yalniz Hipotez 3'un yeni backtest sonucunu degerlendir. Backtest Muhendisi'nin bu
  adimi (ana test) 3 cagriyla tamamlandi (1. kredi-kesintisi, 2. sebep-belirsiz hata, 3. basarili
  — bkz. rapor Bolum 0); bu dongu notu sadece surec-izlenebilirligi icindir, sonucun gecerliligini
  etkilemez (script'in kendisi sozdizimsel/mantiksal olarak degismedi, sadece bir verimlilik
  duzeltmesi yapildi).

## Amac
Backtest Muhendisi'nin HIPOTEZ 3 (Ana Test) dogrulama raporunu degerlendir, ONAYLI/KOSULLU/RED
karari ver. Kendi sistem promptundaki 8 kontrolu (istatistiksel anlamlilik, IS/OOS bozulma,
Monte Carlo, pes-pese kayip, kar konsantrasyonu, kirilim analizi, parametre hassasiyeti,
gercek-hayat duzeltmesi) sirasiyla uygula ve raporunu kendi "Rapor Formati" sablonuna gore uret.

DIKKAT (Orkestrator'un on-gozlemi, senin bagimsiz kararini yonlendirmesin diye ayrica
belirtiliyor — kendi 8 kontrolunu yine de tam ve bagimsiz uygula):
- 6 sinyal-ailesi/varyanti test edildi: GENEL-FADE, STREAK-FADE (L2-L5), BIGBAR-FADE.
  TUMUNDE tum-donem PF 1'in altinda (araligi 0,448-0,548).
- IS/OOS: 6 senaryonun TAMAMINDA hem IS hem OOS PF<1 (IS araligi 0,455-0,580, OOS araligi
  0,333-0,517). IS zaten <1 oldugu icin OOS'taki hafif kotulesme klasik "karli-gorunup-cakma"
  overfitting deseni degil, mevcut olumsuz sonucun pekismesi.
- Walk-Forward: 6 senaryo x 6 pencere = 36 kesitin TAMAMINDA PF<1 (araligi 0,303-0,627), en iyi
  tekil pencere dahi 1'in altinda — tek-donem sansi/carpitmasi yok.
- Rejim-post-hoc (VOL genis/dar, TREND trend/range, ayni islem seti uzerinde ikincil filtre):
  6 senaryo x 4 rejim = 24 hucrenin TAMAMINDA PF<1 (araligi 0,377-0,652) — hicbir rejim
  segmentinde gizli bir edge yok.
- TOPLAM: 60'tan fazla ayri kesitin (tum-donem+IS+OOS+6-WF+4-rejim, 6 senaryo icin) HICBIRINDE
  PF>=1 gozlemlenmedi — bu, Hipotez 1/2'den bile daha genis kapsamli ve tutarli bir olumsuz sonuc.
- Dikkat noktasi (Muhendis'in kendisi de isaretledi): M1 zaman diliminde ortalama toplam maliyet
  ATR'nin ~%15-19'u / ATR-bazli SL mesafesinin ~%28-34'u — Muhendis "fiziksel olarak imkansiz
  DEGIL" diye dogruladi (slipaj her zaman spread'in altinda, tick-zaman-uyusmazligi reddi=0) ama
  M1 scalping'in yapisal olarak yuksek goreceli maliyet-yuku tasidigini not dustu; degerlendirmene
  dahil et.
- STREAK-FADE L4'te IS-OOS sapmasi (0,501→0,333, fark 0,168) digerlerine gore goreceli genis;
  n=305 (OOS) tek basina karar dayanagi degil, Muhendis de boyle degerlendirdi.
- SL/TP semasi (ATR14x0,5, RR=1:1) Stratejist'in Hipotez-3-ozel bir deger belirtmemesi nedeniyle
  H1/H2'den TASINDI — Muhendis bunu ayrica onaylanmasi gereken bir muhendislik karari olarak
  isaretledi (Stratejist onayi bekliyor). Degerlendirmene dahil et / gerekirse Stratejist'e
  iletilmek uzere not dus.
- Saat esleme/DST bulgusu (kis aylarinda SESSION_PRIMARY=15-18 fiilen 1 saat kaymis olabilir)
  bu ana testte de gecerli — 4. kez bagimsiz dogrulandi, RED/PASS esigi degil prosedurel not.
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
Beklemede"). Hipotez 1/2 turlerinde oldugu gibi: KESIN olarak proje-ozel bir hedef/kasa buyuklugu
gerekiyorsa bunu acikca "eksik/istenen bilgi" olarak raporunda belirt (Orkestrator'a/Ertan'a
iletilecek); ancak kendi promptundaki genel/varsayilan kirmizi-bayrak esiklerini ve oransal
(yuzde-bazli) analizi kullanarak degerlendirmeye devam edebilirsin — dolar-bazli KONTROL 4/8
hesaplarini yalniz ORANSAL olarak raporla, varsayilan bir dolar rakami uydurma.

## ONCEKI ADIMIN CIKTISI
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_hipotez3_20260711.md
(JSON rapor + Risk Analistine Iletim ozeti, bolum 4 ve 8)
Ham detay: C:\MilaYatirim\Justin\backtest_hipotez3_output.json
Stratejist'in Hipotez 3 tanimi: C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_20260713.md
(Bolum 5)

## BEKLENEN CIKTI
C:\MilaYatirim\Justin\risk_analisti_raporu_justin_gold_scalping_hipotez3_20260711.md
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
