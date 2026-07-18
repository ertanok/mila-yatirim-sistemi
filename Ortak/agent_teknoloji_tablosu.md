# MiLA Yatirim Sistemi — Agent Teknoloji Tablosu

Bu dosya bir basucu kitabidir. Amac: hangi agent hangi AI modelini/kutuphaneyi kullaniyor, hizli gorulebilsin. Ertan disaridan bir bilgi (okuma/izleme) edindiginde buraya bakip karsilastirma yapabilir, Claude'a aktarir, degerlendirme birlikte yapilir.

**Secim ilkesi:** Birincil kriter kalite/performans. Maliyet ancak esit performansta ikincil tercih sebebidir. Hicbir agent sirf ucuz oldugu icin secilmez, sirf pahali oldugu icin elenmez.

**Guncelleme kurali:** Yeni bir agent karari verildiginde veya mevcut biri degistiginde bu tablo o oturumda guncellenir. Spekulatif/henuz karari verilmemis satirlar "TBD" olarak birakilir, onceden doldurulmaz.

---

## Ana Iskelet

| Agent/Rol | Gorev | AI Model/Aile | Framework/Kutuphane | Durum | Not |
|---|---|---|---|---|---|
| Arayuz | Ertan ile etkilesim | Claude | Sonnet 5 (varsayilan), Opus/Fable (yukseltme) | Karar verildi (5 Tem) | Kesin, geri donusu yok |
| Orkestrator | Agent koordinasyonu, STOP/START/CHANGE yetkisi, tum ekibi yonetir | Claude | Sonnet 5 (varsayilan), Opus/Fable (yukseltme) | Model karari kesin — **sistem promptu durumu dogrulanacak** | Kesin, geri donusu yok. Kendi bagimsiz surecinde (Claude API) calisacak — bu surecin calismasi icin sistem promptunun yazilmis olmasi sart. Digerlerinin STOP/escalation/rollback davranislari bu agent'in yetkisine baglaniyor, o yuzden yazim sirasinda ilk olmasi gerekiyor |

