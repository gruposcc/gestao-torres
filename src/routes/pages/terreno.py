import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from core.settings import TEMPLATES
from deps.auth import get_user_session
from deps.db import get_db

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

    logger.debug(data)

    return HTTPException(300)
