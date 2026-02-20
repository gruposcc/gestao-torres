from core.service import AbstractModelService
from models.clientes import Cliente, ClientePF, ClientePJ
from core.schema import ModelSchema
from sqlalchemy.orm import with_polymorphic
from sqlalchemy import select
from models.base import ObjectStatus


class ClienteService(AbstractModelService[Cliente]):
    model = Cliente

    async def get_list(
        self,
        out_schema: ModelSchema | None = None,
        only_enabled=True,
        load_relations: list | None = None,
    ):
        entity = with_polymorphic(self.model, [ClientePF, ClientePJ])
        stmt = select(entity)
        return await super().get_list(out_schema, only_enabled, load_relations, stmt)

    async def search_by_name(self, name: str, limit: int = 3):
        # Se o nome estiver vazio, podemos retornar os mais recentes
        if not name or len(name.strip()) == 0:
            stmt = select(self.model).order_by(self.model.name.desc())
        else:
            # O .contains() gera automaticamente o '%termo%'
            stmt = select(self.model).filter(self.model.name.ilike(f"%{name}%"))

        stmt = stmt.filter(self.model.status == ObjectStatus.ENABLE).limit(limit)

        # self.logger.debug(f"SEARCH BY: {stmt}")
        result = await self.dbSession.execute(stmt)
        return result.scalars().all()


class ClientePFService(AbstractModelService[ClientePF]):
    model = ClientePF


class ClientePJService(AbstractModelService[ClientePJ]):
    model = ClientePJ
