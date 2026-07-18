# RISK ANALISTI HESAPLAMA RAPORU — Justin / Gold Scalping
# "Gecmis Calisma/Cerceve" Eksik Parametreleri: Kasa + Risk Yuzdesi + Lot Kurali

Tarih: 14 Temmuz 2026
Statu: ONERI / PROPOSAL — kalici justin_gecmis_calisma.md DEGILDIR. Ertan onayindan sonra
Orkestrator kalici cerceve dosyasini ayrica olusturacaktir.
Girdi dosyalari (yalniz C:\MilaYatirim\Justin\ icinden):
- arastirmaci_gold_scalping_raporu.md (BULGU 1: saatlik M5 range; BULGU 2: spread; BULGU 8: gap)
- stratejici_raporu_justin_gold_scalping_20260711.md (Bolum 4: onceki taslak, WR=1/(1+RR) formulu)

SABIT (Ertan tarafindan verildi, bu raporda degistirilmedi):
- HEDEF_PF = 1,5
- HEDEF_DD = %20 (maksimum, toplam donem bazinda)

BELIRSIZLIK: R:R orani henuz secilmedi (Backtest Muhendisi tarayacak). Bu nedenle asagidaki
oneri, uc R:R senaryosunun (1:1, 1:2, 2:1) TAMAMINDA guvenli kalacak sekilde (robust)
turetilmistir — tek bir senaryoya optimize edilmemistir.

---

## VARSAYIMLAR (acikca listelenmistir — sonuclar "bu varsayimlar altinda" gecerlidir)

| # | Varsayim | Kaynak/Gerekce |
|---|---|---|
| V1 | GOLD sozlesme parametreleri: contract_size=100 (ons/lot), point=0.01 USD | Arastirmaci raporu basligi (MT5'ten okunan deger); XM "GOLD" spot metal standart degeri |
| V2 | 0,01 lot icin puan degeri = 0,01 lot x 100 ons x 0,01 USD = 0,01 USD/puan (100 puan = 1 USD) | V1'den aritmetik |
| V3 | Islem-basi risk, kasanin sabit YUZDESI olarak tanimlanir (kayipta kasa kuculdukce dolar-riski de kuculur — bilesik model) | Standart fractional-risk modeli |
| V4 | Binom DD modeli: islemler bagimsiz, kayip olasiligi sabit = 1-WR; DD asimi yalniz ARDISIK kayip dizisiyle modellenir | Gorev tanimindaki basit model; SINIRLARI asagida ayrica belirtildi |
| V5 | Degerlendirme ufku T = 500 islem (scalping'de gunde ~5-10 islem varsayimiyla kabaca 2-5 ay) | Varsayim — islem frekansi henuz olculmedi, Backtest Muhendisi netlestirecek |
| V6 | WR degerleri, PF=1,5'i tam saglayan TEORIK degerlerdir; gercek WR bilinmiyor. Robustluk kontrolu icin WR'nin kirilma noktasina (PF=1,0) dusmesi senaryosu da ayrica hesaplandi | Temkin ilkesi |
| V7 | Saatlik volatilite degerleri sunucu-saati eslemesine dayanir (GMT+3 varsayimi, DST dogrulanmadi — arastirmaci raporu ACIK SORULAR 1) | Arastirmaci raporu BULGU 1 SINIR notu |

---

## ADIM 1 — PF=1,5 icin GEREKLI WR (uc R:R senaryosu)

### Formulun turetilmesi

N islem, WR kazanma orani, islem-basi risk R (dolar), odul:risk orani r olsun.
- Brut kar  = WR x N x (r x R)
- Brut zarar = (1-WR) x N x R
- PF = brut kar / brut zarar = (WR x r) / (1-WR)

PF'yi cozersek:
- PF x (1-WR) = WR x r
- PF = WR x (r + PF)
- **WR = PF / (r + PF)**  ... (dogrulama: PF=1 icin WR = 1/(1+r) — Stratejist Bolum 4'teki
  kirilma-noktasi formulu WR=1/(1+RR) ile birebir ayni, tutarli.)

### Sayisal sonuclar (HEDEF_PF = 1,5)

| Senaryo | r (odul:risk) | Gerekli WR = 1,5/(r+1,5) | Kirilma WR (PF=1) = 1/(1+r) | Marj |
|---|---|---|---|---|
| A) R:R = 1:1 | 1,0 | 1,5/2,5 = **%60,0** | %50,0 | +10,0 puan |
| B) R:R = 1:2 | 2,0 | 1,5/3,5 = **%42,9** | %33,3 | +9,5 puan |
| C) R:R = 2:1 | 0,5 | 1,5/2,0 = **%75,0** | %66,7 | +8,3 puan |

