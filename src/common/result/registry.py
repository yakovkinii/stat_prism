#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import Dict, Union

from src.common.result.classes.base_result import BaseResult
from src.modules.contingency.result import ContingencyResult
from src.modules.correlation.result import CorrelationResult
from src.modules.descriptive.result import DescriptiveResult
from src.modules.mean_comparison.result import MeanComparisonResult
from src.modules.regression.result import RegressionResult
from src.modules.reliability.result import ReliabilityResult
from src.modules.v2.result import V2Result

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
        V2Result,
    ],
] = {}
