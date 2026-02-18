from sqlalchemy import select

from core.schema import ModelSchema
from core.service import AbstractModelService
from models.base import ObjectStatus
from models.terreno import Terreno
from schemas.terreno import TerrenoIn


class TerrenoService(AbstractModelService[Terreno]):
    model = Terreno

    async def create(self, data: TerrenoIn) -> Terreno:
        payload = data.model_dump()

        # name
        # lat
        # lng
        # addr?
        # TODO cidade, estado.

        new_terreno = await self.save(Terreno(**payload))
        return new_terreno

    """ async def exists_name(self, name: str):
        stmt = select(self.model).where(Terreno.name == name)
        result = await self.dbSession.execute(stmt)
        return result.scalar() is not None """

    """ async def get_list(self, out_schema: ModelSchema = None, only_enable=True):
        stmt = select(self.model)

        if only_enable:
            stmt.where(self.model.status == ObjectStatus.ENABLE)

        result = await self.dbSession.execute(stmt)

        items = result.scalars().all()

        if not out_schema:
            return items

        #
        # cogitar uso de type adapter
        else:
            parsed = [out_schema.model_validate(item) for item in items]
            return parsed """

    async def search_by_name(self, name: str, limit: int = 3):
        # Se o nome estiver vazio, podemos retornar os mais recentes
        if not name or len(name.strip()) == 0:
            stmt = select(self.model).order_by(self.model.created_at.desc())
        else:
            # O .contains() gera automaticamente o '%termo%'
            stmt = select(self.model).filter(self.model.name.ilike(f"%{name}%"))

        stmt = stmt.filter(self.model.status == ObjectStatus.ENABLE).limit(limit)

        self.logger.debug(f"SEARCH BY: {stmt}")
        result = await self.dbSession.execute(stmt)
        return result.scalars().all()
