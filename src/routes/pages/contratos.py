import uuid
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
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from models.torre import RecorrenciaDespesa
from pydantic import ValidationError
from datetime import date
from core.templates import render_chunk, render_page
from core.utils.htmx import is_htmx_request, redirect_htmx_header
from deps.auth import get_user_session
from deps.db import get_db
from schemas.despesa import DespesaTorreIn
from schemas.contrato import ContratoIn, AlturaContratoSchema
from services.torre import TorreService
from services.contrato import ContratoService
from models.contrato import RecorrenciaContrato, FaceDirecao
from core.settings import MAX_SIZE_MB

logger = logging.getLogger("app.pages.contratos")

router = APIRouter(prefix="/contrato")


@router.get("/torre/{torre_id}/create")
async def get_create_contrato_torre(
    request: Request,
    torre_id: uuid.UUID,
    user=Depends(get_user_session),
    db=Depends(get_db),
    error_context: Dict | None = None,
):
    template = "pages/contrato/create-contrato-torre.html"
    torre = None

    if not error_context:
        torre_service = TorreService(db)
        torre = await torre_service.get_one_by(id=torre_id)

        if not torre:
            raise HTTPException(404)

    page = {"title": "Torres SCC - Contrato Torre "}
    context = {
        "user": user,
        "page": page,
        "torre": torre,
        "recorrencias": list[RecorrenciaContrato](RecorrenciaContrato),
        "faces": list[FaceDirecao](FaceDirecao),
    }

    if error_context:
        context.update(error_context)

    return render_page(request, template, context)


@router.get("/create")
async def get_create(
    request: Request,
    user=Depends(get_user_session),
    db=Depends(get_db),
    error_context: Dict | None = None,
):
    template = "pages/contrato/create-contrato-torre.html"

    page = {"title": "Torres SCC - Contrato Torre "}
    context = {
        "user": user,
        "page": page,
        "recorrencias": list[RecorrenciaContrato](RecorrenciaContrato),
        "faces": list[FaceDirecao](FaceDirecao),
    }

    if error_context:
        context.update(error_context)

    return render_page(request, template, context)


@router.post("/create")
async def post_create_contrato(
    request: Request,
    name: str = Form(...),
    cliente_id: uuid.UUID = Form(...),
    valor: Decimal = Form(...),
    recorrencia: RecorrenciaContrato = Form(...),
    data_inicio: date = Form(...),
    data_final: date | None = Form(None),
    torre_id: uuid.UUID = Form(...),
    alturas: List[str] = Form(None, alias="alturas[]"),
    user=Depends(get_user_session),
    db=Depends(get_db),
):
    error_context = {}
    parsed_alturas: List[AlturaContratoSchema] = []

    if alturas:
        for altura_json_str in alturas:
            try:
                altura_dict = json.loads(altura_json_str)
                parsed_alturas.append(AlturaContratoSchema(**altura_dict))
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding altura JSON: {e}")
                error_context["errors"] = ["Erro ao processar dados de altura."]
                return await get_create_contrato_torre(
                    request, torre_id, user, db, error_context
                )
            except ValidationError as e:
                logger.error(f"Validation error for altura: {e.errors()}")
                error_context["errors"] = [
                    f"Erro de validação para altura: {e.errors()}"
                ]
                return await get_create_contrato_torre(
                    request, torre_id, user, db, error_context
                )

    if not parsed_alturas:
        error_context["errors"] = [
            "É necessário informar pelo menos uma altura para o contrato."
        ]
        return await get_create_contrato_torre(
            request, torre_id, user, db, error_context
        )

    contrato_service = ContratoService(db)

    try:
        contrato_in_data = {
            "name": name,
            "cliente_id": cliente_id,
            "valor": valor,
            "recorrencia": recorrencia,
            "data_inicio": data_inicio,
            "data_final": data_final,
            "torre_id": torre_id,
            "alturas": parsed_alturas,
        }

        # Using Pydantic for validation before passing to service
        contrato_create_schema = ContratoIn(**contrato_in_data)

        await contrato_service.create(contrato_create_schema, user.id)

    except ValidationError as e:
        logger.error(f"Validation error creating contrato: {e.errors()}")
        error_context["errors"] = [f"Erro de validação ao criar contrato: {e.errors()}"]
        return await get_create_contrato_torre(the c)
    except Exception as e:
        logger.error(f"Error creating contrato: {e}")
        error_context["errors"] = [f"Erro ao criar contrato: {e}"]
        return await get_create_contrato_torre(
            request, torre_id, user, db, error_context
        )

    # If it's an HTMX request, redirect to the list page
    if is_htmx_request(request):
        response = Response()
        # redirect para torre com o header de subpage contratos
        redirect_htmx_header(response, "/contrato/list")
        return response

    return RedirectResponse(
        url="/contrato/list", status_code=303
    )  # Redirect after successful creation


@router.get("/list")
async def list_contrato(request: Request, user=Depends(get_user_session)):
    template = "pages/contrato/list-contrato.html"
    page = {"title": "Torres SCC - Clientes"}
    context = {"user": user, "page": page}

    return render_page(request, template, context)


@router.get("/list/items")
async def list_cliente_items(request: Request, db=Depends(get_db)):
    service = ContratoService(db)
    contratos = await service.get_list()

    context = {"items": contratos}
    template = "pages/contrato/list-contrato.html"

    return render_chunk(request, template, context, block="items")
