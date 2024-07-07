from src.trashcan.result.plot.ui import PlotResultItemWidget
from src.trashcan.result.table.ui import TableResultItemWidget
from src.trashcan.result.text.ui import TextResultItemWidget

RESULT_ITEM_WIDGET_CLASS = {
    "TextResultItem": TextResultItemWidget,
    "TableResultItem": TableResultItemWidget,
    "PlotResultItem": PlotResultItemWidget,
}
