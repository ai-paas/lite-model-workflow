from sqlalchemy import String
from sqlalchemy.orm import MappedColumn, mapped_column

from app.core.db.models.base import Base, FullTimestamp
from app.schemas.services.model_task import ModelTaskDetailSchema, ModelTaskSchema


# TDOO: 컬럼 분리 및 관계 설정
class ModelTask(Base, FullTimestamp):
    __tablename__ = "model_tasks"

    # 모델 저장 요청별 uuid
    # TODO: 모델 저장시 바로 가져올수 있으면 지우기
    task_uuid: MappedColumn[str] = mapped_column(String, nullable=False)

    # 요청 작업 성공 여부 (기본값 False)
    progress_status: MappedColumn[bool] = mapped_column(default=False, nullable=False)

    # 모델 이름
    # 엥 모델 id 가 맞지 않나요?
    model_name: MappedColumn[str] = mapped_column(String, nullable=False)

    # 경량화 방식
    task_type: MappedColumn[str] = mapped_column(String, nullable=False)

    # 최적화된 모델 경로 (mlflow 작업 완료 후 rest api로 요청)
    model_path_output: MappedColumn[str | None] = mapped_column(
        String, nullable=True, default=None
    )

    # kubeflow experiment id
    kubeflow_experiment_id: MappedColumn[str] = mapped_column(String, nullable=False)

    @classmethod
    def from_schema(cls, task_info: ModelTaskSchema) -> "ModelTask":
        return cls(
            model_name=task_info.model_name,
            progress_status=task_info.progress_status,
            model_path_output=task_info.model_path_output,
            kubeflow_experiment_id=task_info.kubeflow_experiment_id,
            task_uuid=task_info.task_uuid,
            task_type=task_info.task_type,
        )

    def to_schema(self) -> ModelTaskSchema:
        return ModelTaskSchema(
            model_name=self.model_name,
            progress_status=self.progress_status,
            model_path_output=self.model_path_output,
            kubeflow_experiment_id=self.kubeflow_experiment_id,
            task_uuid=self.task_uuid,
            task_type=self.task_type,
        )
    
    def to_detail_schema(self) -> ModelTaskDetailSchema:
        return ModelTaskDetailSchema(
            model_name=self.model_name,
            progress_status=self.progress_status,
            model_path_output=self.model_path_output,
            kubeflow_experiment_id=self.kubeflow_experiment_id,
            task_uuid=self.task_uuid,
            task_type=self.task_type,
        )
