from sqlalchemy import case, func, select

from app.config.vram import (
    VRAM_LEVEL_LOW_MAX_MB,
    VRAM_LEVEL_MID_MAX_MB,
    VRAM_MARGIN_RATIO,
    VramLevel,
)
from app.core.db.connect import SessionDepends
from app.core.db.models.model_inference_resource_usage import ModelInferenceResourceUsage
from app.core.db.session import SessionLocal
from app.schemas.requests.inference_resource_usage import ReqInferenceResourceUsageForm
from app.schemas.services.inference_resource_usage import (
    InferenceResourceUsage as InferenceResourceUsageSchema,
)


class InferenceResourceUsageRepository:
    """
    db에 저장된 모델 추론 자원 사용량 조회

    입력 및 편집 기능은 추후 구현
    """
    def __init__(self, db: SessionLocal):
        self.db = db

    def __vram_occupancy_expr(self):
        return func.ceil(ModelInferenceResourceUsage.peak_vram_mb * VRAM_MARGIN_RATIO)

    def __vram_level_expr(self):
        occupancy = self.__vram_occupancy_expr()
        return case(
            (occupancy < VRAM_LEVEL_LOW_MAX_MB, VramLevel.LOW.value),
            (occupancy < VRAM_LEVEL_MID_MAX_MB, VramLevel.MID.value),
            else_=VramLevel.HIGH.value,
        )

    def __apply_sort_and_paginate(
        self, statement: select, form: ReqInferenceResourceUsageForm
    ) -> select:
        """
        정렬 및 페이지네이션 적용
        - 기본 정렬 조건: 측정일시 내림차순, 동일 측정일시는 id 내림차순
        """
        statement = statement.order_by(
            ModelInferenceResourceUsage.measured_at.desc(),
            ModelInferenceResourceUsage.id.desc(),
        )
        statement = statement.offset(form.offset).limit(form.limit)
        return statement

    def __apply_filter(self, statement: select, form: ReqInferenceResourceUsageForm) -> select:
        """
        필터 적용
        - 모델 id 필터
        - gpu 이름 필터
        - vram 등급(상/중/하) 필터. 등급은 실측값 * 1.2 점유량 기준
        """
        if form.model_id:
            statement = statement.where(ModelInferenceResourceUsage.model_id == form.model_id)
        if form.gpu_name:
            statement = statement.where(
                ModelInferenceResourceUsage.gpu_name.ilike(f"%{form.gpu_name}%")
            )
        if form.vram_level:
            statement = statement.where(self.__vram_level_expr() == form.vram_level.value)
        statement = statement.where(ModelInferenceResourceUsage.deleted_at.is_(None))
        return statement

    def get_inference_resource_usage_list(
        self, form: ReqInferenceResourceUsageForm
    ) -> list[InferenceResourceUsageSchema]:
        """
        추론 자원 사용량 목록 조회
        """
        statement = select(ModelInferenceResourceUsage)
        statement = self.__apply_filter(statement, form)
        statement = self.__apply_sort_and_paginate(statement, form)
        result = self.db.execute(statement).scalars().all()
        return [usage.to_schema() for usage in result]

    def get_inference_resource_usage_count(self, form: ReqInferenceResourceUsageForm) -> int:
        """
        추론 자원 사용량 개수 조회
        """
        statement = select(func.count(ModelInferenceResourceUsage.id))
        statement = self.__apply_filter(statement, form)
        return self.db.execute(statement).scalar_one_or_none()

    def get_inference_resource_usage_by_id(self, id: int) -> InferenceResourceUsageSchema | None:
        """
        추론 자원 사용량 상세 조회
        """
        statement = (
            select(ModelInferenceResourceUsage)
            .where(
                ModelInferenceResourceUsage.id == id,
                ModelInferenceResourceUsage.deleted_at.is_(None),
            )
            .limit(1)
        )
        result = self.db.execute(statement).scalar_one_or_none()
        return result.to_schema() if result else None


def get_inference_resource_usage_repository(db: SessionLocal = SessionDepends):
    return InferenceResourceUsageRepository(db)
