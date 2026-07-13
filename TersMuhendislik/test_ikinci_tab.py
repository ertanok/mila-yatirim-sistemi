"""
GECICI TEST SCRIPTI - test_ikinci_tab.py (v2 - encoding + CDP tiklama duzeltmesi)
Amac: milagold_ocr_agent.py'nin zaten actigi Chrome'a (debug port 9222) AYRI bir
Selenium session ile baglanip, yeni bir sekmede signalgpt.ai'ye gidip "Detail"
tiklamayi denemek ve bu sirada OCR agent'in kesintiye ugrayip ugramadigini izlemek.

milagold_ocr_agent.py'ye HICBIR SEKILDE dokunulmuyor/import edilmiyor - sadece
ayni Chrome'un debug portuna bagimsiz bir CDP baglantisi kuruluyor.

GUVENLIK NOTU: driver.quit() KESINLIKLE cagrilmiyor (debugger_address ile attach
edilen bir Chrome'da quit() tum tarayiciyi kapatabilir, bu da OCR agent'i da
oldurur). Sadece bu scriptin actigi YENI sekme driver.close() ile kapatilir.
"""
import io
import os
import sys
import time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

OCR_LOG = r"C:\MilaYatirim\mila-yatirim-sistemi\MilaGold\milagold_ocr_log.txt"
SIGNAL_JSON = r"C:\MilaYatirim\mila-yatirim-sistemi\MilaGold\signal.json"
SIGNAL_URL = "https://signalgpt.ai/ai-signals"
OUT_DIR = r"C:\MilaYatirim\TersMuhendislik"

os.makedirs(OUT_DIR, exist_ok=True)


def mtime(path):
    return os.path.getmtime(path)


def tail_lines(path, n=5):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return lines[-n:]


def ts():
    return datetime.now().strftime("%H:%M:%S")


def cdp_click(driver, x, y):
    """CDP ile mutlak piksel koordinatinda tiklama - offset/merkez belirsizligi yok,
    canvas tabanli (Flutter) uygulamalar icin en guvenilir yontem."""
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseMoved", "x": x, "y": y,
    })
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1,
    })
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1,
    })


print(f"[{ts()}] === BASLANGIC: OCR durumu (mudahaleden ONCE) ===")
log_mtime_before = mtime(OCR_LOG)
signal_mtime_before = mtime(SIGNAL_JSON)
print(f"  ocr_log mtime : {datetime.fromtimestamp(log_mtime_before)}")
print(f"  signal.json mtime: {datetime.fromtimestamp(signal_mtime_before)}")
print("  ocr_log son satirlar:")
for line in tail_lines(OCR_LOG, 3):
    print("   ", line.rstrip())

print(f"\n[{ts()}] === Debug port 9222'ye baglaniliyor (AYRI Selenium session) ===")
options = Options()
options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=options)

existing_handles = driver.window_handles
print(f"  Baglandi. Mevcut sekme sayisi: {len(existing_handles)}")
for h in existing_handles:
    driver.switch_to.window(h)
    print(f"    - handle={h} url={driver.current_url[:80]}")

