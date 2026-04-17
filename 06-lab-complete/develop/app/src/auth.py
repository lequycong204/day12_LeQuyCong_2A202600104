from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from src.config import AppConfig


ALGORITHM = "HS256"


def build_demo_users(config: AppConfig) -> dict[str, dict[str, str]]:
    return {
        config.admin_username: {"password": config.admin_password, "role": "admin"},
        config.user_username: {"password": config.user_password, "role": "user"},
    }


def verify_password(plain_password: str, expected_password: str) -> bool:
    return hmac.compare_digest(plain_password, expected_password)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(data: dict[str, str], secret: str, expires_minutes: int) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int((datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).timestamp())

    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64url_encode(signature)}"


def decode_token(token: str, secret: str) -> dict:
    header_segment, payload_segment, signature_segment = token.split(".")
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()

    if not hmac.compare_digest(_b64url_encode(expected_signature), signature_segment):
        raise ValueError("Invalid JWT signature")

    header = json.loads(_b64url_decode(header_segment))
    if header.get("alg") != ALGORITHM:
        raise ValueError("Unsupported JWT algorithm")

    payload = json.loads(_b64url_decode(payload_segment))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("JWT expired")
    return payload
