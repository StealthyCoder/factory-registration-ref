from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    namespace: str
    root_crt: str
    pubkey: str
    client_crt: str
    uuid: str
