import math

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from QCustomPlot_PyQt5 import QCP, QCustomPlot

from core.mainwindow.results.result.common.title import TitleWidget
from core.objects import TextResultItem
from core.utility import log_method


class PlotResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: TextResultItem):
        self.result_widget_instance = result_widget_instance
        self.item: TextResultItem = item

        self.frame = QtWidgets.QFrame(parent)
        self.frame.setAttribute(Qt.WA_StyledBackground, True)
        self.title_widget = TitleWidget(self.frame, self.item.title)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(20, 0, 20, 0)

        self.gridLayout.addWidget(self.title_widget)
        self.customPlot = QCustomPlot(self.frame)
        self.gridLayout.addWidget(self.customPlot)
        graph0 = self.customPlot.addGraph()
        # graph0.setPen(QPen(Qt.blue))
        # graph0.setBrush(QBrush(QColor(0, 0, 255, 20)))

        graph1 = self.customPlot.addGraph()
        # graph1.setPen(QPen(Qt.red))

        x, y0, y1 = [], [], []
        for i in range(251):
            x.append(i)
            y0.append(math.exp(-i / 150.0) * math.cos(i / 10.0))  # exponentially decaying cosine
            y1.append(math.exp(-i / 150.0))  # exponential envelope

        graph0.setData(x, y0)
        graph1.setData(x, y1)

        self.customPlot.rescaleAxes()
        self.customPlot.setFixedSize(500, 300)
        # self.customPlot.set
        self.customPlot.setInteraction(QCP.iRangeDrag)
        self.customPlot.setInteraction(QCP.iRangeZoom)
        self.customPlot.setInteraction(QCP.iSelectPlottables)
