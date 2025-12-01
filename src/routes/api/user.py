import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request

from core.database import get_db_session
from core.settings import TEMPLATES
from schemas.auth import UserAuthForm
from schemas.user import UserIn, UserOut
from services.user import UserService

logger = logging.getLogger("app.api.user")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user", tags=["users"])


@router.post("/create", response_model=UserOut)
async def create_user(data: UserIn, dbSession=Depends(get_db_session)):
    service = UserService(dbSession)
    try:
        exists, user = await service.get_or_create(data)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500)

    if not exists:
        return user
    else:
        raise HTTPException(409, "Usuário já existe")
