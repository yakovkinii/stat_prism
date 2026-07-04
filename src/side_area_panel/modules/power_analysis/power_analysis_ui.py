#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.power_analysis.power_analysis_result import SOLVE_FOR, TAILS, TEST_TYPES


class Elements(ItemInSidePanelWithAutoConfigHolder):
    # Power analysis is input-driven (no data source / column selector).
    test_type = IISPWACComboBox(label_text="Test:", items=TEST_TYPES)
    solve_for = IISPWACComboBox(label_text="Solve for:", items=SOLVE_FOR)
    tails = IISPWACComboBox(label_text="Tails:", items=TAILS)
    spacer = IISPWACSpacer()
    # The quantity being solved for is an output, so its input box is disabled.
    alpha = IISPWACLongTextEdit(label_text="Alpha (α):")
    power = IISPWACLongTextEdit(
        label_text="Power (1 − β):",
        enabled_when=lambda kwargs: kwargs.get("solve_for") != "Power",
    )
    effect_size = IISPWACLongTextEdit(
        label_text="Effect size (d / f / r):",
        enabled_when=lambda kwargs: kwargs.get("solve_for") != "Effect size",
    )
    sample_size = IISPWACLongTextEdit(
        label_text="Sample size (n per group):",
        enabled_when=lambda kwargs: kwargs.get("solve_for") != "Sample size",
    )
    n_groups = IISPWACLongTextEdit(
        label_text="Number of groups (ANOVA):",
        enabled_when=lambda kwargs: kwargs.get("test_type") == "One-way ANOVA",
    )


class PowerAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Power Analysis")
