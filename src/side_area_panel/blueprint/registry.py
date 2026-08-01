#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

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
    SELECT_DATA_PROCESSING = PanelRegistryItem(unique_id_for_enum="SELECT_DATA_PROCESSING")
    SELECT_DATA_ANALYSIS = PanelRegistryItem(unique_id_for_enum="SELECT_DATA_ANALYSIS")
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
