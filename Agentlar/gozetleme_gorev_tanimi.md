# GOZETLEME — GOREV TANIMI

Bu dosya bir sistem promptu DEGiLDiR. Claude Code'a "bunu boyle insa et" diyen bir teknik ozellik dokumanidir. Gozetleme, Claude API'ye hic cagri yapmaz — kural-tabanli, surekli calisan bir Python sureci (OCR/MT5/Sync agentlariyla ayni kategori).

---

## 1. Amac ve Kapsam

Gozetleme, piyasa anomalisi (fiyatta ani/buyuk hareket, yon onemsiz, pozisyonda olup olmamamizdan veya SL'den bagimsiz) tespit eder, tespit sonrasi belirli bir sure yeni sinyal alinmasini engeller.

**Tek bir projeye ozgu degildir.** MilaGold, Justin, Ertan Stratejisi, Pariteler — tum scalping/daytrading projeleri icin paylasilan bir servistir.

---

## 2. Tespit Yontemi

- **Rolling 60 saniyelik pencerede en yuksek-en dusuk fark** hesaplanir (ardisik tek fiyat sicramasi degil)
- Bu, hem ani gap-tipi hareketi hem dakika icindeki surekli tirmanisi yakalar — ikisi de anomali sayilir
- Veri kaynagi: MT5'ten canli fiyat (ilgili sembol icin tick/bar akisi)

---

## 3. Esik Degerleri (enstrumana gore parametrik)

- **Gold: 20 USD / 1 dakika (KESiN, 7 Temmuz)**
- Diger enstrumanlar (DAX, Nasdaq, forex ciftleri): **TBD** — her enstruman eklendiginde ayri ayri belirlenecek, sabit bir dolar degeri tum enstrumanlara uygulanmaz
- Kod, esik degerlerini sabit yazmak yerine bir config/mapping yapisinda tutmali (sembol → esik), boylece yeni enstruman eklemek kod degisikligi gerektirmez

---

## 4. Tetiklenince Ne Olur

- Anomali tespit edilince, paylasilan bir dosyaya yazilir — onerilen ad: `market_anomaly_status.json`
- Icerik (taslak): `{"sembol": "GOLD", "tespit_zamani": "...", "hareket_buyuklugu": "...", "durus_bitis_zamani": "..."}` (tespit_zamani + 60 dk)
- **Durus suresi: 60 dakika** (baslangic degeri — Raporlama Agent'i veri biriktirdikce revize edilebilir)
- **Tek yazici:** Gozetleme
- **Okuyucular:** her projenin kendi MT5/sinyal agent'i — yeni sinyal islemeden once bu dosyayi kontrol eder, ilgili sembol icin `durus_bitis_zamani` gelecekte ise sinyali atlar

---

## 5. Dosya-Tabanli Iletisim Kurallari (Mimari Boyut C ile tutarli)

- Dosya sadece anomali tespit edildiginde guncellenir — surekli "her sey normal" yazmaz
- Okuyan taraf, ilgili sembol icin dosyada bir kayit var mi ve `durus_bitis_zamani` halen gelecekte mi diye bakar — bu, "bayat kalirsa ne olur" sorusunu dogal olarak cevaplar (kayit yoksa veya sure gecmisse, anomali yok kabul edilir)

**Acik soru (COZULDU, 7 Temmuz):** Gozetleme'nin kendisi cokerse (dosyayi hic guncelleyemez hale gelirse), sistem bunu nasil fark edecek? Anomali dosyasinin kendisi bu durumu yakalamiyor — cunku sadece anomali VARKEN yaziliyor, Gozetleme'nin canli oldugunu surekli dogrulayan bir sey degil.

**Karar:** Gozetleme ayrica bir heartbeat dosyasi yazar (`gozetleme_status.json`, her N saniyede bir guncellenir — Raporlama Agent'inin heartbeat tasarimiyla ayni desen). Orkestrator bu heartbeat'i izler, bayatlarsa Seviye 1 bildirimi tetiklenir. Bu, Gozetleme'nin kendisinin "OCR anomalisi" tipi bir soruna dusmesini (sessizce durmasi) yakalar.

---

## 6. Bildirim

- Anomali tespit edildiginde Telegram'a bilgi notu gider: hangi sembol, ne buyuklukte hareket, durus ne zaman bitecek
- Bu bir onay talebi degil — Gozetleme'nin islevi Orkestrator'un "STOP yetkisi genis" kategorisine girer, otomatik isler

---

## 7. Acik Sorular / TBD

- Diger enstrumanlar icin esik degerleri (DAX, Nasdaq, forex ciftleri — henuz hicbiri aktif degil)
- Sinyal-oncesi kontrol noktasi: her projenin MT5 agent'i bu dosyayi tam olarak nerede kontrol etmeli — signal.json okunmadan once mi, order_send'den hemen once mi? (muhtemelen: MilaGold'daki EMA20/streak filtresi gibi, sinyal islenmeden once ek bir filtre adimi olarak)
- Dosya adi/format kesin degil, Claude Code implementasyon sirasinda ayarlayabilir (onemli olan: tek yazici, stale-safe, sembol-bazli)
