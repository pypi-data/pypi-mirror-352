from typing import Any, Dict, Iterator, Optional, Set
from urllib.parse import ParseResult, urlparse

import yaml

from ..log import LOGGER
from ..worker.vars import dist_file_v
from .base64_decode import b64decode
from .protocol import parse_hysteria2, parse_ss, parse_ssr, parse_vless, parse_vmess


class Parse:
    @classmethod
    def parse(cls, text: str, suffix: str):
        return cls(text, suffix)

    @classmethod
    def parse_text(cls, text: str, deny_protocol: Set[str]):
        return cls(text, deny_protocol=deny_protocol)

    def __init__(
        self,
        text: str,
        suffix: Optional[str] = None,
        deny_protocol: Optional[Set[str]] = None,
    ) -> None:
        self.server_ports = set()
        self.deny_protocol = deny_protocol if isinstance(deny_protocol, set) else set()
        if suffix is None:
            suffix = ""
        match suffix.lower():
            case "list":
                self.res = self.parse_list(text)
            case _:
                try:
                    info = yaml.full_load(text)
                    # LOGGER.info(info)
                    if not isinstance(info, dict):
                        raise TypeError
                    self.res = self.parse_clash(info, self.deny_protocol)
                except Exception:
                    self.res = self.parse_text_seprate_lines(text, self.deny_protocol)

        LOGGER.info("解析完成 %s", dist_file_v.get().name)

    def trans_hy2(self, info: Dict[str, Any]) -> Dict[str, Any]:
        if info["type"] != "hysteria2":
            return info
        if "password" not in info:
            info["password"] = info.get("auth", "")
        if "down" not in info:
            info["down"] = str(info.get("down-speed", "1200 Mbps"))
        if "up" not in info:
            info["up"] = str(info.get("up-speed", "100 Mbps"))
        if "fringerprint" not in info:
            info["fringerprint"] = "ios"
        return info

    def parse_clash(self, info: Dict[str, Any], deny_protocol: Set[str]):
        link_dicts_: Iterator[Dict[str, Any]] = (
            i for i in info["proxies"] if i["type"] not in deny_protocol
        )
        link_dicts: Iterator[Dict[str, Any]] = (
            self.trans_hy2(i) for i in link_dicts_
        )       
        yield from link_dicts

    def parse_one_line_text(self, text: str):
        link: ParseResult = urlparse(text)
        return self.parse_one_link_obj(link)

    def parse_one_link_obj(self, link: ParseResult) -> Optional[Dict[str, Any]]:
        match link.scheme:
            case "ss":
                return parse_ss(link)
            case "ssr":
                return parse_ssr(link)
            case "vless":
                return parse_vless(link)
            case "vmess":
                return parse_vmess(link)
            case "hysteria2":
                return parse_hysteria2(link)
            case _:
                LOGGER.debug(link)
                return None

    def parse_text_seprate_lines(self, text, deny_protocol: Set[str]):
        link_lines = b64decode(text).strip().splitlines()
        link_dicts_1: Iterator[Optional[Dict[str, Any]]] = (
            self.parse_one_line_text(i) for i in link_lines if i
        )
        link_dicts_2: Iterator[Dict[str, Any]] = (i for i in link_dicts_1 if i)
        link_dicts: Iterator[Dict[str, Any]] = (
            i for i in link_dicts_2 if i["type"] not in deny_protocol
        )
        yield from link_dicts

    def parse_list(self, text):
        for line in text.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("/"):
                continue
            try:
                rule, addr, do = line.split(",")
                rule, addr, do = rule.strip(), addr.strip(), do.strip()
            except ValueError:
                continue
            match rule.lower():
                case "host":
                    rule = "DOMAIN"
                case "ip-cidr":
                    rule = "IP-CIDR"
                case "host-suffix":
                    rule = "DOMAIN-SUFFIX"
                case "host-keyword":
                    rule = "DOMAIN-KEYWORD"
                case _:
                    continue
            match do.upper():
                case "DIRECT":
                    do = "直连"
                case "PROXY":
                    do = "PROXY"
                case "REJECT":
                    do = "禁连"
                case "OUTSIDE":
                    do = "Apple OutSide"
                case _:
                    pass
            # LOGGER.debug("%s,%s,%s", rule, addr, do)
            yield (rule, addr, do)
