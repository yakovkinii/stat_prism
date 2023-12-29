from typing import List


class DescriptiveStudyMetadataUI:
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


class DescriptiveStudyMetadata:
    def __init__(self, metadata_ui: DescriptiveStudyMetadataUI):
        self.selected_columns = metadata_ui.selected_columns
        self.n = metadata_ui.n
        self.missing = metadata_ui.missing
        self.mean = metadata_ui.mean
        self.median = metadata_ui.median
        self.stddev = metadata_ui.stddev
        self.variance = metadata_ui.variance
        self.minimum = metadata_ui.minimum
        self.maximum = metadata_ui.maximum
