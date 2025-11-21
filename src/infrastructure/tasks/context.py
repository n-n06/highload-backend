"""
Task context manager for providing dependencies to background tasks.

This module handles database session and repository initialization for taskiq workers,
allowing tasks to access the same repositories and services as the API.
"""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.infrastructure.db.repositories.base_repo import (
    OrderRepository,
    LocationRepository,
    LocationProductRepository,
    ProductRepository,
    UserRepository,
)
from src.infrastructure.logger.factory import create_logger
from src.domain.protocols.logger_protocol import LoggerProtocol
from src.bootstrap.config import settings


class TaskContext:

    def __init__(
        self,
        session: AsyncSession,
        logger: LoggerProtocol,
    ):
        self.session = session
        self.logger = logger

        self.order_repo = OrderRepository(session)
        self.location_repo = LocationRepository(session)
        self.location_product_repo = LocationProductRepository(session)
        self.product_repo = ProductRepository(session)
        self.user_repo = UserRepository(session)


_session_maker: async_sessionmaker | None = None


async def _get_session_maker() -> async_sessionmaker:
    global _session_maker

    if _session_maker is None:
        engine = create_async_engine(
            str(settings.postgres_url),
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=5,
        )
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    return _session_maker


@asynccontextmanager
async def get_task_context() -> TaskContext:

    session_maker = await _get_session_maker()
    session = session_maker()
    logger = create_logger(
        name="taskiq-worker",
        logstash_host=settings.LOGSTASH_HOST,
        logstash_port=settings.LOGSTASH_PORT,
    )

    context = TaskContext(session, logger)

    try:
        yield context
    finally:
        await session.close()
