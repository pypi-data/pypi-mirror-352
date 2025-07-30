import argparse
import os
from collections import namedtuple
from pathlib import Path

from yaml import full_load

__all__ = ["CONFIG"]
__Config__ = namedtuple(
    "Config",
    ["configs", "debug", "proxy", "pwd"],
)

description = """
mct 是 ss 订阅转换工具，用于聚合多个ss订阅文件，并转换为clash配置文件。
"""

parser = argparse.ArgumentParser(
    prog="mct",
    description=description,
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "-c",
    "--config",
    default="config.yaml",
    required=False,
    help="指定配置文件，默认为 $PWD/config.yaml",
)
parser.add_argument(
    "-p",
    "--proxy",
    default=None,
    required=False,
    help="设置代理服务器",
)
parser.add_argument(
    "-d", "--debug", required=False, help="debug mode", action="store_true"
)
parser.add_argument("--pwd", default=None, required=False, help="指定工作的文件夹")
args = parser.parse_args()

if args.pwd:
    cwd = Path(args.pwd)
    if not cwd.is_dir():
        raise FileNotFoundError(f"`{args.pwd}` 文件夹不存在")
    os.chdir(cwd)

__config_path__ = Path(args.config)
if __config_path__.is_file():
    with open(__config_path__) as f:
        __CONFIG__ = full_load(f)
else:
    raise FileNotFoundError("需要指定配置文件位置，command -c <config file>")

CONFIG = __Config__(__CONFIG__, args.debug or __CONFIG__["debug"], args.proxy, args.pwd)
