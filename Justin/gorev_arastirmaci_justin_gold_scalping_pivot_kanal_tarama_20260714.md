=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-14 (Ertan'in Adim 0 raporuna 3-soru geri bildirimi uzerine)
HEDEF AGENT        : Arastirmaci
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\arastirmaci_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — Strateji Ailesi Plani, ADIM 0
EK TARAMASI (Ertan'in Adim 0 raporuna Soru 2 + Soru 3 geri bildirimi)

GOREV              : **Bu da bir tam Yol1 pipeline turu DEGILDIR** (Adim 0'in kendisi gibi).
Arastirmaci-duzeyinde, dar kapsamli bir EK on-tarama gorevidir — hipotez uretilmez,
Stratejist'e devredilmez, sonuc dogrudan Orkestrator'a raporlanir.

**Baglam/gerekce (neden bu gorev var):** Ertan, `arastirmaci_gold_scalping_adim0_tarama_
raporu.md`'yi degerlendirdi ve iki noktayi acikca ayirt etti:
1. Adim 0'in olctugu sey (lag-1..N otokorelasyon, varyans-orani, N-bar-streak-sonrasi-devam
   orani — HEPSI "bar-bar istatistik") ile Ertan'in tarif ettigi "yapisal/kanal-tabanli
   trend-takip" (>=3 dokunus + EMA/MACD teyidi, haftalarca surebilen) FARKLI mekanizmalardir.
2. Adim 0'in bar-bar istatistigi HICBIR surekliligi/momentum isareti VERMEDI (aksine hafif
   tersine-donus isareti verdi — bkz. Adim 0 raporu OZET madde 2, A.2-A.5). Ama yapisal/
   kanal-tabanli surekliligi Adim 0 hic TEST ETMEDI — bu, "A (Momentum) ailesi olu" sonucuna
   varmak icin YETERLI DEGIL, cunku hic denenmemis farkli bir mekanizma var.

Ertan'in acik talimati: **ONCE yapisal/kanal-tabanli surekliligi test et** (bar-bar
otokorelasyonu tekrar test etmek degil). Ayrica: ana trend tespiti icin H4'u BIRAK, H1/M30
(pivot-tabanli: dokunus sayimi + EMA/MACD teyidi) kullan; giris zamanlamasi icin M15/M5'i
AYRICA test et.

**Somut gorev tanimi:**

1. **Pivot/kanal tanimi (yazili, deterministik, yeniden-uretilebilir olmali — rapor icinde
   TAM FORMUL belirtilecek):**
   - Pivot noktalarini (swing high / swing low) somut bir yontemle tanimlayin (orn. N-bar
     sol + N-bar sag pencerede lokal ekstremum / fraktal tanimi, veya esik-tabanli ZigZag —
     hangisini kullandiginizi ve N/esik degerini ACIKCA yazin; bu bir on-tarama, optimizasyon
     DEGIL — makul/standart bir baslangic degeri secin, taramayi bu deger uzerinde
     optimize etmeye CALISMAYIN, bu S2/anti-overfitting protokolunun tam-tur asamasina aittir).
   - Bir trend-kanali "gecerli/yapisal" sayilmasi icin **>=3 dokunus** kriteri: fiyatin ayni
     trend-cizgisine/kanal sinirina en az 3 kez yaklasip (ilk olusum + en az 2 ek dokunus)
     tekrar trend yonunde donmesi. Dokunus tanimini (mesafe/tolerans esigi) acikca yazin.
   - **EMA/MACD teyidi:** hangi EMA periyodu/periyotlari (orn. EMA50/EMA200 yon uyumu) ve
     hangi MACD parametreleri (standart 12/26/9 ile baslayin) kullanildigini acikca belirtin.

