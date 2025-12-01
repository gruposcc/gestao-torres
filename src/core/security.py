from logging import getLogger

import jwt
from fastapi import HTTPException
from fastapi.security import APIKeyCookie
from passlib.context import CryptContext

from core.settings import (
    JWT_ALGORITHM,
    JWT_SECRET,
)
from schemas.auth import AccessTokenPayload, RefreshTokenPayload, TokenBase

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

access_cookie = APIKeyCookie(
    name="access-token", auto_error=False, scheme_name="SessionCookie"
)
refresh_cookie = APIKeyCookie(
    name="refresh-token", scheme_name="RefreshCookie", auto_error=False
)


LOGGER = getLogger("app.security")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encode_token(payload: TokenBase):
    return jwt.encode(payload.model_dump(exclude_none=True), JWT_SECRET, JWT_ALGORITHM)


def decode_token(token: str) -> TokenBase:
    decoded = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)

    if decoded["type"] == "refresh":
        payload = RefreshTokenPayload.model_validate(decoded)

    if decoded["type"] == "access":
        payload = AccessTokenPayload.model_validate(decoded)

    return payload
