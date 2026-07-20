# ORKESTRATOR → YOL1 AGENT CAGRI SABLONU

Bu sablon, Orkestrator'un Arastirmaci, Stratejist, Backtest Muhendisi veya Risk Analisti'nden herhangi birini tetiklerken dolduracagi genel formattır. Dördü icin de ayni yapı kullanilir — sadece HEDEF AGENT ve ona bagli alanlar degisir.

Her cagri, bu sablonla doldurulmus haliyle bir dosyaya kaydedilir (bkz. altta "Kayit" bolumu) — boylece hangi ajana ne zaman hangi gorevin verildigi iz birakir, sadece bellek-ici kalmaz.

---

## Doldurulacak Alanlar

```
=== ORKESTRATOR CAGRISI ===
TARIH-SAAT        : [YYYY-MM-DD HH:MM]
HEDEF AGENT        : [Arastirmaci / Stratejist / Backtest Muhendisi / Risk Analisti]
SISTEM PROMPTU YOLU: C:\MilaYatirim\mila-yatirim-sistemi\Agentlar\[agent_adi]_system_prompt.md

PROJE              : [orn. Gold, Justin, Pariteler, vb.]
GOREV              : [Bu cagri icin somut, tek is tanimi — genis/belirsiz olmasin.
                       Ornek (Arastirmaci): "Gold icin Konu 3: Asya geri donus analizini yap"
                       Ornek (Stratejist): "Arastirmaci raporuna dayanarak 2-3 hipotez uret"
                       Ornek (Backtest M.): "Hipotez X'i dogrula"
                       Ornek (Risk A.): "Backtest raporu X'i degerlendir, karar ver"]

GECMIS CALISMA/CERCEVE DOSYASI: [varsa proje-ozel dosyanin tam yolu,
                                   yoksa "yok — agent gerekli bilgiyi ister/sifirdan baslar"]

ONCEKI ADIMIN CIKTISI: [varsa bir onceki ajanin urettigi rapor/dosyanin tam yolu,
                         yoksa "yok — zincirin ilk adimi"]

BEKLENEN CIKTI     : [Uretilecek rapor/dosyanin adi ve kaydedilecegi klasor]
                       Onerilen isimlendirme: [agent]_raporu_[proje]_[YYYYMMDD].md

ONAY NOKTASI       : [Bu adimin sonucu sadece bilgi notu mu (Ertan'a Telegram/dashboard
                       ile bildirilir, onay beklenmez) yoksa bir sonraki adima gecmeden
                       once Ertan'in onayi mi gerekiyor — Mimari Boyutlar E'deki
                       STOP-genis/START-dar ayrimina gore belirlenir]
```

---

## Kayit

Doldurulmus her cagri, asagidaki konuma kaydedilir (tek yazici Orkestrator'dir):

```
C:\MilaYatirim\Orkestrator_Loglar\cagri_[YYYYMMDD]_[HHMM]_[agent_adi].md
```

Bu, hem izlenebilirlik hem de "bu ajan en son ne zaman, ne icin cagrildi" sorusuna hizli cevap saglar. Raporlama Agent'inin gece raporuna bu log da dahil edilebilir (ileride degerlendirilebilir).

---

## Notlar

- **GOREV alani genis olmamali.** "Arastirma yap" gibi belirsiz bir gorev yerine, Yol1'in sabit sirasina (Arastirmaci → Stratejist → Backtest Muhendisi → Risk Analisti) uygun, tek ve somut bir is tanimlanmalidir.
- **GECMIS CALISMA/CERCEVE DOSYASI** alani bos birakilirsa, ilgili ajanin kendi sistem promptundaki "Ise Baslamadan Once" bolumu geregi, ajan bu bilgiyi ya sizden/Orkestrator'dan ister ya da (Arastirmaci gibi tamamen ozgur olanlarda) sifirdan baslar.
- **MT5 veri erisimi dogrulandi (8 Temmuz):** Arastirmaci ve Backtest Muhendisi, VPS'teki headless Claude Code uzerinden dogrudan `mt5.initialize()` ile MT5'e baglanabilir — RDP/GUI oturumu gerekmez, Session 0 kisitlamasi bu senaryoda gecerli degildir (sadece MT5 terminalini ilk kez baslatma/GUI etkilesimi gerektiren islemler icin gecerlidir).
- **ONAY NOKTASI** her zaman doldurulmalidir — bos birakilmamali. Read-only arastirma/analiz adimlari (orn. Arastirmaci'nin veri okuyup rapor uretmesi) genelde sadece bilgi notu gerektirir; duzeltici/degistirici bir islem (orn. canli sisteme bir filtre eklenmesi) START/CHANGE sayilir ve onay gerektirir.
