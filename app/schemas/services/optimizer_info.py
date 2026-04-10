from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field

from app.config.enums import SupportOptimizerType

class OptimizerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow", populate_by_name=True)
    id: int
    optimizer_name: str
    optimizer_type: str | None = Field(default=None, pattern=SupportOptimizerType.to_regex_pattern())
    accelerator: str
    argument: dict
