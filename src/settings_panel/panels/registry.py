from enum import Enum

import attrs


@attrs.define
class PanelRegistryItem:
    display_name: str
    ui_class: any = None
    ui_instance: any = None
    settings_stacked_widget_index: int = None


class PanelRegistry(Enum):
    HOME = PanelRegistryItem(display_name="Home")
    COLUMN = PanelRegistryItem(display_name="Column Properties")
    COLUMNS = PanelRegistryItem(display_name="Multiple Column Properties")
    INVERSE = PanelRegistryItem(display_name="Invert Scale(s)")
    SELECT_STUDY = PanelRegistryItem(display_name="New Analysis")
    FILTER = PanelRegistryItem(display_name="Filter Properties")
    COLUMN_SELECTOR = PanelRegistryItem(display_name="Select Columns")
    HTML_RESULT_ITEM_SETTINGS = PanelRegistryItem(display_name="HTML Result Item Settings")
    PLOT_RESULT_ITEM_SETTINGS = PanelRegistryItem(display_name="PLOT Result Item Settings")
    BLANK = PanelRegistryItem(display_name="Blank")

    @property
    def display_name(self):
        return self.value.display_name

    @property
    def ui_class(self):
        return self.value.ui_class

    @property
    def ui_instance(self):
        return self.value.ui_instance

    @property
    def settings_stacked_widget_index(self):
        return self.value.settings_stacked_widget_index
