import hashlib


def deep_hash(data) -> bytes:
    length = len(data)

    if isinstance(data, list):
        tag = b"list" + str(length).encode()
        return deep_hash_chunks(data, hashlib.sha384(tag).digest())

    tag = b"blob" + str(length).encode()
    tagged_hash = hashlib.sha384(tag).digest() + hashlib.sha384(data).digest()

    return hashlib.sha384(tagged_hash).digest()


def deep_hash_chunks(chunks, acc) -> bytes:
    if len(chunks) < 1:
        return acc

    hash_pair = acc + deep_hash(chunks[0])

    new_acc = hashlib.sha384(hash_pair).digest()

    return deep_hash_chunks(chunks[1:], new_acc)
