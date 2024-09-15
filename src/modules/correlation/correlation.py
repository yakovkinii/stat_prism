import logging
from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.checkbox.checkbox import LargeCheckbox
from src.common.elements.column_selector.column_selector import Column, ColumnSelectorEx, Field
from src.common.elements.combo_box.combo_box import ComboBox
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.correlation.correlation_result import CORRELATION_TYPE_MAP, CorrelationStudyConfig
from src.modules.correlation.main import recalculate_correlation_study
from src.settings_panel.panels.registry import PanelRegistry

if TYPE_CHECKING:
    pass


class Correlation(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Correlation"),
            "spacer": SpacerSmall(),
            "compact": LargeCheckbox(label_text="Compact table"),
            "report_only_significant": LargeCheckbox(label_text="Report only significant correlations"),
            "correlation_type": ComboBox(),
            "spacer2": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Columns:",
                        column_type=ColumnType.NUMERIC,
                        reasonable_number_of_columns=10,
                    ),
                    # Field(
                    #     name="Dummy 1-column:",
                    #     column_type=ColumnType.NOMINAL,
                    #     reasonable_number_of_columns=1,
                    #     allow_only_single_column=True,
                    # ),
                    # Field(
                    #     name="Dummy long list:",
                    #     column_type=ColumnType.ORDINAL,
                    #     reasonable_number_of_columns=10,
                    # ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True)

    @log_method
    def configure(self, result_id: int, caller_index=None):
        self.configuring = True
        self.caller_index = caller_index
        self.result_id = result_id

        self.elements["correlation_type"].configure(list(CORRELATION_TYPE_MAP.keys()))

        all_column_names = self.tabledata.get_column_names()
        number_of_columns = len(all_column_names)
        types = [self.tabledata.get_column_type(i) for i in range(number_of_columns)]
        all_columns = [Column(name=col, column_type=column_type) for col, column_type in zip(all_column_names, types)]

        config = RESULTS[result_id].config

        self.elements["column_selector"].configure(
            columns=all_columns,
            selected_columns_list=[config.selected_columns, [], []],
        )

        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)

        self.elements["compact"].widget.setChecked(config.compact)
        self.elements["report_only_significant"].widget.setChecked(config.report_only_significant)
        self.elements["correlation_type"].widget.setCurrentIndex(config.correlation_type.value)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            logging.error("Recalculate called while configuring.")
            return

        selected_columns = self.elements["column_selector"].get_selected_columns()[0]
        config = CorrelationStudyConfig(
            selected_columns=selected_columns,
            compact=self.elements["compact"].widget.isChecked(),
            correlation_type=CORRELATION_TYPE_MAP[self.elements["correlation_type"].widget.currentText()],
            report_only_significant=self.elements["report_only_significant"].widget.isChecked(),
            filters=RESULTS[self.result_id].config.filters,
        )
        RESULTS[self.result_id].config = config
        RESULTS[self.result_id] = recalculate_correlation_study(
            df=self.tabledata.get_data(), result=RESULTS[self.result_id]
        )

        RESULTS[self.result_id].needs_update = False
        self.set_recalculate_button_highlight(False)

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

    def open_column_selector_popup(self):
        self.elements["column_selector"].configure_popup()
        PanelRegistry.COLUMN_SELECTOR.ui_instance.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.popup_closed_handler,
            popup=self.elements["column_selector"].popup,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.COLUMN_SELECTOR.settings_stacked_widget_index)

    def open_filter_handler(self):
        PanelRegistry.FILTER.ui_instance.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.filter_closed_handler,
            filters=RESULTS[self.result_id].config.filters,
        )
        self.root_class.action_activate_panel_by_index(PanelRegistry.FILTER.settings_stacked_widget_index)

    def popup_closed_handler(self):
        self.elements["column_selector"].configure_from_popup()

    @log_method
    def filter_closed_handler(self, filters):
        RESULTS[self.result_id].config.filters = filters
        self.elements["compiled_filters"].configure(filters)
        self.handler(Message(message_type=MessageType.STATE_CHANGED, payload=None, caller_id="filter"))
