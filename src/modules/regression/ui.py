#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import TYPE_CHECKING

from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.elements.column_selector.column_selector import ColumnSelectorEx, Field
from src.common.elements.filter.filter import CompiledFilterHistory
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.registry import RESULTS
from src.modules.base.base import BaseModulePanel
from src.modules.regression.main import recalculate_regression_study
from src.modules.regression.result import RegressionStudyConfig

if TYPE_CHECKING:
    pass


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
                [RESULTS[result_id].config.dependent_column] if RESULTS[result_id].config.dependent_column else [],
                RESULTS[result_id].config.independent_columns,
                [RESULTS[result_id].config.moderator_column] if RESULTS[result_id].config.moderator_column else [],
                [RESULTS[result_id].config.mediator_column] if RESULTS[result_id].config.mediator_column else [],
            ],
            columns=self.tabledata.get_all_columns_as_column_types(),
        )
        self.elements["compiled_filters"].configure(RESULTS[result_id].config.filters)
        self.set_recalculate_button_highlight(RESULTS[result_id].needs_update)

        self.configuring = False

    def recalculate(self):
        if self.configuring:
            return

        RESULTS[self.result_id].config = RegressionStudyConfig(
            dependent_column=self.elements["column_selector"].get_selected_columns()[0][0]
            if len(self.elements["column_selector"].get_selected_columns()[0]) == 1
            else None,
            independent_columns=self.elements["column_selector"].get_selected_columns()[1],
            moderator_column=self.elements["column_selector"].get_selected_columns()[2][0]
            if len(self.elements["column_selector"].get_selected_columns()[2]) == 1
            else None,
            mediator_column=self.elements["column_selector"].get_selected_columns()[3][0]
            if len(self.elements["column_selector"].get_selected_columns()[3]) == 1
            else None,
            filters=RESULTS[self.result_id].config.filters,
        )

        all_columns = [
            RESULTS[self.result_id].config.dependent_column,
        ] + RESULTS[self.result_id].config.independent_columns
        if RESULTS[self.result_id].config.moderator_column is not None:
            all_columns.append(RESULTS[self.result_id].config.moderator_column)
        if RESULTS[self.result_id].config.mediator_column is not None:
            all_columns.append(RESULTS[self.result_id].config.mediator_column)

        ordinal_orders = {
            col: self.tabledata.get_column_ordinal_order_from_column_name(col)
            for col in all_columns
            if self.tabledata.get_column_type_from_column_name(col) == ColumnType.ORDINAL
        }
        RESULTS[self.result_id] = recalculate_regression_study(
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
