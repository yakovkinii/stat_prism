from PyQt5 import QtCore, QtWidgets

from ui.constructors.misc import icon
from ui.constructors.results.results_frame import Results
from ui.constructors.study.study_frame import Study
from ui.constructors.table.table_frame import Table


class MainWindow(object):
    def setupUi(self, main_window):
        main_window.setWindowIcon(icon(":/mat/resources/Icon.ico"))

        self.centralwidget = QtWidgets.QWidget(main_window)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout.addWidget(self.splitter)  # , 0, 0, 1, 1)

        self.table_frame = Table(self.splitter)
        self.results_frame = Results(self.splitter)
        self.study_frame = Study(self.splitter)

        main_window.setCentralWidget(self.centralwidget)

        self.menuBar = QtWidgets.QMenuBar(main_window)
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        main_window.setMenuBar(self.menuBar)

        self.actionAbout = QtWidgets.QAction(main_window)
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StatPrism"))
        self.table_frame.retranslateUI()
        self.study_frame.retranslateUI()
        self.results_frame.retranslateUI()
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAbout.setText(_translate("MainWindow", "About"))


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
