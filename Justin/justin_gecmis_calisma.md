# JUSTIN — GECMIS CALISMA / CERCEVE (Gold Scalping)

Statu: KALICI CERCEVE DOSYASI. Olusturan: Orkestrator, Ertan'in acik onayi uzerine (14 Temmuz
2026). Kaynak: `justin_gecmis_calisma_hesaplama_20260714.md` (Fable 5'in hazirladigi hesaplama/
oneri raporu — tam gerekce, varsayimlar, formuller ve hesaplamalar icin bkz. o dosya, burada
sadece sonuc degerleri ve kisa referanslar tekrarlanmistir).

**Izolasyon notu:** Bu dosyayi olustururken format/yapi referansi icin MilaGold'un
`stratejici_gold_gecmis_calisma.md` dosyasi ACILMISTIR — ama oradan hicbir icerik, sayi veya
format-kalibi buraya tasinmamistir: bu dosya yalniz Justin'e ait deger/karar icerir. Asagidaki
degerler MilaGold'un kendi parametrelerinden (200 USD kasa, gunluk %20 emniyet stopu vb.)
TURETILMEMISTIR — bagimsiz olarak HEDEF_PF/HEDEF_DD sabitleri + binom DD modeli + Justin'e ozel
arastirmaci bulgulari (M5 range, spread, gap) uzerinden hesaplanmistir (dogrulandi). Detay:
hesaplama raporu, "IZOLASYON NOTU" bolumu.

Bu dosya sistem promptuna dahil degildir; Justin/Gold Scalping pipeline'inda gorev alan
Stratejist ve diger agent'lar, iliskili bir gorevle karsilastiklarinda referans olarak buna basvurup
uzerine insa eder.

---

## Hedefler (Ertan tarafindan verilen sabitler)

- **HEDEF_PF = 1,5**
- **HEDEF_DD = %20** — bu deger **KUMULATIF/TOPLAM DONEM BAZINDADIR, GUNLUK DEGILDIR.**

> **ONEMLI NETLIK (14 Temmuz 2026, Ertan'in ozellikle istedigi ayrim):** Buradaki %20 DD,
> Justin/Gold Scalping'in baslangic kasasindan (2.000 USD) itibaren **kumulatif/toplam olarak**
> biriken dusustur — kasa herhangi bir anda baslangicin %20 altina (1.600 USD'ye) dustugunde
> devreye girer. Bu, **MilaGold'un GUNLUK (her gece 00:00'da sifirlanan) emniyet-stopuyla
> KARISTIRILMAMALIDIR** — MilaGold'daki %20, o gunun baslangic bakiyesine gore gunluk olcum;
> buradaki Justin %20'si ise gunluk sifirlanmaz, kasanin ilk baslangicindan (veya son
> yuvarlamadan) itibaren KUMULATIF olarak takip edilen tek, surekli bir esiktir. Iki mekanizma
> ayni isimle (%20 DD-stop) anilsa da FARKLI olcum birimlerine (kumulatif/toplam vs gunluk)
> sahiptir ve birbirinin yerine kullanilamaz.

## Kasa ve Risk Parametreleri

