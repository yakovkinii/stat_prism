from PyQt5 import QtWebEngineWidgets, QtWidgets


class Results:
    def __init__(self, parent):
        #   parent
        #       frame
        #           gridLayout
        #               scrollArea
        #                   scrollAreaWidgetContents
        #                       gridLayout_2
        #                           browser

        self.frame = QtWidgets.QFrame(parent)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QtWidgets.QScrollArea(self.frame)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        self.browser = QtWebEngineWidgets.QWebEngineView(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.browser)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea)

    def retranslateUI(self):
        pass
