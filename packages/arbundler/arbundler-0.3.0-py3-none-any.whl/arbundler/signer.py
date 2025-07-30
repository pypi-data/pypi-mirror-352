import json
import logging
from enum import IntEnum, auto

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from jwt import PyJWK

from arbundler.helpers.converters import owner_to_address
from arbundler.helpers.hashing import base64url_decode

logger = logging.getLogger(__name__)


class SignatureType(IntEnum):
    ARWEAVE = auto()
    ED25519 = auto()
    ETHEREUM = auto()
    SOLANA = auto()
    INJECTEDAPTOS = auto()
    MULTIAPTOS = auto()
    TYPEDETHEREUM = auto()


class ArweaveSigner:
    HASH = "sha256"
    SIGNATURE_TYPE = SignatureType.ARWEAVE

    def __init__(self, jwk_data: dict) -> None:
        self.jwk_data = jwk_data
        self.jwk = PyJWK(self.jwk_data, algorithm="RS256")

        self.public_key = base64url_decode(self.owner)
        self.address = owner_to_address(self.owner)

    @property
    def owner(self):
        return self.jwk_data["n"]

    @classmethod
    def from_file(cls, jwk_file_path: str) -> "ArweaveSigner":
        with open(jwk_file_path) as r:
            return cls(json.load(r))

    def sign(self, message: bytes):
        return self.jwk.key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
