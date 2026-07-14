"""
milaboard_api.py
Proje-geneli kontrol katmani: giris (/login) ve oturum-token dogrulama.
MilaGold'a ozgu degil - gelecekteki proje-genel endpoint'ler (Breakout Order
girisi, ileride durdur/baslat vb.) burada yasayacak.
Port: 5001
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mila_auth

PORT = 5001


class BoardApiHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[Board API] {self.address_string()} — {format % args}")

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
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path == "/login":
            self._handle_login()
        elif self.path == "/verify":
            self._handle_verify()
        else:
            self.send_json(404, {"error": "not found"})

    def _handle_login(self):
        ip = self.client_address[0]
        if mila_auth.ip_kilitli_mi(ip):
            self.send_json(429, {"error": "cok fazla basarisiz deneme, 15 dakika sonra tekrar deneyin"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        sifre = body.get("password", "")
        if not mila_auth.sifre_dogru_mu(sifre):
            mila_auth.basarisiz_deneme_kaydet(ip)
            self.send_json(401, {"error": "hatali sifre"})
            return

        mila_auth.basarili_giris_sonrasi_temizle(ip)
        oturum = mila_auth.oturum_tokeni_uret()
        self.send_json(200, {"ok": True, "token": oturum["token"], "expires_at": oturum["expires_at"]})

    def _handle_verify(self):
        # Dahili kullanim - diger servisler (milagold_api.py vb.) token dogrulamak icin bunu cagirir.
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        token = body.get("token", "")
        gecerli = bool(token) and mila_auth.oturum_tokeni_gecerli_mi(token)
        self.send_json(200, {"valid": gecerli})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), BoardApiHandler)
    print(f"[Board API] MilaBoard API servisi baslatildi — port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Board API] Durduruldu.")
