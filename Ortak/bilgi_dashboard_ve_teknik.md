# Dashboard ve Teknik Altyapi — Detay (Project Knowledge)

## Mila Dashboard

**Amac:** Tum sistemin (tum projeler, tum agentlar) tek noktadan izlenmesi ve yonetilmesi. Yeni projeler eklendikce genisler.

**Mimari (16 Temmuz'da guncellendi):** Dashboard artik GitHub Pages'te (`https://ertanok.github.io/mila-yatirim-sistemi/`), herkese acik bir URL — eskiden `file://` ile sadece yerelde aciliyordu.

**Veri okuma (goruntuleme):** Tum kart verileri (agent_status.json, signal.json, milagold_trades.json, milagold_control.json, detay_karti_durum.json, log tail'leri) `raw.githubusercontent.com`'dan okunuyor. Akis degismedi: milagold_sync_agent.py (VPS) → GitHub API push → raw.githubusercontent.com → Dashboard. **Yenileme araligi: 60 saniye** (`REFRESH_MS = 60000`, `setInterval(loadAll, REFRESH_MS)`), `rawUrl()` fonksiyonu cache-bypass icin timestamp ekliyor. Repo public (raw.githubusercontent.com private repoda calismiyor).

**Yazma/kimlik dogrulama (ayri kanal):** `milaboard_api.py` (VPS'te, Cloudflare Tunnel + domain uzerinden: `dashboard.milaertanok.com` / `login.milaertanok.com`) — SADECE giris (sifre/Passkey), MilaGold pause/resume POST'u, manuel emir gonderimi icin kullanilir. Dashboard'un gosterdigi hicbir kart verisi bu API'den gelmiyor — okuma ve yazma tamamen ayri iki kanal.

**Guvenlik katmani — Passkey/WebAuthn (16 Temmuz, TAMAMLANDI, canlida):**
- Sebep: GitHub Pages'e tasinirken goruntulemenin (P&L, sinyal, log) giris gerektirmedigi, sadece pause/resume ve manuel emrin gerektirdigi fark edildi — bu acik kapatilip tam kilit eklendi (header/icerik girise kadar gizli).
- Planlanan Telegram onay-kodu katmani iptal edildi, yerine Passkey getirildi.
- `mila_auth.py` + `milaboard_api.py`: py_webauthn ile register/login/reauth endpoint'leri. Credential'lar `webauthn_credentials.json`'da (git disi).
- Laptop (Windows Hello PIN) ve telefon (yuz tanima) ayri kayitli, cihaz-bazli (TPM'e bagli).
- Manuel emir gonderiminde oturum token'ina guvenilmez — her seferinde taze Passkey dogrulamasi sart.
- Mimari ayrimi: `milaboard_api.py` merkezi auth sahibi, `milagold_api.py` sadece `/verify`'a soran "aptal" servis — ileride yazilacak her proje-ozel API (Breakout Order dahil) ayni merkezi servise soracak.

**Manuel emir girisi (MilaGold'a eklendi, 16 Temmuz):** Dashboard'dan yon+fiyat girilip Passkey ile onaylanir. `manuel_signal.json` (ayri dosya, signal.json ile ayni sema, tek yazicisi milaboard_api.py). milagold_mt5_agent.py bunu OCR sinyaliyle ayni fonksiyondan isler (SL hesaplama, trailing, emir tipi) — sadece EMA20/Streak filtreleri atlanir. Gap koruma, pause kontrolu, %20 drawdown stopu manuel emirler icin de aynen gecerli. Bekleyen manuel emir varken gelen OCR sinyali onu iptal etmez, OCR sinyali atlanir ("manuel emir aktif" sebebiyle loglanir).

**Senkronize dosyalar:** signal.json, milagold_trades.json, milagold_log_tail.txt, milagold_ocr_log_tail.txt, agent_status.json, milagold_control.json (pause/aktif — dogrulandi, gercekten calisiyor).

**Yeniden tasarim (14 Temmuz'dan itibaren, aktif oturum):**
- Once "dashboard dogru arayuz mu" sorusu tartisildi (bildirim/konusma/rapor/log alternatifleriyle karsilastirilarak) — dashboard dogru secim olarak dogrulandi.
- Icerik turu (operasyonel/analitik/kontrol) ve kapsam (portfoy-seviyesi vs proje-detay + drill-down) — sistemin ucune de ihtiyaci var, 9 proje tek ekranda gorunmeli.
- **Copy Trading, ayri proje degil, cok-yonlu bir gelir katmani** — hangi proje copy trading'e acilirsa o projenin satiri, kendi Copy Trading kartinda gorunur (kendi hesap P&L, toplam follower fonu, toplam follower kari, o gece odenecek ucret sutunlariyla). Bu kart, portfoy grid'inin en ustunde sabit — cunku copy trading ana gelir kaynagi olacak, bireysel proje hesap karlari operasyonel gider + yeni proje sermayesini karsiliyor.
- Her proje karti, asama-bazli (backtest/demo/live/copy trading) sablon kullanir — hangi metrigin gosterilecegini otomatik belirler, kart tek tek elle tasarlanmaz.
- Agent aktivite/durum bolumu reddedildi — pipeline gorevleri cok hizli tamamlaniyor, takip etmeye deger degil.
- Kart grid layout secildi (sidebar+panel, tabs, terminal, kanban karsisinda).
- Rozet-vurgulu (badge-highlighted), asama-bazli semantik renkli gorsel stil secildi (sol-kenar renklendirme ve pastel dolgu alternatiflerine karsi, interaktif widget'larla karsilastirilarak). Mevcut renk semasi degistirilmedi.
- **Acik soru:** 9 proje karti esit boyutta mi, yoksa aktif/canli projeler daha buyuk mu (erken-asama projeler kompakt "stub" kart) — cozulmedi, buradan devam edilecek.

**Bilinen gelistirme ihtiyaclari (bekleyen):**
- "Pause aktif" durumu icin surekli gorunur, gorsel uyari (MilaGold'daki 14+ saatlik unutulmus pause olayindan, 14-15 Temmuz)
- Layer 2 (genel onay mekanizmasi: agent oneri uretir, dashboard'da gorunur, kullanici onaylar) — sadece MilaGold pause butonu canli, genel mekanizma genisletiliyor
- Layer 3 (dashboard'dan agent tetikleme) — son asama, baslanmadi
- Breakout Order'in seviye/parametre girisi arayuzu — bu proje uzerinden Layer 2/3 somutlasacak

**Orkestrasyon Yol Haritasi:**
1. Veri akisi + goruntuleme — TAMAMLANDI
2. Onay mekanizmasi — kismen canli
3. Tetikleme — baslanmadi

---

## Teknik Altyapi (Genel)

- Python 3.14 (py komutu)
- MT5 Python kutuphanesi
- Selenium + chromedriver-autoinstaller
- EasyOCR + Pillow (screenshot ile sinyal okuma)
- pyautogui (gerekirse)
- requests (Telegram)
- GitHub repo: ertanok/mila-yatirim-sistemi — sadece .py + .gitignore commit edilir

## VPS & Araclar

- **VPS:** Contabo, Portsmouth UK, Windows Server, GMT+3, High Performance guc plani, RDP session timeout kapali
- **MT5:** XMGlobal-MT5 6, mt5.initialize() parametresiz
- **Signal kaynagi:** Signal GPT (signalgpt.ai), Chrome remote debugging (port 9222, ChromeDebug profili)
- **GitHub:** ertanok/mila-yatirim-sistemi (public), Personal Access Token ile auth
- **Telegram:** MilaGoldBot — islem alertleri, hata bildirimleri
- **Deploy pipeline:** deploy.py, paramiko (SSH/SFTP)
- **Credentials:** config.py (version control disinda)
- **Orkestrator/headless Claude Code:** Ertan'in Pro aboneliginden ayri Anthropic API key ("Ertan's Individual"). Kredi/kullanim takibi: platform.claude.com → Billing/Usage.
- **Audit logging (14 Temmuz):** Security log'da "Other Logon/Logoff Events" (4778/4779) acik, log max 200MB — Chrome/OCR kararlilik arastirmasi icin.

## Dosya/Depo Senkron Notu

Dort kaynak: Project Instructions (bu dosyanin cekirdegi), yerel CLAUDE.md, VPS CLAUDE.md, agent_teknoloji_tablosu.md. Bunlarin arasindaki tutarlilik Genel Isleyis basliginda periyodik olarak kontrol edilir — PI'nin bu reorganizasyonu (cekirdek + Project Knowledge dosyalari) tamamlaninca, senkron kontrolu bu 4 kaynaga gore yeniden yapilacak.
