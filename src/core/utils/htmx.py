from fastapi import Request


def is_htmx_request(request: Request):
    if not request.headers.get("hx-request") == "true":
        return False
    else:
        return True
