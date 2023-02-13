from starlette.responses import JSONResponse


def bad_request(msg: str):
    content = {"error": msg}
    return JSONResponse(content=content, status_code=400)
