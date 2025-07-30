import json
from typing import Any, Dict
from urllib.parse import ParseResult

from ..base64_decode import b64decode


def parse(url: ParseResult) -> Dict[str, Any]:
    link: ParseResult = url
    netloc = b64decode(link.netloc)
    info = json.loads(netloc)
    server = info["add"]
    port = int(info["port"])
    link_dict = {
        "name": info["ps"],
        "type": "vmess",
        "server": server,
        "port": port,
        "uuid": info["id"],
        "alterId": info["aid"],
        "cipher": "auto",
        "udp": True,
        "tls": True,
        "skip-cert-verify": True,
        "servername": info.get("sni", ""),
        "network": info["net"],
        "grpc-opts": {"grpc-service-name": info["path"]},
    }
    return link_dict
