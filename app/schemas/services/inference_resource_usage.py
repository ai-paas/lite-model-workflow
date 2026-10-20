from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.config.vram import VramLevel


class InferenceResourceUsage(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow", populate_by_name=True)
    id: int
    model_id: int
    gpu_name: str
    vram_occupancy_mb: int
    vram_level: VramLevel = Field(pattern=VramLevel.to_regex_pattern())
    measured_at: datetime | None = None
    additional_info: dict | None = None
