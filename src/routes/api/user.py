import logging

from fastapi import APIRouter, Depends, HTTPException

from deps.db import get_db
from schemas.user import UserIn, UserOut
from services.user import UserService

logger = logging.getLogger("app.api.user")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user", tags=["users"])


@router.post("/create", response_model=UserOut)
async def create_user(data: UserIn, dbSession=Depends(get_db)):
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


@router.post("/list")
async def list(): ...
