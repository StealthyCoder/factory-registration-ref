import os
from starlette.config import Config


class _Settings():
    
    def __init__(self):
        self.config = Config()
        
    @property
    def CA_KEY(self):
        if hasattr(self, '_ca_key'):
            return self._ca_key
        
        with open(os.path.join(self.config('CERTS_DIR'), "local-ca.key"), "rb") as key:
            self._ca_key = key.read()
            return self._ca_key

    @property
    def CA_CRT(self):
        if hasattr(self, '_ca_crt'):
            return self._ca_crt
            
        with open(os.path.join(self.config('CERTS_DIR'), "local-ca.pem"), "rb") as crt:
            self._ca_crt = crt.read()
            return self._ca_crt

    @property
    def ROOT_CRT(self):
        if hasattr(self, '_root_crt'):
            return self._root_crt
            
        with open(os.path.join(self.config('CERTS_DIR'), "factory_ca.pem"), "r") as crt:
            self._root_crt = crt.read()
            return self._root_crt

    @property
    def DEVICES_DIR(self):
        return self.config("DEVICES_DIR")

    @property
    def API_TOKEN(self):
        return self.config("API_TOKEN", default="")

    @property
    def DEVICE_GROUP(self):
        return self.config("DEVICE_GROUP", default="")

    @property
    def DEVICE_GATEWAY_SERVER(self):
        self.config("DEVICE_GATEWAY_SERVER", default="")

    @property
    def is_debug(self):
        return self.config("STARLETTE_DEBUG", cast=bool, default=False)


Settings = _Settings()