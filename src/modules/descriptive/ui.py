#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method, log_method_noarg
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.descriptive.main import recalculate_descriptive_study
from src.modules.descriptive.result import DescriptiveStudyConfig
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title


class Descriptive(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Descriptive Statistics"),
            "spacer": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variable(s):",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=10,
                    ),
                    Field(
                        name="Grouping Column (optional):",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True)

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[
                RESULTS[result_id].config.selected_columns,
                [RESULTS[result_id].config.grouping_column],
            ],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        return True


    @log_method_noarg
    def recalculate(self):
        if self.configuring:
            return

        if not self.check():
            return

        RESULTS[self.result_id].config = DescriptiveStudyConfig(
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            grouping_column=self.elements["column_selector"].get_selected_columns()[1][0],
            filters=RESULTS[self.result_id].config.filters,
        )

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_descriptive_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )


    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
