import time
import re
import os
import sys
import json
import logging
import msvcrt
import requests
from datetime import datetime

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import easyocr
import MetaTrader5 as mt5

sys.path.insert(0, r"C:\MilaYatirim\MilaGold")
try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
except Exception:
    TELEGRAM_TOKEN = None
    TELEGRAM_CHAT_ID = None

# --- AYARLAR ---
SIGNAL_URL      = "https://signalgpt.ai/ai-signals"
SIGNAL_FILE     = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\signal.json"
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR  = os.path.join(BASE_DIR, "detay_kartlari")
ARSIV_DIR       = os.path.join(BASE_DIR, "detay_kartlari_tekrar")
LOG_FILE        = os.path.join(BASE_DIR, "detay_karti_log.txt")
DURUM_FILE      = os.path.join(BASE_DIR, "detay_karti_toplama_durumu.json")
KOMBINASYON_FILE = os.path.join(BASE_DIR, "detay_karti_kombinasyonlar.json")
ILERLEME_DURUM_FILE = os.path.join(BASE_DIR, "detay_karti_durum.json")

SYMBOL          = "GOLD"
PRICE_TIER      = 25.0   # dolar - fiyat esigi dilim genisligi
HEDEF_KART_SAYISI = 50   # benzersiz (yon, entry) kombinasyonu hedefi

CALISMA_BASLANGIC_SAAT = 5   # 05:00 - 00:00 (dahil degil) araligi calisir, 00:00-05:00 hicbir tetikleme yapmaz

# Kalibre edilmis (13/07/2026, EasyOCR ile olculdu) koordinatlar - pencere 1366x641 viewport, DPR=1
DETAIL_CLICK_FALLBACK = (280, 520)   # OCR "Detail" metnini bulamazsa kullanilmaz (bulunamazsa zaten kart yok sayilir)
GO_BACK_CLICK         = (1139, 49)

ENTRY_MATCH_TOLERANCE = 0.5  # signal.json entry vs ekrandan OCR ile okunan entry - izin verilen fark

ANA_POLL_ARALIGI       = 30   # saniye - pencere icinde tetikleyici kontrolu
PENCERE_DISI_BEKLEME   = 300  # saniye - 00:00-05:00 arasi kontrol araligi
TAMAMLANDI_BEKLEME     = 300  # saniye - hedef tamamlaninca duraklama kontrol araligi

# --- TEK INSTANCE KILIDI ---
_LOCK_FILE_PATH = os.path.join(BASE_DIR, "detay_karti_okuyucu.lock")
_lock_fh = open(_LOCK_FILE_PATH, "w")
try:
    msvcrt.locking(_lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
except OSError:
    print("[Detay Karti Okuyucu] Baska bir instance zaten calisiyor. Bu process sonlandiriliyor.")
    _lock_fh.close()
    raise SystemExit(0)

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(ARSIV_DIR, exist_ok=True)

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()


def kombinasyonlari_yukle():
    if not os.path.exists(KOMBINASYON_FILE):
        return []
    try:
        with open(KOMBINASYON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"{KOMBINASYON_FILE} okuma hatasi: {e}")
        return []


def kombinasyon_kaydet(yon, entry, dosya_adi):
    _kayitlar.append({
        "yon": yon,
        "entry": entry,
        "dosya": dosya_adi,
        "zaman": datetime.now().isoformat(),
    })
    try:
        with open(KOMBINASYON_FILE, "w", encoding="utf-8") as f:
            json.dump(_kayitlar, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log.warning(f"{KOMBINASYON_FILE} yazma hatasi: {e}")


# Onceki oturumlardan devralinan benzersiz (yon, entry) kombinasyonlari - restart'ta sifirlanmaz
_kayitlar = kombinasyonlari_yukle()
_gorulen  = {(k["yon"], k["entry"]) for k in _kayitlar}
log.info(f"Kombinasyon durumu yuklendi: {len(_gorulen)}/{HEDEF_KART_SAYISI} benzersiz (yon, entry).")


def telegram_bildir(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        log.warning(f"Telegram hatasi: {e}")


# --- OCR ---
log.info("EasyOCR yukleniyor...")
reader = easyocr.Reader(['en'], gpu=False)
log.info("EasyOCR hazir.")


def get_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    # Kendi sekmemizi ac - OCR agent'in sekmesine dokunmuyoruz
    driver.execute_script("window.open('about:blank', '_blank');")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])

    driver.get(SIGNAL_URL)
    log.info("Signal GPT sayfasina gidildi (kendi sekme).")
    time.sleep(30)
    return driver


def cdp_click(driver, x, y):
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1
    })
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1
    })


