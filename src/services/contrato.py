from core.service import AbstractModelService
from models.contrato import Contrato
from sqlalchemy import select
from models.base import ObjectStatus


class ContratoService(AbstractModelService[Contrato]):
    model = Contrato

    """ async def search_by_name(self, name: str, limit: int = 3):
        # Se o nome estiver vazio, podemos retornar os mais recentes
        if not name or len(name.strip()) == 0:
            stmt = select(self.model).order_by(self.model.created_at.desc())
        else:
            # O .contains() gera automaticamente o '%termo%'
            stmt = select(self.model).filter(self.model.name.ilike(f"%{name}%"))

        stmt = stmt.filter(self.model.status == ObjectStatus.ENABLE).limit(limit)

        # self.logger.debug(f"SEARCH BY: {stmt}")
        result = await self.dbSession.execute(stmt)
        return result.scalars().all()
 """
