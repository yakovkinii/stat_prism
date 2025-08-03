#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from typing import List, Union

from src.data.data import Data


class DataManager:
    def __init__(self):
        self.raw_data: Union[Data, None] = None
        self.data_items: List[Data] = [self.raw_data]

    def set_raw_data(self, data: Data):
        self.raw_data = data
        self.data_items = [self.raw_data]

    def get_latest_data(self) -> Data:
        if self.data_items:
            return self.data_items[-1]

    def add_data_item(self, data: Data):
        self.data_items.append(data)

    def get_data_item(self, index: int) -> Data:
        return self.data_items[index]


DATA_MANAGER = DataManager()
