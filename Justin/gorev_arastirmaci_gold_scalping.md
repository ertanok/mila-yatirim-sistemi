# GOREV TANIMI — Orkestrator → Arastirmaci

## Gorev Kimligi
- Proje: PROJE 2 — Justin Stratejisi (Gold Scalping alt-hedefi)
- Pipeline adimi: 1/4 — Arastirmaci (Yol1 metodolojisi: Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti; bu sira atlanamaz)
- Tarih: 10 Temmuz 2026
- Gorevlendiren: Orkestrator

## Amac
XAUUSD (Gold) uzerinde, kisa vadeli (scalping, tipik olarak M1-M5 tutus suresi, dakikalar mertebesinde) bir strateji ailesi icin arastirma/hipotez raporu uret. Bu asamada nihai kurallar/parametreler beklenmiyor — amac, test edilebilir hipotezler ve literatur/veri gozlemleriyle desteklenmis aday yaklasimlar sunmak. Stratejist bir sonraki adimda bunlari somut kurallara donusturecek.

## VERI iZOLASYONU — ZORUNLU KISIT (CLAUDE.md, 10 Temmuz, KESiN)
Bu gorev, Justin projesi kapsaminda yapiliyor. Asagidaki kisitlar MUTLAKTIR, istisna yoktur:

- Tek veri kaynagi: XM/MT5 fiyat verisi, dogrudan MetaTrader5 kutuphanesi araciligiyla (OHLCV, tick verisi, spread, oturum saatleri).
- MilaGold, Lisa (ters muhendislik), Signal GPT ile ilgili HICBIR bulguya, indikatore, sinyal mantigina, performans kaydina veya dosyaya erisim/atif YOK. Ozellikle:
  - signal.json, milagold_trades.json, lisa_performance.json, stratejici_gold_gecmis_calisma.md, positions_status.json vb. dosyalarina bakma, referans verme.
  - Lisa'nin ters muhendislik calismasi kapsaminda Signal GPT icin tespit edilmis/varsayilmis herhangi bir karar mekanizmasini "baslangic noktasi" olarak KULLANMA — bu bilginin kendisi izolasyon kapsamindadir ve Justin'e aktarilmamalidir; Justin bu konuda tamamen bagimsiz/orijinal analiz yapmalidir.
  - MilaGold'un kendine ozgu aktif filtreleri/parametreleri (hangi indikatorler ve hangi ayarlanmis degerlerin kullanildigi burada belirtilmeyecek — bu bilginin kendisi izolasyon kapsamindadir) fikir kaynagi olarak KULLANILMAYACAK. Justin'in EMA/RSI/ATR gibi genel teknik kavramlari kullanmasi serbesttir (bunlar herkese acik, genel finans bilgisi) — ama spesifik olarak "MilaGold'da su calisiyor, oradan alalim" mantigi yasak.
- Calisma dizini: yalniz C:\MilaYatirim\Justin\ altinda oku/yaz. Bu dizinin disindaki MilaGold'a ait hicbir dosyaya erisme.
- Amac hatirlatma: Justin sifirdan, dis kaynaksiz bir arastirma hattidir; farkli AI/istatistik ailelerinin (klasik ML, RL, kural-tabanli) sifirdan denenmesi bekleniyor.

Eger arastirma sirasinda MilaGold/Lisa'ya ait bir dosya/veri karsina cikarsa: KULLANMA, calismana dahil etme, ve raporunda "su kaynak izolasyon geregi disarida birakildi" seklinde not dus.

## Kapsam
1. XAUUSD'in kisa vadeli (M1-M5) fiyat davranisini karakterize eden genel, halka acik bilgiye dayali gozlemler (volatilite paternleri, oturum bazli davranis: Asya/Londra/NY acilisi, spread davranisi, haber saatleri civari hareket).
2. En az 3 birbirinden bagimsiz aday scalping yaklasimi onerisi (orn. volatilite-breakout, ortalamaya-donus/VWAP tabanli, momentum/order-flow yaklasimi — bunlar ornek, bagimsiz arastirmanla genisletebilir/degistirebilirsin).
3. Her aday icin: hangi ham MT5 verisiyle (fiyat/hacim/spread) test edilebilecegi, olasi risk/tuzaklar (spread genisligi, slipaj, gap riski), scalping'e ozgu sinirlamalar (islem maliyeti/spread'in kucuk hedefe orani).
4. Acik sorular / belirsizlikler listesi (Stratejist'in karar vermesi gereken noktalar).

## Beklenen Cikti
- Rapor formati: Markdown, C:\MilaYatirim\Justin\arastirmaci_gold_scalping_raporu.md
- Bolumler: Ozet, Gozlemler, Aday Yaklasimlar (>=3), Riskler/Sinirlamalar, Acik Sorular, Izolasyon Notu (disarida birakilan kaynaklar varsa)

## Sonraki Adim
Rapor tamamlaninca Orkestrator, Stratejist'i bu raporla gorevlendirecek (pipeline sirasi geregi Backtest Muhendisi'ne dogrudan atlanmaz).

## Bildirim
Bu gorev tamamlandiginda Orkestrator, Ertan'a Telegram bilgi notu gonderir (onay talebi degil, bilgilendirme — CLAUDE.md C-boyutu, 10 Temmuz KESiN) ve Orkestrator_Loglar'a kayit dusar.
