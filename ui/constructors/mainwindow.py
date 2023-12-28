from PyQt5 import QtCore, QtGui, QtWidgets

from ui.handlers.table_handler import CustomTableWidget
from PyQt5 import QtWebEngineWidgets
import resources_rc


class Table:
    def __init__(self, parent):
        self.tableWidget_2 = CustomTableWidget(parent)
        self.tableWidget_2.setMinimumSize(QtCore.QSize(50, 0))
        self.tableWidget_2.setAutoFillBackground(False)
        self.tableWidget_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tableWidget_2.setAlternatingRowColors(True)
        self.tableWidget_2.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableWidget_2.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.tableWidget_2.setShowGrid(True)
        self.tableWidget_2.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.horizontalHeader().setVisible(True)
        self.tableWidget_2.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.verticalHeader().setVisible(True)
        self.tableWidget_2.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.verticalHeader().setHighlightSections(True)
        self.tableWidget_2.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget_2.verticalHeader().setStretchLastSection(False)


def icon(path):
    _icon = QtGui.QIcon()
    _icon.addPixmap(
        QtGui.QPixmap(path),
        QtGui.QIcon.Normal,
        QtGui.QIcon.Off,
    )
    return _icon


class Frame2:
    def __init__(self, parent):
        self.frame_2 = QtWidgets.QFrame(parent)
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_4.setContentsMargins(0, 0, 0, -1)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.scrollArea = QtWidgets.QScrollArea(self.frame_2)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 138, 998))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.browser = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents)
        self.browser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.browser.setObjectName("browser")
        self.gridLayout_2.addWidget(self.browser, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_4.addWidget(self.scrollArea, 0, 0, 1, 1)


class Frame:
    def __init__(self, parent):
        self.frame = QtWidgets.QFrame(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(410, 0))
        self.frame.setMaximumSize(QtCore.QSize(410, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.Home = QtWidgets.QWidget()
        self.Home.setObjectName("Home")
        self.DescriptiveStatisticsButton = QtWidgets.QToolButton(self.Home)
        self.DescriptiveStatisticsButton.setGeometry(QtCore.QRect(60, 240, 101, 101))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/bar_chart/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.DescriptiveStatisticsButton.setIcon(icon1)
        self.DescriptiveStatisticsButton.setIconSize(QtCore.QSize(60, 60))
        self.DescriptiveStatisticsButton.setToolButtonStyle(
            QtCore.Qt.ToolButtonIconOnly
        )
        self.DescriptiveStatisticsButton.setObjectName("DescriptiveStatisticsButton")
        self.OpenFileButton = QtWidgets.QToolButton(self.Home)
        self.OpenFileButton.setGeometry(QtCore.QRect(60, 40, 101, 101))
        self.OpenFileButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/folder_open/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.OpenFileButton.setIcon(icon2)
        self.OpenFileButton.setIconSize(QtCore.QSize(60, 60))
        self.OpenFileButton.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.OpenFileButton.setObjectName("OpenFileButton")
        self.label = QtWidgets.QLabel(self.Home)
        self.label.setGeometry(QtCore.QRect(60, 150, 101, 61))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.Home)
        self.label_2.setGeometry(QtCore.QRect(60, 350, 101, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label_2.setObjectName("label_2")
        self.DescriptiveStatisticsButton_2 = QtWidgets.QToolButton(self.Home)
        self.DescriptiveStatisticsButton_2.setEnabled(False)
        self.DescriptiveStatisticsButton_2.setGeometry(QtCore.QRect(240, 240, 101, 101))
        self.DescriptiveStatisticsButton_2.setIcon(icon1)
        self.DescriptiveStatisticsButton_2.setIconSize(QtCore.QSize(60, 60))
        self.DescriptiveStatisticsButton_2.setToolButtonStyle(
            QtCore.Qt.ToolButtonIconOnly
        )
        self.DescriptiveStatisticsButton_2.setObjectName(
            "DescriptiveStatisticsButton_2"
        )
        self.label_3 = QtWidgets.QLabel(self.Home)
        self.label_3.setEnabled(False)
        self.label_3.setGeometry(QtCore.QRect(240, 350, 101, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label_3.setObjectName("label_3")
        self.SaveReportButton = QtWidgets.QToolButton(self.Home)
        self.SaveReportButton.setGeometry(QtCore.QRect(240, 40, 101, 101))
        self.SaveReportButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/save_alt/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.SaveReportButton.setIcon(icon3)
        self.SaveReportButton.setIconSize(QtCore.QSize(60, 60))
        self.SaveReportButton.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.SaveReportButton.setObjectName("SaveReportButton")
        self.label_4 = QtWidgets.QLabel(self.Home)
        self.label_4.setGeometry(QtCore.QRect(240, 150, 101, 61))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label_4.setObjectName("label_4")
        self.stackedWidget.addWidget(self.Home)
        self.Descriptive = QtWidgets.QWidget()
        self.Descriptive.setObjectName("Descriptive")
        self.listWidget_2 = QtWidgets.QListWidget(self.Descriptive)
        self.listWidget_2.setGeometry(QtCore.QRect(10, 423, 381, 231))
        self.listWidget_2.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget = QtWidgets.QListWidget(self.Descriptive)
        self.listWidget.setGeometry(QtCore.QRect(10, 93, 381, 271))
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setObjectName("listWidget")
        self.groupBox = QtWidgets.QGroupBox(self.Descriptive)
        self.groupBox.setGeometry(QtCore.QRect(10, 663, 116, 251))
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBox)
        self.checkBox_missing = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_missing.setChecked(True)
        self.checkBox_missing.setObjectName("checkBox_missing")
        self.formLayout.setWidget(
            1, QtWidgets.QFormLayout.LabelRole, self.checkBox_missing
        )
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setObjectName("checkBox_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.checkBox_3)
        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_4.setChecked(False)
        self.checkBox_4.setObjectName("checkBox_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.checkBox_4)
        self.checkBox_6 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_6.setChecked(True)
        self.checkBox_6.setObjectName("checkBox_6")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.checkBox_6)
        self.checkBox_7 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_7.setChecked(False)
        self.checkBox_7.setObjectName("checkBox_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.checkBox_7)
        self.checkBox_8 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_8.setChecked(True)
        self.checkBox_8.setObjectName("checkBox_8")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.checkBox_8)
        self.checkBox_9 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_9.setChecked(True)
        self.checkBox_9.setObjectName("checkBox_9")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.checkBox_9)
        self.HomeButton = QtWidgets.QToolButton(self.Descriptive)
        self.HomeButton.setGeometry(QtCore.QRect(10, 10, 61, 61))
        self.HomeButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/menu/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.HomeButton.setIcon(icon4)
        self.HomeButton.setIconSize(QtCore.QSize(40, 40))
        self.HomeButton.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.HomeButton.setObjectName("HomeButton")
        self.DownButton = QtWidgets.QPushButton(self.Descriptive)
        self.DownButton.setGeometry(QtCore.QRect(140, 370, 51, 51))
        self.DownButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/arrow_downward/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.DownButton.setIcon(icon5)
        self.DownButton.setIconSize(QtCore.QSize(40, 40))
        self.DownButton.setObjectName("DownButton")
        self.UpButton = QtWidgets.QPushButton(self.Descriptive)
        self.UpButton.setGeometry(QtCore.QRect(210, 370, 51, 51))
        self.UpButton.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(
                ":/mat/resources/material-icons-png-master/png/black/arrow_upward/round-4x.png"
            ),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.UpButton.setIcon(icon6)
        self.UpButton.setIconSize(QtCore.QSize(40, 40))
        self.UpButton.setObjectName("UpButton")
        self.stackedWidget.addWidget(self.Descriptive)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.stackedWidget.setCurrentIndex(1)

    def retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate

        self.DescriptiveStatisticsButton.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics")
        )
        self.label.setText(_translate("MainWindow", "Open File"))
        self.label_2.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Numeric)")
        )
        self.DescriptiveStatisticsButton_2.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics")
        )
        self.label_3.setText(
            _translate("MainWindow", "Descriptive\n" "Statistics\n" "(Literal)")
        )
        self.label_4.setText(_translate("MainWindow", "Save Report"))
        self.groupBox.setTitle(_translate("MainWindow", "Options"))
        self.checkBox.setText(_translate("MainWindow", "N"))
        self.checkBox_missing.setText(_translate("MainWindow", "Missing"))
        self.checkBox_3.setText(_translate("MainWindow", "Mean"))
        self.checkBox_4.setText(_translate("MainWindow", "Median"))
        self.checkBox_6.setText(_translate("MainWindow", "Std. deviation"))
        self.checkBox_7.setText(_translate("MainWindow", "Variance"))
        self.checkBox_8.setText(_translate("MainWindow", "Minimum"))
        self.checkBox_9.setText(_translate("MainWindow", "Maximum"))
        self.HomeButton.setShortcut(_translate("MainWindow", "Backspace"))


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
        # self.actionOpen.setIcon(icon2)
        self.actionOpen.setObjectName("actionOpen")
        self.actionDesctiptive_Statistics = QtWidgets.QAction(main_window)
        # self.actionDesctiptive_Statistics.setIcon(icon1)
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

    _ = resources_rc
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
