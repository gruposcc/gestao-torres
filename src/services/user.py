from typing import List, Optional, Tuple

from sqlalchemy import Sequence, exists, select

from core.schema import ModelSchema
from core.security import hash_password
from core.service import AbstractModelService
from models.base import ObjectStatus
from models.user import User
from schemas.user import UserIn


class UserService(AbstractModelService[User]):
    model = User

    async def get_or_create(self, data: UserIn) -> Tuple[bool, User]:
        exists: bool

        user = await self.get_one_by(email=data.email)

        if user:
            exists = True
            return exists, user

        exists = False
        new_user = await self.create(data)
        return exists, new_user

    async def create(self, data: UserIn) -> User:
        payload = data.model_dump()
        raw_pass = payload.pop("password")
        hashed_pass = hash_password(raw_pass)
        payload["password"] = hashed_pass
        new_user = await self.save(User(**payload))
        # validar IntegrityError
        return new_user

    async def get_all(self, response_schema=None):
        stmt = select(self.model).where(self.model.status == ObjectStatus.ENABLE)
        result = await self.dbSession.execute(stmt)

        users = result.scalars().all()
        if not response_schema:
            return users

        serialized: List[ModelSchema] = [
            response_schema.model_validate(user) for user in users
        ]

        return serialized

    async def exists_by_username(self, username: str):
        stmt = select(User.id).where(User.email == username)

        # 2. Executa o EXISTS() sobre o statement.
        exists_stmt = select(exists(stmt))

        # 3. Executa a query na sessão assíncrona e retorna o resultado.
        #    .scalar_one() pega o resultado único do SELECT EXISTS (que é um booleano).
        #    O resultado é um booleano nativo (True ou False).
        result = await self.dbSession.execute(exists_stmt)

        # Retorna o valor booleano (True ou False)
        return result.scalar_one()

    async def email_exists(self, email: str):
        stmt = select(self.model).where(User.email == email)
        result = await self.dbSession.execute(stmt)
        return result.scalar() is not None
