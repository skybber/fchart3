#    fchart3 draws beautiful deepsky charts in vector formats
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
    def __init__(self, deepsky_list=[], force_messier = False):
        self.deepsky_list = []
        self.visible_deepsky_list = []
        self.names = []
        self.force_messier = force_messier
        self.add_objects(deepsky_list)


    def add_objects(self, objects):
        # Sort
        # deepsky_list = []
        #if type(objects) != type([]):
        #    deepsky_list = list([objects])
        #else:
        #    deepsky_list = list(objects)

        for obj in objects:
            self.deepsky_list.append(obj)
            if obj.visible:
                self.visible_deepsky_list.append(obj)
            self.names.append(obj.cat.upper() + ' ' + obj.name.upper())


    def add_dso(self, obj):
        if not obj in self.deepsky_list:
            self.deepsky_list.append(obj)
            self.names.append(obj.cat.upper() + ' ' + obj.name.upper())
            if obj.visible:
                self.visible_deepsky_list.append(obj)


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
        pos_mag_array = np.zeros((len(self.visible_deepsky_list),3),dtype=np.float64)
        for i in range(len(self.visible_deepsky_list)):
            pos_mag_array[i,0] = self.visible_deepsky_list[i].ra
            pos_mag_array[i,1] = self.visible_deepsky_list[i].dec
            pos_mag_array[i,2] = self.visible_deepsky_list[i].mag

        ra = pos_mag_array[:,0]
        dec = pos_mag_array[:,1]

        object_in_field = np.logical_and(np.abs((ra-fieldcentre[0])*np.cos(dec)) < radius, np.abs(dec-fieldcentre[1]) < radius)
        indices = np.where(object_in_field == 1)[0]

        selected_list_pos = []
        for index in indices:
            selected_list_pos.append(self.visible_deepsky_list[index])

        # select on magnitude
        selection = []
        for obj in selected_list_pos:
            if obj.mag <= lm_deepsky or (obj.messier > 0 and self.force_messier):
                selection.append(obj)

        return selection


    def select_type(self, typelist=[]):
        selection = []
        if typelist == []:
            selection = list(self.deepsky_list)
        else:
            for obj in self.deepsky_list:
                if obj.type in typelist:
                    selection.append(obj)
        return DeepskyCatalog(selection)


    def sort(self,cmp_func=cmp_ra):
        lst = list(self.deepsky_list)
        lst.sort(cmp_func)
        return DeepskyCatalog(lst)


    def __str__(self):
        s = StringIO()
        for obj in self.deepsky_list:
            s.write(str(obj)+'\n')
        return s.getvalue()[:-1]

