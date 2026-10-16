from enum import Enum

from app.config.enums import (
    OptimizerAffinityFlag,
    SupportNPUNodeSelector,
    SupportNPUToleration,
    SupportOptimize,
    SupportTensorRTNodeSelector,
    SupportTensorRTToleration,
)


class SupportTolerationFactory:
    @staticmethod
    def get_toleration_by_optimizer(optimizer: SupportOptimize) -> Enum:
        if optimizer == SupportOptimize.NPU and OptimizerAffinityFlag.NPU_TOLERATION_FLAG.value:
            return SupportNPUToleration
        if optimizer == SupportOptimize.TENSORRT and OptimizerAffinityFlag.TENSORRT_TOLERATION_FLAG.value:
            return SupportTensorRTToleration
        return None

class SupportNodeSelectorFactory:
    @staticmethod
    def get_node_selector_by_optimizer(optimizer: SupportOptimize) -> Enum:
        if optimizer == SupportOptimize.NPU and OptimizerAffinityFlag.NPU_NODE_SELECTOR_FLAG.value:
            return SupportNPUNodeSelector
        if optimizer == SupportOptimize.TENSORRT and OptimizerAffinityFlag.TENSORRT_NODE_SELECTOR_FLAG.value:
            return SupportTensorRTNodeSelector
        return None
