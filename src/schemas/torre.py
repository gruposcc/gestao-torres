from decimal import Decimal
import uuid
from pydantic import Field

from core.schema import BaseSchema, ModelSchema
from models.torre import TipoTorre


class TorreIn(BaseSchema):
    name: str
    tipo: TipoTorre
    """ altura: Decimal = Field(
        gt=0, max_digits=6, decimal_places=2, description="Altura em metros"
    ) """
    altura: int
    terreno_id: int


class DocumentoTorreIn(BaseSchema):
    filename: str
    nickname: str
    torre_id: uuid.UUID
    path: str
    content_type: str | None = None
