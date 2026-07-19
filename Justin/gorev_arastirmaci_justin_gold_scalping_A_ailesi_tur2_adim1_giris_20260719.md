=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-19
HEDEF AGENT        : Arastirmaci
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\arastirmaci_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
TUR 2 / ADIM 1 GIRISI (Ertan'in 19 Temmuz 2026 "devam karari" ile tetiklendi)

GOREV              : Bu gorev **Tam Yol1 pipeline turunun Arastirmaci adimidir** (Arastirmaci
→ Stratejist → Backtest Muhendisi → Risk Analisti sirasi degistirilmeyecek, atlanmayacak).
Hipotez uretilmez, Stratejist'e devredilir.

**KRITIK GOVERNANCE BAGLAMI (Arastirmaci'nin neden sadece "M1 ekle" degil, asagidaki genisletilmis
gorevi aldigini aciklar):**
`stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md` ve
`risk_analisti_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260713.md` geregi, A ailesinin
**Tam Tur 1**'i (13 Temmuz) ZATEN ayni cekirdek mekanizmayla (H1/M30'da >=3 dokunus + EMA50/200 +
MACD 12/26/9 teyitli kanal FILTRESI + kanal cizgisine "dokunus + BIR SONRAKI barin trend
yonunde kapanmasi" GIRIS TETIGI, M5/M15/M30-yukselen-asimetrik varyantlarla) test edildi ve
UCU de RED oldu — en guclu/en genis-orneklemli RED (H2, M15-giris) ozellikle "bu giris
MEKANIZMASININ KENDISI (sadece bir ufuk/parametre secimi degil) bu veri setinde pozitif edge
uretmiyor" sonucuna vardi. Risk Analisti'nin Tur 2 onerisi (karar degil, oneri) ACIKCA sunu
belirtiyor: bir sonraki tur, SL/TP yeniden-kalibrasyonu veya sadece farkli bir zaman-dilimi
secmek DEGIL, GIRIS TETIGININ KENDISINI (dokunus+hemen-devam disi bir mantik) degistirmelidir.
Ertan'in Cevap 1 (`justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`) da ayni yonde:
ardisik turlar mekanizma/mantik duzeyinde GERCEKTEN ayrismali, sadece parametre/ufuk degisikligi
YETERLI SAYILMAZ — bu esitlik her turun Stratejist/Risk Analisti raporunda ACIKCA teyit
edilmelidir ("Onceki-Turden-Ayrisma-Teyidi" bolumu).

Bu nedenle bugunku (19 Temmuz) "Adim 1'e gec" karari, H1/M30 pivot+EMA/MACD yapisal-trend
FILTRESINI merkezde tutmaya devam ediyor (bu kisim Tam Tur 1'le AYNI kalabilir — filtrenin
kendisi RED edilmedi, sadece giris-tetigi RED edildi), ama GIRIS TETIGININ Tam Tur 1'dekiyle
(dokunus+hemen-devam) AYNI KALMAMASI gerekiyor. Arastirmaci'nin bu turdaki gorevi, Stratejist'e
hem M1 ufkunu hem de ALTERNATIF giris-tetigi tanimlarini olcerek somut, karsilastirmali ham veri
saglamaktir — Arastirmaci hicbir tetigi "onerir" ya da "secer" demez, sadece olcer.

**Somut gorev tanimi:**

1. **M1 giris-zamanlama testi (yeni — Adim 0'da hic yapilmadi):** Onaylanmis H1/M30
   kanallarinin (>=3 dokunus + EMA50/200 + MACD teyidi, TAM FORMUL degistirilmeden —
   `arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`, "PIVOT/KANAL TANIMI" bolumu)
   aktif penceresinde, kanal cizgisinin M1 barlarina projeksiyonuyla AYNI giris-tetigi
   tanimini (dokunus + bir-sonraki-barin-trend-yonunde-kapanmasi — SADECE KARSILASTIRMA
   ICIN BASELINE olarak) M1 seviyesinde olc. M1 icin veri derinligi kisiti olabilir (M5'te
   `m5_donem_dogrulama_raporu.md`daki 100.000-bar/~1,4-yil sinirina benzer bir sinir M1'de
   DAHA DA kisa olabilir) — varsa bunu bir BULGU olarak hemen raporla, "veri yok" gecerli
   bir sonuctur.
2. **ALTERNATIF giris-tetigi tanimlari (asil yeni katki — mekanizma-duzeyinde ayrisma icin
   ham malzeme):** Ayni H1/M30 kanal FILTRESI SABIT tutularak (degistirilmeden), M1/M5/M15
   seviyelerinde en az 2 farkli, "dokunus+hemen-devam" MANTIGINDAN gercekten farkli giris-tetigi
   tanimini olc (Risk Analisti'nin Tur 2 onerisi madde 1'deki yonlerle uyumlu, ama tanimlarin
   kesin sekli Arastirmaci'nin kendi tasarimi olabilir):
   a) **Gecikmeli/coklu-teyit tetigi:** dokunus sonrasi TEK bir barin degil, ARDISIK N (orn.
      N=2 ve N=3, iki ayri deger olarak olc) barin trend yonunde kapanmasi sarti.
   b) **Momentum-esikli tetigi:** dokunus barinin (veya teyit barinin) govde/ATR orani belli
      bir esigi (orn. govde >= 0,5xATR14 ve >= 1,0xATR14, iki deger) asmasi sarti — sadece
      yon degil, barin "gucu" de tetigin parcasi.
   Her tanim icin: giris-tetigi sayisi, ortusen kanal sayisi (bagimsizlik icin kritik — mevcut
   raporlarda oldugu gibi ACIKCA ayri belirt), S1 maliyet-orani (>=15-20x) esigine ulasma suresi
   (mevcut raporlardaki ayni yontemle: hedef_pts = N-bar-ileri |kapanis farki| medyani,
   cost_pts = spread+0,037xATR14), ve orijinal (dokunus+hemen-devam) tanimla YAN YANA
   karsilastirmali tablo.
3. **Hicbir tetigi "daha iyi" olarak ONERME** — sadece ham sayilarla yan yana sun. Stratejist
   bu ham verilerden mekanizma-duzeyinde gercekten farkli bir hipotez (veya birden fazla)
   kuracak.
4. **Konsolidasyon:** Adim 0'in mevcut UC raporunun (pivot_kanal_tarama 14 Temmuz,
   ic_ice_kanal_devam 16 Temmuz, m5_donem_dogrulama 16 Temmuz) OZET bulgularini, yeni
   olculen M1/alternatif-tetik sonuclarinin YANINDA, TEK bir konsolide "Stratejist'e Iletim"
   bolumunde topla (sistem promptundaki standart iletim formatiyla) — boylece Stratejist'in
   Adim 1 hipotezlerini uretmek icin tek bir rapora bakmasi yeterli olsun. Bu bir OZETLEME'dir,
   eski raporlardaki hicbir sayi/bulgu DEGISTIRILMEZ veya YENIDEN YORUMLANMAZ, sadece bir araya
   getirilir + yeni bulgular eklenir.
