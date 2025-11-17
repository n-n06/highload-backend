import logging

from dishka import Container, Provider, Scope, make_container
from dishka.integrations.fastapi import FastapiProvider

from src.domain.protocols.logger import LoggerProtocol
from src.infrastructure.db.repositories.base_repo import (
    ProductRepository,
    UserRepository,
    LocationRepository,
    OrderRepository,
    LocationProductRepository,
)
from src.infrastructure.db import (
    get_engine,
    get_async_sessionmaker,
    get_async_session,
)
from src.infrastructure.logger.logstash_logger import LogstashLogger



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
    provider.provide(LocationProductRepository)

    return provider


def service_provider() -> Provider:
    from src.application.services.orders import OrderService
    from src.application.services.inventory import InventoryService
    from src.application.services.locations import LocationService

    provider = Provider(scope=Scope.REQUEST)

    provider.provide(OrderService)
    provider.provide(InventoryService)
    provider.provide(LocationService)

    return provider



def logger_provider() -> Provider:
    provider = Provider(scope=Scope.APP)
    provider.provide(LogstashLogger, provides=LoggerProtocol)

    return provider


def setup_providers()->list[Provider]:
    return [
        db_provider(),
        repo_provider(),
        service_provider(),
        logger_provider(),
        redis_provider(),
        task_provider(),
    ]


def setup_di()->Container:
    container = make_container(
        *setup_providers(),
        FastapiProvider()
    )

    return container
