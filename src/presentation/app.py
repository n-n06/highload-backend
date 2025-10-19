import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, HTTPException, Response, status

from src.bootstrap.di import setup_di
from src.presentation.handlers import router

app = FastAPI()

setup_dishka(setup_di(), app)
app.include_router(router)

@app.get('/health')
async def health():
    return Response(status_code=status.HTTP_200_OK)


if __name__ == '__main__':
    uvicorn.run('src.presentation.app:app', host='0.0.0.0', port=8009, reload=True)