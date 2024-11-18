#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from src.result_display_panel.result_widget_containers.html_widget_container import HTMLResultElementWidgetContainer
from src.result_display_panel.result_widget_containers.plot_widget_container import PlotResultElementWidgetContainer

result_widget_container_registry = {
    "HTMLResultElement": HTMLResultElementWidgetContainer,
    "PlotResultElement": PlotResultElementWidgetContainer,
}
