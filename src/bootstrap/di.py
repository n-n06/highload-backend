from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.fastapi import FastapiProvider


def db_provider()-> Provider:...


def repo_provider()-> Provider:...


def logger_provider()-> Provider:...


def setup_providers()->list[Provider]:...


"""def user_id_provider() -> Provider:
    provider = Provider()

    provider.provide(get_user_id, scope=Scope.REQUEST, provides=UserId)

    return provider"""


def setup_di()->AsyncContainer:
    container = make_async_container(
        *setup_providers(),
        FastapiProvider()
    )

    return container