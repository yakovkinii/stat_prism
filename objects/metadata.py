from typing import List


class DescriptiveStudyMetadata:
    def __init__(self,
                 selected_columns: List[str],
                 n: bool,
                 missing: bool,
                 mean: bool,
                 median: bool,
                 stddev: bool,
                 variance: bool,
                 minimum: bool,
                 maximum: bool):
        self.selected_columns = selected_columns
        self.n = n
        self.missing = missing
        self.mean = mean
        self.median = median
        self.stddev = stddev
        self.variance = variance
        self.minimum = minimum
        self.maximum = maximum
