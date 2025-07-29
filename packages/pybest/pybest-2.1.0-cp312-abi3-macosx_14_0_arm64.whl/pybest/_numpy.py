# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""
This is a shim to handle numpy 2.0.0, change of copy behavior
https://github.com/scipy/scipy/pull/20172
"""

from typing import Optional

import numpy as np

copy_if_needed: Optional[bool]

if np.lib.NumpyVersion(np.__version__) >= "2.0.0":
    copy_if_needed = None
elif np.lib.NumpyVersion(np.__version__) < "1.28.0":
    copy_if_needed = False
else:
    # 2.0.0 dev versions, handle cases where copy may or may not exist
    try:
        np.array([1]).__array__(copy=None)
        copy_if_needed = None
    except TypeError:
        copy_if_needed = False
