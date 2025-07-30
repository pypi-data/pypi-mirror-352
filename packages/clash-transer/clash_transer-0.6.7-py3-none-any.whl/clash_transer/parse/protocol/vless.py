from typing import Any, Dict
from urllib.parse import ParseResult, unquote


def parse(url: ParseResult) -> Dict[str, Any]:
    link: ParseResult = url
    query_pairs = (i.split("=", 1) for i in link.query.split("&"))
    query_dict = {key: value for key, value in query_pairs}
    link_dict = {
        "name": unquote(link.fragment),
        "type": "vless",
        "server": link.hostname,
        "port": link.port,
        "uuid": link.username,
        "alterId": 0,
        "cipher": "auto",
        "udp": True,
        "flow": query_dict.get("flow", "xtls-rprx-vision"),
        "tls": True,
        "skip-cert-verify": query_dict['encryption'] == 'none',
        "servername": query_dict.get("servername", "apps.apple.com"),
        "reality-opts": {
            "public-key": query_dict["pbk"],
            "short-id": query_dict["sid"],
        },
        "client-fingerprint": query_dict.get("fp", "firefox"),
    }
    return link_dict
