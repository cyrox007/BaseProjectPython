from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Database
from core.logger import setup_logger


logger = setup_logger(__name__)

async def get_db_session() -> AsyncSession: # type: ignore
    """
    FastAPI dependency для получения сессии БД
    """
    db_session = await Database.get_session()
    try:
        yield db_session
        await db_session.commit()
    except Exception as e:
        logger.error(f"get_db_session() -> {e}")
        raise
    finally:
        await db_session.close()


async def get_client_info(request: Request) -> dict:
    """
    Получение информации о клиенте для логирования
    """
    return {
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "method": request.method,
        "path": request.url.path,
    }