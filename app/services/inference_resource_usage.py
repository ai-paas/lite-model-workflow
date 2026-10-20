from fastapi import Depends, HTTPException

from app.core.repo.inference_resource_usage import (
    InferenceResourceUsageRepository,
    get_inference_resource_usage_repository,
)
from app.schemas.requests.inference_resource_usage import ReqInferenceResourceUsageForm
from app.schemas.responses.inference_resource_usage import RespInferenceResourceUsagePage
from app.schemas.services.inference_resource_usage import (
    InferenceResourceUsage as InferenceResourceUsageSchema,
)


class InferenceResourceUsageService:
    # crud 중 r 만 구현, 추후 필요시 추가
    def __init__(self, inference_resource_usage_repo: InferenceResourceUsageRepository):
        self.inference_resource_usage_repo = inference_resource_usage_repo

    def get_inference_resource_usage_list(
        self, form: ReqInferenceResourceUsageForm
    ) -> RespInferenceResourceUsagePage:
        usage_list = self.inference_resource_usage_repo.get_inference_resource_usage_list(form)
        total_count = self.inference_resource_usage_repo.get_inference_resource_usage_count(form)
        return RespInferenceResourceUsagePage(
            items=usage_list,
            total_count=total_count,
            page_size=form.page_size,
            current_page=form.page_num,
            url_params=form.model_dump(exclude_none=True),
        )

    def get_inference_resource_usage_by_id(self, id: int) -> InferenceResourceUsageSchema:
        usage = self.inference_resource_usage_repo.get_inference_resource_usage_by_id(id)
        if not usage:
            raise HTTPException(status_code=404, detail="Inference resource usage not found")
        return usage


def get_inference_resource_usage_service(
    inference_resource_usage_repo: InferenceResourceUsageRepository = Depends(
        get_inference_resource_usage_repository
    ),
):
    return InferenceResourceUsageService(inference_resource_usage_repo)
