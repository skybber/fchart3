#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005  Michiel Brentjens
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
from numpy import *
from fchart.astrocalc import *

from io import StringIO

class DeepskyCatalog:
    def __init__(self, deepsky_list=[], reject_doubles=False):
        self.deepsky_list = []
        self.names = []
        self.pos_mag_array = zeros((0,3),dtype=float64)

        self.add_objects(deepsky_list, reject_doubles)

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

            for object in deepsky_list:
                name = object.cat.upper()+' '+object.name.upper()
                n = object.name
                if len(self.names) == 0:
                    self.deepsky_list.append(object)
                    self.names.append(name)
                else:
                    ra = object.ra
                    dec = object.dec
                    include = True
                    ang_dist = angular_distance

                    old_list = list(self.deepsky_list)
                    old_list.reverse()
                    for old in old_list:
                        if object.name in old.all_names:
                            old.all_names.append(object.name)
                            include = False
                            break

                    if include:
                        self.deepsky_list.append(object)
                        self.names.append(name)

            for object in self.deepsky_list:
                name = object.name
                count = 1
                all_names = object.all_names
                for n in all_names:
                    c = all_names.count(n)
                    if c > count:
                        count = c
                        name = n
                object.name = name
        else: # Do not reject doubles
            for object in deepsky_list:
                self.deepsky_list.append(object)
                self.names.append(object.cat.upper()+' '+object.name.upper())


        # Recompute help array
        self.pos_mag_array = zeros((len(self.deepsky_list),3),dtype=float64)
        for i in range(len(self.deepsky_list)):
            self.pos_mag_array[i,0] = self.deepsky_list[i].ra
            self.pos_mag_array[i,1] = self.deepsky_list[i].dec
            self.pos_mag_array[i,2] = self.deepsky_list[i].mag

    def compute_names(self):
        self.names = []
        for object in self.deepsky_list:
            self.names.append(object.cat.upper()+' '+object.name.upper())


    def select_deepsky(self, fieldcentre, radius, lm_deepsky=100.0, force_messier=False):
        """
        returns a list of deepsky objects meeting the set requirements.

        fieldcentre is a tuple (ra, dec) in radians. radius is also in
        radians
        """
        ra = self.pos_mag_array[:,0]
        dec = self.pos_mag_array[:,1]

        object_in_field = logical_and(abs((ra-fieldcentre[0])*cos(dec)) < radius, abs(dec-fieldcentre[1]) < radius)
        indices = where(object_in_field == 1)[0]

        selected_list_pos = []
        for index in indices:
            selected_list_pos.append(self.deepsky_list[index])

        # select on magnitude
        selection = []
        for object in selected_list_pos:
            if object.mag <= lm_deepsky or (object.messier > 0 and force_messier):
                selection.append(object)

        return DeepskyCatalog(selection, reject_doubles=False)


    def select_type(self, typelist=[]):
        selection = []
        if typelist == []:
            selection = list(self.deepsky_list)
        else:
            for object in self.deepsky_list:
                if object.type in typelist:
                    selection.append(object)
        return DeepskyCatalog(selection, reject_doubles=False)


    def sort(self,cmp_func=cmp_ra):
        lst = list(self.deepsky_list)
        lst.sort(cmp_func)
        return DeepskyCatalog(lst, reject_doubles=False)

    def __str__(self):
        s = StringIO()
        for object in self.deepsky_list:
            s.write(str(object)+'\n')
        return s.getvalue()[:-1]


__all__ = ['DeepskyCatalog']
