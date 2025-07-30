from typing import TypedDict

MAX_TAG_BYTES = 4096


class Tag(TypedDict):
    name: str
    value: str


class AVSCTap:
    def __init__(self, buf: bytearray | None = None, pos: int = 0) -> None:
        self.buf = buf if buf is not None else bytearray(MAX_TAG_BYTES)
        self.pos = pos

    def write_tags(self, tags: list[Tag]) -> None:
        if not isinstance(tags, list):
            raise ValueError("Input must be a list")

        n = len(tags)
        if n:
            self.write_long(n)
            for tag in tags:
                if not isinstance(tag["name"], str) or not isinstance(tag["value"], str):
                    raise ValueError(f"Invalid tag format for {tag}, expected {{name: str, value: str}}")
                self.write_string(tag["name"])
                self.write_string(tag["value"])
            self.write_long(0)

    def to_bytes(self) -> bytes:
        if self.pos > len(self.buf):
            raise ValueError(f"Too many tag bytes ({self.pos} > {len(self.buf)})")
        return bytes(self.buf[: self.pos])

    def write_long(self, n: int) -> None:
        if -1073741824 <= n < 1073741824:
            m = n << 1 if n >= 0 else (~n << 1) | 1
            while m:
                self.buf[self.pos] = m & 0x7F
                m >>= 7
                if m:
                    self.buf[self.pos] |= 0x80
                self.pos += 1
        else:
            f = n * 2 if n >= 0 else -n * 2 - 1
            while f >= 1:
                self.buf[self.pos] = int(f) & 0x7F
                f /= 128
                if f >= 1:
                    self.buf[self.pos] |= 0x80
                self.pos += 1

    def write_string(self, s: str) -> None:
        len_s = len(s)
        self.write_long(len_s)
        self.buf[self.pos : self.pos + len_s] = s.encode("utf-8")
        self.pos += len_s


def serialize_tags(tags: list[Tag]) -> bytes:
    tap = AVSCTap()
    tap.write_tags(tags)
    return tap.to_bytes()
