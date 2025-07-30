from typing import Any, Dict
from urllib.parse import ParseResult, urlparse

from ..base64_decode import b64decode


def parse(url: ParseResult) -> Dict[str, Any]:
    parsed_url: ParseResult = url
    f_str = b64decode(parsed_url.netloc)
    link_obj = urlparse(f_str)
    server = link_obj.scheme
    try:
        port, protocol, cipher, obfs, password_base64 = link_obj.path.strip("/").split(
            ":"
        )
    except ValueError:
        server, port, protocol, cipher, obfs, password_base64 = link_obj.path.strip(
            "/"
        ).split(":")
    password = b64decode(password_base64)
    query_pairs = (i.split("=", 1) for i in link_obj.query.split("&"))
    query_dict = {key: value for key, value in query_pairs}
    protoparam = b64decode(query_dict["protoparam"])
    name = b64decode(query_dict["remarks"])
    obfsparam = b64decode(query_dict["obfsparam"])
    obfsparam = obfsparam if obfsparam else "none"
    link_dict = {
        "name": name,
        "type": "ssr",
        "server": server,
        "port": port,
        "cipher": cipher,
        "password": password,
        "protocol": protocol,
        "protocol-param": protoparam,
        "obfs": obfs,
        "obfs-param": obfsparam,
    }
    return link_dict
