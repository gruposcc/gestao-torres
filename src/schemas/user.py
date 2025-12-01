from uuid import UUID

from pydantic import EmailStr, Field

from core.schema import BaseSchema, ModelSchema


class UserIn(BaseSchema):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="Identificador único. Aceita letras, números e _ . -",
        examples=["bernardo"],
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    email: EmailStr | None = Field(
        default=None,
    )


class JsonUserIn(UserIn): ...


class UserOut(ModelSchema):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    # groups


class UserSession(UserOut):
    permissions: list[str]
