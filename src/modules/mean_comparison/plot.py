from typing import List

import pandas as pd

from src.common.result.classes.plot_result import Box, Colors, PlotResultElement, Scatter, ScatterPlotConfig
from src.settings_panel.panels.registry import PanelRegistry


def create_mean_comparison_plot(
    groups: List[pd.Series],
    group_names: List[str],
    column: str,
    grouping_column: str,
) -> PlotResultElement:
    plot_result = PlotResultElement(
        settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
        tab_title=f"Box Plot: Mean comparison of {column}",
        plot_title=f"Mean comparison of {column}",
        x_axis_title=grouping_column,
        y_axis_title=column,
        x_axis_items=group_names,
    )
    colors = Colors()
    for i, (group, group_name) in enumerate(zip(groups, group_names)):
        color = colors.get_color_list()
        plot_result.items.append(
            Scatter(
                x=pd.Series([i] * len(group)),
                y=group,
                label=group_name,
                config=ScatterPlotConfig(color=color, fill_alpha=30, line_alpha=50, jitter_x=1.0),
            )
        )

        plot_result.items.append(Box.from_data_mean_std(group, index=i, label=group_name, color=color))

    return plot_result
