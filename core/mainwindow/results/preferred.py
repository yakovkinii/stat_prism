from PyQt5 import QtWidgets


def createPreferredWidget(widgetClass, *args, **kwargs):
    widget = widgetClass(*args, **kwargs)
    widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    return widget
