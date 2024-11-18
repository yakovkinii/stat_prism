#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from PySide6 import QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QVBoxLayout

from src.common.elements.base.base import BasePanelElement
from src.common.elements.utility.layout_helpers import empty_widget, widget_in_layout
from src.common.elements.utility.primitive_elements import QWidgetClickable


class Logo(BasePanelElement):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.widget, self.layout = empty_widget(
            widget_class=QWidgetClickable,
            parent=self.parent_widget,
            inner_layout_class=QVBoxLayout,
        )

        self.watermark = widget_in_layout(
            layout=self.layout,
            widget=QLabel(self.widget),
            setup=lambda widget, layout: [
                widget.setPixmap(QIcon(":/mat/resources/watermark.png").pixmap(250, 250)),
                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter),
                widget.setFixedHeight(500),
            ],
        )
