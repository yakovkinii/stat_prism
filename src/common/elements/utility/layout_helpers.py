#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

from typing import Callable

from PySide6.QtWidgets import QVBoxLayout, QWidget


def empty_widget(
    parent,
    inner_layout_class=None,
    widget_class=None,
    outer_layout=None,
    setup: Callable[[object, object], any] = None,
):
    if inner_layout_class is None:
        inner_layout_class = QVBoxLayout
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
):
    layout.addWidget(widget)
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
