class ColumnSelector:
    self.listWidget_all_columns = QtWidgets.QListWidget(self.widget)
    self.listWidget_all_columns.setGeometry(QtCore.QRect(10, 93, 381, 271))
    self.listWidget_all_columns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    self.listWidget_selected_columns = QtWidgets.QListWidget(self.widget)
    self.listWidget_selected_columns.setGeometry(QtCore.QRect(10, 423, 381, 231))
    self.listWidget_selected_columns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    self.DownButton = create_tool_button(
        parent=self.widget,
        button_geometry=QtCore.QRect(140, 370, 51, 51),
        icon_path=":/mat/resources/material-icons-png-master/png/black/arrow_downward/round-4x.png",
        icon_size=QtCore.QSize(40, 40),
    )

    self.UpButton = create_tool_button(
        parent=self.widget,
        button_geometry=QtCore.QRect(210, 370, 51, 51),
        icon_path=":/mat/resources/material-icons-png-master/png/black/arrow_upward/round-4x.png",
        icon_size=QtCore.QSize(40, 40),
    )