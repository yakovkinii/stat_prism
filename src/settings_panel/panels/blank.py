#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.pyside_ext.elements.logo import Logo
from src.settings_panel.panels.base import BasePanel
from src.settings_panel.registry import PanelRegistry


class Blank(BasePanel):
    def setup_ui(self):
        self.elements = {
            "logo": Logo(),
        }

        self.setup(stretch=False, navigation_elements=False)
        self.elements["logo"].widget.clicked.connect(
            lambda: self.root_class.action_activate_panel_by_index(
                PanelRegistry.SELECT_DATA_ANALYSIS.settings_stacked_widget_index
            )
        )
