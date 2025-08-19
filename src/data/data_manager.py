#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from src.common.decorators import log_method
from src.modules.common.result.registry import RESULTS


class DataManager:
    # todo not used yet, but will be used in the future to manage data items
    def __init__(self):
        self.raw_data_result_id = None
        self.data_chain = []

    def set_raw_data_result_id(self, result_id: str):
        assert (
            self.raw_data_result_id is None or self.raw_data_result_id == result_id
        ), "Raw data result ID is already set."
        self.raw_data_result_id = result_id
        self.data_chain.append(result_id)

    def add_data_to_chain(self, result_id: str):
        assert result_id not in self.data_chain, "Result ID already in data chain."
        self.data_chain.append(result_id)

    def remove_data_from_chain(self, result_id: str):
        assert result_id in self.data_chain, "Result ID not found in data chain."
        self.data_chain.remove(result_id)

    @log_method
    def remove_data_from_chain_if_exists(self, result_id: str):
        if result_id in self.data_chain:
            self.data_chain.remove(result_id)

    def get_raw_data_result_id(self) -> str:
        return self.raw_data_result_id

    def get_latest_data(self):
        return RESULTS[self.data_chain[-1]].config.data.copy()

    def get_data_before_result_id(self, result_id: str):
        if result_id not in self.data_chain:
            raise ValueError(f"Result ID {result_id} not found in data chain.")
        index = self.data_chain.index(result_id)
        if index == 0:
            raise ValueError("No data before the first result ID.")
        return RESULTS[self.data_chain[index - 1]].config.data.copy()

    def from_unpickled(self, data: "DataManager"):
        self.raw_data_result_id = data.raw_data_result_id
        self.data_chain = data.data_chain.copy()


DATA_MANAGER = DataManager()
