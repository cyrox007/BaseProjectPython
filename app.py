from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette_compress import CompressMiddleware
from asgi_compression import CompressionMiddleware
from asgi_compression import BrotliAlgorithm, GzipAlgorithm

from core.logger import setup_logger
from core.redis import redis_client

from handlers.auth_handler import routers as auth_routers
from handlers.home_handler import routers as home_routers
from handlers.permission_handler import routers as permission_routers
from handlers.role_handler import routers as roles_routers
from handlers.role_permission_handler import routers as role_perm_routers
from handlers.users_handler import routers as users_routers
from handlers.user_role_handler import routers as user_role_routers

from settings import config

logger = setup_logger(__name__)

ALLOWED_ORIGINS = config.get_allowed_origins
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE"]
STATIC_DIRECTORIES = {
    "static": "/static",
    "uploads": "/uploads"
}


def _setup_cors(app: FastAPI):
    """Настройка CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=ALLOWED_METHODS,
        allow_headers=["*"],
    )

def _setup_staticfiles(app: FastAPI):
    """Подключение статических файлов."""
    for dir_name, mount_path in STATIC_DIRECTORIES.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        app.mount(mount_path, StaticFiles(directory=dir_name), name=dir_name)

def _register_routers(app: FastAPI) -> None:
    routers = [
        auth_routers,
        home_routers,
        permission_routers,
        roles_routers,
        role_perm_routers,
        users_routers,
        user_role_routers
    ]

    for router in routers:
        app.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    # Запуск
    await redis_client.connect()
    logger.info("Redis инициализирован")
    
    yield
    
    # Остановка
    await redis_client.close()
    logger.info("Redis отключён")

def create_app() -> FastAPI:
    
    app = FastAPI(
        title=config.APPNAME,
        description=config.APPDESCRIPTION,
        version=config.APPVERSION,
        lifespan=lifespan
    )

    _setup_cors(app)
    app.add_middleware(
        CompressionMiddleware,
        algorithms=[
            BrotliAlgorithm(),
            GzipAlgorithm(),
        ],
        minimum_size=1000
    )
    _setup_staticfiles(app)
    _register_routers(app)
    
    return app

app = create_app()