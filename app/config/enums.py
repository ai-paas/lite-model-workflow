from enum import Enum

from app.core.settings import get_settings

SETTINGS = get_settings()


class ModelLiteMapper(Enum):
    """
    경량화 / 최적화 이미지 매핑
    """

    # Bert
    BERT_TRT = SETTINGS.BERT_TRT
    BERT_OPENVINO = SETTINGS.BERT_OPENVINO

    # Owlv2
    OWLV2_PTQ = SETTINGS.OWLV2_PTQ

    # DETR-Resnet50
    DETR_Resnet50 = SETTINGS.DETR_RESNET50


class SupportModel(Enum):
    """
    지원하는 모델
    """

    Bert = "bert"
    OwlV2 = "owlv2"
    DETR_Resnet50 = "detr-resnet50"


class SupportAccelerator(Enum):
    CPU = "cpu"
    GPU = "nvidia.com/gpu"
    NPU = "furiosa.ai/npu"


class SupportOptimize(Enum):
    """
    지원하는 최적화 / 경량화
    """

    PTQ = "ptq"
    PRUNING = "pruning"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    SKLEARN_ONNX = "sklearn_onnx"
    NPU = "npu"
    TPU = "tpu"


class SupportOptimizerType(Enum):
    OPTIMIZE = "optimize"
    LIGHTWEIGHT = "lightweight"

    @classmethod
    def to_regex_pattern(cls) -> str:
        content = "|".join([opt.value for opt in cls])
        return rf"^({content})$"


class SupportNPUToleration(Enum):
    KEY = SETTINGS.NPU_NODE_SELECTOR_KEY
    OPERATOR = SETTINGS.NPU_TOLERATION_OPERATOR
    VALUE = SETTINGS.NPU_TOLERATION_VALUE
    EFFECT = SETTINGS.NPU_TOLERATION_EFFECT

class SupportNPUNodeSelector(Enum):
    KEY = SETTINGS.NPU_NODE_SELECTOR_KEY
    VALUE = SETTINGS.NPU_NODE_SELECTOR_VALUE
