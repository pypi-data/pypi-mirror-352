import base64
from typing import Union

__all__ = ["b64decode"]


def b64decode(text: Union[str, bytes]) -> str:
    if isinstance(text, str):
        byte = text.encode("utf-8")
    else:
        byte = text
    if not byte.endswith(b"="):
        byte = byte + b"=" * (4 - (len(byte) % 4))
    res = base64.urlsafe_b64decode(byte).decode("utf-8")
    return res
