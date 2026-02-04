from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

from core.api import app as api_app
from core.database import sessionmanager
from core.geocode_old import stop_geocoder
from core.middleware.no_cache import NoCacheMiddleware
from core.notifier import Notifier, get_notifier
from core.settings import BASE_DIR, TEMPLATES
from core.utils.jinja import CommentExtension
from deps.auth import get_user_session
from routes.htmx.router import router as htmx_router
from routes.pages.router import router as pages_router
from schemas.auth import UserSession

TEMPLATES.env.add_extension(CommentExtension)
LOGGER = getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ...
        geocoder = Nominatim(user_agent="scctorres_v1", adapter_factory=AioHTTPAdapter)
        sessionmanager.init_db()  #
        # posso transformar a dependencia do db em um app.state tambem
        app.state.geocoder = geocoder

        yield
    except:
        await stop_geocoder()
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


# --- Rota SSE (Endpoint de Conexão) ---
@app.get("/events")
async def sse_endpoint(
    request: Request,
    # 💡 Usa sua dependência existente para autenticar e obter o objeto UserSession
    user_session: UserSession = Depends(get_user_session),
    notifier: Notifier = Depends(get_notifier),
):
    """Endpoint para a conexão Server-Sent Events, roteado pelo user_id autenticado."""
    # Extrai o ID do usuário autenticado para roteamento unicast
    user_id = user_session.id

    return StreamingResponse(
        notifier.subscribe(request, user_id.hex), media_type="text/event-stream"
    )


app.add_middleware(NoCacheMiddleware)

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