## Yol1 / Yapisal-Hipotez Takimi
*(3-4-5-6 projeleri ve Lisa'nin yon-tayini alt-problemi bu takimi paylasiyor)*

| Agent/Rol | Gorev | AI Model/Aile | Framework/Kutuphane | Durum | Not |
|---|---|---|---|---|---|
| Arastirmaci | Piyasa/karakter analizi | Claude (LLM-tabanli akil yurutme) | — | Karar verildi, calisiyor | Mevcut MilaGold takimi — **sistem promptu var mi, dosya-tabanli mi yoksa konusma-ici rol mu, dogrulanacak** |
| Stratejist | Hipotez, indikator kombinasyonu | Claude | — | Karar verildi, calisiyor | Mevcut MilaGold takimi — ayni dogrulama gerekli |
| Backtest Muhendisi | MT5'te test, JSON rapor | Claude (kod uretimi) | Python + MetaTrader5 + pandas | Karar verildi, calisiyor | Mevcut MilaGold takimi — ayni dogrulama gerekli |
| Risk Analisti | Elestirel inceleme | Claude | — | Karar verildi, calisiyor | Mevcut MilaGold takimi — ayni dogrulama gerekli |
| Yapisal/Gorsel Patern Tanima | Trend kanali, destek/direnc tespiti | Belirsiz — klasik TA + olasi vision hibriti | ta-lib/pandas-ta/scipy (aday), Claude vision (kanal aktarimi icin aday) | **TBD** | Ertan Stratejisi, pariteler icin de gerekli, henuz netlesmedi |

## Yol2 / Veri-Once Kesif Takimi

| Agent/Rol | Gorev | AI Model/Aile | Framework/Kutuphane | Durum | Not |
|---|---|---|---|---|---|
| Justin | Scalping, sifirdan patern kesfi | Belirsiz — klasik ML / derin ogrenme / RL denenecek | scikit-learn / PyTorch / stable-baselines3 (adaylar) | **TBD, deneysel** | Vendor bagimsizligi ilkesi burada gecerli |
| Lisa Entry-Noktasi Cozucu | Neden 4127 degil de 4126 sorusu | Belirsiz — kural bulunamazsa ML/RL ihtimali | — | **TBD, deneysel** | Justin ile ayni beceri setini paylasabilir |

## Lisa Ters Muhendislik — Veri Toplama

| Agent/Rol | Gorev | AI Model/Aile | Framework/Kutuphane | Durum | Not |
|---|---|---|---|---|---|
| Detay Karti Okuyucu | Sinyal detay kartini (Structure&Trend, Momentum, Volatility, Price Plan, Risk) okuyup JSON'a cevirme | Claude (vision) | Anthropic API (vision) | Karar verildi (5 Tem) | EasyOCR degil — ifade/yorum icerdigi icin vision gerekli. Saatlik + anomali-tetiklemeli calisir |
| Yon-Tayini Cozucu | M30/M5 EMA100 karar mekanizmasini cozme | Claude (hipotez-test) | Yol1 takimiyla ayni | Karar verildi (5 Tem) | Kural tabanli oldugu dusunuluyor |

## Sistem Sagligi / Zamanlama (5 Temmuz — Mimari Boyutlar C/E/F)

| Agent/Rol | Gorev | AI Model/Aile | Framework/Kutuphane | Durum | Not |
|---|---|---|---|---|---|
| Gozetleme | Canli sistem sagligi, anomali-sonrasi-durus (buyuk SL sonrasi bir sure yeni sinyal alma freni) | Muhtemelen kural tabanli (AI gerekmeyebilir) | — | **TBD** | Suresi (baslangic 15 dk) ve hangi agent'in uygulayacagi netlesmedi |
| Ekonomik Takvim Agent'i | FED, TDI gibi bilinen-zamanli yuksek-etkili ekonomik olaylari harici kaynaktan ceker, islem penceresini kapatir | Yok — kural tabanli veri cekme, AI gerekmeyebilir | requests / ekonomik takvim API'si (ForexFactory, Investing.com — aday) | **TBD** | Tum scalping/daytrading projeleri icin gecerli, tek projeye ozgu degil |
| Escalation Seviye 3 Tetikleyicisi | VPS yanit vermiyor mu tespiti, GitHub push yasini izler | Yok — bulut tabanli izleme servisi | UptimeRobot / healthchecks.io / cron-job.org (ucretsiz, aday) | **TBD** | VPS'e ve Ertan'in bilgisayarina bagimli DEGIL, bagimsiz calisir |
| Raporlama Agent'i | Gece piyasa kapanisi sonrasi gunluk performans raporu (islem bazinda Lisa karsilastirmasi: TP1/TP2/TP3/SL sayilari, win rate, kar faktoru, toplam pip) | Yok — kural tabanli rapor uretimi, AI gerekmeyebilir | Python, surekli-donen script (Task Scheduler DEGIL — Session 0 riski) | Tasarim tam netlesmis, **sistem promptu/kod yok** | Tarihli rapor JSON + raporlama_status.json heartbeat yazar. Telegram sadece esik asiminda. Orkestrator heartbeat'i ~10 dk sonra kontrol eder, 3 kez retry, sonra escalate |

## Sistem Promptu Yazma Sirasi (7 Temmuz — oncelik onerisi)

Oncelik, agent'in digerlerinin davranisini belirleme derecesine ve aciliyete gore verildi:

1. **Orkestrator** — once bu. Mimari Boyutlar B/E/F'deki STOP/START/CHANGE yetkisi, en-kotu-boyut-kazanir kurali, heartbeat-retry mantigi burada kodlanmadan, altindaki agentlarin escalation/rollback davranisi havada kalir.
2. **Gozetleme** — canli sistem sagligi + anomali-sonrasi-durus, Mimari C/E/F'nin canli guvenlik parcasi.
3. **Ekonomik Takvim Agent'i** — 10 Temmuz CPI yaklasiyor (3 gun kaldi), aciliyet var. Zamanlama tutmazsa yedek plan (tek seferlik manuel pencere kapatma) devreye girmeli.
4. **Detay Karti Okuyucu** — Lisa ters muhendisliginin veri toplama ayagi, fiili baslangic noktasi.
5. **Raporlama Agent'i** — tasarimi tam netlesmis, yazimi nispeten hizli olmali.

*Not: Yon-Tayini Cozucu icin ayri bir sistem promptu gerekmeyebilir — "Yol1 takimiyla ayni" karari var, Arastirmaci/Stratejist/Backtest/Risk promptlarina Lisa-yon-tayini gorevi ek madde olarak islenebilir. Ayri mi yazilacak yoksa mevcutlara ek mi yapilacak, netlesmedi.*

## Acik Sorular (henuz konusulmadi, sadece not)
- Copy Trading icin ayri bir agent gerekiyor mu, yoksa mevcut mt5_agent instance'i yeterli mi?
- Iletisim agenti (Twilio) — su an gundemde degil, Telegram yeterli goruluyor (5 Temmuz)
