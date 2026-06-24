from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.roles_model import Role


async def get_role_list(session: AsyncSession, limit: int = 10, offset: int = 0) -> List[Role]:
    stmt = select(Role)

    # делаем фильтры тут

    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)

    return result.scalars()