import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request

from core.templates import TResponse
from deps.db import get_db
from schemas.auth import UserAuthForm
from services.user import UserService

logger = logging.getLogger("app.hmtx.user")
logger.level = logging.DEBUG


router = APIRouter(prefix="/user")


@router.post("/email")
async def email_input(request: Request, email: str = Form(), dbSession=Depends(get_db)):
    if not request.headers.get("hx-request") == "true":
        raise HTTPException(403)

    template = "pages/user/create.html"

    service = UserService(dbSession)
    exists = await service.email_exists(email)

    if exists:
        context = {
            "request": request,
            "error": {"email": "Email em uso"},
        }
        return TResponse(template, context, block_name="email_feedback")

    context = {"request": request}

    return TResponse(template, context, block_name="email_feedback")
