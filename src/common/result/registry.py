from typing import Dict, Union

from src.common.result.classes.base_result import BaseResult
from src.modules.correlation.result import CorrelationResult
from src.modules.descriptive.result import DescriptiveResult
from src.modules.mean_comparison.result import MeanComparisonResult

RESULTS: Dict[
    int,
    Union[
        BaseResult,
        CorrelationResult,
        DescriptiveResult,
        MeanComparisonResult,
    ],
] = {}
