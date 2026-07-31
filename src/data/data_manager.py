#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

from src.common.decorators import log_method
from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import RESULTS


class DataManager:
    def __init__(self):
        self.raw_data_result_id = None
        self.data_chain = []

    def reset(self):
        """Forget all chain state (used when opening a project / starting a new one)."""
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

    def move_in_chain(self, result_id: int, delta: int) -> bool:
        """Swap a data-processing result with its neighbor in the chain. Index 0
        (raw data) always stays first. Returns True if a move happened."""
        if result_id not in self.data_chain:
            return False
        i = self.data_chain.index(result_id)
        j = i + delta
        if j < 1 or j >= len(self.data_chain):
            return False
        self.data_chain[i], self.data_chain[j] = self.data_chain[j], self.data_chain[i]
        return True

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

    def get_data_from_data_label(self, data_label: str, current_result_id: int) -> Data:
        if data_label == "Auto":
            # "Auto" = the data that feeds this study. For a data-processing step (which is a
            # chain member) that is the *immediately preceding* step's output
            if current_result_id in self.data_chain:
                index = self.data_chain.index(current_result_id)
                result_id = self.data_chain[index - 1] if index > 0 else current_result_id
            else:
                result_id = self.data_chain[-1]
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
