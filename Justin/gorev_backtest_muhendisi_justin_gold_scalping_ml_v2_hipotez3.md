=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-12 15:30
HEDEF AGENT        : Backtest Muhendisi
SISTEM PROMPTU YOLU: C:\MilaYatirim\Agentlar\backtest_muhendisi_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — ML/Feature-Tabanli Aile, Faz 2, v2
                      (ML Tam Tur 2), HIPOTEZ 3 (OLCEKLENEBILIRLIK PILOTU, DUSUK ONCELIK: Grup D
                      /mikro-yapi feature'i, SADECE son 60-90 islem gunu penceresi)

GOREV              : Stratejist'in (stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md,
                      Bolum "HIPOTEZ 3") tanimladigi kisitli/pilot testi dogrula. **ONCELIK
                      DUSUK** — Hipotez 1/2 tamamlanmadan sonucu Tur 2'nin nihai KABUL/RED
                      kararinin dayanagi OLAMAZ (Stratejist'in acik uyarisi); kapasite izin
                      verirse Hipotez 1/2 ile paralel/kuyrukta calistirilabilir, sonucu ayri, dar
                      kapsamli bir on-gozlem olarak raporlanmali.

                      Sira / kapsam:
                      1. **Veri penceresi:** SADECE son 60-90 islem gunu (kesin sayi tick-verisi
                         cekme suresine gore ayarlanabilir, tahmini ~7-11 saniye) — TAM 4,2
                         yillik egitim/test setinden TAMAMEN AYRI, kucuk-olcekli bir alt-deney.
                         Ana Hipotez 1/2'nin egitim/test bolme mantigina KARISTIRILMAMALI.
                      2. **Feature seti:** Hipotez 1 ile AYNI (Grup 1-5 + Grup B) + EK Grup D
                         (tick-kural-tabanli imbalance orani, tick-sayisi, tick-ici mikro-
                         volatilite/mid_ret_std, tick-seviyesi ortalama spread — Arastirmaci
                         BULGU 7-9).
                      3. **Egitim/test bolme:** Purge/embargo ORANTILI kucultulmeli (orn. N=16-bar
                         + 1 gunluk embargo, tam-tarihsel Hipotez 1/2'deki gibi haftalik/aylik
                         DEGIL) — kucuk n bu ilkelerin gevsetilmesi icin GEREKCE DEGILDIR, S2
                         protokolu (ileri-bakis/nedensel kontrol dahil) TAM uygulanmali.
                      4. **SL/TP/risk:** Hipotez 1 ile BIREBIR AYNI (k_risk=1,5xATR14, N=16,
                         RR=1:1, HEDEF_WR=%60,0, ayni lot/risk kurallari). Opsiyonel: bu kisitli
                         pencerede spread'in KENDI medyanini ayrica olcup S1'i teyit edebilirsin
                         (ek saglamlik kontrolu, ZORUNLU DEGIL).
                      5. **Tick-agregasyon nedensellik kontrolu:** M15-bucket icinde tick
                         agregasyonlarinin ileri-bakis icermedigi BAGIMSIZ tekrar kontrol
                         edilmeli (Arastirmaci'nin kendi iddiasi YETERLI SAYILMAZ).
                      6. **Raporlama cercevesi (Stratejist'in acik talimati):** Kucuk orneklem
                         (~3.780-5.670 M15-bucket) nedeniyle istatistiksel guc SINIRLIDIR — sonuc
                         "KESIN RED/KABUL" DEGIL, "bu olcekte ilk gozlem, tam-tarihsel
                         olceklendirme HALA cozulmemis" seklinde cerceve lenmeli. Bu hipotez
                         BASARILI (KABUL) cikSa bile, Grup D'nin tam 4,2 yillik egitim setine
                         nasil tasinacagi bu raporla COZULMEZ, ayri bir tasarim/muhendislik
                         sorusu olarak acik birakilmali.

GECMIS CALISMA/CERCEVE DOSYASI:
- C:\MilaYatirim\Justin\justin_gecmis_calisma.md
- C:\MilaYatirim\Justin\justin_ml_anti_overfitting_protokolu.md
- C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md

ONCEKI ADIMIN CIKTISI:
- C:\MilaYatirim\Justin\stratejici_raporu_justin_gold_scalping_ml_v2_20260712.md (HIPOTEZ 3
  tanimi, Karar 4)

BEKLENEN CIKTI     :
C:\MilaYatirim\Justin\backtest_muhendisi_raporu_justin_gold_scalping_ml_v2_hipotez3_20260712.md
(bolum yapisi: Veri Penceresi/Tick-Cekme Suresi, Nedensellik Kontrolu [Grup D], Ana Test
Tasarimi, Sonuclar [ISTATISTIKSEL GUC SINIRLI vurgusuyla], Olceklenebilirlik Durumu [COZULMEDI,
acik soru olarak], Risk Analistine Iletim, Izolasyon Notu, Onay Noktasi) + ham veri/script
dosyalari.

VERI IZOLASYONU HATIRLATMASI (CLAUDE.md, 10 Temmuz KESIN): MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre/format-sablonu acilmayacak/referans alinmayacak. Calisma dizini yalniz
C:\MilaYatirim\Justin\.

GOVERNANCE HATIRLATMASI (S3, bilgi amacli): S3 sayaci su an 1/2. Hipotez 3, Stratejist'in kendi
tanimiyla ana karar agirligini TASIMAMALI — Risk Analisti'nin Tur 2 nihai KABUL/RED kararinda
(S3 sayacini etkileyen karar) Hipotez 1/2 birincil dayanak, Hipotez 3 tamamlayici/on-gozlem
niteligindedir.

ONAY NOKTASI       : Bilgi notu — bu adim salt-okunur/analitik/offline backtest calismasi, canli
sisteme dokunus yok, Justin demo/arastirma asamasinda (henuz canli hesap yok). 4 boyutlu
degerlendirme: geri donulebilirlik tam, mali etki yok, tespit gecikmesi konusu degil, etki alani
dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu kategorisi, Ertan onayi gerekmez. Rapor
uretildiginde Ertan'a Telegram bilgi notu + Orkestrator_Loglar kaydi Orkestrator tarafindan
dusulecektir.
