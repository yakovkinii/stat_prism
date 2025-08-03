import attrs
import pandas as pd
import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QLabel

from src.common.elements.utility.layout_helpers import empty_widget
from src.data_viewer.data_viewer import Data, TableViewer
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


@attrs.define()
class DataProcessingConfig:
    unique_id: int
    caption: str
    dataframe: pd.DataFrame  # Will be data model


class DataProcessing:
    def __init__(self, config: DataProcessingConfig, parent_widget, parent_class, root_class):
        self.config = config
        self.parent_widget = parent_widget
        self.parent_class = parent_class
        self.root_class = root_class

        # Create Data object instead of raw dataframe
        self.data = Data(self.config.dataframe)

        self.table_viewer = TableViewer(
            parent_widget=parent_widget,
            root_class=root_class,
            data=self.data,
        )

        self.widget, self.layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QHBoxLayout,
        )
        set_stylesheet(self.widget, css(background_color=Style.Color.BackgroundElevated))

        self.title = QLabel(self.config.caption)
        set_stylesheet(
            self.title,
            css(font_family=Style.FontFamily.SegoeUI, font_size=Style.FontSize.larger, text_align="left", margin="5px"),
        )
        self.layout.addWidget(self.title)

        self.layout.addWidget(self.table_viewer.button)
        self.layout.addStretch()