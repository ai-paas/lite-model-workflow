from app.config.vram import VramLevel
from app.schemas.requests.base import PageReq


class ReqInferenceResourceUsageForm(PageReq):
    model_id: int | None = None
    gpu_name: str | None = None
    vram_level: VramLevel | None = None
