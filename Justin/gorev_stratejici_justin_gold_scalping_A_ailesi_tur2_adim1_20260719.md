=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-19 09:07
HEDEF AGENT        : Stratejist
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\stratejici_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — A Ailesi (Momentum/Trend-Following),
TUR 2 / ADIM 1 (Arastirmaci adiminin devami)

GOREV              : Arastirmaci'nin bu tur icin urettigi konsolide rapora dayanarak, Tam-Tur-1'in
"dokunus+hemen-devam" giris-tetiginden MEKANIZMA DUZEYINDE gercekten ayrisan 2-3 hipotez uret.
Yol1 sirasi (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti) korunur, bir sonraki
adim Backtest Muhendisi'dir (senin ciktin gelmeden atlanmaz).

Arastirmaci HICBIR tetigi onermedi/secmedi — sadece M1 baseline olcumu ve iki alternatif
mekanizmayi (coklu-teyit N=2/3, momentum-esikli k=0,5/1,0) ham sayilarla, 24 HTF x LTF x yon
kombinasyonunda yan yana sundu. Hipotez uretme sorumlulugu tamamen sana ait.

**ZORUNLU BOLUM — "Onceki-Turden-Ayrisma-Teyidi" (Ertan'in Cevap 1 geregi, atlanamaz):**
Urettigin HER hipotez icin, bu hipotezin Tam-Tur-1'in ("dokunus+hemen-devam", H1/M30 kanal
filtresi + kanal cizgisine dokunus + bir-sonraki-barin-trend-yonunde-kapanmasi, ZATEN 3/3 RED
sonuclanmis) giris-tetiginden MEKANIZMA DUZEYINDE gercekten farkli oldugunu ACIKCA teyit et —
sadece bir parametre/ufuk degisikligi (orn. SL/TP yeniden-kalibrasyonu veya farkli bir zaman-
dilimi secmek) YETERLI SAYILMAZ. Eger urettigin bir hipotezin Tam-Tur-1'den mekanizma-duzeyinde
gercekten ayristigini teyit EDEMIYORSAN, o hipotezi hic uretme — bunun yerine bu durumu acik bir
soru olarak raporunda Orkestrator'a bildir (hipotez sayisini zorla doldurma).

Arastirmaci raporundaki ham malzeme (coklu-teyit / momentum-esikli / ikisinin kombinasyonu / veya
bunlarin disinda kendi tasarladigin baska bir mekanizma) senin hipotez tasarimin icin baslangic
noktasidir, zorunlu secim degildir — mekanizma-duzeyinde ayrisma testini gecen herhangi bir
tasarimi kullanabilirsin.

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\justin_gecmis_calisma.md` (kasa/risk/DD cercevesi)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md`
  (governance — Cevap 1-5, Adim 0→1→2 sirasi, Onceki-Turden-Ayrisma-Teyidi zorunlulugu)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\stratejici_gold_gecmis_calisma.md`
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260714.md`
  (Tam Tur 1'in tam mekanizma tanimi — ayrisma karsilastirmasi icin referans)
- `C:\MilaYatirim\mila-yatirim-sistemi\Justin\risk_analisti_raporu_justin_gold_scalping_A_ailesi_tam_tur1_20260713.md`
  (Tam Tur 1 RED gerekcesi + Tur 2 onerisi)

ONCEKI ADIMIN CIKTISI:
`C:\MilaYatirim\mila-yatirim-sistemi\Justin\arastirmaci_gold_scalping_A_ailesi_tur2_adim1_raporu_20260719.md`
(bu turun tek girdisi — M1 baseline + coklu-teyit/momentum-esikli 24-kombinasyon tablolari +
Adim-0 konsolide ozeti + sinirlamalar)

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Baska bir dahili sistemin (MilaGold/Lisa/Signal GPT)
bulgu/veri/parametresine/format-sablonuna erisim veya atif YOKTUR. Calisma dizini yalniz
`C:\MilaYatirim\mila-yatirim-sistemi\Justin\` altindadir.

BEKLENEN CIKTI     : Markdown rapor,
`C:\MilaYatirim\mila-yatirim-sistemi\Justin\stratejici_raporu_justin_gold_scalping_A_ailesi_tur2_adim1_20260719.md`.
Icerik: sistem promptundaki standart format + zorunlu "Onceki-Turden-Ayrisma-Teyidi" bolumu (her
hipotez icin ayri ayri) + Backtest Muhendisi'ne iletim (test edilecek somut kurallar: giris/cikis/
SL-TP/zaman dilimi/kanal filtresi — belirsizlik birakma).

ONAY NOKTASI       : Bilgi notu — bu adim hipotez URETIMI/tasarim niteliginde, canli sisteme/
hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri donulebilirlik tam, mali etki yok (canli/
demo hesap baglanmadi), tespit gecikmesi konusu degil, etki alani dar (yalniz Justin arastirma
hatti) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor uretildiginde Ertan'a
Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan dusulecektir.

SAYAC NOTU: Bu cagriyla birlikte A-ailesi gunluk tam-tur (Stratejist cagrisi = 1 tur) sayaci
BASLAR (Arastirmaci adimi bu sayaca dahil degildi, bkz. onceki gorev dosyasi).
