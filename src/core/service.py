import logging
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.schema import BaseSchema
from models.base import BaseSQLModel, ObjectStatus

logger = logging.getLogger("app.core.service")

T = TypeVar("T", bound=BaseSQLModel)


class AbstractBaseService:
    def __init__(self, dbSession: AsyncSession):
        self.dbSession = dbSession
        self.logger = logging.getLogger(
            f"app.service.{self.__class__.__name__.lower()}"
        )


class AbstractModelService(AbstractBaseService, Generic[T]):
    model: type[T]

    async def save(self, obj: T):
        try:
            self.dbSession.add(obj)
            await self.dbSession.commit()
            await self.dbSession.refresh(obj)
            return obj
        except Exception as e:
            raise e

    async def get_one_by(self, only_enabled=True, **kwargs) -> Optional[T]:
        conditions = []

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                conditions.append(getattr(self.model, key) == value)
            else:
                # se o filtro nao existe no modelo so passa
                self.logger.debug("Filtro não existe no modelo ...")
                ...

        # se status nao foi passado no filtro, filtra por status == enabled
        if hasattr(self.model, "status") and "status" not in kwargs and only_enabled:
            conditions.append(getattr(self.model, "status") == ObjectStatus.ENABLE)

        stmt = select(self.model).where(*conditions)
        logger.debug(f"Buscando: {stmt}")

        result = await self.dbSession.execute(stmt)
        instance = result.scalar_one_or_none()
        return instance

    async def create(self, data: BaseSchema, *args, **kwargs):
        raise NotImplementedError

    async def create_unique(
        self, keys: Dict[str, Any], data: BaseSchema
    ) -> Tuple[bool, T]:
        exists: bool

        obj = await self.get_one_by(kwargs=keys)

        if obj:
            exists = True
            return exists, obj

        exists = False
        new_obj = await self.create(data=data)
        return exists, new_obj
