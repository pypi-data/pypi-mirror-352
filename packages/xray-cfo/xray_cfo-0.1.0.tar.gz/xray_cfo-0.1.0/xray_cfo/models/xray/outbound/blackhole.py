from pydantic import Field

from .._base import XBase


def get_default_response():
    return {"type": "none"}


class BlackHoleOut(XBase):
    response: dict[str, str] = Field(default_factory=get_default_response)
