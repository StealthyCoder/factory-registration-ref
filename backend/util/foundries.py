import requests
from starlette.exceptions import HTTPException
from time import sleep
from typing import Optional
from config.settings import Settings
from util.logging import log_msg, log_error

async def create_in_foundries(client_cert: str, api_token: str, name: Optional[str] = None) -> None:
    if not api_token:
        return None
    await log_msg(f"Creating in foundries with {name}", __name__)
    data = {
        "client.pem": client_cert,
    }
    if Settings.DEVICE_GROUP:
        data["group"] = Settings.DEVICE_GROUP
    if name:
        data["name"] = name

    headers: dict = {
        "OSF-TOKEN": api_token,
    }
    for x in (0.1, 0.2, 1):
        r = requests.put(
            "https://api.foundries.io/ota/devices/", headers=headers, json=data
        )
        if r.status_code == 409:
            raise HTTPException(r.status_code, detail=r.text)
        if r.ok:
            return None
        msg = f"Unable to create device on server: HTTP_{r.status_code} - {r.text}"
        await log_error(msg, __name__)
        
        await log_msg(f"Trying again in {x}s", __name__)
        sleep(x)
    else:
        raise HTTPException(500, detail=msg)