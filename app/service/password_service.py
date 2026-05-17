from __future__ import annotations

import hashlib
import hmac
import os
import re


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
_LEGACY_SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False

    if is_legacy_sha256_hash(stored_hash):
        candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(candidate, stored_hash)

    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != PBKDF2_ALGORITHM:
        return False

    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected = bytes.fromhex(parts[3])
    except ValueError:
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(candidate, expected)


def is_legacy_sha256_hash(stored_hash: str) -> bool:
    return bool(_LEGACY_SHA256_RE.fullmatch(stored_hash or ""))
