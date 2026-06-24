import time
import re
import logging
import json
import os
from datetime import datetime
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import easyocr
import io

# --- AYARLAR ---
SIGNAL_URL  = "https://signalgpt.ai/ai-signals"
SIGNAL_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\signal.json"
CHECK_INTERVAL = 2  # saniye
FAIL_THRESHOLD = 10  # bu kadar ust uste okuma hatasinda sayfa yenilenir
LOG_FILE  = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_ocr_log.txt"
DEBUG_DIR = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\"

# SL ve TP hesaplama (sabit mesafeler)
SL_DISTANCE  = 5.0
TP1_DISTANCE = 3.0
TP2_DISTANCE = 5.0
TP3_DISTANCE = 8.0

# Entry degisikligi tespiti
ENTRY_CHANGE_THRESHOLD  = 0.5
ENTRY_CONFIRM_TOLERANCE = 0.5

# Liste karti koordinatlari (1366x768 cozunurluk)
LIST_LEFT   = 50
LIST_TOP    = 355
LIST_RIGHT  = 490
LIST_BOTTOM = 520

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

# --- OCR ---
log.info("EasyOCR yukleniyor...")
reader = easyocr.Reader(['en'], gpu=False)
log.info("EasyOCR hazir.")


def get_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver


def screenshot_region(driver, left, top, right, bottom, filename):
    screenshot = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(screenshot))
    region = img.crop((left, top, right, bottom))
    path = DEBUG_DIR + filename
    region.save(path)
    return path


def ocr_read(path):
    return reader.readtext(path, detail=0, paragraph=False)


def parse_list_card(texts):
    full = " ".join(texts).upper()
    card = {
        "has_signal": False,
        "status":     None,
        "direction":  None,
        "entry":      None,
        "signal_no":  None,
    }

    if "XAU" not in full and "GOLD" not in full:
        return card

    card["has_signal"] = True

    if "RUNN" in full:
        card["status"] = "RUNNING"
    elif "WAITING" in full or "WAITIN" in full or "NOT MATCHED" in full:
        card["status"] = "WAITING"
    elif "COMPLETED" in full or "CLOSED" in full:
        card["status"] = "CLOSED"

    if "SELL" in full:
        card["direction"] = "SELL"
    elif "BUY" in full:
        card["direction"] = "BUY"

    # Entry
    match = re.search(r'ENTRY[:\s]+(\d{4,5}\.?\d*)', full)
    if match:
        card["entry"] = float(match.group(1))
    else:
        nums = re.findall(r'\b(\d{4,5}\.?\d*)\b', full)
        gold = [float(n) for n in nums if 3000 < float(n) < 9000]
        if gold:
            card["entry"] = gold[0]

    # Sinyal numarasi (#6214 gibi)
    match = re.search(r'#(\d{4,6})', full)
    if match:
        card["signal_no"] = match.group(1)

    return card


def calculate_levels(direction, entry):
    if direction == "SELL":
        return {
            "sl":  round(entry + SL_DISTANCE,  2),
            "tp1": round(entry - TP1_DISTANCE, 2),
            "tp2": round(entry - TP2_DISTANCE, 2),
            "tp3": round(entry - TP3_DISTANCE, 2),
        }
    else:
        return {
            "sl":  round(entry - SL_DISTANCE,  2),
            "tp1": round(entry + TP1_DISTANCE, 2),
            "tp2": round(entry + TP2_DISTANCE, 2),
            "tp3": round(entry + TP3_DISTANCE, 2),
        }


def signal_from_card(card, confirmed=False):
    """Karttan yeni sinyal sozlugu olustur."""
    if card["status"] in ("RUNNING", "WAITING") and card["entry"] and card["direction"]:
        levels = calculate_levels(card["direction"], card["entry"])
        return {
            "signal_no": card["signal_no"],
            "direction": card["direction"],
            "entry":     card["entry"],
            "sl":        levels["sl"],
            "tp1":       levels["tp1"],
            "tp2":       levels["tp2"],
            "tp3":       levels["tp3"],
            "status":    card["status"],
            "time":      datetime.now().strftime("%H:%M:%S"),
            "processed": False,
            "confirmed": confirmed,
            "cancel":    False,
        }
    return None


def write_signal(signal):
    try:
        with open(SIGNAL_FILE, "w") as f:
            json.dump(signal, f, indent=2)
        log.info("signal.json yazildi.")
    except Exception as e:
        log.warning(f"signal.json yazma hatasi: {e}")