- **Baslangic kasasi: 2.000 USD** (Justin'e ayrilacak ayri XM hesabinin baslangic bakiyesi;
  MilaGold'un 200 USD baslangicindan tamamen bagimsiz).
- **Islem-basi risk: %1 (UST SINIR)** — islem basina maksimum risk = kasa x 0,01 (baslangicta
  20 USD). SL mesafesi x puan degeri hicbir islemde bu tutari asamaz. Backtest Muhendisi daha
  dar bir SL secerse fiili risk %1'in altina duser — bu, kurali ihlal etmez (temkin yonunde sapma).
- **Lot kurali:**
  - Baslangic lotu: **0,01 lot (sabit)**.
  - Risk-tutarlilik formulu: lot = (kasa x 0,01) / (SL_puan x 1 USD/puan-per-lot), asagi
    yuvarlanir, taban 0,01 lot.
  - Olceklendirme: **her tam 2.000 USD kasa = 0,01 lot** (2.000-3.999 USD → 0,01 lot;
    4.000-5.999 USD → 0,02 lot; ...).
  - Kasa 2.000 USD'nin altina duserse lot 0,01'de (taban) kalir; ancak bu durumda fiili risk
    yuzdesi %1'i asmaya baslar — bu asama zaten DD-stop esigine (kasa 1.600 USD, -%20 kumulatif)
    yakin/onunde gerceklesir, asagidaki DD-stop devreye girer.

## Operasyonel DD-Stop (HEDEF_DD'nin uygulamasi)

- Kumulatif drawdown **%20'ye (kasa 1.600 USD'ye) ulastiginda islem otomatik DURUR** (STOP,
  Orkestrator'un yetkisinde — bkz. Mimari Boyut B, STOP-genis kategorisi).
- **Yeniden baslama (START) her zaman Ertan'in acik onayini gerektirir**, otomatik degildir —
  bu, MilaGold'daki ayni STOP-otomatik/START-onayli kaliba birebir uyar, ayri bir istisna degildir.
- Tekrar: bu esik **GUNLUK SIFIRLANMAZ**; kasa iyilesip tekrar dusse bile olcum hep baslangic
  referansina (veya Ertan'in onayladigi bir sonraki yuvarlama noktasina) gore kumulatiftir.

---

## Hesaplama Raporunun Kisa Ozeti (detay icin bkz. `justin_gecmis_calisma_hesaplama_20260714.md`)

Yukaridaki sayilar, asagidaki zincirle turetilmistir (tam formuller/tablolar hesaplama
raporunda):

1. **PF=1,5 icin gerekli WR**, uc R:R senaryosunda (1:1 → %60,0; 1:2 → %42,9; 2:1 → %75,0)
   hesaplandi — R:R henuz Backtest Muhendisi tarafindan secilmedi, bu yuzden oneri robust
   (uc senaryoda da guvenli) sekilde turetildi.
2. **%20 kumulatif DD asma olasiligi** basit binom/ardisik-kayip modeliyle T=500 islemlik bir
   ufukta hesaplandi: p=%1 islem-basi risk uc senaryoda da <%0,1 (bozulmus-WR stres testinde
   bile ~%0,9) — p=%2 en agir senaryoda (%23-63) robustlugu bozdugu icin elendi, p=%0,5 asiri
   temkinli kalip SL'i volatilite gurultusune gomdugu icin elendi.
3. **SL butcesi vs volatilite gurultusu**: 0,01 lot sabitken, kasa=2.000 USD + risk=%1
   kombinasyonu, en volatil saatteki M5 P90 bar range'inin (1.346 puan) ustunde (2.000 puan)
   bir SL butcesi birakiyor — daha kucuk kasalar bu kosulu saglamiyor.
4. Sonuc: **kasa 2.000 USD + risk %1 + 0,01 lot baslangic + her 2.000 USD = 0,01 lot
   olceklendirme**, hem DD kosulunu hem gurultu kosulunu ayni anda saglayan en kucuk yuvarlak
   kombinasyon olarak secildi.

### Varsayimlar / Sinirlar (kisa referans — tam liste hesaplama raporunda V1-V7 ve "SINIRLAR" bolumu)

- **T=500 islem ufku bir varsayimdir** (gercek islem frekansi henuz olculmedi); T buyudukce
  olasiliklar kabaca dogrusal buyur ama p=%1 icin sonuc niteliksel olarak degismez.
- **Binom/ardisik-kayip modeli DD'yi oldugundan kucuk gosterir** — gercek drawdown'lar yalniz
  kesintisiz kayip serilerinden degil, arada kucuk kazanclarla kesilen "karisik dizi" uzun
  kayip-agirlikli bolgelerden de olusabilir. Kesin DD dagilimi Backtest Muhendisi'nin tam islem
  logu uzerindeki Monte Carlo'suyla ayrica dogrulanmalidir.
- **R:R orani henuz secilmedi** (Backtest Muhendisi tarayacak) — R:R netlesince Adim 1'deki
  WR gereksinimi ve fiili SL mesafesi yeniden siklastirilabilir; bu, yukaridaki kasa/risk/lot
  sayilarini gecersiz kilmaz (robust taraf zaten baslangic icin secildi).
- Saat-16 volatilite referansi DST/sunucu-saat eslemesi varsayimina dayanir; esleme kayarsa
  "en volatil saat" etiketi kayabilir ama sonuc niteliksel olarak benzer kalir.
- Kasa 2.000 USD, matematiksel alt sinirin (~1.400 USD) uzerine Ertan'in tercihiyle yuvarlanmis
  bir sermaye-tahsis kararidir; Ertan ileride daha buyuk kasa onaylarsa formuller aynen gecerli
  kalir (SL butcesi ve robustluk sadece genisler).

---

## Onay ve Durum

- Bu dosya, hesaplama raporundaki oneriyi Ertan'in 14 Temmuz 2026 tarihli onayi uzerine
  kalicilastirir (bkz. Ertan bildirimi: "Fable'in onerisini onayliyoruz" + DD'nin kumulatif/
  gunluk ayrimi netlestirme talebi — bu dosyada yukarida acikca islenmistir).
- **Faz 0 / Madde 1: TAMAMLANDI.** Detay ve Faz 0'in tum maddelerinin guncel durumu icin bkz.
  `justin_gold_scalping_karar_ve_governance_20260714.md`.
- Faz 1 (Stratejist v6 turu / Arastirmaci gorevi) bu dosyanin olusturulmasiyla ayri bir
  onay/tetikleme olmadan BASLATILMAZ — Faz 1'in baslatilmasi icin Orkestrator ayrica
  gorevlendirilmelidir.
