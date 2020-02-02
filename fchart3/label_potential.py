#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
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

from numpy import *


class LabelPotential:
    def __init__(self, fieldradius, deepskylist):
        """
        fieldradius in mm
        deepskylist [(x,y,size), (x,y,size),...]
        x,y, size in mm
        """
        self.fieldradius  = fieldradius
        self.positions = zeros((len(deepskylist), 2))*0.0
        self.sizes = zeros(len(deepskylist))*0.0
        for i in range(len(deepskylist)):
            x,y,s = deepskylist[i]
            if s <= 0:
                s = 1
            self.sizes[i] = s**0.5
            self.positions[i,0] = x
            self.positions[i,1] = y


    def add_position(self,x,y,size):
        N = len(self.sizes)
        newpos = zeros((N+1,2))*0.0
        newpos[0:N,:] = self.positions
        newpos[N,:] = [x,y]

        newsize = zeros(N+1)*0.0
        newsize[0:N] = self.sizes
        newsize[N] = size**0.5

        self.positions = newpos
        self.sizes = newsize

    def compute_potential(self,x,y):
        """
        x,y in mm
        """
        value = 0.0
        ss = sum(self.sizes)
        rf = ((x**2+y**2)**0.5 - self.fieldradius)**-3

        r2 = (self.positions[:,0]-x)**2 + (self.positions[:,1]-y)**2
        sr = (r2+0.1)**(-1)
        p = self.sizes*sr
        value = sum(p) + ss*rf
        return value


__all__ = ['LabelPotential']
