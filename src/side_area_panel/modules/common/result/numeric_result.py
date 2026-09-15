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


# Base for a study's non-rendered numeric result: the exact values a study computed, decoupled
# from any HTML. A study's *_main computes one of these (a pure, headless step, no Qt), then a
# transpiler turns it into rendered result elements. Headless tests read the numbers straight off
# it and compare them to numeric benchmarks, instead of diffing localized, rounded HTML. Subclasses
# are attrs data classes holding the study's coefficients plus `error`: a non-empty message means
# the study could not compute, and the transpiler renders only that message.
class NumericResult:
    error = ""
