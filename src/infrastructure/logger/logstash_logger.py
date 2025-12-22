import sys
import logging
from typing import Any

from logstash_async.handler import AsynchronousLogstashHandler


class LogstashLogger:

    def __init__(
        self,
        name: str,
        logstash_host: str,
        logstash_port: int,
        level: int = logging.INFO
    ):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)


        self._logger.handlers.clear()


        logstash_handler = AsynchronousLogstashHandler(
            host=logstash_host,
            port=logstash_port,
            database_path="logstash.db"
        )
        logstash_handler.setLevel(level)


        console_formatter = logging.Formatter(
            "[%(asctime)s] | [%(levelname)s] %(name)s: %(message)s"
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)


        self._logger.addHandler(logstash_handler)
        self._logger.addHandler(console_handler)

    def info(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            self._logger.info(message, extra=kwargs)
        else:
            self._logger.info(message)

    def warning(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            self._logger.warning(message, extra=kwargs)
        else:
            self._logger.warning(message)

    def error(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            self._logger.error(message, extra=kwargs)
        else:
            self._logger.error(message)

    def exception(self, message: str, exc: Exception | None = None, **kwargs: Any) -> None:
        if kwargs:
            self._logger.exception(message, exc_info=exc, extra=kwargs)
        else:
            self._logger.exception(message, exc_info=exc)

    def debug(self, message: str, **kwargs: Any) -> None:
        if kwargs:
            self._logger.debug(message, extra=kwargs)
        else:
            self._logger.debug(message)

    @property
    def logger(self) -> logging.Logger:
        return self._logger
