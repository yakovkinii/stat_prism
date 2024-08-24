from typing import Dict, Union

from src.common.result.classes.base_result import BaseResult
from src.core.correlation.correlation_result import CorrelationResult

RESULTS: Dict[int, Union[BaseResult, CorrelationResult]] = {}
