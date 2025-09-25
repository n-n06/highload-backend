import sys
import os

sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

import uvicorn
from fastapi import FastAPI

from auth.router import auth_router
from locations.router import router as locations_router
from orders.router import router as orders_router
from products.router import router as products_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(orders_router)
app.include_router(products_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
