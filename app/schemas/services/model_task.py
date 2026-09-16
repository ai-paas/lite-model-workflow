from pydantic import BaseModel
from pydantic.fields import computed_field

from app.utils.mlflow import get_mlflow_experiment_id_from_path, get_mlflow_run_id_from_path


class ModelTaskSchema(BaseModel):
    model_name: str
    progress_status: bool = False
    model_path_output: str | None = None
    kubeflow_experiment_id: str
    task_uuid: str
    task_type: str


class ModelTaskDetailSchema(ModelTaskSchema):
    @computed_field
    @property
    def mlflow_run_id(self) -> str | None:
        return get_mlflow_run_id_from_path(self.model_path_output)

    @computed_field
    @property
    def mlflow_experiment_id(self) -> str | None:
        return get_mlflow_experiment_id_from_path(self.model_path_output)
