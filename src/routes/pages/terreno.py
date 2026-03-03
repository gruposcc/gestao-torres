import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from pydantic import ValidationError

from core.templates import TResponse, render_chunk, render_page, render
from core.utils.htmx import is_htmx_request
from deps.auth import get_user_session
from deps.db import get_db
from schemas.terreno import TerrenoIn
from services.terreno import TerrenoService
from core.utils.htmx import redirect_htmx_header

logger = logging.getLogger("app.pages.terreno")

router = APIRouter(prefix="/terreno")


@router.get("/list")
async def list_terreno(
    request: Request,
    session=Depends(get_user_session),
):
    template = "pages/terreno/list-terreno.html"
    page = {"title": "Torres SCC - Terrenos"}
    context = {"user": session, "page": page}

    return render_page(request, template, context)


@router.get("/list/items")
async def list_items_terreno(request: Request, db=Depends(get_db)):
    if not is_htmx_request:
        raise HTTPException(403)

    service = TerrenoService(db)

    # TODO, parametros de ordenação, paginação e filtro
    terrenos = await service.get_list(load_relations=["torres"])
    template = "pages/terreno/list-terreno.html"
    context = {"request": request, "items": terrenos}

    return render_chunk(request, template, context, block="items")


@router.get("/create")
async def get_create_terreno(request: Request, session=Depends(get_user_session)):
    template = "pages/terreno/create-terreno.html"
    page = {"title": "Torres SCC - Novo Terreno"}
    context = {"request": request, "user": session, "page": page}

    return render_page(request, template, context)


@router.post("/create")
async def post_create_terreno(
    request: Request,
    db_session=Depends(get_db),
):
    if not is_htmx_request:
        raise HTTPException(403)

    template = "pages/terreno/create.html"
    context: Dict[str, Any] = {"request": request}
    errors: Dict[str, Any] = {}

    data = await request.form()
    # logger.debug(data)
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

    # tenta garantir unicidade por nome
    exists = await service.exists_by(name=valid_data.name)
    if exists:
        context.update(
            {
                "name": {"value": valid_data.name, "error": "Nome em uso"},
                "lat": {"value": valid_data.lat},
                "lng": {"value": valid_data.lng},
                # "address": {"value": valid_data.address},
            }
        )
        logger.debug("ja existe bobo")

        # RETORNA O BLOCK DO FORM COM OS ERROS E VALORES NO CONTEXTO
        return TResponse(template, context, block_name="form")

    # SE UNICO CRIA NOVO
    try:
        new_terreno = await service.create(valid_data)

        # await notifier.push bla bla
        # prepara o redirecionamento
        response = Response(status_code=200)

        return redirect_htmx_header(response, f"/terreno/view/{new_terreno.id}")

    except Exception as e:
        logger.warning(e)
        raise HTTPException(500, "Erro Criando o objeto")


@router.get("/view/{terreno_id}")
async def view_terreno(terreno_id: int, request: Request, dbSession=Depends(get_db)):
    template = "pages/terreno/view-terreno.html"
    context: Dict[str, Any] = {"request": request}

    initial_subpage = request.headers.get("X-Initial-Subpage", "mapa")
    context["initial_subpage"] = initial_subpage

    service = TerrenoService(dbSession)
    terreno = await service.get_one_by(id=terreno_id, load_relations=["torres"])

    context.update({"item": terreno})

    if not terreno:
        raise HTTPException(404)

    if is_htmx_request:
        response = TResponse(template, context, block_name="content")

    else:
        response = TResponse(template, context)

    return response


@router.post("/search")
async def search_terreno(
    request: Request,
    searchQuery: str = Form(),
    db_session=Depends(get_db),
):
    template = "pages/terreno/terreno-search-results.html"
    context = {}
    # logger.debug(searchQuery)

    # sanitizar a query

    service = TerrenoService(db_session)
    terrenos = await service.search_by_name(name=searchQuery)

    # logger.debug(terrenos)
    if terrenos:
        context.update({"results": terrenos})

    if not isinstance(terrenos, list):
        terrenos = [terrenos]

    return render(request, template, context)


### SUBPAGES


@router.get("/view/{terreno_id}/mapa")
async def subpage_mapa(terreno_id: int, request: Request, dbSession=Depends(get_db)):
    template = "pages/terreno/subpage/mapa.html"
    context: Dict[str, Any] = {}

    service = TerrenoService(dbSession)
    terreno = await service.get_one_by(id=terreno_id)

    if not terreno:
        raise HTTPException(404)

    context = {"item": terreno, "terreno_id": terreno_id, "current_tab": "mapa"}

    return render_chunk(request, template, context)


@router.get("/view/{terreno_id}/torres")
async def subpage_torres(terreno_id: int, request: Request, dbSession=Depends(get_db)):
    template = "pages/terreno/subpage/torres.html"
    context: Dict[str, Any] = {}

    service = TerrenoService(dbSession)
    terreno = await service.get_one_by(id=terreno_id, load_relations=["torres"])

    if not terreno:
        raise HTTPException(404)

    context = {"item": terreno, "terreno_id": terreno_id, "current_tab": "torres"}

    return render_chunk(request, template, context)


@router.get("/view/{terreno_id}/documentos")
async def subpage_documentos(
    terreno_id: int, request: Request, dbSession=Depends(get_db)
):
    template = "pages/terreno/subpage/documentos.html"
    context: Dict[str, Any] = {}

    service = TerrenoService(dbSession)
    terreno = await service.get_one_by(id=terreno_id)

    if not terreno:
        raise HTTPException(404)

    context = {"item": terreno, "terreno_id": terreno_id, "current_tab": "documentos"}

    return render_chunk(request, template, context)
