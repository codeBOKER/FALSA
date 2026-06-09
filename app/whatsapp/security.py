import hashlib
import hmac


def verify_meta_signature(body: bytes, signature_header: str | None, app_secret: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def verify_webhook_challenge(
    mode: str | None,
    verify_token: str | None,
    expected_verify_token: str,
) -> bool:
    return mode == "subscribe" and verify_token == expected_verify_token
