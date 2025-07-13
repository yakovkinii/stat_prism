#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from src.result_display_panel.result_widget_containers.html_widget_container import HTMLResultElementWidgetContainer
from src.result_display_panel.result_widget_containers.plot_widget_container import PlotResultElementWidgetContainer

result_widget_container_registry = {
    "HTMLTableV2": HTMLResultElementWidgetContainer,
    "HTMLMultiTableV2": HTMLResultElementWidgetContainer,
    "PlotV2": PlotResultElementWidgetContainer,
}
