from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def create_admin_user_lifespan(app: FastAPI):
    yield
