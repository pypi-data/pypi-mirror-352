from enum import StrEnum

from pydantic import Field

from .._base import XBase


class RealityFingerprint(StrEnum):
    chrome = "chrome"
    firefox = "firefox"
    safari = "safari"
    ios = "ios"
    android = "android"
    edge = "edge"
    f360 = "360"
    qq = "qq"
    random = "random"
    randomized = "randomized"
    unsafe = "unsafe"


class XRealitySettingsIN(XBase):
    show: bool = False
    target: str
    xver: int = 0
    server_names: list[str] = Field(serialization_alias="serverNames")
    private_key: str = Field(serialization_alias="privateKey")
    min_client_ver: str | None = Field(serialization_alias="minClientVer")
    max_client_ver: str | None = Field(serialization_alias="maxClientVer")
    max_time_diff: int = Field(0, serialization_alias="maxTimeDiff")
    short_ids: list[str] | None = Field(None, serialization_alias="shortIds")


class XRealitySettingsOUT(XBase):
    fingerprint: RealityFingerprint = RealityFingerprint.chrome
    server_name: str = Field(serialization_alias="serverName")
    public_key: str = Field(serialization_alias="publicKey")
    short_id: str | None = Field(serialization_alias="shortId")
    spider_x: str = Field(serialization_alias="spiderX")
