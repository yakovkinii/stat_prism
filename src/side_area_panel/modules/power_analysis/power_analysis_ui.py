#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.power_analysis.power_analysis_result import (
    SOLVE_FOR,
    TAILS,
    TEST_TYPES,
)


class Elements(ItemInSidePanelWithAutoConfigHolder):
    # Power analysis is input-driven (no data source / column selector).
    test_type = IISPWACComboBox(label_text="Test:", items=TEST_TYPES)
    solve_for = IISPWACComboBox(label_text="Solve for:", items=SOLVE_FOR)
    tails = IISPWACComboBox(label_text="Tails:", items=TAILS)
    spacer = IISPWACSpacer()
    alpha = IISPWACLongTextEdit(label_text="Alpha (α):")
    power = IISPWACLongTextEdit(label_text="Power (1 − β):")
    effect_size = IISPWACLongTextEdit(label_text="Effect size (d / f / r):")
    sample_size = IISPWACLongTextEdit(label_text="Sample size (n per group):")
    n_groups = IISPWACLongTextEdit(label_text="Number of groups (ANOVA):")


class PowerAnalysis(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Power Analysis")
