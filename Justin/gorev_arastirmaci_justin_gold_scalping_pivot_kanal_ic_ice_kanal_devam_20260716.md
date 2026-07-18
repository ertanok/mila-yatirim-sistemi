=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-16
HEDEF AGENT        : Arastirmaci
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\arastirmaci_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — Strateji Ailesi Plani, ADIM 0 EK
TARAMA, IC-ICE KANAL METODOLOJI SORUSU (devam-orani olcum yontemi)

GOREV              : **Bu da bir tam Yol1 pipeline turu DEGILDIR.** Arastirmaci-duzeyinde,
yeni bir METODOLOJI sorusunu test eden dar kapsamli bir EK olcum gorevidir — hipotez
uretilmez, Stratejist'e devredilmez, sonuc dogrudan Orkestrator'a raporlanir.

**Baglam/gerekce:** `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (14 Temmuz),
"H1/M30 Yapisal Trend Bulgulari" bolumunde "Onay-sonrasi trend-yonunde-devam orani" olcumu
tanimliydi: onaylanmis bir H1/M30 kanalindan 1/3/7/14 gun sonra **fiyatin hala trend yonunde
ilerde olup olmadigi** (kanalin kirilip kirilmadigina degil, o sabit zaman noktasindaki
konumuna bakiyor). Sonuc %13-80 arasinda TUTARSIZ/monotonik-olmayan cikti (rapor, madde 3 ve
5; ONERILEN SONRAKI ADIM madde 5).

**Yeni soru (bu gorevin konusu):** Bu tutarsizligin bir nedeni, olcumun sadece TEK bir
zaman-dilimini/kanal genisligini (H1/M30 kanalinin kendisini) esas almasi olabilir. Gercekte
genis (H1/M30) kanal ana trendi korurken, o kanalin ICINDE daha kisa vadeli (M15/M5) kendi
alt-kanallari/kisa ters-yon hareketleri olusabilir — bunlar ana trendin BOZULMASI degil, dogal
bir parcasi (ic-ice/nested yapisi) olabilir. Mevcut 1/3/7/14-gun "fiyatin konumu" olcumu, ana
kanal hala saglamken ICERIDE olusan boyle bir kisa ters-alt-kanali "basarisizlik/devamsizlik"
olarak yanlislikla sayiyor olabilir.

**Somut gorev tanimi:**

1. **Ayni pivot/kanal tanimini (TAM FORMUL — rapordaki N=5 fraktal swing, >=3 dokunus,
   EMA50/EMA200 + MACD 12/26/9 teyidi, 0,5xATR14 tolerans, degistirmeden) M15 VE M5
   seviyesinde de uygula** — ama bunu GENEL veri uzerinde degil, ONAYLANMIS bir H1/M30
   kanalinin AKTIF PENCERESI (onay→kirilim araligi) ICINDE, o pencereyle kesisen M15/M5
   barlari uzerinde yap (rapordaki M15/M5 giris-zamanlama boluminde zaten kurulmus olan
   "H1/M30 kanali icinde M15/M5 projeksiyonu" altyapisini temel al).
2. **Yeni bir "devam" tanimi olustur ve eskisiyle YAN YANA raporla:**
   - ESKI TANIM (rapordaki mevcut olcum, degismeden tekrar hesapla/referans ver): 1/3/7/14 gun
     sonra fiyat H1/M30 kanal projeksiyonuna gore hala trend yonunde ileride mi?
   - YENI TANIM: Ayni 1/3/7/14 gun ufuklarinda, ana H1/M30 kanalinin KENDISI (rapordaki
     kirilim tanimiyla — dondurulmus cizgi, kapanis fiyati tol'u trend-aleyhine asarsa)
     KIRILMIS MI, KIRILMAMIS MI? Bu ikili (kirilmadi/kirildi) olcumu, ic-ice M15/M5
     alt-kanallarindaki kisa ters-yon hareketlerini SAYMADAN yapar — ana kanal hala aktifse,
     icinde M15/M5'te kac tane kisa ters-yon alt-kanali olustugu bu olcumu ETKILEMEZ.
3. **Iki tanimi karsilastir:** Ayni kanal orneklemi (H1 yukselen/alcalan, M30 yukselen/alcalan,
   n=20-39) uzerinde, ESKI tanimla (%13-80 tutarsiz) YENI tanim (ana-kanal-kirilma-bazli) ne
   kadar farkli sonuc veriyor? Fark varsa, bu farkin BUYUKLUGU ve YONU (yeni tanim daha yuksek/
   daha tutarli bir devam orani mi gosteriyor?) somut sayilarla raporlanmali.
4. **Ic-ice alt-kanal sikligini da ayrica olc:** Onaylanmis bir H1/M30 kanalinin aktif
   penceresi icinde, ortalama kac tane M15/M5-seviyesi alt-kanal (>=3 dokunus + EMA/MACD
   teyidiyle onaylanmis, ayni yonde VEYA zit yonde) olustugu gozlemle — bu, "ic-ice yapi
   gercekten var mi" sorusuna bagimsiz bir kanit saglar (yeni "devam" tanimi anlamli olsun
   diye varsayilmamali, ayrica olculmelidir).
5. Bu bir hipotez/model KURMA gorevi degildir — sadece iki olcum yontemini yan yana
   karsilastirmali sekilde raporla. Hangi tanimin "dogru" olduguna karar verme; ikisini de ham
   sayilarla sun.
6. Kucuk orneklem (n=20-39 kanal) sinirini ACIKCA tekrar belirt — bu olcum de ayni kanal
   sayisina dayanir, orneklem buyumez.

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (PIVOT/KANAL
  TANIMI bolumu — TAM FORMUL, degistirmeden kullan; H1/M30 Yapisal Trend Bulgulari bolumu —
  ESKI "devam orani" tanimi ve sayilari, madde 11 — M15/M5 giris-zamanlama altyapisi)
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama.py` (ana tarama scripti —
  pivot/kanal ve M15/M5 projeksiyon kodu buradan yeniden kullanilabilir)
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_output.json` (ham
  kanal listesi — onay/kirilim bar indeksleri, tarihleri; yeni M15/M5 alt-kanal taramasi icin
  baslangic noktasi)

ONCEKI ADIMIN CIKTISI: `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`
(bu gorev, o raporun "devam orani tutarsiz" bulgusunun OLCUM-YONTEMI kritigini/genisletmesini
yapar — eski bulguyu gecersiz kilmaz, YANINDA ikinci bir olcum sunar)

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Baska bir dahili sistemin (MilaGold/Lisa/Signal
GPT) bulgu/veri/parametresine/format-sablonuna erisim veya atif YOKTUR. Tek veri kaynagi
XM/MT5 (dogrudan `MetaTrader5` kutuphanesi). Calisma dizini yalniz `C:\MilaYatirim\Justin\`
altindadir.

BEKLENEN CIKTI     : Markdown rapor,
`C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam_raporu.md`.
Bolumler: Ozet, Yontem (ic-ice M15/M5 alt-kanal tarama tanimi — TAM FORMUL), Ic-Ice Alt-Kanal
Sikligi (bagimsiz kanit), Eski vs Yeni "Devam" Tanimi Karsilastirmasi (ham sayilar, tum
ufuklar/yonler), Sinirlamalar, Izolasyon Notu.

ONAY NOKTASI       : Bilgi notu — bu gorev salt-arastirma/metodoloji niteliginde, canli
sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki
yok (Justin arastirma/demo asamasi, canli hesap yok), tespit gecikmesi konusu degil, etki
alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez.
Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi dusulecek (10
Temmuz kurali geregi).

SAYAC NOTU: Bu gorev gunluk pipeline dongu sinirina (5/gun, Stratejist cagrisi = 1 tur)
SAYILMAZ — Stratejist bu asamada devrede degildir. Aile-bazli RED sayacina da sayilmaz.

NOT — BAGIMSIZLIK: Bu gorev, ayni oturumda Orkestrator tarafindan baslatilan DIGER bir gorevle
(M5-donem dogrulamasi, ayri dosya) BAGIMSIZDIR — iki gorevin sonuclari birbirine
karistirilmamali, ayri raporlar olarak kalmalidir.
