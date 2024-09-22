from typing import Dict, Union

from src.common.result.classes.base_result import BaseResult
from src.modules.correlation.result import CorrelationResult
from src.modules.cross_correlation.result import CrossCorrelationResult
from src.modules.descriptive.result import DescriptiveResult
from src.modules.t_test.result import TTestResult

RESULTS: Dict[int, Union[BaseResult, CorrelationResult, CrossCorrelationResult, TTestResult, DescriptiveResult]] = {}
