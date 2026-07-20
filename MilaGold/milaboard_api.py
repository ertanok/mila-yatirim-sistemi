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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mila_auth

PORT = 5001

DATA_DIR = r"C:\MilaYatirim\mila-yatirim-sistemi\data"
BREAKOUT_LEVELS_FILE = os.path.join(DATA_DIR, "breakout_levels.json")

MILAGOLD_DIR = r"C:\MilaYatirim\mila-yatirim-sistemi\MilaGold"
MANUEL_SIGNAL_FILE = os.path.join(MILAGOLD_DIR, "manuel_signal.json")


class BoardApiHandler(BaseHTTPRequestHandler):

    timeout = 10  # saniye - tikanan baglantiyi otomatik kapatir

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
        elif self.path == "/webauthn/register/begin":
            self._handle_webauthn_register_begin()
        elif self.path == "/webauthn/register/complete":
            self._handle_webauthn_register_complete()
        elif self.path == "/webauthn/login/begin":
            self._handle_webauthn_login_begin()
        elif self.path == "/webauthn/login/complete":
            self._handle_webauthn_login_complete()
        elif self.path == "/manual-order/begin":
            self._handle_manual_order_begin()
        elif self.path == "/manual-order/submit":
            self._handle_manual_order_submit()
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

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))

    def _handle_webauthn_register_begin(self):
        """Yeni Passkey cihazi kaydi baslatir. Sadece zaten sifreyle giris
        yapmis (gecerli oturum token'ina sahip) kullanici cihaz ekleyebilir."""
        if not self._oturum_token_gecerli_mi():
            self.send_json(401, {"error": "unauthorized"})
            return
        try:
            body = self._read_json_body()
        except Exception:
            body = {}
        cihaz_etiketi = body.get("device_label", "")

        options_json = mila_auth.webauthn_register_baslat(cihaz_etiketi)
        self.send_json(200, json.loads(options_json))

    def _handle_webauthn_register_complete(self):
        if not self._oturum_token_gecerli_mi():
            self.send_json(401, {"error": "unauthorized"})
            return
        try:
            body = self._read_json_body()
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        credential = body.get("credential")
        if not credential:
            self.send_json(400, {"error": "credential gerekli"})
            return

        basarili, hata = mila_auth.webauthn_register_tamamla(credential)
        if not basarili:
            self.send_json(400, {"error": hata or "kayit basarisiz"})
            return
        print("[Board API] yeni Passkey cihazi kaydedildi")
        self.send_json(200, {"ok": True})

    def _handle_webauthn_login_begin(self):
        """Passkey ile giris baslatir. Hic kayitli cihaz yoksa frontend
        sifre-tabanli girise dusmeli (passkey_kurulu: false)."""
        ip = self.client_address[0]
        if mila_auth.ip_kilitli_mi(ip):
            self.send_json(429, {"error": "cok fazla basarisiz deneme, 15 dakika sonra tekrar deneyin"})
            return

        options_json = mila_auth.webauthn_dogrulama_baslat("login")
        if options_json is None:
            self.send_json(200, {"passkey_kurulu": False})
            return
        self.send_json(200, json.loads(options_json))

    def _handle_webauthn_login_complete(self):
        ip = self.client_address[0]
        if mila_auth.ip_kilitli_mi(ip):
            self.send_json(429, {"error": "cok fazla basarisiz deneme, 15 dakika sonra tekrar deneyin"})
            return

        try:
            body = self._read_json_body()
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        credential = body.get("credential")
        if not credential:
            self.send_json(400, {"error": "credential gerekli"})
            return

        basarili, hata = mila_auth.webauthn_dogrulama_tamamla(credential, "login")
        if not basarili:
            mila_auth.basarisiz_deneme_kaydet(ip)
            self.send_json(401, {"error": hata or "dogrulama basarisiz"})
            return

        mila_auth.basarili_giris_sonrasi_temizle(ip)
        oturum = mila_auth.oturum_tokeni_uret()
        self.send_json(200, {"ok": True, "token": oturum["token"], "expires_at": oturum["expires_at"]})

    def _handle_manual_order_begin(self):
        """Manuel emir formu icin taze Passkey dogrulamasi baslatir.
        Gecerli oturum token'i yetmez - MilaGold - Manuel Emir gorev tanimi geregi
        her gonderimde ayrica bir Passkey dokunusu gerekir (calinmis oturum
        token'i tek basina emir acamasin diye)."""
        if not self._oturum_token_gecerli_mi():
            self.send_json(401, {"error": "unauthorized"})
            return

        options_json = mila_auth.webauthn_dogrulama_baslat("reauth")
        if options_json is None:
            self.send_json(400, {"error": "kayitli Passkey yok - once bir cihaz ekleyin"})
            return
        self.send_json(200, json.loads(options_json))

    def _handle_manual_order_submit(self):
        """Yon + fiyat alir, credential'i BURADA dogrular (begin cagrisina
        guvenmez) ve basariliysa manuel_signal.json'a yazar. Boylece calinmis
        bir oturum token'i tek basina yeterli olmaz - gecerli, taze bir
        Passkey imzasi sart. Trading mantigi (SL/TP hesaplama, emir tipi,
        trailing) bu endpoint'in kapsaminda degil - milagold_mt5_agent.py
        (ayri, onayli bir adimda) bu dosyayi okuyup isleyecek."""
        if not self._oturum_token_gecerli_mi():
            self.send_json(401, {"error": "unauthorized"})
            return

        try:
            body = self._read_json_body()
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        yon = body.get("direction", "")
        fiyat = body.get("price")
        credential = body.get("credential")

        if not isinstance(yon, str) or yon.strip().upper() not in ("BUY", "SELL"):
            self.send_json(400, {"error": "direction BUY veya SELL olmali"})
            return
        yon = yon.strip().upper()

        if not isinstance(fiyat, (int, float)) or isinstance(fiyat, bool) or fiyat <= 0:
            self.send_json(400, {"error": "price pozitif sayisal olmali"})
            return

        if not credential:
            self.send_json(400, {"error": "credential gerekli (Passkey dogrulamasi)"})
            return

        basarili, hata = mila_auth.webauthn_dogrulama_tamamla(credential, "reauth")
        if not basarili:
            self.send_json(401, {"error": hata or "Passkey dogrulamasi basarisiz"})
            return

        sinyal = {
            "direction": yon,
            "entry": fiyat,
            "time": datetime.now().strftime("%H:%M:%S"),
            "processed": False,
            "confirmed": True,
            "cancel": False,
        }

        os.makedirs(MILAGOLD_DIR, exist_ok=True)
        with open(MANUEL_SIGNAL_FILE, "w", encoding="utf-8") as f:
            json.dump(sinyal, f, indent=2)

        print(f"[Board API] manuel emir yazildi: {yon} @ {fiyat}")
        self.send_json(200, {"ok": True, "direction": yon, "entry": fiyat})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), BoardApiHandler)
    server.daemon_threads = True
    print(f"[Board API] MilaBoard API servisi baslatildi — port {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Board API] Durduruldu.")
