#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from typing import List

import pandas as pd

from src.common.result.classes.plot_result import Box, Colors, PlotV2


def create_box_plot(
    groups: List[pd.Series],
    group_names: List[str],
    column: str,
    grouping_column: str,
) -> PlotV2:
    plot_result = PlotV2(
        tab_title=f"Box Plot: Comparison of {column} within {grouping_column}",
        plot_title=f"Comparison of {column} within {grouping_column}",
        x_axis_title=grouping_column,
        y_axis_title=column,
        x_axis_items=group_names,
    )
    colors = Colors()
    for i, (group, group_name) in enumerate(zip(groups, group_names)):
        color = colors.get_color_list()
        plot_result.items.append(Box.from_data(group, index=i, label=group_name, color=color))

    return plot_result
