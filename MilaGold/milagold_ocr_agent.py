import time
import re
import logging
import json
import os
import subprocess
import urllib.request
import zipfile
import msvcrt
import requests
from datetime import datetime
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import easyocr
import io

try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
except Exception:
    TELEGRAM_TOKEN = None
    TELEGRAM_CHAT_ID = None


def telegram_bildir(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        logging.getLogger().warning(f"Telegram hatasi: {e}")


# --- TEK INSTANCE KILIDI ---
# Lock dosyasi process kapaninca otomatik serbest kalir, temizlik gerekmez.
_LOCK_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "milagold_ocr_agent.lock"
)
_lock_fh = open(_LOCK_FILE_PATH, "w")
try:
    msvcrt.locking(_lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
except OSError:
    print("[OCR Agent] Baska bir instance zaten calisiyor. Bu process sonlandiriliyor.")
    _lock_fh.close()
    raise SystemExit(0)

# --- AYARLAR ---
SIGNAL_URL  = "https://signalgpt.ai/ai-signals"
SIGNAL_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\signal.json"
CHECK_INTERVAL = 2  # saniye
FAIL_THRESHOLD = 10  # bu kadar ust uste okuma hatasinda sayfa yenilenir
LOG_FILE  = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_ocr_log.txt"
DEBUG_DIR             = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\"
POSITIONS_STATUS_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\positions_status.json"
OCR_RESTART_FLAG      = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\ocr_restart_flag.txt"
ANOMALI_ESIK_SANIYE       = 720   # 12 dakika
DEBUG_SCREENSHOT_INTERVAL = 1800  # 30 dakika
CHROMEDRIVER_CACHE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "chromedriver_cache"
)

# SL ve TP hesaplama (sabit mesafeler)
SL_DISTANCE  = 5.0
TP1_DISTANCE = 3.0
TP2_DISTANCE = 5.0
TP3_DISTANCE = 8.0

# Entry degisikligi tespiti
ENTRY_CHANGE_THRESHOLD  = 0.5
ENTRY_CONFIRM_TOLERANCE = 0.5

# Liste karti koordinatlari (1366x768 cozunurluk)
# LIST_LEFT  170→50:  XAUUSD ve SELL/BUY kart solunda kesiliyordu
# LIST_TOP   450→360: filter bar (y≈255-355) altinda, kart basligini yakalar
# LIST_RIGHT 700→450→580: 450 RUNNING badge ve Entry degerini kesiyordu (list_debug.png ile dogrulandi)
LIST_LEFT   = 50
LIST_TOP    = 360
LIST_RIGHT  = 580
LIST_BOTTOM = 640

# Sinyal filtreleme parametreleri
SIGNAL_MAX_AGE_MINUTES = 60      # bu kadar dakikadan eski sinyal isleme konmaz
MARKET_CLOSE_HOUR      = 23      # piyasa kapanisi baslangic saati
MARKET_CLOSE_MINUTE    = 30      # piyasa kapanisi baslangic dakikasi
MARKET_OPEN_HOUR       = 1       # piyasa acilis saati
MARKET_OPEN_MINUTE     = 5       # piyasa acilis dakikasi

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


