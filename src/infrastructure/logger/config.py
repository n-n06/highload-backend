import sys
import logging.config
from logstash_async.handler import AsynchronousLogstashHandler

from src.bootstrap.config import settings


LOGSTASH_HOST = settings.LOGSTASH_HOST
LOGSTASH_PORT = settings.LOGSTASH_PORT


def setup_logger() -> logging.Logger:

    logger = logging.getLogger("epp-module-app")
    logger.setLevel(logging.INFO)

    logstash_handler = AsynchronousLogstashHandler(
        host=LOGSTASH_HOST,  
        port=LOGSTASH_PORT,
        database_path="logstash.db"  
    )
    logstash_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(
        "[%(asctime)s] | [%(levelname)s] %(name)s: %(message)s"
    ) 

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(logstash_handler)
    logger.addHandler(console_handler)

    return logger
