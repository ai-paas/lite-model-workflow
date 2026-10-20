from fastapi import APIRouter

from app.api.v1.model import router as model_router
from app.api.v1.task import router as task_router
from app.api.v1.optimize import router as optimize_router
from app.api.v1.info import router as info_router
from app.api.v1.inference_resource_usage import router as inference_resource_usage_router

# API 버전 관리 폴더
router = APIRouter(prefix="/v1")

router.include_router(model_router, prefix="/models", tags=["Models"])
router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
router.include_router(optimize_router, prefix="/optimize", tags=["Optimize"])
router.include_router(info_router, prefix="/checked", tags=["Info"])
router.include_router(
    inference_resource_usage_router,
    prefix="/inference-resources",
    tags=["InferenceResource"],
)
