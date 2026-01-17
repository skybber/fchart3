#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import math
from typing import TypeAlias, Tuple, Sequence

import numpy as np
from numpy.typing import NDArray

DeepskyItem: TypeAlias = Tuple[object, float, float, float]


class LabelPotential:
    field_radius: float
    positions: NDArray[np.float32]
    sizes: NDArray[np.float32]

    def __init__(self, field_radius: float) -> None:
        """
        field_radius in mm
        deepskylist [(x,y,size), ...]  # note: code expects 4-tuple: (_, x, y, s)
        x, y, size in mm
        """
        self.field_radius = float(field_radius)
        self.positions = np.empty((0, 2), dtype=np.float32)
        self.sizes = np.empty((0,), dtype=np.float32)

    def add_deepsky_list(self, deepskylist: Sequence[DeepskyItem]) -> None:
        n_old = int(self.sizes.shape[0])
        n_new = n_old + len(deepskylist)

        newpos = np.zeros((n_new, 2), dtype=np.float32)
        newsize = np.zeros((n_new,), dtype=np.float32)

        newpos[:n_old, :] = self.positions
        newsize[:n_old] = self.sizes

        for i, item in enumerate(deepskylist):
            _, x, y, s = item
            if s <= 0:
                s = 1.0
            newsize[n_old + i] = np.float32(math.sqrt(float(s)))
            newpos[n_old + i, :] = (float(x), float(y))

        self.positions = newpos
        self.sizes = newsize

    def add_position(self, x: float, y: float, size: float) -> None:
        self.positions = np.append(self.positions, [[float(x), float(y)]], axis=0)
        self.sizes = np.append(self.sizes, np.float32(math.sqrt(float(size))))

    def compute_potential(self, x: float, y: float, edge_opt: bool = False) -> float:
        dx = self.positions[:, 0] - float(x)
        dy = self.positions[:, 1] - float(y)
        r2 = dx * dx + dy * dy

        sr = (r2 + 0.1) ** (-1)
        p = self.sizes * sr

        value = float(np.sum(p))

        if edge_opt:
            ss = float(np.sum(self.sizes))
            r = math.hypot(float(x), float(y))
            rf = (r - self.field_radius) ** (-3)
            value += ss * rf

        return value
