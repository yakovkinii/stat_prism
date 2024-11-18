#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import Dict, Union

from attr import define

from src.common.constant import ColumnType


@define
class ColumnAttributesRegistry:
    inverted = "inverted"
    color = "color"
    column_type = "column_type"
    ordinal_order = "ordinal_order"


class ColumnAttributes:
    def __init__(self, dtype: str):
        self.column_type = ColumnType.NUMERIC if dtype in ["int", "float"] else ColumnType.NOMINAL
        self.inverted = False
        self.color = None
        self.ordinal_order: Dict[Union[int, float, str], int] = dict()
        self.original_name: str = ""

        self._flags = {
            "inverted": self.inverted,
        }

    def set_flag(self, flag: str, value):
        self._flags[flag] = value

    def get_flag(self, flag: str):
        return self._flags[flag]
