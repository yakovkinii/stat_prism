#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar, QProgressBar, QVBoxLayout

from src.common.constant import SettingsPanelSize
from src.common.languages import LANGUAGE, Languages
from src.common.theme import THEME, Themes
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

        language_menu = QMenu("Language", self.widget)
        theme_menu = QMenu("Theme", self.widget)
        help_menu = QMenu("Help", self.widget)

        # EN and UA checkable actions
        self.en_action = QAction("English", self.widget)
        self.ua_action = QAction("Українська", self.widget)
        self.en_action.setCheckable(True)
        self.ua_action.setCheckable(True)
        self.en_action.setChecked(True)  # Default to English
        self.about_action = QAction("About", self.widget)

        # One checkable action per theme (driven by the Themes enum, so adding a
        # theme there automatically adds a menu entry).
        self.theme_actions = {}
        for theme in Themes:
            theme_action = QAction(theme.value, self.widget)
            theme_action.setCheckable(True)
            theme_action.setChecked(theme == Themes.DEFAULT)
            theme_action.triggered.connect(lambda _checked=False, t=theme: self.set_theme(t))
            theme_menu.addAction(theme_action)
            self.theme_actions[theme] = theme_action

        menu_bar.addMenu(language_menu)
        menu_bar.addMenu(theme_menu)
        menu_bar.addMenu(help_menu)

        language_menu.addAction(self.en_action)
        language_menu.addAction(self.ua_action)
        help_menu.addAction(self.about_action)

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

    def set_language_EN(self):
        LANGUAGE.set_language(Languages.EN)
        self.en_action.setChecked(True)
        self.ua_action.setChecked(False)
        self.root_class.main_area_panel.recompute_all()

    def set_language_UA(self):
        LANGUAGE.set_language(Languages.UA)
        self.en_action.setChecked(False)
        self.ua_action.setChecked(True)
        self.root_class.main_area_panel.recompute_all()

    def set_theme(self, theme: Themes):
        THEME.set_theme(theme)
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
