# MiLA YATIRIM SiSTEMi — CLAUDE CODE TALiMATLARI

## Genel
- Dil: Turkce (karaktersiz: u, o, i, s, c, g)
- Her karar mekanizmasi iceren kod: once Turkce acikla, onayla, sonra yaz
- Ertan vizyonu ve kararlari yonetir, Claude teknik implementasyonu yapar

## PROJE LiSTESi (7 Temmuz)
1) MilaGold Stratejisi
2) XM Copy Trading
3) Justin Stratejisi
4) Ters Muhendislik
5) Pariteler Stratejisi
6) Gold Daytrading
7) Agnostic B Stratejisi
8) Agnostic A Stratejisi

## Multi-Agent Mimarisi — Model Secimi
- Arayuz ve Orkestrator: Claude (kesin karar, degistirilemez)
- Varsayilan model: Sonnet 5
- Kritik inceleme/dogrulama noktalarinda Opus veya Fable'a yukseltme opsiyonu acik
- Bu karar yalnizca arayuz/orkestrator rolleri icin gecerli — Justin gibi ozel roller icin farkli AI aileleri (klasik ML, RL, baska LLM'ler) hala degerlendirmeye acik
- Orkestrator'un calisma bicimi (7 Temmuz, KESiN): Claude Code'dan ayri, kendi basina surekli/tetiklemeli calisan bir surec — Claude API'ye dogrudan cagri yapar, Orkestrator sistem promptuyla. Tum agent ekibini yönetir. Gercek VPS/kod islemi gerektiginde Claude Code'a gorev verir; Claude Code = implementasyon eli, tum projeler icin ortak kaynak, Orkestrator'in kapasitesine bagli degil.

## Multi-Agent Mimarisi — Mimari Boyutlar (A-F, 5 Temmuz)
Detay: Project Instructions, "MULTI-AGENT MiMARiSi — MiMARi BOYUTLAR" bolumu. Ozet:
- **A) Orkestrasyon:** Hiyerarsik-hibrit (runtime: supervisor, arastirma: pipeline)
- **B) Yetki:** STOP genis, START/CHANGE dar, en-kotu-boyut-kazanir kurali
- **C) Iletisim:** Dosya-tabanli (tek yazici + stale-safe), anomali-sonrasi-durus (15 dk baslangic, TBD), Ekonomik Takvim Agent'i (yeni, TBD)
  - **Agent gorevlendirme/sonuc bildirimi (10 Temmuz, KESiN):** Orkestrator bir agent'i gorevlendirdiginde ve o agent sonuc/rapor urettiginde Ertan'a Telegram bilgi notu gonderir + Orkestrator_Loglar'a kayit yazar. Onay talebi degil, sadece bilgilendirme (STOP-genis/bilgi-notu kategorisi).
  - **Agent'lar arasi sayisal tutarlilik (10 Temmuz, KESiN):** Bir agent'in urettigi sayisal bulgu (orn. ornek buyuklugu, oran, esik-gecen olay sayisi) bir sonraki agent tarafindan referans alinacaksa/karsilastirilacaksa, sadece kopyalanmaz — hangi hesaplama/tanimdan geldigi (orn. sabit/global ortalama vs hareketli/nedensel ortalama, farkli veri araligi) once teyit edilir. Farkli agent'larin ayni metrigi farkli (ama kendi icinde gecerli) yontemle hesaplamis olmasi mumkundur; bu fark fark edilmeden tasinirsa, bir hesaplamanin sonucu yanlislikla digerinin "bagimsiz dogrulamasi" olarak sunulabilir.
