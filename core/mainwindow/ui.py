from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from core.common_ui import icon
from core.constants import OUTPUT_WIDTH
from core.mainwindow.results.ui import Results
from core.mainwindow.study.ui import Study
from core.mainwindow.table.ui import Table
from core.utility import log_method_noarg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        #   centralwidget
        #       gridLayout
        #           splitter
        #               table_frame
        #               results_frame
        #               study_frame

        super().__init__()
        self.setWindowIcon(icon(":/mat/resources/Icon.ico"))

        self.centralwidget = QtWidgets.QWidget(self)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout.addWidget(self.splitter)

        self.table_frame: Table = Table(self.splitter)
        self.results_frame: Results = Results(self.splitter)
        self.study_frame: Study = Study(self.splitter)

        self.setCentralWidget(self.centralwidget)

        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.setMenuBar(self.menuBar)

        self.actionAbout = QtWidgets.QAction(self)
        self.actionAbout.triggered.connect(self.about_handler)

        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self._collapse_results()

        # Custom actions
        self.study_frame.actionUpdateTableFrame.triggered.connect(
            self.table_frame.update
        )
        self.study_frame.actionUpdateResultsFrame.triggered.connect(
            self.update_results_frame
        )

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StatPrism"))
        self.table_frame.retranslateUI()
        self.study_frame.retranslateUI()
        self.results_frame.retranslateUI()
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAbout.setText(_translate("MainWindow", "About"))

    @log_method_noarg
    def about_handler(self):
        QMessageBox.about(
            self,
            "StatPrism",
            "StatPrism Professional \nVersion: 0.1 \n(C) 2023 I.Y. and A.B.",
        )

    @log_method_noarg
    def _collapse_results(self):
        # cannot use actual sizes because the frame is not fully loaded yet
        self.splitter.setSizes([1, 0, 1])

    @log_method_noarg
    def _uncollapse_results(self):
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setSizes([sizes[0] - OUTPUT_WIDTH, OUTPUT_WIDTH, sizes[2]])

    @log_method_noarg
    def update_results_frame(self):
        self.results_frame.update()
        self._uncollapse_results()
