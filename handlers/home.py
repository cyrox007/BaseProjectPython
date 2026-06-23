from typing import Annotated

from fastapi import APIRouter, Query, Depends

from core.security import get_current_user
from schemas.test.test import TestRequest, TestResponse


routers = APIRouter(prefix='/api/v2')

@routers.get('/', 
            name="Тестовый", 
            description="TestHome", 
            response_model=TestResponse)
async def home(data: Annotated[TestRequest, Query()], current_user = Depends(get_current_user)):
    return {
        'uuid': data.uuid,
        'name': 'John',
        'age': 20
    }

@routers.post('/', 
            name="Тестовый2", 
            description="TestHome2", 
            response_model=TestResponse)
async def home(data: TestRequest, current_user = Depends(get_current_user)):
    return {
        'uuid': data.uuid,
        'name': 'John',
        'age': 20
    }