import logging

from fastapi import Depends, HTTPException, Security

from core.database import get_db_session
from core.security import access_cookie, decode_token
from schemas.auth import UserSession
from services.user import UserService

logger = logging.getLogger("app.deps.auth")


async def get_current_user(
    cookie_token=Security(access_cookie), dbSession=Depends(get_db_session)
):
    try:
        token_payload = decode_token(cookie_token)
    except Exception as e:
        logger.exception(f"Erro decodificando token: {e}")
        raise HTTPException(401, "Token inválido")

    user_service = UserService(dbSession)
    user = await user_service.get_one_by(id=token_payload.sub)
    if not user:
        raise HTTPException(401)

    dict_payload = token_payload.model_dump()

    user_session = UserSession.model_validate(
        (user, {"permissions": dict_payload.get("permissions", [])})
    )
    return user_session
