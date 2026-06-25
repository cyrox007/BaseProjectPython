from fastapi import APIRouter


routers = APIRouter(prefix='/api/v1/users', tags=['Admin.Users'])

async def get_users():
    pass