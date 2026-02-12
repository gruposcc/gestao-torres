import pkgutil
from importlib import import_module

from core.settings import BASE_DIR

MODELS_DIR = str(BASE_DIR / "models")


def load_models():
    for module_info in pkgutil.iter_modules([MODELS_DIR]):
        if module_info.ispkg:
            # Se quiser tratar subpackages depois…
            continue
        if module_info.name == "__init__":
            continue
        if module_info.name == "base":
            continue

        module_name = f"models.{module_info.name}"
        _module = import_module(module_name)
