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

from typing import Optional, TypeAlias, Sequence, Callable

from .vector_math import *

Vec3: TypeAlias = Sequence[float]
TriangleEdges: TypeAlias = tuple[Vec3, Vec3, Vec3]
VisitFunc: TypeAlias = Callable[[int, int, Vec3, Vec3, Vec3], None]

octahedron_corners = (
    (0,  0,  1),
    (1,  0,  0),
    (0,  1,  0),
    (-1,  0,  0),
    (0, -1,  0),
    (0,  0, -1),
)

octahedron_triangles = (
    (1, 5, 2),  #  S0
    (2, 5, 3),  #  S1
    (3, 5, 4),  #  S2
    (4, 5, 1),  #  S3
    (1, 0, 4),  #  N3
    (4, 0, 3),  #  N3
    (3, 0, 2),  #  N3
    (2, 0, 1),  #  N3
)


class HtmGrid:
    ''' HtmGrid: keeps HTM structure '''

    max_depth: int
    _triangles: Optional[list[list[Optional[TriangleEdges]]]]
    _triangle_centers: Optional[list[list[Optional[Vec3]]]]

    @staticmethod
    def nr_of_triangles(depth):
        return 8 * 4 ** depth

    def __init__(self, depth: int) -> None:
        self.max_depth = depth

        if depth >= 0:
            self._triangles = [None] * (depth + 1)
            self._triangle_centers = [None] * (depth + 1)

            nr_of_triangles = 8
            for i in range(depth + 1):
                self._triangles[i] = [None] * nr_of_triangles
                self._triangle_centers[i] = [None] * nr_of_triangles
                nr_of_triangles *= 4

            for i in range(8):
                corners = octahedron_triangles[i]
                self._init_triangle(0, i, octahedron_corners[corners[0]], octahedron_corners[corners[1]], octahedron_corners[corners[2]])
        else:
            self._triangles = None
            self._triangle_centers = None

    def _init_triangle(
        self,
        depth: int,
        index: int,
        v0: Vec3,
        v1: Vec3,
        v2: Vec3,
        center: Optional[Vec3] = None,
    ) -> None:
        t: TriangleEdges = (vector_norm_add(v1, v2), vector_norm_add(v2, v0), vector_norm_add(v0, v1))
        self._triangles[depth][index] = t

        if center is None:
            center = vector_norm_add3(v0, v1, v2)
        self._triangle_centers[depth][index] = center

        depth += 1
        if depth <= self.max_depth:
            index *= 4
            self._init_triangle(depth, index + 0, v0, t[2], t[1])
            self._init_triangle(depth, index + 1, v1, t[0], t[2])
            self._init_triangle(depth, index + 2, v2, t[1], t[0])
            self._init_triangle(depth, index + 3, t[0], t[1], t[2], center)

    def visit_triangles(self, max_visit_depth: int, visit_func: Optional[VisitFunc]) -> None:
        if visit_func and max_visit_depth >= 0:
            if max_visit_depth > self.max_depth:
                max_visit_depth = self.max_depth

            for i in range(8):
                corners = octahedron_triangles[i]
                self._visit_triangles(0, i,
                    octahedron_corners[corners[0]],
                    octahedron_corners[corners[1]],
                    octahedron_corners[corners[2]],
                    max_visit_depth, visit_func
                )

    def _visit_triangles(
        self,
        depth: int,
        index: int,
        v0: Vec3,
        v1: Vec3,
        v2: Vec3,
        max_visit_depth: int,
        func: VisitFunc,
    ) -> None:
        func(depth, index, v0, v1, v2)

        depth += 1
        if depth <= max_visit_depth:
            t = self._triangles[depth - 1][index]
            index *= 4
            self._visit_triangles(depth, index + 0, v0, t[2], t[1], max_visit_depth, func)
            self._visit_triangles(depth, index + 1, v1, t[0], t[2], max_visit_depth, func)
            self._visit_triangles(depth, index + 2, v2, t[1], t[0], max_visit_depth, func)
            self._visit_triangles(depth, index + 3, t[0], t[1], t[2], max_visit_depth, func)
