"""
breakout_price_compare.py
Breakout Order kapsamindaki enstrumanlar icin TV/harici kaynak fiyati ile
MT5/XM fiyati arasindaki farki olcer. Yontem MilaGold/gold_price_compare.py
ile ayni: 30 ornek, 10 saniye araliklarla (toplam ~5 dakika), ornek basina
ortalama fark + StdDev, CSV'ye kaydet.

OCR agent'in Chrome'una (port 9222) DOKUNMAZ - tamamen ayri bir Chrome
instance (port 9223, ayri user-data-dir) kullanir.

Gereksinim: pip install websocket-client
"""

import MetaTrader5 as mt5
import requests
import json
import csv
import time
import os
import subprocess
import statistics
import threading
from datetime import datetime

# -------------------------------------------------------------------
# Ayarlar
# -------------------------------------------------------------------

CDP_PORT = 9223   # OCR agent'in 9222'sinden FARKLI - cakisma olmasin
CDP_HOST = f"http://localhost:{CDP_PORT}"
OUTPUT_DIR = r"C:\MilaYatirim\mila-yatirim-sistemi\BreakoutOrder"
CHROME_PROFILE = os.path.join(os.environ.get("TEMP", r"C:\Temp"), "chrome_breakout_measure_profile")
INTERVAL = 10    # saniye
SAMPLES = 30     # 30 x 10sn = 5 dakika (MilaGold Gold olcumuyle ayni yontem)
PAGE_LOAD_WAIT = 35  # 7 sekme birlikte yuklendigi icin biraz daha uzun

# Enstruman listesi: ad (dosya/rapor icin), mt5 sembolu, TV URL, tab_hint
# (tab_hint: sayfa yuklenince TV'nin yonlendirebilecegi nihai URL'de de
# degismeden kalan, sekmeyi guvenilir eslestirmek icin kullanilan anahtar kelime)
INSTRUMENTS = [
    {"ad": "gold",   "mt5": "GOLD",      "tv_url": "https://www.tradingview.com/symbols/OANDA-XAUUSD/",     "tab_hint": "XAUUSD"},
    {"ad": "silver", "mt5": "SILVER",    "tv_url": "https://www.tradingview.com/symbols/OANDA-XAGUSD/",     "tab_hint": "XAGUSD"},
    {"ad": "ger40",  "mt5": "GER40Cash", "tv_url": "https://www.tradingview.com/symbols/FPMARKETS-GER40/",  "tab_hint": "GER40"},
    {"ad": "us100",  "mt5": "US100Cash", "tv_url": "https://www.tradingview.com/symbols/FPMARKETS-US100/",  "tab_hint": "US100"},
    {"ad": "eurusd", "mt5": "EURUSD",    "tv_url": "https://www.tradingview.com/symbols/EURUSD/?exchange=FX", "tab_hint": "EURUSD"},
    {"ad": "usdjpy", "mt5": "USDJPY",    "tv_url": "https://www.tradingview.com/symbols/USDJPY/?exchange=FX", "tab_hint": "USDJPY"},
    {"ad": "gbpjpy", "mt5": "GBPJPY",    "tv_url": "https://www.tradingview.com/symbols/GBPJPY/?exchange=FX", "tab_hint": "GBPJPY"},
]

try:
    import websocket
except ImportError:
    print("HATA: websocket-client yuklu degil. Calistir: pip install websocket-client")
    raise


def chrome_agaci_kapat(chrome_proc):
    """chrome_proc.terminate() tek basina yetersiz kalabiliyor - Task Scheduler
    uzerinden tetiklenince (16/07/2026'da gozlendi) sadece ana Chrome surecini
    degil, tum alt surecleri (renderer/GPU vb.) de kapatmak gerekiyor.
    taskkill /T ile tum surec agacini garantili kapatir."""
    try:
        subprocess.run(
            ["taskkill", "/PID", str(chrome_proc.pid), "/T", "/F"],
            capture_output=True, timeout=15,
        )
    except Exception as e:
        print(f"UYARI: chrome_agaci_kapat basarisiz: {e}")


# -------------------------------------------------------------------
# Chrome bulma
# -------------------------------------------------------------------

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


# -------------------------------------------------------------------
# CDP istemcisi (bir sekmeye ozel websocket baglantisi)
# -------------------------------------------------------------------

class CDPClient:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=15)
        self._id = 0
        self._lock = threading.Lock()
        self._pending = {}
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while True:
            try:
                msg = json.loads(self.ws.recv())
                mid = msg.get("id")
                if mid and mid in self._pending:
                    self._pending[mid]["result"] = msg
                    self._pending[mid]["event"].set()
            except Exception:
                break

    def _send(self, method, params=None):
        with self._lock:
            self._id += 1
            mid = self._id
        ev = threading.Event()
        self._pending[mid] = {"event": ev, "result": None}
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        ev.wait(timeout=15)
        return self._pending.pop(mid, {}).get("result")

    def evaluate(self, expr):
        result = self._send("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": False,
        })
        if result and "result" in result:
            return result["result"].get("result", {}).get("value")
        return None

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


