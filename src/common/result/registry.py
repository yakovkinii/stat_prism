from typing import Dict, Union

from src.common.result.classes.base_result import BaseResult
from src.modules.correlation.result import CorrelationResult
from src.modules.cross_correlation.result import CrossCorrelationResult

RESULTS: Dict[int, Union[BaseResult, CorrelationResult, CrossCorrelationResult]] = {}
