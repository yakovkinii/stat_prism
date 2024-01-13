from typing import List

from core.constants import CORRELATION_MODEL_NAME
from core.objects import Result


class CorrelationStudyMetadata:
    def __init__(
        self,
        selected_columns: List[str],
            compact:bool,
            table_name:str
    ):
        self.selected_columns = selected_columns
        self.compact = compact
        self.table_name = table_name


class CorrelationResult(Result):
    def __init__(self, result_id: int, metadata: CorrelationStudyMetadata = None):
        super().__init__(result_id, module_name=CORRELATION_MODEL_NAME)
        self.title = f"Descriptive statistics (study #{result_id})"
        self.items = []
        if metadata is None:
            self.metadata = CorrelationStudyMetadata(
                selected_columns=[],
                compact=False,
                table_name=''
            )
        else:
            self.metadata = metadata
