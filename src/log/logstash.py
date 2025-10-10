import logging.config

from src.config import settings

LOGSTASH_HOST = settings.LOGSTASH_HOST
LOGSTASH_PORT = settings.LOGSTASH_PORT

logging_config_dict = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "[%(asctime)s] | [%(levelname)s] %(name)s: %(message)s"
        },
    },

    "handlers": {
        # local debugging
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        # custom logs to logstash
        "logstash": {
            "class": "logstash_async.handler.AsynchronousLogstashHandler",
            "host": LOGSTASH_HOST,
            "port": LOGSTASH_PORT,
            "database_path": "logstash.db"
        },
    },

    "loggers": {
        "erp-module-app": {
            "handlers": ["logstash"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config_dict)
logger = logging.getLogger("erp-module-app")
