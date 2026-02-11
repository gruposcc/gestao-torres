import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from core.templates import TResponse, render_chunk, render_html, render_page
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

    return render_page(request, template, context)


@router.get("/login")
async def login_page(request: Request):
    template = "pages/login.html"
    page = {"title": "SCC Torres - Login"}
    context = {"request": request, "page": page, "error": None}

    return render_html(request, template, context)


@router.post("/login")
async def login_post(
    request: Request,
    form: Annotated[UserAuthForm, Form()],
    dbSession=Depends(get_db),
):
    logger.debug("entrei no post login")

    if not request.headers.get("hx-request") == "true":
        logger.warning("not htmx")
        raise HTTPException(403)

    template = "pages/login.html"
    service = AuthService(dbSession)

    logger.debug("chamando serviço ")
    success, payload = await service.login(form)

    if not success:
        # retorna fragmento de html com erro
        context = {"request": request, "email": form.email, "error": payload}
        return TResponse(template, context, block_name="login_form")

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
