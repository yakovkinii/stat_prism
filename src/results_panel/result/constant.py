from src.results_panel.result.plot.ui import PlotResultItemWidget
from src.results_panel.result.table.ui import TableResultItemWidget
from src.results_panel.result.text.ui import TextResultItemWidget

RESULT_ITEM_WIDGET_CLASS = {
    "TextResultItem": TextResultItemWidget,
    "TableResultItem": TableResultItemWidget,
    "PlotResultItem": PlotResultItemWidget,
}