Yorum: PF=1,5 hedefi, her senaryoda kirilma noktasinin ~8-10 puan uzerinde WR gerektiriyor.
Kayip OLASILIGI acisindan en agir senaryo B'dir (kayip orani 1-0,429 = %57,1) — ardisik kayip
serileri en cok bu senaryoda uzar; robust risk yuzdesi B'ye (ve B'nin bozulmus haline, V6) gore
secilmelidir.

---

## ADIM 2 — %20 DD'yi ASMA OLASILIGI (basit binom / ardisik-kayip modeli)

### 2a) %20 DD'ye ulasmak icin gereken ardisik kayip sayisi (N_breach)

Bilesik modelde (V3) N ardisik kayip sonrasi kasa = (1-p)^N. %20 DD asimi kosulu:
(1-p)^N <= 0,80  →  N >= ln(0,80)/ln(1-p)

| Islem-basi risk p | N_breach (bilesik) | N_breach (basit toplama, 20/p) |
|---|---|---|
| %0,5 | ln0,8/ln0,995 = 44,5 → **45 kayip** | 40 |
| %1,0 | ln0,8/ln0,99 = 22,2 → **23 kayip** | 20 |
| %2,0 | ln0,8/ln0,98 = 11,0 → **12 kayip** | 10 |

(Asagida bilesik degerler kullanildi; basit-toplama degerleri daha muhafazakar bir alt sinir
olarak tabloda birakildi.)

### 2b) T=500 islemde en az bir kez N_breach uzunlugunda kayip serisi gorme olasiligi

Yaklasim: seri-baslangici beklenen sayisi E ≈ T x WR x (1-WR)^N; P ≈ 1 - e^(-E)
(kayip serisinin bir kazancla baslamasi kosulu WR carpani ile; standart yaklasik formul).

| Senaryo (WR / kayip orani L) | p=%0,5 (N=45) | p=%1 (N=23) | p=%2 (N=12) |
|---|---|---|---|
| A) 1:1 (0,600 / 0,400) | ~0 (L^45≈1e-18) | %0,00002 (L^23=7,0e-10) | **%0,5** (L^12=1,68e-5) |
| B) 1:2 (0,429 / 0,571) | ~0 (L^45≈1e-11) | **%0,055** (L^23=2,6e-6) | **%22,9** (L^12=1,21e-3; E=0,26) |
| C) 2:1 (0,750 / 0,250) | ~0 | ~0 (L^23≈1e-14) | %0,002 (L^12=6,0e-8) |

### 2c) Robustluk kontrolu (V6): strateji hedefe ulasamaz, WR kirilma noktasina duserse?

En kotu makul durum: senaryo B'de WR %42,9 yerine ~%33-35'e duser (PF≈1,0 civari, strateji
"basabas" calisiyor). WR=0,35 / L=0,65 alirsak:

| p | N_breach | L^N | E = 500 x 0,35 x L^N | P(DD>%20) |
|---|---|---|---|---|
| %1 | 23 | 0,65^23 = 5,0e-5 | 0,0087 | **~%0,9** |
| %2 | 12 | 0,65^12 = 5,7e-3 | 0,996 | **~%63** |

### 2d) Sonuc — hangi kombinasyon riskli, hangisi guvenli

