from src.results_panel.results.table_element import TableResultElementWidgetContainer
from src.results_panel.results.text_element import TextResultElementWidgetContainer

result_widget_container_registry = {
    "TextResultElement": TextResultElementWidgetContainer,
    "TableResultElement": TableResultElementWidgetContainer,
}
