# MiLA YATIRIM SiSTEMi — CLAUDE CODE TALiMATLARI

## Genel
- Sistem: Mila Yatirim Sistemi, cok bilesenli yatirim platformu. Trading gelirleri hem amac hem arac.
- Dil: Turkce (karaktersiz: u, o, i, s, c, g)
- Ertan vizyonu ve kararlari yonetir, Claude teknik implementasyonu yapar
- Karar mekanizmasi iceren her kod: once Turkce acikla, onayla, sonra yaz

## Proje Listesi (guncel — PI_cekirdek.md ile ayni numaralandirma)
1. MilaGold Stratejisi
2. XM Copy Trading
3. Justin Stratejisi
4. Ters Muhendislik
5. Pariteler Stratejisi
6. Gold Daytrading
7. Agnostic B Stratejisi
8. Agnostic A Stratejisi
9. Breakout Order

Her projenin teknik detayi: Ortak/bilgi_*.md dosyalarinda.

## Degisiklik Akisi (KESiN)
diff goster → onay al → uygula → commit → push → VPS pull

## Dokunulmaz Kural
`*_system_prompt.md` ve `*_gorev_tanimi.md` dosyalarina diff gostermeden ve onay almadan dokunulmaz.

## Agent Yetki Modeli (ozet)
Dort risk boyutu (geri donulebilirlik, mali etki, tespit gecikmesi, etki alani) — en kotu boyut kazanir.
**STOP otomatik olabilir, START/CHANGE (canliya gecis, reboot, restart) her zaman Ertan'in onayini gerektirir.**
Detay: Ortak/bilgi_multi_agent_mimarisi.md

## Dosya Yapisi
- Yerel: C:\MilaYatirim\ (ana klasor, dashboard, agent promptlari, deploy.py)
- VPS: C:\MilaYatirim\mila-yatirim-sistemi\ (git-tracked repo, tum proje kodlari)
- GitHub: ertanok/mila-yatirim-sistemi (public)
- VPS: baglanti bilgileri config.py'de (git disi), baglanti deploy.py (paramiko SSH/SFTP)

## Ortak Klasoru Icerigi (Project Knowledge'in Claude-Code-erisilebilir aynasi)
- bilgi_milagold.md — MilaGold teknik detay
- bilgi_diger_projeler.md — Copy Trading, Justin, Ters Muhendislik, Pariteler, Gold Daytrading, Agnostic A/B, Breakout Order
- bilgi_multi_agent_mimarisi.md — Model secimi, Mimari Boyutlar A-F, agent ekibi
- bilgi_dashboard_ve_teknik.md — Dashboard mimarisi, teknik altyapi, VPS/araclar
- agent_teknoloji_tablosu.md — Agent/model/kutuphane secim tablosu

Bu dosyalar Project Instructions'taki ayni-adli bilgi_*.md dosyalarinin senkron tutulan kopyalaridir — Claude Code Project Instructions'a erisemedigi icin bu ayna gereklidir. Guncelleme: Ertan PI tarafinda degisiklik yaptiginda, Claude Code'a yeni icerigi iletir, Ortak/ guncellenir.

Referans: Project Instructions, PI_cekirdek.md ile ayni mantik/uzunluk hedefi.
