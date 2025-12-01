from datetime import datetime, timedelta, timezone

from core.security import encode_token, verify_password
from core.service import AbstractBaseService
from core.settings import JWT_EXPIRE_MINUTES, JWT_EXPIRE_MINUTES_REFRESH
from schemas.auth import (
    AccessTokenPayload,
    EncodedTokenPair,
    RefreshTokenPayload,
    UserAuthForm,
)
from services.user import UserService


class AuthService(AbstractBaseService):
    async def login(self, data: UserAuthForm):
        user_service = UserService(self.dbSession)
        user = await user_service.get_one_by(username=data.username)
        if not user:
            return False, {"username": "Usuário não existe"}
        if not verify_password(data.password, user.password):
            return False, {"password": "Senha incorreta"}

        # TEMPORARIO
        permissions = ["admin"]

        now = datetime.now(timezone.utc)
        exp_access = int((now + timedelta(JWT_EXPIRE_MINUTES)).timestamp())

        access_token = encode_token(
            AccessTokenPayload.model_validate(
                {"sub": user.id, "exp": exp_access, "permissions": permissions}
            )
        )

        exp_refresh = int((now + timedelta(JWT_EXPIRE_MINUTES_REFRESH)).timestamp())
        refresh_token = encode_token(
            RefreshTokenPayload.model_validate({"sub": user.id, "exp": exp_refresh})
        )
        tokens = EncodedTokenPair.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

        return (True, tokens)
