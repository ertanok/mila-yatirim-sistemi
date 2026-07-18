=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-16
HEDEF AGENT        : Arastirmaci
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\arastirmaci_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — Strateji Ailesi Plani, ADIM 0 EK
TARAMA, M5-DONEM DOGRULAMASI

GOREV              : **Bu da bir tam Yol1 pipeline turu DEGILDIR** (Adim 0 ve Adim 0 EK
Tarama/Pivot-Kanal gorevleri gibi). Arastirmaci-duzeyinde, dar kapsamli bir DOGRULAMA
gorevidir — hipotez uretilmez, Stratejist'e devredilmez, sonuc dogrudan Orkestrator'a
raporlanir.

**Baglam/gerekce:** `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (14 Temmuz), S1
Sonucu ve Celiski Bulgusu bolumlerinde, H1→M5 ve M30→M5 giris kombinasyonlarinin (her iki
yon) S1 esigini (15x/20x) 0,9-3,7 saat araliginda gectigini bulmustu — Adim 0'in en iyi M15
adayindan (5,3-8,3 saat) belirgin daha hizli, Ertan'in "dakikalar-birkac saat" scalping
tanimina en net uyan aday. Ancak raporun kendisi bu bulguyu ACIKCA "kirilgan/dar-kanitli"
olarak isaretledi (bkz. rapor, "Celiski Bulgusu" bolumu, madde: ortusen yapisal kanal sayisi
sadece 2-8; M5 verisi MT5 `copy_rates_from_pos`/`maxbars=100000` sinirindan sadece ~17 ay
[2025-02-11→2026-07-13] kapsiyor) ve "Onerilen Sonraki Adim" bolumunde (madde 3) BIZZAT KENDISI
su dogrulamayi onerdi: "M5 verisinin farkli/daha genis bir donemde (mumkunse broker/veri
kaynagi degistirilerek veya ileri tarihte tekrar) DOGRULANMASI, M5-giris bulgusunun
donem-etkisi mi yoksa kalici bir ozellik mi oldugunu ayirt etmek icin faydali olabilir."

Bu gorev, Arastirmaci'nin kendi onerdigi bu dogrulamayi gerceklestirir.

**Somut gorev tanimi:**

1. **Daha genis/farkli bir M5 veri donemi elde etmeyi dene.** Mevcut tarama
   `mt5.copy_rates_from_pos` ile en son ~99.999 bari (~17 ay) cekmisti. Once şunu arastir/dene:
   - `mt5.copy_rates_range(...)` ile daha eski bir tarih araligini (orn. 2020-2024 arasi bir
     dilim) dogrudan istemek, `maxbars` sinirini asabilir mi? (Bu sinirin `copy_rates_from_pos`'a
     mi yoksa terminal/broker geçmişinin kendisine mi ait oldugunu netlestir — rapor bu ikisini
     ayirt etmemisti.)
   - Broker/terminalin GOLD icin M5 gecmisinin gercekte ne kadar geriye gittigini once teyit et
     (orn. `copy_rates_range` ile cok eski bir tarih isteyip donen ilk barin tarihine bak).
   - Eger teknik olarak daha genis/farkli bir M5 donemi elde edilemiyorsa (broker gecmisi
     gercekten ~17 ayla siniirliysa), bunu bir BULGU olarak rapor et — "veri yok, dogrulama
     yapilamiyor" gecerli bir sonuctur, konuyu genisletme.
2. **Elde edilebilirse, AYNI pivot/kanal + M5-giris metodolojisini (rapordaki TAM FORMUL,
   degistirmeden — swing N=5 fraktal, >=3 dokunus, EMA50/EMA200 + MACD 12/26/9 teyidi, 0,5xATR14
   tolerans) farkli/daha genis M5 donem uzerinde tekrar calistir** (H1→M5 ve M30→M5, her iki
   yon — ayni 4 kombinasyon).
3. **Yeni donemde S1-gecis suresini (15x/20x esigi) olc** ve mevcut ~17 aylik donemin sonucuyla
   (0,9-3,7 saat araligi) DOGRUDAN KARSILASTIR:
   - Ayni mertebede mi (donem-bagimsiz, kalici bir ozellik olabilir)?
   - Farkli mertebede mi (donem-etkisi/rejim-bagimliligi isareti)?
   - Ortusen yapisal kanal sayisi bu yeni donemde de kucuk mu (2-8), yoksa daha genis veri
     daha fazla kanal mi veriyor (istatistiksel guc artisi)?
4. **Sinirlamalari acikca belirt** — orneklem buyuklugu (yeni donemde kac kanal), veri kaynagi
   degisikligi varsa (orn. farkli broker) bunun getirdigi ek belirsizlik (spread/fiyat farki),
   rejim degisikligi riski.
5. Bu bir "celiski cozuldu/cozulmedi" KARARI degildir — sadece dogrulama sonucunu ham olarak
   raporla, yorum Orkestrator'a/Stratejist asamasina aittir.

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (asil bulgu ve
  TAM FORMUL — bu gorev metodolojiyi DEGISTIRMEDEN, sadece veri donemini degistirerek tekrar
  uygular)
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama.py` (ana tarama scripti —
  veri-cekme kismi disinda DEGISTIRILMEDEN yeniden kullanilabilir)
- `C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` (S1 tanimi, 15-20x esigi —
  degismedi)

ONCEKI ADIMIN CIKTISI: `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`
(bu gorev, o raporun KENDI ONERDIGI dogrulama adimidir — S1 Sonucu ve Celiski Bulgusu
bolumlerini gecersiz kilmaz, kirilganligini azaltmaya/artirmaya calisir)

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Baska bir dahili sistemin (MilaGold/Lisa/Signal
GPT) bulgu/veri/parametresine/format-sablonuna erisim veya atif YOKTUR. Tek veri kaynagi
XM/MT5 (veya rapor edilecek sekilde farkli bir harici fiyat verisi kaynagi, eger MT5 yetersiz
kalirsa) ham OHLCV verisidir. Calisma dizini yalniz `C:\MilaYatirim\Justin\` altindadir.

BEKLENEN CIKTI     : Markdown rapor,
`C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_raporu.md`.
Bolumler: Ozet, Veri Donemi Tespiti (ne kadar genis/farkli donem elde edilebildi, nasil),
Yontem (rapor ile ayni oldugunu teyit), Sonuclar (yeni donem vs mevcut ~17 ay karsilastirmasi),
Sinirlamalar, Izolasyon Notu.

ONAY NOKTASI       : Bilgi notu — bu gorev salt-arastirma/dogrulama niteliginde, canli
sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki
yok (Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu degil, etki
alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez.
Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi dusulecek (10
Temmuz kurali geregi).

SAYAC NOTU: Bu gorev gunluk pipeline dongu sinirina (5/gun, Stratejist cagrisi = 1 tur)
SAYILMAZ — Stratejist bu asamada devrede degildir. Aile-bazli RED sayacina da sayilmaz.

NOT — BAGIMSIZLIK: Bu gorev, ayni oturumda Orkestrator tarafindan baslatilan DIGER bir gorevle
(ic-ice kanal/devam-orani metodolojisi dogrulamasi, ayri dosya) BAGIMSIZDIR — iki gorevin
sonuclari birbirine karistirilmamali, ayri raporlar olarak kalmalidir.
