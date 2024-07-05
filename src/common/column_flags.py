import pandas as pd
from attr import define


@define
class ColumnFlagsRegistry:
    inverted = "inverted"
    color="color"


class ColumnFlags:
    def __init__(self, column: pd.Series):
        self.numeric = column.dtype in [int, float]
        self.inverted = False
        self.color = None

        self._flags = {
            "inverted": self.inverted,
        }

    def set_flag(self, flag: str, value: bool):
        self._flags[flag] = value

    def get_flag(self, flag: str):
        return self._flags[flag]
