#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023 fchart authors
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

import numpy as np


class LabelPotential:
    def __init__(self, fieldradius):
        """
        fieldradius in mm
        deepskylist [(x,y,size), (x,y,size),...]
        x,y, size in mm
        """
        self.fieldradius  = fieldradius
        self.positions = np.empty((0, 2))
        self.sizes = np.empty(0)

    def add_deepsky_list(self, deepskylist):
        N = len(self.sizes)
        newpos = np.zeros((N+len(deepskylist),2))
        newpos[0:N,:] = self.positions
        newsize = np.zeros(N+len(deepskylist))
        newsize[0:N] = self.sizes

        for i in range(len(deepskylist)):
            _, x,y,s = deepskylist[i]
            if s <= 0:
                s = 1
            newsize[N + i] = math.sqrt(s)
            newpos[N + i,:] = [x, y]

        self.positions = newpos
        self.sizes = newsize

    def add_position(self, x, y, size):
        self.positions = np.append(self.positions, [[x, y]], axis=0)
        self.sizes = np.append(self.sizes, math.sqrt(size))

    def compute_potential(self, x, y, edge_opt=False):
        r2 = (self.positions[:,0]-x)**2 + (self.positions[:,1]-y)**2
        sr = (r2+0.1)**(-1)
        p = self.sizes*sr
        if edge_opt:
            ss = np.sum(self.sizes)
            rf = ((x**2+y**2)**0.5 - self.fieldradius)**-3
            value = np.sum(p) + ss*rf
        else:
            value = np.sum(p)
        return value
