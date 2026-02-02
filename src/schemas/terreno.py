from core.schema import BaseSchema, ModelSchema


class TerrenoIn(BaseSchema):
    lat: float
    lng: float

    # is_alugado: bool
    # valor_aluguel: float = 0
    # address: str
    name: str

    # validate name, garante que nao é´uma string
