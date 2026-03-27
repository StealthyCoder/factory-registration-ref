import datetime
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)
from cryptography.x509.base import load_pem_x509_certificate, load_pem_x509_csr
from cryptography.x509.oid import NameOID  # type: ignore

from config.settings import Settings
from dto.device import DeviceInfo


async def _key_pair() -> Tuple[EllipticCurvePrivateKey, x509.Certificate]:
    try:
        return _key_pair._cached  # type: ignore
    except AttributeError:
        pass

    ca = load_pem_x509_certificate(Settings.CA_CRT)
    pk = load_pem_private_key(Settings.CA_KEY, None)

    # Make sure the Factory owner gave us a cert capable of signing CSRs
    try:
        ext = ca.extensions.get_extension_for_class(x509.BasicConstraints)
        if not ext.value.ca:
            raise ValueError("Factory not allowed to sign Device CSRs")
    except x509.extensions.ExtensionNotFound:  # type: ignore
        raise ValueError("Factory not allowed to sign Device CSRs")

    _key_pair._cached = (pk, ca)  # type: ignore
    return _key_pair._cached  # type: ignore


async def sign_device_csr(csr: str) -> DeviceInfo:
    cert = load_pem_x509_csr(csr.encode())
    factory = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[
        0
    ].value
    uuid = str(cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)

    pk, ca = await _key_pair()
    actual_factory = ca.subject.get_attributes_for_oid(
        NameOID.ORGANIZATIONAL_UNIT_NAME
    )[0].value
    if factory != actual_factory:
        raise ValueError(f"Invalid factory({factory}) must be {actual_factory}")

    signed = (
        x509.CertificateBuilder()
        .subject_name(cert.subject)  # type: ignore
        .serial_number(int("0x" + str(uuid.replace("-", "")), 16))
        .issuer_name(ca.subject)
        .public_key(cert.public_key())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7300)
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.ExtendedKeyUsage.oid]),
            critical=True,
        )
        .sign(pk, SHA256(), default_backend())
    )
    signed_bytes = signed.public_bytes(encoding=Encoding.PEM)
    public_bytes = cert.public_key().public_bytes(
        format=PublicFormat.SubjectPublicKeyInfo, encoding=Encoding.PEM
    )

    return DeviceInfo(
        str(factory),
        Settings.ROOT_CRT,
        public_bytes.decode(),
        signed_bytes.decode(),
        uuid,
    )
