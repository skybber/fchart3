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

from .vector_math import *

import numpy as np
from time import time
# from memory_profiler import profile

icosahedron_G = 0.5*(1.0+math.sqrt(5.0))
icosahedron_b = 1.0/math.sqrt(1.0+icosahedron_G*icosahedron_G)
icosahedron_a = icosahedron_b*icosahedron_G

icosahedron_corners = (
    (icosahedron_a,  -icosahedron_b,            0.0),
    (icosahedron_a,   icosahedron_b,            0.0),
    (-icosahedron_a,  icosahedron_b,            0.0),
    (-icosahedron_a, -icosahedron_b,            0.0),
    (           0.0,  icosahedron_a, -icosahedron_b),
    (           0.0,  icosahedron_a,  icosahedron_b),
    (           0.0, -icosahedron_a,  icosahedron_b),
    (           0.0, -icosahedron_a, -icosahedron_b),
    (-icosahedron_b,            0.0,  icosahedron_a),
    (icosahedron_b,            0.0,   icosahedron_a),
    (icosahedron_b,            0.0,  -icosahedron_a),
    (-icosahedron_b,            0.0, -icosahedron_a),
)

icosahedron_triangles = (
    (1,  0,  10),  # 1
    (0,  1,  9),   # 0
    (0,  9,  6),   # 12
    (9,  8,  6),   # 9
    (0,  7,  10),  # 16
    (6,  7,  0),   # 6
    (7,  6,  3),   # 7
    (6,  8,  3),   # 14
    (11, 10, 7),   # 11
    (7,  3,  11),  # 18
    (3,  2,  11),  # 3
    (2,  3,  8),   # 2
    (10, 11, 4),   # 10
    (2,  4,  11),  # 19
    (5,  4,  2),   # 5
    (2,  8,  5),   # 15
    (4,  1,  10),  # 17
    (4,  5,  1),   # 4
    (5,  9,  1),   # 13
    (8,  9,  5)    # 8
)


class SphericalCap:
    def __init__(self, view_dir, inner_view_cos, outer_view_cos):
        """
        Construct a SphericalCap from its direction and aperture.
        - view_dir a unit vector indicating the direction.
        - inner_view_cos cosinus of the aperture.
        - inner_view_cos cosinus of the aperture + max angular size of triangle in level
        """
        self._view_dir = view_dir
        self._inner_view_cos = inner_view_cos
        self._outer_view_cos = outer_view_cos

    def inside_inner(self, v):
        x = vector_dot(v, self._view_dir)
        return x >= self._inner_view_cos

    def inside_outer(self, c):
        x = vector_dot(c, self._view_dir)
        return x >= self._outer_view_cos


class GeodesicSearchResult:
    """ Result of grid search
    """
    def __init__(self, max_level):
        self.zone_lists = [None] * (max_level + 1)
        self.inside_indexes = [None] * (max_level + 1)
        self.border_indexes = [None] * (max_level + 1)
        self.max_level = max_level

        for i in range(max_level+1):
            n = GeodesicGrid.nr_of_zones(i)
            self.zone_lists[i] = [0] * n

        self.reset()

    def reset(self):
        for i in range(self.max_level+1):
            self.inside_indexes[i] = 0
            self.border_indexes[i] = GeodesicGrid.nr_of_zones(i)

    def add_inside_index(self, lev, index):
        self.zone_lists[lev][self.inside_indexes[lev]] = index
        self.inside_indexes[lev] += 1

    def add_border_index(self, lev, index):
        self.border_indexes[lev] -= 1
        self.zone_lists[lev][self.border_indexes[lev]] = index


class GeodesicSearchBorderIterator:
    """ Iterates over border triangles
    """
    def __init__(self, search_result, level):
        self._search_zones = search_result.zone_lists[level]
        self._index = search_result.border_indexes[level]

    def next(self):
        if self._index >= len(self._search_zones):
            return -1
        ret = self._search_zones[self._index]
        self._index += 1
        return ret


