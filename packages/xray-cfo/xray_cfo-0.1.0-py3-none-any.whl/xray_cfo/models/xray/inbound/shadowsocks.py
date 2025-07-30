from enum import StrEnum

from xray_cfo.models.xray.enums import Network

from .._base import XBase


class SsMethod(StrEnum):
    aes_256 = "aes-256-gcm"
    aes_128 = "aes-128-gcm"
    chacha20_poly1305 = "chacha20-poly1305"
    chacha20_ietf_poly1305 = "chacha20-ietf-poly1305"
    xchacha20_poly1305 = "xchacha20-poly1305"
    xchacha20_ietf_poly1305 = "xchacha20-ietf-poly1305"

    blake3_aes_128 = "2022-blake3-aes-128-gcm"
    blake3_aes_256 = "2022-blake3-aes-256-gcm"

    blake3_chacha20_poly1305 = "blake3_chacha20-poly1305"


class SsClint(XBase):
    password: str
    method: SsMethod | None
    level: int | None
    email: str | None


class XShadowsocksIn(XBase):
    network: Network = Network.tcp
    method: SsMethod | None
    password: str
    level: int = 0
    email: str | None
    clients: list[SsClint] | None
