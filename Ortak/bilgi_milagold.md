# MilaGold Projesi — Detay (Project Knowledge)

## Kaynak
- Site: signalgpt.ai (Elite uyelik aktif, unlimited sinyal — 15 Temmuz'da teyit edildi)
- Sinyal: Signal GPT sitesi OCR ile izleniyor
- Yon: Trend following scalping, tam karar mekanizmasi bilinmiyor. Kesin gozlem: EMA100, M1/M5/M15/M30 zaman dilimlerinin hepsinde gorulmus — sabit tek bir zaman dilimi kullanilmiyor, ayni kartta birden fazla zaman dilimi bir arada olabilir (orn. Structure&Trend icin M15 EMA100, Momentum icin M30 MACD birlikte gorulen bir ornek var). Hangi zaman diliminin ne zaman/nicin secildigi (karar mantigi) hala bilinmiyor — bu, Ters Muhendislik'in yon-tayini alt-probleminin konusu.
- Fiyat saglayici: Signal GPT, TradingView'in TVC fiyat saglayicisini kullaniyor (CFDs on Gold). MT5 (XM) ile TVC arasindaki fark ihmal edilebilir (PRICE_OFFSET = 0.0, olculdu ve dogrulandi).

## Sinyal Yapisi
- Entry, yon, emir tipi: OCR ile okunuyor
- TP1: 3$, TP2: 5$, TP3: 8$ (Lisa'nin sinyalinde gelen sabit mesafeler)
- SL: 5$
- Kademeli SL yonetimi: TP1 gecilince SL entry+2$'a cekilir (kismi risk azaltma); TP2 gecilince SL girise (breakeven) cekilir ve iz suren stop bu noktada baslar; TP3'te artik broker-side otomatik kapanis yok (tp parametresi kaldirildi), ama TP3 seviyesi hala sonuc etiketlemesi icin kontrol edilir — trailing TP3'u de gecip devam edebilir
- Tek seferde bir islem; SL breakeven'e cekildikten (TP2 sonrasi, sl_level>=1) sonra yeni/daha-kotu-entry'li bir sinyal gelirse 2. pozisyon acilabilir (max 2 eszamanli islem). SL hala orijinal risk seviyesindeyse (sl_level=0), yeni sinyal sadece hafizaya alinir, ikinci pozisyon acilmaz

## Lisa'nin Algoritmasi (dogrulanmis)
- TP3'e ulasinca pozisyonu kapatir
- TP1/TP2 sadece "ulasti" etiketi, orada kapatmaz
- TP3'e ulasamazsa maliyete yakin kapatip TP1/TP2 olarak kaydeder (performans manipulasyonu suphesi)
- Exit muhtemelen sure bazli; Lisa exit yapinca biz de kapatiriz
- Lisa'nin gecmis performansi guvenilir referans degil — kendi milagold_trades.json esas veri kaynagi

## Aktif Filtreler
- **M5 EMA20:** SELL icin fiyat EMA20 altinda, BUY icin ustunde olmali. Aksi halde atlanir (retry dahil). Her iki taraf da kodlu ve dogrulandi (14 Temmuz).
- **EMA100 streak:** Son EMA100 kesisiminden bu yana gecen M5 mum sayisi >= 13. Anlik hesaplanir, state tutulmaz (restart guvenli). Her iki taraf kodlu (kesisim sayaci yon-bagimsiz). Backtest: KF 0.920 → 1.564, 135→48 islem.
- **Sinyal yasi:** SIGNAL_MAX_AGE_MINUTES=60
- **Piyasa saati (iki mekanizma):** OCR: 23:30-01:05 arasi hic islenmez. MT5/gap koruma: 23:45'ten sonra yeni islem yok, 23:55'te acik pozisyon kapatilir (gapte SL calismiyor, demoda 5$ SL varken 11$ zararla kapanma yasandi).
- **Kademeli SL/trailing:** TP1 gecilince SL entry+2$'a cekilir; TP2 gecilince SL girise (breakeven) cekilir, iz suren stop burada baslar. TP3'te broker-side otomatik kapanis yok (tp parametresi order request'ten kaldirildi, XM tp:0 reddediyor) — TP3 sadece sonuc etiketi icin kontrol edilir, trailing bu seviyeyi de gecebilir.
- **Sinyal atlandi bildirimi:** EMA20/Streak atlarsa Telegram'a anlik bildirim (4 tetikleyici: yeni/hafizadaki sinyal x EMA20/Streak).

## Gercek Hesap
- Hesap no: #302599619, "Mila", baslangic 203.97 USD, kaldirac 1:500, Standard
- Demo: Login 1301560935 (test icin aktif)
- Gercek hesaba gecis kriteri: 80 USD/gun esigi kaldirildi (7 Temmuz, piyasa range + nakit akisi aciliyeti). Yeni kriter: BUY EMA20+streak filtresi (tamamlandi, 14 Temmuz) → en az bir canli BUY sinyali gozlenir → sonuc makulse gecis
- Baslangic kasasi 200 USD, 0.01 lot; her 200 USD = +0.01 lot; ust sinir 1500-2000 USD
- Lot buyutme: 200→0.01, 400→0.02, 600→0.03, 1000→0.05

## VPS Altyapisi
- Contabo Cloud VPS 20 NVMe, Windows Server, Portsmouth UK, GMT+3
- Ekran cozunurlugu 1366x768 (OCR koordinatlari buna kalibre) — RDP oturumlarinda gercek cozunurluk kayabiliyor, izlenmeli
- Otomatik baslama: Task Scheduler (LogonTrigger, 8 gorev) — Startup klasoru degil
- RDP zaman asimi kapali, Guc plani High Performance

## OCR Self-Check
- Parser okuyamiyor ama ham metinde SELL/BUY/RUNNING/WAITING varsa "anomali"
- 12 dk surerse Telegram uyarisi; acik pozisyon yoksa ve gunluk restart sayaci <3 ise otomatik restart
- positions_status.json 30 sn'den eskiyse guvenli taraf: acik pozisyon var kabul edilir
- Gunluk restart sayaci 00:00'da sifirlanir

## Chrome/OCR Kararlilik Sorunu — Cozuldu (15 Temmuz)
- Kronik "invalid session id" hatasi (29 Haziran'dan beri, 2893 tekrar). K1 (gercek cokme) RDP/mudahale ile korele — kesin tetikleme mekanizmasi (connect/disconnect) tam kanitlanmadi ama kontrol altina alindi.
- Yetim chromedriver process birikimi bulundu ve temizlendi.
- Audit logging acildi (4778/4779), log boyutu artirildi — gelecek teshis icin.
- 14+ saatlik "sinyal islenmiyor" korkusu, dashboard'daki pause dugmesinin unutulmus olmasindan kaynaklaniyormus — kod saglam.
- Bu Chrome ornegi Ters Muhendislik ile paylasilir (CDP port 9222, Model B); kok neden burada cozulunce TM de faydalanir.

## Sinyal Numarasi
- Signal GPT artik numara gostermiyor. Karsilastirma anahtari: HH:MM + entry fiyati.

## Performans Takibi
- milagold_trades.json (bizim islemlerimiz), lisa_performance.json (Lisa'nin sonuclari)
- Sonuc turleri — **bizim islemlerimiz icin** (determine_result fonksiyonu, kod dogrulandi): TP3 (kapanis fiyati TP3 seviyesini gecmis), Entry (breakeven'de kapanmis), Exit (zorla/gap kapatma), SL (SL hala orijinal seviyedeyken vurulmus). TP1/TP2 nihai sonuc olarak donmez, sadece ara SL-tasima tetikleyicisi. **Lisa icin** ayri siniflandirma: TP1/TP2/TP3/SL (Lisa'nin kendi etiketleri)
- Metrikler: toplam pip, islem sayisi, win rate, ort. kar/zarar, kar faktoru, Lisa karsilastirmasi

## Emniyet Stopu
- Gunluk baslangic bakiyesine gore %20 dusus → islem alma durur, Telegram bildirimi (MilaGoldBot), 00:00 sifirlama
- Tekrar baslama Ertan onayi gerektirir (otomatik devam etmez)
- Dashboard'daki manuel pause/aktiflestir butonu ayri bir kontrol, sessizce acik kalabiliyor — dikkatli kullanilmali (bkz. Dashboard gelistirme listesi: surekli gorunur "pause aktif" uyarisi eklenecek)

## Key Learnings
- Entry bazli momentum filtreleri pending order mimarisiyle calismiyor (async doluyor)
- Signal GPT'nin EMA100'u guclu trendlerde lag yapiyor — M5 EMA20 bunu hafifletir
- Windows Session 0 izolasyonu: MT5 agent RDP oturumundan baslatilmali
- order_send None: sinyali temizleme, retry icin koru; tp keyini tamamen kaldir
- SELL_LIMIT/STOP siniflandirmasi emir gonderim anindaki fiyata gore, sinyal zamanina gore degil
- Gapli acilista SL, gap sonrasi ilk fiyattan tetiklenir — gap koruma SL'in yerini almaz, ek mekanizmadir
- MT5 agent restart guvenilir: orphan pozisyonlari dogru devralir, trailing stop devam eder
- Gecikmis sinyal isleme riski: SELL_LIMIT/BUY_LIMIT dezavantajli fiyattan kurulabilir (yas filtresi zaman bazinda yakalar, fiyat sapmasi bazinda yakalamaz — dusuk oncelikli gelistirme fikri)
- Teshis scriptlerinde driver.quit() kullanilmali, driver.close() degil (chromedriver process/port temizligi icin)

## Gelecek Gelistirmeler
- Iz suren stop — trend gucu indikatoru ile (EMA/ATR/RSI) dinamik mesafe ayarlama, Lisa'yi yakalayinca devreye alinacak
- Fiyat-sapmasi filtresi (dusuk oncelik): sinyal fiyati ile gerceklesen fiyat farki esigi asarsa sinyali atla
- 8 Temmuz kacirilan kar firsati degerlendirmesi (dusuk oncelik): streak esiginin (13 mum) hizli/keskin hareketlerde cok kati olup olmadigi

## Teknik Dosya Yapisi
- C:\MilaYatirim\MilaGold\ : milagold_ocr_agent.py, milagold_mt5_agent.py, milagold_sync_agent.py, lisa_history_reader.py, config.py (git disi), signal.json, milagold_trades.json, lisa_performance.json, loglar, positions_status.json, ocr_restart_flag.txt, milagold_control.json
- GitHub: ertanok/mila-yatirim-sistemi (public) — sadece .py + .gitignore commit edilir, config/json/log/png haric
