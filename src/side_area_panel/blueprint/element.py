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
    def iter_items(self):
        cls = self.__class__
        return [v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)]

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

        # recurse=False keeps nested attrs (e.g. filter settings) as objects rather than dicts.
        kwargs = attrs.asdict(config, recurse=False)
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

    def broken_columns(self):
        """Selected columns that an upstream edit invalidated (renamed/removed, or type changed),
        aggregated across every element that tracks them (currently the column selector). Empty
        when nothing is broken. Modules stop / no-op on a non-empty result (see BaseModulePanel)."""
        cls = self.__class__
        items = {k: v for k, v in vars(cls).items() if not k.startswith("_") and not callable(v)}

        names = []
        for name, item in items.items():
            getter = getattr(item, "broken_columns", None)
            if callable(getter):
                names.extend(getter())
        return names
