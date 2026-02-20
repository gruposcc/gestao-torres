import uuid
import logging
from decimal import Decimal
from typing import Dict

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
)
from models.torre import RecorrenciaDespesa
from pydantic import ValidationError
from datetime import date
from core.templates import render_chunk, render_page
from core.utils.htmx import is_htmx_request, redirect_htmx_header
from deps.auth import get_user_session
from deps.db import get_db
from schemas.despesa import DespesaTorreIn
from services.torre import TorreService, DespesaTorreSerivce


logger = logging.getLogger("app.pages.despesa")

router = APIRouter(prefix="/despesa")


@router.get("/torre/{torre_id}/create")
async def get_create_despesa_torre(
    request: Request,
    torre_id: uuid.UUID,
    user=Depends(get_user_session),
    db=Depends(get_db),
    error_context: Dict | None = None,
):
    template = "pages/despesa/create-despesa-torre.html"

    torre = None
    if not error_context:
        torre_service = TorreService(db)
        torre = await torre_service.get_one_by(id=torre_id)

        if not torre:
            raise HTTPException(404)

    page = {"title": "Torres SCC - Despesa Torre "}
    context = {
        "user": user,
        "page": page,
        "torre": torre,
        "recorrencias": list[RecorrenciaDespesa](RecorrenciaDespesa),
    }

    if error_context:
        context.update(error_context)

    return render_page(request, template, context)


@router.post("/torre/{torre_id}/create")
async def post_create_despesa_torre(
    request: Request,
    torre_id: uuid.UUID,
    user=Depends(get_user_session),
    db=Depends(get_db),
    # FORM
    name: str = Form(...),
    valor: Decimal = Form(...),
    recorrencia: str = Form(...),
    data_inicio: date = Form(...),
    data_final: str = Form(None),
    valor_total_calculado: Decimal = Form(...),
    description: str = Form(None),
):
    try:
        dt_final = None
        if data_final and data_final.strip():
            try:
                dt_final = date.fromisoformat(data_final)
            except ValueError:
                # Caso o usuário digite algo inválido manualmente
                raise HTTPException(status_code=400, detail="Data final inválida")

        # logger.error(valor_total_calculado)

        data = {
            "name": name,
            "valor": valor,
            "recorrencia": recorrencia,
            "data_inicio": data_inicio,
            "data_final": dt_final,
            "description": description,
            "torre_id": torre_id,
            "valor_total": valor_total_calculado,
        }

        valid_data = DespesaTorreIn.model_validate(data)

    except ValidationError as ve:
        # TODO
        logger.warning(ve)

    torre_service = TorreService(db)

    torre = await torre_service.get_one_by(id=torre_id)
    if not torre:
        raise HTTPException(404)

    despesa_service = DespesaTorreSerivce(db)
    exists = await despesa_service.get_one_by(name=valid_data.name, torre_id=torre.id)

    if exists:
        error_context = {
            "torre": torre,
            "form": {
                "name": {"value": valid_data.name, "error": "Nome em uso"},
                "valor": {"value": valid_data.valor},
                "recorrencia": {"value": valid_data.recorrencia.value},
                "recorrencia_text": {"value": valid_data.recorrencia.value},
                "data_inicio": {"value": valid_data.data_inicio},
                "data_final": {"value": valid_data.data_final},
                "description": {"value": valid_data.description},
                # OUTROS CAMPOS
            },
        }
        return await get_create_despesa_torre(
            request,
            torre_id,
            user=user,
            error_context=error_context,
        )

    try:
        new_despesa = await despesa_service.create(valid_data)

    except Exception as e:
        logger.warning(e)
        raise HTTPException(500, "erro criando a despesa")

    response = Response(status_code=200)
    # TODO MENSAGEM ?

    initial_subpage_header = {"X-Initial-Subpage": "despesas"}

    return redirect_htmx_header(
        response, path=f"/torre/view/{torre_id}", extra_headers=initial_subpage_header
    )


@router.delete("/torre/{despesa_id}")
async def delete_torre_despesa(request: Request, despesa_id: int, db=Depends(get_db)):
    service = DespesaTorreSerivce(db)

    despesa = await service.get_one_by(id=despesa_id)
    if not despesa:
        raise HTTPException(404)

    await service.hard_delete(despesa)

    torre_id = despesa.torre_id
    torre_service = TorreService(db)

    torre = await torre_service.get_one_by(id=torre_id, load_relations=["despesas"])
    if not torre:
        raise HTTPException(404)

    template = "pages/torre/subpage/despesas.html"
    context = {
        "items": torre.despesas,
        "torre_id": torre.id,
        "current_tab": "despesas",
        # "initial_subpage": "despesas",
    }

    return render_chunk(request, template, context)
