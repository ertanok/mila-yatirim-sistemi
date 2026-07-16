# PASSKEY (WebAuthn) + MANUEL EMIR GIRISI — GOREV TANIMI

**Tarih:** 16 Temmuz 2026
**Durum:** Onaylandi, implementasyona hazir
**Ilgili proje:** Mila Dashboard (Guvenlik/Kontrol Katmani) + MilaGold (Manuel Emir)

---

## 1) AMAC

Su anda planlanan Telegram onay-kodu katmani **iptal edildi**. Yerine, dashboard giris ve
yuksek-riskli islem onayi icin **Passkey (WebAuthn)** kullanilacak. Bu, hem giris guvenligini
hem de manuel emir onayini tek mekanizmayla cozer — ayri bir kod bekleme/dogrulama sureci
gerektirmez.

Ayni gorev kapsaminda, MilaGold projesine **manuel emir girisi** ozelligi eklenir: Ertan
dashboard'dan yon + entry fiyati girip Passkey ile onaylayinca, MT5 agent bu emri OCR
sinyalleriyle ayni sekilde (SL hesaplama, trailing, emir tipi siniflandirma) isler.

---

## 2) KAPSAM

### A) Passkey / WebAuthn Katmani

**Backend — `milaboard_api.py`:**
- Kutuphane: `py_webauthn` (pip install)
- Yeni endpoint'ler:
  - `POST /webauthn/register/begin` — challenge uretir, kullaniciya doner
  - `POST /webauthn/register/complete` — cihazdan gelen public key + credential_id'yi kaydeder
  - `POST /webauthn/login/begin` — challenge uretir
  - `POST /webauthn/login/complete` — imzayi dogrular, basariliysa oturum token'i uretir (mevcut
    24 saatlik token mantigi korunur)
  - `POST /webauthn/reauth/begin` ve `/webauthn/reauth/complete` — manuel emir gibi tek islemlik
    yeniden-dogrulama icin (oturum token'indan bagimsiz, her cagrida taze challenge)
- **Credential store:** `webauthn_credentials.json`
  - Tek yazicisi: `milaboard_api.py`
  - Alanlar: `credential_id`, `public_key`, `device_label` (orn. "laptop", "telefon"),
    `created_at`, `last_used_at`
  - Bu dosya `.gitignore`'a eklenir (kimlik dogrulama materyali, config.py ile ayni kategoride)
- **Rate-limit:** Ayni kimlik (credential_id) icin ust uste basarisiz dogrulama denemesi olursa
  kisa sureli kilitleme (orn. 5 basarisiz deneme → 5 dk kilit). Mevcut brute-force onleme
  prensibiyle tutarli.

**Frontend — `dashboard.html`:**
- Giris ekranina "Passkey ile giris" secenegi eklenir (`navigator.credentials.get()`)
- Ilk kurulum akisi: mevcut sifreyle bir kereye mahsus giris yapildiktan sonra "Bu cihazi
  Passkey olarak ekle" butonu gorunur (`navigator.credentials.create()`)
  - Iki cihaz ayri ayri kaydedilir: laptop (Windows Hello PIN) ve telefon (yuz tanima)
- Manuel emir formu gonderiminde: mevcut oturum token'ina guvenilmez, form submit anında
  `navigator.credentials.get()` ile taze bir Passkey dogrulamasi istenir. Basarisiz olursa
  islem gonderilmez.

**Domain/HTTPS notu:** WebAuthn sabit domain + HTTPS gerektirir. Mevcut Cloudflare Tunnel
kurulumu bu sarti zaten karsiliyor, ek islem gerekmiyor.

**Telegram onay-kodu katmaninin kaldirilmasi:**
- Eger onceki oturumlarda bu yonde kismi bir implementasyon baslatildiysa (kod uretme/gonderme
  mantigi), kaldirilir. Bu gorev tanimi, o mekanizmanin yerini alir.

---

### B) Manuel Emir Girisi (MilaGold)

**Yeni dosya:** `manuel_signal.json`
- Sema, mevcut `signal.json` ile **birebir ayni** (yon, entry fiyati, timestamp, ve
  `signal.json`'da zaten var olan diger zorunlu alanlar — mevcut dosyadaki alan adlarina
  sadik kalinir)
- Tek yazicisi: `milaboard_api.py`
- MT5 agent tarafindan sadece okunur, islendikten sonra MT5 agent tarafindan temizlenir/
  isaretlenir (mevcut `signal.json` "islendi" mantigina esdeger — tekrar islenmeyi onlemek icin)

**Dashboard formu (yeni bilesen):**
- Alanlar: **Yon** (Buy/Sell), **Fiyat** (entry)
- Baska hicbir alan yok — SL, TP, lot, emir tipi (Stop/Limit) formda **gösterilmez**, mevcut
  MilaGold mantigi bunlari otomatik belirler (asagida)
- Submit → Passkey re-auth (yukarida A bolumu) → basariliysa `milaboard_api.py`
  `manuel_signal.json`'a yazar

**`milagold_mt5_agent.py` degisikligi:**
- Mevcut dongude, `signal.json`'a ek olarak `manuel_signal.json` da okunur
- **Kritik fark:** `manuel_signal.json`'dan gelen sinyal, M5 EMA20 ve EMA100 Streak
  filtrelerinden **gecirilmez** — dogrudan mevcut isleme fonksiyonuna verilir
- Isleme fonksiyonu (emir tipi siniflandirma — piyasa fiyatina gore Stop/Limit karari, SL
  mesafe hesaplama, trailing stop baglama) **OCR sinyaliyle ayni kod yolunu** kullanir —
  ayri bir fonksiyon yazilmaz, mevcut fonksiyon iki kaynaktan da cagrilir
- TP davranisi mevcut mantikla ayni kalir: MT5'e TP gonderilmez, trailing stop OCR
  sinyalindeki gibi calisir

**Loglama/bildirim:**
- Manuel emir isleyisi, mevcut Telegram bildirim kanalindan (islem acildi/atlandi bildirimleri)
  gecer — kaynak ("manuel" vs "OCR") mesajda belirtilir, boylece log/gecmis karisikligi olmaz

---

## 3) DOSYA YAPISI OZETI

```
C:\MilaYatirim\MilaGold\
  signal.json              (mevcut, OCR agent yazar)
  manuel_signal.json        (YENI, milaboard_api.py yazar)
  milagold_mt5_agent.py     (GUNCELLENECEK — iki dosyayi da okur, filtre atlama mantigi)

C:\MilaYatirim\ (proje-genel dashboard katmani)
  milaboard_api.py          (GUNCELLENECEK — webauthn endpoint'leri + manuel emir endpoint'i)
  webauthn_credentials.json (YENI, .gitignore'a eklenecek)
  dashboard.html             (GUNCELLENECEK — passkey giris/kurulum + manuel emir formu)
```

---

## 4) UYGULAMA SIRASI (onerilen)

1. `py_webauthn` kurulumu + `milaboard_api.py`'ye register/login endpoint'leri
2. Dashboard'a Passkey kurulum akisi (laptop + telefon kaydi, mevcut sifreyle bir kereye
   mahsus giris uzerinden)
3. Test: iki cihazdan da Passkey ile giris calisiyor mu
4. Reauth endpoint'i + manuel emir formu (frontend)
5. `manuel_signal.json` + `milagold_mt5_agent.py` guncellemesi (filtre-atlama mantigi)
6. Uctan uca test: demo hesapta manuel emir gir → Passkey onayi → MT5'te emir acildi →
   agent trailing/SL'i devraldi mi kontrol
7. Onay sonrasi git commit + push + VPS pull (mevcut deploy pipeline)

---

## 5) DIKKAT NOKTALARI (Claude Code icin)

- `webauthn_credentials.json` ve manuel_signal.json GIT'E COMMIT EDILMEZ (credential/gecici
  veri) — `.gitignore`'a eklenmesi ilk adimda yapilmali
- Sistem promptu/gorev tanimi dosyalarinda oldugu gibi, `milagold_mt5_agent.py` uzerindeki
  degisiklik **diff olarak once gosterilir**, Ertan onayi alinmadan uygulanmaz (mevcut kural)
- Manuel emir icin lot hesaplama mevcut kasa-bazli kurala (200 USD = 0.01 lot) tabidir,
  formda ayrica sorulmaz
