import json
import logging
from decimal import Decimal
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.datastructures import UploadFile
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from core.schema import validate_html_form
from core.templates import render_page
from core.utils.htmx import is_htmx_request, redirect_htmx_header, update_htmx_title
from deps.auth import get_user_session
from deps.db import get_db
from models.torre import TipoTorre
from schemas.torre import TorreIn
from services.torre import TorreService

logger = logging.getLogger("app.pages.torre")

router = APIRouter(prefix="/torre")


@router.get("/")
async def list_page(
    request: Request,
    user=Depends(get_user_session),
):
    template = "pages/torre/list.html"
    page = {"title": "Torres SCC - Torres"}
    context = {
        "request": request,
        "user": user,
        "page": page,
    }

    return render_page(request, template, context)


@router.get("/create")
async def get_create(
    request: Request, user=Depends(get_user_session), extra_context={}
):
    template = "pages/torre/create.html"
    page = {"title": "Torres SCC - Nova Torre"}

    context: Dict[str, Any] = {
        "request": request,
        "user": user,
        "page": page,
        "tipos": list[TipoTorre](TipoTorre),
    }

    if len(extra_context.items()) > 0:
        context.update(extra_context)

    return render_page(request, template, context)


@router.post("/create")
async def create_torre(
    request: Request,
    # FORM FIELDS
    name: str = Form(...),
    terreno_id: str = Form(...),
    tipotorre: str = Form(...),
    altura: Decimal = Form(...),
    searchQuery: str = Form(...),
    # ARQUIVOS
    arquivos: List[UploadFile] = File(default=[]),
    nomes_customizados: List[str] = Form(default=[]),
    # DEPS
    db=Depends(get_db),
):
    # TODO HTMX VALIDATION

    # 3. Processar arquivos
    """
    for arquivo, custom_name in zip(arquivos, nomes_customizados):
        # content = await arquivo.read()
        logger.debug(f"Recebido: {custom_name}")
    """

    # PASSO 1 validar FORM -> SCHEMA
    try:
        data = {
            "name": name,
            "terreno_id": terreno_id,
            "tipo": tipotorre,
            "altura": altura,
        }

        valid_data = TorreIn.model_validate(data)

        logger.debug(valid_data)

    except (ValidationError, ValueError) as e:
        # TODO: Retornar o form com erros (HTMX swap o form)
        # Por enquanto, retornamos um erro simples
        logger.error(f"Erro de validação: {e}")
        return HTMLResponse(
            content=f"<div class='alert error'>Erro nos dados: {e}</div>",
            status_code=422,
        )

    service = TorreService(db)
    # CRIAR A TORRE

    # validar unicidade
    exists = await service.exists_by(name=valid_data.name)
    if exists:  # RETORNA A PAGINA DO FORMULÁRIO COM OS ERROS
        extra_context = {
            "form": {
                "name": {"value": valid_data.name, "error": "Nome em uso"},
                "terreno_id": {"value": valid_data.terreno_id},
                "terreno_text": {"value": searchQuery},
                "tipo": {"value": valid_data.tipo.value},
                "tipo_text": {"value": valid_data.tipo.value},
                "altura": {"value": valid_data.altura},
            },
        }
        return await get_create(request, extra_context=extra_context)

    try:
        new_torre = await service.create(valid_data)

    except Exception as e:
        logger.warning(e)
        raise HTTPException(500, "Erro Criando o objeto")

    response = Response(status_code=200)
    return redirect_htmx_header(response, path=f"/torre/view/{new_torre.id}")


@router.get("/view/{id}")
async def view(id: int, request: Request, dbSession=Depends(get_db)):
    template = "pages/torre/view.html"

    context: Dict[str, Any] = {"request": request}

    service = TorreService(dbSession)
    torre = await service.get_one_by(id=id)

    if not torre:
        raise HTTPException(404)

    page = {"title": f"Torres SCC - {torre.name}"}
    context.update({"item": torre, "page": page})

    return render_page(request, template, context)
