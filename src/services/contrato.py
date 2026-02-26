from core.service import AbstractModelService
from models.contrato import Contrato, Altura
from sqlalchemy import select
from models.base import ObjectStatus


class ContratoService(AbstractModelService[Contrato]):
    model = Contrato

    async def create(self, contrato_in: ContratoIn, user_id: UUID) -> Contrato:
        alturas_data = contrato_in.alturas
        contrato_data = contrato_in.model_dump(exclude={'alturas'})

        new_contrato = self.model(**contrato_data, created_by=user_id)
        self.dbSession.add(new_contrato)
        await self.dbSession.flush() # Flush to get the new_contrato.id

        for altura_in_data in alturas_data:
            new_altura = Altura(**altura_in_data.model_dump(), contrato_id=new_contrato.id, created_by=user_id)
            self.dbSession.add(new_altura)
        
        await self.dbSession.commit()
        await self.dbSession.refresh(new_contrato)
        return new_contrato

