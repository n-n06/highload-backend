from typing import Any, Protocol

class LoggerProtocol(Protocol):
    def info(self, message: str, **kwargs: Any) -> None:
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        ...

    def exception(self, message: str, exc: Exception | None = None, **kwargs: Any) -> None:
        ...

    def debug(self, message: str, **kwargs: Any) -> None:
        ...