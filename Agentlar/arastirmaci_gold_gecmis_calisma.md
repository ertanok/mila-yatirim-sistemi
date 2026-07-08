# ARASTIRMACI — GOLD (XAUUSD) GECMiS CALiSMA

Bu dosya, Arastirmaci agent'inin Gold uzerinde daha once yaptigi/planladigi calismalarin kaydidir. Agent, Gold ile ilgili bir gorev aldiginda bu dosyayi okuyup ustune insa eder — sistem promptunun bir parcasi degildir, sadece Gold'a ozel bir referanstir.

---

## Zaten Bilinen Bulgular (Genislet, Tekrar Etme)

Bu bulgular onceki calismalarda uretildi. Bunlarin ustune insa et — ayni sonuclari tekrar yazma:

- Gold kisa vadeli ara trendler olusturuyor
- M15 sinyal, H1 filtre olarak kullanilabilir
- Tum gun hedefi zorlayici — Asya seansı sorunlu
- H1 ile M15 ayni yondeyse devam gucu artiyor
- Trend following uygundur; mean reversion uygunsuz

Bunlari **sayisal olarak dogrula ve derinlestir**. "Asya sorunlu" degil — "Asya'da X USD'yi asan M15 hareketlerin %Y'si Londra acilisina kadar geri doniyor" de.

---

## Planlanan/Onerilen Analiz Konulari

Asagidaki 10 konu, Gold uzerinde daha once tanimlanmis arastirma basliklaridir. Her biri icin: ne arastirildigi, hangi Python koduyla, cikti nasil formatlanacagi.

---

### KONU 1 — Seans Bazinda Volatilite Profili

**Soru:** Her GMT+3 saatinde M15 barlarin ortalama genisligi (high-low) nedir?

```python
import MetaTrader5 as mt5
import pandas as pd

mt5.initialize()
rates = mt5.copy_rates_from_pos("GOLD", mt5.TIMEFRAME_M15, 0, 50000)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s') + pd.Timedelta(hours=3)
df['hour'] = df['time'].dt.hour
df['range'] = df['high'] - df['low']
df['body']  = abs(df['close'] - df['open'])
df['wick']  = df['range'] - df['body']

rapor = df.groupby('hour').agg(
    ort_range=('range', 'mean'),
    ort_body=('body', 'mean'),
    ort_wick=('wick', 'mean'),
    bar_sayisi=('range', 'count')
).round(3)

print(rapor)
```

Raporla:
- Saat bazinda ortalama bar genisligi (USD)
- Wick/body orani — buyuk wick = yanlis sinyal riski
- En yuksek 3 saat, en dusuk 3 saat
- Seans sinirlarini tabloya isaretle: Asya (00–07), Londra (07–16), NY (13–22) GMT+3

---

### KONU 2 — Trend Surekliligi (Persistence) Analizi

**Soru:** M15'te bir bar yukari kapanirsa, sonraki bar ne kadar siklikla yukari kapanir? Seansa gore degisiyor mu?

```python
df['yukari'] = (df['close'] > df['open']).astype(int)
df['sonraki_yukari'] = df['yukari'].shift(-1)
df['ayni_yon'] = (df['yukari'] == df['sonraki_yukari']).astype(int)

persistence = df.groupby('hour')['ayni_yon'].mean().round(3)
print("Saat bazinda trend surekliligi (1.0 = her zaman devam):")
print(persistence)

# Arka arkaya ayni yonde kac bar?
# Seri uzunlugunu hesapla
def max_seri(series):
    max_s = cur_s = 0
    for v in series:
        cur_s = cur_s + 1 if v == series.iloc[0] else 0
        max_s = max(max_s, cur_s)
    return max_s
```

Raporla:
- Her saat icin trend surekliligi yuzdesi
- Ortalama art arda ayni yonde bar sayisi (tipik trend uzunlugu)
- Asya vs Londra vs NY karsilastirmasi

---

### KONU 3 — Asya Hareketi Geri Donus Analizi

**Soru:** Asya seansında (00:00–07:00 GMT+3) yapılan X USD'lik hareketin yuzde kaci Londra acilisinda geri doniyor?

```python
df['date'] = df['time'].dt.date

# Her gun icin Asya seansini izole et
asya = df[df['hour'].between(0, 6)]
londra_acilis = df[df['hour'] == 7]  # ilk Londra bari

asya_hareket = asya.groupby('date').apply(
    lambda g: g['close'].iloc[-1] - g['open'].iloc[0]
)
# Londra acilis fiyati ile kiyasla
# Geri donus = Londra'da Asya hareketin tersi yonde mi?
```

