import logging
from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.custom_widget_containers import BigAssCheckbox, Column, ColumnSelectorEx, Field, SpacerSmall, Title
from src.common.decorators import log_method
from src.common.result.registry import RESULTS
from src.core.correlation.correlation_result import CorrelationStudyConfig
from src.core.correlation.main import recalculate_correlation_study
from src.settings_panel.panels.base import BaseSettingsPanel

if TYPE_CHECKING:
    pass


class Correlation(BaseSettingsPanel):
    def __init__(self, parent_widget, parent_class, root_class, stacked_widget_index):
        super().__init__(
            parent_widget=parent_widget,
            parent_class=parent_class,
            root_class=root_class,
            stacked_widget_index=stacked_widget_index,
            stretch=True,
            recalculate=True,
        )

        self.elements = {
            "title": Title(
                parent_widget=self.widget_for_elements,
                label_text="Correlation",
            ),
            "spacer": SpacerSmall(parent_widget=self.widget_for_elements),
            "compact": BigAssCheckbox(
                parent_widget=self.widget_for_elements,
                label_text="Compact table",
                handler=self.study_settings_changed,
            ),
            "report_only_significant": BigAssCheckbox(
                parent_widget=self.widget_for_elements,
                label_text="Report only significant correlations",
                handler=self.study_settings_changed,
            ),
            "spacer2": SpacerSmall(parent_widget=self.widget_for_elements),
            "column_selector": ColumnSelectorEx(
                parent_widget=self.widget_for_elements,
                fields=[
                    Field(
                        name="Columns:",
                        column_type=ColumnType.NUMERIC,
                    ),
                    Field(
                        name="Dummy 1-column:",
                        column_type=ColumnType.NOMINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                    Field(
                        name="Dummy long list:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=10,
                    ),
                ],
                clicked_handler=self.open_popup_handler,
                study_settings_changed_handler=self.study_settings_changed,
            ),
        }
        self.place_elements()

    @log_method
    def configure(self, result_id: int, caller_index=None):
        self.configuring = True
        self.caller_index = caller_index
        self.result_id = result_id

        all_column_names = self.tabledata.get_column_names()
        number_of_columns = len(all_column_names)
        types = [self.tabledata.get_column_type(i) for i in range(number_of_columns)]

        all_columns = [Column(name=col, column_type=column_type) for col, column_type in zip(all_column_names, types)]

        config = RESULTS[result_id].config

        self.elements["column_selector"].configure(
            columns=all_columns,
            selected_columns_list=[config.selected_columns, [], []],
        )
        self.elements["compact"].widget.setChecked(config.compact)
        self.elements["report_only_significant"].widget.setChecked(config.report_only_significant)
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
            report_only_significant=self.elements["report_only_significant"].widget.isChecked(),
            filter_id=RESULTS[self.result_id].config.filter_id,
        )
        RESULTS[self.result_id].config = config
        filter_result = None
        RESULTS[self.result_id] = recalculate_correlation_study(
            df=self.tabledata.get_data(), result=RESULTS[self.result_id], filter_result=filter_result
        )

        RESULTS[self.result_id].needs_update = False
        self.set_recalculate_button_highlight(False)

        self.root_class.result_selector_panel.refresh_result(result_id=self.result_id)
        self.root_class.results_panel.display(result_id=self.result_id)
        self.root_class.action_activate_results_panel()

    def study_settings_changed(self):
        if self.configuring:
            return

        RESULTS[self.result_id].needs_update = True
        self.set_recalculate_button_highlight(True)

    def open_popup_handler(self):
        self.elements["column_selector"].configure_popup()

        self.root_class.settings_panel.column_selector_panel.configure(
            caller_index=self.stacked_widget_index,
            finished_handler=self.popup_closed_handler,
            popup=self.elements["column_selector"].popup,
        )
        self.root_class.action_activate_panel_by_index(self.root_class.settings_panel.column_selector_panel_index)

    def popup_closed_handler(self):
        self.elements["column_selector"].configure_from_popup()
