#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import QMenu, QMenuBar, QProgressBar, QVBoxLayout

USER_GUIDE_URL = "https://stat-prism.readthedocs.io/en/latest/"

from src.common.constant import SettingsPanelSize
from src.common.languages import LANGUAGE, Languages
from src.common.theme import THEME, Themes
from src.common.ui_theme import IS_DARK_THEME, write_ui_value
from src.pyside_ext.elements.utility.layout_helpers import widget_in_layout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.registry import PanelRegistry, PanelRegistryItem
from src.side_area_panel.blueprint.registry_injector import (
    inject_classes_to_panel_registry,
)
from src.side_area_panel.modules.registry import ModuleRegistry, ModuleRegistryItem
from src.side_area_panel.modules.registry_injector import (
    inject_classes_to_module_registry,
)

if TYPE_CHECKING:
    from src.ui_main import MainWindowClass


class SettingsPanelClass:
    def __init__(self, parent_widget, parent_class, root_class):
        # Setup
        self.root_class: MainWindowClass = root_class
        self.parent_class: MainWindowClass = parent_class
        self.widget = QtWidgets.QWidget(parent_widget)

        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.widget_layout)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setFixedWidth(SettingsPanelSize.width)

        # Definition
        self.stacked_widget = QtWidgets.QStackedWidget(self.widget)

        self.max_used_panel_index = None

        self.panels = []

        self.widget_layout.addWidget(self.stacked_widget)

        self.progress_bar = widget_in_layout(
            widget=QProgressBar(self.widget),
            layout=self.widget_layout,
            setup=lambda w, l: [
                w.setTextVisible(False),
                # w.setFixedHeight(10),
                w.hide(),
            ],
        )

        # Create a file menu and add actions
        menu_bar = QMenuBar(self.widget)
        self.widget_layout.setMenuBar(menu_bar)
        set_stylesheet(
            menu_bar,
            css(
                border_bottom=Style.General.border,
                border_bottom_color=Style.Color.BorderElevated,
                background_color=Style.Color.BackgroundElevated,
            ),
        )

        file_menu = QMenu("File", self.widget)
        settings_menu = QMenu("Settings", self.widget)
        language_menu = QMenu("Language", self.widget)
        plot_theme_menu = QMenu("Plot theme", self.widget)
        ui_theme_menu = QMenu("UI theme", self.widget)
        help_menu = QMenu("Help", self.widget)

        # ----- File menu: documents | recalculate | exit ----- (handlers wired below)
        self.open_action = QAction("Open…", self.widget)
        self.save_action = QAction("Save", self.widget)
        self.save_as_action = QAction("Save As…", self.widget)
        self.copy_all_action = QAction("Copy All Results", self.widget)
        self.export_report_action = QAction("Export Report (HTML)…", self.widget)
        self.collapse_all_action = QAction("Collapse All", self.widget)
        self.recalculate_all_action = QAction("Recalculate All", self.widget)
        self.exit_action = QAction("Exit", self.widget)
        for action in (self.open_action, self.save_action, self.save_as_action):
            file_menu.addAction(action)
        file_menu.addSeparator()
        file_menu.addAction(self.copy_all_action)
        file_menu.addAction(self.export_report_action)
        file_menu.addAction(self.collapse_all_action)
        file_menu.addSeparator()
        file_menu.addAction(self.recalculate_all_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # ----- Settings menu: language | plot theme | UI theme | auto-recalculate -----
        self.en_action = QAction("English", self.widget)
        self.ua_action = QAction("Українська", self.widget)
        self.en_action.setCheckable(True)
        self.ua_action.setCheckable(True)
        self.en_action.setChecked(LANGUAGE.is_en())
        self.ua_action.setChecked(LANGUAGE.is_ua())
        language_menu.addAction(self.en_action)
        language_menu.addAction(self.ua_action)

        # One checkable action per plot theme (driven by the Themes enum, so adding a
        # theme there automatically adds a menu entry).
        self.theme_actions = {}
        for theme in Themes:
            theme_action = QAction(theme.value, self.widget)
            theme_action.setCheckable(True)
            theme_action.setChecked(theme.value == THEME.name())
            theme_action.triggered.connect(lambda _checked=False, t=theme: self.set_theme(t))
            plot_theme_menu.addAction(theme_action)
            self.theme_actions[theme] = theme_action

        # UI (chrome) theme: light/dark. Persisted to statprism.ini and applied on the
        # next start (Style.Color captures the palette at import time).
        self.ui_theme_actions = {}
        for ui_name in ("light", "dark"):
            ui_action = QAction(ui_name.capitalize(), self.widget)
            ui_action.setCheckable(True)
            ui_action.setChecked((ui_name == "dark") == IS_DARK_THEME)
            ui_action.triggered.connect(lambda _checked=False, n=ui_name: self.set_ui_theme(n))
            ui_theme_menu.addAction(ui_action)
            self.ui_theme_actions[ui_name] = ui_action

        # Auto-recalculate: when on (default), changing a data-processing study recomputes
        # every dependent study immediately. When off, dependents are only flagged (their
        # Refresh button turns an alarm colour) until recalculated.
        self.auto_recalculate_action = QAction("Auto-recalculate", self.widget)
        self.auto_recalculate_action.setCheckable(True)
        self.auto_recalculate_action.setChecked(True)
        self.auto_recalculate_action.toggled.connect(self.set_auto_recalculate)

        settings_menu.addMenu(language_menu)
        settings_menu.addSeparator()
        settings_menu.addMenu(plot_theme_menu)
        settings_menu.addSeparator()
        settings_menu.addMenu(ui_theme_menu)
        settings_menu.addSeparator()
        settings_menu.addAction(self.auto_recalculate_action)

        # ----- Help menu -----
        self.about_action = QAction("About", self.widget)
        self.user_guide_action = QAction("User Guide", self.widget)
        help_menu.addAction(self.user_guide_action)
        help_menu.addAction(self.about_action)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(settings_menu)
        menu_bar.addMenu(help_menu)

        # Add all panels
        inject_classes_to_panel_registry()
        for panel in PanelRegistry:
            self.add_panel(panel.value)

        # Add all modules
        inject_classes_to_module_registry()
        for module in ModuleRegistry:
            self.add_module(module.value)

        # post-init
        self.stacked_widget.setCurrentIndex(PanelRegistry.HOME_INITIAL.value.settings_stacked_widget_index)

        self.en_action.triggered.connect(self.set_language_EN)
        self.ua_action.triggered.connect(self.set_language_UA)
        self.about_action.triggered.connect(PanelRegistry.HOME.value.ui_instance.about_handler)
        self.user_guide_action.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl(USER_GUIDE_URL))
        )

        # File menu: panels now exist, so resolve their handlers at trigger time via lambdas.
        self.open_action.triggered.connect(lambda: PanelRegistry.HOME_INITIAL.value.ui_instance.open_handler())
        self.save_action.triggered.connect(lambda: PanelRegistry.HOME.value.ui_instance.save_handler())
        self.save_as_action.triggered.connect(lambda: PanelRegistry.HOME.value.ui_instance.save_as_handler())
        self.copy_all_action.triggered.connect(lambda: self.root_class.main_area_panel.copy_all_results())
        self.export_report_action.triggered.connect(lambda: self.root_class.main_area_panel.export_report_html())
        self.collapse_all_action.triggered.connect(lambda: self.root_class.main_area_panel.collapse_all())
        self.recalculate_all_action.triggered.connect(lambda: self.root_class.main_area_panel.recompute_all())
        self.exit_action.triggered.connect(lambda: self.root_class.close())

    def set_language_EN(self):
        LANGUAGE.set_language(Languages.EN)
        write_ui_value("language", Languages.EN.value)
        self.en_action.setChecked(True)
        self.ua_action.setChecked(False)
        self.root_class.main_area_panel.recompute_all()

    def set_language_UA(self):
        LANGUAGE.set_language(Languages.UA)
        write_ui_value("language", Languages.UA.value)
        self.en_action.setChecked(False)
        self.ua_action.setChecked(True)
        self.root_class.main_area_panel.recompute_all()

    def set_ui_theme(self, name: str):
        """Persist the UI (chrome) theme to statprism.ini. It only takes effect on the next
        start, because Style.Color captures the palette at import time -- so prompt the user."""
        write_ui_value("theme", name)
        for candidate, action in self.ui_theme_actions.items():
            action.setChecked(candidate == name)
        QtWidgets.QMessageBox.information(
            self.widget,
            "UI theme",
            "The UI theme will change the next time you start StatPrism.",
        )

    def set_auto_recalculate(self, enabled: bool):
        self.root_class.main_area_panel.auto_recalculate = enabled

    def set_theme(self, theme: Themes):
        THEME.set_theme(theme)
        write_ui_value("plot_theme", theme.value)
        for candidate, action in self.theme_actions.items():
            action.setChecked(candidate == theme)
        # Recompute so every plot rebuilds with the new theme defaults. Each setting
        # adopts the new default unless the user had changed it from its previous
        # default, in which case load_settings_from carries the edit over.
        self.root_class.main_area_panel.recompute_all()
        # The recompute rebuilds result elements, so any currently-focused study's
        # settings panel would reference stale elements. Deselect and return home.
        self.root_class.main_area_panel.update_focus(None, None)
        self.root_class.action_activate_panel_by_index(PanelRegistry.HOME.settings_stacked_widget_index)

    def get_available_index(self):
        if self.max_used_panel_index is None:
            self.max_used_panel_index = 0
            return 0
        self.max_used_panel_index += 1
        return self.max_used_panel_index

    def add_module(self, panel_registry_item: ModuleRegistryItem):
        panel_registry_item.settings_stacked_widget_index = self.get_available_index()
        panel_registry_item.ui_instance = panel_registry_item.ui_class(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=panel_registry_item.settings_stacked_widget_index,
        )
        panel_registry_item.ui_instance.main_function = panel_registry_item.main_function
        panel_registry_item.ui_instance.setup_ui()
        self.panels.append(panel_registry_item.ui_instance)
        self.stacked_widget.addWidget(panel_registry_item.ui_instance.widget)

    def add_panel(self, panel_registry_item: PanelRegistryItem):
        panel_registry_item.settings_stacked_widget_index = self.get_available_index()
        if panel_registry_item.content_class is not None:
            for content_class in panel_registry_item.content_class:
                content_class.settings_panel_index = panel_registry_item.settings_stacked_widget_index

        panel_registry_item.ui_instance = panel_registry_item.ui_class(
            parent_widget=self.stacked_widget,
            parent_class=self,
            root_class=self.root_class,
            stacked_widget_index=panel_registry_item.settings_stacked_widget_index,
        )
        panel_registry_item.ui_instance.setup_ui()
        self.panels.append(panel_registry_item.ui_instance)
        self.stacked_widget.addWidget(panel_registry_item.ui_instance.widget)


logging.debug("settings loaded")
