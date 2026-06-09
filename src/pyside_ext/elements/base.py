#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from abc import abstractmethod


class BasePanelElement:
    def __init__(self):
        self.parent_widget = ...
        self.handler = ...
        self.widget = ...
        self.layout = ...
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

    # --- Default-value tracking ---------------------------------------------------
    # Value-holding settings remember the value they were created with as their
    # "default" and can restore it / report whether the user changed it. Elements
    # that hold no value (e.g. containers) inherit these no-ops.
    def get_default_value(self):
        return None

    def set_default_value(self, value):
        pass

    def restore_default_value(self):
        pass

    def is_modified(self):
        return False
