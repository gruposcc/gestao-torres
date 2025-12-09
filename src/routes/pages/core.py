import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from core.settings import TEMPLATES
from deps.auth import get_user_session
from deps.db import get_db
from schemas.auth import UserAuthForm
from services.auth import AuthService

logger = logging.getLogger("app.pages.core")
logger.level = logging.DEBUG


router = APIRouter()


@router.get("/home")
async def home(request: Request, user=Depends(get_user_session)):
    template = "pages/home.html"
    page = {"title": "Home"}

    context = {"request": request, "user": user, "page": page}

    if request.headers.get("hx-request") == "true":
        return TEMPLATES.TemplateResponse(template, context, block_name="content")

    return TEMPLATES.TemplateResponse(template, context)


@router.get("/login")
async def login_page(request: Request):
    template = "pages/login.html"
    context = {"request": request, "error": None}
    return TEMPLATES.TemplateResponse(template, context)


@router.post("/login")
async def login_post(
    request: Request,
    form: Annotated[UserAuthForm, Form()],
    dbSession=Depends(get_db),
):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    template = "pages/login.html"
    service = AuthService(dbSession)

    success, payload = await service.login(form)

    if not success:
        # retorna fragmento de html com erro
        context = {"request": request, "email": form.email, "error": payload}
        return TEMPLATES.TemplateResponse(template, context, block_name="login_form")

    response = HTMLResponse(status_code=200)
    response.set_cookie(
        "access-token",
        payload.access_token,  # pyright: ignore[reportAttributeAccessIssue]
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh-token",
        payload.refresh_token,  # pyright: ignore[reportAttributeAccessIssue]
        httponly=True,
        secure=False,
        samesite="lax",
        path="",
    )

    response.headers["HX-Redirect"] = "/home"

    return response


@router.post("/logout", status_code=204)
async def logout(request: Request):
    response = HTMLResponse()
    response.delete_cookie("access-token", path="/")
    response.delete_cookie("refresh-token", path="/")
    response.headers["HX-Redirect"] = "/login"
    return response
