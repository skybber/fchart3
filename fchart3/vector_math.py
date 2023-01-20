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


def vector_norm_add(a, b):
    v0 = a[0] + b[0]
    v1 = a[1] + b[1]
    v2 = a[2] + b[2]
    n = math.sqrt(v0**2 + v1**2 + v2**2)
    return v0/n, v1/n, v2/n


def vector_norm_add_assign(dest, a, b):
    v0 = a[0] + b[0]
    v1 = a[1] + b[1]
    v2 = a[2] + b[2]
    n = math.sqrt(v0**2 + v1**2 + v2**2)
    dest[0], dest[1], dest[2] = v0/n, v1/n, v2/n


def vector_norm_add3(a, b, c):
    v0 = a[0] + b[0] + c[0]
    v1 = a[1] + b[1] + c[1]
    v2 = a[2] + b[2] + c[2]
    n = math.sqrt(v0**2 + v1**2 + v2**2)
    return v0/n, v1/n, v2/n


def vector_sub(a, b):
    v0 = a[0] - b[0]
    v1 = a[1] - b[1]
    v2 = a[2] - b[2]
    return v0, v1, v2


def vector_sub(a, b):
    v0 = a[0] - b[0]
    v1 = a[1] - b[1]
    v2 = a[2] - b[2]
    return v0, v1, v2


def vector_dot(a, b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]


def vector_cross(a, b):
    v0 = a[1]*b[2] - a[2]*b[1]
    v1 = a[2]*b[0] - a[0]*b[2]
    v2 = a[0]*b[1] - a[1]*b[0]
    return v0, v1, v2


def vector_norm_cross(a, b):
    v0 = a[1]*b[2] - a[2]*b[1]
    v1 = a[2]*b[0] - a[0]*b[2]
    v2 = a[0]*b[1] - a[1]*b[0]
    n = math.sqrt(v0*v0 + v1*v1 + v2*v2)
    return v0/n, v1/n, v2/n


def vector_scal_dot(x, a):
    return x*a[0], x*a[1], x*a[2]


def vector_length(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


__all__ = ['vector_norm_add', 'vector_norm_add_assign', 'vector_norm_add3', 'vector_sub','vector_dot', 'vector_cross',
           'vector_norm_cross', 'vector_scal_dot', 'vector_length'
           ]