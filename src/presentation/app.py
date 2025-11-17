from contextlib import asynccontextmanager
import uvicorn
import asyncio
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Response, status

import sys
import os


sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

from src.bootstrap.di import setup_di
from src.domain.protocols.logger import LoggerProtocol
from src.infrastructure.logger.middleware import LogMiddleware
from src.presentation.handlers import router
from src.presentation.handlers.users import auth_router

app = FastAPI()

container = setup_di()

app = FastAPI()

from src.infrastructure.logger.factory import create_logger
from src.bootstrap.config import settings

logger = create_logger(
    name="highload-backend-app",
    logstash_host=settings.LOGSTASH_HOST,
    logstash_port=settings.LOGSTASH_PORT
)


app.add_middleware(LogMiddleware, logger=logger)

setup_dishka(container, app)

logger = container.get(LoggerProtocol)

app.add_middleware(LogMiddleware, logger=logger)
app.include_router(router)
app.include_router(auth_router)

if __name__ == '__main__':
    uvicorn.run("src.presentation.app:app", host='0.0.0.0', port=8009, reload=True)
