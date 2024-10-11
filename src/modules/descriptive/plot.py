from typing import List

import numpy as np
import pandas as pd

from src.common.result.classes.plot_result import Box, Colors, PlotResultElement, Scatter
from src.settings_panel.panels.registry import PanelRegistry


def create_box_plot(
    groups: List[pd.Series],
    group_names: List[str],
    column: str,
    grouping_column: str,
) -> PlotResultElement:
    plot_result = PlotResultElement(
        settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
        tab_title=f"Box Plot: Comparison of {column} within {grouping_column}",
        plot_title=f"Comparison of {column} within {grouping_column}",
        x_axis_title=grouping_column,
        y_axis_title=column,
        x_axis_items=group_names,
    )
    colors = Colors()
    for i, (group, group_name) in enumerate(zip(groups, group_names)):
        color = colors.get_color_list()

        iqr = np.percentile(group, 75) - np.percentile(group, 25)
        lower_whisker = np.max([np.min(group), np.percentile(group, 25) - 1.5 * iqr])
        upper_whisker = np.min([np.max(group), np.percentile(group, 75) + 1.5 * iqr])

        plot_result.items.append(Box.from_data(group, index=i, label=group_name, color=color))
        outliers = group[(group < lower_whisker) | (group > upper_whisker)]
        if len(outliers) > 0:
            plot_result.items.append(
                Scatter(
                    x=0 * outliers,
                    y=outliers,
                    label=f"Outliers for {group_name}",
                )
            )
    return plot_result
