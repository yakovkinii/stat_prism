#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#


class BaseResultElement:
    def __init__(self, v2=False):
        if not v2:
            self.title: str = ...
            self.class_id: str = ...
            self.settings_panel_index: int = ...

    def get_html(self):
        return ...
