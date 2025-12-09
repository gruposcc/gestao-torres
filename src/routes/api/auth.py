import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse

from deps.auth import get_db, get_user_session
from schemas.auth import UserAuthForm, UserSession
from schemas.user import UserOut
from services.auth import AuthService

logger = logging.getLogger("app.api.user")
logger.level = logging.DEBUG


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
async def login(data: UserAuthForm, dbSession=Depends(get_db)):
    service = AuthService(dbSession)

    success, payload = await service.login(data)
    if not success:
        raise HTTPException(401, payload)

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

    return response


@router.get("/me", response_model=UserSession)
async def me(response: Response, user=Depends(get_user_session)):
    return user
