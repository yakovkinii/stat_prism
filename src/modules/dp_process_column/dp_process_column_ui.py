#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.dp_process_column.dp_process_column_result import ProcessColumnStudyConfig
from src.modules.mean_comparison.constant import (
    AssumptionChecksInGrouping,
    MeanComparisonMethod,
    MissingValuesInGrouping,
)
from src.modules.mean_comparison.main import recalculate_mean_comparison_study
from src.modules.mean_comparison.result import MeanComparisonStudyConfig
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.edit import LabeledLineEdit
from src.pyside_ext.elements.filter import CompiledFilterHistory


class ProcessColumn(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Column:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                        minimum_columns=1,
                    ),
                ],
            ),
            'rename': LabeledLineEdit(
                label_text="Rename:",
            ),
            'encode': LargeButton(
                label_text="Encode",
                icon_path="ph.arrows-clockwise",
            ),
        }
        self.setup(stretch=True, label="Process Column")
        self.elements['rename'].set_editing_finished_handler(self.recalculate)

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id
        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[
                [RESULTS[result_id].config.column],
            ],
        )
        self.elements['rename'].set_text(RESULTS[result_id].config.rename)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)
        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        # Data should not be stored in config, maybe except for raw data
        # anyway, the data is to be stored in result.
        # after each dp result recalculate, the result should be registered
        # as a data source using its result id.
        # Later there will also be a choicer for data source in each module panel.


        RESULTS[self.result_id].config = ProcessColumnStudyConfig(
            data=DATA_MANAGER.get_data_before_result_id(self.result_id),
            column=self.elements["column_selector"].get_selected_columns()[0][0],
            rename=self.elements['rename'].get_text(),
        )

        def main(update):
            return recalculate_mean_comparison_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)

    def encode_handler(self):
        selected_columns = self.elements["column_selector"].get_selected_columns()[0]
        if not selected_columns:
            return
        column_to_encode = selected_columns[0]

        def main(update):
            data = DATA_MANAGER.get_latest_data()
            df = data.get_dataframe().copy()
            update(20)
            df[column_to_encode] = df[column_to_encode].astype('category').cat.codes
            update(80)
            data.update_dataframe(df)
            return

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.encode_on_done
        )

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "encode":
                self.encode_handler()
            return
        super().handler(message)
