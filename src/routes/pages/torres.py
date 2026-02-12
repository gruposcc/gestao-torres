import shutil
import uuid
import os
from core.settings import UPLOADS_DIR
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
from models.torre import TipoTorre
from pydantic import ValidationError

from core.schema import validate_html_form
from core.templates import render_chunk, render_page
from core.utils.htmx import is_htmx_request, redirect_htmx_header, update_htmx_title
from deps.auth import get_user_session
from deps.db import get_db
from schemas.torre import TorreIn
from services.torre import TorreService, DocumentoTorreService

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


@router.get("/list")
async def list_items(request: Request, db=Depends(get_db)):
    if not is_htmx_request:
        raise HTTPException(403)

    service = TorreService(db)

    # parametros de oordenação, filtro, etc etc
    torres = await service.get_list(load_relations=["terreno"])
    context = {"request": request, "items": torres}
    template = "pages/torre/list.html"

    return render_chunk(request, template, context, block="items")


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

    if len(extra_context.items()) > 0:  # Usado no retorno de erros do post
        context.update(extra_context)

    return render_page(request, template, context)


@router.post("/create")
async def post_create(
    request: Request,
    # FORM FIELDS
    name: str = Form(...),
    terreno_id: str = Form(...),
    tipotorre: str = Form(...),
    altura: Decimal = Form(...),
    searchQuery: str = Form(...),
    # ARQUIVOS
    # arquivos: List[UploadFile] = File(default=[]),
    # nomes_customizados: List[str] = Form(default=[]),
    # DEPS
    db=Depends(get_db),
):
    # PASSO 1 validar FORM -> SCHEMA
    try:
        data = {
            "name": name,
            "terreno_id": terreno_id,
            "tipo": tipotorre,
            "altura": altura,
        }

        valid_data = TorreIn.model_validate(data)

        # logger.debug(valid_data)

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
async def view(
    id: uuid.UUID,
    request: Request,
    dbSession=Depends(get_db),
    user=Depends(get_user_session),
):
    template = "pages/torre/view.html"

    context: Dict[str, Any] = {"request": request, "user": user}

    service = TorreService(dbSession)
    torre = await service.get_one_by(id=id, load_relations=["terreno", "documentos"])

    if not torre:
        raise HTTPException(404)

    page = {"title": f"Torres SCC - {torre.name}"}
    context.update({"item": torre, "page": page})

    return render_page(request, template, context)


@router.put("/{id}")
async def update(
    id: uuid.UUID,
    request: Request,
    name: str = Form(...),
    arquivos: List[UploadFile] = File(default=[]),
    nomes_customizados: List[str] = Form(default=[]),
    db=Depends(get_db),
):
    service = TorreService(db)
    # 1. Busca a torre existente com os documentos atuais
    torre = await service.get_one_by(id=id, load_relations=["documentos"])

    if not torre:
        raise HTTPException(404, "Torre não encontrada")

    # 2. Validar se o novo nome já existe em OUTRA torre
    if name != torre.name:
        exists = await service.get_one_by(name=name)
        if exists:
            # Aqui você retornaria o form com erro de "Nome em uso"
            return HTMLResponse(content="Nome já existe", status_code=422)
        torre.name = name

    # 3. Salvar alterações básicas
    await service.save(torre)

    # 4. Processar novos documentos, se houver
    if arquivos and any(a.filename for a in arquivos):
        await service.append_docs(
            torre=torre, arquivos=arquivos, nicknames=nomes_customizados
        )

    # 5. Resposta HTMX: Redireciona para a visualização
    # Ou você pode retornar a própria página de view renderizada
    response = Response(status_code=200)
    return redirect_htmx_header(response, path=f"/torre/view/{torre.id}")


@router.delete("/documento/{doc_id}")
async def delete_documento(doc_id: uuid.UUID, db=Depends(get_db)):
    service = DocumentoTorreService(db)
    # Buscamos o documento
    doc = await service.get_one_by(id=doc_id)
    if not doc:
        return Response(status_code=204)  # Já não existe

    # 1. Remover arquivo físico
    if os.path.exists(doc.path):
        os.remove(doc.path)

    # 2. Remover do banco
    await service.soft_delete(doc)

    # Retorna vazio para o HTMX remover o elemento do DOM (hx-swap="outerHTML")
    return Response(status_code=200)


@router.delete("/{id}")
async def soft_delete(id: int, request: Request, db=Depends(get_db)):
    service = TorreService(db)
    torre = await service.get_one_by(id=id)

    if not torre:
        response = Response(status_code=204)
    else:
        success = await service.soft_delete(torre)
    if success:
        # RETORNA VAZIO PARA O HTMX
        response = Response(status_code=200)
    return response
