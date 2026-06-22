"""
MilaGold History Reader v3 - Flutter Web / Screenshot+OCR
Calistirma: py lisa_history_reader.py

Signal GPT History sayfasi Flutter Web ile yapilmis - DOM okuma calismiyor.
Her sayfa screenshot alinip OCR ile okunuyor, Next butonuna koordinat bazli tiklaniyor.

Onkosul:
- Chrome --remote-debugging-port=9223 ile acik olmali
- signalgpt.ai/ai-signals sayfasinda History sekmesi acik olmali
- Date Range: 15 Haziran - bugun, Time: GMT+3 secili olmali
- Tarayici penceresi tam ekran olmali
"""

import time
import re
import json
import os
from datetime import datetime
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import easyocr
import io

# --- AYARLAR ---
MILAGOLD_PERF_FILE = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\milagold_signal_performance.json"
DEBUG_DIR      = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold\\"
PAGE_WAIT      = 3.0   # sayfa gecisi sonrasi bekleme (saniye)
MAX_PAGES      = 20    # guvenlik siniri

# Ekran koordinatlari (1366x768 tam ekran icin)
# Tablo bolumu: sol ust - sag alt
TABLE_LEFT   = 100
TABLE_TOP    = 280
TABLE_RIGHT  = 980
TABLE_BOTTOM = 660

# Next butonu koordinati (tam ekran 1366x768)
NEXT_BTN_X = 620
NEXT_BTN_Y = 690

# Sayfa bilgisi ("Page X of Y") bolumu
PAGE_INFO_LEFT   = 420
PAGE_INFO_TOP    = 670
PAGE_INFO_RIGHT  = 750
PAGE_INFO_BOTTOM = 710

print("EasyOCR yukleniyor...")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR hazir.")


def get_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    return webdriver.Chrome(options=options)


def take_screenshot(driver, left, top, right, bottom, filename=None):
    """Belirtilen bolgeden screenshot al."""
    screenshot = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(screenshot))
    region = img.crop((left, top, right, bottom))
    if filename:
        region.save(DEBUG_DIR + filename)
    return region


def ocr_image(img):
    """PIL Image'i OCR ile oku."""
    import numpy as np
    arr = np.array(img)
    return reader.readtext(arr, detail=0, paragraph=False)


def parse_history_ocr(texts):
    """OCR metinlerinden History satirlarini parse et.
    Her satir: DD/MM/YYYY | HH:MM | GOLD | SELL/BUY | STATUS | PIPS | ENTRY | CLOSED
    """
    records = []
    full = " ".join(texts)

    # Tarih pattern ile satirlari ayir
    # Her DD/MM/YYYY bir yeni satirin baslangici
    date_pattern = re.compile(r'\b(\d{2}[/\-]\d{2}[/\-]\d{4})\b')
    date_positions = [(m.start(), m.group()) for m in date_pattern.finditer(full)]

    if not date_positions:
        return records

    # Her tarihten sonraki metni ayri bir "satir" olarak isle
    for i, (pos, date_str) in enumerate(date_positions):
        end_pos = date_positions[i+1][0] if i+1 < len(date_positions) else len(full)
        row_text = full[pos:end_pos].strip()

        try:
            # Zaman: HH:MM
            time_match = re.search(r'\b(\d{2}:\d{2})\b', row_text)
            time_str = time_match.group(1) if time_match else "00:00"

            # Yon
            direction = None
            if "SELL" in row_text.upper():
                direction = "SELL"
            elif "BUY" in row_text.upper():
                direction = "BUY"

            if not direction:
                continue

            # Status
            row_up = row_text.upper()
            if "TP3" in row_up:
                sonuc = "TP3"
            elif "TP2" in row_up:
                sonuc = "TP2"
            elif "TP1" in row_up:
                sonuc = "TP1"
            elif "SL" in row_up and "HIT" in row_up:
                sonuc = "SL"
            elif "SL" in row_up:
                sonuc = "SL"
            elif "EXIT" in row_up:
                sonuc = "Exit"
            else:
                continue

            # Pip degeri: +80, -50, +14.5 gibi
            pip_match = re.search(r'([+-]\d+\.?\d*)', row_text)
            pips = float(pip_match.group(1)) if pip_match else None

            # Fiyatlar: 4XXX.XX formatinda (4000-5000 arasi)
            prices = re.findall(r'\b(4\d{3}\.\d{1,2})\b', row_text)
            prices = [float(p) for p in prices]

            entry       = prices[0] if len(prices) > 0 else None
            close_price = prices[1] if len(prices) > 1 else None

            # Tarih normalize
            date_clean = date_str.replace("-", "/")
            try:
                dt = datetime.strptime(f"{date_clean} {time_str}", "%d/%m/%Y %H:%M")
                dt_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                dt_str = f"{date_clean} {time_str}"

            records.append({
                "datetime":    dt_str,
                "direction":   direction,
                "sonuc":       sonuc,
                "pip":         pips,
                "entry":       entry,
                "close_price": close_price,
            })

        except Exception as e:
            pass  # Parse hatasi - bu satiri atla

    return records


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.5)


