"""
milaboard_api.py
Proje-geneli kontrol katmani: giris (/login), oturum-token dogrulama (/verify)
ve proje-genel endpoint'ler. MilaGold'a ozgu degil.
Port: 5001
"""
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mila_auth

PORT = 5001

DATA_DIR = r"C:\MilaYatirim\mila-yatirim-sistemi\data"
BREAKOUT_LEVELS_FILE = os.path.join(DATA_DIR, "breakout_levels.json")


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
        elif self.path == "/breakout/levels":
            self._handle_breakout_levels()
        else:
            self.send_json(404, {"error": "not found"})

    def _oturum_token_gecerli_mi(self):
        """Bu istegin Authorization: Bearer header'inda gecerli bir oturum
        token'i olup olmadigini kontrol eder. Dusuk-riskli endpoint'ler icin
        yeterli dogrulama seviyesi - milaboard_api.py zaten mila_auth'u
        dogrudan import ettigi icin ag cagrisina gerek yok."""
        auth_header = self.headers.get("Authorization", "")
        token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
        return bool(token) and mila_auth.oturum_tokeni_gecerli_mi(token)

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

    def _handle_breakout_levels(self):
        """Breakout Order projesi icin direnc seviyesi besleme arayuzu.
        Trading mantigi (emir gonderme, ATH toggle, reaktivasyon) bu
        endpoint'in kapsaminda degil - sadece seviyeyi dosyaya yazar,
        Breakout Order agent'i (ayri gorev) bu dosyayi okur.
        Dusuk-riskli islem - sadece oturum-token yeterli, ek onay katmani yok."""
        if not self._oturum_token_gecerli_mi():
            self.send_json(401, {"error": "unauthorized"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        enstruman = body.get("instrument", "")
        seviye = body.get("level")

        if not isinstance(enstruman, str) or not enstruman.strip():
            self.send_json(400, {"error": "instrument gerekli"})
            return
        enstruman = enstruman.strip().upper()

        if not isinstance(seviye, (int, float)) or isinstance(seviye, bool):
            self.send_json(400, {"error": "level sayisal olmali"})
            return
        if seviye <= 0:
            self.send_json(400, {"error": "level pozitif olmali"})
            return

        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(BREAKOUT_LEVELS_FILE, "r", encoding="utf-8") as f:
                tum_seviyeler = json.load(f)
        except Exception:
            tum_seviyeler = {}

        tum_seviyeler[enstruman] = {
            "level": seviye,
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

        with open(BREAKOUT_LEVELS_FILE, "w", encoding="utf-8") as f:
            json.dump(tum_seviyeler, f, indent=2, ensure_ascii=False)

        print(f"[Board API] breakout level guncellendi: {enstruman} -> {seviye}")
        self.send_json(200, {"ok": True, "instrument": enstruman, "level": seviye})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), BoardApiHandler)
    print(f"[Board API] MilaBoard API servisi baslatildi — port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Board API] Durduruldu.")
