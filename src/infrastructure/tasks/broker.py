
from taskiq_redis import RedisAsyncBroker

from src.bootstrap.config import settings

broker = RedisAsyncBroker(
    url=str(settings.redis_url),

    result_backend=None,

    task_id_generator=None,
)

def setup_broker():
    try:
        from src.infrastructure.tasks import tasks  # noqa: F401
    except ImportError:
        pass