- **D) Onay Katmani
Izleme ve onay/karar ayri fonksiyonlar, ikisi de bir arayuz gerektirir. Kanal secimi (Telegram vs Dashboard) daha once ertelendi, Dashboard Layer 2 (onay mekanizmasi) ile ortusuyor.
- **E) Escalation:** 4 seviye — otomatik restart → Telegram → Claude Code uzaktan mudahale → bagimsiz uptime servisi + Contabo panel + onayli reboot
  - **Not (10 Temmuz, netlestirme — 3 ardisik RED esigi):** "3 ardisik RED" esigi tetiklenip Stratejist'e genis-capli yaklasim degisikligi onerisi sunulursa, bu oneri ve onu takip eden backtest/arastirma turlari hala arastirma/backtest asamasi sayilir — canli sisteme/hesaba hicbir etkisi olmadigi surece bilgi notu yeterlidir, onay gerekmez (B boyutundaki STOP-genis kategorisi). Onay sinirini degistiren sey yaklasimin genisligi degil, canliya/demo/gercek hesaba gecis adimidir — o adim her zaman ayrica ve acikca onay gerektirir.
  - **Gunluk Pipeline Dongu Siniri (10 Temmuz, KESiN):** Proje basina, gunluk (00:00'da sifirlanan) bir tam-tur sayaci tutulur (Stratejist cagrisi = 1 tur). Sayac 5'in altindaysa otomatik devam + Telegram bilgi notu (onay degil). Sayac 5'e ulasmis/gecmisse: sistem durur, Ertan'a Telegram'dan somut onay sorusu gider ("N tur denendi, hepsi RED, devam edeyim mi?") — otomatik devam etmez. Bu, Emniyet Stopu'ndaki STOP-otomatik/START-onayli kaliniyla ayni mantik, arastirma maliyetine uygulanmis hali.
- **F) Rollback:** Her deploy sonrasi Orkestrator belirli sureligine (TBD) sonuclari izler; anomali saptanirsa STOP otomatik, geri alma/devam onayli

## Dosya Yapisi
- Yerel: C:\MilaYatirim\ (ana klasor, dashboard, agent promptlari, deploy.py)
- VPS: C:\MilaYatirim\mila-yatirim-sistemi\MilaGold\ (production dosyalari)
- GitHub: ertanok/mila-yatirim-sistemi (public)

## VPS Baglantisi
- IP: 81.0.220.10
- Baglanti: deploy.py (paramiko SSH/SFTP)
- VPS saat dilimi: GMT+3

## Aktif Projeler