class GeodesicSearchInsideIterator:
    """ Iterates over inside triangles
    """
    def __init__(self, search_result, max_level):
        self._search_result = search_result
        self._level = 0
        self._max_level = max_level
        self._max_count = 1 << (max_level << 1)  # 4^maxLevel
        self._lev_zones = search_result.zone_lists[0]
        self._cur_index = 0
        self._end_index = search_result.inside_indexes[0]
        self._index = self._lev_zones[0] * self._max_count
        self._count = 0 if self._end_index > 0 else self._max_count

    def next(self):
        if self._count < self._max_count:
            ret = self._index + self._count
            self._count += 1
            return ret

        self._cur_index += 1

        if self._cur_index < self._end_index:
            self._index = self._lev_zones[self._cur_index] * self._max_count
            self._count = 1
            return self._index

        while self._level < self._max_level:
            self._level += 1
            self._max_count = self._max_count >> 2
            self._lev_zones = self._search_result.zone_lists[self._level]
            self._cur_index = 0
            self._end_index = self._search_result.inside_indexes[self._level]
            if self._end_index > 0:
                self._index = self._lev_zones[0] * self._max_count
                self._count = 1
                return self._index

        return -1


class GeodesicGrid:
    """
    GeodesicGrid: a library for dividing the sphere into triangle zones by subdividing the icosahedron
    Based on work of Johannes Gajdosik, 2006
    """
    @staticmethod
    def nr_of_zones(level):
        return 20 << (level << 1)

    # @profile
    def __init__(self, level):
        # tm = time()
        self.max_level = level
        if level >= 0:
            self._triangles = [None] * (level+1)
            self._triangle_centers = [None] * (level+1)
            nr_of_triangles = 20
            for i in range(level+1):
                self._triangles[i] = [None] * nr_of_triangles
                self._triangle_centers[i] = [None] * nr_of_triangles
                nr_of_triangles *= 4
            for i in range(20):
                corners = icosahedron_triangles[i]
                self._init_triangle(0, i, icosahedron_corners[corners[0]], icosahedron_corners[corners[1]], icosahedron_corners[corners[2]])
        else:
            self._triangles = None
        # print("#################### Geodesic grid within {} s".format(str(time()-tm)), flush=True)

    def to_np_arrays(self):
        for i in range(self.max_level+1):
            self._triangles[i] = np.array(self._triangles[i], dtype=np.float32)
            self._triangle_centers[i] = np.array(self._triangle_centers[i], dtype=np.float32)

    def get_triangle_corners(self, lev, index):
        h0, h1, h2 = None, None, None
        if lev <= 0:
            corners = icosahedron_triangles[index]
            h0 = icosahedron_corners[corners[0]]
            h1 = icosahedron_corners[corners[1]]
            h2 = icosahedron_corners[corners[2]]
        else:
            lev -= 1
            i = index >> 2
            t = self._triangles[lev][i]
            x = index & 3
            if x == 0:
                c0, c1, c2 = self.get_triangle_corners(lev, i)
                h0, h1, h2 = c0, t[2], t[1]
            elif x == 1:
                c0, c1, c2 = self.get_triangle_corners(lev, i)
                h0, h1, h2 = t[2], c1, t[0]
            elif x == 2:
                c0, c1, c2 = self.get_triangle_corners(lev, i)
                h0, h1, h2 = t[1], t[0], c2
            elif x == 3:
                h0, h1, h2 = t[0], t[1], t[2]
        return h0, h1, h2

    def get_partner_triangle(self, lev, index):
        if lev == 0:
            return index+1 if (index&1) == 1 else index-1

        x = index & 7
        if x == 2 or x == 6:
            return index+1
        if x == 3 or x == 7:
            return index-1
        if x == 0:
            return index+5 if lev == 1 else (self.get_partner_triangle(lev-1, index >> 2) << 2)+1
        if x == 1:
            return index+3 if lev == 1 else (self.get_partner_triangle(lev-1, index >> 2) << 2)+0
        if x == 4:
            return index-3 if lev == 1 else (self.get_partner_triangle(lev-1, index >> 2) << 2)+1
        if x == 5:
            return index-5 if lev == 1 else (self.get_partner_triangle(lev-1, index >> 2) << 2)+0
        return 0

    def _init_triangle(self, lev, index, c0, c1, c2, center=None):
        t = (vector_norm_add(c1, c2), vector_norm_add(c2, c0), vector_norm_add(c0, c1))
        self._triangles[lev][index] = t
        if center is None:
            center = vector_norm_add3(c0, c1, c2)
        self._triangle_centers[lev][index] = center
        lev += 1
        if lev <= self.max_level:
            index *= 4
            self._init_triangle(lev, index+0, c0, t[2], t[1])
            self._init_triangle(lev, index+1, t[2], c1, t[0])
            self._init_triangle(lev, index+2, t[1], t[0], c2)
            self._init_triangle(lev, index+3, t[0], t[1], t[2], center)

    def search_zones(self, lev_spherical_caps, search_result, max_search_level):
        if max_search_level < 0:
            max_search_level = 0
        elif max_search_level > self.max_level:
            max_search_level = self.max_level

        corner_in_inner = []

        for i in range(12):
            corner_in_inner.append(lev_spherical_caps[0].inside_inner(icosahedron_corners[i]))

        for i in range(20):
            if lev_spherical_caps[0].inside_outer(self._triangle_centers[0][i]):
                corners = icosahedron_triangles[i]
                self._search_zones(0, i, lev_spherical_caps,
                                   corner_in_inner[corners[0]], corner_in_inner[corners[1]], corner_in_inner[corners[2]],
                                   search_result, max_search_level)

    def _search_zones(self, lev, index, lev_spherical_caps,
                      corner0_in_inner, corner1_in_inner, corner2_in_inner,
                      search_result, max_search_level):

        if corner0_in_inner and corner1_in_inner and corner2_in_inner:
            search_result.add_inside_index(lev, index) # totally inside
            return True
        else:
            if lev >= max_search_level:
                search_result.add_border_index(lev, index)
                return True

            master_lev = lev
            master_index = index

            t = self._triangles[lev][index]
            lev += 1
            index <<= 2

            edge0_in_inner = lev_spherical_caps[lev].inside_inner(t[0])
            edge1_in_inner = lev_spherical_caps[lev].inside_inner(t[1])
            edge2_in_inner = lev_spherical_caps[lev].inside_inner(t[2])

            in1 = False
            in2 = False
            in3 = False
            in4 = False

            if lev_spherical_caps[lev].inside_outer(self._triangle_centers[lev][index+0]):
                in1 = self._search_zones(lev, index+0, lev_spherical_caps,
                                         corner0_in_inner, edge2_in_inner, edge1_in_inner,
                                         search_result, max_search_level)

            if lev_spherical_caps[lev].inside_outer(self._triangle_centers[lev][index+1]):
                in2 = self._search_zones(lev, index+1, lev_spherical_caps,
                                         edge2_in_inner, corner1_in_inner, edge0_in_inner,
                                         search_result, max_search_level)

            if lev_spherical_caps[lev].inside_outer(self._triangle_centers[lev][index+2]):
                in3 = self._search_zones(lev, index+2, lev_spherical_caps,
                                         edge1_in_inner, edge0_in_inner, corner2_in_inner,
                                         search_result, max_search_level)

            if lev_spherical_caps[lev].inside_outer(self._triangle_centers[lev][index+3]):
                in4 = self._search_zones(lev, index+3, lev_spherical_caps,
                                         edge0_in_inner, edge1_in_inner, edge2_in_inner,
                                         search_result, max_search_level)

            if in1 or in2 or in3 or in4:
                search_result.add_border_index(master_lev, master_index)
                return True
            return False

    def visit_triangles(self, max_visit_level, visit_func):
        if visit_func and max_visit_level >= 0:
            if max_visit_level > self.max_level:
                max_visit_level = self.max_level
            for i in range(20):
                corners = icosahedron_triangles[i]
                self._visit_triangles(0, i,
                                      icosahedron_corners[corners[0]],
                                      icosahedron_corners[corners[1]],
                                      icosahedron_corners[corners[2]],
                                      max_visit_level, visit_func)

    def _visit_triangles(self, lev, index, c0, c1, c2, max_visit_level, func):
        func(lev, index, c0, c1, c2)
        lev += 1
        if lev <= max_visit_level:
            t = self._triangles[lev-1][index]
            index *= 4
            self._visit_triangles(lev, index+0, c0, t[2], t[1], max_visit_level, func)
            self._visit_triangles(lev, index+1, t[2], c1, t[0], max_visit_level, func)
            self._visit_triangles(lev, index+2, t[1], t[0], c2, max_visit_level, func)
            self._visit_triangles(lev, index+3, t[0], t[1], t[2], max_visit_level, func)
