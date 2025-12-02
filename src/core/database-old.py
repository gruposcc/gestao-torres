# from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import DB_URL

logger = getLogger("app.database")

engine = create_async_engine(DB_URL, echo=False)
SessionLocal = async_sessionmaker[AsyncSession](
    engine, expire_on_commit=False, class_=AsyncSession
)


# asynccontextmanager
""" async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
 """


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    try:
        # A sessão é criada aqui, e é o ponto onde a conexão com o DB
        # será tentada ou usada a partir do pool.
        async with SessionLocal() as session:
            yield session

    except InvalidRequestError as ve:
        # ⚠️ CONCEITO CRUCIAL: OperationalError é a exceção do SQLAlchemy
        # que tipicamente engloba erros de conectividade de rede, como
        # ConnectionRefusedError ou Timeout, se ocorrerem ao tentar
        # pegar uma conexão do pool ou iniciar a sessão.

        # O retorno é um 503 Service Unavailable, o código padrão
        # para quando um serviço externo está temporariamente fora do ar.
        logger.debug(ve)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O Banco de Dados está indisponível. Por favor, tente novamente mais tarde.",
        )

    except:
        # Captura qualquer outra falha inesperada na sessão
        raise
