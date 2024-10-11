from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig
from src.modules.correlation.ui import Correlation
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.descriptive.ui import Descriptive
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.modules.mean_comparison.ui import MeanComparison
from src.modules.registry import ModuleRegistry


def inject_classes_to_module_registry():
    ModuleRegistry.CORRELATION.value.ui_class = Correlation
    ModuleRegistry.CORRELATION.value.result_class = CorrelationResult
    ModuleRegistry.CORRELATION.value.config_class = CorrelationStudyConfig

    ModuleRegistry.DESCRIPTIVE.value.ui_class = Descriptive
    ModuleRegistry.DESCRIPTIVE.value.result_class = DescriptiveResult
    ModuleRegistry.DESCRIPTIVE.value.config_class = DescriptiveStudyConfig

    ModuleRegistry.MEAN_COMPARISON.value.ui_class = MeanComparison
    ModuleRegistry.MEAN_COMPARISON.value.result_class = MeanComparisonResult
    ModuleRegistry.MEAN_COMPARISON.value.config_class = MeanComparisonStudyConfig