# -------------------------------------------------------------------
# TV fiyat okuma — innerText + MT5 referansli +-%5 tolerans
# -------------------------------------------------------------------

def build_tv_price_js(ref_price):
    low = ref_price * 0.95
    high = ref_price * 1.05
    return f"""
(function() {{
    const low = {low:.5f};
    const high = {high:.5f};
    const text = document.body ? (document.body.innerText || document.body.textContent || '') : '';
    const tokens = text.match(/\\b[\\d,]+\\.\\d+/g) || [];
    for (const token of tokens) {{
        const v = parseFloat(token.replace(/,/g, ''));
        if (!isNaN(v) && v >= low && v <= high) return String(v);
    }}
    return null;
}})()
"""


def get_tv_price(cdp, ref_price):
    val = cdp.evaluate(build_tv_price_js(ref_price))
    if val is None:
        return None
    try:
        return float(str(val).replace(",", ""))
    except (ValueError, TypeError):
        return None


# -------------------------------------------------------------------
# Ana fonksiyon
# -------------------------------------------------------------------

def main():
    chrome_exe = find_chrome()
    if not chrome_exe:
        print("HATA: Chrome bulunamadi.")
        return

    print(f"Chrome baslatiliyor: {chrome_exe}")
    print(f"  Port: {CDP_PORT}  |  Profil: {CHROME_PROFILE}")

    urls = [inst["tv_url"] for inst in INSTRUMENTS]
    chrome_proc = subprocess.Popen(
        [
            chrome_exe,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={CHROME_PROFILE}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-sync",
            "--remote-allow-origins=*",
        ] + urls,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Chrome PID: {chrome_proc.pid}  ({len(urls)} sekme aciliyor)")

    print("Chrome basliyor, 5 saniye bekleniyor...")
    time.sleep(5)

    for attempt in range(5):
        try:
            tabs = requests.get(f"{CDP_HOST}/json", timeout=3).json()
            break
        except Exception:
            if attempt == 4:
                print(f"HATA: Chrome'a baglanilamiyor (port {CDP_PORT}).")
                chrome_agaci_kapat(chrome_proc)
                return
            time.sleep(2)

    # MT5 baglan
    print("MT5'e baglaniliyor...")
    if not mt5.initialize():
        print(f"MT5 basarisiz: {mt5.last_error()}")
        chrome_agaci_kapat(chrome_proc)
        return

    for inst in INSTRUMENTS:
        info = mt5.symbol_info(inst["mt5"])
        if info is None:
            print(f"HATA: MT5 sembol bulunamadi: {inst['mt5']}")
            mt5.shutdown(); chrome_agaci_kapat(chrome_proc)
            return
        if not info.visible:
            mt5.symbol_select(inst["mt5"], True)
        inst["digits"] = info.digits
    print("MT5 baglantisi tamam, tum semboller Market Watch'a eklendi.")

    print(f"Sayfalar yukleniyor, {PAGE_LOAD_WAIT} saniye bekleniyor...")
    time.sleep(PAGE_LOAD_WAIT)

    # Tab listesini tazele, her enstrumana kendi CDP client'ini bagla
    try:
        tabs = requests.get(f"{CDP_HOST}/json", timeout=5).json()
    except Exception as e:
        print(f"HATA: Tab listesi alinamadi: {e}")
        mt5.shutdown(); chrome_agaci_kapat(chrome_proc)
        return

    kullanilan_tab_id = set()
    for inst in INSTRUMENTS:
        tab = None
        for t in tabs:
            tid = t.get("id")
            if tid in kullanilan_tab_id:
                continue
            if t.get("type") != "page":
                continue
            if inst["tab_hint"].upper() in t.get("url", "").upper() or inst["tab_hint"].upper() in t.get("title", "").upper():
                tab = t
                break
        if tab is None:
            print(f"UYARI: {inst['ad']} icin sekme bulunamadi (hint={inst['tab_hint']}), atlaniyor.")
            print(f"  Mevcut sekmeler: {[(t.get('url',''), t.get('title','')) for t in tabs if t.get('type')=='page']}")
            inst["cdp"] = None
            continue
        kullanilan_tab_id.add(tab.get("id"))
        ws_url = tab.get("webSocketDebuggerUrl")
        inst["cdp"] = CDPClient(ws_url) if ws_url else None
        print(f"  {inst['ad']}: sekme baglandi -> {tab.get('url','')}")

    # Referans fiyatlarla ilk test okuma
    print("\nIlk fiyat dogrulamasi:")
    for inst in INSTRUMENTS:
        if inst["cdp"] is None:
            continue
        tick = mt5.symbol_info_tick(inst["mt5"])
        ref = tick.bid if tick else None
        test_price = get_tv_price(inst["cdp"], ref) if ref else None
        if test_price is None:
            print(f"  {inst['ad']}: TV fiyati okunamadi, 10sn daha bekleniyor...")
            time.sleep(10)
            test_price = get_tv_price(inst["cdp"], ref) if ref else None
        print(f"  {inst['ad']}: MT5={ref} | TV={test_price}")

    print(f"\nOlcum basliyor - {SAMPLES} ornek, {INTERVAL}sn araliklarla (~{SAMPLES*INTERVAL//60} dakika)\n")

    fieldnames = ["timestamp", "mt5_bid", "mt5_ask", "tv_price", "diff_bid", "diff_ask"]
    for inst in INSTRUMENTS:
        inst["samples"] = []
        inst["csv_path"] = os.path.join(OUTPUT_DIR, f"breakout_price_comparison_{inst['ad']}.csv")
        inst["csv_file"] = open(inst["csv_path"], "w", newline="", encoding="utf-8")
        inst["writer"] = csv.DictWriter(inst["csv_file"], fieldnames=fieldnames)
        inst["writer"].writeheader()

    for i in range(SAMPLES):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"--- Ornek {i+1}/{SAMPLES} ({ts}) ---")

        for inst in INSTRUMENTS:
            if inst["cdp"] is None:
                continue
            digits = inst["digits"]
            tick = mt5.symbol_info_tick(inst["mt5"])
            mt5_bid = round(tick.bid, digits) if tick else None
            mt5_ask = round(tick.ask, digits) if tick else None
            loop_ref = mt5_bid if mt5_bid else None
            tv_price = get_tv_price(inst["cdp"], loop_ref) if loop_ref else None
            diff_bid = round(tv_price - mt5_bid, digits + 1) if (tv_price and mt5_bid) else None
            diff_ask = round(tv_price - mt5_ask, digits + 1) if (tv_price and mt5_ask) else None

            row = {
                "timestamp": ts, "mt5_bid": mt5_bid, "mt5_ask": mt5_ask,
                "tv_price": tv_price, "diff_bid": diff_bid, "diff_ask": diff_ask,
            }
            inst["writer"].writerow(row)
            inst["csv_file"].flush()
            inst["samples"].append(row)

            print(f"  {inst['ad']:<8} MT5 bid/ask: {mt5_bid}/{mt5_ask}  TV: {tv_price}  diff_bid: {diff_bid}")

        if i < SAMPLES - 1:
            time.sleep(INTERVAL)

    for inst in INSTRUMENTS:
        inst["csv_file"].close()

    # Ozet istatistikler
    print(f"\n{'=' * 90}")
    print("OZET - Enstruman bazinda TV - MT5 farki")
    print(f"{'=' * 90}")
    ozet_sonuclari = {}
    for inst in INSTRUMENTS:
        valid = [s for s in inst["samples"] if s["diff_bid"] is not None and s["diff_ask"] is not None]
        print(f"\n{inst['ad'].upper()} ({inst['mt5']}) — {len(valid)}/{SAMPLES} gecerli ornek")
        if len(valid) >= 2:
            diffs_bid = [s["diff_bid"] for s in valid]
            diffs_ask = [s["diff_ask"] for s in valid]
            mean_bid = statistics.mean(diffs_bid)
            stdev_bid = statistics.stdev(diffs_bid)
            mean_ask = statistics.mean(diffs_ask)
            stdev_ask = statistics.stdev(diffs_ask)
            print(f"  TV - MT5 Bid | Ort: {mean_bid:+.5f} | StdDev: {stdev_bid:.5f} | Min: {min(diffs_bid):+.5f} | Max: {max(diffs_bid):+.5f}")
            print(f"  TV - MT5 Ask | Ort: {mean_ask:+.5f} | StdDev: {stdev_ask:.5f} | Min: {min(diffs_ask):+.5f} | Max: {max(diffs_ask):+.5f}")
            ozet_sonuclari[inst["ad"]] = {
                "mt5_sembol": inst["mt5"], "n": len(valid),
                "ort_diff_bid": mean_bid, "stdev_diff_bid": stdev_bid,
                "ort_diff_ask": mean_ask, "stdev_diff_ask": stdev_ask,
            }
        else:
            print("  Yetersiz gecerli ornek.")
        print(f"  CSV: {inst['csv_path']}")

    print(f"\n{'=' * 90}")

    ozet_path = os.path.join(OUTPUT_DIR, "breakout_price_comparison_ozet.json")
    with open(ozet_path, "w", encoding="utf-8") as f:
        json.dump(ozet_sonuclari, f, indent=2, ensure_ascii=False)
    print(f"Ozet JSON: {ozet_path}")

    # Temizlik
    mt5.shutdown()
    for inst in INSTRUMENTS:
        if inst.get("cdp"):
            inst["cdp"].close()
    chrome_agaci_kapat(chrome_proc)
    print("Chrome (olcum instance'i, port 9223) kapatildi. MT5 baglantisi kapatildi.")
    print("NOT: OCR agent'in Chrome'una (port 9222) hic dokunulmadi.")


if __name__ == "__main__":
    main()
