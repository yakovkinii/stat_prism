#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel

NORMALITY_TESTS = ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"]


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variable(s):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=10,
                minimum_columns=1,
            ),
            Field(
                name="Grouping Column (optional):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    # --- Tables ---
    extended_stats = IISPWACCheckBox(label_text="Extended numeric stats", default_state=False)
    frequency_table = IISPWACCheckBox(label_text="Categorical frequency table", default_state=True)
    show_normality = IISPWACCheckBox(label_text="Normality test", default_state=True)
    normality_test = IISPWACComboBox(label_text="Normality test:", items=NORMALITY_TESTS)
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=False)
    number_columns = IISPWACCheckBox(label_text="Number variables in tables", default_state=False)
    # --- Plots (each opt-in) ---
    show_distribution = IISPWACCheckBox(label_text="Distribution plots", default_state=False)
    show_box = IISPWACCheckBox(label_text="Box plots", default_state=False)
    mark_outliers = IISPWACCheckBox(label_text="Label outliers on box plots", default_state=False)
    show_frequency_bars = IISPWACCheckBox(label_text="Frequency bar charts", default_state=False)
    show_pie = IISPWACCheckBox(label_text="Pie charts", default_state=False)
    show_qq = IISPWACCheckBox(label_text="Q-Q plots", default_state=False)
    # --- Distribution-plot controls ---
    show_kde = IISPWACCheckBox(label_text="Show KDE curve", default_state=True)
    # Bin / KDE controls only apply while distribution plots (and KDE) are shown.
    bin_width = IISPWACLongTextEdit(
        label_text="Bin width (blank: auto):",
        enabled_when=lambda kwargs: bool(kwargs.get("show_distribution")),
    )
    bin_reference = IISPWACLongTextEdit(
        label_text="Bin reference (blank: auto):",
        enabled_when=lambda kwargs: bool(kwargs.get("show_distribution")),
    )
    kde_smoothing = IISPWACLongTextEdit(
        label_text="KDE smoothing (blank: auto; <1: sharper; >1: smoother):",
        enabled_when=lambda kwargs: bool(kwargs.get("show_distribution")) and bool(kwargs.get("show_kde")),
    )


class Descriptive(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Descriptive Statistics")