def _get_chrome_version_from_exe():
    """Chrome.exe binary'den versiyon oku — registry pending update'ten etkilenmez."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            r = subprocess.run(
                ["powershell", "-command",
                 f'(Get-Item "{p}").VersionInfo.FileVersion'],
                capture_output=True, text=True, timeout=5
            )
            v = r.stdout.strip()
            if re.match(r"\d+\.\d+\.\d+\.\d+", v):
                return v
        except Exception:
            pass
    return None


def _get_chromedriver(chrome_version):
    """
    Chrome versiyonuna tam uyan chromedriver.exe yolunu doner.
    Cache'de yoksa Chrome for Testing API'den indirir.
    """
    exe = os.path.join(CHROMEDRIVER_CACHE, chrome_version, "chromedriver.exe")
    if os.path.exists(exe):
        log.info(f"ChromeDriver cache'den: {exe}")
        return exe

    log.info(f"ChromeDriver {chrome_version} indiriliyor (Chrome for Testing API)...")
    os.makedirs(os.path.dirname(exe), exist_ok=True)

    api = ("https://googlechromelabs.github.io/chrome-for-testing/"
           "known-good-versions-with-downloads.json")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with urllib.request.urlopen(
            urllib.request.Request(api, headers=headers), timeout=20
        ) as resp:
            versions = json.loads(resp.read()).get("versions", [])

        major = chrome_version.split(".")[0]
        build = ".".join(chrome_version.split(".")[:3])
        matched = None
        for v in versions:
            if v["version"] == chrome_version:
                matched = v
                break
        if not matched:
            for v in versions:
                if v["version"].startswith(build + "."):
                    matched = v
        if not matched:
            cands = [v for v in versions if v["version"].startswith(major + ".")]
            if cands:
                matched = cands[-1]

        if not matched:
            log.error(f"Chrome {chrome_version} icin ChromeDriver JSON'da bulunamadi!")
            return None

        win_url = None
        for d in matched.get("downloads", {}).get("chromedriver", []):
            if d["platform"] == "win64":
                win_url = d["url"]
                break
            if d["platform"] == "win32":
                win_url = d["url"]

        if not win_url:
            log.error("win64/win32 ChromeDriver URL bulunamadi!")
            return None

        log.info(f"Indiriliyor: {win_url}")
        with urllib.request.urlopen(
            urllib.request.Request(win_url, headers=headers), timeout=30
        ) as resp:
            zip_bytes = resp.read()

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for name in zf.namelist():
                if name.lower().endswith("chromedriver.exe"):
                    with zf.open(name) as src, open(exe, "wb") as dst:
                        dst.write(src.read())
                    log.info(f"ChromeDriver indirildi: {exe}")
                    return exe

        log.error("ZIP icinde chromedriver.exe bulunamadi!")
    except Exception as e:
        log.error(f"ChromeDriver indirme hatasi: {e}")

    return None


def get_driver():
    chrome_ver = _get_chrome_version_from_exe()
    driver_exe = None

    if chrome_ver:
        log.info(f"Chrome versiyonu (exe): {chrome_ver}")
        driver_exe = _get_chromedriver(chrome_ver)
    else:
        log.warning("Chrome exe versiyonu okunamadi.")

    if driver_exe:
        service = Service(driver_exe)
        log.info(f"ChromeDriver: {driver_exe}")
    else:
        log.warning("Ozel ChromeDriver bulunamadi, chromedriver_autoinstaller'a donum yapiliyor...")
        chromedriver_autoinstaller.install()
        service = Service()

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=service, options=options)
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


def parse_signal_datetime(full_text):
    """
    Karttan sinyal tarih ve saatini parse eder.
    Format: DD/MM/YYYY HH:MM veya DD/MM/YYYY.HH.MM (nokta ayirici da olabilir)
    Basarili olursa datetime objesi, basarisiz olursa None doner.
    """
    # Ornek: 27/06/2026 03:58 veya 27/06/2026.03.58
    match = re.search(r'(\d{2}/\d{2}/\d{4})[\s.]+(\d{2}[:.]\d{2})', full_text)
    if match:
        try:
            date_str = match.group(1)
            time_str = match.group(2).replace('.', ':')  # nokta varsa ikiye donustur
            return datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        except Exception:
            pass
    return None


def is_market_closed(now=None):
    """
    VPS saatine gore piyasanin kapali olup olmadigini kontrol eder.
    23:30 - 01:05 arasi kapali sayilir.
    """
    if now is None:
        now = datetime.now()
    h, m = now.hour, now.minute
    # Kapali aralik: 23:30'dan gece yarisi ve 00:00'dan 01:05'e kadar
    after_close  = (h == 23 and m >= 30) or (h == 0)
    before_open  = (h == 1 and m < 5)
    return after_close or before_open


def is_signal_too_old(signal_dt, now=None):
    """
    Sinyal tarihi SIGNAL_MAX_AGE_MINUTES dakikadan eskiyse True doner.
    signal_dt None ise (okunamazsa) sinyal gecerli sayilir — hata durumunda bloklama yapma.
    """
    if signal_dt is None:
        return False
    if now is None:
        now = datetime.now()
    age_minutes = (now - signal_dt).total_seconds() / 60
    return age_minutes > SIGNAL_MAX_AGE_MINUTES


def parse_list_card(texts):
    full = " ".join(texts).upper()
    raw  = " ".join(texts)  # tarih parse icin kucuk harf korunmali
    card = {
        "has_signal":  False,
        "status":      None,
        "direction":   None,
        "entry":       None,
        "signal_no":   None,
        "signal_dt":   None,  # datetime objesi (parse edilebilirse)
    }

    has_gold = "XAU" in full or "GOLD" in full

    # Fallback: koordinatlar kart basligini kaclirabilir; Entry + gecerli altin
    # fiyati (2000-9000) + SELL/BUY birlikte varsa sinyali kabul et
    if not has_gold:
        e_fb = re.search(r'ENTRY[:\s]+(\d{4,5}\.?\d*)', full)
        if e_fb:
            e_val = float(e_fb.group(1))
            if 2000 < e_val < 9000 and ("SELL" in full or "BUY" in full):
                log.info("GOLD/XAU bulunamadi ama Entry+yon var — sinyal kabul edildi "
                         "(kart baslik kaybi, koordinat fallback)")
                has_gold = True

    if not has_gold:
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

    # Sinyal tarihi ve saati (27/06/2026 03:58 gibi)
    card["signal_dt"] = parse_signal_datetime(raw)
    if card["signal_dt"]:
        log.info(f"Sinyal tarihi okundu: {card['signal_dt'].strftime('%d/%m/%Y %H:%M')}")
    else:
        log.info("Sinyal tarihi okunamadi (filtre devrede degil).")

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
    """Karttan yeni sinyal sozlugu olustur. Yas ve piyasa saati filtreleri uygulanir."""
    if not (card["status"] in ("RUNNING", "WAITING") and card["entry"] and card["direction"]):
        return None

    now = datetime.now()

    # Filtre 1: Piyasa kapali mi? (23:30 - 01:05)
    if is_market_closed(now):
        log.warning(f"SINYAL ATLANDI — Piyasa kapali ({now.strftime('%H:%M')}). "
                    f"Gecerli aralik: 01:05 - 23:30.")
        return None

    # Filtre 2: Sinyal cok eski mi? (60 dakikadan fazla)
    if is_signal_too_old(card["signal_dt"], now):
        age = int((now - card["signal_dt"]).total_seconds() / 60)
        log.warning(f"SINYAL ATLANDI — Sinyal {age} dakika once uretildi "
                    f"(max: {SIGNAL_MAX_AGE_MINUTES} dk). "
                    f"Sinyal tarihi: {card['signal_dt'].strftime('%d/%m/%Y %H:%M')}.")
        return None

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
        "time":      now.strftime("%H:%M:%S"),
        "processed": False,
        "confirmed": confirmed,
        "cancel":    False,
    }


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


def acik_pozisyon_var_mi():
    """positions_status.json'dan MT5 acik pozisyon durumunu oku.
    Dosya yoksa, 30 sn'den eskiyse veya okunamazsa True doner (guvenli taraf: restart yapma)."""
    try:
        if not os.path.exists(POSITIONS_STATUS_FILE):
            return True
        if time.time() - os.path.getmtime(POSITIONS_STATUS_FILE) > 30:
            return True
        with open(POSITIONS_STATUS_FILE, "r") as f:
            data = json.load(f)
        return data.get("acik_pozisyon_var", True)
    except Exception:
        return True


