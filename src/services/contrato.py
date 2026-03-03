from uuid import UUID
from datetime import datetime
from core.service import AbstractModelService
from models.contrato import Contrato, Altura, FaceDirecao
from schemas.contrato import ContratoIn
from sqlalchemy import select
from models.base import ObjectStatus


class ContratoService(AbstractModelService[Contrato]):
    model = Contrato

    async def create(self, contrato_in: ContratoIn, user_id: UUID) -> Contrato:
        alturas_data = contrato_in.alturas
        contrato_data = contrato_in.model_dump(exclude={"alturas"})

        # Map schema fields to model fields
        if "data_inicio" in contrato_data:
            contrato_data["data_inicial"] = contrato_data.pop("data_inicio")

        # lidar com a data final

        new_contrato = self.model(**contrato_data)  # created_by=user_id

        self.dbSession.add(new_contrato)
        await self.dbSession.flush()  # Flush to get the new_contrato.id

        for altura_in_data in alturas_data:
            # Map schema fields to model fields for Altura
            altura_payload = altura_in_data.model_dump(exclude={"id", "face_nome"})
            altura_payload["face"] = FaceDirecao(altura_payload.pop("face"))
            altura_payload["metro_inicial"] = altura_payload.pop("metro_de")
            altura_payload["metro_final"] = altura_payload.pop("metro_ate")

            new_altura = Altura(
                **altura_payload,
                contrato_id=new_contrato.id,
            )
            self.dbSession.add(new_altura)

        await self.dbSession.commit()
        await self.dbSession.refresh(new_contrato)
        return new_contrato
