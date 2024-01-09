from typing import List

from core.constants import CORRELATION_MODEL_NAME
from core.objects import Result


class CorrelationStudyMetadata:
    def __init__(
        self,
        selected_columns: List[str],
    ):
        self.selected_columns = selected_columns


class CorrelationResult(Result):
    def __init__(self, result_id: int, metadata: CorrelationStudyMetadata = None):
        super().__init__(result_id, module_name=CORRELATION_MODEL_NAME)
        self.title = f"Descriptive statistics (study #{result_id})"
        self.items = []
        if metadata is None:
            self.metadata = CorrelationStudyMetadata(
                selected_columns=[],
            )
        else:
            self.metadata = metadata
