from src.common.elements.logo.logo import Logo
from src.settings_panel.panels.base.base import BasePanel


class Blank(BasePanel):
    def setup_ui(self):
        self.elements = {
            "logo": Logo(),
        }

        self.setup(stretch=False)
