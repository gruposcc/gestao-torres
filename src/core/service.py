import logging
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar

from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload
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

    async def get_one_by(
        self, only_enabled=True, load_relations: list | None = None, **kwargs
    ) -> Optional[T]:
        stmt = select(self.model)

        if load_relations:
            for rel in load_relations:
                # VERIFICAR SE EXISTE A REFERENCIA
                # ex: Torre.terreno
                if hasattr(self.model, rel):
                    attr = getattr(self.model, rel)
                    stmt = stmt.options(selectinload(attr))

                else:
                    pass

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                column = getattr(self.model, key)
                stmt = stmt.where(column == value)
            else:  # se nao existe so passa
                logger.warning(
                    f"Buscando coluna que nao existe no modelo: {self.model.__name__}, {key}"
                )
                pass

        # se status nao foi passado no filtro, filtra por status == enabled
        if hasattr(self.model, "status") and "status" not in kwargs and only_enabled:
            stmt = stmt.where(getattr(self.model, "status") == ObjectStatus.ENABLE)

        logger.debug(f"Buscando {self.model.__name__} unico por: {stmt}")

        result = await self.dbSession.execute(stmt)
        instance = result.scalar_one_or_none()

        return instance

    async def create(self, data: BaseSchema, *args, **kwargs):
        payload = data.model_dump()

        await self.before_create(payload, *args, **kwargs)

        object = await self.save(self.model(**payload))

        # TRATAR EXECÇÔES DO self.save

        return object

    async def before_create(self, payload: Dict[str, Any], *args, **kwargs):
        """SOBREESCREVER O METODO QUE RECEBE O PAYLOAD E É CHAMADO ANTES DE SALVAR A INSTANCIA CRIADA NO DB"""
        pass

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

    async def get_list(self):
        raise NotImplementedError

    async def exists_by(self, **kwargs):
        stmt = select(exists(self.model))  # inicializa query do modelo
        for key, value in kwargs.items():
            # analiza o kwargs pra ver se o model tem uma propriedade que pode ser filtrada
            if hasattr(self.model, key):
                column = getattr(self.model, key)
                # adiciona cada um dos kwargs analisados ao stmt
                stmt = stmt.where(column == value)
            else:  # se nao existe so passa
                logger.warning(
                    f"Buscando coluna que nao existe no modelo: {self.model.__name__}, {key}"
                )
                pass

        stmt.exists()

        raw_result = await self.dbSession.execute(stmt)
        result = raw_result.scalar()

        self.logger.debug(result)
        return result

    async def soft_delete(self, obj: T) -> bool:
        # Verifica se o objeto suporta soft delete
        if not hasattr(obj, "status"):
            return False

        # Altera o status
        obj.status = ObjectStatus.DELETED  # pyright: ignore[reportAttributeAccessIssue]

        # Se você tiver um campo de timestamp, preencha-o
        """ if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now() """

        # Salva a alteração (commit)
        instance = await self.save(obj)
        return True
