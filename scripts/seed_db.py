import asyncio
import logging
import sys
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import sessionmanager
from models.user import User
from models.clientes import ClientePF, ClientePJ, TipoCliente
from models.terreno import Terreno
from models.torre import Torre, TipoTorre, DespesaTorre, RecorrenciaDespesa
from models.contrato import Contrato, Altura, RecorrenciaContrato, FaceDirecao
from schemas.user import UserIn
from services.user import UserService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def get_or_create_superuser(session: AsyncSession):
    user_service = UserService(session)
    superuser_data = UserIn(
        email="admin@root.com",
        password="securepass",
        first_name="Super",
        last_name="Admin",
    )
    
    # Check if exists
    result = await session.execute(select(User).where(User.email == superuser_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.info("Creating superuser...")
        user = await user_service.create(superuser_data)
        logger.info(f"Superuser created: {user.email}")
    else:
        logger.info(f"Superuser already exists: {user.email}")
    return user

async def seed_data():
    async for session in sessionmanager.get_session():
        # 1. Superuser
        admin = await get_or_create_superuser(session)
        user_id = admin.id

        # 2. Clientes
        logger.info("Seeding Clientes...")
        c1 = ClientePF(
            name="João",
            last_name="Silva",
            cpf="12345678901",
            tipo=TipoCliente.PF
        )
        c2 = ClientePJ(
            name="Torre Telecom S.A.",
            cnpj="12345678000199",
            tipo=TipoCliente.PJ
        )
        session.add_all([c1, c2])
        await session.flush()

        # 3. Terrenos
        logger.info("Seeding Terrenos...")
        t1 = Terreno(
            name="Morro do Elefante",
            lat=Decimal("-22.7032"),
            lng=Decimal("-45.5847")
        )
        t2 = Terreno(
            name="Pico da Bandeira",
            lat=Decimal("-20.4344"),
            lng=Decimal("-41.7925")
        )
        session.add_all([t1, t2])
        await session.flush()

        # 4. Torres
        logger.info("Seeding Torres...")
        torre1 = Torre(
            name="Torre Alpha-01",
            terreno_id=t1.id,
            altura=45,
            tipo=TipoTorre.ESTAIADA
        )
        torre2 = Torre(
            name="Torre Beta-02",
            terreno_id=t2.id,
            altura=30,
            tipo=TipoTorre.AUTO_MISTA
        )
        session.add_all([torre1, torre2])
        await session.flush()

        # 5. Despesas
        logger.info("Seeding Despesas...")
        d1 = DespesaTorre(
            name="Manutenção Semestral",
            torre_id=torre1.id,
            valor=Decimal("1500.00"),
            recorrencia=RecorrenciaDespesa.ANUAL,
            data_inicio=datetime.now()
        )
        session.add(d1)

        # 6. Contratos e Alturas
        logger.info("Seeding Contratos...")
        contrato1 = Contrato(
            name="Contrato Telecom - Alpha",
            valor=Decimal("5000.00"),
            data_inicial=datetime.now(),
            data_final=datetime.now() + timedelta(days=365),
            recorrencia=RecorrenciaContrato.MENSAL,
            torre_id=torre1.id,
            cliente_id=c2.id
        )
        session.add(contrato1)
        await session.flush()

        a1 = Altura(
            metro_inicial=10,
            metro_final=20,
            face=FaceDirecao.NORTE,
            contrato_id=contrato1.id
        )
        a2 = Altura(
            metro_inicial=20,
            metro_final=30,
            face=FaceDirecao.SUL,
            contrato_id=contrato1.id
        )
        session.add_all([a1, a2])

        await session.commit()
        logger.info("Database seeded successfully! ✅")

async def main():
    sessionmanager.init_db()
    try:
        await seed_data()
    except Exception as e:
        logger.exception(f"Error seeding database: {e}")
    finally:
        await sessionmanager.close()

if __name__ == "__main__":
    asyncio.run(main())
