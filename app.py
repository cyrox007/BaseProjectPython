from fastapi import FastAPI

from handlers.auth_handler import routers as auth_routers
from handlers.home_handler import routers as home_routers
from handlers.role_handler import routers as roles_routers
from handlers.permission_handler import routers as permission_routers

def _setup_cors(app: FastAPI):
    pass

def _setup_staticfiles(app: FastAPI):
    pass

def _register_routers(app: FastAPI) -> None:
    routers = [
        auth_routers,
        home_routers,
        permission_routers,
        roles_routers
    ]

    for router in routers:
        app.include_router(router)

def create_app() -> FastAPI:
    
    app = FastAPI(
        title="TestApp",
        description='Description app',
        version='1.0.0'
    )

    _setup_cors(app)
    _setup_staticfiles(app)
    _register_routers(app)
    
    return app

app = create_app()