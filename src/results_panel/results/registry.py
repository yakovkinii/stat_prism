from src.results_panel.results.common.html_element import HTMLResultElementWidgetContainer
from src.results_panel.results.correlation.correlation_table_element import CorrelationTableResultElementWidgetContainer
from src.results_panel.results.descriptive.descriptive_table_element import DescriptiveTableResultElementWidgetContainer
from src.results_panel.results.common.text_element import TextResultElementWidgetContainer

result_widget_container_registry = {
    "TextResultElement": TextResultElementWidgetContainer,
    "HTMLResultElement": HTMLResultElementWidgetContainer,
    "DescriptiveTableResultElement": DescriptiveTableResultElementWidgetContainer,
    "CorrelationTableResultElement": CorrelationTableResultElementWidgetContainer,
}
