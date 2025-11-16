import sys
import os

sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

"""
===Application Creation stuff===
"""

from src.db import load_all_models
load_all_models()

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.auth.router import auth_router
from src.auth.admin import lifespan
from src.locations.router import location_router
from src.locations.inventory_router import inventory_router
from src.orders.router import order_router
from src.products.router import product_router


from src.log.middleware import LogMiddleware


app = FastAPI(lifespan=lifespan)
app.add_middleware(LogMiddleware)

app.include_router(auth_router)
app.include_router(location_router)
app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(product_router)

@app.get("/")
async def redirection():
    return RedirectResponse("/docs")

def main():
    uvicorn.run("src.main:app", reload=True)

