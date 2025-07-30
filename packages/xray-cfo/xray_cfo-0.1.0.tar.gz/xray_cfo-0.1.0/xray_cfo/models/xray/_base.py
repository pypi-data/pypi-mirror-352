from pydantic import BaseModel, ConfigDict


class XBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
