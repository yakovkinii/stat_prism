#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Dict, Union

from src.side_area_panel.modules.common.result.base_result import BaseResult
from src.side_area_panel.modules.contingency.result import ContingencyResult
from src.side_area_panel.modules.correlation.result import CorrelationResult
from src.side_area_panel.modules.descriptive.result import DescriptiveResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import (
    CalculateScaleResult,
)
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import (
    InvertScaleResult,
)
from src.side_area_panel.modules.dp_process_column.dp_process_column_result import (
    ProcessColumnResult,
)
from src.side_area_panel.modules.exploratory_factor_analysis.result import (
    FactorAnalysisResult,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import (
    MeanComparisonResult,
)
from src.side_area_panel.modules.raw_data.result import RawDataResult
from src.side_area_panel.modules.regression.result import RegressionResult
from src.side_area_panel.modules.reliability.result import ReliabilityResult

RESULTS: Dict[
    int,
    Union[
        BaseResult,
        CorrelationResult,
        DescriptiveResult,
        MeanComparisonResult,
        ReliabilityResult,
        RegressionResult,
        ContingencyResult,
        RawDataResult,
        FactorAnalysisResult,
        CalculateScaleResult,
        ProcessColumnResult,
        InvertScaleResult,
    ],
] = {}


def get_unique_result_id():
    return max(RESULTS.keys()) + 1 if len(RESULTS) > 0 else 1
