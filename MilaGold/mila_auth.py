"""
mila_auth.py
Paylasilan kimlik dogrulama yardimcilari - sifre dogrulama, oturum-token
uretme/dogrulama, Passkey (WebAuthn) kayit/giris/reauth. MilaGold'a ozgu
degil, tum dashboard/sistem icin gecerli.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone

import webauthn
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)

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

# --- WEBAUTHN / PASSKEY ---
WEBAUTHN_RP_ID = "login.milaertanok.com"
WEBAUTHN_RP_NAME = "Mila Dashboard"
WEBAUTHN_ORIGIN = "https://login.milaertanok.com"
WEBAUTHN_USER_ID = b"ertan-mila-dashboard"
WEBAUTHN_USER_NAME = "ertan"
WEBAUTHN_USER_DISPLAY_NAME = "Ertan Ok"
WEBAUTHN_CHALLENGE_TTL_SN = 5 * 60

WEBAUTHN_CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webauthn_credentials.json")

_aktif_challenge = None  # {"challenge": bytes, "amac": "register"|"login"|"reauth", "zaman": float, "cihaz_etiketi": str|None}


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


# --- WEBAUTHN / PASSKEY YARDIMCILARI ---

def _webauthn_kimlikleri_oku():
    if not os.path.exists(WEBAUTHN_CREDENTIALS_FILE):
        return []
    try:
        with open(WEBAUTHN_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _webauthn_kimlikleri_yaz(kimlikler):
    with open(WEBAUTHN_CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(kimlikler, f, indent=2, ensure_ascii=False)


def webauthn_kayitli_cihazlar():
    """Dashboard'da gosterilecek cihaz listesi (public_key/credential_id icermez)."""
    return [
        {"device_label": k.get("device_label"), "created_at": k.get("created_at"), "last_used_at": k.get("last_used_at")}
        for k in _webauthn_kimlikleri_oku()
    ]


def webauthn_register_baslat(cihaz_etiketi: str) -> str:
    """Yeni bir Passkey cihazi kaydi icin challenge uretir. Donen deger JSON string
    (navigator.credentials.create() secenekleri)."""
    global _aktif_challenge
    kayitli = _webauthn_kimlikleri_oku()
    exclude = [
        PublicKeyCredentialDescriptor(id=_b64url_decode(k["credential_id"]))
        for k in kayitli
    ]
    options = webauthn.generate_registration_options(
        rp_id=WEBAUTHN_RP_ID,
        rp_name=WEBAUTHN_RP_NAME,
        user_id=WEBAUTHN_USER_ID,
        user_name=WEBAUTHN_USER_NAME,
        user_display_name=WEBAUTHN_USER_DISPLAY_NAME,
        exclude_credentials=exclude or None,
    )
    _aktif_challenge = {
        "challenge": options.challenge,
        "amac": "register",
        "zaman": time.time(),
        "cihaz_etiketi": cihaz_etiketi or "bilinmeyen cihaz",
    }
    return webauthn.options_to_json(options)


def webauthn_register_tamamla(credential_json):
    """Cihazdan donen kayit yanitini dogrular, basariliysa credential'i kaydeder.
    Doner: (basarili: bool, hata_mesaji: str|None)"""
    global _aktif_challenge
    if not _aktif_challenge or _aktif_challenge["amac"] != "register":
        return False, "aktif kayit islemi yok"
    if time.time() - _aktif_challenge["zaman"] > WEBAUTHN_CHALLENGE_TTL_SN:
        _aktif_challenge = None
        return False, "islem suresi doldu, tekrar deneyin"

    try:
        result = webauthn.verify_registration_response(
            credential=credential_json,
            expected_challenge=_aktif_challenge["challenge"],
            expected_rp_id=WEBAUTHN_RP_ID,
            expected_origin=WEBAUTHN_ORIGIN,
        )
    except Exception as e:
        _aktif_challenge = None
        return False, f"dogrulama hatasi: {e}"

    kayitli = _webauthn_kimlikleri_oku()
    kayitli.append({
        "credential_id": _b64url_encode(result.credential_id),
        "public_key": _b64url_encode(result.credential_public_key),
        "sign_count": result.sign_count,
        "device_label": _aktif_challenge.get("cihaz_etiketi") or "bilinmeyen cihaz",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "last_used_at": None,
    })
    _webauthn_kimlikleri_yaz(kayitli)
    _aktif_challenge = None
    return True, None


def webauthn_dogrulama_baslat(amac: str):
    """amac: 'login' veya 'reauth'. Kayitli Passkey yoksa None doner (cagiran taraf
    sifre-tabanli girise dusmeli)."""
    global _aktif_challenge
    kayitli = _webauthn_kimlikleri_oku()
    if not kayitli:
        return None
    allow = [
        PublicKeyCredentialDescriptor(id=_b64url_decode(k["credential_id"]))
        for k in kayitli
    ]
    options = webauthn.generate_authentication_options(
        rp_id=WEBAUTHN_RP_ID,
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    _aktif_challenge = {"challenge": options.challenge, "amac": amac, "zaman": time.time()}
    return webauthn.options_to_json(options)


def webauthn_dogrulama_tamamla(credential_json, beklenen_amac: str):
    """credential_json: str veya dict (client'tan gelen assertion).
    Doner: (basarili: bool, hata_mesaji: str|None)"""
    global _aktif_challenge
    if not _aktif_challenge or _aktif_challenge["amac"] != beklenen_amac:
        return False, "aktif dogrulama islemi yok"
    if time.time() - _aktif_challenge["zaman"] > WEBAUTHN_CHALLENGE_TTL_SN:
        _aktif_challenge = None
        return False, "islem suresi doldu, tekrar deneyin"

    try:
        cred_dict = json.loads(credential_json) if isinstance(credential_json, str) else credential_json
        gelen_id = cred_dict.get("id", "")
    except Exception:
        return False, "gecersiz credential"

    kayitli = _webauthn_kimlikleri_oku()
    eslesen = None
    eslesen_index = None
    for i, k in enumerate(kayitli):
        if k["credential_id"].rstrip("=") == gelen_id.rstrip("="):
            eslesen = k
            eslesen_index = i
            break
    if eslesen is None:
        _aktif_challenge = None
        return False, "taninmayan cihaz"

    try:
        result = webauthn.verify_authentication_response(
            credential=credential_json,
            expected_challenge=_aktif_challenge["challenge"],
            expected_rp_id=WEBAUTHN_RP_ID,
            expected_origin=WEBAUTHN_ORIGIN,
            credential_public_key=_b64url_decode(eslesen["public_key"]),
            credential_current_sign_count=eslesen.get("sign_count", 0),
        )
    except Exception as e:
        _aktif_challenge = None
        return False, f"dogrulama hatasi: {e}"

    kayitli[eslesen_index]["sign_count"] = result.new_sign_count
    kayitli[eslesen_index]["last_used_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _webauthn_kimlikleri_yaz(kayitli)
    _aktif_challenge = None
    return True, None
