# Multi-Agent Mimarisi — Detay (Project Knowledge)

## Model Secimi — Gerekce ve Detay

**Orkestrator'un calisma bicimi:** Claude Code'dan ayri, kendi basina surekli/tetiklemeli calisan bir surec — Claude API'ye dogrudan cagri yapar, kendi sistem promptuyla. **Guncellendi (10 Temmuz):** Arastirmaci/Stratejist/Backtest Muhendisi/Risk Analisti gibi arastirma-pipeline agent'larini Orkestrator artik Claude Code'a ugramadan, kendi Agent SDK cagrisiyla direkt tetikliyor. Claude Code'a gorev verme hala gecerli ama sadece gercek dosya/kod/VPS implementasyonu gerektiginde (script yazma, deploy, config degisikligi) — arastirma pipeline'i icin degil.

**Calisma yeri:** VPS'te, headless (arka planda, terminal acmadan) bir Claude Code ornegi — Python Agent SDK araciligiyla Orkestrator bu ornegi cagirir, her tool cagrisini kendi yetki modeline gore canli onaylar/reddeder. Ayri API key ile kimlik dogrular (Ertan'in Pro aboneligi disinda).

**Yukseltme mekanizmasi:** Gunluk sayac (00:00 sifirlanir): <15 ise otomatik yukseltme + Telegram bilgi notu; >=15 ise onay istenir. Amac maliyet kontrolu degil, anormallik/bug yakalamak.

**Kanit:** Arena.ai Code Arena — claude-sonnet-5-thinking 92 modelden 6., selefinin (Sonnet 4.6, 13.) acikca ustunde.

**Maliyet — guncellendi (17 Temmuz):**
- **Bu ayki gercek maliyet: 99,87 $** (Anthropic Console Usage'tan).
- **Onemli duzeltme:** Arastirmaci/Stratejist/Backtest Muhendisi/Risk Analisti "Pro kapsaminda, faturaya girmez" degil artik — Orkestrator bunlari kendi Agent SDK cagrisiyla (ayri API key) tetikledigi icin metered. Bu, faturanin muhtemelen en buyuk kismi.
- **Bu maliyet surekli/sabit bir aylik taban degil, is-yogunluguna gore patlamali:** Bir proje aktif arastirma fazindayken (Justin gibi, gunluk 5 tur limitine yakin calisirken) yuksek, proje bir sonuca varinca (basarili strateji veya "durduruldu" karari) cagrilar durur. Baska bir proje kendi arastirma fazina girince tekrar yukselir.
- **Detay Karti Okuyucu:** Su an Faz 1'de (ekran goruntusu biriktirme) — tamamen kod-tabanli, Claude vision hic devrede degil, sifir maliyet. Vision maliyeti ancak Faz 2 (JSON'a cevirme) baslayinca dogar, o da muhtemelen toplu/bir kerelik bir is olabilir (surekli mi yoksa toplu mu olacagi henuz netlesmedi).
- Diger kalemler: Orkestrator'un kendi dongusu, headless Claude Code, Opus/Fable yukseltmeleri — bunlar da devam ediyor.

---

## Mimari Boyutlar (A-F)

### A) Orkestrasyon Modeli
Hiyerarsik-hibrit: runtime'da supervisor pattern (Orkestrator ustte, agentlar altta), arastirma tarafinda pipeline (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti).

