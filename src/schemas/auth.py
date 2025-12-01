from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from core.schema import BaseSchema, ModelSchema


class TokenBase(BaseSchema):
    sub: str
    exp: int  # timestamp UNIX

    @field_validator("sub", mode="before")
    @classmethod
    def validate_sub_from_uuid(cls, v: Any) -> str:
        # Se o valor de entrada (v) for um objeto UUID,
        # transforma em string hexadecimal.
        if isinstance(v, UUID):
            return v.hex

        # Caso contrário (se for uma string, por exemplo),
        # o Pydantic continua o processo de validação normal para str.
        return v


class AccessTokenPayload(TokenBase):
    permissions: list[str] | None = None
    type: str = "access"


class RefreshTokenPayload(TokenBase):
    type: str = "refresh"


class EncodedTokenPair(BaseSchema):
    access_token: str
    refresh_token: str


class UserAuthForm(BaseSchema):
    username: str = Field(...)
    password: str = Field(...)
    # source: Literal["ldap"] | Literal["local"] = "local"


class UserSession(ModelSchema):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    # groups
    permissions: list[str]
