# JUSTIN / GOLD SCALPING — ERTAN KARARI VE GOVERNANCE KAYDI (14 Temmuz 2026)

Statu: KALICI GOVERNANCE KAYDI — Faz 1 (Stratejist v6 turu) tetiklendiginde bu dosyaya atif
yapilmali; icerigi o gorev tanimina TASINMALI (kopyalanmali), bu dosya sadece kayittir.
Olusturan: Orkestrator, Ertan'in bildirimi uzerine (14 Temmuz 2026).
Kaynak: orkestrator_degerlendirme_madde7_gold_scalping_20260714.md (Orkestrator'un Fable 5
yukseltmesiyle yaptigi degerlendirme, ozellikle Bolum 4 ve 5).

---

## 1) ERTAN'IN KARARI (RESMI KAYIT)

Ertan, Orkestrator'un onerdigi **(a) — Stratejist'in genis-kapsamli hali** secenegini,
Orkestrator'un onerdigi **UC SERTLESTIRME (S1, S2, S3) ile birlikte** onaylamistir.

Karar sorusu ve secenekler icin kaynak: stratejici_raporu_justin_gold_scalping_20260714.md
(v5), Bolum 3. Sertlestirmelerin gerekcesi icin kaynak: orkestrator_degerlendirme_madde7_
gold_scalping_20260714.md, Bolum 4.

Onaylanan (a)'nin tanimi (Stratejist Bolum 3'teki "ve/veya" ifadesi Orkestrator onerisiyle
"VE" olarak DUZELTILMIS haliyle geçerlidir — zaman-ufku degisikligi artik OPSIYONEL degil
ZORUNLU bir bilesen):

> Arastirmaci'ya, kural-tabanli fiyat-aksiyonu yerine ozellik-tabanli klasik ML (orn.
> LightGBM/XGBoost), daha zengin bir veri/ozellik seti VE daha genis bir zaman-dilimi/
> tutma-suresi ile YENI bir Gold Scalping yaklasimi arastirma gorevi verilecek.

## 2) UC SERTLESTIRME — RESMI OLARAK YURURLUKTE

**S1 — Maliyet-orani zorunlulugu:** Yeni yaklasimin hedef islem-basi brut kazanci, tahmini
maliyetin en az ~15-20 kati olmali. Kalici on-kontrol standardina islendi, bkz.
`justin_backtest_onkontrol_standardi.md`, Madde 2.

**S2 — ML anti-overfitting protokolu:** Purged/embargolu walk-forward, test-seti tek-kullanim,
feature sizinti kontrol listesi, basari kriterleri egitimden once sabit. Ayri dosyaya islendi,
bkz. `justin_ml_anti_overfitting_protokolu.md`.

**S3 — On-taahhutlu gunbatimi maddesi (asagida detayli, RESMI GOVERNANCE KAYDI):**

> ML ailesinde 2 tam tur ayni olumsuz paternle RED olursa, otomatik olarak Ertan'a yeniden
> cikilir, varsayilan oneri (b) [alt-hedefi durdurma] olur.

Bu maddenin uygulama detaylari:
- "Tam tur" tanimi: CLAUDE.md'deki gunluk pipeline dongu siniri maddesindeki ayni birim —
  bir Stratejist cagrisi = 1 tur (Arastirmaci → Stratejist → Backtest Muhendisi → Risk
  Analisti zincirinin bir Risk Analisti KARARI ile sonuclanmasi).
- "Ayni olumsuz patern" tanimi: H1/H2/H3'te gorulenle ayni imza — aggregate/on-kontrolde
  istatistiksel olarak "anlamli" gorunen bir sinyal/model, Backtest Muhendisi'nin tam
  testinde (walk-forward/OOS/gercekci-maliyet) tutarli sekilde PF<1 veya benzeri sistematik
  RED sonucu vermesi. Farkli bir basarisizlik modu (orn. veri/altyapi hatasi, on-kontrolde
  elenme) bu sayaca DAHIL DEGILDIR — yalniz "gercek RED karari" sayilir.
- Sayac Faz 1'in ILK Arastirmaci/Stratejist turunden itibaren SIFIRDAN baslar (H1/H2/H3'un
  kural-tabanli-aile sayaci bu yeni ML-ailesi sayacina DEVREDILMEZ — Madde-7 zaten o aileyi
  kapatmisti).
- 2. tam turun RED sonucu netlestigi anda Orkestrator, Ertan'a **onay sorusu** (bilgi notu
  DEGIL) gonderir: "ML ailesinde de 2. tur RED oldu, varsayilan onerim (b) [alt-hedefi
  durdurma] — onaylar misiniz, yoksa devam mi edelim?" Bu, Bolum B/E'deki START/CHANGE
  onay kaliбiyla ayni mantik (bir arastirma serisinin acik-uclu devamina karar, kaynak-tahsisi
  kararidir).