### PROJE 1: MiLAGOLD (Aktif — Demo Hesap)
- Sinyal kaynagi: signalgpt.ai (OCR ile Chrome remote debugging, port 9222)
- Gercek hesap: #302599619, "Mila", Standard, 1:500, 200 USD baslangic — HENUZ AKTIVE EDILMEDI
- Demo hesap: #1301560935 (aktif kullanimda)
- Ajanlar: milagold_ocr_agent.py, milagold_mt5_agent.py, milagold_sync_agent.py
- Aktif filtreler:
  - M5 EMA20 (SELL icin fiyat EMA20 altinda, BUY icin fiyat EMA20 ustunde olmali — 7 Temmuz'da BUY tarafina da simetrik olarak eklendi)
  - EMA100 streak>=13 (SELL icin fiyatin EMA100 altinda, BUY icin EMA100 ustunde kaldigi ardisik M5 mum sayisi — 7 Temmuz'da BUY tarafina da simetrik olarak eklendi)
  - Sinyal yas filtresi (OCR agent, SIGNAL_MAX_AGE_MINUTES=60) — 60 dakikadan eski sinyal islenmez
  - Piyasa saati filtresi — IKI AYRI mekanizma:
    (1) OCR tarafi: sinyal 23:30-01:05 arasi hic islenmez (MARKET_CLOSE_MINUTE=30, MARKET_OPEN_MINUTE=5)
    (2) MT5 tarafi/gap koruma: 23:45'ten sonra yeni islem alinmaz, 23:55'te acik pozisyon varsa kapatilir. Sebep: gapli acilista SL calismiyor (demoda yasandi, 5$ SL varken 11$ zarar olustu).
- Not: Signal GPT'nin karar mekanizmasi tam bilinmiyor. Gozlemlenen karar vericilerden biri M30 EMA100, digeri M5 EMA100 (3 Temmuz'da dogrulandi). Detay: Project Instructions, "Kaynak" bolumu.

### Sinyal Atlandi Bildirimi
- EMA20 veya Streak filtresi bir sinyali atladiginda Telegram bildirimi gider (birikme yok, anlik)
- Dort tetikleyici: yeni sinyal EMA20, yeni sinyal Streak, hafizadaki sinyal EMA20 retry, hafizadaki sinyal Streak retry
- Mesaj: [MilaGold] {Filtre} filtresi: sinyal atlandi / hafizadaki sinyal atlandi — {direction} @ {entry}
- Amac: islem alinmadiginda sebebini gormek + OCR/sistem sagligini dolayli teyit etmek

- Trailing stop aktif, TP3'te otomatik kapanma yok
- Lot: 0.01 | SL: 5$ | TP1: 3$ | TP2: 5$ | TP3: 8$
- Emniyet stopu: gunluk %20 dusus → islem durur, Telegram bildirimi. **Tekrar baslama Ertan'in onayini gerektirir, otomatik degil** (bkz. Mimari Boyutlar E).
- Lot artis kurali: her 200 USD kasa = 0.01 lot

### OCR Koordinatlari (1366x768)
- LIST_LEFT=50, LIST_TOP=360, LIST_RIGHT=580, LIST_BOTTOM=640
- Guncelleme (3 Temmuz): LIST_RIGHT 445→580 — RUNNING badge ve Entry degeri kesiliyordu, list_debug.png ile dogrulanip duzeltildi.

### OCR Self-Check Mekanizmasi
- Anomali kosulu: has_signal=True ama status/entry parse edilemedi, ham OCR metninde SELL/BUY/RUNNING/WAITING kelimelerinden biri var
- 12 dakika surekli anomali → Telegram uyarisi (tek seferlik)
- Acik pozisyon yoksa ve gunluk restart sayaci < 3 ise → otomatik OCR process restart (tek seferlik)
- Acik pozisyon varsa veya gunluk limit dolmussa → sadece Telegram uyarisi, restart yapilmaz
- 30 dakikada bir zaman damgali debug screenshot (list_debug_YYYYMMDD_HHMMSS.png)
- Acik pozisyon kaynagi: positions_status.json (MT5 agent her dongude yazar, OCR okur); dosya 30 sn'den eskiyse guvenli taraf: acik pozisyon var kabul edilir

### PROJE 2: JUSTiN (Gelistirme — Beklemede)
- MilaGold oturunca baslatilacak
- Ayri XM hesabi (hesap tipi belirlenmedi — MilaGold low-spread testi sonucuna bagli)
- 5 Temmuz Multi-Agent Mimarisi tartismasinda profil netlesti — sifirdan, dis kaynaksiz, farkli AI aileleri (klasik ML/derin ogrenme/RL) denenecek bir proje.

### Veri Izolasyonu (10 Temmuz, KESiN)
Justin'de calisan hicbir agent, Lisa/Signal GPT/MilaGold'un bulgu, veri, indikator veya performansina erisemez/basvuramaz. Tek kaynak: XM/MT5 fiyat verisi (dogrudan MetaTrader5 kutuphanesiyle). Yapisal izolasyon: Justin gorevleri calisma dizini olarak yalnizca Justin'e ait klasoru (C:\MilaYatirim\Justin\) kullanir — MilaGold dosyalarini (milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md vb.) fiziksel olarak icermez.

Not (10 Temmuz, netlestirme): Bu izolasyon MilaGold/Signal GPT'nin KENDI bulgu/veri/parametrelerine yoneliktir (dosyalari, ayarlanmis esik degerleri, Lisa'nin ozel mekanizmasi) — EMA, RSI, ATR gibi genel/evrensel teknik kavramlarin kullanimini yasaklamaz; Justin bunlari kendi bagimsiz analiziyle yeniden kesfedip kullanabilir. Bir agent'a "X'i kullanma" talimati verilirken X'in Signal GPT/MilaGold'a ait oldugu veya nasil calistigi aciklanmaz/isimlendirilmez (izolasyonu uygularken bilgi sizdirmamak icin) — sadece "tamamen bagimsiz/orijinal analiz yap" denir.

Ek netlestirme (14 Temmuz): Izolasyon kurali sadece sayisal icerige degil, format/cumle-kalibi kopyalamaya da uygulanir — bir dosyayi "yapi/sablon referansi" icin acmak da izolasyon kapsamindadir, sadece parametre/veri kopyalamak degil. Orkestrator kendi sablonunu MilaGold dosyasina bakmadan bagimsiz turetmelidir.

### PROJE 3: COPY TRADiNG (Hazir — Beklemede)
- XM Strategy Manager, "Mila Gold" hesabi
- Min yatirim: ~200 USD, Ucret: ~%20
- Arkadaslara odenen ucret manuel iade edilecek
- **KESIN — SONRADAN DEGISTIRILEMEZ:** Minimum yatirim ve ucret orani baslangicta dogru belirlenmeli. XM kurallari geregi sonradan yalnizca AZALTILABILIR, artirilamaz.

### PROJE 4: ERTAN STRATEJiSi (Baslangic)
- BB(20,2) + SMA tabanli, XAUUSD M15
- MT5 uyarlama ve backtest yapilacak
- 5 Temmuz notu: sabit mesafe yerine trend kanali + S/R'a revize edilebilir (detay: PI)

