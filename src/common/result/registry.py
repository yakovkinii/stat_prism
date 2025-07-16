#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#
from typing import Dict, Union

from src.common.result.base_result import BaseResult
from src.modules.contingency.result import ContingencyResult
from src.modules.correlation.result import CorrelationResult
from src.modules.descriptive.result import DescriptiveResult
from src.modules.mean_comparison.result import MeanComparisonResult
from src.modules.regression.result import RegressionResult
from src.modules.reliability.result import ReliabilityResult

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
    ],
] = {}


def get_unique_result_id():
    return max(RESULTS.keys()) + 1 if len(RESULTS) > 0 else 1