- Gunluk pipeline dongu siniri (5/gun) bu sayactan BAGIMSIZ, PARALEL olarak aynen gecerliligini
  korur — biri gunluk hiz sinirlamasi, digeri (S3) toplam-aile-basarisizligi esigidir.

**Bu madde, Faz 1'de yazilacak Stratejist v6 gorev tanimina AYNEN (kopyalanarak) islenecektir
— bu dosya sadece onceden-kayit/governance amaclidir, Faz 1'in kendisi degildir.**

## 3) FAZ 0 DURUMU — TAMAMLANAN VE BEKLEYEN MADDELER

| Madde | Durum | Not |
|---|---|---|
| 1. `justin_gecmis_calisma.md` | **TAMAMLANDI (14 Temmuz 2026)** | Ertan'in onayi + kumulatif/gunluk DD netlestirmesi uzerine Orkestrator tarafindan olusturuldu, bkz. Bolum 4 (guncel) ve `justin_gecmis_calisma.md` |
| 2. Kalici on-kontrol listesi (DST + maliyet-orani + SL/TP-ozel) | TAMAMLANDI | `justin_backtest_onkontrol_standardi.md` |
| 3. S2 anti-overfitting protokolu metni | TAMAMLANDI | `justin_ml_anti_overfitting_protokolu.md` |
| 4. S3 gunbatimi governance kaydi | TAMAMLANDI (bu dosya) | Faz 1'de Stratejist v6 gorev tanimina aynen tasinacak |

**FAZ 0: TAMAMLANDI (14 Temmuz 2026, tum 4 madde kapandi).**

**Faz 1 (Stratejist v6 turu / Arastirmaci gorevi), Faz 0 tamamlanmis olsa da bu turde
BASLATILMAMISTIR** — Ertan'in acik talimatiyla bu bildirimde yalniz Faz 0/Madde 1'in kapatilmasi
istenmis, Faz 1'in tetiklenmesi (agent_cagir) KESINLIKLE BU TURDE YAPILMAMASI gereken bir adim
olarak ayrica belirtilmistir. Faz 1'in baslatilmasi icin Orkestrator'a ayri ve acik bir
gorevlendirme/onay gelmelidir.

## 4) MADDE 1 — SONUCLANAN SAYISAL DEGERLER (guncelleme: 14 Temmuz 2026)

Asagidaki degerler, Fable 5'in hazirladigi hesaplama raporu (`justin_gecmis_calisma_hesaplama_
20260714.md`) uzerinden Ertan'in onayiyla netlesmistir (asagidaki iki madde — HEDEF_WR ve
"lot/olceklendirme kurali" — hesaplama raporunda dogrudan sabit olarak degil, turetilmis/kosullu
deger olarak yer alir, ayrintisi ilgili maddede belirtilmistir):

1. **HEDEF_PF = 1,5**
2. **HEDEF_WR**: sabit tek bir deger olarak degil, R:R senaryosuna gore turetilen bir gereksinim
   olarak belirlendi (R:R henuz Backtest Muhendisi tarafindan secilmedi) — 1:1 icin %60,0,
   1:2 icin %42,9, 2:1 icin %75,0. Detay: hesaplama raporu Adim 1.
3. **HEDEF_DD = %20 — KUMULATIF/TOPLAM DONEM BAZINDA, GUNLUK DEGIL.** MilaGold'un gunluk
   (00:00'da sifirlanan) emniyet-stopuyla KARISTIRILMAMALIDIR; bu iki mekanizma farkli olcum
   birimlerine sahiptir. Detay ve tam gerekce: `justin_gecmis_calisma.md`.
4. **Kasa buyuklugu = 2.000 USD** (MilaGold'un 200 USD baslangicindan bagimsiz, Justin'e ozel).
5. **Islem-basi risk yuzdesi = %1** (ust sinir).
6. **Lot / olceklendirme kurali**: baslangic 0,01 lot (sabit), her tam 2.000 USD kasa = 0,01 lot
   olceklendirme (MilaGold'daki "her 200 USD = 0,01 lot" kuralindan bagimsiz, farkli esiklerle).

Bu degerlerin tam gerekcesi/hesaplama zinciri icin bkz. `justin_gecmis_calisma_hesaplama_
20260714.md`; kalici, Stratejist'in referans alacagi cerceve dosyasi `justin_gecmis_calisma.md`
olarak olusturulmustur.

---

## IZOLASYON NOTU

Bu dosya yalniz Justin'e ait bilgi/karar iceriyor; MilaGold/Lisa/Signal GPT'ye ait hicbir
dosya/parametre bu governance kaydinda kullanilmamistir.
