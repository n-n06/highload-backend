from typing import Any, Generic, Protocol, TypeVar

class LoggerProtocol(Protocol):
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info-level message"""
        raise NotImplementedError()        

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning-level message"""
        raise NotImplementedError()        

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error-level message"""
        raise NotImplementedError()        

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback"""
        raise NotImplementedError()        
