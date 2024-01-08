from core.mainwindow.results.result.plot.ui import PlotResultItemWidget
from core.mainwindow.results.result.table.ui import TableResultItemWidget
from core.mainwindow.results.result.text.ui import TextResultItemWidget

RESULT_ITEM_WIDGET_CLASS = {
    "TextResultItem": TextResultItemWidget,
    "TableResultItem": TableResultItemWidget,
    "PlotResultItem": PlotResultItemWidget,
}