def update_signal_field(field, value):
    """signal.json'daki tek bir alani guncelle."""
    try:
        with open(SIGNAL_FILE, "r") as f:
            data = json.load(f)
        data[field] = value
        with open(SIGNAL_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.warning(f"signal.json guncelleme hatasi ({field}={value}): {e}")


def main():
    log.info("=" * 50)
    log.info("MilaGold OCR Agent - Signal GPT versiyonu")
    log.info("=" * 50)

    driver = get_driver()

    driver.get(SIGNAL_URL)
    log.info("Signal GPT sayfasina gidildi.")
    log.info("Sayfa yukleniyor, 15 saniye bekleniyor...")
    time.sleep(15)

    screenshot_region(driver, 0, 0, 1366, 768, "fullscreen_debug.png")
    log.info("Baslangic screenshot alindi.")
    log.info("Ilk okuma oncesi 5 saniye bekleniyor...")
    time.sleep(5)

    active_signal = None
    fail_count = 0

    # Erken emir + arka plan dogrulama:
    # pending_entry: ilk okumada gorduğumuz yeni entry (henuz dogrulanmadi)
    # confirmed: False → MT5 emri acti ama dogrulama bekleniyor
    # confirmed: True  → dogrulandi, devam
    # cancel: True     → dogrulanamadi, MT5 iptal etmeli
    pending_entry     = None
    pending_direction = None

    log.info("Okuma dongusune giriliyor...")

    while True:
        try:
            # Sayfa kaymis olabilir - her okumadan once en uste sar
            try:
                driver.execute_script("window.scrollTo(0, 0)")
            except Exception:
                pass

            list_path = screenshot_region(driver, LIST_LEFT, LIST_TOP,
                                          LIST_RIGHT, LIST_BOTTOM, "list_debug.png")
            list_texts = ocr_read(list_path)
            card = parse_list_card(list_texts)

            if not card["has_signal"]:
                fail_count += 1
                log.warning(f"GOLD karti okunamadi ({fail_count}). Ham: {list_texts[:3]}")
                if fail_count >= FAIL_THRESHOLD:
                    log.warning(f"{fail_count} kez ust uste okunamadi - sayfa yenileniyor...")
                    try:
                        driver.get(SIGNAL_URL)
                        time.sleep(8)
                        driver.execute_script("window.scrollTo(0, 0)")
                        log.info("Sayfa yenilendi.")
                    except Exception as e:
                        log.error(f"Sayfa yenileme hatasi: {e}")
                    fail_count = 0
                time.sleep(CHECK_INTERVAL)
                continue
            else:
                fail_count = 0

            if active_signal is None:
                # Yeni sinyal bekle
                new_sig = signal_from_card(card, confirmed=False)
                if new_sig:
                    active_signal = new_sig
                    log.info(f"Olasi yeni sinyal, HEMEN yazildi (dogrulama bekleniyor 1/2): "
                             f"#{active_signal['signal_no']} | "
                             f"{active_signal['direction']} @ {active_signal['entry']}")
                    write_signal(active_signal)
                    pending_entry     = card["entry"]
                    pending_direction = card["direction"]
                else:
                    log.info(f"Sinyal bekleniyor... Status:{card['status']} Entry:{card['entry']}")
                    pending_entry     = None
                    pending_direction = None

            else:
                # Aktif sinyal var - entry degisti mi?
                entry_changed = card["entry"] and \
                    abs(card["entry"] - active_signal["entry"]) > ENTRY_CHANGE_THRESHOLD

                if entry_changed:
                    if (pending_entry is not None
                            and abs(card["entry"] - pending_entry) <= ENTRY_CONFIRM_TOLERANCE
                            and card["direction"] == pending_direction):
                        # 2. ardisik okuma da ayni yeni degeri gosterdi -> DOGRULANDI
                        log.info(f"Yeni sinyal DOGRULANDI (2 okuma): "
                                 f"{active_signal['entry']} -> {card['entry']}")
                        update_signal_field("confirmed", True)
                        active_signal["confirmed"] = True

                        pending_entry     = None
                        pending_direction = None

                    else:
                        # Ilk farkli okuma - HEMEN signal.json'a yaz (confirmed=False)
                        # MT5 agent emri hemen acar, biz arkaplanda dogrulama yapariz
                        new_sig = signal_from_card(card, confirmed=False)
                        if new_sig:
                            log.info(f"Olasi yeni sinyal, HEMEN yazildi (dogrulama bekleniyor 1/2): "
                                     f"{active_signal['entry']} -> {card['entry']}")
                            active_signal = new_sig
                            write_signal(active_signal)
                        pending_entry     = card["entry"]
                        pending_direction = card["direction"]

                else:
                    # Entry ayni gorunuyor - pending varsa dogrulama kontrolu yap
                    if pending_entry is not None:
                        if abs(card["entry"] - pending_entry) <= ENTRY_CONFIRM_TOLERANCE                                 and card["direction"] == pending_direction:
                            # 2. okuma pending_entry ile uyustu -> DOGRULANDI
                            log.info(f"Yeni sinyal DOGRULANDI (2 okuma): "
                                     f"entry={card['entry']} pending={pending_entry}")
                            update_signal_field("confirmed", True)
                            active_signal["confirmed"] = True
                            pending_entry     = None
                            pending_direction = None
                        else:
                            # Gercekten dogrulanamadi
                            log.info(f"Dogrulama basarisiz: pending={pending_entry} "
                                     f"ama simdi entry={card['entry']}. cancel=True yaziliyor.")
                            update_signal_field("cancel", True)
                            active_signal["cancel"] = True
                            pending_entry     = None
                            pending_direction = None
                    else:
                        log.info(f"Takip: {card['direction']} @ {card['entry']} | Status:{card['status']}")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log.info("Agent durduruldu.")
            break
        except Exception as e:
            log.error(f"Dongu hatasi: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
