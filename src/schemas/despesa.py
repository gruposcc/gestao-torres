from decimal import Decimal
import uuid
from datetime import date
from pydantic import field_validator
from core.schema import BaseSchema, ModelSchema
from models.torre import RecorrenciaDespesa


class DespesaTorreIn(BaseSchema):
    name: str
    valor: Decimal
    recorrencia: RecorrenciaDespesa
    description: str | None = None
    data_inicio: date
    data_final: date | None = None
    torre_id: uuid.UUID
    valor_total: Decimal

    """ @field_validator("data_final")
    @classmethod
    def verificar_datas(cls, v, info):
        if info.data["data_final"] is not None:
            if "data_inicio" in info.data and v < info.data["data_inicio"]:
                raise ValueError("A data final não pode ser anterior à data inicial")
            return v
        else:
            return v """
