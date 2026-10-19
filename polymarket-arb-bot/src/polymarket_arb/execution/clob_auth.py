"""CLOB L2 request authentication (HMAC-SHA256). Used only by the live transport.

Per docs: message = timestamp + METHOD + path + body (body appended exactly as sent);
signature = urlsafe-base64(HMAC_SHA256(base64decode(secret), message)).
Credentials are never printed: ``ApiCredentials.__repr__`` masks every field.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ApiCredentials:
    address: str = field(repr=False)
    api_key: str = field(repr=False)
    secret: str = field(repr=False)
    passphrase: str = field(repr=False)

    def __repr__(self) -> str:  # never leak secrets into logs
        return "ApiCredentials(<masked>)"


def _decode_secret(secret: str) -> bytes:
    if any(ch in secret for ch in "-_"):
        return base64.urlsafe_b64decode(secret + "=" * (-len(secret) % 4))
    return base64.b64decode(secret + "=" * (-len(secret) % 4))


def l2_signature(secret: str, timestamp: str, method: str, path: str, body: str = "") -> str:
    message = f"{timestamp}{method.upper()}{path}{body}"
    digest = hmac.new(_decode_secret(secret), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii")


def l2_headers(
    creds: ApiCredentials,
    timestamp: str,
    method: str,
    path: str,
    body: str = "",
) -> dict[str, str]:
    return {
        "POLY_ADDRESS": creds.address,
        "POLY_SIGNATURE": l2_signature(creds.secret, timestamp, method, path, body),
        "POLY_TIMESTAMP": timestamp,
        "POLY_API_KEY": creds.api_key,
        "POLY_PASSPHRASE": creds.passphrase,
    }
