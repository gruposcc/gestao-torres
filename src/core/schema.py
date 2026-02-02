from logging import getLogger
from typing import Dict, Literal, Tuple

from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.datastructures import FormData


class BaseSchema(BaseModel): ...


class ModelSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True)


logger = getLogger("app.schemas")


def validate_html_form[T: BaseSchema](
    data: FormData, schema: type[T]
) -> tuple[Literal[True], BaseSchema] | tuple[Literal[False], Dict[str, str]]:
    errors = {}
    try:
        validated_form = schema.model_validate(data)
        return True, validated_form

    except ValidationError as ve:
        # logger.error(ve)
        for error in ve.errors():
            logger.debug(error)
            field_name = error["loc"][0]

            errors[field_name] = f"Error no campo: {error['msg']}"
        return False, errors
