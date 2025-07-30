import ipaddress
import re
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from ._base import XBase


class ApiService(StrEnum):
    handler = "HandlerService"
    logger = "LoggerService"
    stats = "StatsService"
    routing = "RoutingService"
    reflection = "ReflectionService"


LISTEN_REGEX = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[.*\]|\w+):\d+$")


class XApi(XBase):
    tag: str
    listen: str | None
    service: list[ApiService] = Field(default_factory=list)

    @field_validator("listen")
    def validate_listen_format(cls, v):
        if v is None:
            return v

        if not LISTEN_REGEX.match(v):
            raise ValueError("listen must be in format 'ip:port'")

        try:
            ip, port = v.rsplit(":", 1)
            ip_cleaned = ip[1:-1] if ip.startswith("[") and ip.endswith("]") else ip
            ipaddress.ip_address(ip_cleaned)
        except Exception as e:
            raise ValueError(f"Invalid IP address or port: {e}")

        return v
