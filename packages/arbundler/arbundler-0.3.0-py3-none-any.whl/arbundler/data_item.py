import hashlib

from arbundler.helpers.deep_hash import deep_hash
from arbundler.helpers.hashing import base64url_decode, base64url_encode
from arbundler.signer import ArweaveSigner
from arbundler.tag import Tag, serialize_tags


class DataItem:
    def __init__(
        self,
        raw_data: bytes,
        signer: ArweaveSigner,
        tags: list[Tag] | None = None,
        target: str = "",
        anchor: str = "",
    ) -> None:
        self.raw_data = raw_data
        self.signer = signer
        self.tags = tags or []
        self.target = target
        self.anchor = anchor

        self._raw_signature: bytes | None = None
        self._raw_id: bytes | None = None

    @property
    def data(self) -> str:
        return base64url_encode(self.raw_data).decode()

    @property
    def signature(self) -> str:
        if not self._raw_signature:
            raise ValueError("DataItem is not signed!")
        return base64url_encode(self._raw_signature).decode()

    @property
    def id(self) -> str:
        if not self._raw_id:
            raise ValueError("DataItem is not signed!")
        return base64url_encode(self._raw_id).decode()

    def get_signature_data(self) -> bytes:
        return deep_hash(
            [
                b"dataitem",
                b"1",
                str(self.signer.SIGNATURE_TYPE.value).encode(),
                self.signer.public_key,
                base64url_decode(self.target),
                base64url_decode(self.anchor),
                serialize_tags(self.tags),
                self.raw_data,
            ]
        )

    def sign(self):
        data_to_sign = self.get_signature_data()
        raw_signature = self.signer.sign(data_to_sign)

        self._raw_signature = raw_signature
        self._raw_id = hashlib.sha256(raw_signature).digest()

    def to_binary(self) -> bytes:
        owner = self.signer.public_key
        owner_length = len(owner)

        target = base64url_decode(self.target)
        target_length = 1 + len(target)

        anchor = base64url_decode(self.target) if self.anchor else None
        anchor_length = 1 + (len(anchor) if anchor else 0)

        tags = serialize_tags(self.tags)
        tags_length = 16 + len(tags)

        length = (
            2
            + len(self._raw_signature)
            + len(self.signer.public_key)
            + target_length
            + anchor_length
            + tags_length
            + len(self.raw_data)
        )
        bytes_arr = bytearray(length)
        bytes_arr[0:2] = self.signer.SIGNATURE_TYPE.to_bytes(2, "little")

        type_offset = 2
        bytes_arr[type_offset : type_offset + len(self._raw_signature)] = self._raw_signature

        owner_offset = type_offset + len(self._raw_signature)
        bytes_arr[owner_offset : owner_offset + owner_length] = owner

        target_offset = owner_offset + owner_length
        if target:
            if len(target) != 32:
                raise ValueError("Target must be 32 bytes")
            bytes_arr[target_offset] = 1
            bytes_arr[target_offset + 1 : target_offset + 1 + len(target)] = target
        else:
            bytes_arr[target_offset] = 0

        anchor_offset = target_offset + target_length
        if anchor:
            if len(anchor) != 32:
                raise ValueError("Anchor must be 32 bytes")
            bytes_arr[anchor_offset] = 1
            bytes_arr[anchor_offset + 1 : anchor_offset + 1 + len(anchor)] = anchor
        else:
            bytes_arr[anchor_offset] = 0

        tags_offset = anchor_offset + anchor_length
        bytes_arr[tags_offset : tags_offset + 8] = len(self.tags).to_bytes(8, "little")
        bytes_arr[tags_offset + 8 : tags_offset + 16] = (len(tags) if tags else 0).to_bytes(8, "little")
        if tags:
            bytes_arr[tags_offset + 16 : tags_offset + 16 + len(tags)] = tags

        data_offset = tags_offset + tags_length
        bytes_arr[data_offset : data_offset + len(self.raw_data)] = self.raw_data

        return bytes(bytes_arr)

    def to_dict(self) -> dict[str, str]:
        return {
            "signature": self.signature,
            "owner": self.signer.owner,
            "target": self.target,
            "tags": self.tags,
            "data": self.data,
        }
