from PyQt5 import QtCore, QtWidgets

from ui.constructors.misc import icon
from ui.constructors.results_frame import Frame2
from ui.constructors.study_frame import Frame
from ui.constructors.table_frame import Table


class UiMainWindow(object):
    def setupUi(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.resize(997, 1057)
        main_window.setWindowIcon(icon(":/mat/resources/Icon.ico"))

        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        self.table = Table(self.splitter)
        self.frame2_obj = Frame2(self.splitter)

        self.frame_obj = Frame(self.splitter)

        main_window.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(main_window)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 997, 26))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuAnalyse = QtWidgets.QMenu(self.menuBar)
        self.menuAnalyse.setObjectName("menuAnalyse")
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")

        main_window.setMenuBar(self.menuBar)
        self.actionOpen = QtWidgets.QAction(main_window)
        self.actionOpen.setObjectName("actionOpen")
        self.actionDesctiptive_Statistics = QtWidgets.QAction(main_window)
        self.actionDesctiptive_Statistics.setObjectName("actionDesctiptive_Statistics")
        self.actionAbout = QtWidgets.QAction(main_window)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionOpen)
        self.menuAnalyse.addAction(self.actionDesctiptive_Statistics)
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuAnalyse.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StatPrism"))

        self.frame_obj.retranslateUI()
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAnalyse.setTitle(_translate("MainWindow", "Analyse"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionDesctiptive_Statistics.setText(
            _translate("MainWindow", "Desctiptive Statistics")
        )
        self.actionAbout.setText(_translate("MainWindow", "About"))


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
