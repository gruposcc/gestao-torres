import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from core.notifier import Notifier, get_notifier
from core.settings import TEMPLATES
from deps.auth import get_user_session
from deps.db import get_db
from schemas.user import UserIn, UserOut
from services.user import UserService

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
        return TEMPLATES.TemplateResponse(
            template, context, block_name="content"
        )

    return TEMPLATES.TemplateResponse(template, context)