def scroll_to_top(driver):
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(0.3)


def click_next_btn(driver):
    """Next butonuna koordinat bazli tikla."""
    try:
        scroll_to_bottom(driver)
        time.sleep(0.5)
        actions = ActionChains(driver)
        # Tarayici penceresinin sol ust kosesine gore koordinat
        actions.move_by_offset(NEXT_BTN_X, NEXT_BTN_Y).click().perform()
        # ActionChains offsets birikiyor - sifirla
        actions.move_by_offset(-NEXT_BTN_X, -NEXT_BTN_Y).perform()
        return True
    except Exception as e:
        print(f"  Next tiklanamadi: {e}")
        return False


def get_page_num_from_screenshot(driver):
    """'Page X of Y' bolumunun screenshot'indan sayfa numarasini oku."""
    try:
        scroll_to_bottom(driver)
        time.sleep(0.3)
        img = take_screenshot(driver, PAGE_INFO_LEFT, PAGE_INFO_TOP,
                              PAGE_INFO_RIGHT, PAGE_INFO_BOTTOM)
        texts = ocr_image(img)
        full = " ".join(texts)
        match = re.search(r'(\d+)\s+of\s+(\d+)', full)
        if match:
            return int(match.group(1)), int(match.group(2))
    except Exception:
        pass
    return None, None


def load_existing(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_records(filepath, records):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"{len(records)} kayit yazildi: {filepath}")


def main():
    print("=" * 55)
    print("MilaGold History Reader v3 (Flutter Web / OCR)")
    print("=" * 55)
    print()
    print("Lutfen kontrol edin:")
    print("  1. Chrome --remote-debugging-port=9223 ile acik")
    print("  2. signalgpt.ai History sekmesi acik")
    print("  3. Date Range: 15 Haziran - bugun secili")
    print("  4. Time: GMT+3 secili")
    print("  5. Tarayici penceresi TAM EKRAN (F11)")
    print()
    input("Hazir olunca Enter'a basin...")

    driver = get_driver()
    print("Chrome'a baglandi.")
    print("Tarayici penceresi tam ekrana aliniyor...")
    try:
        driver.maximize_window()
    except Exception:
        pass  # Zaten maximize
    time.sleep(1)

    all_records = []
    page_num = 1

    for _ in range(MAX_PAGES):
        scroll_to_top(driver)
        time.sleep(0.5)

        print(f"\n--- Sayfa {page_num} okunuyor ---")

        # Screenshot al ve OCR ile oku
        img = take_screenshot(driver, TABLE_LEFT, TABLE_TOP,
                              TABLE_RIGHT, TABLE_BOTTOM,
                              f"history_page{page_num:02d}.png")
        texts = ocr_image(img)
        print(f"  OCR metin sayisi: {len(texts)}")

        records = parse_history_ocr(texts)
        print(f"  Parse edilen kayit: {len(records)}")
        all_records.extend(records)

        if records:
            print(f"  Ilk: {records[0]['datetime']} {records[0]['direction']} "
                  f"@ {records[0]['entry']} -> {records[0]['sonuc']}")
            print(f"  Son: {records[-1]['datetime']} {records[-1]['direction']} "
                  f"@ {records[-1]['entry']} -> {records[-1]['sonuc']}")

        # Sayfa bilgisi
        cur, total = get_page_num_from_screenshot(driver)
        if cur and total:
            print(f"  Sayfa: {cur} / {total}")
            if cur >= total:
                print("Son sayfaya ulasildi.")
                break
        else:
            print(f"  Sayfa numarasi okunamadi (sayfa {page_num})")

        # Next butonuna tikla
        if not click_next_btn(driver):
            print("  Next tiklanamadi - durduruluyor.")
            break

        time.sleep(PAGE_WAIT)
        page_num += 1

    print(f"\nToplam {len(all_records)} ham kayit okundu.")

    if not all_records:
        print("Hic kayit okunamadi.")
        print("Ipucu: history_page01.png dosyasini kontrol edin.")
        return

    # Tekrarlari temizle
    seen = set()
    unique = []
    for r in all_records:
        key = (r["datetime"], r["entry"], r["direction"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    print(f"Tekrar temizleme sonrasi: {len(unique)} benzersiz kayit.")

    # Mevcut kayitlarla birlestir
    existing = load_existing(MILAGOLD_PERF_FILE)
    existing_keys = {(r.get("datetime"), r.get("entry"), r.get("direction"))
                     for r in existing}
    new_records = [r for r in unique
                   if (r["datetime"], r["entry"], r["direction"]) not in existing_keys]

    all_combined = existing + new_records
    save_records(MILAGOLD_PERF_FILE, all_combined)
    print(f"{len(new_records)} yeni kayit eklendi.")

    # Ozet
    print("\n--- Sonuc Ozeti ---")
    from collections import Counter
    sonuclar = Counter(r["sonuc"] for r in unique)
    for s, c in sorted(sonuclar.items()):
        print(f"  {s:12}: {c} islem")


if __name__ == "__main__":
    main()
