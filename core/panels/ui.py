from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QStackedWidget, QHBoxLayout

from core.panels.common.common_ui import icon
from core.registry.constants import OUTPUT_WIDTH
from core.panels.data_panel.ui import DataPanelClass
from core.registry.utility import log_method_noarg, log_method
from core.panels.settings.ui import SettingsPanelClass


class MainWindowClass(QtWidgets.QMainWindow):
    """
    Root class and root widget
    """

    def __init__(self):
        super().__init__()

        # Setup
        self.widget = self  # split class and widget for clarity

        # Definitions
        self.central_widget = QtWidgets.QWidget(self.widget)
        self.central_widget_layout = QHBoxLayout(self.central_widget)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget_layout.setSpacing(0)
        self.stacked_widget = QStackedWidget()
        self.data_panel: DataPanelClass = DataPanelClass(
            parent_widget=self.stacked_widget, parent_class=self.widget, root_class=self
        )
        self.settings_panel: SettingsPanelClass = SettingsPanelClass(
            parent_widget=self.stacked_widget, parent_class=self.widget, root_class=self
        )

        # self.menu = QtWidgets.QMenuBar(self.widget)
        # self.menu_help = QtWidgets.QMenu(self.menu)
        # self.action_about = QtWidgets.QAction(self.widget)

        # Relations
        self.widget.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.stacked_widget)
        self.central_widget_layout.addWidget(self.settings_panel.widget)

        self.stacked_widget.addWidget(self.data_panel.widget)
        # self.menu = QtWidgets.QMenuBar(self.widget)
        # self.menu_help = QtWidgets.QMenu(self.menu)
        # self.action_about = QtWidgets.QAction(self.widget)

        # self.widget.setMenuBar(self.menu)
        # self.menu.addAction(self.menu_help.menuAction())
        # self.menu_help.addAction(self.action_about)
        # self.action_about.triggered.connect(self.about_handler)

        # Misc
        self.setWindowIcon(icon(":/mat/resources/Icon.ico"))

        # Post-init
        self.stacked_widget.setCurrentIndex(0)

        self.retranslateUi(self)
        # QtCore.QMetaObject.connectSlotsByName(self)

        # self._collapse_results()

        # Custom actions
        # self.actionUpdateStudyFrame = QtWidgets.QAction(self)
        # self.actionUpdateTableFrame = QtWidgets.QAction(self)
        # self.actionUpdateResultsFrame = QtWidgets.QAction(self)

        # self.actionUpdateStudyFrame.triggered.connect(self.study_frame.update)
        # self.actionUpdateResultsFrame.triggered.connect(self.update_results_frame)
        # self.actionUpdateTableFrame.triggered.connect(self.data_panel.update)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindowClass", "StatPrism"))
        # self.data_panel.retranslateUI()
        self.settings_panel.retranslateUI()
        # self.results_frame.retranslateUI()
        # self.menu_help.setTitle(_translate("MainWindowClass", "Help"))
        # self.action_about.setText(_translate("MainWindowClass", "About"))


    @log_method_noarg
    def action_update_data_panel(self):
        raise NotImplementedError("deprecated action")
        # self.data_panel.update()

    @log_method
    def action_activate_column_panel(self, column_index):
        if (self.settings_panel.stacked_widget.currentIndex == self.settings_panel.column_panel_index) and (
            self.settings_panel.column_panel.column_index == column_index
        ):
            return
        self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.column_panel_index)
        self.settings_panel.column_panel.configure(column_index)

    @log_method_noarg
    def action_activate_home_panel(self):
        self.settings_panel.stacked_widget.setCurrentIndex(self.settings_panel.home_panel_index)

    @log_method
    def action_activate_panel_by_index(self, index):
        if index is not None:
            self.settings_panel.stacked_widget.setCurrentIndex(index)

    @log_method
    def action_select_table_column(self, column_index):
        self.data_panel.tableview.selectColumn(column_index)
