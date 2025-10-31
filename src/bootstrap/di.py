import logging

from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.infrastructure.db.repositories.base_repo import (
    ProductRepository,
    UserRepository,
    LocationRepository,
    OrderRepository,
)
from src.infrastructure.db.dependencies import (
    get_engine,
    get_async_sessionmaker,
    get_async_session,
)
from src.infrastructure.logger.config import setup_logger
from src.infrastructure.logger.repositories.logger_repo import LoggingRepository

def db_provider()-> Provider:
    provider = Provider()

    provider.provide(
        get_engine,
        scope=Scope.APP
    )

    provider.provide(
        get_async_sessionmaker,
        scope=Scope.APP
    )

    provider.provide(
        get_async_session,
        scope=Scope.REQUEST
    )

    return provider


def repo_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)

    provider.provide(ProductRepository)
    provider.provide(UserRepository)
    provider.provide(OrderRepository)
    provider.provide(LocationRepository)

    return provider



def logger_provider()-> Provider:
    provider = Provider(scope=Scope.APP)
    logger = setup_logger()
    
    provider.provide(..., provides=LoggerProtocol)

    return provider


def setup_providers()->list[Provider]:
    return [
        db_provider(),
        repo_provider(),
        logger_provider()
    ]


def setup_di()->AsyncContainer:
    container = make_async_container(
        *setup_providers(),
        FastapiProvider()
    )

    return container
