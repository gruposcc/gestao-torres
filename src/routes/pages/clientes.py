from fastapi import APIRouter, Request, Form, Depends, HTTPException, Response
from core.utils.htmx import redirect_htmx_header
from logging import getLogger
from deps.db import get_db
from services.clientes import ClienteService, ClientePJService, ClientePFService
from typing import Dict, Any
from core.templates import render_page, render, render_chunk
from deps.auth import get_user_session
from models.clientes import TipoCliente
from schemas.clientes import ClienteIn, ClientePFIn, ClientePJIn
from pydantic import TypeAdapter, ValidationError
import uuid

logger = getLogger("app.pages.clientes")
router = APIRouter(prefix="/cliente")


@router.post("/search")
async def search_cliente_by_name(
    request: Request, clienteSearch: str = Form(), db=Depends(get_db)
):
    template = "pages/cliente/search-results.html"
    context: Dict[str, Any] = {}

    service = ClienteService(db)
    clientes = await service.search_by_name(name=clienteSearch)

    if clientes:
        context.update({"results": clientes})

    return render(request, template, context)


@router.get("/list")
async def list_cliente(request: Request, user=Depends(get_user_session)):
    template = "pages/cliente/list-cliente.html"
    page = {"title": "Torres SCC - Clientes"}
    context = {"user": user, "page": page}

    return render_page(request, template, context)


@router.get("/list/items")
async def list_cliente_items(request: Request, db=Depends(get_db)):
    service = ClienteService(db)
    clientes = await service.get_list()

    context = {"items": clientes}
    template = "pages/cliente/list-cliente.html"

    return render_chunk(request, template, context, block="items")


@router.get("/create")
async def get_create_cliente(
    request: Request,
    # FORM
    # ...
    user=Depends(get_user_session),
    db=Depends(get_db),
    error_context: Dict | None = None,
):
    template = "pages/cliente/create-cliente.html"

    if not error_context:
        ...

    page = {"title": "Torres SCC - Novo Cliente"}
    context = {
        "user": user,
        "page": page,
        "tipo_cliente": list[TipoCliente](TipoCliente),
    }

    if error_context:
        context.update(error_context)

    return render_page(request, template, context)


@router.post("/create")
async def post_create_cliente(request: Request, db=Depends(get_db)):
    form_data = await request.form()
    logger.debug(form_data)

    """ [app.pages.clientes] -  FormData([('selecTipo', 'pj'),
                    ('tipo', 'pj'), ('name', 'ber'), ('last_name', ''),
                    ('cnpj', '12.31.123/1231-12')])


    [10:36:53] DEBUG    [app.pages.clientes] -  FormData([('selecTipo', 'pf'),
                    ('tipo', 'pf'), ('name', 'asdasd'), ('last_name',
                    'asdasdasd'), ('cpf', '123.123.123-12')])
           INFO     [uvicorn.access] -  127.0.0.1:36362 - "POST
    """

    exists = False

    try:
        valid_data: ClienteIn = TypeAdapter(ClienteIn).validate_python(form_data)
    except ValidationError as ve:
        logger.error(ve)
        raise HTTPException(500)

    error_context = {
        "form": {
            "name": {"value": valid_data.name},
            # "last_name": {"value": valid_data.last_name},
            "tipo": {"value": valid_data.tipo.value},
        }
    }

    cliente_service = ClienteService(db)
    exists_by_name = await cliente_service.exists_by(name=valid_data.name)

    if exists_by_name:
        error_context["form"]["name"].update({"error": "Nome em uso"})
        exists = True

    if isinstance(valid_data, ClientePFIn):
        service = ClientePFService(db)

        # exists_by_name = await service.exists_by(name=valid_data.name)
        exists_by_cpf = await service.exists_by(cpf=valid_data.cpf)

        ectx = {
            "last_name": {"value": valid_data.last_name},
            "documento": {"value": valid_data.cpf},
        }

        """ if exists_by_name:
            ectx["name"].update({"error": "Nome em uso"})
            exists = True """

        if exists_by_cpf:
            # ectx["documento"] = {"value": valid_data.cpf, "error": "Documento em uso"}
            ectx["documento"].update({"error": "Documento em uso"})
            exists = True

        if exists:
            error_context["form"].update(ectx)
            # logger.debug(error_context)

            return await get_create_cliente(request, error_context=error_context)

        try:
            new_cliente = await service.create(valid_data)
        except Exception as e:
            logger.warning(e)
            raise HTTPException(500, "Erro criando cliente")

    elif isinstance(valid_data, ClientePJIn):
        service = ClientePJService(db)

        # exists_by_name = await service.exists_by(name=valid_data.name)
        exists_by_cnpj = await service.exists_by(cnpj=valid_data.cnpj)

        ectx = {
            "documento": {"value": valid_data.cnpj},
        }

        if exists_by_cnpj:
            ectx["documento"].update({"error": "Documento em uso"})
            exists = True

        if exists:
            error_context["form"].update(ectx)
            return await get_create_cliente(request, error_context)

        try:
            new_cliente = await service.create(valid_data)
        except Exception as e:
            logger.warning(e)
            return HTTPException(500, "Erro criando cliente")
        # exists_by_cpf = await serivce.exists_by

    response = Response(status_code=200)
    return redirect_htmx_header(response, path=f"/cliente/view/{new_cliente.id}")


@router.get("/view/{cliente_id}")
async def view_cliente(
    cliente_id: uuid.UUID,
    request: Request,
    user=Depends(get_user_session),
    db=Depends(get_db),
):
    template = "pages/cliente/view-cliente.html"
    # initial_subpage

    context = {"user": user}

    service = ClienteService(db)

    cliente = await service.get_one_by(id=cliente_id)

    # ver o tipo para saber que cliente mostrar

    if not cliente:
        raise HTTPException(404)

    page = {"title": f"Torres SCC - {{cliente.name}}"}
    context.update({"item": cliente, "page": page})

    return render_page(request, template, context)
