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
from fastapi.responses import HTMLResponse
from models.torre import RecorrenciaDespesa
from pydantic import ValidationError
from datetime import date
from core.templates import render_chunk, render_page
from core.utils.htmx import is_htmx_request, redirect_htmx_header
from deps.auth import get_user_session
from deps.db import get_db
from schemas.despesa import DespesaTorreIn
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