**Esneklik notu (17 Temmuz):** Orkestrator, her gorevi tam pipeline sirasiyla vermek zorunda degil — ihtiyaca gore dogrudan bir asamaya (orn. Stratejist'e) sorabilir. Bu karar Orkestrator'un kendi degerlendirmesine birakilmistir, sabit bir kural olarak kisitlanmamistir.

### B) Yetki/Sinir Ayrimi
Dort risk boyutu: geri donulebilirlik, mali etki, tespit gecikmesi, etki alani — en kotu boyut kazanir. Orkestrator'un STOP yetkisi genis, START/CHANGE yetkisi dar. Katalog onceden kurulmaz, gercek vakalardan organik cikar.

### C) Iletisim / Durum Paylasimi
- **Dosya-tabanli iletisim:** JSON dosyalari, tek yazicisi olan, okuyan taraf yasini kontrol eder ("bayat kalirsa" davranisi tanimli).
- **Piyasa anomalisi tespiti (Gozetleme):** Rolling 60 sn penceresinde en yuksek-en dusuk fark. Gold esigi: 20 USD/1 dk. Diger enstrumanlar icin parametrik, henuz netlesmedi. Tespit sonrasi 60 dk yeni sinyal alinmaz. Tum projeler icin paylasilan servis, kural-tabanli.
- **Ekonomik Takvim Agent'i:** FED/CPI/TDI gibi olaylari izler, olay oncesi+sonrasi 30 dk (toplam 60 dk) durus uygular. Kaynak: ForexFactory (Selenium). Sadece yuksek-etki (kirmizi). Haftalik toplu cekme + gunluk kontrol. Tum scalping/daytrading projeleri icin gecerli, kural-tabanli.
- **Iletisim ajani:** Telegram su an yeterli. Twilio/telefon fikri aciliyetsiz.
- **Agent gorevlendirme/sonuc bildirimi:** Orkestrator agent'i gorevlendirdiginde ve sonuc uretildiginde Telegram bilgi notu + Orkestrator_Loglar kaydi. Onay talebi degil, sadece bilgilendirme.
- **Agent'lar arasi sayisal tutarlilik:** Bir agent'in urettigi sayisal bulgu baska bir agent tarafindan referans alinacaksa, hangi hesaplama/tanimdan geldigi once teyit edilir (farkli agent'lar ayni metrigi farkli yontemle hesaplamis olabilir).
- **Dashboard onay mekanizmasi (Layer 2):** Kismen canli — MilaGold pause/aktiflestir butonu gercekten calisiyor (milagold_control.json). Risk: buton degistirildikten sonra sessizce o durumda kalabiliyor (14 Temmuz'da ~14.5 saat, gercekte 15 Temmuz'da tekrar yasandi — pause unutulmus).

### D) Onay Katmani
Izleme ve onay/karar ayri fonksiyonlar, ikisi de bir arayuz gerektirir. Kanal secimi (Telegram vs Dashboard) Dashboard Layer 2 ile ortusuyor.

### E) Escalation Hiyerarsisi (4 seviyeli merdiven)
- **Seviye 0 — Otomatik:** OCR self-check anomalisi, acik pozisyon yoksa ve gunluk restart sayaci <3 ise otomatik 1 kez restart.
- **Seviye 1 — Bildirim:** Restart basarisiz veya limit dolmus → Telegram uyarisi, sistem bekler.
- **Seviye 2 — Otomatik arastirma:** Orkestrator, headless Claude Code'u read-only arastirma (durum kontrolu/log okuma) icin onaysiz gorevlendirir, sadece bilgi notu gider. Duzeltici islem (restart/dosya degisikligi) gerekiyorsa bu START/CHANGE — onay sorulur.
- **Seviye 3 — VPS yanit vermiyor:** Bagimsiz uptime-monitoring (UptimeRobot/healthchecks.io), GitHub push zamanini izler. Esik (~15 dk) gecilirse Ertan'a haber, Claude Code (Chrome ile) Contabo panelini kontrol eder, reboot onerisini sorar. Reboot hicbir zaman onaysiz yapilmaz.
- **Genel ilke:** Tespit/STOP otomatik olabilir; yeniden baslatma/reboot/devam etme (START/CHANGE) her zaman onay gerektirir.
- **3 ardisik RED esigi:** Genis-capli yaklasim degisikligi onerisi ve takip eden backtest/arastirma turlari, canliya/hesaba etkisi olmadigi surece bilgi notu yeterli, onay gerekmez.
- **Gunluk Pipeline Dongu Siniri:** Proje basina gunluk tam-tur sayaci (Stratejist cagrisi=1 tur). <5 otomatik devam + bilgi notu; >=5 sistem durur, somut onay sorusu gider.

### F) Versiyon/Rollback Guvenligi
- Git tek dogru kaynak, deploy.py ile commit/push/VPS pull, her deploy'un commit hash'i kayitli.
- Post-deploy izleme: 24 saat (tum piyasa seanslarini + gece gap penceresini kapsar). Muhakeme yetenegi sadece Orkestrator'da — diger agentlar sabit kurallarla calisir.
- Anomali saptanirsa: Sistem durur (otomatik STOP). Geri alma/devam karari onayli, otomatik degil.

---

## Agent Sistemi — Ekip Listesi

| Agent/Rol | Gorev | Durum |
|---|---|---|
| Orkestrator | Koordinasyon, STOP/START/CHANGE yetkisi | Canli, otonom (agent tetikleme dahil) |
| Arastirmaci | Piyasa/karakter analizi | Calisiyor |
| Stratejist | Hipotez, indikator kombinasyonu | Calisiyor (gunluk 5 tur siniri) |
| Backtest Muhendisi | MT5'te test, JSON rapor | Calisiyor |
| Risk Analisti | Elestirel inceleme | Calisiyor |
| Detay Karti Okuyucu | Lisa ters muhendisligi, detay karti okuma | Faz 1 canli test (Ters Muhendislik) |
| Gozetleme | Piyasa anomalisi tespiti | Gorev tanimi tamam, implementasyon bekliyor |
| Ekonomik Takvim Agent'i | Haber-durusu | Gorev tanimi tamam, implementasyon bekliyor |
| Raporlama Agent'i | Gece performans raporu, Lisa karsilastirmasi | Gorev tanimi tamam, implementasyon bekliyor |
| Iletisim ajani | — | Ileriki asama |

Her agent kendi konusmasinda yasar, rol degisimi yapilmaz (Orkestrator ve kod-tabanli surekli surecler haric).

**Yazma sirasi (tamamlandi):** Orkestrator → Gozetleme → Ekonomik Takvim → Detay Karti Okuyucu → Raporlama (gorev tanimlari)

**Sistem promptlari:** C:\MilaYatirim\*_system_prompt.md (Orkestrator TAMAMLANDI)
**Gorev tanimlari:** C:\MilaYatirim\*_gorev_tanimi.md (Gozetleme, Ekonomik Takvim TAMAMLANDI)

---

## Agent Teknoloji Tablosu — Ozet

**Secim ilkesi:** Birincil kriter kalite/performans, maliyet esitlikte ikincil. Guncelleme kurali: yeni karar verildiginde tablo o oturumda guncellenir, spekulatif satirlar TBD kalir.

**Yol1 / Yapisal-Hipotez Takimi** (Gold Daytrading, Agnostic A/B, Pariteler, Lisa yon-tayini paylasiyor): Arastirmaci/Stratejist/Backtest/Risk — Claude, karar verildi. Yapisal/Gorsel Patern Tanima (trend kanali, S/R) — TBD (ta-lib/pandas-ta/scipy adaylari, Claude vision aday).

**Yol2 / Veri-Once Kesif Takimi:** Justin — klasik ML/derin ogrenme/RL denenecek (scikit-learn/PyTorch/stable-baselines3 adaylari), TBD deneysel. Lisa Entry-Noktasi Cozucu — Justin ile ayni beceri seti, TBD deneysel.

**Lisa Ters Muhendislik — Veri Toplama:** Detay Karti Okuyucu — Claude vision (Anthropic API), karar verildi.

Detayli/guncel tablo icin ayri dosya: agent_teknoloji_tablosu.md (VPS/yerelde tutulan, PI'nin bir parcasi degil, senkron kontrolu Genel Isleyis'te takip edilir).
