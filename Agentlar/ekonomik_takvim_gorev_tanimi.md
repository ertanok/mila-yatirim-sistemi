# EKONOMIK TAKViM AGENT'i — GOREV TANIMI

Gorev tanimidir, sistem promptu degil — kural-tabanli, Claude API'ye cagri yapmaz. Claude Code'a yapim talimati olarak verilir.

---

## 1. Amac ve Kapsam

FED aciklamasi, CPI/TDI verisi gibi bilinen-zamanli yuksek-etkili ekonomik olaylari izler, o saatler oncesi/sonrasi islem penceresini kapatir. Sabit kod degeri kullanilmaz — saatler gunden gune degistigi icin her seferinde yeniden cekilir.

**Tek bir projeye ozgu degil.** MilaGold, Justin, Ertan Stratejisi, Pariteler — tum scalping/daytrading projeleri icin paylasilan bir servis.

---

## 2. Veri Kaynagi (7 Temmuz arastirmasi sonucu)

MT5'in dahili takvimi var ama Python kutuphanesinden (`MetaTrader5` paketi) erisilemiyor — sadece MQL5'ten. Diger yeni agent planlari (Justin/FinRL, TradingView→MT5 migrasyonlari) da MQL5'e itmiyor bizi, dolayisiyla izole bir MQL5 bridge yazmak yerine:

**Karar: Harici kaynak, Selenium/scraping pattern — Signal GPT'de zaten kanitlanmis yaklasimla ayni.**

**Site: ForexFactory (8 Temmuz, KESiN).** Gerekce: acik-kaynak Python/Selenium scraper ekosistemi olgun, renk kodlamasi (kirmizi/turuncu/gri) ihtiyacimiza tam uygun, Investing.com'a kiyasla daha az bot-koruma zorlugu var.

---

## 3. Filtre Kriteri

- **Etki seviyesi (8 Temmuz, KESiN): sadece "yuksek etki" (ForexFactory'de kirmizi).** Orta/dusuk etki penceresi tetiklemez.
- **Para birimi/enstruman eslesmesi (parametrik olmali):** Gold icin USD haberleri onemli; ileride DAX icin EUR, forex ciftleri icin ilgili iki para birimi de eklenecek. Sabit degil, enstrumana gore config/mapping yapisinda tutulmali (Gozetleme'nin esik yapisiyla ayni mantik).

---

## 4. Haber Durusu (isim ve sure, 8 Temmuz KESiN)

Terim: **"haber durusu"** — Gozetleme'deki "piyasa anomalisi durusu" ile ayni kalip (tetikleyici + durus), karisikligi onlemek icin.

Sure: **Olay oncesi 30 dk + olay sonrasi 30 dk (toplam 60 dk pencere), 8 Temmuz KESiN.**

Not: Toplam sure, Gozetleme'nin "piyasa anomalisi durusu" ile ayni (60 dk) — tesaduf, iki mekanizma farkli tetikleyicilerle calisiyor (biri zamanlanmis olay, digeri reaktif fiyat hareketi), karistirilmamali.

---

## 5. Tetiklenince Ne Olur

- Paylasilan bir dosyaya yazilir — onerilen ad: `ekonomik_takvim_status.json`
- Icerik (taslak): `{"olay": "CPI (US)", "olay_zamani": "...", "pencere_baslangic": "...", "pencere_bitis": "..."}`
- **Tek yazici:** Ekonomik Takvim Agent'i
- **Okuyucular:** her projenin kendi MT5/sinyal agent'i — Gozetleme'nin piyasa anomalisi dosyasiyla ayni okuma pattern'i (sinyal islenmeden once kontrol)

---

## 6. Dosya-Tabanli Iletisim ve Heartbeat (Gozetleme ile ayni desen)

- Dosya sadece yaklasan/aktif bir olay varken guncellenir
- Heartbeat dosyasi da yazar (`ekonomik_takvim_status_heartbeat.json`) — Orkestrator bunu izler, bayatlarsa Seviye 1 bildirimi
- **Cekme sikligi (8 Temmuz, KESiN):** Haftalik bir toplu cekme (ForexFactory'nin haftalik gorunumunden) + gunluk kontrol (o hafta icindeki olaylarin guncel durumu). Siteyi az yormak ile guncel kalmak arasinda denge.

---

## 7. Bildirim

- Pencere acildiginda/kapandiginda Telegram bilgi notu (hangi olay, ne kadar surecek)
- Onay talebi degil — STOP-genis kategorisinde otomatik isler

---

## 8. Acik Sorular / TBD

- 10 Temmuz CPI icin bu agent zamaninda hazir olmazsa yedek plan gerekmiyor artik (demo hesap, aciliyet kalkti)

---

**Durum: Gorev tanimi tamamlandi (8 Temmuz).** Claude Code'a verilebilir.
