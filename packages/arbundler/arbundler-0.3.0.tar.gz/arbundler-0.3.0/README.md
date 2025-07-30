# arbundler

A small package to interact with arweave bundlers, supports turbo API `https://upload.ardrive.io/api-docs`. 
Features:
- produces signature compliant with [ANS-104](https://github.com/ArweaveTeam/arweave-standards/blob/master/ans/ANS-104.md)
- supports only `ArweaveSigner` for now

## Example usage

```python
from arbundler import ArweaveSigner, ArBundlerClient

signer = ArweaveSigner.from_file("wallet.json")
client = ArBundlerClient(signer)

r = await client.upload_file("test.png", tags=[{"name": "content-type", "value": "image/png"}])
```
