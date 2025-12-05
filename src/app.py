from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.api import app as api_app
from core.database import sessionmanager
from core.settings import BASE_DIR, TEMPLATES
from core.utils.jinja import CommentExtension
from routes.htmx.router import router as htmx_router
from routes.pages.router import router as pages_router

TEMPLATES.env.add_extension(CommentExtension)
LOGGER = getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ...
        sessionmanager.init_db()
        yield
    except:
        raise


app = FastAPI(lifespan=lifespan, docs=False)

app.include_router(pages_router)
app.include_router(htmx_router)


# adiciona o app da api
app.mount("/api", api_app, name="api")

# estaticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "dist")), name="static")


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    is_page_route = not request.url.path.startswith(
        "/api"
    ) and not request.url.path.startswith("/static")

    if is_page_route:
        return RedirectResponse("/login", status_code=302)


# REDIRECT / -> /home
@app.get("/")
async def root_redirect(request: Request):
    return RedirectResponse(url="/home", status_code=302)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://10.4.0.7:8000",
        "http://10.11.11.204:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
