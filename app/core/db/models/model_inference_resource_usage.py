from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import MappedColumn, mapped_column

from app.config.vram import apply_vram_margin, classify_vram_level
from app.core.db.models.base import IDwithTimestamp
from app.schemas.services.inference_resource_usage import (
    InferenceResourceUsage as InferenceResourceUsageSchema,
)


class ModelInferenceResourceUsage(IDwithTimestamp):
    __tablename__ = "model_inference_resource_usage"

    # 측정 대상 모델
    model_id: MappedColumn[int] = mapped_column(
        ForeignKey("model_info.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    # 측정에 사용된 GPU 이름
    gpu_name: MappedColumn[str] = mapped_column(String, nullable=False)
    # 추론 시 최대 VRAM 실측값 (MB). API 응답에는 노출하지 않는다.
    peak_vram_mb: MappedColumn[int] = mapped_column(Integer, nullable=False)
    # 측정 일시
    measured_at: MappedColumn[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
    )
    # 배치 크기, 시퀀스 길이 등 측정 조건
    additional_info: MappedColumn[dict] = mapped_column(JSON, nullable=True)

    def to_schema(self) -> InferenceResourceUsageSchema:
        vram_occupancy_mb = apply_vram_margin(self.peak_vram_mb)
        return InferenceResourceUsageSchema(
            id=self.id,
            model_id=self.model_id,
            gpu_name=self.gpu_name,
            vram_occupancy_mb=vram_occupancy_mb,
            vram_level=classify_vram_level(vram_occupancy_mb),
            measured_at=self.measured_at,
            additional_info=self.additional_info,
        )
