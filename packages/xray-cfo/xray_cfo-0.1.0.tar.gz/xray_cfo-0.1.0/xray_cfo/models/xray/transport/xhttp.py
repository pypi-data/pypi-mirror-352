from pydantic import Field

from .._base import XBase


class XXHttpSettings(XBase):
    host: str
    path: str
    mode: str
    extra: str
