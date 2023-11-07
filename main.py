import uvicorn
from fastapi import FastAPI

from router import router as router_service

app = FastAPI()

app.include_router(router_service)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
