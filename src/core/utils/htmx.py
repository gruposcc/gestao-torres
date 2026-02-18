import json
from typing import Dict, Any
from fastapi import Request, Response


def is_htmx_request(request: Request):
    if not request.headers.get("hx-request") == "true":
        return False
    else:
        return True


def update_htmx_title(response: Response, title) -> Response:
    response.headers["HX-Trigger-After-Swap"] = json.dumps({"updateTitle": title})
    return response


def redirect_htmx_header(
    response: Response,
    path: str,
    target: str = "#content",
    swap: str = "innerHTML",
    extra_headers: Dict[str, Any] | None = None,
):
    hx_location_header = {"path": path, "target": target, "swap": swap}

    if extra_headers:
        headers = {"headers": extra_headers}
        hx_location_header.update(headers)

    response.headers["HX-location"] = json.dumps(hx_location_header)

    return response