def escape_tusu(driver):
    """Go back tiklamasi sirasinda (press/release arasi sayfa gecisi nedeniyle) kazara
    acilabilen hesap menusunu (Profile/Email preferences/Log out) kapatmak icin."""
    driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
        "type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27
    })
    driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
        "type": "keyUp", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27
    })


def ekrani_oku(driver):
    """Kendi sekmenin ekran goruntusunu EasyOCR ile okur.
    Doner: (detail_bulundu, detail_merkez_xy, entry_deger)"""
    png_bytes = driver.get_screenshot_as_png()
    results = reader.readtext(png_bytes)

    detail_bulundu = False
    detail_merkez = None
    full_text = " ".join(text for (_, text, _) in results).upper()

    for (bbox, text, _conf) in results:
        if "detail" in text.lower():
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            detail_merkez = (sum(xs) / 4, sum(ys) / 4)
            detail_bulundu = True
            break

    entry_deger = None
    match = re.search(r'ENTRY[:\s]+(\d{4,5}\.?\d*)', full_text)
    if match:
        entry_deger = float(match.group(1))

    return detail_bulundu, detail_merkez, entry_deger


def signal_json_oku():
    try:
        with open(SIGNAL_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"signal.json okuma hatasi: {e}")
        return None


def hedefe_ulasildi_mi_kontrol_et():
    """Benzersiz (yon, entry) kombinasyon sayisi hedefe ulastiysa durum dosyasini yazar
    (bir kez) ve True doner - ana dongu bunu gorunce duraklar."""
    if os.path.exists(DURUM_FILE):
        return True
    if len(_gorulen) >= HEDEF_KART_SAYISI:
        durum = {
            "benzersiz_kombinasyon_sayisi": len(_gorulen),
            "tamamlanma_zamani": datetime.now().isoformat(),
        }
        with open(DURUM_FILE, "w") as f:
            json.dump(durum, f, indent=2)
        log.info(f"{len(_gorulen)} benzersiz kombinasyon tamamlandi - durum dosyasi yazildi, ana dongu duraklatiliyor.")
        telegram_bildir(f"[TersMuhendislik] {len(_gorulen)} benzersiz (yon,entry) kombinasyonu tamamlandi - toplama duraklatildi")
        return True
    return False


