#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2021 fchart authors
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

import numpy as np


def _radec_from_img(mw_points, point):
    x, y = point.split(',')
    x, y = int(x), int(y)
    ra = 2.5 * np.pi - 2.0*np.pi * x / 2048
    dec = - np.pi * (y-512) / 1024
    if mw_points is None:
        mw_points = np.array([[ra, dec]])
    else:
        mw_points = np.append(mw_points, [[ra, dec]], axis=0)
    return mw_points


def import_enhanced_milky_way(filename):
    milkyway_file = open(filename, 'r')
    lines = milkyway_file.readlines()
    milkyway_file.close()

    mw_triangles = []
    index_map = {}
    mw_points = None

    index = 0

    for line in lines:
        items = line.split()
        if items[3] == 'rgb(0,0,0)':
            continue

        index1 = index_map.get(items[0])
        if index1 is None:
            mw_points = _radec_from_img(mw_points, items[0])
            index_map[items[0]] = index
            index1, index = index, index+1

        index2 = index_map.get(items[1])
        if index2 is None:
            mw_points = _radec_from_img(mw_points, items[1])
            index_map[items[1]] = index
            index2, index = index, index+1

        index3 = index_map.get(items[2])
        if index3 is None:
            mw_points = _radec_from_img(mw_points, items[2])
            index_map[items[2]] = index
            index3, index = index, index+1

        r, g, b = items[3][4:-1].split(',')
        r = int(r) / 255.0
        g = int(g) / 255.0
        b = int(b) / 255.0

        mw_triangles.append([index1, index2, index3, (r, g, b)])

    return mw_points, mw_triangles
