from typing import Dict


class BaseResult:
    def __init__(self, unique_id):
        # Unique integer id, not for display
        self.unique_id: int = unique_id
        # Result elements, each takes one tab
        self.result_elements: Dict[str, BaseResultElement] = {}
        # Display title (result selector)
        self.title: str = ...
        # Display title context (result display)
        self.title_context: str = ...
        # Settings panel index for activating the result
        self.settings_panel_index: int = ...
        # Result config
        self.config = ...
        # Flag for updating the result
        self.needs_update: bool = False

    def element_keys(self):
        return list(self.result_elements.keys())

    def configure(self, *args, **kwargs):
        pass


class BaseResultElement:
    def __init__(self):
        self.title: str = ...
        self.class_id: str = ...
        self.settings_panel_index: int = ...
