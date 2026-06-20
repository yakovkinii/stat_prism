#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Dict, Union

from src.side_area_panel.modules.common.result.base_result import BaseResult
from src.side_area_panel.modules.contingency.contingency_result import ContingencyResult
from src.side_area_panel.modules.correlation.correlation_result import CorrelationResult
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
)
from src.side_area_panel.modules.dp_filter.dp_filter_result import (
    FilterDataResult,
)
from src.side_area_panel.modules.dp_impute.dp_impute_result import ImputeResult
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult
from src.side_area_panel.modules.dp_formula.dp_formula_result import FormulaResult
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_result import BootstrapResult
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import (
    InvertScaleResult,
)
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_result import (
    PreprocessResult,
)
from src.side_area_panel.modules.dp_group.dp_group_result import (
    GroupValuesResult,
)
from src.side_area_panel.modules.dp_select_id.dp_select_id_result import (
    SelectIDResult,
)
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import (
    OutliersResult,
)
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    FactorAnalysisResult,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
)
from src.side_area_panel.modules.paired.paired_result import PairedResult
from src.side_area_panel.modules.power_analysis.power_analysis_result import (
    PowerAnalysisResult,
)
from src.side_area_panel.modules.raw_data.raw_data_result import RawDataResult
from src.side_area_panel.modules.regression.regression_result import RegressionResult
from src.side_area_panel.modules.reliability.reliability_result import ReliabilityResult

RESULTS: Dict[
    int,
    Union[
        BaseResult,
        CorrelationResult,
        DescriptiveResult,
        MeanComparisonResult,
        PairedResult,
        ReliabilityResult,
        RegressionResult,
        ContingencyResult,
        RawDataResult,
        FactorAnalysisResult,
        CalculateScaleResult,
        InvertScaleResult,
        FilterDataResult,
        PreprocessResult,
        GroupValuesResult,
        SelectIDResult,
        OutliersResult,
        PowerAnalysisResult,
        ImputeResult,
        TransformResult,
        FormulaResult,
        BootstrapResult,
    ],
] = {}


def get_unique_result_id():
    return max(RESULTS.keys()) + 1 if len(RESULTS) > 0 else 1
