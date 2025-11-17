import logging
import sys
from typing import Any

from logstash_async.handler import AsynchronousLogstashHandler

from src.domain.protocols.logger import LoggerProtocol
from src.bootstrap.config import settings

class LogstashLogger(LoggerProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger("erp-module-app")
        self.logger.setLevel(logging.INFO)

        logstash_handler = AsynchronousLogstashHandler(
            host=settings.LOGSTASH_HOST,  
            port=settings.LOGSTASH_PORT,
            database_path="logstash.db"
        )
        logstash_handler.setLevel(logging.INFO)

        console_formatter = logging.Formatter(
            "[%(asctime)s] | [%(levelname)s] %(name)s: %(message)s"
        ) 
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)


        self.logger.addHandler(logstash_handler)
        self.logger.addHandler(console_handler)

        
    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(message, extra=kwargs)


    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(message, extra=kwargs)


    def error(self, message: str, **kwargs: Any) -> None:
        self.logger.error(message, extra=kwargs)


    def exception(self, message: str, **kwargs):
        self.logger.exception(message, extra=kwargs)
