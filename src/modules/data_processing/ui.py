#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

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
from src.modules.correlation.main import recalculate_correlation_study
from src.modules.correlation.result import CORRELATION_TYPE_MAP, CorrelationStudyConfig


class DataProcessing(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Data Processing"),
            "spacer": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Questions:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=10,
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
            columns=self.tabledata.get_all_columns_as_column_types(),
            selected_columns_list=[RESULTS[result_id].config.selected_columns],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.elements["compact"].widget.setChecked(RESULTS[result_id].config.compact)
        self.elements["report_only_significant"].widget.setChecked(RESULTS[result_id].config.report_only_significant)
        self.elements["generate_heatmap"].widget.setChecked(RESULTS[result_id].config.generate_heatmap)
        self.elements["generate_plots"].widget.setChecked(RESULTS[result_id].config.generate_plots)
        self.elements["correlation_type"].combo_box.setCurrentIndex(RESULTS[result_id].config.correlation_type.value)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        if len(self.elements["column_selector"].get_selected_columns()[0]) < 2:
            logging.info("Please select at least 2 columns")
            return False

        #     if kind in [CorrelationType.PHI, CorrelationType.TETRACHORIC]:
        #         if not all(df[col].nunique() <= 2 for col in df.columns):
        #             msg = f"All columns must have at most 2 unique values for {kind.name} correlation."
        #             result.set_placeholder(msg)
        #             logging.debug(msg)
        #             return result

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = CorrelationStudyConfig(
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            compact=self.elements["compact"].widget.isChecked(),
            correlation_type=CORRELATION_TYPE_MAP[self.elements["correlation_type"].combo_box.currentText()],
            report_only_significant=self.elements["report_only_significant"].widget.isChecked(),
            generate_heatmap=self.elements["generate_heatmap"].widget.isChecked(),
            generate_plots=self.elements["generate_plots"].widget.isChecked(),
            filters=RESULTS[self.result_id].config.filters,
        )

        RESULTS[self.result_id] = recalculate_correlation_study(
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