Raporla:
- Asya hareketi > 1 USD → Londra'da geri donus orani: %?
- Asya hareketi > 3 USD → Londra'da geri donus orani: %?
- Asya hareketi > 5 USD → Londra'da geri donus orani: %?
- Sonuc: Asya kac dolar ustunden sonra "geri donus bolgesine" giriyor?

---

### KONU 4 — Londra Acilisi Dinamigi

**Soru:** Londra acilisinda (07:00–08:30 GMT+3) ilk 30 dakika ile sonraki 2 saat arasinda trend surekliligi farki ne?

```python
# Londra ilk 2 bari (07:00, 07:15) vs sonraki 8 bari
londra_erken = df[df['hour'] == 7]
londra_gec   = df[df['hour'].between(8, 10)]

# Ilk 30 dk yon ile 08:00-10:00 yon uyumu ne kadar?
```

Raporla:
- "Londra acilisinin ilk 30 dakikasinda olusan yonun saat 10'a kadar devam etme orani: %?"
- "False breakout (ilk 30 dk yonu tersine donen) orani: %?"
- Bu Stratejist icin kritik: Londra acilis filtresi koymali mi?

---

### KONU 5 — H1 / M15 Yön Uyumu Analizi

**Soru:** H1 ve M15 ayni yonde oldugunda M15 trend devam orani, zit yonde oldugundan ne kadar farkli?

```python
rates_h1 = mt5.copy_rates_from_pos("GOLD", mt5.TIMEFRAME_H1, 0, 12000)
df_h1 = pd.DataFrame(rates_h1)
df_h1['time'] = pd.to_datetime(df_h1['time'], unit='s') + pd.Timedelta(hours=3)
df_h1['h1_yukari'] = (df_h1['close'] > df_h1['open']).astype(int)

# M15 ile birlestir (merge_asof ile look-ahead olmadan)
df = pd.merge_asof(df.sort_values('time'),
                   df_h1[['time','h1_yukari']].sort_values('time'),
                   on='time', direction='backward')

ayni_yon = df[df['yukari'] == df['h1_yukari']]['ayni_yon'].mean()
zit_yon  = df[df['yukari'] != df['h1_yukari']]['ayni_yon'].mean()
print(f"H1-M15 ayni yon → surekliligi: {ayni_yon:.3f}")
print(f"H1-M15 zit yon  → surekliligi: {zit_yon:.3f}")
```

Raporla:
- H1-M15 yön uyumu: surekliligi %?
- H1-M15 yön uyumsuzlugu: surekliligi %?
- Fark anlamli mi? (>5 yuzde puani = anlamli)

---

### KONU 6 — ATR Dagilimi ve TP/SL Fizibilitesi

**Soru:** M15 barlarin ATR dagilimi 3/5/8 USD TP hedeflerini destekliyor mu?

```python
df['atr14'] = df['range'].rolling(14).mean()

print("ATR yuzdelik dilimleri:")
print(df['atr14'].quantile([0.10, 0.25, 0.50, 0.75, 0.90]).round(3))

# Seans bazinda ATR
print("\nSeans bazinda ATR:")
print(df.groupby('hour')['atr14'].mean().round(3))

# TP mesafesi kaç ATR'ye karsilik geliyor?
medyan_atr = df['atr14'].median()
for tp in [3.0, 5.0, 8.0]:
    print(f"TP {tp} USD = ATR'nin {tp/medyan_atr:.1f} kati")
```

Raporla:
- M15 medyan ATR: ? USD
- TP1 (3 USD) = ATR'nin kac kati?
- TP3 (8 USD) = ATR'nin kac kati? (ulasilabilir mi?)
- Seans bazinda: "Asya'da TP3 = ATR'nin X kati — gerci bir gunde ulasilmasi zor"

---

### KONU 7 — Gun Bazinda Karakter Analizi

**Soru:** Haftanin hangi gunu Gold daha trend, hangi gunu daha yatay?

