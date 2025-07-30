from typing import Any, Dict
from urllib.parse import ParseResult, unquote


def parse(url: ParseResult) -> Dict[str, Any]:
    link: ParseResult = url
    query_pairs = (i.split("=", 1) for i in link.query.split("&"))
    query_dict = {key: value for key, value in query_pairs}
    link_dict = {
        "name": unquote(link.fragment),
        "server": link.hostname,
        "port": link.port,
        "sni": query_dict.get("sni", None),
        "up": 1000,
        "down": 1000,
        "skip-cert-verify": query_dict.get("insecure") == "1",
        "type": "hysteria2",
        "password": link.username,
    }
    return link_dict
