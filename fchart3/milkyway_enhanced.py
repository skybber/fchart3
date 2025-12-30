#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2025 fchart3 authors
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
from collections import defaultdict, deque

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
        tmp = time()-tm
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
        self.mw_opti_polygons = self._merge_polygons(self.mw_opti_polygons, max_col_diff)
        self.mw_opti_polygons = self._merge_polygons(self.mw_opti_polygons, max_col_diff)
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
                edges = merged_poly_ar[pol_ind]
                if not edges:
                    out_polygons.append([polygons[pol_ind][0][:], polygons[pol_ind][1]])
                    continue

                loops = self._edges_to_polygons(edges)
                if not loops:
                    out_polygons.append([polygons[pol_ind][0][:], polygons[pol_ind][1]])
                    continue

                main_loop = max(loops, key=len)
                rgb = polygons[pol_ind][1]
                out_polygons.append([main_loop, rgb])

        return out_polygons

    def _merge_edges(self, edges1, edges2):
        if edges1 is None: edges1 = []
        if edges2 is None: edges2 = []

        from collections import defaultdict
        count = defaultdict(int)
        ab_map = {}

        for e in edges1 + edges2:
            key, a, b = e
            count[key] ^= 1  # mod 2
            ab_map[key] = (a, b)

        boundary = []
        for key, c in count.items():
            if c == 1:
                a, b = ab_map[key]
                if a != b:
                    boundary.append([key, a, b])

        return boundary

    def _edges_to_polygons(self, edges):
        if not edges:
            return []

        adj = defaultdict(list)
        for _, a, b in edges:
            if a == b:
                continue
            adj[a].append(b)
            adj[b].append(a)

        work = {u: adj[u][:] for u in adj}
        loops = []

        visited = set()
        for start in list(work.keys()):
            if start in visited:
                continue
            comp = []
            q = deque([start]);
            visited.add(start)
            while q:
                u = q.popleft()
                comp.append(u)
                for w in work.get(u, []):
                    if w not in visited:
                        visited.add(w)
                        q.append(w)

            local = {u: [v for v in work.get(u, []) if v in comp] for u in comp}

            def pick():
                for u, vs in local.items():
                    if vs:
                        return u, vs[-1]
                return None

            while True:
                sel = pick()
                if sel is None:
                    break
                u, v = sel
                cycle = [u, v]
                local[u].pop()
                local[v].remove(u)

                prev, cur = u, v
                safety = 0
                max_steps = 4 * len(edges) + 10
                while safety < max_steps:
                    safety += 1
                    nxts = [x for x in local.get(cur, []) if x != prev]
                    if not nxts:
                        break
                    nxt = nxts[-1]
                    local[cur].remove(nxt)
                    local[nxt].remove(cur)
                    cycle.append(nxt)
                    prev, cur = cur, nxt
                    if nxt == cycle[0]:
                        cycle.pop()
                        if len(cycle) >= 3:
                            loops.append(cycle)
                        break
        return loops

    def select_polygons(self, field_center, radius):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * field_center[0], RAD2DEG * field_center[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_polygons = self.polygon_center_blocks[trixel ^ mask]
            if trixel_polygons is not None:
                selection.extend(trixel_polygons)

        return selection

    def select_opti_polygons(self, field_center, radius):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * field_center[0], RAD2DEG * field_center[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_polygons = self.opti_polygon_center_blocks[trixel ^ mask]
            if trixel_polygons is not None:
                selection.extend(trixel_polygons)

        return selection
