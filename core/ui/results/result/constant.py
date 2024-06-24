from core.ui.results.result.plot.ui import PlotResultItemWidget
from core.ui.results.result.table.ui import TableResultItemWidget
from core.ui.results.result.text.ui import TextResultItemWidget

RESULT_ITEM_WIDGET_CLASS = {
    "TextResultItem": TextResultItemWidget,
    "TableResultItem": TableResultItemWidget,
    "PlotResultItem": PlotResultItemWidget,
}
