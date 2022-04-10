import logging
import logging.config
import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="project_name",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="project_name_env",
    load_dotenv=True,
)

logger_cfg = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": "%(asctime)s | %(levelname)s | %(process)d | %(thread)d | %(filename)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "logstash": {
            "format": "%(message)s",
            "class": "core.logs.LogStashV1Formatter",
            "datefmt": "%Y-%m-%dT%H:%M:%S.%f%z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
        "data_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "logstash",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "critical": {
            "level": "INFO",
            "handlers": settings.LOG_HANDELER.split(","),
            "propagate": False,
        }
    },
}


def setup_logging(config=None):
    """Set up logger"""

    if not config:
        config = logger_cfg

    cfg_dict = config
    if "telegram" in settings.LOG_HANDELER.split(","):
        cfg_dict["handlers"]["telegram"] = {
            "class": "core.logs.LogTelegramHandler",
            "token": settings.TELEGRAM_BOT_TOKEN,
            "chat_id": settings.TELEGRAM_GROUP_ID,
            "prefix": f"[INSURANCE]",
        }

    logging.config.dictConfig(cfg_dict)
    os.environ["LOGGER_ID"] = "main"
