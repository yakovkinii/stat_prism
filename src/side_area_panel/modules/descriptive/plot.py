#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import pandas as pd

from src.common.qcolor import Colors
from src.side_area_panel.modules.common.result.plot_result import Box, PlotV2


def create_box_plot(
    groups: List[pd.Series],
    group_names: List[str],
    column: str,
    grouping_column: str,
) -> PlotV2:
    items = []
    colors = Colors()
    for i, (group, group_name) in enumerate(zip(groups, group_names)):
        color = colors.get_color_list()
        items.append(Box.from_data(group, index=i, label=group_name, color=color))

    plot_result = PlotV2(
        items=items,
        title=f"Box Plot: Comparison of {column} within {grouping_column}",
        plot_title=f"Comparison of {column} within {grouping_column}",
        x_axis_title=grouping_column,
        y_axis_title=column,
        x_axis_items=group_names,
    )
    return plot_result
