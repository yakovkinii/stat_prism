#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Callable

from PySide6.QtWidgets import QWidget

from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.unique_qss import set_stylesheet


def add_widget(
    parent=None,
    widget=None,
    widget_class=None,
    inner_layout_class=None,
    outer_layout=None,
    outer_layout_grid_row=None,
    outer_layout_grid_column=None,
    css=None,
):
    if widget is None:
        if widget_class is None:
            widget_class = QWidget
        widget = widget_class(parent)
    else:
        assert widget_class is None, "Cannot specify both widget and widget_class"

    if inner_layout_class is not None:
        layout = inner_layout_class(widget)
        widget.setLayout(layout)
    else:
        layout = None

    if outer_layout is not None:
        args = []
        if outer_layout_grid_row is not None:
            assert outer_layout_grid_column is not None, "If specifying grid row, must also specify column"
            args = [outer_layout_grid_row, outer_layout_grid_column]
        outer_layout.addWidget(widget, *args)

    if css is not None:
        set_stylesheet(
            widget,
            css,
        )

    return widget, layout


def empty_widget(
    parent,
    inner_layout_class=None,
    widget_class=None,
    outer_layout=None,
    setup: Callable[[object, object], any] = None,
):
    if inner_layout_class is None:
        inner_layout_class = VBoxLayout
    if widget_class is None:
        widget_class = QWidget

    widget = widget_class(parent)
    layout = inner_layout_class(widget)
    widget.setLayout(layout)

    if outer_layout is not None:
        outer_layout.addWidget(widget)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    if setup is not None:
        _ = setup(widget, layout)

    return widget, layout


def widget_in_layout(
    widget,
    layout,
    setup: Callable[[object, object], any] = None,
    alignment=None,
):
    if alignment is None:
        layout.addWidget(widget)
    else:
        layout.addWidget(widget, alignment=alignment)
    if setup is not None:
        _ = setup(widget, layout)
    return widget


def clean_up_list_widget(list_widget):
    for index in range(list_widget.count()):
        item = list_widget.item(index)
        widget = list_widget.itemWidget(item)
        if widget:
            widget.deleteLater()
        list_widget.takeItem(index)
    list_widget.clear()