new_tab_handle = None
try:
    print(f"\n[{ts()}] === Yeni sekme aciliyor ===")
    driver.switch_to.new_window("tab")
    new_tab_handle = driver.current_window_handle
    print(f"  Yeni sekme handle: {new_tab_handle}")

    driver.get(SIGNAL_URL)
    print(f"  Sayfa yuklendi (get). {SIGNAL_URL}")
    time.sleep(20)

    before_path = os.path.join(OUT_DIR, "test_ikinci_tab_1_yuklendi.png")
    driver.save_screenshot(before_path)
    print(f"  Ekran goruntusu kaydedildi: {before_path}")

    window_size = driver.get_window_size()
    print(f"  Pencere boyutu: {window_size}")

    click_success = False
    click_method = None

    # 1) DOM tabanli deneme - Flutter canvas oldugu icin muhtemelen basarisiz olacak
    print(f"\n[{ts()}] === Tiklama denemesi 1: DOM find_element (metin='Detail') ===")
    try:
        el = driver.find_element("xpath", "//*[contains(text(),'Detail')]")
        el.click()
        click_success = True
        click_method = "DOM find_element(xpath, text=Detail) + click()"
        print("  BASARILI (beklenmedik - DOM elementi bulundu ve tiklandi)")
    except Exception as e:
        print(f"  BASARISIZ: {type(e).__name__}: {e}")

    # 2) CDP mutlak koordinat tiklamasi
    if not click_success:
        print(f"\n[{ts()}] === Tiklama denemesi 2: CDP Input.dispatchMouseEvent (mutlak koordinat) ===")
        # Duzeltilmis koordinat: onceki denemenin ekran goruntusune bakarak "Detail"
        # satirinin gercek konumu tespit edildi (~x=123 y=520). Ertan'in manuel deneyimine
        # gore tam metne/oka tiklamak sart degil - ayni yatay seritte herhangi bir nokta
        # calisir. Satirin ortasina yakin, guvenli bir nokta seciyoruz.
        target_x = 280
        target_y = 520
        print(f"  Mutlak tiklama noktasi: x={target_x}, y={target_y}")
        try:
            cdp_click(driver, target_x, target_y)
            click_success = True
            click_method = f"CDP Input.dispatchMouseEvent(x={target_x}, y={target_y})"
            print("  Tiklama komutu gonderildi (basarili olup olmadigi ekran goruntusunden dogrulanmali)")
        except Exception as e:
            print(f"  BASARISIZ (exception): {type(e).__name__}: {e}")

    time.sleep(2)
    after_path = os.path.join(OUT_DIR, "test_ikinci_tab_2_tiklama_sonrasi.png")
    driver.save_screenshot(after_path)
    print(f"  Ekran goruntusu kaydedildi: {after_path}")
    print(f"\n  OZET: click_method={click_method} | gonderildi={click_success}")
    print("  NOT: Gercek basari, before/after PNG'lerin gorsel karsilastirmasiyla dogrulanmali"
          " (bu script otomatik dogrulama yapmiyor - Flutter canvas'ta DOM/URL degisimi olmayabilir).")

    # OCR kesinti izleme (~150 sn, istenen 2-3 dk araliginda)
    print(f"\n[{ts()}] === OCR sureklilik izleme basliyor (150 sn) ===")
    last_log_mtime = mtime(OCR_LOG)
    last_signal_mtime = mtime(SIGNAL_JSON)
    log_changed_count = 0
    signal_changed_count = 0
    start = time.time()
    while time.time() - start < 150:
        time.sleep(10)
        cur_log_mtime = mtime(OCR_LOG)
        cur_signal_mtime = mtime(SIGNAL_JSON)
        log_changed = cur_log_mtime != last_log_mtime
        signal_changed = cur_signal_mtime != last_signal_mtime
        if log_changed:
            log_changed_count += 1
        if signal_changed:
            signal_changed_count += 1
        print(f"  [{ts()}] log_degisti={log_changed} signal_degisti={signal_changed}")
        last_log_mtime = cur_log_mtime
        last_signal_mtime = cur_signal_mtime

    print(f"\n  Izleme boyunca log kac kez guncellendi: {log_changed_count}/15 kontrol")
    print(f"  Izleme boyunca signal.json kac kez guncellendi: {signal_changed_count}/15 kontrol")
    print("  ocr_log son satirlar (izleme sonrasi):")
    for line in tail_lines(OCR_LOG, 5):
        print("   ", line.rstrip())

finally:
    print(f"\n[{ts()}] === Temizlik: sadece yeni sekme kapatiliyor (driver.quit() CAGRILMIYOR) ===")
    try:
        if new_tab_handle and new_tab_handle in driver.window_handles:
            driver.switch_to.window(new_tab_handle)
            driver.close()
            print("  Yeni sekme kapatildi.")
    except Exception as e:
        print(f"  Sekme kapatma hatasi (onemsiz): {e}")
    try:
        if existing_handles:
            driver.switch_to.window(existing_handles[0])
    except Exception:
        pass
    print(f"[{ts()}] === TEST TAMAMLANDI (browser'a dokunulmadi, sadece sekme kapatildi) ===")
