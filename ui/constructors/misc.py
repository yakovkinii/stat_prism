from PyQt5 import QtGui

import resources_rc


def icon(path):
    _icon = QtGui.QIcon()
    _icon.addPixmap(
        QtGui.QPixmap(path),
        QtGui.QIcon.Normal,
        QtGui.QIcon.Off,
    )
    return _icon


if __name__ == "__main__":
    _ = resources_rc
