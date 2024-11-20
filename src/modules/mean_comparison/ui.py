#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.checkbox.checkbox import LargeCheckbox
from src.common.elements.column_selector.column_selector import ColumnSelectorEx, Field
from src.common.elements.combo_box.combo_box import ComboBox
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.mean_comparison.constant import MeanComparisonMethod
from src.modules.mean_comparison.main import recalculate_mean_comparison_study
from src.modules.mean_comparison.result import MeanComparisonStudyConfig

if TYPE_CHECKING:
    pass


class MeanComparison(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Mean Comparison"),
            "spacer": SpacerSmall(),
            "method": ComboBox(
                label_text="Method:",
            ),
            "effect_size": LargeCheckbox(label_text="Effect size"),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variable(s):",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=10,
                        minimum_columns=1,
                    ),
                    Field(
                        name="Grouping Column:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                        minimum_columns=1,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True)
        self.elements["method"].configure(MeanComparisonMethod.get_values())

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["method"].combo_box.setCurrentText(RESULTS[result_id].config.method.value)
        self.elements["effect_size"].widget.setChecked(RESULTS[result_id].config.effect_size)
        self.elements["column_selector"].configure(
            columns=self.tabledata.get_all_columns_as_column_types(),
            selected_columns_list=[
                RESULTS[result_id].config.selected_columns,
                [RESULTS[result_id].config.grouping_column]
                if RESULTS[result_id].config.grouping_column is not None
                else [],
            ],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = MeanComparisonStudyConfig(
            method=MeanComparisonMethod(self.elements["method"].combo_box.currentText()),
            effect_size=self.elements["effect_size"].widget.isChecked(),
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            selected_columns_types=[
                self.tabledata.get_column_type_from_column_name(col)
                for col in self.elements["column_selector"].get_selected_columns()[0]
            ],
            grouping_column=self.elements["column_selector"].get_selected_columns()[1][0]
            if len(self.elements["column_selector"].get_selected_columns()[1]) == 1
            else None,
            filters=RESULTS[self.result_id].config.filters,
        )

        ordinal_orders = {
            col: self.tabledata.get_column_ordinal_order_from_column_name(col)
            for col in RESULTS[self.result_id].config.selected_columns
            if self.tabledata.get_column_type_from_column_name(col) == ColumnType.ORDINAL
        }
        RESULTS[self.result_id] = recalculate_mean_comparison_study(
            df=self.tabledata.get_data(),
            result=RESULTS[self.result_id],
            ordinal_orders=ordinal_orders,
        )

        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.result_selector_panel.refresh_result(result_id=self.result_id)
        self.root_class.results_panel.display(result_id=self.result_id)
        self.root_class.action_activate_results_panel()

    @log_method
    def handler(self, message: Message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "compiled_filters":
                self.open_filter_handler()
            elif message.caller_id == "column_selector":
                self.open_column_selector_popup()
            else:
                super().handler(message)
        elif message.message_type == MessageType.FILTER_CLICKED:
            self.open_filter_handler()
        else:
            super().handler(message)
