import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Response, status

from src.bootstrap.di import setup_di
from src.infrastructure.logger.middleware import LogMiddleware
from src.infrastructure.user.admin import create_admin_user_lifespan
from src.presentation.handlers import router, setup_routers


container = setup_di()

app = FastAPI(lifespan=create_admin_user_lifespan)

from src.infrastructure.logger.factory import create_logger
from src.bootstrap.config import settings

logger = create_logger(
    name="highload-backend-app",
    logstash_host=settings.LOGSTASH_HOST,
    logstash_port=settings.LOGSTASH_PORT
)


app.add_middleware(LogMiddleware, logger=logger)

setup_dishka(container, app)

setup_routers()
app.include_router(router)


@app.get('/health')
async def health():
    return Response(status_code=status.HTTP_200_OK)


if __name__ == '__main__':
    uvicorn.run('src.presentation.app:app', host='0.0.0.0', port=8009, reload=True)

