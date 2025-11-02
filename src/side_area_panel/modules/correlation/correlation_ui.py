#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from src.common.constant import ColumnType
from src.common.decorators import log_method, log_method_noarg
from src.common.messages import Message, MessageType
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.correlation.main import recalculate_correlation_study
from src.side_area_panel.modules.correlation.result import (
    CORRELATION_TYPE_MAP,
    CorrelationStudyConfig,
)


class Correlation(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "compact": LargeCheckbox(label_text="Compact table"),
            "report_only_significant": LargeCheckbox(label_text="Report only significant correlations"),
            "generate_heatmap": LargeCheckbox(label_text="Heatmap"),
            "generate_plots": LargeCheckbox(label_text="Pairwise plots"),
            "correlation_type": ComboBox("Correlation type: "),
            "spacer2": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Variables:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=10,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True, label="Correlations")
        self.elements["correlation_type"].configure(list(CORRELATION_TYPE_MAP.keys()))

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
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

    @log_method_noarg
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

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_correlation_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)

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
