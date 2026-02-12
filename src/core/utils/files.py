import os
import re


def truncate_filename(filename: str, max_length: int = 80) -> str:
    """
    Encurta o nome do arquivo preservando a extensão.
    Ex: 'projeto_muito_grande_mesmo.pdf' -> 'projeto_muito_gr.pdf'
    """
    if len(filename) <= max_length:
        return filename

    name, ext = os.path.splitext(filename)
    # Subtrai o tamanho da extensão do limite total
    allowed_name_len = max_length - len(ext)
    return name[:allowed_name_len] + ext


def sanitize_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_\-\.]", "", name)
    return name
