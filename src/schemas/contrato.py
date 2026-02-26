from uuid import UUID
from datetime import date
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator
from models.contrato import RecorrenciaContrato, FaceDirecao


class AlturaContratoSchema(BaseModel):
    id: Optional[int] = None # This seems to be a frontend ID, not a backend one
    metro_de: int
    metro_ate: int
    face: FaceDirecao
    face_nome: Optional[str] = None # This is likely for display, face enum is sufficient


class ContratoIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    cliente_id: UUID
    valor: Decimal = Field(..., gt=0)
    recorrencia: RecorrenciaContrato
    data_inicio: date
    data_final: Optional[date] = None
    torre_id: UUID
    alturas: List[AlturaContratoSchema] = Field(default_factory=list)

    @field_validator('data_final', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == '':
            return None
        return v
