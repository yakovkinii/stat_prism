#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

from src.common.decorators import log_method
from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import RESULTS


class DataManager:
    def __init__(self):
        self.raw_data_result_id = None
        self.data_chain = []

    def set_raw_data_result_id(self, result_id: str):
        assert (
            self.raw_data_result_id is None or self.raw_data_result_id == result_id
        ), "Raw data result ID is already set."
        if self.raw_data_result_id is None:
            self.data_chain.append(result_id)
        self.raw_data_result_id = result_id

    def add_data_to_chain(self, result_id: str):
        assert result_id not in self.data_chain, "Result ID already in data chain."
        self.data_chain.append(result_id)

    def remove_data_from_chain(self, result_id: int):
        assert result_id in self.data_chain, "Result ID not found in data chain."
        self.data_chain.remove(result_id)

    @log_method
    def remove_data_from_chain_if_exists(self, result_id: int):
        if result_id in self.data_chain:
            self.data_chain.remove(result_id)

    def get_latest_data(self):
        logging.error("Deprecated")

        return RESULTS[self.data_chain[-1]].data.copy()

    def get_data_before_result_id(self, result_id: int):
        logging.error("Deprecated")
        if result_id not in self.data_chain:
            raise ValueError(f"Result ID {result_id} not found in data chain.")
        index = self.data_chain.index(result_id)
        if index == 0:
            raise ValueError("No data before the first result ID.")
        return RESULTS[self.data_chain[index - 1]].data.copy()

    def from_unpickled(self, data: "DataManager"):
        self.raw_data_result_id = data.raw_data_result_id
        self.data_chain = data.data_chain.copy()

    def get_all_available_data_labels(self, result_id):
        ids = ["Auto"]
        for rid in self.data_chain:
            if rid == result_id:
                continue
            ids.append(f"Data{rid}")

        return ids

    def get_data_from_data_label(self, data_label: str, current_result_id: int)->Data:
        if data_label == "Auto":
            result_id = self.data_chain[-1]
            if result_id == current_result_id:
                result_id = self.data_chain[-2]
        else:
            result_id = int(data_label.replace("Data", ""))

        if result_id not in self.data_chain:
            # To be caught by main() of data analysis
            raise ValueError(f"Data label {result_id} not found in data chain.")

        return RESULTS[result_id].data.copy()

    def try_to_remove_result(self, result_id: int):
        if result_id in self.data_chain:
            self.data_chain.remove(result_id)
            if self.raw_data_result_id == result_id:
                self.raw_data_result_id = None

DATA_MANAGER = DataManager()
