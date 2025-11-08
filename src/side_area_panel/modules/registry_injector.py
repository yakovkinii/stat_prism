#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.side_area_panel.modules.calculate_scale.calculate_scale_ui import (
    CalculateScale,
)
from src.side_area_panel.modules.calculate_scale.result import (
    CalculateScaleResult,
    CalculateScaleStudyConfig,
)
from src.side_area_panel.modules.cluster_analysis.cluster_analysis_ui import (
    ClusterAnalysis,
)
from src.side_area_panel.modules.cluster_analysis.result import (
    ClusterAnalysisConfig,
    ClusterAnalysisResult,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.factor_analysis_ui import (
    ConfirmatoryFactorAnalysis,
)
from src.side_area_panel.modules.confirmatory_factor_analysis.result import (
    CFAResult,
    CFAStudyConfig,
)
from src.side_area_panel.modules.contingency.contingency_ui import Contingency
from src.side_area_panel.modules.contingency.result import (
    ContingencyResult,
    ContingencyStudyConfig,
)
from src.side_area_panel.modules.correlation.correlation_ui import Correlation
from src.side_area_panel.modules.correlation.result import (
    CorrelationResult,
    CorrelationStudyConfig,
)
from src.side_area_panel.modules.descriptive.descriptive_ui import Descriptive
from src.side_area_panel.modules.descriptive.result import (
    DescriptiveResult,
    DescriptiveStudyConfig,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_main import (
    dp_process_column_main,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_result import (
    ProcessColumnResult,
    ProcessColumnStudyConfig,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_ui import (
    DpProcessColumn,
)
from src.side_area_panel.modules.exploratory_factor_analysis.factor_analysis_ui import (
    FactorAnalysis,
)
from src.side_area_panel.modules.exploratory_factor_analysis.result import (
    FactorAnalysisResult,
    FactorAnalysisStudyConfig,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_ui import (
    MeanComparison,
)
from src.side_area_panel.modules.mean_comparison.result import (
    MeanComparisonResult,
    MeanComparisonStudyConfig,
)
from src.side_area_panel.modules.raw_data.raw_data_ui import RawData
from src.side_area_panel.modules.raw_data.result import (
    RawDataResult,
    RawDataStudyConfig,
)
from src.side_area_panel.modules.registry import ModuleRegistry
from src.side_area_panel.modules.regression.regression_ui import Regression
from src.side_area_panel.modules.regression.result import (
    RegressionResult,
    RegressionStudyConfig,
)
from src.side_area_panel.modules.reliability.result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)
from src.side_area_panel.modules.reliability.ui import Reliability
from src.side_area_panel.modules.rename_columns.rename_columns_ui import RenameColumns
from src.side_area_panel.modules.rename_columns.result import (
    RenameColumnsResult,
    RenameColumnsStudyConfig,
)


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

    ModuleRegistry.RENAME_COLUMNS.value.ui_class = RenameColumns
    ModuleRegistry.RENAME_COLUMNS.value.result_class = RenameColumnsResult
    ModuleRegistry.RENAME_COLUMNS.value.config_class = RenameColumnsStudyConfig

    ModuleRegistry.CALCULATE_SCALE.value.ui_class = CalculateScale
    ModuleRegistry.CALCULATE_SCALE.value.result_class = CalculateScaleResult
    ModuleRegistry.CALCULATE_SCALE.value.config_class = CalculateScaleStudyConfig

    ModuleRegistry.DP_PROCESS_COLUMN.value.ui_class = DpProcessColumn
    ModuleRegistry.DP_PROCESS_COLUMN.value.result_class = ProcessColumnResult
    ModuleRegistry.DP_PROCESS_COLUMN.value.config_class = ProcessColumnStudyConfig
    ModuleRegistry.DP_PROCESS_COLUMN.value.main_function = dp_process_column_main
