from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import numpy as np


class BoxPlotItem(pg.GraphicsObject):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.calculate_statistics()
        self.generatePicture()

    def calculate_statistics(self):
        # Calculate key statistics for the box plot
        self.q1 = np.percentile(self.data, 25)
        self.q3 = np.percentile(self.data, 75)
        self.median = np.median(self.data)
        self.iqr = self.q3 - self.q1
        self.lower_whisker = np.min(self.data[self.data >= self.q1 - 1.5 * self.iqr])
        self.upper_whisker = np.max(self.data[self.data <= self.q3 + 1.5 * self.iqr])
        self.outliers = self.data[(self.data < self.lower_whisker) | (self.data > self.upper_whisker)]

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen('k', width=2))

        # Box representing IQR
        painter.setBrush(pg.mkBrush(150, 150, 255, 100))
        painter.drawRect(QtCore.QRectF(-0.2, self.q1, 0.4, self.q3 - self.q1))

        # Median line
        painter.setPen(pg.mkPen('r', width=2))
        painter.drawLine(QtCore.QPointF(-0.2, self.median), QtCore.QPointF(0.2, self.median))

        for value in self.outliers:
            painter.drawEllipse(QtCore.QPointF(0, value), 0.05, 0.05)

        # Whiskers
        painter.setPen(pg.mkPen('k', width=2))
        painter.drawLine(QtCore.QPointF(0, self.lower_whisker), QtCore.QPointF(0, self.q1))  # Lower whisker
        painter.drawLine(QtCore.QPointF(0, self.q3), QtCore.QPointF(0, self.upper_whisker))  # Upper whisker

        # Whisker caps
        painter.drawLine(QtCore.QPointF(-0.1, self.lower_whisker), QtCore.QPointF(0.1, self.lower_whisker))  # Lower cap
        painter.drawLine(QtCore.QPointF(-0.1, self.upper_whisker), QtCore.QPointF(0.1, self.upper_whisker))  # Upper cap

        painter.end()

    def paint(self, painter, option, widget):
        # Draw the pre-rendered box, whiskers, and median line
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


# Set up the application and plot
if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # Example data for box plot
    data = np.random.normal(50, 10, 100)
    data = np.append(data, [100, 105, 3])  # Add some outliers

    # Create a plot widget
    plot_widget = pg.PlotWidget()
    plot_widget.setBackground('w')
    plot_widget.setYRange(np.min(data) - 10, np.max(data) + 10)
    plot_widget.setXRange(-1, 1)

    # Create and add the BoxPlotItem
    box_plot_item = BoxPlotItem(data)
    plot_widget.addItem(box_plot_item)

    # Show the plot
    plot_widget.show()

    app.exec()
