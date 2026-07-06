import time
import os
import subprocess
import requests
from datetime import datetime

# --- AYARLAR ---
MILAGOLD_DIR          = "C:\\MilaYatirim\\mila-yatirim-sistemi\\MilaGold"
LOG_FILE              = f"{MILAGOLD_DIR}\\milagold_watchdog_log.txt"
OCR_LOG               = f"{MILAGOLD_DIR}\\milagold_ocr_log.txt"
MT5_LOG               = f"{MILAGOLD_DIR}\\milagold_mt5_log.txt"
SIGNAL_JSON           = f"{MILAGOLD_DIR}\\signal.json"

OCR_SCRIPT            = "milagold_ocr_agent.py"
MT5_SCRIPT            = "milagold_mt5_agent.py"
OCR_WINDOW_TITLE      = "MilaGold - OCR Agent"
MT5_WINDOW_TITLE      = "MilaGold - MT5 Agent"

CHECK_INTERVAL        = 30    # saniye - kontrol araligi
AGENT_LOG_TIMEOUT     = 60    # saniye - bu kadar log gelmezse donmus say
SIGNAL_STALE_MINUTES  = 10    # dakika - signal.json bu kadar eskiyse Signal GPT donmus
RESTART_COOLDOWN      = 1800  # saniye (30dk) - ayni agent icin restart araligi

TELEGRAM_TOKEN   = None
TELEGRAM_CHAT_ID = None

try:
    import sys
    sys.path.insert(0, MILAGOLD_DIR)
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
except Exception:
    pass

