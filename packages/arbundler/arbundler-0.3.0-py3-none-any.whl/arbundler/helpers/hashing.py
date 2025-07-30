import base64


def base64url_decode(inp: str | bytes) -> bytes:
    """Helper method to base64url_decode a string."""
    rem = len(inp) % 4

    if rem > 0:
        char = "=" if isinstance(inp, str) else b"="
        inp += char * (4 - rem)

    return base64.urlsafe_b64decode(inp)


def base64url_encode(inp: bytes) -> bytes:
    """Helper method to base64url_encode a string."""
    return base64.urlsafe_b64encode(inp).replace(b"=", b"")
