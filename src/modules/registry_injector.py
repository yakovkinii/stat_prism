#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.modules.exploratory_factor_analysis.factor_analysis_ui import FactorAnalysis
from src.modules.exploratory_factor_analysis.result import FactorAnalysisResult, FactorAnalysisStudyConfig



from src.modules.contingency.contingency_ui import Contingency
from src.modules.contingency.result import ContingencyResult, ContingencyStudyConfig
from src.modules.correlation.correlation_ui import Correlation
from src.modules.correlation.result import CorrelationResult, CorrelationStudyConfig
from src.modules.descriptive.descriptive_ui import Descriptive
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.mean_comparison.mean_comparison_ui import MeanComparison
from src.modules.mean_comparison.result import MeanComparisonResult, MeanComparisonStudyConfig
from src.modules.raw_data.raw_data_ui import RawData
from src.modules.raw_data.result import RawDataResult, RawDataStudyConfig
from src.modules.registry import ModuleRegistry
from src.modules.regression.regression_ui import Regression
from src.modules.regression.result import RegressionResult, RegressionStudyConfig
from src.modules.reliability.result import ReliabilityResult, ReliabilityStudyConfig
from src.modules.reliability.ui import Reliability
from src.modules.confirmatory_factor_analysis.factor_analysis_ui import ConfirmatoryFactorAnalysis
from src.modules.confirmatory_factor_analysis.result import CFAResult, CFAStudyConfig
from src.modules.cluster_analysis.cluster_analysis_ui import ClusterAnalysis
from src.modules.cluster_analysis.result import ClusterAnalysisResult, ClusterAnalysisConfig


def inject_classes_to_module_registry():
    ModuleRegistry.RAW_DATA.value.ui_class = RawData
    ModuleRegistry.RAW_DATA.value.result_class = RawDataResult
    ModuleRegistry.RAW_DATA.value.config_class = RawDataStudyConfig

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

    ModuleRegistry.FACTOR_ANALYSIS.value.ui_class = FactorAnalysis
    ModuleRegistry.FACTOR_ANALYSIS.value.result_class = FactorAnalysisResult
    ModuleRegistry.FACTOR_ANALYSIS.value.config_class = FactorAnalysisStudyConfig

    ModuleRegistry.CFA.value.ui_class = ConfirmatoryFactorAnalysis
    ModuleRegistry.CFA.value.result_class = CFAResult
    ModuleRegistry.CFA.value.config_class = CFAStudyConfig

    ModuleRegistry.CLUSTER_ANALYSIS.value.ui_class = ClusterAnalysis
    ModuleRegistry.CLUSTER_ANALYSIS.value.result_class = ClusterAnalysisResult
    ModuleRegistry.CLUSTER_ANALYSIS.value.config_class = ClusterAnalysisConfig
