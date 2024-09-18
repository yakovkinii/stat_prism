from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig
from src.modules.correlation.ui import Correlation
from src.modules.cross_correlation.result import CrossCorrelationResult, CrossCorrelationStudyConfig
from src.modules.cross_correlation.ui import CrossCorrelation
from src.modules.registry import ModuleRegistry


def inject_classes_to_module_registry():
    ModuleRegistry.CORRELATION.value.ui_class = Correlation
    ModuleRegistry.CORRELATION.value.result_class = CorrelationResult
    ModuleRegistry.CORRELATION.value.config_class = CorrelationStudyConfig

    ModuleRegistry.CROSS_CORRELATION.value.ui_class = CrossCorrelation
    ModuleRegistry.CROSS_CORRELATION.value.result_class = CrossCorrelationResult
    ModuleRegistry.CROSS_CORRELATION.value.config_class = CrossCorrelationStudyConfig
