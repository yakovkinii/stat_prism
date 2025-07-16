#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from src.modules.contingency.result import ContingencyResult, ContingencyStudyConfig
from src.modules.contingency.ui import Contingency
from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig
from src.modules.correlation.ui import Correlation
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.descriptive.ui import Descriptive
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.modules.mean_comparison.ui import MeanComparison
from src.modules.registry import ModuleRegistry
from src.modules.regression.result import RegressionResult, RegressionStudyConfig
from src.modules.regression.ui import Regression
from src.modules.reliability.result import ReliabilityResult, ReliabilityStudyConfig
from src.modules.reliability.ui import Reliability


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

    ModuleRegistry.RELIABILITY.value.ui_class = Reliability
    ModuleRegistry.RELIABILITY.value.result_class = ReliabilityResult
    ModuleRegistry.RELIABILITY.value.config_class = ReliabilityStudyConfig

    ModuleRegistry.REGRESSION.value.ui_class = Regression
    ModuleRegistry.REGRESSION.value.result_class = RegressionResult
    ModuleRegistry.REGRESSION.value.config_class = RegressionStudyConfig

    ModuleRegistry.CONTINGENCY.value.ui_class = Contingency
    ModuleRegistry.CONTINGENCY.value.result_class = ContingencyResult
    ModuleRegistry.CONTINGENCY.value.config_class = ContingencyStudyConfig
