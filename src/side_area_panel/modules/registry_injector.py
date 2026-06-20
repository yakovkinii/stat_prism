#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_ui import (
    ClusterAnalysis,
)
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_main import (
    recalculate_cluster_analysis_study,
)
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_result import (
    ClusterAnalysisConfig,
    ClusterAnalysisResult,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.factor_analysis_ui import (
    ConfirmatoryFactorAnalysis,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_main import (
    recalculate_cfa_study,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.confirmatory_factor_analysis_result import (
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
from src.side_area_panel.modules.dp_impute.dp_impute_main import dp_impute_main
from src.side_area_panel.modules.dp_impute.dp_impute_result import (
    ImputeResult,
    ImputeStudyConfig,
)
from src.side_area_panel.modules.dp_impute.dp_impute_ui import Impute
from src.side_area_panel.modules.dp_transform.dp_transform_main import dp_transform_main
from src.side_area_panel.modules.dp_transform.dp_transform_result import (
    TransformResult,
    TransformStudyConfig,
)
from src.side_area_panel.modules.dp_transform.dp_transform_ui import Transform
from src.side_area_panel.modules.dp_formula.dp_formula_main import dp_formula_main
from src.side_area_panel.modules.dp_formula.dp_formula_result import (
    FormulaResult,
    FormulaStudyConfig,
)
from src.side_area_panel.modules.dp_formula.dp_formula_ui import Formula
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_main import dp_bootstrap_main
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_result import (
    BootstrapResult,
    BootstrapStudyConfig,
)
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_ui import Bootstrap
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_main import (
    dp_split_multiselect_main,
)
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_result import (
    SplitMultiSelectResult,
    SplitMultiSelectStudyConfig,
)
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_ui import SplitMultiSelect
from src.side_area_panel.modules.dp_onehot.dp_onehot_main import dp_onehot_main
from src.side_area_panel.modules.dp_onehot.dp_onehot_result import (
    OneHotResult,
    OneHotStudyConfig,
)
from src.side_area_panel.modules.dp_onehot.dp_onehot_ui import OneHot
from src.side_area_panel.modules.multiple_response.multiple_response_ui import MultipleResponse
from src.side_area_panel.modules.multiple_response.multiple_response_main import (
    recalculate_multiple_response_study,
)
from src.side_area_panel.modules.multiple_response.multiple_response_result import (
    MultipleResponseResult,
    MultipleResponseStudyConfig,
)
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
from src.side_area_panel.modules.dp_select_id.dp_select_id_main import dp_select_id_main
from src.side_area_panel.modules.dp_select_id.dp_select_id_result import (
    SelectIDResult,
    SelectIDStudyConfig,
)
from src.side_area_panel.modules.dp_select_id.dp_select_id_ui import SelectID
from src.side_area_panel.modules.dp_outliers.dp_outliers_main import dp_outliers_main
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import (
    OutliersResult,
    OutliersStudyConfig,
)
from src.side_area_panel.modules.dp_outliers.dp_outliers_ui import Outliers
from src.side_area_panel.modules.dp_grouped_outliers.dp_grouped_outliers_main import (
    dp_grouped_outliers_main,
)
from src.side_area_panel.modules.dp_grouped_outliers.dp_grouped_outliers_result import (
    GroupedOutliersResult,
    GroupedOutliersStudyConfig,
)
from src.side_area_panel.modules.dp_grouped_outliers.dp_grouped_outliers_ui import GroupedOutliers
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_main import dp_2d_outliers_main
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_result import (
    TwoDOutliersResult,
    TwoDOutliersStudyConfig,
)
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_ui import TwoDOutliers
from src.side_area_panel.modules.contingency.contingency_ui import Contingency
from src.side_area_panel.modules.contingency.contingency_main import recalculate_contingency_study
from src.side_area_panel.modules.contingency.contingency_result import (
    ContingencyResult,
    ContingencyStudyConfig,
)
from src.side_area_panel.modules.correlation.correlation_ui import Correlation
from src.side_area_panel.modules.correlation.correlation_main import recalculate_correlation_study
from src.side_area_panel.modules.correlation.correlation_result import (
    CorrelationResult,
    CorrelationStudyConfig,
)
from src.side_area_panel.modules.descriptive.descriptive_main import (
    recalculate_descriptive_study,
)
from src.side_area_panel.modules.descriptive.descriptive_ui import Descriptive
from src.side_area_panel.modules.descriptive.descriptive_result import (
    DescriptiveResult,
    DescriptiveStudyConfig,
)
from src.side_area_panel.modules.exploratory_factor_analysis.factor_analysis_ui import (
    FactorAnalysis,
)
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_main import (
    recalculate_factor_analysis_study,
)
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
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
from src.side_area_panel.modules.paired.paired_main import recalculate_paired_study
from src.side_area_panel.modules.paired.paired_result import (
    PairedResult,
    PairedStudyConfig,
)
from src.side_area_panel.modules.paired.paired_ui import Paired
from src.side_area_panel.modules.power_analysis.power_analysis_ui import PowerAnalysis
from src.side_area_panel.modules.power_analysis.power_analysis_main import (
    recalculate_power_analysis_study,
)
from src.side_area_panel.modules.power_analysis.power_analysis_result import (
    PowerAnalysisResult,
    PowerAnalysisStudyConfig,
)
from src.side_area_panel.modules.raw_data.raw_data_ui import RawData
from src.side_area_panel.modules.raw_data.raw_data_result import (
    RawDataResult,
    RawDataStudyConfig,
)
from src.side_area_panel.modules.registry import ModuleRegistry
from src.side_area_panel.modules.regression.regression_main import recalculate_regression_study
from src.side_area_panel.modules.regression.regression_ui import Regression
from src.side_area_panel.modules.regression.regression_result import (
    RegressionResult,
    RegressionStudyConfig,
)
from src.side_area_panel.modules.reliability.reliability_main import recalculate_reliability_study
from src.side_area_panel.modules.reliability.reliability_ui import Reliability
from src.side_area_panel.modules.reliability.reliability_result import (
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

    ModuleRegistry.PAIRED.value.ui_class = Paired
    ModuleRegistry.PAIRED.value.result_class = PairedResult
    ModuleRegistry.PAIRED.value.config_class = PairedStudyConfig
    ModuleRegistry.PAIRED.value.main_function = recalculate_paired_study

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

    ModuleRegistry.POWER_ANALYSIS.value.ui_class = PowerAnalysis
    ModuleRegistry.POWER_ANALYSIS.value.result_class = PowerAnalysisResult
    ModuleRegistry.POWER_ANALYSIS.value.config_class = PowerAnalysisStudyConfig
    ModuleRegistry.POWER_ANALYSIS.value.main_function = recalculate_power_analysis_study

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

    ModuleRegistry.IMPUTE.value.ui_class = Impute
    ModuleRegistry.IMPUTE.value.result_class = ImputeResult
    ModuleRegistry.IMPUTE.value.config_class = ImputeStudyConfig
    ModuleRegistry.IMPUTE.value.main_function = dp_impute_main

    ModuleRegistry.TRANSFORM.value.ui_class = Transform
    ModuleRegistry.TRANSFORM.value.result_class = TransformResult
    ModuleRegistry.TRANSFORM.value.config_class = TransformStudyConfig
    ModuleRegistry.TRANSFORM.value.main_function = dp_transform_main

    ModuleRegistry.FORMULA.value.ui_class = Formula
    ModuleRegistry.FORMULA.value.result_class = FormulaResult
    ModuleRegistry.FORMULA.value.config_class = FormulaStudyConfig
    ModuleRegistry.FORMULA.value.main_function = dp_formula_main

    ModuleRegistry.BOOTSTRAP.value.ui_class = Bootstrap
    ModuleRegistry.BOOTSTRAP.value.result_class = BootstrapResult
    ModuleRegistry.BOOTSTRAP.value.config_class = BootstrapStudyConfig
    ModuleRegistry.BOOTSTRAP.value.main_function = dp_bootstrap_main

    ModuleRegistry.SPLIT_MULTISELECT.value.ui_class = SplitMultiSelect
    ModuleRegistry.SPLIT_MULTISELECT.value.result_class = SplitMultiSelectResult
    ModuleRegistry.SPLIT_MULTISELECT.value.config_class = SplitMultiSelectStudyConfig
    ModuleRegistry.SPLIT_MULTISELECT.value.main_function = dp_split_multiselect_main

    ModuleRegistry.ONE_HOT.value.ui_class = OneHot
    ModuleRegistry.ONE_HOT.value.result_class = OneHotResult
    ModuleRegistry.ONE_HOT.value.config_class = OneHotStudyConfig
    ModuleRegistry.ONE_HOT.value.main_function = dp_onehot_main

    ModuleRegistry.MULTIPLE_RESPONSE.value.ui_class = MultipleResponse
    ModuleRegistry.MULTIPLE_RESPONSE.value.result_class = MultipleResponseResult
    ModuleRegistry.MULTIPLE_RESPONSE.value.config_class = MultipleResponseStudyConfig
    ModuleRegistry.MULTIPLE_RESPONSE.value.main_function = recalculate_multiple_response_study

    ModuleRegistry.PREPROCESS.value.ui_class = Preprocess
    ModuleRegistry.PREPROCESS.value.result_class = PreprocessResult
    ModuleRegistry.PREPROCESS.value.config_class = PreprocessStudyConfig
    ModuleRegistry.PREPROCESS.value.main_function = dp_preprocess_main

    ModuleRegistry.GROUP_VALUES.value.ui_class = GroupValues
    ModuleRegistry.GROUP_VALUES.value.result_class = GroupValuesResult
    ModuleRegistry.GROUP_VALUES.value.config_class = GroupValuesStudyConfig
    ModuleRegistry.GROUP_VALUES.value.main_function = dp_group_main

    ModuleRegistry.SELECT_ID.value.ui_class = SelectID
    ModuleRegistry.SELECT_ID.value.result_class = SelectIDResult
    ModuleRegistry.SELECT_ID.value.config_class = SelectIDStudyConfig
    ModuleRegistry.SELECT_ID.value.main_function = dp_select_id_main

    ModuleRegistry.OUTLIERS.value.ui_class = Outliers
    ModuleRegistry.OUTLIERS.value.result_class = OutliersResult
    ModuleRegistry.OUTLIERS.value.config_class = OutliersStudyConfig
    ModuleRegistry.OUTLIERS.value.main_function = dp_outliers_main

    ModuleRegistry.GROUPED_OUTLIERS.value.ui_class = GroupedOutliers
    ModuleRegistry.GROUPED_OUTLIERS.value.result_class = GroupedOutliersResult
    ModuleRegistry.GROUPED_OUTLIERS.value.config_class = GroupedOutliersStudyConfig
    ModuleRegistry.GROUPED_OUTLIERS.value.main_function = dp_grouped_outliers_main

    ModuleRegistry.TWO_D_OUTLIERS.value.ui_class = TwoDOutliers
    ModuleRegistry.TWO_D_OUTLIERS.value.result_class = TwoDOutliersResult
    ModuleRegistry.TWO_D_OUTLIERS.value.config_class = TwoDOutliersStudyConfig
    ModuleRegistry.TWO_D_OUTLIERS.value.main_function = dp_2d_outliers_main
