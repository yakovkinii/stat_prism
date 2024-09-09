from enum import Enum

import attrs


@attrs.define
class ModuleRegistryItem:
    display_name: str
    ui_class: any = None
    result_class: any = None
    config_class: any = None
    ui_instance: any = None
    settings_stacked_widget_index: int = None
    icon_path: str = None


class ModuleRegistry(Enum):
    CORRELATION = ModuleRegistryItem(
        display_name="Correlation",
        icon_path="ph.chart-line-up-fill",
    )

    @property
    def display_name(self):
        return self.value.display_name

    @property
    def ui_class(self):
        return self.value.ui_class

    @property
    def result_class(self):
        return self.value.result_class

    @property
    def ui_instance(self):
        return self.value.ui_instance

    @property
    def settings_stacked_widget_index(self):
        return self.value.settings_stacked_widget_index
