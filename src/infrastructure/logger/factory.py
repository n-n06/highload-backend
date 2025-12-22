import logging
from src.infrastructure.logger.logstash_logger import LogstashLogger
from src.domain.protocols.logger_protocol import LoggerProtocol


def create_logger(
    name: str = "highload-backend-app",
    logstash_host: str = "logstash",
    logstash_port: int = 5000,
    level: int = logging.INFO
) -> LoggerProtocol:

    return LogstashLogger(
        name=name,
        logstash_host=logstash_host,
        logstash_port=logstash_port,
        level=level
    )
