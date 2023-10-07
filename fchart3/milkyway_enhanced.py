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
import gettext
import os

uilanguage=os.environ.get('fchart3lang')
try:
    lang = gettext.translation( 'messages',localedir='locale', languages=[uilanguage])
    lang.install()
    _ = lang.gettext
except:                  
    _ = gettext.gettext


from .deepsky_object import *
from .htm.htm import HTM

from time import time


RAD2DEG = 180.0/np.pi


class EnhancedMilkyWay:
    def __init__(self, milkyway_filename, optim_max_col_diff=None):
        self.sky_mesh = HTM(4)
        self.polygon_center_blocks = [None] * self.sky_mesh.size()
        self.opti_polygon_center_blocks = [None] * self.sky_mesh.size()
        self.mw_points = None
        self.mw_polygons = []
        self.mw_opti_polygons = None
        tm = time()
        self.add_polygons(milkyway_filename)
        tmp=time()-tm
        if optim_max_col_diff is not None and optim_max_col_diff > 0 and optim_max_col_diff < 1.0:
            self._create_opti_polygons(optim_max_col_diff)
            print( _("Enhanced milky way initialized within {}s. Optimized polygons={}, total polygons={}".format(tmp, len(self.mw_opti_polygons), len(self.mw_polygons))), flush=True)
                
        else:
            print(_("Enhanced milky way initialized within {}s. Total polygons={}".format(tmp, len(self.mw_polygons))), flush=True)
            

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

    def _create_opti_polygons(self, max_col_diff):
        self.mw_opti_polygons = self._merge_polygons(self.mw_polygons, max_col_diff)
        arr_ra, arr_dec, poly_index = ([], [], [])
        ind = 0
        for polygon, _ in self.mw_opti_polygons:
            sum_ra = 0.0
            sum_dec = 0.0
            for point_ind in polygon:
                sum_ra += self.mw_points[point_ind][0]
                sum_dec += self.mw_points[point_ind][1]
            arr_ra.append(sum_ra * RAD2DEG / len(polygon))
            arr_dec.append(sum_dec * RAD2DEG / len(polygon))
            poly_index.append(ind)
            ind += 1

        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)
        indexes = self.sky_mesh.lookup_id(arr_ra, arr_dec)
        for i in range(len(indexes)):
            index = indexes[i] ^ mask
            if self.opti_polygon_center_blocks[index] is None:
                self.opti_polygon_center_blocks[index] = [poly_index[i]]
            else:
                self.opti_polygon_center_blocks[index].append(poly_index[i])

    def _merge_polygons(self, polygons, max_col_diff):
        merges = 0

        npoints = len(self.mw_points)
        merge_to_ind_ar = [-1] * len(polygons)
        merged_poly_ar = [None] * len(polygons)
        edge_join_map = {}

        for pol_ind, pol_def in enumerate(polygons):
            polygon = pol_def[0]
            r, g, b = pol_def[1]

            min_diff = max_col_diff
            min_merge_pol_ind = -1

            edges = []

            for point_ind in range(len(polygon)):
                i1, i2 = polygon[point_ind], polygon[(point_ind+1) % len(polygon)]
                if i1 > i2:
                    i1, i2 = i2, i1
                edge_key = i1 * npoints + i2

                edges.append([edge_key, polygon[point_ind], polygon[(point_ind+1) % len(polygon)]])

                if edge_key in edge_join_map:
                    merge_pol_ind = edge_join_map[edge_key]

                    while merge_to_ind_ar[merge_pol_ind] != -1:
                        merge_pol_ind = merge_to_ind_ar[merge_pol_ind]

                    rj, gj, bj = polygons[merge_pol_ind][1]
                    diff = abs(r-rj) + abs(g-gj) + abs(b-bj)
                    if diff < min_diff:
                        min_diff = diff
                        min_merge_pol_ind = merge_pol_ind

            if min_merge_pol_ind != -1:
                merges += 1
                merge_to_ind_ar[pol_ind] = min_merge_pol_ind
                merged_poly_ar[min_merge_pol_ind] = self._merge_edges(merged_poly_ar[min_merge_pol_ind], edges)
            else:
                for edge_key, _, _ in edges:
                    edge_join_map[edge_key] = pol_ind
                merged_poly_ar[pol_ind] = edges

        out_polygons = []
        for pol_ind, merge_to in enumerate(merge_to_ind_ar):
            if merge_to == -1:
                polygon = []
                for edge in merged_poly_ar[pol_ind]:
                    polygon.append(edge[1])
                rgb = polygons[pol_ind][1]
                out_polygons.append([polygon, rgb])

        return out_polygons

    def _merge_edges(self, edges1, edges2):
        out_edges = []
        for e1 in edges1:
            if not any(e1[0] == e2[0] for e2 in edges2) and e1[1] != e1[2]:
                out_edges.append([e1[0], e1[1], e1[2]])
        for e2 in edges2:
            if not any(e2[0] == e1[0] for e1 in edges1) and e2[1] != e2[2]:
                out_edges.append([e2[0], e2[1], e2[2]])
        end_point = -1;
        res_edges = []
        for i in range(len(out_edges)):
            e = out_edges[i]
            if end_point == -1 or e[1] == end_point:
                res_edges.append(e)
                end_point = e[2]
                continue
            for j in range(i, len(out_edges)):
                te = out_edges[j]
                if te[1] == end_point:
                    out_edges[i], out_edges[j] = out_edges[j], out_edges[i]
                    break
                if te[2] == end_point:
                    te[1], te[2] = te[2], te[1]
                    if j != i:
                        out_edges[i], out_edges[j] = out_edges[j], out_edges[i]
                    break
            e = out_edges[i]
            res_edges.append(e)
            end_point = e[2]
        return res_edges

    def select_polygons(self, fieldcentre, radius):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_polygons = self.polygon_center_blocks[trixel ^ mask]
            if trixel_polygons is not None:
                selection.extend(trixel_polygons)

        return selection

    def select_opti_polygons(self, fieldcentre, radius):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_polygons = self.opti_polygon_center_blocks[trixel ^ mask]
            if trixel_polygons is not None:
                selection.extend(trixel_polygons)

        return selection
