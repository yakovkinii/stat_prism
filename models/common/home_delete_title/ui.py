class HomeDeleteTitle:
    self.HomeButton = create_tool_button_qta(
        parent=self.widget,
        button_geometry=QtCore.QRect(10, 10, 61, 61),
        icon_path="fa.home",
        icon_size=QtCore.QSize(40, 40),
    )

    self.DeleteButton = create_tool_button_qta(
        parent=self.widget,
        button_geometry=QtCore.QRect(10 + 380 - 59, 10, 61, 61),
        icon_path="mdi.delete-forever",
        icon_size=QtCore.QSize(40, 40),
    )
    self.DeleteButton.setEnabled(False)

    self.title = create_label(
        parent=self.widget,
        label_geometry=QtCore.QRect(10 + 61, 10, 381 - 122, 61),
        font_size=16,
        alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
    )
