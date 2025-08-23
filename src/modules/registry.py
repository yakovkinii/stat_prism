#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from enum import Enum

import attrs


class ModuleType(Enum):
    RAW_DATA = "RAW_DATA"
    DATA_PROCESSING = "DATA_PROCESSING"
    DATA_ANALYSIS = "DATA_ANALYSIS"


@attrs.define
class ModuleRegistryItem:
    display_name: str
    ui_class: any = None
    result_class: any = None
    config_class: any = None
    ui_instance: any = None
    settings_stacked_widget_index: int = None
    icon_path: str = None
    module_type: ModuleType = ModuleType.DATA_ANALYSIS


class ModuleRegistry(Enum):
    RAW_DATA = ModuleRegistryItem(
        display_name="Raw Data",
        icon_path="msc.database",
        module_type=ModuleType.RAW_DATA,
    )

    MEAN_COMPARISON = ModuleRegistryItem(
        display_name="T-test/ANOVA",
        icon_path="ph.scales",
    )

    CONTINGENCY = ModuleRegistryItem(
        display_name="Contingency Table",
        icon_path="msc.table",
    )

    CORRELATION = ModuleRegistryItem(
        display_name="Correlation",
        icon_path="msc.link",
    )

    DESCRIPTIVE = ModuleRegistryItem(
        display_name="Descriptive Statistics",
        icon_path="msc.unverified",
    )

    RELIABILITY = ModuleRegistryItem(
        display_name="Reliability",
        icon_path="msc.unverified",
    )

    REGRESSION = ModuleRegistryItem(
        display_name="Regression",
        icon_path="msc.unverified",
    )

    FACTOR_ANALYSIS = ModuleRegistryItem(
        display_name="Exploratory Factor Analysis",
        icon_path="msc.unverified",
    )

    CFA = ModuleRegistryItem(
        display_name="Confirmatory Factor Analysis",
        icon_path="msc.unverified",
    )

    CLUSTER_ANALYSIS = ModuleRegistryItem(
        display_name="Cluster Analysis",
        icon_path="msc.unverified",
    )

    RENAME_COLUMNS = ModuleRegistryItem(
        display_name="Rename Columns",
        icon_path="mdi6.rename-outline",
        module_type=ModuleType.DATA_PROCESSING,
    )

    CALCULATE_SCALE = ModuleRegistryItem(
        display_name="Calculate Scale",
        icon_path="mdi6.scale-balance",
        module_type=ModuleType.DATA_PROCESSING,
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
