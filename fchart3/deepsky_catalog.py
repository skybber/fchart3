#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020  Michiel Brentjens
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
import numpy as np

from .deepsky_object import *
from .astrocalc import *

class DeepskyCatalog:
    def __init__(self, deepsky_list=[], force_messier = False, reject_doubles=False):
        self.deepsky_list = []
        self.names = []
        self.force_messier = force_messier
        self.showing_dsos = set()
        self.add_objects(deepsky_list, reject_doubles)


    def add_showing_dso(self, dso):
        self.showing_dsos.add(dso)


    def clear_showing_dsos(self):
        self.showing_dsos.clear()


    def add_objects(self, objects, reject_doubles=False):
        # Sort
        deepsky_list = []
        if type(objects) != type([]):
            deepsky_list = list([objects])
        else:
            deepsky_list = list(objects)

        if reject_doubles:
            # Reject doubles
            deepsky_list.sort(cmp_name)

            for obj in deepsky_list:
                name = obj.cat.upper() + ' ' + obj.name.upper()
                n = obj.name
                if len(self.names) == 0:
                    self.deepsky_list.append(obj)
                    self.names.append(name)
                else:
                    ra = obj.ra
                    dec = obj.dec
                    include = True
                    ang_dist = angular_distance

                    old_list = list(self.deepsky_list)
                    old_list.reverse()
                    for old in old_list:
                        if obj.name in old.all_names:
                            old.all_names.append(obj.name)
                            include = False
                            break

                    if include:
                        self.deepsky_list.append(obj)
                        self.names.append(name)

            for obj in self.deepsky_list:
                name = obj.name
                count = 1
                all_names = obj.all_names
                for n in all_names:
                    c = all_names.count(n)
                    if c > count:
                        count = c
                        name = n
                obj.name = name
        else: # Do not reject doubles
            for obj in deepsky_list:
                self.deepsky_list.append(obj)
                self.names.append(obj.cat.upper() + ' ' + obj.name.upper())


    def add_dso(self, obj):
        if not obj in self.deepsky_list:
            self.deepsky_list.append(obj)
            self.names.append(obj.cat.upper() + ' ' + obj.name.upper())


    def compute_names(self):
        self.names = []
        for obj in self.deepsky_list:
            self.names.append(obj.cat.upper()+' '+obj.name.upper())


    def select_deepsky(self, fieldcentre, radius, lm_deepsky):
        """
        returns a list of deepsky objects meeting the set requirements.

        fieldcentre is a tuple (ra, dec) in radians. radius is also in
        radians
        """
        pos_mag_array = np.zeros((len(self.deepsky_list),3),dtype=np.float64)
        for i in range(len(self.deepsky_list)):
            pos_mag_array[i,0] = self.deepsky_list[i].ra
            pos_mag_array[i,1] = self.deepsky_list[i].dec
            pos_mag_array[i,2] = self.deepsky_list[i].mag

        ra = pos_mag_array[:,0]
        dec = pos_mag_array[:,1]

        object_in_field = np.logical_and(np.abs((ra-fieldcentre[0])*np.cos(dec)) < radius, np.abs(dec-fieldcentre[1]) < radius)
        indices = np.where(object_in_field == 1)[0]

        selected_list_pos = []
        for index in indices:
            selected_list_pos.append(self.deepsky_list[index])

        # select on magnitude
        selection = []
        for obj in selected_list_pos:
            if obj.mag <= lm_deepsky or (obj.messier > 0 and self.force_messier) or obj in self.showing_dsos:
                selection.append(obj)

        return DeepskyCatalog(selection, reject_doubles=False)


    def select_type(self, typelist=[]):
        selection = []
        if typelist == []:
            selection = list(self.deepsky_list)
        else:
            for obj in self.deepsky_list:
                if obj.type in typelist:
                    selection.append(obj)
        return DeepskyCatalog(selection, reject_doubles=False)


    def sort(self,cmp_func=cmp_ra):
        lst = list(self.deepsky_list)
        lst.sort(cmp_func)
        return DeepskyCatalog(lst, reject_doubles=False)


    def __str__(self):
        s = StringIO()
        for obj in self.deepsky_list:
            s.write(str(obj)+'\n')
        return s.getvalue()[:-1]


__all__ = ['DeepskyCatalog']
