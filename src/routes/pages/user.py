import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from core.settings import TEMPLATES
from deps.auth import get_current_user
from deps.db import get_db
from schemas.auth import UserAuthForm
from schemas.user import UserIn
from services.user import UserService

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user")


@router.get("/list")
async def home(request: Request, user=Depends(get_current_user)):
    page = {"title": "Usuários"}
    context = {"request": request, "user": user, "page": page}
    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(
            "user/list.html", context, block_name="content"
        )
    return TEMPLATES.TemplateResponse("user/list.html", context)


@router.get("/create")
async def create_page(request: Request, user=Depends(get_current_user)):
    template = "user/create.html"
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

        ...
        # validar manualmente
        # sanitizar
        # TODO extrair o metodo para tornar reutilizavel
