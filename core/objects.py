from typing import Callable, Dict

import pandas as pd

from core.constants import NO_RESULT_SELECTED


class Result:
    def __init__(self, result_id: int, module_name: str):
        self.result_id = result_id
        self.module_name = module_name
        self.content = ...
        self.metadata = ...


class ResultContainer:
    def __init__(self):
        self.results: Dict[int, Result] = dict()
        self.current_result = NO_RESULT_SELECTED


class Data:
    def __init__(self, df: pd.DataFrame = None):
        if df is None:
            self.df = None
        else:
            self.df = df


class ModelRegistryItem:
    def __init__(
        self,
        model_name: str,
        stacked_widget_index: int,
        setup_from_result_handler: Callable,
        run_handler: Callable,
    ):
        self.model_name = model_name
        self.stacked_widget_index = stacked_widget_index
        self.setup_from_result_handler = setup_from_result_handler
        self.run_handler = run_handler
