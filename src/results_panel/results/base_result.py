from typing import Dict, List

from src.results_panel.results.base_element import BaseResultElement


class BaseResult:
    def __init__(self, unique_id):
        self.unique_id: int = unique_id
        self.result_elements: Dict[str, BaseResultElement] = {}
        self.title: str = ...
        self.settings_panel_index: int = ...
        self.config = ...

    def configure(self, *args, **kwargs):
        pass
