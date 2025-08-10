#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from typing import List, Union

from src.data.data import Data


class DataManager:
    # todo not used yet, but will be used in the future to manage data items
    def __init__(self):
        self.raw_data_result_id = None

    def set_raw_data_result_id(self, result_id: str):
        self.raw_data_result_id = result_id



DATA_MANAGER = DataManager()
