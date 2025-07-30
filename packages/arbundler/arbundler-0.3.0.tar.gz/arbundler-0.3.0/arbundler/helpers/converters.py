import hashlib
from decimal import Decimal

from .hashing import base64url_decode, base64url_encode


def owner_to_address(owner: str) -> str:
    result = base64url_encode(hashlib.sha256(base64url_decode(owner.encode("ascii"))).digest()).decode()

    return result


def winston_to_ar(winston_str: str) -> float:
    length = len(winston_str)

    if length > 12:
        past_twelve = length - 12
        winston_str = f"{winston_str[0:past_twelve]}.{winston_str[-12:]}"
    else:
        lessthan_twelve = 12 - length
        winston_str = "0.{}{}".format("0" * lessthan_twelve, winston_str)

    return float(winston_str)


def ar_to_winston(ar_amount: str | int | float | Decimal) -> str:
    return str(int(Decimal(ar_amount) * 10**12))
