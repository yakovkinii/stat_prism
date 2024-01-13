import logging
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt

from core.mainwindow.layout import VerticalLayout
from core.mainwindow.results.result.common.frame import FrameClickable
from core.mainwindow.results.result.common.title import TitleWidget
from core.mainwindow.results.result.constant import RESULT_ITEM_WIDGET_CLASS
from core.shared import result_container
from core.utility import log_method

if TYPE_CHECKING:
    from core.mainwindow.results.ui import Results


class ResultWidget:
    @log_method
    def __init__(self, parent, results_instance, result_id, result):
        self.result_item_widgets = None
        self.title_widget = None
        self.result = result
        self.results_instance: Results = results_instance
        self.result_id = result_id

        self.frame = FrameClickable(parent)

        self.frame.clicked.connect(self.set_active)
        self.frame.setAttribute(Qt.WA_StyledBackground, True)

        self.layout = VerticalLayout(self.frame)

        self.update(self.result)

    @log_method
    def update(self, result):
        self.result = result
        for i in range(self.layout.count()):
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.title_widget = TitleWidget(self.frame, self.result.title, 10, centered=True)
        # self.title_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.layout.addWidget(self.title_widget)

        self.result_item_widgets = []
        for item in self.result.items:
            item_widget = RESULT_ITEM_WIDGET_CLASS[item.type](self.frame, self, item)
            self.result_item_widgets.append(item_widget)
            self.layout.addWidget(item_widget.frame)

        # vertical_spacer = QtWidgets.QSpacerItem(
        #     0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        # )
        # self.gridLayout.addItem(vertical_spacer)

    @log_method
    def set_active(self):
        logging.info(f"Clicked: {self.result_id}")
        if self.result_id == result_container.current_result:
            return
        result_container.current_result = self.result_id
        self.results_instance.mainwindow_instance.actionUpdateStudyFrame.trigger()
        self.results_instance.mainwindow_instance.actionUpdateResultsFrame.trigger()
