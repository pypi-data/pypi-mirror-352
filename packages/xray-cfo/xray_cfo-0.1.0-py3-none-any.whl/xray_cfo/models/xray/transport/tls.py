from enum import StrEnum

from pydantic import Field

from .._base import XBase


def get_default_alpn():
    return ["h2", "http/1.1"]


class TLSFingerprint(StrEnum):
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


class TLSCurvePreferences(StrEnum):
    CurveP256 = "CurveP256"
    CurveP384 = "CurveP384"
    CurveP521 = "CurveP521"
    X25519 = "X25519"
    x25519Kyber768Draft00 = "x25519Kyber768Draft00"


def get_default_curve_preferences():
    return ["X25519"]


class TLSCertificateUsage(StrEnum):
    encipherment = "encipherment"
    verify = "verify"
    issue = "issue"


class TLSCertificate(XBase):
    ocsp_stapling: int = Field(3600, serialization_alias="ocspStapling")
    one_time_loading: bool = Field(False, serialization_alias="oneTimeLoading")
    usage: TLSCertificateUsage = TLSCertificateUsage.encipherment
    build_chain: bool = Field(False, serialization_alias="buildChain")
    certificate_file: str | None = Field(None, serialization_alias="certificateFile")
    key_file: str | None = Field(None, serialization_alias="keyFile")
    certificate: list[str] | None = None
    key: list[str] | None = None


class XTLSSettings(XBase):
    server_name: str = Field(serialization_alias="serverName")
    server_name_to_verify: str | None = Field(
        None, serialization_alias="serverNameToVerify"
    )
    reject_unknown_sni: bool = Field(False, serialization_alias="rejectUnknownSni")
    allow_insecure: bool = Field(True, serialization_alias="allowInsecure")
    alpn: list[str] = Field(default_factory=get_default_alpn)
    min_version: str = Field("1.2", serialization_alias="minVersion")
    max_version: str = Field("1.3", serialization_alias="maxVersion")
    cipher_suites: str | None = Field(None, serialization_alias="CipherSuites")
    certificates: list[TLSCertificate] = Field(default_factory=list)
    disable_system_root: bool = Field(False, serialization_alias="disableSystemRoot")
    enable_session_resumption: bool = Field(
        False, serialization_alias="enableSessionResumption"
    )
    fingerprint: TLSFingerprint = TLSFingerprint.chrome
    pinned_peer_certificate_chain_sha256: list[str] | None = Field(
        serialization_alias="pinnedPeerCertificateChainSha256"
    )
    curve_preferences: list[TLSCurvePreferences] = Field(
        default_factory=get_default_curve_preferences,
        serialization_alias="curvePreferences",
    )
    master_key_log: str | None = Field(None, serialization_alias="masterKeyLog")
