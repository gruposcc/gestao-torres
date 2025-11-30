import importlib
import pkgutil

from fastapi import APIRouter

from routes.pages import (
    __path__ as pages_path,  # pyright: ignore[reportAttributeAccessIssue]
)

router = APIRouter()

for module_info in pkgutil.iter_modules(pages_path):
    name = module_info.name
    if name == "router":
        continue

    module = importlib.import_module(f"routes.pages.{name}")

    if hasattr(module, "router"):
        router.include_router(module.router)
