import asyncio
import logging
import sys
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import sessionmanager
from models.clientes import ClientePF, ClientePJ, TipoCliente
from models.terreno import Terreno
from models.torre import Torre, TipoTorre, DespesaTorre, RecorrenciaDespesa
from models.contrato import Contrato, Altura, RecorrenciaContrato, FaceDirecao
from core.service import AbstractModelService
from models.base import ObjectStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COORDS_SP = [
    (-23.5505, -46.6333),
    (-23.5612, -46.6565),
    (-23.5867, -46.6394),
    (-23.5733, -46.6150),
    (-23.6288, -46.7150),
    (-23.4813, -46.6700),
    (-23.4567, -46.5321),
    (-23.5321, -46.6477),
    (-23.5994, -46.5765),
    (-23.6167, -46.5667),
]

COORDS_RJ = [
    (-22.9068, -43.1729),
    (-22.9700, -43.3650),
    (-22.8163, -43.2499),
    (-22.9481, -43.4506),
    (-22.8908, -43.0977),
    (-22.8866, -43.2984),
    (-22.9938, -43.3688),
    (-22.9250, -43.2200),
    (-22.8343, -43.3412),
    (-22.8750, -43.1000),
]

FACE_DIRECOES = list(FaceDirecao)
TIPOS_TORRE = list(TipoTorre)
RECORRENCIAS_CONTRATO = list(RecorrenciaContrato)
RECORRENCIAS_DESPESA = list(RecorrenciaDespesa)


def generate_suffix() -> str:
    return uuid.uuid4().hex[:6]


def generate_cpf() -> str:
    return f"{random.randint(100000000, 999999999):011d}"


def generate_cnpj() -> str:
    return f"{random.randint(10000000, 99999999):08d}{random.randint(10, 99):02d}"


async def get_or_create_cliente(
    session: AsyncSession, tipo: TipoCliente, nome: str = None
):
    if tipo == TipoCliente.PF:
        cpf = generate_cpf()
        result = await session.execute(select(ClientePF).where(ClientePF.cpf == cpf))
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        cliente = ClientePF(
            name=nome or f"Pessoa {random.randint(1, 1000)}",
            last_name="Sobrenome",
            cpf=cpf,
            tipo=TipoCliente.PF,
            status=ObjectStatus.ENABLE,
        )
    else:
        cnpj = generate_cnpj()
        result = await session.execute(select(ClientePJ).where(ClientePJ.cnpj == cnpj))
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        cliente = ClientePJ(
            name=nome or f"Empresa {random.randint(1, 1000)}",
            cnpj=cnpj,
            tipo=TipoCliente.PJ,
            status=ObjectStatus.ENABLE,
        )
    session.add(cliente)
    await session.flush()
    return cliente


async def seed_clientes(session: AsyncSession) -> list:
    logger.info("Creating clientes...")
    clientes = []
    for i in range(10):
        tipo = TipoCliente.PF if i < 5 else TipoCliente.PJ
        cliente = await get_or_create_cliente(session, tipo)
        clientes.append(cliente)
    logger.info(f"Created {len(clientes)} clientes")
    return clientes


async def seed_terrenos(session: AsyncSession, count: int = 20) -> list[Terreno]:
    logger.info(f"Creating {count} terrenos...")
    terrenos = []
    for i in range(count):
        lat, lng = random.choice(COORDS_SP + COORDS_RJ)
        lat = Decimal(str(lat + random.uniform(-0.1, 0.1)))
        lng = Decimal(str(lng + random.uniform(-0.1, 0.1)))
        terreno = Terreno(
            name=f"Terreno {i + 1:02d}-{generate_suffix()}",
            lat=lat,
            lng=lng,
            status=ObjectStatus.ENABLE,
        )
        session.add(terreno)
        terrenos.append(terreno)
    await session.flush()
    logger.info(f"Created {len(terrenos)} terrenos")
    return terrenos


async def seed_torres(session: AsyncSession, terrenos: list[Terreno]) -> list[Torre]:
    logger.info("Creating torres...")
    torres = []
    for i, terreno in enumerate(terrenos):
        if i < 17:
            num_torres = 1
        else:
            num_torres = 3

        for j in range(num_torres):
            torre = Torre(
                name=f"Torre {i + 1:02d}-{j + 1}-{generate_suffix()}",
                terreno_id=terreno.id,
                altura=random.choice([30, 40, 45, 50, 60]),
                tipo=random.choice(TIPOS_TORRE),
                status=ObjectStatus.ENABLE,
            )
            session.add(torre)
            torres.append(torre)
    await session.flush()
    logger.info(f"Created {len(torres)} torres")
    return torres