2. **Ana trend tespiti — H1 VE M30 (H4 KULLANILMIYOR bu turde, Ertan'in acik talimati):**
   Yukaridaki pivot/kanal tanimiyla, GOLD'da H1 ve M30 ufuklarinda boyle bir yapisal trend/
   kanalin ne siklikta olustugunu, ortalama/medyan SURESINI (gercekten haftalarca surebiliyor
   mu, yoksa cok daha kisa mi), ve trend YONUNDE devam oranini olcun. Bu, Adim 0'daki
   "bar-bar" tanimindan farkli olarak "yapisal trend tanimlandiktan SONRA fiyat trend
   yonunde ilerlemeye devam ediyor mu, ne kadar/ne sure" sorusuna cevap vermelidir.

3. **Giris zamanlamasi — M15/M5 AYRICA test edilecek:** H1/M30'da tespit edilen yapisal
   trend/kanal icinde, M15/M5 seviyesinde somut bir giris tetigi tanimlayin (orn. kanal
   sinirina geri-donusten sonraki M15/M5 mum kapanisi, veya pivot-teyidi sonrasi ilk N bar).
   Bu girisin sonraki hareketini (S1 icin gerekli hedef puanlari acisindan) Adim 0'daki AYNI
   yontemle (gercek N-bar-ileri |kapanis farki| medyani / maliyet) olcun — karsilastirilabilir
   olmasi icin metodoloji Adim 0 ile tutarli tutulmalidir.

4. **S1 on-kontrolu (zorunlu, esik DEGISMEDI — bkz. asagida):** Bu yeni yapisal/kanal-tabanli
   + M15/M5-giris kombinasyonunun hedef/maliyet orani, `justin_backtest_onkontrol_
   standardi.md` Madde 2'deki **15-20x esigini** (bu esik bu turde DEGISTIRILMEDI — Orkestrator
   Ertan'in ayri Soru 1'ine kendi degerlendirmesiyle cevap verdi, esigi gevsetme karari
   VERILMEDI, bkz. `orkestrator_yanit_3soru_justin_20260714.md`) hangi tutma suresinde
   gectigini olcun. Bu tutma suresinin scalping karakterini ("dakikalar-birkac-saat",
   Ertan'in Cevap-3 tanimi) koruyup korumadigini AYRICA VE ACIKCA raporlayin — Adim 0'daki
   "Celiski Bulgusu" formatinda: celiski varsa KARAR VERMEYIN, acik bulgu olarak isaretleyip
   raporlayin.

5. **C-notu (opsiyonel, gozlemsel):** Kanal siniri kirildiginda (yapisal trendin BOZULMASI)
   ne oldugu hakkinda bir gozlemsel not ekleyebilirsiniz (ayri hipotez/model KURMAYIN, Adim 0
   ile tutarli sekilde sadece not).

6. **Veri araligi ve DST notlari:** Adim 0'daki veri-araligi-asimetrisi sinirlamasi (M15
   ~4,25 yil vs H1/H4 ~25 yil, MT5 `maxbars=100000` sinirindan) bu turde de gecerli olabilir
   (M30 verisinin kapsadigi donemi de ayrica raporlayin). DST/saat-eslesme dogrulamasi bu
   turde (on-tarama, tam backtest degil) ZORUNLU degildir ama Adim 1/tam-backtest asamasinda
   BAGIMSIZ dogrulanmasi gerektigini hatirlatma olarak rapora ekleyin (`justin_backtest_
   onkontrol_standardi.md` Madde 1).

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` (S1 tanimi, Madde 2 — esik
  DEGISMEDI, bkz. gorev Madde 4)
- `C:\MilaYatirim\Justin\justin_gecmis_calisma.md` (baglam icin, bu turde dogrudan
  kullanilmiyor)
- `C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md` (Cevap 3
  — scalping karakteri korunmali, S1-vs-SL/TP gerilimi)
- `C:\MilaYatirim\Justin\orkestrator_yanit_3soru_justin_20260714.md` (bu gorevi dogrudan
  tetikleyen Orkestrator degerlendirmesi — Ertan'in 3 sorusuna verilen cevap, ozellikle
  Soru 2/Soru 3 bolumu)

ONCEKI ADIMIN CIKTISI: `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_adim0_tarama_
raporu.md` (bu gorev, o raporun DEVAMI/TAMAMLAYICISIDIR — ayni "Adim 0" asamasinda, farkli/
tamamlayici bir mekanizma test eder; Adim 0'in bar-bar bulgularini GECERSIZ KILMAZ, sadece
ayri bir mekanizmayi ayrica sinar).

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Baska bir dahili sistemin (MilaGold/Lisa/
Signal GPT) bulgu/veri/parametresine/format-sablonuna erisim veya atif YOKTUR. Tek veri
kaynagi XM/MT5 fiyat verisidir (dogrudan `MetaTrader5` kutuphanesi). Calisma dizini yalniz
`C:\MilaYatirim\Justin\` altindadir.

BEKLENEN CIKTI: Markdown rapor, `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_
kanal_tarama_raporu.md`. Bolumler: Ozet, Pivot/Kanal Tanimi (tam formul), H1/M30 Yapisal
Trend Bulgulari (siklik/sure/devam-orani), M15/M5 Giris-Zamanlama Bulgulari, S1 Sonucu,
**Celiski Bulgusu (varsa)**, C-Notu (varsa), Onerilen Sonraki Adim (aday listesi — KARAR
DEGIL), Sinirlamalar, Izolasyon Notu.

ONAY NOKTASI: Bilgi notu — bu gorev salt-arastirma/analiz niteliginde (on-tarama, hipotez/
karar uretmiyor), canli sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri
donulebilirlik tam, mali etki yok (Justin arastirma/demo asamasi, canli hesap yok), tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu
kategorisi, Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu +
Orkestrator_Loglar kaydi dusulecek (10 Temmuz kurali geregi).

SAYAC NOTU: Bu gorev gunluk pipeline dongu sinirina (5/gun, Stratejist cagrisi = 1 tur)
SAYILMAZ — Stratejist bu asamada devrede degildir. Aile-bazli RED sayacina da sayilmaz — bu
sayac Risk Analisti karariyla isler, bu turde Risk Analisti yoktur. Bu, Adim 0 gibi sadece
Arastirmaci-duzeyinde bir on-olcumdur.
