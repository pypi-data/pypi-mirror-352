import datetime
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Set

from yaml import dump

from ..config import CONFIG
from ..downloader import Downloader, DownloadRequest, DownloadText
from ..log import LOGGER
from ..parse import Parse
from .detail import get as get_proxy_groups
from .vars import dist_file_v, rules_v, servers_v


class Worker:
    def __init__(self) -> None:
        self.configs = CONFIG.configs
        self.counter = Counter()
        self.deny_protocol: Set[str] = set(self.configs.get("deny_protocol", list()))

    def download(self) -> Iterable[DownloadText]:
        downloader = Downloader(default_store_path=self.configs["store_path"])
        d = [i for i in CONFIG.configs["subscriptions"]]
        s = [
            DownloadRequest(
                i["url"],
                i["dist"],
                datetime.timedelta(seconds=i.get("expire", 86400)),
                self.deny_protocol.union(set(i.get("deny_protocol", list()))),
                i.get("ua", "")
            )
            for i in d
        ]
        download_resps: Iterable[DownloadText] = downloader.downloads(s)
        return download_resps

    def parse(self, download_resps: Iterable[DownloadText]):
        servers = []
        rules = []
        erros = 0
        for resp in download_resps:
            if resp.text is None:
                LOGGER.error("下载失败 %s", resp.url)
                erros += 1
                continue
            suffix = resp.dist.suffix.strip(".")
            dist_file_v.set(resp.dist)
            if suffix.lower() == "list":
                for i in Parse.parse(resp.text, suffix).res:
                    rules.append(i)
            else:
                for i in Parse.parse_text(
                    resp.text, deny_protocol=resp.deny_protocol
                ).res:
                    if i["type"] in self.deny_protocol:
                        continue
                    # i["name"] = i["name"].replace(" ", "")
                    self.counter += Counter({i["name"]: 1})
                    if self.counter[i["name"]] > 1:
                        i["name"] = f"""{i["name"]}_{self.counter[i["name"]] - 1:02d}"""
                    servers.append(i)
        if erros:
            sys.exit(1)
        # store_map = {
        #     "DST-PORT": 10,
        #     "SRC-IP-CIDR": 20,
        #     "IP-CIDR": 30,
        #     "DOMAIN": 40,
        #     "DOMAIN-KEYWORD": 60,
        #     "DOMAIN-SUFFIX": 50,
        # }
        # rules = sorted(rules, key=lambda x: store_map[x[0]])
        exclude_server_regex = re.compile(
            r"|".join(
                [re.escape(keyword) for keyword in self.configs["servers"]["exclude"]]
            )
        )
        servers = [
            server
            for server in servers
            if not re.findall(exclude_server_regex, server["name"])
        ]
        return servers, rules

    def check(self, proxy_group, rules):
        action_set = set()
        group_set = set()
        for _, _, action in rules[:-1]:
            action_set.add(action)
        for group in proxy_group:
            group_set.add(group["name"])
        if "DIRECT" in action_set:
            action_set.remove("DIRECT")
        if "REJECT" in action_set:
            action_set.remove("REJECT")
        diffs = action_set.difference(group_set)
        if diffs:
            LOGGER.error("这些转发组没有设置：%s", ",".join(list(diffs)))
            raise TypeError()

    def combine(self):
        frame = CONFIG.configs["frame"]
        frame["proxies"] = self.server
        frame["proxy-groups"] = self.proxy_groups
        frame["rules"] = self.rules
        return frame
        # cellphone_rule = {
        #     "name": "ssid-group",
        #     "type": "select",
        #     "proxies": ["PROXY", "DIRECT"],
        #     "ssid-policy": {
        #         "ChinaNet-Tn9y_5G": "DIRECT",
        #         "aaaTop1_5G": "DIRECT",
        #         "a13101_5G": "DIRECT",
        #         "cellular": "PROXY",
        #         "default": "PROXY",
        #     },
        # }
        # res["proxy-groups"].append(cellphone_rule)
        # return yaml.dump(res, allow_unicode=True)

    @staticmethod
    def split_rule(rule: str):
        commas = [m.start() for m in re.finditer(",", rule)]
        if len(commas) < 2:
            return rule.split(",")
        first = commas[0]
        last = commas[-1]

        part1 = rule[:first]
        part2 = rule[first + 1 : last]
        part3 = rule[last + 1 :]

        return [part1, part2, part3]

    def do(self):
        download_resps = self.download()
        servers, rules = self.parse(download_resps)
        servers.append(
            {
                "cipher": "chacha20-ietf-poly1305",
                "name": "_占位",
                "password": "xxxxxxxxxxxxxxxx",
                "port": 65534,
                "protocol": "origin",
                "server": "2.2.2.2",
                "type": "ss",
                "udp": False,
            }
        )
        servers_v.set(servers)
        rules_v.set(rules)

        self.proxy_groups = get_proxy_groups()
        self.server = servers
        _rules = (
            [self.split_rule(i) for i in self.configs["rules"]["add_before"]]
            + rules
            + [self.split_rule(i) for i in self.configs["rules"]["add_last"]]
        )
        self.check(self.proxy_groups, _rules)
        self.rules = [",".join(rule) for rule in _rules]
        res = self.combine()
        dist_file = Path(self.configs.get("dist_file"))
        if not dist_file.is_absolute():
            dist_file = Path(os.getcwd()) / dist_file
        with open(dist_file, "w") as f:
            dump(res, f, allow_unicode=True)
            LOGGER.info("新的 clash 配置文件写入 %s", dist_file.as_posix())
