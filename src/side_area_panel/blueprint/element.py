#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from abc import abstractmethod

import attrs


class ItemInSidePanelWithAutoConfig:
    def __init__(self):
        self.widget = ...
        self.name = ...
        self.alert = False
        self.handler_recalculate = None

    # handler methods should be set with set_handler_{event_name} methods
    # handlers need to be defined in init. The signals should not be linked directly to external handlers.
    @abstractmethod
    def post_init(self, name, parent_widget):
        # Here, actual widgets are created
        pass

    @abstractmethod
    def get_kwargs(self):
        # To construct a config entry
        pass

    @abstractmethod
    def configure(self, **kwargs):
        # To configure the element based on config entry
        pass

    @abstractmethod
    def set_alert(self):
        # To highlight wrong inputs
        pass

    @abstractmethod
    def clear_alert(self):
        # To clear highlight of wrong inputs
        pass

    def on_recalculate(self):
        if self.handler_recalculate is not None:
            self.handler_recalculate()

    def set_handler_recalculate(self, handler):
        self.handler_recalculate = handler


class ItemInSidePanelWithAutoConfigHolder:
    def complete_init_of_items(self, parent_widget, parent_layout, handler_on_recalculate, stretch=True):
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        for name, item in items.items():
            item.post_init(name=name, parent_widget=parent_widget)
            item.set_handler_recalculate(handler_on_recalculate)
            parent_layout.addWidget(item.widget)
        if stretch:
            parent_layout.addStretch()
        return self

    def configure(self, config, result_id):
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        kwargs = attrs.asdict(config)
        kwargs["result_id"] = result_id
        for name, item in items.items():
            item.configure(**kwargs)

    def get_kwargs(self):
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        kwargs = {}
        for name, item in items.items():
            kwargs.update(item.get_kwargs())
        return kwargs

    def clear_alerts(self):
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        for name, item in items.items():
            item.clear_alert()
