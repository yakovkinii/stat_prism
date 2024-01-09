from typing import List

from core.constants import DESCRIPTIVE_MODEL_NAME
from core.objects import Result


class DescriptiveStudyMetadata:
    def __init__(
        self,
        selected_columns: List[str],
        n: bool,
        missing: bool,
        mean: bool,
        median: bool,
        stddev: bool,
        variance: bool,
        minimum: bool,
        maximum: bool,
    ):
        self.selected_columns = selected_columns
        self.n = n
        self.missing = missing
        self.mean = mean
        self.median = median
        self.stddev = stddev
        self.variance = variance
        self.minimum = minimum
        self.maximum = maximum


class DescriptiveResult(Result):
    def __init__(self, result_id: int, metadata: DescriptiveStudyMetadata = None):
        super().__init__(result_id, module_name=DESCRIPTIVE_MODEL_NAME)
        self.title = f"Descriptive statistics (study #{result_id})"
        self.items = []
        if metadata is None:
            self.metadata = DescriptiveStudyMetadata(
                selected_columns=[],
                n=False,
                missing=False,
                mean=True,
                median=False,
                stddev=True,
                variance=False,
                minimum=True,
                maximum=True,
            )
        else:
            self.metadata = metadata
