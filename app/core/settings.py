from enum import Enum
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

current_directory = Path(__file__).parent
root_directory = Path(__file__).parent.parent.parent
dotenv_path = root_directory / ".env"
load_dotenv(dotenv_path=dotenv_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,  # 대소문자 구분 허용
        env_file=".env",  # settings env file name
        env_file_encoding="utf-8",  # setting env file encoding
    )
    # 디버그 모드
    DEBUG: bool = False

    DB_TYPE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # kubeflow 관련 설정
    KUBEFLOW_ENDPOINT: str
    KUBEFLOW_USERNAME: str
    KUBEFLOW_PASSWORD: str
    KUBEFLOW_NAMESPACE: str

    SERVER_URL: str

    # mlflow 관련 설정
    MLFLOW_TRACKING_URL: str
    MLFLOW_S3_ENDPOINT_URL: str

    # Model Image
    BERT_TRT: str
    BERT_OPENVINO: str

    # Owlv2
    OWLV2_PTQ: str

    # DETR_RESNET50
    DETR_RESNET50: str

    # Pruning
    PRUNING_IMG: str

    # TENSORRT
    TENSORRT_IMG: str

    # OpenVINO
    OPENVINO_IMG: str

    # SKLEARN_ONNX
    SKLEARN_ONNX_IMG: str

    # NPU
    NPU_IMG: str
    TARGET_NPU_NAME: str

    # TPU
    TPU_IMG: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    MLFLOW_HTTP_REQUEST_TIMEOUT: str

    NPU_NODE_SELECTOR_KEY: str
    NPU_NODE_SELECTOR_VALUE: str

    NPU_TOLERATION_KEY: str
    NPU_TOLERATION_VALUE: str
    NPU_TOLERATION_EFFECT: str
    NPU_TOLERATION_OPERATOR: str

    @property
    def get_db_uri(self) -> str:
        """Environment variables로부터 DB 정보를 받아와 URI를 반환"""
        return f"{self.DB_TYPE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache
def get_settings():
    return Settings()

@lru_cache
def get_common_env():
    SETTINGS = get_settings()
    return {
        "MLFLOW_TRACKING_URL": SETTINGS.MLFLOW_TRACKING_URL,
        "MLFLOW_S3_ENDPOINT_URL": SETTINGS.MLFLOW_S3_ENDPOINT_URL,
        "AWS_ACCESS_KEY_ID": SETTINGS.AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": SETTINGS.AWS_SECRET_ACCESS_KEY,
        "MLFLOW_HTTP_REQUEST_TIMEOUT": SETTINGS.MLFLOW_HTTP_REQUEST_TIMEOUT,
        "SERVER_PATH": f"{SETTINGS.SERVER_URL}/api/v1/tasks",
    }