def self_restart():
    """OCR agent'i yeniden baslatir. Yeni pencere acar, mevcut process cikiyor (lock otomatik serbest)."""
    import sys
    script = os.path.abspath(__file__)
    base_dir = os.path.dirname(script)
    cmd = f'start "MilaGold - OCR Agent" cmd /k "cd /d {base_dir} && py {os.path.basename(script)}"'
    subprocess.Popen(cmd, shell=True, cwd=base_dir)
    log.warning("OCR Agent kendini yeniden baslatiyor (anomali duzelmedi)...")
    sys.exit(0)


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

    # Onceki otomatik restart flag kontrolu
    anomali_restart_yapildi = False
    if os.path.exists(OCR_RESTART_FLAG):
        try:
            flag_ts = float(open(OCR_RESTART_FLAG).read().strip())
            if time.time() - flag_ts < 86400:
                anomali_restart_yapildi = True
                log.warning("Onceki otomatik restart tespit edildi (< 24 saat). Restart dongu korumasi aktif.")
        except Exception:
            pass

    active_signal = None
    fail_count = 0
    son_sayfa_yenileme    = time.time()
    son_debug_screenshot  = time.time()
    SAYFA_YENILEME_INTERVAL = 30 * 60  # 30 dakika

    # Anomali state
    anomali_baslangic          = None
    anomali_telegram_gonderildi = False
    gunluk_restart_sayaci      = 0

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

            # 30 dakikada bir zaman damgali debug screenshot
            if time.time() - son_debug_screenshot >= DEBUG_SCREENSHOT_INTERVAL:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_region(driver, LIST_LEFT, LIST_TOP, LIST_RIGHT, LIST_BOTTOM,
                                  f"list_debug_{ts}.png")
                log.info(f"Periyodik debug screenshot: list_debug_{ts}.png")
                son_debug_screenshot = time.time()

            # Gunluk sifirlama (00:00)
            if datetime.now().hour == 0 and datetime.now().minute == 0 and datetime.now().second < 5:
                gunluk_restart_sayaci = 0
                anomali_restart_yapildi = False
                try:
                    os.remove(OCR_RESTART_FLAG)
                except Exception:
                    pass

            # Periyodik sayfa yenileme (30 dakikada bir - sayfa donma korumasi)
            if time.time() - son_sayfa_yenileme >= SAYFA_YENILEME_INTERVAL:
                log.info("Periyodik sayfa yenileme (30 dk) basliyor...")
                try:
                    driver.get(SIGNAL_URL)
                    time.sleep(8)
                    driver.execute_script("window.scrollTo(0, 0)")
                    log.info("Periyodik sayfa yenileme tamamlandi.")
                except Exception as e:
                    log.error(f"Periyodik sayfa yenileme hatasi: {e}")
                son_sayfa_yenileme = time.time()
                time.sleep(CHECK_INTERVAL)
                continue

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

            # --- ANOMALi KONTROLU ---
            # has_signal True ama status/entry parse edilemedi, ancak ham metinde sinyal kelimesi var
            ocr_ham = " ".join(list_texts).upper()
            anomali = (
                card["has_signal"] and
                (card["status"] is None or card["entry"] is None) and
                any(k in ocr_ham for k in ("SELL", "BUY", "RUNNING", "WAITING"))
            )

            if anomali:
                if anomali_baslangic is None:
                    anomali_baslangic = time.time()
                sure = time.time() - anomali_baslangic
                if sure >= ANOMALI_ESIK_SANIYE and not anomali_telegram_gonderildi:
                    ham_ozet = " ".join(list_texts)[:200]
                    telegram_bildir(f"[MilaGold OCR] Anomali: sinyal metni var, parse edilemiyor\nHam: {ham_ozet}")
                    anomali_telegram_gonderildi = True

                    if anomali_restart_yapildi:
                        telegram_bildir("[MilaGold OCR] Otomatik restart basarisiz — manuel kontrol gerekli")
                    elif gunluk_restart_sayaci >= 3:
                        telegram_bildir("[MilaGold OCR] Bugun 3. anomali, otomatik restart durduruldu, manuel kontrol gerekli")
                    elif acik_pozisyon_var_mi():
                        telegram_bildir("[MilaGold OCR] Acik pozisyon var — restart yapilmiyor, manuel kontrol gerekli")
                    else:
                        gunluk_restart_sayaci += 1
                        try:
                            with open(OCR_RESTART_FLAG, "w") as _rf:
                                _rf.write(str(time.time()))
                        except Exception:
                            pass
                        self_restart()
            else:
                if anomali_baslangic is not None:
                    log.info("OCR anomali cozuldu.")
                    anomali_restart_yapildi = False
                    try:
                        os.remove(OCR_RESTART_FLAG)
                    except Exception:
                        pass
                anomali_baslangic = None
                anomali_telegram_gonderildi = False

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