def ilerleme_durumunu_yaz(tetikleyici):
    """Dashboard icin ilerleme dosyasini tamamen yeniden yazar. Her tetikleyici donguden
    sonra (basarili kart kaydi VEYA "kart yok" durumu farketmeksizin) cagrilir - tek yazici
    bu fonksiyon/bu script'tir."""
    durum = {
        "toplanan": len(_gorulen),
        "hedef": HEDEF_KART_SAYISI,
        "son_kart_zamani": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "son_tetikleyici": tetikleyici,
    }
    try:
        with open(ILERLEME_DURUM_FILE, "w", encoding="utf-8") as f:
            json.dump(durum, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log.warning(f"{ILERLEME_DURUM_FILE} yazma hatasi: {e}")


def kart_yakala(driver, tetikleyici, detail_merkez, yon, entry):
    x, y = detail_merkez if detail_merkez else DETAIL_CLICK_FALLBACK
    cdp_click(driver, x, y)
    time.sleep(3)

    dosya_adi = f"detay_karti_{datetime.now():%Y%m%d_%H%M}_{tetikleyici}.png"
    dosya_yolu = os.path.join(SCREENSHOT_DIR, dosya_adi)
    driver.save_screenshot(dosya_yolu)
    log.info(f"{tetikleyici}: screenshot alindi - {dosya_adi}")

    cdp_click(driver, *GO_BACK_CLICK)
    time.sleep(1.5)
    escape_tusu(driver)
    time.sleep(0.5)

    _gorulen.add((yon, entry))
    kombinasyon_kaydet(yon, entry, dosya_adi)
    log.info(f"Benzersiz kombinasyon: {len(_gorulen)}/{HEDEF_KART_SAYISI} ({yon} @ {entry})")

    hedefe_ulasildi_mi_kontrol_et()


def tetiklemeyi_isle(driver, tetikleyici, esik_deger=None):
    if hedefe_ulasildi_mi_kontrol_et():
        return  # hedef tamamlandi, yeni kart aranmiyor

    signal_data = signal_json_oku()
    hedef_entry     = signal_data.get("entry") if signal_data else None
    hedef_direction = signal_data.get("direction") if signal_data else None

    if hedef_entry is None or hedef_direction is None:
        if esik_deger is not None:
            log.info(f"fiyat esigi {esik_deger}'e ulasildi, aktif sinyal yok")
        else:
            log.info(f"{tetikleyici}: kart yok (signal.json'da entry/yon yok)")
        return

    if (hedef_direction, hedef_entry) in _gorulen:
        log.info(f"{tetikleyici}: {hedef_direction} @ {hedef_entry} zaten kayitli - tekrar cekilmiyor")
        return

    detail_bulundu, detail_merkez, ocr_entry = ekrani_oku(driver)

    if not detail_bulundu:
        if esik_deger is not None:
            log.info(f"fiyat esigi {esik_deger}'e ulasildi, aktif sinyal yok")
        else:
            log.info(f"{tetikleyici}: kart yok (Detail metni bulunamadi)")
        return

    uyusuyor = ocr_entry is not None and abs(ocr_entry - hedef_entry) <= ENTRY_MATCH_TOLERANCE

    if not uyusuyor:
        log.info(f"{tetikleyici}: entry uyusmuyor (signal.json={hedef_entry}, ekran={ocr_entry}) - sayfa yenileniyor")
        try:
            driver.get(SIGNAL_URL)
            time.sleep(8)
            driver.execute_script("window.scrollTo(0, 0)")
        except Exception as e:
            log.warning(f"{tetikleyici}: sayfa yenileme hatasi: {e}")

        detail_bulundu, detail_merkez, ocr_entry = ekrani_oku(driver)
        uyusuyor = detail_bulundu and ocr_entry is not None and abs(ocr_entry - hedef_entry) <= ENTRY_MATCH_TOLERANCE

        if not uyusuyor:
            log.info(f"{tetikleyici}: entry hala uyusmuyor (signal.json={hedef_entry}, ekran={ocr_entry}) - bu tur gecildi")
            return

    kart_yakala(driver, tetikleyici, detail_merkez, hedef_direction, hedef_entry)


def calisma_penceresinde_mi(now=None):
    if now is None:
        now = datetime.now()
    return CALISMA_BASLANGIC_SAAT <= now.hour < 24


def main():
    log.info("=" * 50)
    log.info("Detay Karti Okuyucu - Faz 1 (SS biriktirme)")
    log.info("=" * 50)

    if not mt5.initialize():
        log.error(f"MT5 baglanma hatasi: {mt5.last_error()}")
    else:
        log.info("MT5 baglandi.")

    driver = get_driver()

    son_saat_tetiklendi = None
    son_fiyat_dilimi = None

    log.info("Ana donguye giriliyor...")

    while True:
        try:
            now = datetime.now()

            if hedefe_ulasildi_mi_kontrol_et():
                time.sleep(TAMAMLANDI_BEKLEME)
                continue

            if not calisma_penceresinde_mi(now):
                time.sleep(PENCERE_DISI_BEKLEME)
                continue

            if son_saat_tetiklendi != now.hour:
                son_saat_tetiklendi = now.hour
                tetiklemeyi_isle(driver, "saatlik")
                ilerleme_durumunu_yaz("saatlik")

            try:
                tick = mt5.symbol_info_tick(SYMBOL)
                if tick is not None:
                    dilim = int(tick.bid // PRICE_TIER) * int(PRICE_TIER)
                    if son_fiyat_dilimi is not None and dilim != son_fiyat_dilimi:
                        tetiklemeyi_isle(driver, "fiyat_esigi", esik_deger=dilim)
                        ilerleme_durumunu_yaz("fiyat_esigi")
                    son_fiyat_dilimi = dilim
                else:
                    log.warning("symbol_info_tick None dondu.")
            except Exception as e:
                log.error(f"MT5 fiyat okuma hatasi: {e}")

            time.sleep(ANA_POLL_ARALIGI)

        except KeyboardInterrupt:
            log.info("Detay Karti Okuyucu durduruldu.")
            break
        except Exception as e:
            log.error(f"Dongu hatasi: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
