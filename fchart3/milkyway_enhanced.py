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

from .deepsky_object import *
from .htm.htm import HTM

RAD2DEG = 180.0/np.pi


class EnhancedMilkyWay:
    def __init__(self, milkyway_filename):
        self.sky_mesh = HTM(4)
        self.polygon_center_blocks = [None] * self.sky_mesh.size()
        self.mw_points = None
        self.mw_polygons = []
        self.add_polygons(milkyway_filename)

    def _radec_from_img(self, point):
        x, y = point.split(',')
        x, y = int(x), int(y)
        ra = 2.5 * np.pi - 2.0*np.pi * x / 2048
        dec = - np.pi * (y-512) / 1024
        return ra, dec

    def add_polygons(self, milkyway_filename):
        milkyway_file = open(milkyway_filename, 'r')
        lines = milkyway_file.readlines()
        milkyway_file.close()

        mw_radec = []
        arr_ra, arr_dec, poly_index = ([], [], [])
        index_map = {}

        cur_index = 0

        for line in lines:
            items = line.split()
            if items[-1] == 'rgb(0,0,0)':
                continue

            polygon = []

            sum_ra = 0.0
            sum_dec = 0.0

            n_points = len(items)-1
            for i in range(n_points):
                point_index = index_map.get(items[i])
                if point_index is None:
                    ra, dec = self._radec_from_img(items[i])
                    mw_radec.append((ra, dec,))
                    if self.mw_points is None:
                        self.mw_points = np.array([[ra, dec]])
                    else:
                        self.mw_points = np.append(self.mw_points, [[ra, dec]], axis=0)
                    index_map[items[i]] = cur_index
                    point_index = cur_index
                    cur_index += 1
                else:
                    ra, dec = mw_radec[point_index]
                sum_ra += ra
                sum_dec += dec
                polygon.append(point_index)

            arr_ra.append(sum_ra * RAD2DEG / n_points)
            arr_dec.append(sum_dec * RAD2DEG / n_points)
            poly_index.append(len(self.mw_polygons))

            r, g, b = items[-1][4:-1].split(',')
            r = int(r) / 255.0
            g = int(g) / 255.0
            b = int(b) / 255.0

            self.mw_polygons.append([polygon, (r, g, b)])

        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)
        indexes = self.sky_mesh.lookup_id(arr_ra, arr_dec)
        for i in range(len(indexes)):
            index = indexes[i] ^ mask
            if self.polygon_center_blocks[index] is None:
                self.polygon_center_blocks[index] = [poly_index[i]]
            else:
                self.polygon_center_blocks[index].append(poly_index[i])

    def select_polygons(self, fieldcentre, radius):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_polygons = self.polygon_center_blocks[trixel ^ mask]
            if trixel_polygons is not None:
                selection.extend(trixel_polygons)

        return selection

