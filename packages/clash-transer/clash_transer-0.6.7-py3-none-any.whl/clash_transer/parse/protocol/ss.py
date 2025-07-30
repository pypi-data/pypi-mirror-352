from typing import Any, Dict
from urllib.parse import ParseResult, unquote

from ..base64_decode import b64decode


def parse(url: ParseResult) -> Dict[str, Any]:
    link: ParseResult = url
    cipher, password = b64decode(link.username).split(":", 1)
    server = link.hostname
    port = link.port
    name = unquote(link.fragment)
    link_dict = {
        "name": name,
        "type": "ss",
        "server": server,
        "port": port,
        "cipher": cipher,
        "password": password,
        "udp": True,
        "protocol": "origin",
    }
    return link_dict
