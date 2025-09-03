#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import qtawesome as qta
from PySide6.QtCore import Qt

from src.pyside_ext.styling import Style

MDASH = "—"
NDASH = "–"

TABLE_OR_PLOT_ID_PLACEHOLDER = "<table_or_plot_id>"


class ColumnType(Enum):
    NOMINAL = "Nominal"
    NUMERIC = "Numeric"
    ORDINAL = "Ordinal"


COLUMN_TYPE_ICONS = {
    ColumnType.NUMERIC: qta.icon("mdi.numeric", color="darkblue", opacity=0.7),
    ColumnType.NOMINAL: qta.icon("mdi6.alphabetical-variant", color="darkred", opacity=0.7),
    ColumnType.ORDINAL: qta.icon("ph.chart-bar", color="darkgreen", opacity=0.7),
}

BASE_STYLES = (
    f"<style>"
    f".double-spacing {{ line-height: 1.5; }}"
    f".font {{ font-size: {Style.FontSize.regular}; font-family: 'Times New Roman'; }}"
    f"table, th, td {{ border-collapse: collapse; }}"
    f".meta {{ font-size: {Style.FontSize.smaller}; }}"
    f"</style>"
)


class SettingsPanelSize:
    width: int = 320
    tab_width: int = 300
    even_col_width: int = 130
    max_col_width: int = 200
