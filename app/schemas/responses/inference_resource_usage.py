from urllib.parse import urlencode

from pydantic import ConfigDict, computed_field, Field

from app.schemas.services.inference_resource_usage import InferenceResourceUsage
from app.schemas.responses.base import RespPagination


class RespInferenceResourceUsagePage(RespPagination):
    model_config = ConfigDict(from_attributes=True, extra="allow", populate_by_name=True)
    items: list[InferenceResourceUsage]
    url_params: dict[str, str | int | None] = Field(default_factory=dict, exclude=True)

    @computed_field
    @property
    def next_page(self) -> str | None:
        """
        다음 페이지 링크 생성
        url_params 입력 필요
        """
        if self.next_page_num:
            url_params = self.url_params
            url_params["page_num"] = str(self.next_page_num)
            url_params_str = ("?" + urlencode(url_params)) if url_params else ""
            return f"/api/v1/inference-resources{url_params_str}"
        return None

    @computed_field
    @property
    def prev_page(self) -> str | None:
        if self.prev_page_num:
            url_params = self.url_params
            url_params["page_num"] = str(self.prev_page_num)
            url_params_str = ("?" + urlencode(url_params)) if url_params else ""
            return f"/api/v1/inference-resources{url_params_str}"
        return None
