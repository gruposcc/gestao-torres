from fastapi import HTTPException, Request


def is_htmx_request(request: Request):
    if not request.headers.get("hx-request") == "true":
        # return False
        raise HTTPException(403)
    else:
        return True
