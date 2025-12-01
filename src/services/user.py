from typing import Tuple

from core.security import hash_password
from core.service import AbstractModelService
from models.user import User
from schemas.user import UserIn


class UserService(AbstractModelService[User]):
    model = User

    async def get_or_create(self, data: UserIn) -> Tuple[bool, User]:
        exists: bool

        user = await self.get_one_by(username=data.username)
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
        return new_user