async def seed_contratos(
    session: AsyncSession, torres: list[Torre], clientes: list
) -> list[Contrato]:
    logger.info("Creating contratos...")
    contratos = []

    for torre in torres:
        num_contratos = random.randint(5, 10)

        for j in range(num_contratos):
            cliente = random.choice(clientes)

            valor = Decimal(str(random.randint(1000, 50000)))
            data_inicial = datetime.now() - timedelta(days=random.randint(0, 365))
            data_final = data_inicial + timedelta(days=random.randint(180, 730))

            contrato = Contrato(
                name=f"Contrato {torre.name}-{j + 1}-{generate_suffix()}",
                valor=valor,
                data_inicial=data_inicial,
                data_final=data_final,
                recorrencia=random.choice(RECORRENCIAS_CONTRATO),
                torre_id=torre.id,
                cliente_id=cliente.id,
            )
            session.add(contrato)
            contratos.append(contrato)

    await session.flush()

    for contrato in contratos:
        num_alturas = random.randint(1, 3)
        for k in range(num_alturas):
            altura = Altura(
                metro_inicial=random.randint(10, 30),
                metro_final=random.randint(35, 60),
                face=random.choice(FACE_DIRECOES),
                contrato_id=contrato.id,
            )
            session.add(altura)

    await session.flush()
    logger.info(f"Created {len(contratos)} contratos")
    return contratos


async def seed_despesas(
    session: AsyncSession, torres: list[Torre]
) -> list[DespesaTorre]:
    logger.info("Creating despesas...")
    despesas = []

    for torre in torres:
        num_despesas = random.randint(2, 5)
        for j in range(num_despesas):
            despesa = DespesaTorre(
                name=f"Despesa {torre.name}-{j + 1}-{generate_suffix()}",
                torre_id=torre.id,
                valor=Decimal(str(random.randint(100, 5000))),
                valor_total=None,
                recorrencia=random.choice(RECORRENCIAS_DESPESA),
                perpetua=random.choice([True, False]),
                data_inicio=datetime.now() - timedelta(days=random.randint(0, 180)),
                data_final=datetime.now() + timedelta(days=random.randint(30, 365)),
                description=f"Descrição da despesa {j + 1}",
            )
            session.add(despesa)
            despesas.append(despesa)

    await session.flush()
    logger.info(f"Created {len(despesas)} despesas")
    return despesas


async def test_pagination(session: AsyncSession):
    logger.info("=" * 50)
    logger.info("TESTING PAGINATION")
    logger.info("=" * 50)

    models = [
        (Terreno, "Terreno"),
        (Torre, "Torre"),
        (Contrato, "Contrato"),
        (DespesaTorre, "DespesaTorre"),
    ]

    for model_class, model_name in models:
        logger.info(f"\n--- Testing {model_name} pagination ---")

        service = type(
            f"{model_name}Service", (AbstractModelService,), {"model": model_class}
        )(session)

        for page_size in [5, 10, 20]:
            items, total_pages, total_count = await service.get_list_paginated(
                page=1, page_size=page_size
            )
            logger.info(
                f"  page_size={page_size}: total_count={total_count}, total_pages={total_pages}, "
                f"items_in_page={len(items)}"
            )

        items_page1, total_pages, total_count = await service.get_list_paginated(
            page=1, page_size=5
        )
        items_page2, _, _ = await service.get_list_paginated(page=2, page_size=5)

        logger.info(f"  Page 1 IDs: {[str(i.id)[:8] for i in items_page1[:3]]}...")
        logger.info(f"  Page 2 IDs: {[str(i.id)[:8] for i in items_page2[:3]]}...")

        if items_page1 and items_page2:
            if items_page1[0].id == items_page2[0].id:
                logger.warning(f"  ⚠️  WARNING: Page 1 and Page 2 have same first item!")
            else:
                logger.info(f"  ✓ Page 1 and Page 2 are different")


async def seed_data():
    async for session in sessionmanager.get_session():
        clientes = await seed_clientes(session)
        terrenos = await seed_terrenos(session, count=20)
        torres = await seed_torres(session, terrenos)
        contratos = await seed_contratos(session, torres, clientes)
        despesas = await seed_despesas(session, torres)

        await session.commit()

        logger.info("=" * 50)
        logger.info("SEED SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Clientes: {len(clientes)}")
        logger.info(f"Terrenos: {len(terrenos)}")
        logger.info(f"Torres: {len(torres)}")
        logger.info(f"Contratos: {len(contratos)}")
        logger.info(f"Despesas: {len(despesas)}")

        await test_pagination(session)

        logger.info("✅ Seed completed successfully!")


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
