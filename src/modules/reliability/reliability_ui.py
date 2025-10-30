#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.correlation.result import CORRELATION_TYPE_MAP
from src.modules.reliability.main import recalculate_reliability_study
from src.modules.reliability.result import ReliabilityStudyConfig
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall


class Reliability(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
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
        self.setup(stretch=True, label="Reliability Study")
        self.elements["correlation_type"].configure(list(CORRELATION_TYPE_MAP.keys()))

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            selected_columns_list=[
                RESULTS[result_id].config.selected_columns,
                [RESULTS[result_id].config.scale_column],
            ],
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.elements["correlation_type"].combo_box.setCurrentIndex(RESULTS[result_id].config.correlation_type.value)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        return True
        #     if len(config.selected_columns) < 2:
        #         msg = "Please select at least two questions"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result

    def recalculate(self):
        if self.configuring:
            return
        if not self.check():
            return
        RESULTS[self.result_id].config = ReliabilityStudyConfig(
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            selected_columns_types=[
                DATA_MANAGER.get_latest_data().get_column_type_from_column_name(col)
                for col in self.elements["column_selector"].get_selected_columns()[0]
            ],
            scale_column=self.elements["column_selector"].get_selected_columns()[1][0],
            correlation_type=CORRELATION_TYPE_MAP[self.elements["correlation_type"].combo_box.currentText()],
            filters=RESULTS[self.result_id].config.filters,
        )

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_reliability_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
