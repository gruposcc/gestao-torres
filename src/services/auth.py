from datetime import datetime, timedelta, timezone
from logging import getLogger

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

logger = getLogger("app.services.auth")


class AuthService(AbstractBaseService):
    async def login(self, data: UserAuthForm):
        # logger.debug("auth service")
        user_service = UserService(self.dbSession)

        user = await user_service.get_one_by(email=data.email)

        if not user:
            error_message = {"email": "usuário não existe"}
            success = False
            # logger.warning("user nao existe")
            return success, error_message

        elif not verify_password(data.password, user.password):
            error_message = {"password": "Senha incorreta"}
            success = False
            # logger.warning("senha incorreta")
            return success, error_message

        # TEMPORARIO
        permissions = ["admin"]

        # logger.debug(f"logando {user.name}")

        now = datetime.now(timezone.utc)
        exp_access = int((now + timedelta(JWT_EXPIRE_MINUTES)).timestamp())
        exp_refresh = int((now + timedelta(JWT_EXPIRE_MINUTES_REFRESH)).timestamp())

        access_token = encode_token(
            AccessTokenPayload.model_validate(
                {"sub": user.id.hex, "exp": exp_access, "permissions": permissions}
            )
        )

        refresh_token = encode_token(
            RefreshTokenPayload.model_validate({"sub": user.id.hex, "exp": exp_refresh})
        )

        tokens = EncodedTokenPair.model_validate(
            {"access_token": access_token, "refresh_token": refresh_token}
        )

        logger.debug(f"returning {tokens}")
        return (True, tokens)
