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
_TYPE_ICON_GLYPH = {
    ColumnType.NUMERIC: "mdi.numeric",
    ColumnType.NOMINAL: "mdi6.alphabetical-variant",
    ColumnType.ORDINAL: "ph.chart-bar",
    ColumnType.ID: "mdi.key",
}
_TYPE_ICON_COLOR = {
    ColumnType.NUMERIC: Style.Color.TypeNumeric.value,
    ColumnType.NOMINAL: Style.Color.TypeNominal.value,
    ColumnType.ORDINAL: Style.Color.TypeOrdinal.value,
    ColumnType.ID: Style.Color.TypeId.value,
}
# Dark, saturated variants for drawing on a column's (light pastel) colour tag, where the
# normal theme-tinted icons -- light in the dark UI theme -- would be hard to see.
_TYPE_ICON_COLOR_ON_LIGHT = {
    ColumnType.NUMERIC: "darkblue",
    ColumnType.NOMINAL: "darkred",
    ColumnType.ORDINAL: "darkgreen",
    ColumnType.ID: "#6a1b9a",
}

COLUMN_TYPE_ICONS = {
    ctype: qta.icon(glyph, color=_TYPE_ICON_COLOR[ctype], opacity=0.9)
    for ctype, glyph in _TYPE_ICON_GLYPH.items()
}
# Use when the icon sits on a column's pastel colour tag (see COLOR_ROLE in the data viewer).
COLUMN_TYPE_ICONS_ON_LIGHT = {
    ctype: qta.icon(glyph, color=_TYPE_ICON_COLOR_ON_LIGHT[ctype], opacity=0.95)
    for ctype, glyph in _TYPE_ICON_GLYPH.items()
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
