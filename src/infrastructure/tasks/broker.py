
from taskiq_redis import ListQueueBroker

from src.bootstrap.config import settings

broker = ListQueueBroker(
    url=str(settings.redis_url)
)

def setup_broker():
    try:
        from src.infrastructure.tasks import tasks  # noqa: F401
    except ImportError:
        pass


