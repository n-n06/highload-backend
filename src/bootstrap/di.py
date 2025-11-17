from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.fastapi import FastapiProvider

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
from src.domain.protocols.logger_protocol import LoggerProtocol
from src.infrastructure.logger.factory import create_logger
from src.infrastructure.redis.client import RedisClient, get_redis_client
from src.infrastructure.tasks.broker import broker
from src.bootstrap.config import settings

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

    def get_logger() -> LoggerProtocol:
        return create_logger(
            name="highload-backend-app",
            logstash_host=settings.LOGSTASH_HOST,
            logstash_port=settings.LOGSTASH_PORT
        )

    provider.provide(get_logger, provides=LoggerProtocol)

    return provider


def redis_provider() -> Provider:
    provider = Provider(scope=Scope.APP)

    provider.provide(get_redis_client, provides=RedisClient)

    return provider


def task_provider() -> Provider:
    provider = Provider(scope=Scope.APP)

    def get_broker():
        return broker

    provider.provide(get_broker, provides=type(broker))

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


def setup_di()->AsyncContainer:
    container = make_async_container(
        *setup_providers(),
        FastapiProvider()
    )

    return container
