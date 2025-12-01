from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel): ...


class ModelSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
