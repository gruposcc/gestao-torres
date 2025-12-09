from uuid import UUID

from pydantic import EmailStr, Field

from core.schema import BaseSchema, ModelSchema


class UserIn(BaseSchema):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    email: EmailStr = Field(
        ...,
    )

    first_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


class JsonUserIn(UserIn): ...


class UserOut(ModelSchema):
    id: UUID
    email: str
    name: str
    first_name: str
    last_name: str
    # groups


class UserSession(UserOut):
    permissions: list[str]
