# JUSTIN — BACKTEST MUHENDISI KALICI ON-KONTROL STANDARDI

Statu: KALICI/STANDART (proje-genelinde gecerli) — hipotez/yaklasima ozel degil.
Olusturulma: Orkestrator, Faz 0 (Ertan'in (a) + 3-sertlestirme onayi, 14 Temmuz 2026),
kaynak: orkestrator_degerlendirme_madde7_gold_scalping_20260714.md, Bolum 5 (Faz 0, madde 2).

Amac: Her yeni Backtest Muhendisi gorev tanimi bu dosyaya REFERANS VERMELI (GECMIS CALISMA/
CERCEVE DOSYASI bolumunde). Asagidaki maddeler, hangi hipotez/yaklasim olursa olsun, her
backtest turunde on-kontrol asamasinda kontrol edilir. Madde eklenirse/degisirse bu dosya
guncellenir — her seferinde gorev dosyasina yeniden yazilmaz.

---

## 1) DST / Saat-Eslesme Dogrulamasi (H1/H2/H3'te 4 kez bagimsiz teyit edildi)

- VPS'in gercek saat dilimi davranisi (GMT+3, DST gecisleri dahil) her yeni backtest turunde
  BAGIMSIZ olarak dogrulanmali — onceki turden devralinmaz.
- Herhangi bir zaman/oturum-bazli filtre (seans saatleri, gun-ici konum, oturum acilis/kapanis
  mesafesi vb.) kullanan HER yaklasimda zorunlu; yaklasim kural-tabanli veya ML olsun fark etmez.
- Kaynak: Stratejist v5 raporu, Bolum 4 Madde 3 ("...ayni DST dogrulamasi... o yaklasim icin de
  Backtest Muhendisi'nin ON-KONTROL listesinde YER ALMALIDIR").

## 2) Maliyet-Orani On-Kontrolu (YENI — S1, 14 Temmuz 2026 sertlestirmesi)

- Her yeni yaklasimin **hedef/beklenen islem-basi brut kazanci**, tahmini toplam islem
  maliyetinin (spread + slipaj) **en az ~15-20 kati** olacak sekilde tasarlanmis olmali.
- Referans kalibrasyon: H2/M5 kesitinde gozlenen ~%3,7 slipaj/ATR orani (bkz.
  backtest_muhendisi_raporu_justin_gold_scalping_hipotez2_20260711.md, satir ~131) "fiziksel
  olarak tutarli" kabul edilen bir maliyet-yuku ornegidir; Hipotez 3'teki M1 senaryosunda
  goruldugu gibi maliyet ATR'nin ~%15-19'una / SL mesafesinin ~%28-34'une ulasan bir tasarim
  bu on-kontrolu GECEMEZ.
- Bu oran on-kontrol asamasinda (ana test baslamadan once) tahmini olarak hesaplanmali; orani
  karsilamayan tasarimlar **otomatik olarak elenir** — ana teste/walk-forward'a gecilmez, sonuc
  Stratejist'e "on-kontrolde elendi, maliyet-orani yetersiz" olarak bildirilir.
- Gerekce: Orkestrator'un "maliyet duvari" analizi (bkz. degerlendirme dosyasi Bolum 2) — M1
  scalping ailesinde PF<1 sonuclarinin buyuk kismi sinyalin ters calismasindan degil, brut
  edge'in maliyet duvari tarafindan yutulmasindan kaynaklaniyordu.

## 3) SL/TP — Her Yaklasima Ozel, Otomatik Tasima Yok

- SL/TP semasi (mesafe, RR orani) her yeni yaklasim icin Stratejist tarafindan O YAKLASIMA OZEL
  belirlenir. Backtest Muhendisi onceki hipotezden/yaklasimdan SL/TP degerini OTOMATIK TASIMAZ.
- Bu, Stratejist'in kendi v5 raporundaki (Bolum 4, Madde 1) taahhududur: "Ileriye donuk: eger
  secenek (a) tercih edilirse ve yeni yaklasim da bir SL/TP semasi gerektiriyorsa, bu kez
  Stratejist yeni yaklasima ozel bir deger/aralik belirtecegim — otomatik tasima yerine."
- Backtest Muhendisi, gorev tanimindaki SL/TP degeri BOSSA veya "onceki turden tasi" gibi bir
  talimat iceriyorsa bunu bir eksiklik olarak isaretlemeli, Orkestrator'a/Stratejist'e geri
  bildirmeli — kendi basina varsayilan bir deger uydurmamali.

---

## Kullanim Notu

Yeni bir Backtest Muhendisi gorev dosyasi yazilirken "GECMIS CALISMA/CERCEVE DOSYASI" bolumune
su satir eklenir:
`C:\MilaYatirim\Justin\justin_backtest_onkontrol_standardi.md (kalici on-kontrol standardi —
DST, maliyet-orani, SL/TP-ozel-belirleme; tumu ZORUNLU)`
