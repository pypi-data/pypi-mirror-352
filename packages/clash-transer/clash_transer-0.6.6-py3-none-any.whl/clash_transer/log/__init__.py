import logging
import logging.config

from ..config import CONFIG

__ALL__ = ["LOGGER"]


LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "normal": {
            "format": "[%(levelname)s]-[%(asctime)s][%(funcName)s:%(lineno)d] --- %(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "normal",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "my_clash_transer": {
            "handlers": ["stdout"],
            "propagate": False,
            "level": "DEBUG" if CONFIG.debug else "INFO",
        }
    },
}


logging.config.dictConfig(LOG_CONFIG)
LOGGER = logging.getLogger("my_clash_transer")
