from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig
from src.modules.correlation.ui import Correlation
from src.modules.cross_correlation.result import CrossCorrelationResult, CrossCorrelationStudyConfig
from src.modules.cross_correlation.ui import CrossCorrelation
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.descriptive.ui import Descriptive
from src.modules.registry import ModuleRegistry
from src.modules.t_test.result import TTestResult, TTestStudyConfig
from src.modules.t_test.ui import TTest


def inject_classes_to_module_registry():
    ModuleRegistry.CORRELATION.value.ui_class = Correlation
    ModuleRegistry.CORRELATION.value.result_class = CorrelationResult
    ModuleRegistry.CORRELATION.value.config_class = CorrelationStudyConfig

    ModuleRegistry.CROSS_CORRELATION.value.ui_class = CrossCorrelation
    ModuleRegistry.CROSS_CORRELATION.value.result_class = CrossCorrelationResult
    ModuleRegistry.CROSS_CORRELATION.value.config_class = CrossCorrelationStudyConfig

    ModuleRegistry.T_TEST.value.ui_class = TTest
    ModuleRegistry.T_TEST.value.result_class = TTestResult
    ModuleRegistry.T_TEST.value.config_class = TTestStudyConfig

    ModuleRegistry.DESCRIPTIVE.value.ui_class = Descriptive
    ModuleRegistry.DESCRIPTIVE.value.result_class = DescriptiveResult
    ModuleRegistry.DESCRIPTIVE.value.config_class = DescriptiveStudyConfig
