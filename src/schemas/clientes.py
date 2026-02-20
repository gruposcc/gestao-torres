from core.schema import BaseSchema, ModelSchema
from models.clientes import Cliente, ClientePF, ClientePJ, TipoCliente
from pydantic import field_validator
import re


class ClienteInBase(BaseSchema):
    tipo: TipoCliente
    name: str


class ClientePFIn(ClienteInBase):
    tipo: TipoCliente = TipoCliente.PF
    last_name: str
    cpf: str

    @field_validator("cpf")
    @classmethod
    def clean_cpf(cls, v):
        return re.sub(r"\D", "", v)  # Remove tudo que não é dígito


class ClientePJIn(ClienteInBase):
    tipo: TipoCliente = TipoCliente.PJ
    cnpj: str

    @field_validator("cnpj")
    @classmethod
    def clean_cnpj(cls, v):
        return re.sub(r"\D", "", v)


ClienteIn = ClientePJIn | ClientePFIn
