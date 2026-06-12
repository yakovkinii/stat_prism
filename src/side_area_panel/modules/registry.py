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
    main_function: any = None
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

    CALCULATE_SCALE = ModuleRegistryItem(
        display_name="Calculate Scale",
        icon_path="mdi6.scale-balance",
        module_type=ModuleType.DATA_PROCESSING,
    )

    INVERT_SCALE = ModuleRegistryItem(
        display_name="Invert Scale",
        icon_path="ri.arrow-up-down-line",
        module_type=ModuleType.DATA_PROCESSING,
    )

    FILTER = ModuleRegistryItem(
        display_name="Filter",
        icon_path="mdi6.filter-outline",
        module_type=ModuleType.DATA_PROCESSING,
    )

    PREPROCESS = ModuleRegistryItem(
        display_name="Preprocess",
        icon_path="mdi6.table-edit",
        module_type=ModuleType.DATA_PROCESSING,
    )

    GROUP_VALUES = ModuleRegistryItem(
        display_name="Group Values",
        icon_path="mdi6.format-list-group",
        module_type=ModuleType.DATA_PROCESSING,
    )

    OUTLIERS = ModuleRegistryItem(
        display_name="Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    GROUPED_OUTLIERS = ModuleRegistryItem(
        display_name="Grouped Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    TWO_D_OUTLIERS = ModuleRegistryItem(
        display_name="2D Outliers",
        icon_path="mdi6.chart-scatter-plot",
        module_type=ModuleType.DATA_PROCESSING,
    )

    DESCRIPTIVE = ModuleRegistryItem(
        display_name="Descriptive Statistics",
        icon_path="ph.note",
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

    RELIABILITY = ModuleRegistryItem(
        display_name="Reliability",
        icon_path="mdi6.check-decagram",
    )

    REGRESSION = ModuleRegistryItem(
        display_name="Regression",
        icon_path="mdi6.chart-bell-curve-cumulative",
    )

    FACTOR_ANALYSIS = ModuleRegistryItem(
        display_name="Exploratory Factor Analysis",
        icon_path="mdi6.chart-bubble",
    )

    CFA = ModuleRegistryItem(
        display_name="Confirmatory Factor Analysis",
        icon_path="mdi6.sitemap-outline",
    )

    CLUSTER_ANALYSIS = ModuleRegistryItem(
        display_name="Cluster Analysis",
        icon_path="mdi6.scatter-plot-outline",
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
    def main_function(self):
        return self.value.main_function

    @property
    def settings_stacked_widget_index(self):
        return self.value.settings_stacked_widget_index
