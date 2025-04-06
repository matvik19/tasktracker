import subprocess

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routers import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # subprocess.run("alembic upgrade head", shell=True, check=True)
    yield


app = FastAPI(
    title="Duplication contact widget",
    description="Microservice for handling contact duplication",
    version="1.0.0",
    lifespan=lifespan,
)
api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Page not found"}},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

for router in all_routers:
    api.include_router(router)

app.include_router(api)
