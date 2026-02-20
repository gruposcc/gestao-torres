import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import ValidationError

from core.notifier import Notifier, get_notifier
from core.templates import TResponse, render_page
from core.utils.htmx import is_htmx_request
from deps.auth import get_user_session
from deps.db import get_db
from schemas.user import UserIn, UserOut
from services.user import UserService

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user")


@router.get("/")
async def list_page(
    request: Request,
    user=Depends(get_user_session),
    dbSession=Depends(get_db),
):
    template = "pages/user/list.html"
    page = {"title": "Usuários"}
    context = {"request": request, "user": user, "page": page}

    return render_page(request, template, context)


@router.post("/list")
async def list_post(request: Request, dbSession=Depends(get_db)):
    if not is_htmx_request:
        raise HTTPException(403)

    service = UserService(dbSession)
    users = await service.get_all(response_schema=UserOut)
    # logger.debug(users)

    template = "pages/user/list.html"
    context = {"request": request, "users": users}

    return TResponse(template, context, block_name="user_list")

    # retorna o framento do html


@router.get("/create")
async def create_page(request: Request, user=Depends(get_user_session)):
    template = "pages/user/create.html"
    page = {"title": "Novo usuário"}
    context = {"request": request, "user": user, "page": page}

    return render_page(request, template, context)


@router.post("/create")
async def create_post(
    request: Request,
    # form: Annotated[UserIn, Form()],
    user_session=Depends(
        get_user_session
    ),  # preciso estar autenticado para criar um user
    dbSession=Depends(get_db),
    notifier: Notifier = Depends(get_notifier),
):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    data = await request.form()

    context = {"request": request}
    errors = {}
    template = "pages/user/create.html"

    try:
        v_form = UserIn.model_validate(data)
    except ValidationError as ve:
        for error in ve.errors():
            logger.debug(error)
            field_name = error["loc"][0]

            errors[field_name] = f"Erro no campo: {error['msg']}"
        context.update(errors)
        # v_form = None

    if errors:
        return TResponse(template, context, block_name="form")

    service = UserService(dbSession)
    exists = await service.email_exists(v_form.email)
    if exists:
        context = {
            "request": request,
            "email": {"value": v_form.email, "error": "Email em uso"},
            "first_name": {"value": v_form.first_name},
            "last_name": {"value": v_form.last_name},
        }
        return TResponse(template, context, block_name="form")

    try:
        new_user = await service.create(v_form)

        # Dispara a notificação de sucesso ANTES do redirecionamento
        await notifier.push_to_user(
            user_session.id,
            level="success",
            title="Usuário Criado!",
            message=f"Bem-vindo, {new_user.first_name}! foi criado com sucesso.",
        )

        # Prepara o redirecionamento via HTMX
        response = Response(status_code=200)
        response.headers["HX-Location"] = json.dumps(
            {
                "path": "/user",
                "target": "#content",
                "swap": "innerHTML",
            }
        )
        return response

    except Exception as e:
        # Erro genérico na criação (ex: erro de DB)
        await notifier.push_to_user(
            user_session.id,
            level="danger",
            title="Erro Interno",
            message="Ocorreu um erro ao criar o usuário. Tente novamente mais tarde.",
        )
        logger.warning(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/create/validate-username")
async def validate_username(username: Optional[str] = None): ...