### PROJE 5: LiSA TERS MUHENDiSLiK (Ayri Proje, 5 Temmuz)
- Amac: Signal GPT'nin karar mekanizmasini cozmek, bagimsizlasmak
- Iki alt-problem: yon-tayini (kural tabanli, Yol1 metodu) + entry-noktasi (belirsiz, Yol2/ML-RL denenecek)
- Detay: Project Instructions, "PROJE 6: LiSA TERS MUHENDiSLiK"

## Dashboard
- Dosya: C:\MilaYatirim\Mila_dashboard.html (yerel tarayici)
- Veri akisi: milagold_sync_agent.py (VPS, her 2 dk) → GitHub API → Dashboard (60 sn yenileme)
- Senkronize: signal.json, milagold_trades.json, log dosyalari, agent_status.json
- Yerel VPS dosyalari (git'e gitmez): positions_status.json (MT5→OCR acik pozisyon koprüsü), ocr_restart_flag.txt (OCR otomatik restart sayaci)

## Teknik Altyapi
- Python 3.14 (py komutu)
- MT5: XMGlobal-MT5 6, mt5.initialize() parametresiz
- Broker: XM, Sembol: GOLD, Filling: ORDER_FILLING_RETURN
- Credentials: config.py (git disinda)
- Deploy: deploy.py (paramiko SSH/SFTP + git push)

## Onemli Kurallar
- config.py, json, log, png dosyalari git'e eklenmez
- data/ klasoru sync agent tarafindan GitHub API ile yonetilir
- Tum agentlar (MT5, OCR, Chrome) Startup klasorunde kisayol olarak kayitli, reboot sonrasi otomatik baslar
- tp parametresi order request'ten tamamen cikarilmali (XM tp:0 reddediyor)
- VPS dosya yolu: C:\MilaYatirim\mila-yatirim-sistemi\MilaGold\ (GitHub repo alt klasoru)
- MT5 agent her zaman RDP oturumundan baslatilmali (Windows Session 0 izolasyonu — Task Scheduler/SYSTEM hesabindan baslatilirsa calismaz)
- Gapli acilista SL calismiyor — gap koruma (23:45/23:55) SL'e ek bir mekanizma, SL'in yerini almaz
- **STOP otomatik olabilir, START/CHANGE (yeniden baslatma, reboot, rollback-sonrasi-devam) her zaman Ertan'in onayini gerektirir** (bkz. Mimari Boyutlar B/E/F)

## Agent Sistemi
**Model/kutuphane secim ilkesi:** Birincil kriter kalite/performans; maliyet ancak esit performans durumunda ikincil tercih sebebidir. Hicbir agent sirf ucuz/ucretsiz oldugu icin secilmez, sirf pahali oldugu icin elenmez. Detay: Project Instructions, "AGENT SiSTEMi" bolumu; guncel agent/model listesi icin bkz. agent_teknoloji_tablosu.md.
- Multi-agent sistem aktif — agent implementasyonlari Claude Code ile yazilir/deploy edilir; Orkestrator kendi bagimsiz surecinde calisir
- Orkestrator — agent koordinasyonu, STOP/START/CHANGE yetkisi, tum ekibi yönetir. Ayri surec (Claude API, Sonnet 5), Claude Code'dan bagimsiz calisir.
- Arastirmaci, Stratejist, Backtest Muhendisi, Risk Analisti
- Gozetleme — canli sistem sagligi, anomali-sonrasi-durus (yeni gorev, 5 Temmuz)
- Ekonomik Takvim Agent'i — FED/TDI gibi bilinen-zamanli olaylari harici kaynaktan ceker, islem penceresini kapatir (yeni, TBD, 5 Temmuz)
- Detay Karti Okuyucu — Lisa ters muhendisligi icin sinyal detay kartini Claude vision (Anthropic API) ile okur, EasyOCR degil (ifade/yorum icerdigi icin sayisal OCR yetersiz). Saatlik + fiyat-esigi tetikleyicileriyle calisir; OCR agent'tan tamamen bagimsiz ayri bir surec/sekme (ayni Chrome, debug port 9222, CDP tiklama) — mevcut liste-OCR'in okumasini kesmez (9 Temmuz testinde dogrulandi). Ileriki asama, henuz uygulanmadi. Detay: Project Instructions, "GELECEK GELiSTiRMELER" bolumu.
- Her agent kendi konusmasinda yasar, rol degisimi yapilmaz
- Sistem promptlari: C:\MilaYatirim\*_system_prompt.md