from typing import List

from core.registry.constants import CORRELATION_MODEL_NAME
from core.registry.objects import Result


class CorrelationStudyMetadata:
    def __init__(
        self,
        selected_columns: List[str],
        compact: bool,
        report_non_significant: bool,
        table_name: str,
    ):
        self.selected_columns = selected_columns
        self.compact = compact
        self.report_non_significant = report_non_significant
        self.table_name = table_name


class CorrelationResult(Result):
    def __init__(self, result_id: int, metadata: CorrelationStudyMetadata = None):
        super().__init__(result_id, module_name=CORRELATION_MODEL_NAME)
        self.title = f"Descriptive statistics (study #{result_id})"
        self.items = []
        if metadata is None:
            self.metadata = CorrelationStudyMetadata(
                selected_columns=[], compact=False, report_non_significant=False, table_name=""
            )
        else:
            self.metadata = metadata
