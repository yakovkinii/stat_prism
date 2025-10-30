#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.contingency.main import recalculate_contingency_study
from src.modules.contingency.result import ContingencyStudyConfig
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.filter import CompiledFilterHistory


class Contingency(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variable 1:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                    Field(
                        name="Variable 2:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True, label="Contingency Table")

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[
                [RESULTS[result_id].config.selected_column1],
                [RESULTS[result_id].config.selected_column2],
            ],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        if self.elements["column_selector"].get_selected_columns()[0][0] == [None]:
            logging.info("No column selected for Variable 1")
            return False
        if self.elements["column_selector"].get_selected_columns()[1][0] == [None]:
            logging.info("No column selected for Variable 2")
            return False
        return True

    def recalculate(self):
        if self.configuring:
            return

        if not self.check():
            return

        RESULTS[self.result_id].config = ContingencyStudyConfig(
            selected_column1=self.elements["column_selector"].get_selected_columns()[0][0],
            selected_column2=self.elements["column_selector"].get_selected_columns()[1][0],
            filters=RESULTS[self.result_id].config.filters,
        )
        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_contingency_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
