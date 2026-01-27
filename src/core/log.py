# import os
from os import environ
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"

DEFAULT_FMT = "%(asctime)s %(levelname)s %(name)s %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
FORMATTERS = {
    "str": {"format": DEFAULT_FMT, "datefmt": DATEFMT},
    "rich": {
        "format": "\\[%(name)s] -  %(message)s",
        "datefmt": "[%X]",
    },
    # "json": {
    #    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    #    "format": DEFAULT_FMT,
    # },
}

""" if environ.get("DEBUG", False):
    LOG_LEVEL = "DEBUG"
else:
    LOG_LEVEL = "WARNING" """

LOG_LEVEL = "DEBUG"

HANDLERS = {
    "console": {
        "level": LOG_LEVEL,
        "class": "rich.logging.RichHandler",
        "show_time": True,
        "show_level": True,
        "show_path": False,  # não mostra o caminho do arquivo
        "formatter": "rich",
        "rich_tracebacks": True,
        "markup": True,
    }
}

DEV_LOGGERS = {
    "uvicorn": {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": False,
    },
    "app": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
}

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS,
    "handlers": HANDLERS,
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": DEV_LOGGERS,
}
