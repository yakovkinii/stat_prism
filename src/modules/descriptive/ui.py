#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.column_selector.column_selector import ColumnSelectorEx, Field
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.descriptive.main import recalculate_descriptive_study
from src.modules.descriptive.result import DescriptiveStudyConfig


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
            columns=self.tabledata.get_all_columns_as_column_types(),
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

        #     if len(cfg.selected_columns) < 1:
        #         msg = "Please select one Grouping Column and at least one Variable"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result

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
        RESULTS[self.result_id] = recalculate_descriptive_study(
            data=self.tabledata.get_data_v2(), result=RESULTS[self.result_id]
        )

        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.result_selector_panel.refresh_result(result_id=self.result_id)
        self.root_class.results_panel.display(result_id=self.result_id)
        self.root_class.action_activate_results_panel()
