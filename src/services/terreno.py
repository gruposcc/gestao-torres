from sqlalchemy import select

from core.service import AbstractModelService
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

    async def exists_name(self, name: str):
        stmt = select(self.model).where(Terreno.name == name)
        result = await self.dbSession.execute(stmt)
        return result.scalar() is not None
