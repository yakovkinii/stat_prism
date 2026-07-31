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
    def setup(self): ...

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
