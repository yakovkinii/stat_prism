from src.modules.correlation.correlation import Correlation
from src.modules.correlation.correlation_result import CorrelationResult, CorrelationStudyConfig
from src.modules.registry import ModuleRegistry


def inject_classes_to_module_registry():
    ModuleRegistry.CORRELATION.value.ui_class = Correlation
    ModuleRegistry.CORRELATION.value.result_class = CorrelationResult
    ModuleRegistry.CORRELATION.value.config_class = CorrelationStudyConfig
