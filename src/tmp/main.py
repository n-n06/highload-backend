import sys
import os


sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)


import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.auth.router import auth_router
from src.locations.router import router as locations_router
from src.orders.router import router as orders_router
from src.products.router import router as products_router
from src.log.middleware import LogMiddleware


app = FastAPI()
app.add_middleware(LogMiddleware)

app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(orders_router)
app.include_router(products_router)

@app.get("/")
async def redirection():
    return RedirectResponse("/docs")

def main():
    uvicorn.run("src.main:app", reload=True)

