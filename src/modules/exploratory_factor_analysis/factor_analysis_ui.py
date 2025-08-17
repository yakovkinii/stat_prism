from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.exploratory_factor_analysis.main import recalculate_factor_analysis_study
from src.modules.exploratory_factor_analysis.result import (
    ExtractionMethod,
    FactorAnalysisStudyConfig,
    RotationType,
)
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.edit import LabeledLineEdit
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.spin import Spin
from src.pyside_ext.elements.title import Title


class FactorAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Exploratory Factor Analysis"),
            "spacer1": SpacerSmall(),
            "method": ComboBox(label_text="Method:"),
            "rotation": ComboBox(label_text="Rotation:"),
            "nfactors": Spin(
                label_text="Number of factors:",
                min_value=1,
                max_value=100,
            ),
            "kaiser": LargeCheckbox(label_text="Kaiser normalization"),
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
        self.setup(stretch=True)

        self.elements["method"].configure(
            ExtractionMethod.get_values(),
        )
        self.elements["rotation"].configure(
            RotationType.get_values(),
        )

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        cfg = RESULTS[result_id].config
        self.elements["method"].combo_box.setCurrentText(cfg.method.value)
        self.elements["rotation"].combo_box.setCurrentText(cfg.rotation.value)
        self.elements["nfactors"].spin_box.setValue(cfg.n_factors)
        self.elements["kaiser"].widget.setChecked(cfg.kaiser_normalization)
        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[cfg.columns],
        )
        self.elements["compiled_filters"].configure(cfg.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = FactorAnalysisStudyConfig(
            columns=self.elements["column_selector"].get_selected_columns()[0],
            n_factors=self.elements["nfactors"].spin_box.value(),
            method=ExtractionMethod(self.elements["method"].combo_box.currentText()),
            rotation=RotationType(self.elements["rotation"].combo_box.currentText()),
            kaiser_normalization=self.elements["kaiser"].widget.isChecked(),
            filters=RESULTS[self.result_id].config.filters,
        )

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_factor_analysis_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
