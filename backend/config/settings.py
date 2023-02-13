import os
from typing import List, Type

from cryptography import x509
from cryptography.x509.extensions import SubjectAlternativeName  # type: ignore
from cryptography.x509.general_name import DNSName
from cryptography.x509.oid import ObjectIdentifier  # type: ignore
from starlette.config import Config


class _Settings:
    def __init__(self):
        self.config = Config()

    @property
    def CA_KEY(self):
        if hasattr(self, "_ca_key"):
            return self._ca_key

        with open(os.path.join(self.config("CERTS_DIR"), "local-ca.key"), "rb") as key:
            self._ca_key = key.read()
            return self._ca_key

    @property
    def CA_CRT(self):
        if hasattr(self, "_ca_crt"):
            return self._ca_crt

        with open(os.path.join(self.config("CERTS_DIR"), "local-ca.pem"), "rb") as crt:
            self._ca_crt = crt.read()
            return self._ca_crt

    @property
    def ROOT_CRT(self):
        if hasattr(self, "_root_crt"):
            return self._root_crt

        with open(os.path.join(self.config("CERTS_DIR"), "factory_ca.pem"), "r") as crt:
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
    def DEVICE_GATEWAY_SERVER(self) -> str:
        if hasattr(self, "_device_gateway_server"):
            return self._device_gateway_server  # type: ignore
        if self.config("DEVICE_GATEWAY_SERVER", default="") == "":
            with open(os.path.join(self.config("CERTS_DIR"), "tls-crt"), "rb") as crt:
                certificate = x509.load_pem_x509_certificate(crt.read())
                ext = certificate.extensions.get_extension_for_oid(
                    ObjectIdentifier("2.5.29.17")
                )
                value: Type[SubjectAlternativeName] = ext.value
                values: List[str] = value.get_values_for_type(DNSName)
                for name in values:
                    if "ota-lite" in name:
                        self._device_gateway_server = f"https://{name}:8443"
        else:
            self._device_gateway_server = self.config("DEVICE_GATEWAY_SERVER")
        return self._device_gateway_server

    @property
    def OSTREE_SERVER(self) -> str:
        if hasattr(self, "_ostree_server"):
            return self._ostree_server  # type: ignore
        if self.config("OSTREE_SERVER", default="") == "":
            with open(os.path.join(self.config("CERTS_DIR"), "tls-crt"), "rb") as crt:
                certificate = x509.load_pem_x509_certificate(crt.read())
                ext = certificate.extensions.get_extension_for_oid(
                    ObjectIdentifier("2.5.29.17")
                )
                value: SubjectAlternativeName = ext.value
                values: List[str] = value.get_values_for_type(DNSName)
                for name in values:
                    if "ostree" in name:
                        self._ostree_server = f"https://{name}:8443"
        else:
            self._ostree_server = self.config("OSTREE_SERVER")
        return self._ostree_server

    @property
    def is_debug(self):
        return self.config("STARLETTE_DEBUG", cast=bool, default=False)


Settings = _Settings()