```python
df['dayofweek'] = df['time'].dt.dayofweek  # 0=Pazartesi, 4=Cuma

gun_analizi = df.groupby('dayofweek').agg(
    ort_range=('range', 'mean'),
    ort_atr=('atr14', 'mean'),
    trend_sureklilik=('ayni_yon', 'mean'),
    bar_sayisi=('range', 'count')
).round(3)

gun_analizi.index = ['Pazartesi','Sali','Carsamba','Persembe','Cuma']
print(gun_analizi)

# Pazartesi gap analizi
pazartesi = df[df['dayofweek'] == 0]
# Onceki Cuma kapanisi ile Pazartesi acilisi farki
```

Raporla:
- Siralanmis gun bazinda volatilite ve trend surekliligi
- Pazartesi gap siklig ve ortalama buyuklugu
- Cuma son 2 saatte trend tersine donme orani

---

### KONU 8 — Haber Saatleri Analizi

**Soru:** NFP, FOMC, CPI gibi onemli haber saatlerinde M15 ATR normal guneye gore ne kadar yukseliyor?

Bu analiz icin web arastirmasi yap — MT5 verisi ekonomik takvim icermez.

Arastir:
- NFP: Her ayin ilk Cumasi, 15:30 GMT+3 — ortalama gunluk hareket etkisi
- FOMC: Yilda 8 kez, 21:00 GMT+3 — karar aciklanmadan once/sonra volatilite
- CPI: Her ay ortasi, 15:30 GMT+3
- Jeopolitik olaylar: anlık spike pattern (V sekli mi, devam mi?)

Raporla:
- Haber gunlerini filtreleyin mi? (sadece saatleri mi, tum gunu mu?)
- Hangi haberler Gold'u en cok etkiliyor?
- Haber oncesi (30 dk) vs sonrasi (30 dk) ortalama hareket karsilastirmasi

---

### KONU 9 — Mum Anatomisi: Wick/Body Orani

**Soru:** Buyuk wick'li mumlar yanlis sinyal mi veriyor?

```python
df['wick_oran'] = df['wick'] / df['range'].replace(0, 0.001)
df['buyuk_wick'] = df['wick_oran'] > 0.5  # Bar uzunlugunun %50'den fazlasi wick

# Buyuk wick'li mumdan sonra trend sureliyor mu?
buyuk_wick_sonrasi = df[df['buyuk_wick']]['ayni_yon'].mean()
kucuk_wick_sonrasi = df[~df['buyuk_wick']]['ayni_yon'].mean()

print(f"Buyuk wick sonrasi trend surekliligi : {buyuk_wick_sonrasi:.3f}")
print(f"Kucuk wick sonrasi trend surekliligi: {kucuk_wick_sonrasi:.3f}")

# Seans bazinda wick orani
print(df.groupby('hour')['wick_oran'].mean().round(3))
```

Raporla:
- Wick orani yuksek barindan sonra trend devam orani dusuyor mu?
- Hangi saatlerde wick orani en yuksek? (yanlis sinyal riski yuksek saatler)
- Stratejist icin ham veri: "Buyuk wick sonrasi surekliligi %48, kucuk wickten sonra %61"

---

### KONU 10 — DXY Korelasyonu ve Dis Faktorler

**Soru:** Gold ile ABD Dolari (DXY) arasindaki iliski ne kadar guvenilir? Hangi kosullarda korelasyon bozuluyor?

Bu analiz icin web arastirmasi + genel piyasa bilgisi kullan (MT5'te DXY verisi olmayabilir).

Arastir:
- Gold-DXY ters korelasyonu: tarihsel guc ve istisnalari
- Risk-off ortami: DXY ve Gold AYNI anda yukarı gidebiliyor mu? (safe haven etkisi)
- Altın ETF akislari (GLD) Gold fiyatini ne kadar etkiliyor?
- Real yield ile iliski: TIPS yields dusunce Gold yukarı — bu M15 strateji icin nasil kullanilir?

Raporla:
- "DXY korelasyonu guvenilir ancak su durumlarda bozuluyor: ..."
- "Risk-off gun tespiti icin ek filtre gerekir mi?"
- Stratejist icin somut: "Haber gunleri ve risk-off donemlerde DXY-Gold iliskisi X oluyor"

---

## Not

Bu dosyadaki Python kod ornekleri Gold/MT5'e ozeldir (sembol: "GOLD", TP hedefleri 3/5/8 USD MilaGold'un kendi yapisidir). Baska bir enstruman icin kullanilacaksa kod buna gore uyarlanmalidir — bu dosya sadece Gold icin bir referanstir, genel Arastirmaci sistem promptunun bir parcasi degildir.
