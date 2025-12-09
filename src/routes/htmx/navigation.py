import logging

from fastapi import APIRouter, Request

from core.settings import TEMPLATES
from deps.db import get_db
from schemas.auth import UserAuthForm
from services.auth import AuthService

logger = logging.getLogger("app.hmtx.navigation")
logger.level = logging.DEBUG


router = APIRouter()


@router.get("/breadcumb")
async def home(request: Request, path: str):
    logger.debug(path)

    template = "partials/breadcumb.html"
    breadcumb = [
        {"label": "home", "url": "/home", "icon": "house"},
        {"label": "usuários", "url": "/user"},
    ]

    context = {"request": request, "breadcumb": breadcumb}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")
