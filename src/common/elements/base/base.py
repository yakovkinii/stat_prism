#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from abc import abstractmethod


class BasePanelElement:
    def __init__(self):
        self.parent_widget = ...
        self.handler = ...
        self.widget = ...
        self.element_id = ...

    def inject(self, parent_widget, handler, element_id):
        self.element_id = element_id
        self.parent_widget = parent_widget
        self.handler = handler

    @abstractmethod
    def setup(self):
        ...

    def configure(self, *args, **kwargs):
        raise NotImplementedError(f"Configure method not implemented for {self.__class__.__name__}.")
