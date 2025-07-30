from pathlib import Path

import anyio
import httpx
from furl import furl

from arbundler.helpers.serializers import decode_json_loosely
from arbundler.signer import ArweaveSigner

from ..data_item import DataItem
from ..tag import Tag
from .types import UploadResponse


class ArBundlerClient:
    def __init__(self, signer: ArweaveSigner, api_url: str = "https://upload.ardrive.io") -> None:
        self.signer = signer
        self.furl = furl(api_url)

    async def upload_file(self, path_or_data: bytes | str | Path, tags: list[Tag] | None = None) -> UploadResponse:
        if isinstance(path_or_data, (str, Path)):
            async with await anyio.open_file(path_or_data, "rb") as r:
                raw_data = await r.read()
        else:
            raw_data = path_or_data

        data_item = DataItem(raw_data, self.signer, tags)
        data_item.sign()

        async with httpx.AsyncClient() as c:
            r = await c.post(
                (self.furl / "tx").url,
                content=data_item.to_binary(),
                headers={"Content-Type": "application/octet-stream"},
            )
            r.raise_for_status()
        return decode_json_loosely(r.content, UploadResponse)
