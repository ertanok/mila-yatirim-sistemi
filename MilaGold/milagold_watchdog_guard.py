import subprocess
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

MILAGOLD_DIR  = r"C:\MilaYatirim\mila-yatirim-sistemi\MilaGold"
GUARD_LOG     = os.path.join(MILAGOLD_DIR, "guard_log.txt")
WATCHDOG_SCRIPT = "milagold_watchdog.py"
SYNC_SCRIPT     = "milagold_sync_agent.py"


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(GUARD_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def telegram_bildir(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import urllib.request, urllib.parse
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        urllib.request.urlopen(url, data=data, timeout=5)
    except Exception:
        pass



def proses_calisiyor_mu(script_name):
    result = subprocess.run(
        ["wmic", "process", "where",
         f"name='python.exe' and CommandLine like '%{script_name}%'",
         "get", "ProcessId", "/FORMAT:CSV"],
        capture_output=True, text=True
    )
    pids = []
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
    return pids


def agent_baslat(window_title, script_name):
    cmd = (
        f'start "{window_title}" cmd /k '
        f'"cd /d {MILAGOLD_DIR} && py {script_name}"'
    )
    subprocess.Popen(cmd, shell=True, cwd=MILAGOLD_DIR)


def main():
    # --- Watchdog kontrolu ---
    pids = proses_calisiyor_mu(WATCHDOG_SCRIPT)
    if pids:
        log(f"[Watchdog] OK | PID: {', '.join(str(p) for p in pids)}")
    else:
        log("[Watchdog] Bulunamadi — yeniden baslatiliyor")
        agent_baslat("MilaGold Watchdog", WATCHDOG_SCRIPT)
        log("[Watchdog] Yeniden baslatildi")
        telegram_bildir("[MilaGold Guard] Watchdog durmus, yeniden baslatildi.")

    # --- Sync Agent kontrolu ---
    pids = proses_calisiyor_mu(SYNC_SCRIPT)
    if pids:
        log(f"[Sync Agent] OK | PID: {', '.join(str(p) for p in pids)}")
    else:
        log("[Sync Agent] Bulunamadi — yeniden baslatiliyor")
        agent_baslat("MilaGold - Sync Agent", SYNC_SCRIPT)
        log("[Sync Agent] Yeniden baslatildi")
        telegram_bildir("[MilaGold Guard] Sync Agent durmus, yeniden baslatildi.")


if __name__ == "__main__":
    main()
