import logging

from fastapi import APIRouter, Depends, Request

from core.settings import TEMPLATES
from deps.auth import get_user_session
from deps.db import get_db
from deps.geocoder import get_geocoder

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


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
