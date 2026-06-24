#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import qtawesome as qta

from src.pyside_ext.styling import Style

MDASH = "—"
NDASH = "–"

TABLE_OR_PLOT_ID_PLACEHOLDER = "<table_or_plot_id>"


class ColumnType(Enum):
    NOMINAL = "Nominal"
    NUMERIC = "Numeric"
    ORDINAL = "Ordinal"
    ID = "ID"


# The mandatory identifier column is always named exactly this.
ID_COLUMN_NAME = "ID"


# Pastel palette for per-column tagging (data-viewer header backgrounds, column-selector
# items). A column's color is None/0 when untagged. Kept deliberately soft so text stays
# readable on top.
PASTEL_PALETTE = [
    "#ffd6d6",  # red
    "#ffe3c2",  # orange
    "#fff5ba",  # yellow
    "#e2f5c4",  # lime
    "#c8f0e0",  # teal
    "#cfe6ff",  # blue
    "#d9d6ff",  # indigo
    "#f0d6ff",  # violet
    "#ffd6ec",  # pink
    "#e6e6e6",  # gray
]


def hex_to_argb(color):
    """'#rrggbb' (or 'rrggbb') -> openpyxl 'AARRGGBB' (opaque). None for falsy/untagged."""
    if not isinstance(color, str) or not color:
        return None
    return "FF" + color.lstrip("#").upper()


def argb_to_hex(argb):
    """openpyxl fill colour ('AARRGGBB' or 'RRGGBB') -> '#rrggbb'. None if not a literal RGB."""
    if not isinstance(argb, str) or len(argb) not in (6, 8):
        return None
    rgb = argb[-6:]
    return "#" + rgb.lower()


# Type colours come from the central scheme (Style.Color); medium-bright so the icons read on
# the dark UI as well as on the (light) pastel column tags in the data viewer.
COLUMN_TYPE_ICONS = {
    ColumnType.NUMERIC: qta.icon("mdi.numeric", color=Style.Color.TypeNumeric.value, opacity=0.9),
    ColumnType.NOMINAL: qta.icon("mdi6.alphabetical-variant", color=Style.Color.TypeNominal.value, opacity=0.9),
    ColumnType.ORDINAL: qta.icon("ph.chart-bar", color=Style.Color.TypeOrdinal.value, opacity=0.9),
    ColumnType.ID: qta.icon("mdi.key", color=Style.Color.TypeId.value, opacity=0.9),
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
    popup_minimum_width: int = 700
    tab_width: int = 300
    even_col_width: int = 130
    max_col_width: int = 200
