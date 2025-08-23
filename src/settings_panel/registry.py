#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs


@attrs.define
class PanelRegistryItem:
    unique_id_for_enum: str
    content_class: any = None  # E.g. HTMLTableV2
    ui_class: any = None
    ui_instance: any = None
    settings_stacked_widget_index: int = None


class PanelRegistry(Enum):
    HOME = PanelRegistryItem(unique_id_for_enum="HOME")
    HOME_INITIAL = PanelRegistryItem(unique_id_for_enum="HOME_INITIAL")
    COLUMN = PanelRegistryItem(unique_id_for_enum="COLUMN")
    COLUMNS = PanelRegistryItem(unique_id_for_enum="COLUMNS")
    INVERSE = PanelRegistryItem(unique_id_for_enum="INVERSE")
    SELECT_DATA_PROCESSING = PanelRegistryItem(unique_id_for_enum="SELECT_DATA_PROCESSING")
    SELECT_DATA_ANALYSIS = PanelRegistryItem(unique_id_for_enum="SELECT_DATA_ANALYSIS")
    FILTER = PanelRegistryItem(unique_id_for_enum="FILTER")
    COLUMN_SELECTOR = PanelRegistryItem(unique_id_for_enum="COLUMN_SELECTOR")
    HTML_TABLE_V2_SETTINGS = PanelRegistryItem(unique_id_for_enum="HTML_TABLE_V2_SETTINGS")
    HTML_MULTI_TABLE_V2_SETTINGS = PanelRegistryItem(unique_id_for_enum="HTML_MULTI_TABLE_V2_SETTINGS")
    RESULT_ITEM_SETTINGS_V2 = PanelRegistryItem(unique_id_for_enum="RESULT_ITEM_SETTINGS_V2")
    BLANK = PanelRegistryItem(unique_id_for_enum="BLANK")
    ORDER = PanelRegistryItem(unique_id_for_enum="ORDER")
    MAPPING = PanelRegistryItem(unique_id_for_enum="MAPPING")
    INVERSION_CONFIG = PanelRegistryItem(unique_id_for_enum="INVERSION_CONFIG")

    @property
    def ui_class(self):
        return self.value.ui_class

    @property
    def ui_instance(self):
        return self.value.ui_instance

    @property
    def settings_stacked_widget_index(self):
        return self.value.settings_stacked_widget_index
