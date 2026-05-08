from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from kfp import dsl, kubernetes
from kfp.client.client import RunPipelineResult

from app.config.enums import SupportOptimize
from app.config.k8s import SupportTolerationFactory, SupportNodeSelectorFactory
from app.core.settings import get_settings
from app.core.repo.model_task import get_model_task_repository, ModelTaskRepository
from app.core.repo.optimizer_info import get_optimizer_info_repository, OptimizerInfoRepository
from app.schemas.services.types import OptimizationSetUp
from app.schemas.requests.optimize import ReqOptimizeWithNameAndArgsBody
from app.schemas.services.model_task import ModelTaskSchema
from app.utils.kfp_client_manager import KFPClientManager
from app.utils.uuid import get_uuid_str

SETTINGS = get_settings()


def get_optimize_service(
    model_task_repo: ModelTaskRepository = Depends(get_model_task_repository),
    optimizer_info_repo: OptimizerInfoRepository = Depends(get_optimizer_info_repository),
):

    return OptimizeService(model_task_repo=model_task_repo, optimizer_info_repo=optimizer_info_repo)


class OptimizeService:
    def __init__(self, model_task_repo: ModelTaskRepository, optimizer_info_repo: OptimizerInfoRepository):
        self.model_task_repo = model_task_repo
        self.optimizer_info_repo = optimizer_info_repo

    @staticmethod
    def run_optimize_task(task_info: OptimizationSetUp):
        """
        최적화 작업 실행
        Args:
            db: 데이터베이스 세션
            task_info: 최적화 작업 정보
        Returns:
            task_info: 최적화 작업 정보
        """
        
        @dsl.container_component
        # 사용할 컨테이너 정의 및 설정 추가
        def lite_model_component():
            return dsl.ContainerSpec(
                # 사용할 도커이미지의 주소 및 태그
                image=task_info.docker_image_path,
                # 실행할 커맨드
                command=task_info.command,
                # 필요한 변수들 정의 (string으로 정의)
                args=task_info.args,
            )

        # 파이프라인 정의
        @dsl.pipeline(name=f"{task_info.model_name}_{task_info.optimize_name}")
        def lite_model():
            lite_model_task = lite_model_component()

            if task_info.accelerator_type != "cpu":
                accelerator_type: str = task_info.accelerator_type
                lite_model_task.set_accelerator_limit(1)  # container_spec.resources.accelerator_limit
                lite_model_task.container_spec.resources.accelerator_type = accelerator_type

                toleration = SupportTolerationFactory.get_toleration_by_optimizer(
                    SupportOptimize(task_info.optimize_name)
                )
                if toleration:
                    kubernetes.add_toleration(
                        lite_model_task, 
                        key=toleration.KEY.value,
                        operator=toleration.OPERATOR.value,
                        value=toleration.VALUE.value,
                        effect=toleration.EFFECT.value,
                    )
                node_selector = SupportNodeSelectorFactory.get_node_selector_by_optimizer(
                    SupportOptimize(task_info.optimize_name)
                )
                if node_selector:
                    kubernetes.add_node_selector(
                        lite_model_task, 
                        label_key=node_selector.KEY.value,
                        label_value=node_selector.VALUE.value,
                    )
            # Kubeflow 파이프라인 캐시 비활성화
            lite_model_task.set_caching_options(False)

            # 환경변수 설정
            for key, value in task_info.env.items():
                lite_model_task.set_env_variable(key, value)

        # 정의된 함수로 파이프라인 생성

        kfp_client = KFPClientManager(
            kubeflow_endpoint=SETTINGS.KUBEFLOW_ENDPOINT,
            kubeflow_username=SETTINGS.KUBEFLOW_USERNAME,
            kubeflow_password=SETTINGS.KUBEFLOW_PASSWORD,
        ).get_kfp_client()

        run: RunPipelineResult = kfp_client.create_run_from_pipeline_func(
            experiment_name="aipaas-lite-model-workflow",
            pipeline_func=lite_model,
            namespace=SETTINGS.KUBEFLOW_NAMESPACE,
        )

        return run


    def _save_task_info(self, task_info: OptimizationSetUp, run: RunPipelineResult):
        kubeflow_experiment_id = run.run_id
        uuid_str = task_info.env["SERVER_UUID"]

        # todo: repository 적용
        new_task = ModelTaskSchema(
            task_uuid=uuid_str,
            model_name=task_info.model_name,
            task_type=task_info.optimize_name,
            kubeflow_experiment_id=kubeflow_experiment_id,
        )

        self.model_task_repo.insert_model_task(new_task)

        return {"task_uuid": uuid_str, "kubeflow_experiment_id": kubeflow_experiment_id}

    def optimize(self, optimizer_id: int, optimize_form: ReqOptimizeWithNameAndArgsBody):
        """
        최적화 작업
        Args:
            optimize_form: 최적화 폼
        Returns:
            task_info: 최적화 작업 정보
        """
        optimizer = self.optimizer_info_repo.get_optimizer_info_by_id(optimizer_id)
        if not optimizer:
            raise HTTPException(status_code=404, detail="Optimizer not found")

        # 사용할 도커 이미지 경로
        container_image: str = getattr(SETTINGS, f"{optimizer.optimizer_name.upper()}_IMG")
        if not container_image:
            raise HTTPException(status_code=500, detail="Container image not found")

        # 최적화 작업 정보
        task_info = OptimizationSetUp(
            model_name=optimize_form.model_name,
            optimize_name=optimizer.optimizer_name,
            docker_image_path=container_image,
            command=[
                "pipenv",
                "run",
                "python",
                "main.py",
            ],
            args=[f"--{key} {value}" for key, value in optimize_form.args.items()],
            env={
                "AWS_ACCESS_KEY_ID": SETTINGS.AWS_ACCESS_KEY_ID,
                "AWS_SECRET_ACCESS_KEY": SETTINGS.AWS_SECRET_ACCESS_KEY,
                "MLFLOW_TRACKING_URI": SETTINGS.MLFLOW_TRACKING_URL,
                "MLFLOW_S3_ENDPOINT_URL": SETTINGS.MLFLOW_S3_ENDPOINT_URL,
                "MLFLOW_HTTP_REQUEST_TIMEOUT": SETTINGS.MLFLOW_HTTP_REQUEST_TIMEOUT,
                "SERVER_UUID": get_uuid_str(),
                "SERVER_PATH": f"{SETTINGS.SERVER_URL}/api/v1/tasks",
                "RUN_ID": optimize_form.saved_model_run_id,
                "MODEL_PATH": optimize_form.saved_model_path,
                "MODEL_NAME": optimize_form.model_name,
            },
            accelerator_type=optimizer.accelerator,
        )
        # NPU 최적화 작업 시 환경변수 추가
        if optimizer.optimizer_name == SupportOptimize.NPU.value \
                and not optimize_form.args.get("target_npu_name"):
            task_info.env["TARGET_NPU_NAME"] = SETTINGS.TARGET_NPU_NAME

        result = self.run_optimize_task(task_info)

        return self._save_task_info(task_info, result)
