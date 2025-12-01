import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from jinja2_fragments.fastapi import Jinja2Blocks

from .log import LOG_CONFIG  # noqa: F401

# diretorio de templates
load_dotenv()

APP_LISTEN_ADDR: str = os.environ.get("APP_LISTEN_ADDR", "0.0.0.0")  # ou dominio
APP_LISTEN_PORT: str = os.environ.get("APP_LISTEN_PORT", "")
APP_ENV: str = os.environ.get("APP_ENV", "dev").lower()

LDAP_AUTH: bool
LDAP_BASE_DN: str = os.environ.get("LDAP_BASE_DN", "")
LDAP_BIND_PASSWORD: str = os.environ.get("LDAP_BIND_PASSWORD", "")
LDAP_BIND_USER: str = os.environ.get("LDAP_BIND_USER", "")
LDAP_SERVER: str = os.environ.get("LDAP_SERVER", "")
LDAP_USE_SSL = True
LDAP_UPN_SUFFIX = os.environ.get("LDAP_UPN_SUFFIX", "")

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.environ.get("POSTGRES_DB")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")

DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

JWT_SECRET = os.getenv("JWT_SECRET", "change_this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 15  # 15 min
JWT_EXPIRE_MINUTES_REFRESH = 60 * 24 * 7  # 7 dias

BASE_DIR = Path(__file__).parent.parent

TEMPLATES = Jinja2Blocks(directory=str(BASE_DIR / "templates"))
