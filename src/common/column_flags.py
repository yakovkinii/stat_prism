from attr import define

from src.common.constant import ColumnType


@define
class ColumnFlagsRegistry:
    inverted = "inverted"
    color = "color"
    column_type = "column_type"


class ColumnFlags:
    def __init__(self, dtype: str):
        self.column_type = ColumnType.NUMERIC if dtype in ["int", "float"] else ColumnType.NOMINAL
        self.inverted = False
        self.color = None

        self._flags = {
            "inverted": self.inverted,
        }

    def set_flag(self, flag: str, value):
        self._flags[flag] = value

    def get_flag(self, flag: str):
        return self._flags[flag]
