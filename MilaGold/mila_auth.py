"""
mila_auth.py
Paylasilan kimlik dogrulama yardimcilari - sifre dogrulama ve oturum-token
uretme/dogrulama. MilaGold'a ozgu degil, tum dashboard/sistem icin gecerli.
Dis kutuphane gerektirmez (stdlib: hashlib, hmac, secrets, json, base64, time).
"""
import base64
import hashlib
import hmac
import json
import time

from config import (
    DASHBOARD_PASSWORD_SALT,
    DASHBOARD_PASSWORD_HASH,
    DASHBOARD_PASSWORD_ITERATIONS,
    SESSION_SECRET,
)

SESSION_TTL_SECONDS = 24 * 60 * 60  # 24 saat

LOCKOUT_ESIK = 5
LOCKOUT_SURESI_SN = 15 * 60

_basarisiz_denemeler = {}  # ip -> [timestamp, ...]


def sifre_dogru_mu(girilen_sifre: str) -> bool:
    salt = bytes.fromhex(DASHBOARD_PASSWORD_SALT)
    dk = hashlib.pbkdf2_hmac("sha256", girilen_sifre.encode("utf-8"), salt, DASHBOARD_PASSWORD_ITERATIONS)
    return hmac.compare_digest(dk.hex(), DASHBOARD_PASSWORD_HASH)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def oturum_tokeni_uret() -> dict:
    now = int(time.time())
    payload = {"iat": now, "exp": now + SESSION_TTL_SECONDS}
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    imza = hmac.new(bytes.fromhex(SESSION_SECRET), payload_b64.encode("ascii"), hashlib.sha256).digest()
    token = f"{payload_b64}.{_b64url_encode(imza)}"
    return {"token": token, "expires_at": payload["exp"]}


def oturum_tokeni_gecerli_mi(token: str) -> bool:
    try:
        payload_b64, imza_b64 = token.split(".", 1)
    except ValueError:
        return False

    beklenen_imza = hmac.new(bytes.fromhex(SESSION_SECRET), payload_b64.encode("ascii"), hashlib.sha256).digest()
    try:
        verilen_imza = _b64url_decode(imza_b64)
    except Exception:
        return False

    if not hmac.compare_digest(beklenen_imza, verilen_imza):
        return False

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception:
        return False

    return payload.get("exp", 0) > time.time()


def ip_kilitli_mi(ip: str) -> bool:
    denemeler = _basarisiz_denemeler.get(ip, [])
    simdi = time.time()
    denemeler = [t for t in denemeler if simdi - t < LOCKOUT_SURESI_SN]
    _basarisiz_denemeler[ip] = denemeler
    return len(denemeler) >= LOCKOUT_ESIK


def basarisiz_deneme_kaydet(ip: str):
    _basarisiz_denemeler.setdefault(ip, []).append(time.time())


def basarili_giris_sonrasi_temizle(ip: str):
    _basarisiz_denemeler.pop(ip, None)
