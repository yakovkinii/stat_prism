#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.modules.base.base import BaseModulePanel
from src.modules.common.result.registry import RESULTS
from src.modules.regression.main import recalculate_regression_study
from src.modules.regression.result import RegressionStudyConfig
from src.pyside_ext.elements.column_selector import ColumnSelectorEx, Field
from src.pyside_ext.elements.filter import CompiledFilterHistory
from src.pyside_ext.elements.spacer_small import SpacerSmall
from src.pyside_ext.elements.title import Title


class Regression(BaseModulePanel):
    def setup_ui(self):
        self.elements = {
            "title": Title(label_text="Regression"),
            "spacer": SpacerSmall(),
            "column_selector": ColumnSelectorEx(
                fields=[
                    Field(
                        name="Dependent Variable:",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                    Field(
                        name="Independent Variable(s):",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=5,
                    ),
                    Field(
                        name="Moderator Variable (optional):",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                    Field(
                        name="Mediator Variable (optional):",
                        column_type=ColumnType.ORDINAL,
                        reasonable_number_of_columns=1,
                        allow_only_single_column=True,
                    ),
                ],
            ),
            "compiled_filters": CompiledFilterHistory(),
        }
        self.setup(stretch=True)

    @log_method
    def configure(self, result_id: int):
        self.configuring = True
        self.result_id = result_id

        self.elements["column_selector"].configure(
            selected_columns_list=[
                [RESULTS[result_id].config.dependent_column],
                RESULTS[result_id].config.independent_columns,
                [RESULTS[result_id].config.moderator_column],
                [RESULTS[result_id].config.mediator_column],
            ],
            columns=DATA_MANAGER.get_latest_data().get_all_columns_as_column_types(),
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def check(self):
        return True
        #  if (cfg.dependent_column is None) or (len(cfg.independent_columns) < 1):
        #         msg = "Please select one Dependent Variable and at least one Independent Variable"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result
        #     if (cfg.mediator_column is not None) and (cfg.moderator_column is not None):
        #         msg = "Please select either a Mediator or a Moderator, not both"
        #         result.set_placeholder(msg)
        #         logging.debug(msg)
        #         return result

    def recalculate(self):
        if self.configuring:
            return

        if not self.check():
            return

        RESULTS[self.result_id].config = RegressionStudyConfig(
            dependent_column=self.elements["column_selector"].get_selected_columns()[0][0],
            independent_columns=self.elements["column_selector"].get_selected_columns()[1],
            moderator_column=self.elements["column_selector"].get_selected_columns()[2][0],
            mediator_column=self.elements["column_selector"].get_selected_columns()[3][0],
            filters=RESULTS[self.result_id].config.filters,
        )

        data = DATA_MANAGER.get_latest_data()
        result = RESULTS[self.result_id]

        def main(update):
            return recalculate_regression_study(data=data, result=result)

        run_in_separate_thread(
            main, progress_bar=self.root_class.settings_panel.progress_bar, on_done=self.recalculate_on_done
        )

    @log_method
    def recalculate_on_done(self, result):
        RESULTS[self.result_id] = result
        RESULTS[self.result_id].needs_update = False
        self.configure(result_id=self.result_id)
        self.root_class.main_area_panel.refresh_result(result_id=self.result_id)
