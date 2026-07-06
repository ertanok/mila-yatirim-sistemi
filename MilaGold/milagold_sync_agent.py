"""
milagold_sync_agent.py
VPS'te calisan bagimsiz sync agent.
Her 2 dakikada bir belirli dosyalari GitHub'a push eder.
Dashboard bu verileri GitHub API uzerinden okur.
"""

import os
import sys
import json
import time
import base64
import requests
import logging
import msvcrt

# --- TEK INSTANCE KILIDI ---
_SYNC_LOCK_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "milagold_sync_agent.lock"
)
_sync_lock_fh = open(_SYNC_LOCK_PATH, "w")
try:
    msvcrt.locking(_sync_lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
except OSError:
    print("[Sync Agent] Baska bir instance zaten calisiyor. Bu process sonlandiriliyor.")
    _sync_lock_fh.close()
    raise SystemExit(0)

from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from config import GITHUB_TOKEN
except ImportError:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

GITHUB_USER   = "ertanok"
GITHUB_REPO   = "mila-yatirim-sistemi"
GITHUB_BRANCH = "main"
SYNC_INTERVAL = 120  # saniye

BASE_DIR     = r"C:\MilaYatirim\mila-yatirim-sistemi\MilaGold"
DATA_DIR     = r"C:\MilaYatirim\mila-yatirim-sistemi\data"
CONTROL_FILE = os.path.join(DATA_DIR, "milagold_control.json")

# GitHub'a yüklenecek dosyalar: (yerel yol, repo'daki yol)
SYNC_FILES = [
    (os.path.join(BASE_DIR, "signal.json"),          "data/signal.json"),
    (os.path.join(BASE_DIR, "milagold_trades.json"), "data/milagold_trades.json"),
    (CONTROL_FILE,                                    "data/milagold_control.json"),
]

# Log dosyasindan son N satiri al
LOG_TAIL_LINES = 80
SYNC_LOG_FILES = [
    (os.path.join(BASE_DIR, "milagold_mt5_log.txt"), "data/milagold_log_tail.txt"),
    (os.path.join(BASE_DIR, "milagold_ocr_log.txt"), "data/milagold_ocr_log_tail.txt"),
]

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "milagold_sync_log.txt"),
    level=logging.INFO,
    format="%(asctime)s [SYNC] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


# ── GitHub API yardimcilari ───────────────────────────────────────────────────
def github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def get_file_sha(repo_path: str) -> str | None:
    """Dosyanin mevcut SHA'sini al (guncelleme icin gerekli)."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{repo_path}"
    r = requests.get(url, headers=github_headers(), timeout=10)
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def push_content(repo_path: str, content: str, commit_msg: str) -> bool:
    """Icerik stringini GitHub'a yükle (base64)."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{repo_path}"
    sha = get_file_sha(repo_path)

    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=github_headers(), json=payload, timeout=15)
    return r.status_code in (200, 201)


# ── Dosya okuma yardimcilari ─────────────────────────────────────────────────
def read_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        log.warning(f"Dosya okunamadi: {path} — {e}")
        return None


def read_tail(path: str, n: int = LOG_TAIL_LINES) -> str | None:
    content = read_file(path)
    if content is None:
        return None
    lines = content.splitlines()
    return "\n".join(lines[-n:])


# ── Agent durum dosyasi ───────────────────────────────────────────────────────
def build_agent_status() -> str:
    """
    Her iki agent log dosyasinin son degistirilme zamanina bakarak
    agent durumunu JSON olarak üretir.
    """
    def age_seconds(path):
        if not os.path.exists(path):
            return None
        return time.time() - os.path.getmtime(path)

    ocr_age = age_seconds(os.path.join(BASE_DIR, "milagold_ocr_log.txt"))
    mt5_age = age_seconds(os.path.join(BASE_DIR, "milagold_mt5_log.txt"))

    def status(age):
        if age is None:
            return "BILINMIYOR"
        if age < 30:
            return "AKTIF"
        if age < 120:
            return "YAVAS"
        return "DURDU"

    data = {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ocr_agent":   {"status": status(ocr_age),  "son_log_saniye": round(ocr_age) if ocr_age else None},
        "mt5_agent":   {"status": status(mt5_age),  "son_log_saniye": round(mt5_age) if mt5_age else None},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── Ana dongu ────────────────────────────────────────────────────────────────
def sync_once():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    errors = 0

    # control.json yoksa olustur
    if not os.path.exists(CONTROL_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CONTROL_FILE, "w", encoding="utf-8") as f:
            json.dump({"pause": False}, f, indent=2)
        log.info("control.json olusturuldu (varsayilan: pause=false)")

    # 1) JSON dosyalari
    for local_path, repo_path in SYNC_FILES:
        content = read_file(local_path)
        if content is None:
            log.warning(f"Bulunamadi, atlandi: {local_path}")
            continue
        ok = push_content(repo_path, content, f"sync: {os.path.basename(local_path)} @ {now}")
        if ok:
            log.info(f"OK  {repo_path}")
        else:
            log.error(f"FAIL {repo_path}")
            errors += 1

    # 2) Log dosyalarinin kuyrugu
    for local_path, repo_path in SYNC_LOG_FILES:
        content = read_tail(local_path)
        if content is None:
            log.warning(f"Log bulunamadi, atlandi: {local_path}")
            continue
        ok = push_content(repo_path, content, f"sync: log tail @ {now}")
        if ok:
            log.info(f"OK  {repo_path}")
        else:
            log.error(f"FAIL {repo_path}")
            errors += 1

    # 3) Agent durum dosyasi
    status_json = build_agent_status()
    ok = push_content("data/agent_status.json", status_json, f"sync: agent status @ {now}")
    if ok:
        log.info("OK  data/agent_status.json")
    else:
        log.error("FAIL data/agent_status.json")
        errors += 1

    return errors


def main():
    log.info("=== MilaGold Sync Agent baslatildi ===")
    log.info(f"Repo: {GITHUB_USER}/{GITHUB_REPO} | Aralik: {SYNC_INTERVAL}s")

    if not GITHUB_TOKEN:
        log.error("GITHUB_TOKEN bulunamadi. config.py kontrol edin.")
        return

    while True:
        try:
            errors = sync_once()
            if errors:
                log.warning(f"Sync tamamlandi ({errors} hata)")
            else:
                log.info("Sync tamamlandi (tum dosyalar OK)")
        except Exception as e:
            log.error(f"Beklenmeyen hata: {e}")

        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
