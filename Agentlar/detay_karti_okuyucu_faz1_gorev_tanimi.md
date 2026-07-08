# DETAY KARTI OKUYUCU — FAZ 1: SS BiRiKTiRME (GOREV TANIMI)

Bu faz kural-tabanli — Claude API'ye (vision) hic cagri yapilmaz. Amac: alan yapisi bilinmedigi icin once ham ornek biriktirmek.

---

## 1. Amac

Detay kartinin (Structure&Trend, Momentum, Volatility, Price Plan, Risk) ekran goruntusunu alip, tarih-saat damgali dosya adiyla kaydetmek. **Ilk hedef: 50 kartlik bir set.** Bu setle birlikte (Faz 2'de) bolumlerin gercek alan/deger yapisi netlesecek, ancak o zaman Claude vision entegrasyonu (bkz. detay_karti_okuyucu_system_prompt.md) devreye girecek.

---

## 2. Adimlar (sirali erisim, mevcut liste-OCR ile cakismamak icin)

1. Liste oku (mevcut OCR agent akisi)
2. signal.json yaz
3. Detay kartina gir
4. **Screenshot al, kaydet** (bu fazda yapilan tek yeni is)
5. Listeye don

---

## 3. Dosya Adi Formati

`detay_karti_{YYYYMMDD}_{HHMM}_{tetikleyici}.png`

Tetikleyici: `saatlik` veya `fiyat_esigi`

Ornekler:
- `detay_karti_20260708_1432_saatlik.png`
- `detay_karti_20260708_1451_fiyat_esigi.png`

---

## 4. Depolama Konumu

`C:\MilaYatirim\TersMuhendislik\detay_kartlari\` — MilaGold'un altina degil, ayri proje (Proje 6: Ters Muhendislik) klasorune.

---

## 5. Tetiklenme

Iki tetikleyici var:

- **Saatlik** — duzenli, sabit araliklarla
- **Fiyat esigi** — fiyat, onceki cekimin oldugu $25'lik dilimden farkli bir dilime gectiginde tetiklenir. Sabit/mutlak fiyat cizgileri (4100, 4125, 4150, 4175...), sinyalin entry'sine gore degil. Ayni seviyeye tekrar donse bile (orn. 4150→4200→4150), her gecis yeni bir tetikleme sayilir. Esik degeri **25 dolar** (50 degil — genis baslamak yerine ince baslamak, gerekirse sonradan azaltmak kolay, once genis toplayip daraltmak veriyi geri getirmez).

**Not (8 Temmuz, duzeltme):** Ayni sinyal aktifken birden fazla fiyat esigi tetiklenirse, kart icerigi **degismez** — kart, sinyalin uretildigi andaki veriyle donmus, bizim cekim animizdaki canli veriyle degil. Yani bu durumda tekrarli cekimler **duplike** olur, "zaman icindeki degisim" gibi ekstra bir anlam tasimaz. Bu sorun degil (dusuk maliyetli), ekstra bir dedup mantigi kurulmuyor — Faz 2 incelemesinde kartin kendi icindeki entry/zaman bilgisiyle duplikeler zaten ayirt edilebilir.

**Fiyat esigi tetiklendiginde aktif sinyal yoksa:** Ekran goruntusu alinmaz (cekilecek bir kart yok), bunun yerine bir **log satiri** birakilir (orn. `detay_karti_log.txt`'ye: zaman + "fiyat esigi X'e ulasildi, aktif sinyal yok"). Boylece bu esigin **atlanmadigi**, kontrol edilip sinyal olmadigi icin kayit birakilmadigi acikca gorunur.

---

## 5b. Calisma Penceresi (8 Temmuz, KESiN)

**Sadece 05:00-00:00 arasi calisir.** Gerekce: piyasa 00:00'da kapanir, Lisa'nin yeniden sinyal uretmeye baslama saati tutarsiz (03:00-05:00 arasi degisken, otomatik bir kural degil, muhtemelen manuel bir mudahale). Bu belirsiz pencerede okunan kart ya donmus/bayat olur ya da "sinyal yok" kaydi olur — anlamli veri uretmez. En gec gozlemlenen baslama saatini (05:00) sabit baslangic kabul ederek bu riski tamamen ortadan kaldiriyoruz. Sonuc: gunde 19 saat veri toplama, 24 degil — ama toplanan verinin tamami anlamli.

00:00-05:00 arasi: ne saatlik ne fiyat_esigi calisir, hic kart okunmaz, log de yazilmaz.

---

## 6. Hedef Sayi ve Esik Bildirimi (8 Temmuz, KESiN)

**Ilk set: 50 kart.**

50. karta ulasildiginda, Faz 1 script'i bir durum dosyasi yazar (orn. `detay_karti_toplama_durumu.json` — toplam sayi, tamamlanma zamani). Bu, digerleriyle (Gozetleme, Raporlama) ayni desen: **tek yazici, Orkestrator okur.**

Orkestrator kurulup calisir hale gelince, bu durum dosyasini izleyip esik asildiginda veri setini **Arastirmaci'ya kendi API cagrisiyla** iletecek (insan-rolesi olmadan — Orkestrator'in muhakeme yetenegi tam bunun icin var). Bu mekanizmanin tam detayi (Orkestrator'in Yol1 ekibini nasil tetikleyecegi) **ayri bir baslikta, Orkestrator'i tamamlarken netlesecek** — kart okuyucunun sorumlulugu, sadece durum dosyasini dogru yazmak.

Orkestrator hazir olana kadar: 50 karta ulasildiginda Telegram'a basit bir bilgi notu gider ("50 kart hazir, TersMuhendislik/detay_kartlari klasorunde").

---

## 7. Sonraki Adim (Faz 2, simdi degil)

Yeterli ornek biriktiginde: birlikte inceleyip her bolumun gercek alan/deger yapisini netlestiririz, `detay_karti_okuyucu_system_prompt.md`'yi (zaten taslak halde hazir) bu gercek yapiya gore guncelleriz, sonra vision-tabanli JSON cevrimi devreye girer.