- **p=%2: RISKLI.** Senaryo B'de (R:R=1:2, hedef WR ile bile) 500 islemde %20 DD asma olasiligi
  ~%23; WR kirilma noktasina duserse ~%63. R:R belirsizken kabul edilemez.
- **p=%1: GUVENLI (robust).** Uc senaryonun ucunde de <%0,1; bozulmus-WR stres testinde bile
  ~%0,9. R:R hangi degerde secilirse secilsin %20 DD sinirina genis pay birakir.
- **p=%0,5: ASIRI GUVENLI.** DD riski pratikte sifir, ancak buyume yariya iner VE (Adim 3'te
  gorulecegi gibi) 0,01 lot sabitken SL butcesini volatilite-gurultusunun altina iter — yani
  guvenligi baska bir riski (erken SL suprulmesi) buyuterek satin alir.

### ONEMLI SINIR (modelin bilincli eksigi)
Binom/ardisik-kayip modeli DD'yi OLDUGUNDAN KUCUK gosterir: gercek drawdown'lar yalniz kesintisiz
kayip serilerinden degil, arada kucuk kazanclarla kesilen uzun kayip AGIRLIKLI bolgelerden de
olusur (orn. 30 islemde 22 kayip + 8 kazanc da %20'ye yaklasabilir). Bu nedenle "guvenli" secim,
tablodaki olasiligi dusuk TUTMAKLA kalmayip senaryolar arasinda buyuk pay birakan p=%1'dir;
p=%2'nin senaryo-B'deki %23'u, gercek (karisik-dizi) modelde daha da yuksek olurdu. Kesin DD
dagilimi Backtest Muhendisi'nin Monte Carlo'suyla (tam islem logu uzerinde) dogrulanmalidir.

---

## ADIM 3 — SL MESAFESI vs VOLATILITE GURULTUSU (0,01 lot SABIT varsayimiyla)

### Puan degeri (V1, V2)
0,01 lot GOLD: 1 puan = 0,01 USD → risk butcesi R$ dolar ise SL mesafesi = R$ / 0,01 = 100 x R$ puan.

### Volatilite referansi (arastirmaci BULGU 1, en volatil saat = sunucu saati 16)
- M5 medyan bar range: 573 puan
- M5 P90 bar range: 1.346 puan
- (En sakin saat 23: medyan 197 puan — dagilimin alt ucu, kontrol icin)

Kriter: SL, EN VOLATIL saatte bile TEK bir "buyuk" M5 barinin (P90) icinde suprulmemeli —
yani SL mesafesi >= ~1.346 puan olmali; medyanin en az ~2 kati olmasi da ek bir saglik kosulu.

### Kasa/risk kombinasyonlarinin SL butcesi (0,01 lot sabit)

| Kasa | p=%0,5 | p=%1 | p=%2 |
|---|---|---|---|
| 1.000 USD | 5 USD → 500 puan (P90'in ALTINDA — YETERSIZ) | 10 USD → 1.000 puan (P90'in altinda — SINIRDA/YETERSIZ) | 20 USD → 2.000 puan (yeterli ama Adim 2'de p=%2 elendi) |
| 1.500 USD | 750 puan — YETERSIZ | 15 USD → 1.500 puan (P90 x1,11 — dar pay) | 3.000 puan (p=%2 elendi) |
| **2.000 USD** | 1.000 puan — YETERSIZ | **20 USD → 2.000 puan (P90 x1,49; medyan x3,5) — YETERLI** | 4.000 puan (p=%2 elendi) |

Kontroller (kasa=2.000, p=%1, SL butcesi 2.000 puan):
- En volatil saat P90 barinin 1,49 kati, medyaninin 3,49 kati → tek bar gurultusuyle suprulme
  olasiligi dusuk ("bu varsayimlar altinda"; intrabar fitil dagilimi ayrica olculmedi).
- Spread payi: tipik spread 44-59 puan (BULGU 2) → SL'in ~%2-3'u. Makul; SL'in anlamli bir
  kismini maliyet yemiyor.
- ATR-bazli SL uyumu: H1'in ATR-bazli 1:1 baslangic onerisi buyuk olasilikla 1-2 x ATR(M5)
  mertebesinde (kabaca birkac yuz puan) SL uretecektir — 2.000 puanlik risk BUTCESI bunun
  ustunde kaldigi icin kisit olusturmaz. NOT: SL butcesi bir UST SINIRDIR; Backtest Muhendisi
  daha dar (orn. ATR-bazli 600 puan) SL secerse fiili islem riski %1'in ALTINA duser (600 puan
  x 0,01 USD = 6 USD = kasanin %0,3'u) — bu, kurali ihlal etmez, temkin yonunde sapmadir.
- Hafta sonu gap stres testi (BULGU 8): gozlenen maksimum gap 8.531 puan → 0,01 lotta 85,31 USD
  = kasanin ~%4,3'u. Yikici degil, ancak %1'lik islem-riskinin ~4 kati — hafta sonu pozisyon
  tasimama filtresi (arastirmaci Aday 4) ayrica onerilir; bu, SL'in yerini almaz (gapte SL
  calismayabilir — genel operasyonel bilgi).

Sonuc: 0,01 lot sabitken hem Adim 2'nin DD kosulunu hem Adim 3'un gurultu kosulunu ayni anda
saglayan en kucuk yuvarlak kombinasyon: **kasa 2.000 USD + risk %1**. Daha kucuk kasa, %1'de
SL'i gurultuye gomuyor; %2'ye cikmak DD tarafinda robustlugu bozuyor; %0,5'e inmek her kasada
SL'i yetersiz birakiyor (0,01 lot sabit kaldikca).

---

## ADIM 4 — SOMUT TEK ONERI (aralik degil, net sayilar)

Bu varsayimlar (V1-V7) ve SABIT hedefler (PF=1,5; max DD %20) altinda:

1. **Kasa buyuklugu: 2.000 USD** (Justin'e ayrilacak ayri XM hesabinin baslangic bakiyesi).
2. **Islem-basi risk: %1** — islem basina maksimum risk = kasa x 0,01 (baslangicta 20 USD).
   Bu bir UST SINIRDIR: SL mesafesi x puan degeri hicbir islemde bu tutari asamaz.
3. **Lot kurali:**
   - Baslangic lotu: **0,01 lot (sabit)**.
   - Risk-tutarlilik formulu: lot = (kasa x 0,01) / (SL_puan x 1 USD/puan-per-lot),
     asagi yuvarlanir, taban 0,01 lot. (Ornek: kasa 2.000, SL 2.000 puan → 20/2.000 x 1 lot
     = 0,01 lot.)
   - Olceklendirme: **her tam 2.000 USD kasa = 0,01 lot** (2.000-3.999 USD → 0,01;
     4.000-5.999 USD → 0,02; ...). Kasa 2.000 USD'nin altina duserse lot 0,01'de kalir
     (minimum lot), ancak bu durumda fiili risk yuzdesi %1'i asmaya baslar — kasa
     1.600 USD'ye (baslangictan -%20, HEDEF_DD) dustugunde islem zaten durmus olmalidir
     (DD-stop, asagida).
4. **Operasyonel DD-stop (HEDEF_DD'nin uygulamasi):** kumulatif drawdown %20'ye (kasa
   1.600 USD'ye) ulasirsa islem DURUR (STOP otomatik olabilir); yeniden baslama Ertan
   onayina baglidir. Bu, MilaGold'dan bagimsiz, HEDEF_DD sabitinin dogrudan sonucudur.

### Gerekce ozeti (neden bu uclu, tek cumleyle her biri)
- %1 risk: R:R belirsizligine karsi tek robust deger — uc senaryoda da (ve WR'nin kirilmaya
  dustugu stres testinde de) %20 DD asma olasiligi <~%1; %2 senaryo B'de %23-63'e firliyor.
- 2.000 USD kasa: 0,01 lot + %1 riskin SL butcesini (2.000 puan) en volatil saatin P90 bar
  range'inin (1.346 puan) uzerine cikaran en kucuk yuvarlak kasa.
- Lot kurali: risk yuzdesini kasa buyudukce sabit tutan dogrusal olcek; baslangicta tek
  serbestlik derecesi (0,01 lot) ile basit ve denetlenebilir.

---

## SINIRLAR / SONRAKI ADIMLARA NOTLAR

1. Binom modeli karisik-dizi drawdown'larini kucumser (Adim 2d) — Backtest Muhendisi tam islem
   logu uzerinde Monte Carlo DD dagilimi uretmeli (Hipotez 1 turundeki eksikligin tekrari
   onlenmeli).
2. T=500 islem ufku bir varsayimdir (V5); gercek islem frekansi backtest'ten cikinca tablolar
   ayni formullerle guncellenebilir (P, T ile yaklasik dogrusal buyur: T=1.000'de olasiliklar
   kabaca 2 katina cikar — p=%1 icin hala <%2, sonuc degismez).
3. Saat-16 volatilite referansi DST/sunucu-saat eslemesi varsayimina dayanir (V7) — Backtest
   Muhendisi'nin her turda yaptigi saat-esleme dogrulamasi burada da gecerli; esleme kayarsa
   "en volatil saat" etiketi kayar ama P90 buyuklugu (dagilimin ust ucu) benzer kalir, sonuc
   niteliksel olarak degismez.
4. R:R taramasi sonuclaninca (Backtest Muhendisi), secilen r icin gerekli WR (Adim 1 formulu)
   ve fiili SL mesafesi netlesecek; bu rapordaki degerler o zaman TEK senaryoya gore yeniden
   siklastirilabilir (orn. r=0,5 secilirse %1 riskin cok muhafazakar kaldigi gorulebilir —
   ama baslangic icin robust taraf tercih edilmistir).
5. Kasa 2.000 USD onerisi Ertan'in sermaye tahsis kararidir — matematiksel alt sinir, %1 risk
   + 0,01 lot + P90 kosulundan gelen ~1.400 USD'dir; 2.000 USD bunun uzerine yuvarlak ve payli
   secilmistir. Ertan daha buyuk kasa onaylarsa formuller aynen gecerli kalir (SL butcesi
   genisler, robustluk artar).

---

## IZOLASYON NOTU

- Bu hesaplama sirasinda MilaGold/Lisa/Signal GPT'ye ait hicbir dosya (stratejici_gold_gecmis_
  calisma.md, milagold_trades.json, lisa_performance.json, positions_status.json, signal.json
  vb.) ACILMADI veya referans ALINMADI.
- Kasa (2.000 USD), risk (%1) ve lot kurali (her 2.000 USD = 0,01 lot) degerleri MilaGold'un
  kendi parametrelerinden TURETILMEDI — tamamen bu rapordaki bagimsiz zincirden geldi:
  HEDEF_PF/HEDEF_DD sabitleri + binom DD modeli + arastirmaci raporunun kendi MT5 olcumleri
  (BULGU 1/2/8) + GOLD sozlesme aritmetigi (V1-V2).
- Kullanilan tek dis-borular: Ertan'in verdigi sabitler (PF=1,5; DD %20) ve Justin dizinindeki
  onceki pipeline raporlari.
- Calisma yalniz C:\MilaYatirim\Justin\ dizininde yapildi (girdi: arastirmaci_gold_scalping_
  raporu.md, stratejici_raporu_justin_gold_scalping_20260711.md; cikti: bu dosya).

## ONAY NOKTASI

Bu dosya bir ONERIDIR (bilgi notu kategorisi — canli sisteme/hesaba dokunus yok). Kalici
justin_gecmis_calisma.md dosyasinin olusturulmasi ve ozellikle 2.000 USD kasanin fiilen
tahsisi Ertan'in acik onayini gerektirir; onay sonrasi dosyayi Orkestrator olusturacaktir.
