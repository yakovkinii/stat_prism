from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen
from QCustomPlot_PyQt5 import QCPGraph, QCPScatterStyle, QCustomPlot

from core.mainwindow.results.result.common.title import TitleWidget
from core.objects import PlotResultItem
from core.utility import log_method


class PlotResultItemWidget:
    @log_method
    def __init__(self, parent, result_widget_instance, item: PlotResultItem):
        self.result_widget_instance = result_widget_instance
        self.item: PlotResultItem = item

        self.frame = QtWidgets.QFrame(parent)
        self.frame.setAttribute(Qt.WA_StyledBackground, True)
        self.title_widget = TitleWidget(self.frame, self.item.title)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(20, 0, 20, 0)

        self.gridLayout.addWidget(self.title_widget)
        self.customPlot = QCustomPlot(self.frame)
        self.gridLayout.addWidget(self.customPlot, 1, 0, QtCore.Qt.AlignLeft)
        graph0 = self.customPlot.addGraph()
        graph0.setPen(QPen(Qt.blue))
        graph0.setBrush(QBrush(QColor(0, 0, 255, 20)))

        self.customPlot.xAxis.setLabel(item.x_axis_title)
        self.customPlot.yAxis.setLabel(item.y_axis_title)
        graph0.setPen(QColor(50, 50, 50, 255))
        graph0.setLineStyle(QCPGraph.lsNone)
        graph0.setScatterStyle(QCPScatterStyle(QCPScatterStyle.ssDisc, 8))
        graph0.setData(item.dataframe.iloc[:, 0], item.dataframe.iloc[:, 1])

        minx = item.dataframe.iloc[:, 0].min()
        maxx = item.dataframe.iloc[:, 0].max()
        gapx = (maxx - minx) / 10
        miny = item.dataframe.iloc[:, 1].min()
        maxy = item.dataframe.iloc[:, 1].max()
        gapy = (maxy - miny) / 10
        if gapx == 0:
            gapx = 1
        if gapy == 0:
            gapy = 1
        self.customPlot.xAxis.setRange(minx - gapx, maxx + gapx)
        self.customPlot.yAxis.setRange(miny - gapy, maxy + gapy)

        # self.customPlot.rescaleAxes()
        self.customPlot.setFixedSize(500, 300)
        # self.customPlot.set
        # self.customPlot.setInteraction(QCP.iRangeDrag)
        # self.customPlot.setInteraction(QCP.iRangeZoom)
        # self.customPlot.setInteraction(QCP.iSelectPlottables)
