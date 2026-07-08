# RAPORLAMA AGENT'i — GOREV TANIMI

Gorev tanimidir, sistem promptu degil — kural-tabanli, Claude API'ye cagri yapmaz. Claude Code'a yapim talimati olarak verilir.

---

## 1. Amac

Her gece, piyasa kapanisi sonrasi gunun performans raporunu cikarir: islem bazinda (saat + entry eslemesi) Lisa ile karsilastirma, TP1/TP2/TP3/SL sayilari, win rate, kar faktoru, toplam pip.

**Tek bir projeye ozgu degil** — su an MilaGold icin calisiyor, ileride diger projeler (Justin, Ertan Stratejisi) eklendikce genisleyebilir.

---

## 2. Calisma Bicimi

**Surekli-donen Python script — Task Scheduler DEGiL.** Sebep: Session 0 izolasyon riski, yeni agentler icin surekli-donen script tercih ediliyor (Orkestrator sistem promptunda da ayni ilke var).

Script kendi ici dongude zamani kontrol eder, piyasa kapanisindan sonra (23:55 gap-koruma penceresiyle uyumlu, orn. 00:05'te) gunluk raporu bir kez uretir.

---

## 3. Rapor Icerigi (PI'deki Raporlama Metrikleri ile ayni)

- TP1/TP2/TP3/SL sayilari ve toplam pip
- Toplam islem sayisi
- Win rate
- Ortalama kar/zarar
- Kar faktoru (profit factor)
- Lisa karsilastirmasi (milagold_trades.json vs lisa_performance.json, HH:MM + entry fiyati eslemesiyle)

---

## 4. Dosya Formati ve Konumu

- **Rapor JSON:** tarihli dosya adi, `rapor_{YYYYMMDD}.json`
- **Konum:** `Performans Raporlari/MilaGold Performans/` altinda (Dashboard'daki mevcut kararla ayni — rapor kartlari yerelde silinmeden gizlenebilir, arsiv bozulmaz)
- **Heartbeat:** `raporlama_status.json` — her dongude (orn. birkac dakikada bir) guncellenir, son basarili rapor uretim zamanini da icerir

---

## 5. Bildirim

**Telegram sadece esik asiminda gider — her gece degil.** Esik ne olacagi (orn. gunluk P&L belirli bir seviyenin altina duserse, ya da win rate/kar faktoru beklenenden ciddi sapmissa) **TBD** — gercek baseline veri biriktikce netlesecek, simdi tahmini bir sayi konmuyor.

---

## 6. Orkestrator ile Iliski (heartbeat-retry deseni, onceden tasarlandi)

Orkestrator, `raporlama_status.json`'daki son basarili rapor zamanini bekler. Beklenen saatten **~10 dakika sonra** kontrol eder, bayatsa **3 kereye kadar retry** dener, hala basarisizsa Seviye 1 bildirimi (Telegram uyarisi) tetiklenir. Bu retry/escalate mantigi Orkestrator'in sorumlulugu — Raporlama Agent'i sadece heartbeat dosyasini dogru/guncel tutmakla yukumlu.

---

## 7. Acik Sorular / TBD

- Bildirim esigi (Bolum 5) — hangi metrik, hangi sinir degeri
- Tam uretim saati (00:05 onerisi, kesin degil)
- Diger projeler eklendikce rapor formatinin nasil genisleyecegi (su an sadece MilaGold)
