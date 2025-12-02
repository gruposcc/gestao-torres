from logging import getLogger
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import sessionmanager

logger = getLogger("app.dep.db")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in sessionmanager.get_session():
        try:
            yield session

        except ConnectionRefusedError as cre:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="O Banco de Dados está indisponível ou inacessível. (Connection Refused)",
            ) from cre

        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from e
