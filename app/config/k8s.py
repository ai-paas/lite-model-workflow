from enum import Enum

from app.config.enums import (
    SupportNPUNodeSelector, 
    SupportNPUToleration, 
    SupportOptimize,
)

class SupportTolerationFactory:
    @staticmethod
    def get_toleration_by_optimizer(optimizer: SupportOptimize) -> Enum:
        if optimizer == SupportOptimize.NPU:
            return SupportNPUToleration
        return None

class SupportNodeSelectorFactory:
    @staticmethod
    def get_node_selector_by_optimizer(optimizer: SupportOptimize) -> Enum:
        if optimizer == SupportOptimize.NPU:
            return SupportNPUNodeSelector
        return None
