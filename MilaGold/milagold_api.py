"""
milagold_api.py
VPS'te calisan hafif HTTP API servisi.
Dashboard'dan gelen POST /control istekleriyle milagold_control.json'u gunceller.
Port: 5000
Auth: Authorization: Bearer <oturum-token> — dogrulama milaboard_api.py'nin
/verify endpoint'ine (localhost:5001) sorularak yapilir. Bu dosya token
formatini/secret'ini hic bilmez, doguluk kararini milaboard_api.py verir.
"""

import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

MILABOARD_VERIFY_URL = "http://localhost:5001/verify"

DATA_DIR     = r"C:\MilaYatirim\mila-yatirim-sistemi\data"
CONTROL_FILES = {
    "milagold": os.path.join(DATA_DIR, "milagold_control.json"),
}

PORT = 5000


def token_gecerli_mi(token):
    if not token:
        return False
    try:
        req = urllib.request.Request(
            MILABOARD_VERIFY_URL,
            data=json.dumps({"token": token}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            result = json.loads(resp.read())
            return bool(result.get("valid", False))
    except Exception as e:
        print(f"[API] milaboard_api /verify hatasi: {e}")
        return False


class ApiHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[API] {self.address_string()} — {format % args}")

    def send_json(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/control":
            self.send_json(404, {"error": "not found"})
            return

        # Oturum token kontrolu - milaboard_api.py'ye sorulur
        auth_header = self.headers.get("Authorization", "")
        token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
        if not token_gecerli_mi(token):
            self.send_json(401, {"error": "unauthorized"})
            return

        # Body oku
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        project = body.get("project", "").lower()
        pause   = body.get("pause")

        if project not in CONTROL_FILES:
            self.send_json(400, {"error": f"unknown project: {project}"})
            return

        if not isinstance(pause, bool):
            self.send_json(400, {"error": "pause must be true or false"})
            return

        # control.json guncelle
        path = CONTROL_FILES[project]
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"pause": pause}, f, indent=2)

        status = "duraklatildi" if pause else "aktif"
        print(f"[API] {project} -> pause={pause} ({status})")
        self.send_json(200, {"ok": True, "project": project, "pause": pause})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), ApiHandler)
    print(f"[API] MilaGold API servisi baslatildi — port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[API] Durduruldu.")