# Restart zamanlari - loop onleme
_last_restart = {"ocr": 0, "mt5": 0}


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def telegram_bildir(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception:
        pass


def get_last_log_time(log_path):
    try:
        if not os.path.exists(log_path):
            return None
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                if line.startswith("["):
                    return datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
                elif "|" in line:
                    return datetime.strptime(line[:19].strip(), "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
    except Exception:
        pass
    return None


def kill_agent(script_name):
    try:
        pids = []
        for exe_name in ["py.exe", "python.exe", "python3.exe"]:
            result = subprocess.run(
                ["wmic", "process", "where",
                 f"name='{exe_name}' and CommandLine like '%{script_name}%'",
                 "get", "ProcessId", "/FORMAT:CSV"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or "ProcessId" in line or "Node" in line:
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    try:
                        pids.append(int(parts[-1].strip()))
                    except Exception:
                        pass
        for pid in pids:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            log(f"  Process kapatildi: PID={pid} ({script_name})")
        return len(pids)
    except Exception as e:
        log(f"  Process kapatma hatasi: {e}")
        return 0


def kill_window(window_title):
    """Basliginda window_title gecen tum cmd pencerelerini kapatir.
    Administrator: on-eki nedeniyle taskkill /FI yerine PowerShell kullanilir."""
    try:
        ps_cmd = (
            f"Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{window_title}*' }} | "
            f"Stop-Process -Force -ErrorAction SilentlyContinue"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True, timeout=10
        )
    except Exception as e:
        log(f"  Pencere kapatma hatasi: {e}")


def restart_agent(script_name, label, window_title, agent_key, neden=""):
    now_ts = time.time()
    since_last = now_ts - _last_restart[agent_key]
    if since_last < RESTART_COOLDOWN:
        log(f"  {label} restart bekleniyor (cooldown: {int(RESTART_COOLDOWN - since_last)}sn kaldi)")
        return False

    try:
        killed = kill_agent(script_name)
        if killed:
            log(f"  {killed} eski process kapatildi.")
        kill_window(window_title)
        time.sleep(3)
        cmd = f'start "{window_title}" cmd /k "cd /d {MILAGOLD_DIR} && py {script_name}"'
        subprocess.Popen(cmd, shell=True, cwd=MILAGOLD_DIR)
        _last_restart[agent_key] = now_ts
        neden_str = f" | Neden: {neden}" if neden else ""
        log(f"  {label} yeniden baslatildi.{neden_str}")
        telegram_bildir(f"[MilaGold Watchdog] {label} yeniden baslatildi.{neden_str}")
        return True
    except Exception as e:
        log(f"  {label} baslatma hatasi: {e}")
        telegram_bildir(f"[MilaGold Watchdog] HATA - {label} baslatılamadi: {e}")
        return False


# ─── KONTROL 1: OCR agent log ───────────────────────────────────────────────

def kontrol_ocr_agent():
    ocr_last = get_last_log_time(OCR_LOG)
    if ocr_last is None:
        log("[OCR] Log dosyasi yok -> baslatiliyor")
        restart_agent(OCR_SCRIPT, "OCR Agent", OCR_WINDOW_TITLE, "ocr", "log yok")
        return

    age = (datetime.now() - ocr_last).total_seconds()
    if age > AGENT_LOG_TIMEOUT:
        log(f"[OCR] DONDU | Son log: {age:.0f}sn once -> yeniden baslatiliyor")
        restart_agent(OCR_SCRIPT, "OCR Agent", OCR_WINDOW_TITLE, "ocr", f"log {age:.0f}sn eski")
    else:
        log(f"[OCR] OK | Son log: {age:.0f}sn once")


# ─── KONTROL 2: MT5 agent log ────────────────────────────────────────────────

def kontrol_mt5_agent():
    mt5_last = get_last_log_time(MT5_LOG)
    if mt5_last is None:
        log("[MT5 Agent] Log dosyasi yok -> baslatiliyor")
        restart_agent(MT5_SCRIPT, "MT5 Agent", MT5_WINDOW_TITLE, "mt5", "log yok")
        return

    age = (datetime.now() - mt5_last).total_seconds()
    if age > AGENT_LOG_TIMEOUT:
        log(f"[MT5 Agent] DONDU | Son log: {age:.0f}sn once -> yeniden baslatiliyor")
        restart_agent(MT5_SCRIPT, "MT5 Agent", MT5_WINDOW_TITLE, "mt5", f"log {age:.0f}sn eski")
    else:
        log(f"[MT5 Agent] OK | Son log: {age:.0f}sn once")


# ─── KONTROL 3: signal.json tazelik ─────────────────────────────────────────

def kontrol_signal_json():
    if not os.path.exists(SIGNAL_JSON):
        log("[signal.json] Dosya yok")
        return

    age_sn = time.time() - os.path.getmtime(SIGNAL_JSON)
    age_dk = age_sn / 60

    if age_dk < SIGNAL_STALE_MINUTES:
        log(f"[signal.json] OK | Son guncelleme: {age_dk:.1f}dk once")
        return

    # Stale - OCR calisiyor mu?
    ocr_last = get_last_log_time(OCR_LOG)
    if ocr_last is None:
        log(f"[signal.json] {age_dk:.1f}dk eski, OCR log da yok (OCR kontrolu halleder)")
        return

    ocr_age = (datetime.now() - ocr_last).total_seconds()
    if ocr_age >= AGENT_LOG_TIMEOUT:
        log(f"[signal.json] {age_dk:.1f}dk eski, OCR log da eski (OCR kontrolu halleder)")
        return

    # OCR calisiyor ama signal.json guncellenmemiyor -> Signal GPT sayfasi donmus
    log(f"[signal.json] {age_dk:.1f}dk eski, OCR calisiyor -> Signal GPT donmus, OCR yeniden baslatiliyor")
    restart_agent(OCR_SCRIPT, "OCR Agent", OCR_WINDOW_TITLE, "ocr",
                  f"Signal GPT {age_dk:.0f}dk dondu")


# ─── KONTROL 4: MT5 terminal process ────────────────────────────────────────

def kontrol_mt5_terminal():
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq terminal64.exe", "/NH"],
            capture_output=True, text=True
        )
        if "terminal64.exe" in result.stdout:
            log("[MT5 Terminal] OK | terminal64.exe calisiyor")
            return True
        else:
            log("[MT5 Terminal] UYARI: terminal64.exe bulunamadi!")
            telegram_bildir(
                "[MilaGold] KRITIK: MT5 terminal calismıyor! "
                "Manuel mudahale gerekiyor."
            )
            return False
    except Exception as e:
        log(f"[MT5 Terminal] Kontrol hatasi: {e}")
        return False


# ─── ANA DONGU ───────────────────────────────────────────────────────────────

def startup_cleanup():
    """Watchdog baslarken mevcut tum eski agent process ve pencerelerini temizler."""
    log("[Startup] Eski agent process'leri temizleniyor...")
    ocr_killed = kill_agent(OCR_SCRIPT)
    mt5_killed = kill_agent(MT5_SCRIPT)
    kill_window(OCR_WINDOW_TITLE)
    kill_window(MT5_WINDOW_TITLE)
    time.sleep(2)
    log(f"[Startup] Temizlik tamamlandi. OCR: {ocr_killed} process, MT5: {mt5_killed} process kapatildi.")


def main():
    log("=" * 55)
    log("MilaGold Watchdog v2 basliyor...")
    log(f"Check: {CHECK_INTERVAL}sn | Agent timeout: {AGENT_LOG_TIMEOUT}sn | Signal stale: {SIGNAL_STALE_MINUTES}dk")
    log("=" * 55)
    telegram_bildir("[MilaGold Watchdog] Watchdog v2 baslatildi.")
    startup_cleanup()

    while True:
        try:
            log(f"--- {datetime.now().strftime('%H:%M:%S')} ---")
            kontrol_ocr_agent()
            kontrol_mt5_agent()
            kontrol_signal_json()
            kontrol_mt5_terminal()
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Watchdog durduruldu.")
            break
        except Exception as e:
            log(f"Watchdog ana dongu hatasi: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
