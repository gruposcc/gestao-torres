import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request

from core.settings import TEMPLATES
from schemas.auth import UserAuthForm
from schemas.user import UserIn

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


router = APIRouter()


@router.get("/home")
async def home(request: Request):
    context = {"request": request}
    return TEMPLATES.TemplateResponse("home.html", context)


@router.get("/login")
async def login_page(request: Request):
    context = {"request": request}
    return TEMPLATES.TemplateResponse("login.html", context)


@router.post("/login")
async def login_post(request: Request, form: Annotated[UserAuthForm, Form()]):
    context = {"request": request}
    return form
