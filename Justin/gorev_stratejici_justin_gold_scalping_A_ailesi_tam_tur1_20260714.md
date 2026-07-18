=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-14 15:05
HEDEF AGENT        : Stratejist
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\stratejici_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — Strateji Ailesi Plani, ADIM 1
                      (A ailesi / Momentum-Trend-Following, kural-tabanli baseline, TAM TUR 1)

GOREV              : Adim 0 (bar-bar otokorelasyon/devam-orani + S1 on-kontrolu) ve Adim 0'in
ek pivot/kanal on-taramasi (yapisal kanal + M15/M5 giris-zamanlama) tamamlandi. Bu ikisi
BIRLIKTE Adim 0 asamasini kapatir (asagida "ONCEKI ADIMIN CIKTISI"). Simdi Yol1 sirasina
uygun olarak Stratejist, A ailesi (Momentum/Trend-Following) icin **3 kural-tabanli varyant
(H1, H2, H3)** uretecek (Ertan'in Cevap 2 karari geregi, "5" veya baska birlesik bir sayi
DEGIL, bu ayristirilmis format kullanilacak — bkz. asagida Zorunlu Kisitlar Madde 3).

Bu, Justin/A-ailesi hattinin **Tam Tur 1**'idir (gunluk pipeline dongu sayacina bu cagriyla
1/5 olarak sayilmaya baslanir; Adim 0 ve ek pivot/kanal taramasi Arastirmaci-duzeyi on-tarama
oldugu icin bu sayaca dahil DEGILDI, bkz. onceki cagri kayitlari).