5. Tum standart sinirlamalari (kucuk orneklem, sag-sansur, DST dogrulanmadi, ileri-bakisli
   pivot/5-bar-gecikme, giris-tetigi olaylarinin bagimsiz olmamasi) mevcut raporlardan
   DEVRAL ve yeni olculen alternatif tetikler icin de AYRICA belirt (orn. coklu-teyit tetigi
   dokunus sayisini azaltir, orneklem daha da kuculebilir — bunu somut sayiyla goster).

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\justin_gecmis_calisma.md` (kasa/risk/DD
  cercevesi)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`
  (governance — Cevap 1-5, A/C iliskisi duzeltmesi, Adim 0→1→2 sirasi)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md`
  (PIVOT/KANAL TANIMI — TAM FORMUL, degistirmeden kullan)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_pivot_kanal_ic_ice_kanal_devam_raporu.md`
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_raporu.md`
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_pivot_kanal_tarama.py`
  (ana tarama scripti — pivot/kanal ve M15/M5 projeksiyon kodu buradan yeniden kullanilabilir,
  M1 ve alternatif-tetik varyantlari icin uyarlanacak)

ONCEKI ADIMIN CIKTISI:
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\risk_analisti_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260713.md`
  (Tur 2 onerisi, madde 1-3 — bu gorevin dogrudan tetikleyicisi)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md`
  (Tam Tur 1'in tam mekanizma tanimlari — karsilastirma icin)

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Baska bir dahili sistemin (MilaGold/Lisa/Signal
GPT) bulgu/veri/parametresine/format-sablonuna erisim veya atif YOKTUR. Tek veri kaynagi
XM/MT5 (dogrudan `MetaTrader5` kutuphanesi). Calisma dizini yalniz
`C:\MilaYatirim\mila-yatirim-sistemi\Justin\` altindadir.

BEKLENEN CIKTI     : Markdown rapor,
`C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_A_ailesi_tur2_adim1_raporu_20260719.md`.
Bolumler (sistem promptundaki standart format + bu goreve ozel ekler): Ozet, M1 Giris-Zamanlama
Bulgulari, Alternatif Giris-Tetigi Tanimlari (coklu-teyit + momentum-esikli — TAM FORMUL +
ham sayilar + orijinal tetikle karsilastirma), Konsolide Adim-0-Ozeti (14+16 Temmuz raporlarinin
kisa ozeti), Arastirma Bosluklari, Sinirlamalar, Izolasyon Notu. Ham veri/script'ler ayni
klasore kaydedilir (orn. `arastirmaci_gold_scalping_A_ailesi_tur2_adim1.py` +
`..._output.json`).

ONAY NOKTASI       : Bilgi notu — bu adim salt-arastirma/olcum niteliginde, canli sisteme/
hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok
(Justin arastirma asamasi, canli/demo hesap baglanmadi), tespit gecikmesi konusu degil, etki
alani dar (yalniz Justin arastirma hatti) → STOP-genis/bilgi-notu kategorisi, Ertan onayi
gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi
Orkestrator tarafindan dusulecektir.

SAYAC NOTU: Bu gorev gunluk pipeline dongu sinirina (5/gun, Stratejist cagrisi = 1 tur)
SAYILMAZ — Stratejist bu asamada henuz devrede degil. Bu turun A-ailesi gunluk tam-tur
sayacina etkisi, Stratejist gorevlendirildiginde (bir sonraki adim) baslayacaktir.

ONEMLI HATIRLATMA (Stratejist'e devir asamasi icin simdiden not, bu Arastirmaci gorevinin
KAPSAMI DISINDA ama Orkestrator'un takip etmesi gereken bir madde): Stratejist gorevlendirilirken
gorev dosyasina ACIKCA "Onceki-Turden-Ayrisma-Teyidi" (Cevap 1 geregi) zorunlu bir bolum olarak
eklenecek — Stratejist, urettigi her hipotezin Tam-Tur-1'in "dokunus+hemen-devam" giris-tetiginden
mekanizma-duzeyinde GERCEKTEN farkli oldugunu ACIKCA teyit etmelidir; teyit edemiyorsa bu durum
hipotez uretmeden once Orkestrator'a acik soru olarak bildirilmelidir.
