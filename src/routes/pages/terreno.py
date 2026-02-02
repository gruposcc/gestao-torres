import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import ValidationError

from core.schema import validate_html_form
from core.settings import TEMPLATES
from core.utils.htmx import is_htmx_request
from deps.auth import get_user_session
from deps.db import get_db
from schemas.terreno import TerrenoIn
from services.terreno import TerrenoService

logger = logging.getLogger("app.pages.terreno")

router = APIRouter(prefix="/terreno")


@router.get("/")
async def list_page(
    request: Request,
    session=Depends(get_user_session),
    dbSession=Depends(get_db),
):
    template = "pages/terreno/list.html"
    page = {"title": "Terrenos"}

    context = {"request": request, "user": session, "page": page}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")

    return TEMPLATES.TemplateResponse(template, context)


@router.get("/create")
async def create(request: Request, session=Depends(get_user_session)):
    template = "pages/terreno/create.html"
    page = {"title": "Novo Terreno"}
    context = {"request": request, "user": session, "page": page}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")

    return TEMPLATES.TemplateResponse(template, context)


@router.post("/create")
async def post_create(
    request: Request,
    user_session=Depends(get_user_session),
    db_session=Depends(get_db),
):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    data = await request.form()

    context: Dict[str, Any] = {"request": request}
    errors: Dict[str, Any] = {}

    template = "pages/terreno/create.html"

    logger.debug(data)

    try:
        valid_data = TerrenoIn.model_validate(data)
    except ValidationError as ve:
        for error in ve.errors():
            # logger.debug(error)
            field_name = str(error["loc"][0])
            errors[field_name] = f"Erro no campo: {error['msg']}"
        context.update(errors)

    # TODO
    if errors:
        return HTTPException(500, errors)
        ...
        # retorna o html do form com os erros

    ## cria o terreno
    service = TerrenoService(db_session)

    # tenta garantir unicidade
    exists = await service.exists_name(name=valid_data.name)
    if exists:
        context.update(
            {
                "name": {"value": valid_data.name, "error": "Nome em uso"},
                "lat": {"value": valid_data.lat},
                "lng": {"value": valid_data.lng},
                # "address": {"value": valid_data.address},
            }
        )
        # RETORNA O BLOCK DO FORM COM OS ERROS E VALORES NO CONTEXTO
        return TEMPLATES.TemplateResponse(template, context, block_name="form")

    # SE UNICO CRIA NOVO
    try:
        new_terreno = await service.create(valid_data)

        # await notifier.push bla bla
        # prepara o redirecionamento
        response = Response(status_code=200)
        response.headers["HX-location"] = json.dumps(
            {
                "path": f"/terreno/view/{new_terreno.id}",
                "target": "#content",
                "swap": "innerHTML",
            }
        )

        return response

    except Exception as e:
        logger.warning(e)
        raise HTTPException(500, "Erro Criando o objeto")


@router.get("/view/{terreno_id}")
async def view_terreno(terreno_id: int, request: Request):
    response = Response(status_code=200, content=f"{terreno_id}")
    return response
