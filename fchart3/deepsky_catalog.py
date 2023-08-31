#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023  Michiel Brentjens
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


from io import StringIO

from .deepsky_object import *
from .htm.htm import HTM

RAD2DEG = 180.0/np.pi


class DeepskyCatalog:
    def __init__(self, deepsky_list=[], force_messier=False):
        self.deepsky_list = []
        self.force_messier = force_messier
        self.sky_mesh = HTM(4)
        self.dso_blocks = [None] * self.sky_mesh.size()
        self.add_objects(deepsky_list)

    def add_objects(self, objects):
        arr_ra, arr_dec, dso_list = ([], [], [])
        for obj in objects:
            if obj.visible:
                arr_ra.append(obj.ra * RAD2DEG)
                arr_dec.append(obj.dec * RAD2DEG)
                dso_list.append(obj)

        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)
        indexes = self.sky_mesh.lookup_id(arr_ra, arr_dec)
        for i in range(len(indexes)):
            index = indexes[i] ^ mask
            if self.dso_blocks[index] is None:
                self.dso_blocks[index] = [dso_list[i]]
            else:
                self.dso_blocks[index].append(dso_list[i])

    def select_deepsky(self, fieldcentre, radius, lm_deepsky):
        intersecting_trixels = self.sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        selection = []
        mask = 1 << (self.sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_dsos = self.dso_blocks[trixel ^ mask]
            if trixel_dsos is not None:
                for obj in trixel_dsos:
                    if obj.mag <= lm_deepsky or (obj.messier > 0 and self.force_messier):
                        selection.append(obj)

        return selection

    def select_type(self, typelist=[]):
        selection = []
        if len(typelist) == 0:
            selection = list(self.deepsky_list)
        else:
            for obj in self.deepsky_list:
                if obj.type in typelist:
                    selection.append(obj)
        return DeepskyCatalog(selection)

    def sort(self, cmp_func=cmp_ra):
        lst = list(self.deepsky_list)
        lst.sort(cmp_func)
        return DeepskyCatalog(lst)

    def __str__(self):
        s = StringIO()
        for obj in self.deepsky_list:
            s.write(str(obj)+'\n')
        return s.getvalue()[:-1]
