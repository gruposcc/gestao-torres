import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from core.settings import TEMPLATES
from deps.auth import get_current_user
from deps.db import get_db
from schemas.auth import UserAuthForm
from schemas.user import UserIn, UserOut
from services.user import UserService

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user")


@router.get("/")
async def list_page(
    request: Request, user=Depends(get_current_user), dbSession=Depends(get_db)
):
    template = "pages/user/list.html"
    page = {"title": "Usuários"}

    context = {"request": request, "user": user, "page": page}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")

    return TEMPLATES.TemplateResponse(template, context)


@router.post("/list")
async def list_post(request: Request, dbSession=Depends(get_db)):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    service = UserService(dbSession)
    users = await service.get_all(response_schema=UserOut)

    logger.debug(users)
    template = "pages/user/list.html"
    context = {"request": request, "users": users}

    return TEMPLATES.TemplateResponse(template, context, block_name="user_list")

    # retorna o framento do html


@router.get("/create")
async def create_page(request: Request, user=Depends(get_current_user)):
    template = "pages/user/create.html"
    page = {"title": "Novo usuário"}
    context = {"request": request, "user": user, "page": page}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")

    return TEMPLATES.TemplateResponse(template, context)


@router.post("/create")
async def create_post(
    request: Request,
    # form: Annotated[UserIn, Form()],
    user=Depends(get_current_user),
    dbSession=Depends(get_db),
):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    data = await request.form()

    context = {"request": request}
    errors = {}
    template = "user/create.html"

    try:
        v_form = UserIn.model_validate(data)
    except ValidationError as ve:
        for error in ve.errors():
            logger.debug(error)
            field_name = error["loc"][0]

            errors[field_name] = f"Erro no campo: {error['msg']}"
        v_form = None

    if errors:
        return TEMPLATES.TemplateResponse(template, context, block_name="content")
    if not v_form:
        raise

    service = UserService(dbSession)
    exists, user = await service.get_or_create(v_form)

    ...
    # validar manualmente
    # sanitizar
    # TODO extrair o metodo para tornar reutilizavel


@router.post("/create/validate-username")
async def validate_username(username: Optional[str] = None): ...
