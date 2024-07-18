from src.results_panel.results.common.html_element import HTMLResultElementWidgetContainer
from src.results_panel.results.common.plot_element import PlotResultElementWidgetContainer

result_widget_container_registry = {
    "HTMLResultElement": HTMLResultElementWidgetContainer,
    "PlotResultElement": PlotResultElementWidgetContainer,
}
