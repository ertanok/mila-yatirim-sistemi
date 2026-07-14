"""
milagold_api.py
VPS'te calisan hafif HTTP API servisi.
Dashboard'dan gelen POST /control istekleriyle milagold_control.json'u gunceller.
Port: 5000
Auth: X-Api-Key header
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import API_TOKEN

DATA_DIR     = r"C:\MilaYatirim\mila-yatirim-sistemi\data"
CONTROL_FILES = {
    "milagold": os.path.join(DATA_DIR, "milagold_control.json"),
}

PORT = 5000


class ApiHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[API] {self.address_string()} — {format % args}")

    def send_json(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/control":
            self.send_json(404, {"error": "not found"})
            return

        # Token kontrol
        token = self.headers.get("X-Api-Key", "")
        if token != API_TOKEN:
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