--- ZORUNLU KISITLAR (Ertan'in kararlarindan, atlanamaz) ---

1. **S1 esigi degismedi** (`justin_backtest_onkontrol_standardi.md`, Madde 2:
   hedef_pts/cost_pts >= 15-20x). Esik dusurulmedi (Orkestrator'un Soru-1 degerlendirmesi,
   `orkestrator_yanit_3soru_justin_20260714.md`, Bolum 1).
2. **Scalping karakteri korunmali** (Cevap 3, KESIN): SL/TP mesafeleri dar/hizli kalmali,
   tutma suresi dakikalar-birkac-saat mertebesinde olmali, gun/hafta mertebesine KAYMAMALI.
   Ortaya cikan her varyant icin beklenen tutma suresi ACIKCA raporlanmalidir.
3. **Sayisal ifade formati** (Cevap 2, KESIN): "3 varyant" gibi bilesenler ayri ayri
   belirtilir; tek bir birlesik sayiya indirgenmez.
4. **C (Breakout) ayri bir aile DEGIL** (A/C duzeltmesi): kirilim-noktalari sadece A'nin
   ICINDE bir ek arac/gozlem olarak kullanilabilir (orn. yapisal-kanal kirilim bari), C
   basli basina bir varyant olarak SUNULMAMALI.
5. **Range rejiminde varsayilan (b):** net trend olusana kadar islem acilmaz (Cevap 4) —
   bu varsayimi kural-tabanli varyantlarin girdi/filtre mantigina yansitin (rejim ust-katmani
   Adim 3'e ait, ama varyantlarin "trend yok/belirsiz" durumda islem ACMAMASI Adim 1'de de
   gecerli bir tasarim ilkesi olarak benimsenmelidir).
6. **"Onceki Turdan Ayrisma Teyidi" bu turde GECERLI DEGIL** (governance notu,
   `justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`, Cevap 1 Uygulama Notu): bu,
   A ailesinin ILK tam turudur, karsilastirilacak onceki bir tur yok. Bu madde Tur 2'den
   itibaren zorunlu olacak.

--- BULGULARIN KULLANIMI ICIN KRITIK UYARI (Orkestrator degerlendirmesi) ---

Ek pivot/kanal raporu bir "CELISKI BULGUSU (kismi/kirilgan cozum)" tespit etti: H1/M30→M5
giris kombinasyonlari (ozellikle alcalan yon) S1 esigini 0,9-3,7 saatte geciyor gorunuyor —
ama bu sonuc SADECE 2-8 bagimsiz yapisal kanala ve ~17 aylik (2025-02→2026-07) dar/yakin
donem M5 verisine dayaniyor; giris-tetigi sayilari (binlerce) bagimsiz gozlem DEGIL, ayni
birkac kanal icinde tekrarlanan otokorelasyonlu olaylar. Bu nedenle:

- Bu bulgu **"celiski cozuldu" olarak KABUL EDILMEMELI.** Stratejist bunu bir ADAY yon
  olarak ele alabilir, ama H1/H2/H3'ten en az birini bu dar-kanitli M5-giris mekanizmasina
  DAYANDIRMAYACAKSA bile, en azindan birini bu mekanizmayla (veya ona yakin bir tasarimla)
  olusturup Backtest Muhendisi asamasinda genis-orneklem/farkli-donem dogrulamasina birakmasi
  ONERILIR (Onerilen Sonraki Adim, madde 1/3).
- H1/M30→M15 giris kombinasyonlari (4,4-10,3 saat, 6-18 kanal) istatistiksel olarak daha
  saglam ama Adim 0'daki S1-vs-scalping gerilimini BUYUK OLCUDE TEKRARLIYOR — bu sinir-bolgesi
  durumu acikca kabul edilmeli, "kesin cozuldu" gibi sunulmamali.
- M30-yukselen kanallarin (devam orani %63-80, en tutarli) ayrica bir varyantta on-plana
  cikarilmasi makul bir tasarim tercihidir (n=20, kucuk orneklem, teyide muhtac).
- Onay-sonrasi devam-oraninin genel olarak TUTARSIZ/monotonik-olmayan yapisi ("yapisal trend
  onaylandi = guvenli devam" varsayiminin bu veri setinde desteklenmedigi) her varyantin
  risk/durus mantigina (orn. sabit bir "N gun sonra kapat" kurali yerine kirilim-bazli cikis)
  yansitilmalidir.
- DST/saat-eslesme dogrulamasi Adim 0'da da bu ek turde de YAPILMADI — bu, Backtest Muhendisi
  asamasinda (`justin_backtest_onkontrol_standardi.md`, Madde 1 geregi) BAGIMSIZ olarak
  dogrulanmadan varyantlarin sonucuna guvenilmemelidir; Stratejist bu adimi acikca Backtest
  Muhendisi'ne bir on-kosul olarak devretmelidir (kendi hesaplamayacak).

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` (S1 tanimi)
- `C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`
  (Ertan'in 5 cevabi + A/C duzeltmesi — bu gorevin governance kaynagi)
- `C:\MilaYatirim\Justin\orkestrator_yanit_3soru_justin_20260714.md` (S1 esiginin neden
  degismedigine dair tam gerekce)
- `C:\MilaYatirim\Justin\orkestrator_gorus_strateji_ailesi_plani_20260712.md` (orijinal plan
  taslagi, 14-aile siniflandirmasi baglaminda A'nin konumu)

ONCEKI ADIMIN CIKTISI:
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_adim0_tarama_raporu.md` (Adim 0, bar-bar
  otokorelasyon/devam-orani + S1)
- `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md` (ek on-tarama,
  yapisal kanal + M15/M5 giris-zamanlama + S1, Celiski Bulgusu kismi/kirilgan cozum)

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): MilaGold/Lisa/Signal GPT'ye ait hicbir dosya,
bulgu, deger veya format/sablon referans olarak KULLANILMAZ. Calisma dizini yalniz
`C:\MilaYatirim\Justin\` altindadir.

BEKLENEN CIKTI     : Markdown rapor, `C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_
scalping_A_ailesi_tam_tur1_20260714.md`. Bolumler: Ozet, H1/H2/H3 (her biri icin: giris/cikis
kurali, kullanilan ufuk/mekanizma, S1 uyumu, beklenen tutma suresi, scalping-uyum notu, dayandigi
kanal/orneklem sayisi ve kirilganlik notu), Range-Rejimi Filtre Notu, Onceki-Tur-Ayrisma-Teyidi
(bu turde N/A, gerekce belirtilerek), Backtest Muhendisi'ne Devir Notlari (DST dogrulamasi dahil),
Sinirlamalar, Izolasyon Notu.

ONAY NOKTASI       : Bilgi notu — bu adim (hipotez/kural-tabanli varyant uretimi) salt
arastirma/tasarim niteliginde, canli sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme:
geri donulebilirlik tam, mali etki yok (Justin arastirma/demo asamasi, canli hesap yok), tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin/A-ailesi hatti) → STOP-genis/bilgi-notu
kategorisi, Ertan onayi gerekmez (Ertan zaten Adim 0→1→2 siralamasina Cevap-5 ile acik onay
vermisti). Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi dusulecek.

SAYAC NOTU: Bu cagri, Justin/A-ailesi gunluk pipeline dongu sayacini 1/5'e getirir (Stratejist
cagrisi = 1 tur). Aile-bazli RED sayaci bu turde henuz devrede degil (Risk Analisti karari yok).
