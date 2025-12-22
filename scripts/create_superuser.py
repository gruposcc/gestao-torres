import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import sessionmanager
from models.user import User
from schemas.user import UserIn
from services.user import UserService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db():
    async for session in sessionmanager.get_session():
        yield session


async def create_superuser(data: UserIn, dbSession: AsyncSession) -> User:
    service = UserService(dbSession)

    try:
        exists, user = await service.get_or_create(data)
    except Exception as e:
        logger.exception("Erro ao tentar criar superusuário: %s", e)
        raise RuntimeError(f"Falha no serviço ao criar usuário: {e}")

    if not exists:
        return user
    else:
        raise ValueError("Usuário já existe.")


async def main():
    logger.info("Iniciando script de criação de Superusuário...")

    superuser_data = UserIn.model_validate(
        {
            "email": "admin@root.com",
            "password": "securepass",
            "first_name": "super",
            "last_name": "admin",
        }
    )

    try:
        async with get_db() as session:
            logger.info("Sessão de banco de dados obtida com sucesso.")

            new_user = await create_superuser(superuser_data, session)

            logger.info("✅ Superusuário '%s' criado com sucesso!", new_user.email)
            logger.info("ID: %s | Email: %s", new_user.id, new_user.email)

    except ValueError as e:
        # Tratamento do 'Usuário já existe' (409)
        logger.warning("⚠️ Operação cancelada: %s", e)
    except RuntimeError as e:
        # Tratamento de erros de DB (503) ou Serviço (500)
        logger.error("❌ Erro fatal durante a execução: %s", e)
    except Exception as e:
        logger.exception("❌ Erro inesperado no script principal: %s", e)


if __name__ == "__main__":
    sessionmanager.init_db()
    asyncio.run(main())
