from fastapi import APIRouter, Depends

from app.schemas.requests.inference_resource_usage import ReqInferenceResourceUsageForm
from app.schemas.responses.inference_resource_usage import RespInferenceResourceUsagePage
from app.schemas.services.inference_resource_usage import InferenceResourceUsage
from app.services.inference_resource_usage import (
    InferenceResourceUsageService,
    get_inference_resource_usage_service,
)

router = APIRouter()


@router.get("")
def get_inference_resource_usage_list(
    form: ReqInferenceResourceUsageForm = Depends(ReqInferenceResourceUsageForm),
    inference_resource_usage_service: InferenceResourceUsageService = Depends(
        get_inference_resource_usage_service
    ),
) -> RespInferenceResourceUsagePage:
    """
    모델 추론 자원 사용량 목록 조회

    - 페이지네이션 적용
    - `model_id`, `gpu_name`, `vram_level`(상/중/하) 으로 필터링
    - 응답의 `vram_occupancy_mb` 는 실측값에 마진 1.2배를 적용한 값
    - 실측 VRAM(`peak_vram_mb`) 은 응답에 포함하지 않음
    """
    return inference_resource_usage_service.get_inference_resource_usage_list(form)


@router.get("/{usage_id}")
def get_inference_resource_usage(
    usage_id: int,
    inference_resource_usage_service: InferenceResourceUsageService = Depends(
        get_inference_resource_usage_service
    ),
) -> InferenceResourceUsage:
    """
    모델 추론 자원 사용량 상세 조회

    - 응답의 `vram_occupancy_mb` 는 실측값에 마진 1.2배를 적용한 값
    - 실측 VRAM(`peak_vram_mb`) 은 응답에 포함하지 않음
    """
    return inference_resource_usage_service.get_inference_resource_usage_by_id(usage_id)
