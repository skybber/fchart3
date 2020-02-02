#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
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

import os

from .constellation import ConstellationCatalog
from .composite_star_catalog import CompositeStarCatalog
from .deepsky import get_deepsky_list
from .deepsky_catalog import DeepskyCatalog
from . import deepsky_object as deepsky

class UsedCatalogs:
    def __init__(self, data_dir, usno_nomad_file, limiting_magnitude_deepsky, force_messier, force_asterisms, force_unknown):
        # Read basic catalogs
        self._starcatalog    = CompositeStarCatalog(data_dir, usno_nomad=usno_nomad_file)
        self._deeplist = get_deepsky_list(data_dir)
        self._constellcatalog = ConstellationCatalog(data_dir+os.sep + 'bsc5.dat',
                                               data_dir+os.sep + 'ConstellationLines.dat',
                                               data_dir+os.sep + 'constbnd.dat')

        # Apply magnitude selection to deepsky list, build Messier list
        self._reduced_deeplist = []
        self._messierlist=[]
        for object in self._deeplist:
            if object.messier > 0:
                self._messierlist.append(object)
            if force_messier and object.messier > 0:
                self._reduced_deeplist.append(object)
            elif object.mag <= limiting_magnitude_deepsky \
                   and object.master_object is None \
                   and object.type != deepsky.GALCL \
                   and (object.type != deepsky.STARS or force_asterisms or (object.messier > 0 and object.type == deepsky.STARS))\
                   and (object.type != deepsky.PG or force_unknown or object.type == deepsky.PG and object.mag > -5.0):
                self._reduced_deeplist.append(object)

        self._messierlist.sort(key = lambda x: x.messier)
        self._deepskycatalog = DeepskyCatalog(self._reduced_deeplist)

    @property
    def messierlist(self):
        return self._messierlist

    @property
    def starcatalog(self):
        return self._starcatalog

    @property
    def constellcatalog(self):
        return self._constellcatalog

    @property
    def deepskycatalog(self):
        return self._deepskycatalog

    @property
    def deeplist(self):
        return self._deeplist

    @property
    def reduced_deeplist(self):
        return self._reduced_deeplist


