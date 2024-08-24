from typing import List, Union

from src.common.result.classes.base_result import BaseResultElement


class Scatter:
    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        self.label = label


class PlotResultElement(BaseResultElement):
    def __init__(
        self,
        tab_title="Plot Result Element",
        plot_id="1",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
    ):
        super().__init__()
        self.title: str = tab_title
        self.class_id: str = "PlotResultElement"
        self.items: List[Union[Scatter]] = []
        self.plot_id = plot_id
        self.plot_title = plot_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
