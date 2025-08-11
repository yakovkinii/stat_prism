#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.modules.common.result.registry import RESULTS


class DataManager:
    # todo not used yet, but will be used in the future to manage data items
    def __init__(self):
        self.raw_data_result_id = None

    def set_raw_data_result_id(self, result_id: str):
        assert (
            self.raw_data_result_id is None or self.raw_data_result_id == result_id
        ), "Raw data result ID is already set."
        self.raw_data_result_id = result_id

    def get_raw_data_result_id(self) -> str:
        return self.raw_data_result_id

    def get_latest_data(self):
        return RESULTS[self.raw_data_result_id].config.data.copy()


DATA_MANAGER = DataManager()
