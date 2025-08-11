#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.mean_comparison.constant import MeanComparisonMethod
from src.modules.mean_comparison.main import recalculate_mean_comparison_study
from src.modules.mean_comparison.result import MeanComparisonStudyConfig
from src.pyside_ext.elements.checkbox import LargeCheckbox
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.combo_box import ComboBox
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title


class MeanComparison(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Mean Comparison"),
            "spacer": SpacerSmall(),
            "method": ComboBox(
                label_text="Method:",
            ),
            "effect_size": LargeCheckbox(label_text="Effect size/Post-hoc"),
            "means": LargeCheckbox(label_text="Means/Medians"),
            "plots": LargeCheckbox(label_text="Plots"),
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
        self.elements["means"].widget.setChecked(RESULTS[result_id].config.means)
        self.elements["plots"].widget.setChecked(RESULTS[result_id].config.plots)
        self.elements["effect_size"].widget.setChecked(RESULTS[result_id].config.effect_size)
        self.elements["column_selector"].configure(
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
            selected_columns_list=[
                RESULTS[result_id].config.selected_columns,
                [RESULTS[result_id].config.grouping_column],
            ],
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        return True
        #     if len(config.selected_columns) < 1 or config.grouping_column is None:
        #         msg = "Please select one Grouping Column and at least one Variable"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result
        #     if config.method in [MeanComparisonMethod.HOMOGENEOUS, MeanComparisonMethod.INHOMOGENEOUS]:
        #         if any([col_type == ColumnType.NOMINAL for col_type in config.selected_columns_types]):
        #             msg = "Cannot perform parametric test on nominal columns"
        #             result.set_placeholder(msg)
        #             logging.debug(msg)

        # n_unique_values_in_grouping_column = len(df[cfg.grouping_column].unique())
        #     if n_unique_values_in_grouping_column < 2:
        #         msg = f"Not enough unique values in grouping column: {df[cfg.grouping_column].unique()}"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result
        #     elif n_unique_values_in_grouping_column == 2:
        #         n_rows_per_group = df.groupby(cfg.grouping_column).size()
        #         if n_rows_per_group.min() < 3:
        #             msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
        #             result.set_placeholder(msg)
        #             logging.debug(msg)
        #             return result
        #         return recalculate_mean_comparison_t_test(df, cfg, result, ordinal_orders)
        #     else:
        #         n_rows_per_group = df.groupby(cfg.grouping_column).size()
        #         if n_rows_per_group.min() < 3:
        #             msg = f"Insufficient population in some groups: {n_rows_per_group.to_dict()}"
        #             result.set_placeholder(msg)
        #             logging.debug(msg)
        #             return result
        #         return recalculate_mean_comparison_anova(df, cfg, result, ordinal_orders)

    def recalculate(self):
        if self.configuring:
            return

        if not self.check():
            return

        RESULTS[self.result_id].config = MeanComparisonStudyConfig(
            method=MeanComparisonMethod(self.elements["method"].combo_box.currentText()),
            means=self.elements["means"].widget.isChecked(),
            effect_size=self.elements["effect_size"].widget.isChecked(),
            plots=self.elements["plots"].widget.isChecked(),
            selected_columns=self.elements["column_selector"].get_selected_columns()[0],
            selected_columns_types=[
                DATA_MANAGER.get_latest_data().get_column_type_from_column_name(col)
                for col in self.elements["column_selector"].get_selected_columns()[0]
            ],
            grouping_column=self.elements["column_selector"].get_selected_columns()[1][0],
            filters=RESULTS[self.result_id].config.filters,
        )

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

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
