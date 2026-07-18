# Diger Projeler — Detay (Project Knowledge)

## Proje 2: XM Copy Trading (Hazir — Gercek Hesap Bekleniyor)

**Model:** XM'de master hesap, follower'lardan kar payi geliri. MilaGold trading gelirinin ustune ek gelir katmani. Arkadaslar da follower olabilir, odenen kar payi manuel iade edilir.

**Teknik yapi:** Ayri XM hesabi (copy trading master), ayni signal.json'u okuyan ikinci bir milagold_mt5_agent instance'i farkli login ile. Kaldirac 1:500. Lot kurali ayni (200 USD=0.01 lot).

**Emniyet stopu:** Gunluk %20 sinirinda islem durur, takipciler o gun baska islem gormez — bu strateji aciklamasina yazilacak (seffaflik). MDD dusuk tutulmasi kritik metrik.

**Kesin, sonradan degistirilemez kararlar:** Minimum yatirim (~200 USD) ve ucret orani (~%20) — XM kurallari geregi sonradan yalnizca azaltilabilir, artirilamaz.

**Durum:** Hazirliklar tamam, gercek hesap performansi 2-3 hafta izlenecek.

---

## Proje 3: Justin Stratejisi

**Profil (5 Temmuz netlesti):** Sifirdan, dis kaynaksiz, Gold scalping. Lisa'ya rakip — entry/yon tamamen kendi uretimi. Farkli AI aileleri (klasik ML/derin ogrenme/RL) denenecek, vendor bagimsizligi ilkesi burada gecerli.

**Veri izolasyonu (10 Temmuz, KESiN):** Justin'deki hicbir agent Lisa/Signal GPT/MilaGold'un bulgu/veri/indikator/performansina erisemez. Tek kaynak: XM/MT5 fiyat verisi (dogrudan MetaTrader5 kutuphanesi). Calisma dizini: C:\MilaYatirim\Justin\ (fiziksel izolasyon). Not: EMA/RSI/ATR gibi genel kavramlarin kullanimi yasak degil — Justin bunlari kendi bagimsiz analiziyle yeniden kesfedebilir. Bir agent'a "X'i kullanma" derken X'in Signal GPT'ye ait oldugu aciklanmaz/isimlendirilmez.

**Ek netlestirme (14 Temmuz):** Izolasyon kurali format/cumle-kalibi kopyalamaya da uygulanir — dosyayi "sablon referansi" icin acmak da izolasyon kapsaminda.

**Gecmis (Faz 0):** Project Instructions'ta "M15 agirlikli, H1 filtreli trend following, backtest asamasinda" seklinde bir kayit vardi, ama bu hic tamamlanmis bir Arastirmaci raporuna/backtest'e karsilik gelmiyordu — hayalet/kontamine bir metin oldugu 5 Temmuz'da dogrulanip kaldirildi. Justin gercekten sifirdan basladi, justin_gecmis_calisma.md ile Faz 0 kapandi.

**Ilerleme (14-17 Temmuz):** 3 kural-tabanli hipotez (SMA-deviation, big-bar fade, regime-aware fade) + 2 ML turu (LightGBM/XGBoost) — tumu RED. Gunbatimi maddesi ML'de 2/2'de tetiklendi, sistem otonom olarak durdu, onay bekledi. Governance dosyalari yazildi (justin_gold_scalping_karar_ve_governance, justin_ml_anti_overfitting_protokolu, justin_backtest_onkontrol_standardi).

**Aile-bazli yeniden degerlendirme (17 Temmuz):** Orkestrator'a bagimsiz bir strateji-ailesi siniflandirmasi yaptirildi (Fable 5) — sonuc: denenen 5 hipotezin (3 kural-tabanli + 2 ML) hepsi mean-reversion/fade ailesindeymis, trend-following/breakout hic dogrudan denenmemis. Karar: mean-reversion ailesi kapatildi, **trend-following merkeze alindi** — yontem serbest (kural-tabanli veya ML/RL acik). Bu yeni tur Orkestrator'a iletildi, sonuc henuz gelmedi.

**Governance (10-17 Temmuz, KESiN):**
- 5 Stratejist cagrisi/gun siniri (00:00 sifirlanir), asilirsa otomatik pause + Telegram onay talebi
- "3 ardisik RED" esigi bilgi notu yeterli (STOP-genis kategorisi), onay gerekmez — onay siniri canliya/demo/gercek hesaba gecis adimidir
- Aile-bazli gunbatimi maddesi: bir ailede (orn. ML) 2 ardisik RED paterni → otomatik onceki secenege donus
- Sayisal tutarlilik kurali: bir agent'in urettigi sayisal bulgu, sonraki agent tarafindan referans alinacaksa hangi hesaplama/tanimdan geldigi once teyit edilir

