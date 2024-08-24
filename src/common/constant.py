from enum import Enum
import qtawesome as qta

DEBUG_LAYOUT = False

COLORS = ["#ffcccc", "#ccffcc", "#bbbbff", "#ffffbb", "#ffbbff", "#bbffff"]
COLORS_SELECTION = ["#ffbbbb", "#aaffaa", "#aaaaff", "#ffffaa", "#ffaaff", "#aaffff"]

MDASH = "—"
NDASH = "–"


class ColumnType(Enum):
    NOMINAL = "nominal"
    NUMERIC = "numeric"
    ORDINAL = "ordinal"
    CATEGORICAL = "categorical"


COLUMN_TYPE_ICONS = {
    ColumnType.NUMERIC: qta.icon("mdi.numeric", color="darkblue", opacity=0.7),
    ColumnType.NOMINAL: qta.icon("mdi6.alphabetical-variant", color="darkred", opacity=0.7),
    ColumnType.ORDINAL: qta.icon("ph.chart-bar", color="darkgreen", opacity=0.7),
}
