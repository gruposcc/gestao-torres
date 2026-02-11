from fastapi import HTTPException, Request, Response
from jinja2_fragments.fastapi import Jinja2Blocks

from core.settings import BASE_DIR
from core.utils.htmx import is_htmx_request, update_htmx_title
from core.utils.jinja import CommentExtension

T = Jinja2Blocks(directory=str(BASE_DIR / "templates"))

T.env.auto_reload = True
T.env.cache = {}
T.env.add_extension(CommentExtension)

TResponse = T.TemplateResponse


def render_page(
    request: Request,
    template: str,
    context: dict,
    htmx_block: str | None = "content",
    update_title: bool = True,
) -> Response:
    # se request htmx
    if is_htmx_request(request):
        if not htmx_block:  # se, bloco
            response = TResponse(template, context)

        response = TResponse(template, context, block_name=htmx_block)  # com bloco

        if (
            context["page"] and update_title
        ):  # se update_title atualiza titulo por header
            title = context["page"].get("title", None)
            if title:
                response = update_htmx_title(response, str(title))

    else:  # Retorno o template inteiro
        response = TResponse(template, context)

    return response


def render_chunk(
    request: Request,
    template: str,
    context: dict,
    block: str | None = None,
):
    if not is_htmx_request(request):
        raise HTTPException(403)

    if not block:
        response = TResponse(template, context)
    else:
        response = TResponse(template, context, block_name=block)

    return response


def render_html(request: Request, template: str, context: dict):
    return TResponse(template, context)


""" def render_raw(
    
)


def handle_htmx_form(
    
) """