**Klasor duzeni notu (13 Temmuz, ACIK):** Justin klasoru MilaGold'un git-tracked repo'sunun (mila-yatirim-sistemi) disinda kaldi — izolasyon icin bu sart degildi (cwd sabitlemesi yeterli). Tek-kural onerisi: kod ne olursa olsun mila-yatirim-sistemi icinde, veri/log .gitignore ile harici (MilaGold'daki desen). Justin, Orkestrator_Loglar, TersMuhendislik hepsi bu kurala gore iceri tasinmali — henuz uygulanmadi, Genel Isleyis'in bekleyen listesinde.

---

## Proje 4: Ters Muhendislik (Aktif — Canli Test Asamasi)

**Amac:** Signal GPT'nin karar mekanizmasini cozmek, bagimsizlasmak.

**Iki alt-problem:** (1) Yon-tayini (M30/M15/M5/M1 EMA100 gozlendi) — kural tabanli, Yol1 (Arastirmaci/Stratejist/Backtest/Risk) metodolojisi. (2) Entry-noktasi (neden 4127 degil 4126) — kural bulunamayabilir, ML/RL ihtimali (Yol2, Justin ile ayni beceri seti).

**Detay Karti Okuyucu — Faz 1 (SS biriktirme):**
- Model B mimarisi: OCR agent'tan tamamen bagimsiz, ayri Selenium oturumu/sekme, ayni Chrome (CDP port 9222). OCR'in liste okumasi kesilmiyor (test edildi, guvenli).
- CDP Input.dispatchMouseEvent ile tiklama (Selenium .click()/ActionChains Flutter canvas'ta calismiyor)
- Tetikleyiciler: saatlik + fiyat_esigi ($25 farkli dilime gecince)
- Esik tetiklenip aktif sinyal yoksa: PNG yerine log satiri ("kart yok")
- Calisma penceresi: 05:00-00:00
- Hedef: entry+yon bazinda **50 benzersiz kart** (rastgele 50 screenshot degil) — bu sayi, kartin alan yapisini (Structure&Trend, Momentum, Volatility, Price Plan, Risk bolumlerinin ici) netlestirmek icin secildi. 50'ye ulasinca durum dosyasi + Telegram bilgi notu, veri seti Arastirmaci'ya teslim edilir.
- Faz 2 (ileride): Claude vision ile JSON'a cevirme — EasyOCR degil, kart ifade/yorum iceriyor
- Konum: C:\MilaYatirim\TersMuhendislik\detay_kartlari\, dosya adi detay_karti_{YYYYMMDD}_{HHMM}_{tetikleyici}.png

**Canli test durumu (13-14 Temmuz):** Chrome, testler sirasinda 5 kez cöktü (20-40 dk araliklarla), tam uctan uca test bloke oldu. Kok neden MilaGold Chrome sorunuyla ortak — orada cozuldu (15 Temmuz), TM testine devam edilebilir.

**Uyelik durumu:** SignalGPT uyelik sorunu cozuldu (15 Temmuz oncesi), sinyal hakki "unlimited" — canli test onkosulu kalkti.

**Not:** Bu Chrome ornegi MilaGold ile paylasiliyor — MilaGold'daki Chrome/OCR Kararlilik Sorunu bu projeyi de dogrudan etkiliyordu.

---

## Proje 5: Pariteler Stratejisi (Fikir Asamasi)

Doviz ciftleri uzerine bir strateji fikri, henuz tasarlanmadi. Daytrading'e uygun (scalping degil). Yapisal/gorsel patern tanima (trend kanali, S/R) muhtemelen burada da kullanilacak.

---

## Proje 6: Gold Daytrading / Proje 7-8: Agnostic A/B

Ertan'in daha once TradingView'da gelistirdigi kendi stratejileri — MT5'e uyarlanacak, backtest yapilacak, gelistirilecek. BB(20,close,2) + SMA tabanli, SELL sinyalleri ust bantta, skor sistemi var. Enstruman XAUUSD, muhtemelen M15. Sabit mesafe yerine trend kanali + S/R onemliyse revize edilebilir — bu durumda yapisal/gorsel patern tanima gerekir.

Ideal olarak coklu enstruman uyumlu; enstruman karakteri izin vermezse biri Gold, biri DAX, biri Nasdaq olabilir. Basari esigi: Kar faktoru 2.0. TradingView'dan MT5'e tasima, bu 3 proje calisirken yapilacak.

**Durum:** Baslangic asamasi, oncelik sirasinda "onumuzdeki aylar" kategorisinde — Justin/Orkestrator olgunlasana kadar bekliyor.

---

## Proje 9: Breakout Order

**Amac:** Manuel yurutulen bir stratejiyi otomatize etmek. Her sabah Cem Arslan analizinden (metin, seviye bilgisi guvenilir okunur — grafik degil) alinan direnc seviyelerine buy-stop emirleri kurup takip etmek. Asil problem hiz degil, ilk deneme sonrasi olusan yeni firsatlarin takip edilememesi.

**Kapsam ayrimi:** Otomatiklesmeyecek: seviye belirleme/analiz (Ertan'in isi). Otomatiklesecek: verilen seviyeye gore emir kurma + yeniden-tetikleme + coklu enstruman takibi.

**Enstrumanlar:** Gold, Silver, Ger40Cash, US100Cash (rutin), EURUSD, GBPJPY (sik), GBPCAD, NZDCAD (bazen), OilCash/BrentCash (nadir). Her enstruman icin ayri SL/TP (pip).

**Girdi (Dashboard uzerinden, 17 Temmuz'da netlesti):** Direnc ve destek seviyeleri Ertan tarafindan Dashboard'dan girilecek (Enstruman, Seviye, yon, ATH isareti). Excel ile gecici cozum plani terk edildi — arayuz detayi Dashboard basliginda ele aliniyor.
- Durum dosyasi (sadece motor yazar): aktif/pasif/sayac bilgisi

**Yeniden-tetikleme mantigi (17 Temmuz, cift yonlu):**
- Direnc seviyelerine buy-stop, destek seviyelerine sell-stop emri girilir — ikisi de aktif, "destek ileride acilir" plani terk edildi
- Emir tetiklenince seviye pasiflesir (silinmez)
- Sonuc (SL/TP) sonrasi fiyat seviyeden X pip geri cekilirse (yon: direnc icin yukari, destek icin asagi) yeniden aktif olur, yeni emir girilir
- X pip esigi enstruman basina ayri parametre (SL mesafesiyle ayni olamaz, SL cok kisa — 1-2$ mertebesinde)
- Gunluk sayac: bir seviye gunde max N kez aktif olabilir (00:00 sifirlanir)
- ATH kirilimlarinda SL daha uzun tutulabilir (ayri tik/switch)

**Risk/koruma:**
- Toplam portfoy %20 gunluk dusus limiti (MilaGold emniyet stopuyla ayni mantik)
- Gap koruma: MilaGold'daki 23:45/23:55 penceresi dogrudan tasinir
- Ekonomik Takvim Agent'i (paylasilan servis) bu projeye de baglanir — spread genislemesi riski icin
- Low-spread hesap kullanilacak (SL mesafesi cok kisa, spread kritik — SL'in yarisi kadar spread olabiliyor)

**Teknik:** Tek MT5 agent, coklu enstrumani kendi icinde donen (MilaGold'un mt5_agent mantiginin genellemesi). Her enstrumanin durumu (aktif/pasif/sayac) ayri tutulmali. Birim ayrimi kritik: Gold dolar bazli, doviz ciftleri pip/point bazli. Sifir Claude API maliyeti — tamamen kural-tabanli.

**Durum:** PRICE_OFFSET (TradingView/MT5 fiyat farki) calismasi tamamlanmak uzere. Girdi Dashboard'a baglandigi icin, arayuz Dashboard basliginda netlesene kadar motor implementasyonu buna bagli olmayan kisimlarda (coklu enstruman durum yonetimi, gap/ekonomik takvim entegrasyonu) ilerleyebilir.

---

## Gelecek Plan (uzun vadeli, projelerin ustunde)

1. MilaGold gibi baska sinyal kaynaklari ekle (her biri ayri proje, ayri hesap)
2. TradingView stratejisi tamamla
3. Iletisim agenti — Twilio ile arama/WhatsApp, aciliyeti yok
4. Gayrimenkul, startup yatirimlari
5. Polikultur ciftlik
