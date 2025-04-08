#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.column_selector.column_selector import ColumnSelectorEx, Field
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.v2.main import recalculate_v2_study
from src.modules.v2.result import V2StudyConfig

if TYPE_CHECKING:
    pass


class V2(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="V2"),
            "spacer": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variable(s):",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=10,
                        minimum_columns=1,
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
            selected_columns_list=[RESULTS[result_id].config.selected_columns],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = V2StudyConfig(
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            filters=RESULTS[self.result_id].config.filters,
        )

        RESULTS[self.result_id] = recalculate_v2_study(
            data=self.tabledata.get_data_v2(),
            result=RESULTS[self.result_id],
        )

        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.result_selector_panel.refresh_result(result_id=self.result_id)
        self.root_class.results_panel.display(result_id=self.result_id)
        self.root_class.action_activate_results_panel()

    @log_method
    def handler(self, message: Message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "column_selector":
                self.open_column_selector_popup()
                return
        super().handler(message)
