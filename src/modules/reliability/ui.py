#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.column_selector.column_selector import ColumnSelectorEx, Field
from src.common.elements.combo_box.combo_box import ComboBox
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.correlation.result import CORRELATION_TYPE_MAP
from src.modules.reliability.main import recalculate_reliability_study
from src.modules.reliability.result import ReliabilityStudyConfig

if TYPE_CHECKING:
    pass


class Reliability(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Reliability"),
            "spacer": SpacerSmall(),
            "correlation_type": ComboBox("Correlation type: "),
            "spacer2": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Underlying Questions:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=10,
                    ),
                    Field(
                        name="Scale (optional):",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True)
        self.elements["correlation_type"].configure(list(CORRELATION_TYPE_MAP.keys()))

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            selected_columns_list=[
                RESULTS[result_id].config.selected_columns,
                [RESULTS[result_id].config.scale_column] if RESULTS[result_id].config.scale_column is not None else [],
            ],
            columns=self.tabledata.get_all_columns_as_column_types(),
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.elements["correlation_type"].combo_box.setCurrentIndex(RESULTS[result_id].config.correlation_type.value)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = ReliabilityStudyConfig(
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            selected_columns_types=[
                self.tabledata.get_column_type_from_column_name(col)
                for col in self.elements["column_selector"].get_selected_columns()[0]
            ],
            scale_column=self.elements["column_selector"].get_selected_columns()[1][0]
            if len(self.elements["column_selector"].get_selected_columns()[1]) == 1
            else None,
            correlation_type=CORRELATION_TYPE_MAP[self.elements["correlation_type"].combo_box.currentText()],
            filters=RESULTS[self.result_id].config.filters,
        )

        ordinal_orders = {
            col: self.tabledata.get_column_ordinal_order_from_column_name(col)
            for col in RESULTS[self.result_id].config.selected_columns
            if self.tabledata.get_column_type_from_column_name(col) == ColumnType.ORDINAL
        }
        RESULTS[self.result_id] = recalculate_reliability_study(
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
