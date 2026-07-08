# STRATEJICI — GOLD (XAUUSD) GECMiS CALISMA / CERCEVE

**Not:** Bu icerik eski promptta "Justin Projesi — Cerceve" basligi altindaydi. Ancak icerik (MT5/GOLD sembolu, M15/H1 zaman dilimleri, dolar bazli TP 3/5/8$, SL 5-6$) MilaGold projesinin kendi yapisiyla birebir uyumlu — Justin projesi ise sifirdan/dis kaynaksiz olarak tanimli, bu cerceveyle uyusmuyor. Bu yuzden Gold'a ait bir gecmis calisma dosyasi olarak buraya tasindi. Justin projesi baslatildiginda bu dosya degil, o proje icin ayrica olusturulacak bir cerceve kullanilmali.

Bu dosya sistem promptunun bir parcasi degildir — Stratejist, Gold ile ilgili bir gorev aldiginda bu dosyayi okuyup ustune insa eder.

---

## Arastirmaci'dan Gelen Bulgular (Giris Bilgisi)
- Altin (XAUUSD/GOLD) kisa vadeli ara trendleri hedefleniyor
- M15 agirlikli, H1 filtre olarak kullanilabilir
- Tum gun calisiyor — Asya seansı sorunlu cikarsa filtre eklenebilir
- H1 ayni yondeyse: daha uzun TP hedefi (8 dolar ustu) denenebilir
- H1 ters yondeyse: daha temkinli (kisa TP veya girmeme) denenebilir
- Trend following bu enstrumanda simdiye kadar mean reversion'dan daha iyi sonuc vermis (bu, Gold'un su anki gozlemlenen karakteri — genel bir kural degil)

## Basari Kriterleri (Backtest hedefi — Gold icin)
- Profit factor: 2.0+
- Win rate: %55+
- Maksimum drawdown: %10 altinda
- Lot: 0.01, 1 pip = 0.1 USD

## Teknik Kisitlar (Gold icin)
- MT5 tabanli backtest (TradingView degil)
- Sembol: GOLD (XM broker, CFD)
- Timeframe: M15 sinyal, H1 filtre
- Emir tipi: Market order (veya stop order)
- TP mesafeleri: dolar bazli (pip degil)
- SL: maksimum 5-6 dolar (MilaGold ile tutarli)
- Tek seferde bir pozisyon (ayni anda 2'ye cikabilir ama kural degil)

## Risk / Islem Parametreleri (Gold icin — Risk Analisti icin gerekli)
- Baslangic kasasi: 200 USD (0.01 lot ile baslar)
- Lot buyutme: her 200 USD kasa artisinda +0.01 lot (200→0.01, 400→0.02, 600→0.03, 1000→0.05)
- Kasa ust siniri: 1500-2000 USD (1500 civarinda netlesecek), ulasilinca cekim yapilir
- Gunluk emniyet stopu: gunluk baslangic bakiyesine gore %20 dusus olunca islem alma durur (00:00'da sifirlanir)
- Islem maliyeti/slipaj varsayimi: 0.30 USD sabit spread (GOLD XM) — Backtest Muhendisi'nin spread varsayimiyla ayni, Risk Analisti'nin Kontrol 8'inde ek slipaj olarak cift sayilmamali
- Ortalama kayip (pes pese kayip hesaplamasi icin referans): SL mesafesi 5 USD baz alinabilir, ama gercek backtest raporundaki `ortalama_kayip_usd` degeri varsa o tercih edilir

**Not:** Bu risk parametreleri gercek hesabin su anki (8 Temmuz) durumunu yansitir — kasa ust siniri ve lot buyutme kademeleri ilerleyen zamanda guncellenebilir, Risk Analisti gorev aninda guncel degeri gorevi verenden teyit etmeli.

---

## Ornek Hipotez (Gold icin uretilmis, gecmis calisma)

```
HIPOTEZ ADI: EMA Kirılım + ADX Filtre
MANTIK: M15'te EMA20/EMA50 kesismesi kisa vadeli trendin donus noktasini verir.
        ADX > 20 filtresiyle sadece guclu trendlerde islem alinir, yan piyasa
        kirilimlari elenir. Gold trendi suren bir varlik oldugu icin bu kombinasyon
        uyumlu.
INDIKTORLER: EMA20, EMA50, ADX(14)
H1 FiLTRE: H1 kapanis fiyati H1 EMA50'nin ustundeyse sadece BUY sinyali al,
           altindaysa sadece SELL. H1 EMA50'ye cok yakinsa (<%0.3) girme.
GiRiS KOSULu: M15 mumunda EMA20, EMA50'yi yukari keser VE ADX > 20 → BUY market order.
              M15 mumunda EMA20, EMA50'yi asagi keser VE ADX > 20 → SELL market order.
SL KURALi: Kesisme mumunun karsi tarafina + 0.5 dolar. Maksimum 5 dolar.
TP KURALi: TP1: 3$, TP2: 5$. H1 ayni yondeyse TP3: 9$. TP3'te kapat.
SEANS FiLTRE: 07:00-20:00 GMT+3. Asya (00:00-07:00) disinda kal.
ONCELIK: 1-Yuksek — basit, test edilmesi kolay, goldun karakteriyle uyumlu
RiSKLER: Yatay piyasada EMA kirilmalari sahte sinyal uretir. ADX filtresi bunu
         azaltir ama tamamen engelleyemez. Hizli haber zamanlarinda SL asimi olabilir.
```
