#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_ui import (
    ClusterAnalysis,
)
from src.side_area_panel.modules.cluster_analysis.main import (
    recalculate_cluster_analysis_study,
)
from src.side_area_panel.modules.cluster_analysis.result import (
    ClusterAnalysisConfig,
    ClusterAnalysisResult,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.factor_analysis_ui import (
    ConfirmatoryFactorAnalysis,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.main import (
    recalculate_cfa_study,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.result import (
    CFAResult,
    CFAStudyConfig,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_main import (
    dp_calculate_scale_main,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
    CalculateScaleStudyConfig,
)
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_ui import (
    CalculateScale,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_main import (
    dp_invert_scale_main,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import (
    InvertScaleResult,
    InvertScaleStudyConfig,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_ui import (
    InvertScale,
)
from src.side_area_panel.modules.dp_filter.dp_filter_main import dp_filter_main
from src.side_area_panel.modules.dp_filter.dp_filter_result import (
    FilterDataResult,
    FilterDataStudyConfig,
)
from src.side_area_panel.modules.dp_filter.dp_filter_ui import FilterData
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_main import dp_preprocess_main
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_result import (
    PreprocessResult,
    PreprocessStudyConfig,
)
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_ui import Preprocess
from src.side_area_panel.modules.dp_group.dp_group_main import dp_group_main
from src.side_area_panel.modules.dp_group.dp_group_result import (
    GroupValuesResult,
    GroupValuesStudyConfig,
)
from src.side_area_panel.modules.dp_group.dp_group_ui import GroupValues
from src.side_area_panel.modules.dp_outliers.dp_outliers_main import dp_outliers_main
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import (
    OutliersResult,
    OutliersStudyConfig,
)
from src.side_area_panel.modules.dp_outliers.dp_outliers_ui import Outliers
from src.side_area_panel.modules.contingency.contingency_ui import Contingency
from src.side_area_panel.modules.contingency.main import recalculate_contingency_study
from src.side_area_panel.modules.contingency.result import (
    ContingencyResult,
    ContingencyStudyConfig,
)
from src.side_area_panel.modules.correlation.correlation_ui import Correlation
from src.side_area_panel.modules.correlation.main import recalculate_correlation_study
from src.side_area_panel.modules.correlation.result import (
    CorrelationResult,
    CorrelationStudyConfig,
)
from src.side_area_panel.modules.descriptive.descriptive_main import (
    recalculate_descriptive_study,
)
from src.side_area_panel.modules.descriptive.descriptive_ui import Descriptive
from src.side_area_panel.modules.descriptive.result import (
    DescriptiveResult,
    DescriptiveStudyConfig,
)
from src.side_area_panel.modules.exploratory_factor_analysis.factor_analysis_ui import (
    FactorAnalysis,
)
from src.side_area_panel.modules.exploratory_factor_analysis.main import (
    recalculate_factor_analysis_study,
)
from src.side_area_panel.modules.exploratory_factor_analysis.result import (
    FactorAnalysisResult,
    FactorAnalysisStudyConfig,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_main import (
    recalculate_mean_comparison_study,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
    MeanComparisonStudyConfig,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_ui import (
    MeanComparison,
)
from src.side_area_panel.modules.raw_data.raw_data_ui import RawData
from src.side_area_panel.modules.raw_data.result import (
    RawDataResult,
    RawDataStudyConfig,
)
from src.side_area_panel.modules.registry import ModuleRegistry
from src.side_area_panel.modules.regression.main import recalculate_regression_study
from src.side_area_panel.modules.regression.regression_ui import Regression
from src.side_area_panel.modules.regression.result import (
    RegressionResult,
    RegressionStudyConfig,
)
from src.side_area_panel.modules.reliability.main import recalculate_reliability_study
from src.side_area_panel.modules.reliability.reliability_ui import Reliability
from src.side_area_panel.modules.reliability.result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)


def inject_classes_to_module_registry():
    ModuleRegistry.RAW_DATA.value.ui_class = RawData
    ModuleRegistry.RAW_DATA.value.result_class = RawDataResult
    ModuleRegistry.RAW_DATA.value.config_class = RawDataStudyConfig

    ModuleRegistry.CORRELATION.value.ui_class = Correlation
    ModuleRegistry.CORRELATION.value.result_class = CorrelationResult
    ModuleRegistry.CORRELATION.value.config_class = CorrelationStudyConfig
    ModuleRegistry.CORRELATION.value.main_function = recalculate_correlation_study

    ModuleRegistry.DESCRIPTIVE.value.ui_class = Descriptive
    ModuleRegistry.DESCRIPTIVE.value.result_class = DescriptiveResult
    ModuleRegistry.DESCRIPTIVE.value.config_class = DescriptiveStudyConfig
    ModuleRegistry.DESCRIPTIVE.value.main_function = recalculate_descriptive_study

    ModuleRegistry.MEAN_COMPARISON.value.ui_class = MeanComparison
    ModuleRegistry.MEAN_COMPARISON.value.result_class = MeanComparisonResult
    ModuleRegistry.MEAN_COMPARISON.value.config_class = MeanComparisonStudyConfig
    ModuleRegistry.MEAN_COMPARISON.value.main_function = recalculate_mean_comparison_study

    ModuleRegistry.RELIABILITY.value.ui_class = Reliability
    ModuleRegistry.RELIABILITY.value.result_class = ReliabilityResult
    ModuleRegistry.RELIABILITY.value.config_class = ReliabilityStudyConfig
    ModuleRegistry.RELIABILITY.value.main_function = recalculate_reliability_study

    ModuleRegistry.REGRESSION.value.ui_class = Regression
    ModuleRegistry.REGRESSION.value.result_class = RegressionResult
    ModuleRegistry.REGRESSION.value.config_class = RegressionStudyConfig
    ModuleRegistry.REGRESSION.value.main_function = recalculate_regression_study

    ModuleRegistry.CONTINGENCY.value.ui_class = Contingency
    ModuleRegistry.CONTINGENCY.value.result_class = ContingencyResult
    ModuleRegistry.CONTINGENCY.value.config_class = ContingencyStudyConfig
    ModuleRegistry.CONTINGENCY.value.main_function = recalculate_contingency_study

    ModuleRegistry.FACTOR_ANALYSIS.value.ui_class = FactorAnalysis
    ModuleRegistry.FACTOR_ANALYSIS.value.result_class = FactorAnalysisResult
    ModuleRegistry.FACTOR_ANALYSIS.value.config_class = FactorAnalysisStudyConfig
    ModuleRegistry.FACTOR_ANALYSIS.value.main_function = recalculate_factor_analysis_study

    ModuleRegistry.CFA.value.ui_class = ConfirmatoryFactorAnalysis
    ModuleRegistry.CFA.value.result_class = CFAResult
    ModuleRegistry.CFA.value.config_class = CFAStudyConfig
    ModuleRegistry.CFA.value.main_function = recalculate_cfa_study

    ModuleRegistry.CLUSTER_ANALYSIS.value.ui_class = ClusterAnalysis
    ModuleRegistry.CLUSTER_ANALYSIS.value.result_class = ClusterAnalysisResult
    ModuleRegistry.CLUSTER_ANALYSIS.value.config_class = ClusterAnalysisConfig
    ModuleRegistry.CLUSTER_ANALYSIS.value.main_function = recalculate_cluster_analysis_study

    ModuleRegistry.CALCULATE_SCALE.value.ui_class = CalculateScale
    ModuleRegistry.CALCULATE_SCALE.value.result_class = CalculateScaleResult
    ModuleRegistry.CALCULATE_SCALE.value.config_class = CalculateScaleStudyConfig
    ModuleRegistry.CALCULATE_SCALE.value.main_function = dp_calculate_scale_main

    ModuleRegistry.INVERT_SCALE.value.ui_class = InvertScale
    ModuleRegistry.INVERT_SCALE.value.result_class = InvertScaleResult
    ModuleRegistry.INVERT_SCALE.value.config_class = InvertScaleStudyConfig
    ModuleRegistry.INVERT_SCALE.value.main_function = dp_invert_scale_main

    ModuleRegistry.FILTER.value.ui_class = FilterData
    ModuleRegistry.FILTER.value.result_class = FilterDataResult
    ModuleRegistry.FILTER.value.config_class = FilterDataStudyConfig
    ModuleRegistry.FILTER.value.main_function = dp_filter_main

    ModuleRegistry.PREPROCESS.value.ui_class = Preprocess
    ModuleRegistry.PREPROCESS.value.result_class = PreprocessResult
    ModuleRegistry.PREPROCESS.value.config_class = PreprocessStudyConfig
    ModuleRegistry.PREPROCESS.value.main_function = dp_preprocess_main

    ModuleRegistry.GROUP_VALUES.value.ui_class = GroupValues
    ModuleRegistry.GROUP_VALUES.value.result_class = GroupValuesResult
    ModuleRegistry.GROUP_VALUES.value.config_class = GroupValuesStudyConfig
    ModuleRegistry.GROUP_VALUES.value.main_function = dp_group_main

    ModuleRegistry.OUTLIERS.value.ui_class = Outliers
    ModuleRegistry.OUTLIERS.value.result_class = OutliersResult
    ModuleRegistry.OUTLIERS.value.config_class = OutliersStudyConfig
    ModuleRegistry.OUTLIERS.value.main_function = dp_outliers_main
