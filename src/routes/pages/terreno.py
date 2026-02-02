import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from core.schema import validate_html_form
from core.settings import TEMPLATES
from deps.auth import get_user_session
from deps.db import get_db
from schemas.terreno import TerrenoIn

logger = logging.getLogger("app.pages.terreno")
# logger.level = logging.DEBUG


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

    context = {"request": request}
    errors = {}
    template = "pages/terreno/create.html"

    form_schema = TerrenoIn
    success, _ = validate_html_form(data, form_schema)

    if errors:  # se tiver erro retorna o form com o erro renderizado
        context.update(errors)
        return TEMPLATES.TemplateResponse(template, context, block_name="form")

    ## cria o terreno

    """ service = TerrenoService(db_session)
    exists = await service. """

    return HTTPException(300)


""" 
[ BACKEND]            DEBUG    [app.pages.terreno] -  FormData([('lat',                    
[ BACKEND]                     '-27.802639479776524'), ('lng', '-51.03149414062501'),      
[ BACKEND]                     ('isAlugado', 'true'), ('valorAluguel', '123'),             
[ BACKEND]                     ('selectedAddress', 'Anita Garibaldi, Região Geográfica     
[ BACKEND]                     Imediata de Lages, Região Geográfica Intermediária de Lages,
[ BACKEND]                     Santa Catarina, Região Sul, Brasil')])                 
"""
