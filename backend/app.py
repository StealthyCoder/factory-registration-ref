from time import sleep
from typing import Optional

from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from auth.anonymous import AllAllowed
from config.settings import Settings
from crypto import sign_device_csr
from responses.error import bad_request
from util.foundries import create_in_foundries
from util.logging import log_device, log_error
from util.sota_toml import sota_toml_fmt


@requires("authenticated")
async def sign(request: Request):
    if await request.body() != b"":
        data = await request.json()

        csr = data.get("csr")
        if not csr:
            return bad_request("Missing required field 'csr'")
        if not isinstance(csr, str):
            return bad_request("Data type of 'csr' is not string")

        hwid = data.get("hardware-id")
        if not hwid:
            return bad_request("Missing required field 'hardware-id'")

        overrides = data.get("overrides") or {}
        sota_config_dir = data.get("sota-config-dir") or "/var/sota"
        name = data.get("name") or None

        if data.get("group"):
            # Since we run w/o any authentication, allowing devices to determine
            # their device group is too dangerous to allow by default. We instead
            # allow a server defined config, Settings.DEVICE_GROUP.
            return bad_request("Registration-reference does not support 'group' field")

        try:
            fields = await sign_device_csr(csr)
        except ValueError as e:
            return bad_request(str(e))

        await create_in_foundries(fields.client_crt, Settings.API_TOKEN, name)

        await log_device(fields.uuid, fields.pubkey)

        return JSONResponse(
            {
                "root.crt": fields.root_crt,
                "sota.toml": await sota_toml_fmt(hwid, overrides, sota_config_dir),
                "client.pem": fields.client_crt,
                "client.chained": fields.client_crt
                + "\n"
                + Settings.CA_CRT.decode("utf-8"),
            },
            status_code=201,
        )

    return bad_request("Missing request body")


middleware = [Middleware(AuthenticationMiddleware, backend=AllAllowed())]

app = Starlette(
    debug=Settings.is_debug,
    routes=[
        Route("/sign", sign, methods=["POST"]),
    ],
    middleware=middleware,
)
