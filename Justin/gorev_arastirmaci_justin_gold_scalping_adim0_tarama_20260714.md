=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : 2026-07-14 14:40
HEDEF AGENT        : Arastirmaci
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\arastirmaci_system_prompt.md

PROJE              : Justin (Gold Scalping alt-hedefi) — Strateji Ailesi Plani, ADIM 0

GOREV              : **Bu bir tam Yol1 pipeline turu DEGILDIR.** Arastirmaci-duzeyinde, dar
kapsamli, iki parcali bir ON-TARAMA gorevidir (hipotez uretilmez, Stratejist'e devredilmez —
sonuc dogrudan Orkestrator'a raporlanir). Amac: H1-H3'te gorulen "aggregate'te anlamli, tam
testte olu" tuzagina karsi, herhangi bir hipotez kurmadan ONCE ufuk/maliyet matematigini
sabitlemek.

**A-TARAMASI (birincil):**
1. M15 / H1 / H4 ufuklarinda GOLD icin getiri otokorelasyonu isareti (basit lag-1..lag-N
   otokorelasyon veya varyans-orani testi — Stratejist duzeyinde model kurulmuyor, sadece
   isaret var mi/yok mu ve hangi ufukta daha guclu).
2. Basit MA-kesisim / N-bar-devam kosullu devam oranlari (orn. "N bar ayni yonde kapandiginda,
   bir sonraki M bar da ayni yonde kapanma orani, rastgele ile karsilastirmali") her ufukta.
3. **S1 on-kontrolu (zorunlu):** Hangi ufukta hedef-brut-kazanc/maliyet orani 1/15-1/20
   esigine ulasiyor (bkz. `justin_backtest_onkontrol_standardi.md`, Madde 2). Bu, muhtemel
   giris-filtresi ufkunun ilk isaretidir.
4. **YENI KISIT (14 Temmuz governance guncellemesi geregi — ZORUNLU, atlanamaz):** S1'i
   saglayan ufuk/parametre bolgesinde, SL/TP mesafesinin scalping karakterini (dar/hizli,
   MilaGold'daki 5$/3$/5$/8$ mertebesine kiyasla ORANTILI dar bir mesafe — Justin kendi kasa/
   risk-yuzdesi olceginde, MilaGold ile birebir ayni rakam degil ama AYNI KARAKTERDE: dakikalar-
   birkac-saat mertebesinde tutma, gun/hafta mertebesinde DEGIL) koruyup korumadigini AYRICA VE
   ACIKCA raporlayin. Ertan'in acik talimati: "A ailesi test edilirken de SL/TP mesafeleri
   scalping'e uygun (dar/hizli) kalmali; intraday/swing'e kayma bu alt-hedefin kapsaminda
   degil." Eger S1'i saglayan TEK ufuk/parametre bolgesi, tutma-suresini saatler-gun mertebesine
   veya SL/TP'yi genis mesafelere zorluyorsa, bu bir "hangi ufku seceyim" karari DEGIL, acik bir
   CELISKI BULGUSUDUR — karar vermeyin, "Celiski Bulgusu" baslikli ayri bir bolumde acikca
   isaretleyip Orkestrator'a/Ertan'a raporlayin.
5. Not: C (Breakout/kirilim) ayri bir tarama konusu DEGILDIR. A-taramasi yaparken, kirilim
   noktalarinin (Donchian-tipi N-bar yuksek/dusuk asimi gibi) A'nin devam-sinyaline katki
   sağlayıp saglamadigina dair bir alt-not/gozlem ekleyin (orn. "devam orani, kirilim-tipi giris
   ile MA-kesisim-tipi giris arasinda farkli mi") — ayri bir hipotez/model kurmayin, sadece
   gozlemsel not.

**J-TARAMASI (ikincil, ucuz):**
1. Gun-ici saat (session: Asya/Avrupa/ABD) ve haftanin-gunu bazinda GOLD getiri profili.
2. Coklu-test duzeltmesi UYGULAYIN (orn. Bonferroni veya benzeri basit duzeltme — kac tane
   saat/gun kombinasyonu test edildiyse ona gore anlamlilik esigini ayarlayin). Duzeltmesiz
   ham p-degeri raporlamayin.
3. Yalniz GUCLU ve duzeltme-sonrasi anlamli bir sonuc varsa "hipoteze yukseltilebilir" olarak
   isaretleyin; aksi halde J'nin varsayilan rolu baska ailelerin (A) filtresi/feature'i olarak
   kalmasidir — bu turde J icin ayri bir hipotez/pipeline turu ONERMEYIN, sadece bulguyu
   raporlayin.

GECMIS CALISMA/CERCEVE DOSYASI:
- `C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md` (S1 tanimi, Madde 2)
- `C:\MilaYatirim\Justin\justin_gecmis_calisma.md` (HEDEF_PF/DD, kasa, risk%, lot kurali —
  referans amacli, bu tur bir tam tur olmadigi icin bu sabitler dogrudan kullanilmiyor ama
  baglam icin faydali)
- `C:\MilaYatirim\Justin\orkestrator_gorus_strateji_ailesi_plani_20260712.md` (Bolum 3, Adim 0
  orijinal tanimi + Bolum 2.3 gerilim analizi)
- `C:\MilaYatirim\Justin\justin_strateji_ailesi_plani_ertan_kararlari_20260714.md` (Ertan'in
  5 cevabi + A/C duzeltmesi — bu gorevin governance kaynagi, ozellikle Bolum 1/Cevap-3 ve
  Bolum 3)

ONCEKI ADIMIN CIKTISI: yok — bu, strateji-ailesi-plani dalinin ilk somut gorevlendirmesidir
(plan taslagi ve governance kaydi disinda onceki bir agent raporu yok).

VERI IZOLASYONU — ZORUNLU KISIT (degismedi): Bu proje kapsaminda baska bir dahili sistemin
(MilaGold/Lisa/Signal GPT) bulgu/veri/parametresine erisim veya atif YOKTUR; tamamen bagimsiz/
orijinal analiz yapilmalidir. Tek veri kaynagi XM/MT5 fiyat verisidir (dogrudan MetaTrader5
kutuphanesi araciligiyla). Calisma dizini yalniz `C:\MilaYatirim\Justin\` altindadir — baska
proje dosyasi format/sablon referansi icin bile acilmaz.

BEKLENEN CIKTI: Markdown rapor, `C:\MilaYatirim\Justin\arastirmaci_gold_scalping_adim0_tarama_
raporu.md`. Bolumler: Ozet, A-Taramasi Bulgulari (ufuk bazinda otokorelasyon/devam-orani
tablosu + S1 sonucu + kirilim-notu), **Celiski Bulgusu (varsa — S1 vs scalping-SL/TP)**,
J-Taramasi Bulgulari (coklu-test-duzeltmeli), Onerilen Sonraki Adim (Adim 1'e gecis icin hangi
ufuk/parametrelerin aday oldugu — KARAR degil, Stratejist'in degerlendirecegi aday listesi),
Sinirlamalar, Izolasyon Notu.

ONAY NOKTASI: Bilgi notu — bu gorev salt-arastirma/analiz niteliginde (on-tarama, hipotez/
karar uretmiyor), canli sisteme/hesaba hicbir etkisi yok. 4 boyutlu degerlendirme: geri
donulebilirlik tam, mali etki yok (Justin arastirma/demo asamasi, canli hesap yok), tespit
gecikmesi konusu degil, etki alani dar (yalniz Justin klasoru) → STOP-genis/bilgi-notu
kategorisi, Ertan onayi gerekmez. Rapor uretildiginde Ertan'a Telegram bilgi notu +
Orkestrator_Loglar kaydi dusulecek (10 Temmuz kurali geregi).

SAYAC NOTU (onemli, Stratejist/Risk Analisti karistirmasin diye): Bu gorev gunluk pipeline
dongu sinirina (5/gun, Stratejist cagrisi = 1 tur) SAYILMAZ — Stratejist bu asamada devrede
degildir. Aile-bazli RED sayacina (Bolum 4.1) da sayilmaz — bu sayac Risk Analisti karariyla
isler, bu turde Risk Analisti yoktur. Bu, sadece Arastirmaci-duzeyinde bir on-olcumdur.
