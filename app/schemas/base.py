from pydantic import BaseModel, ConfigDict

class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
