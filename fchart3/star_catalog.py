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


class StarObject:
    def __init__(self):
        self.ra = None
        self.dec = None
        self.dRa = None
        self.dDec = None
        self.HD = None
        self.mag = None
        self.spec_type = None
        self.flags = None
        self.name = None
        self.name2 = None
        self.lname = None

    def init(self, stardata):
        self.ra = stardata['ra']
        self.dec = stardata['dec']
        self.dRa = stardata['dRa']
        self.dDec = stardata['dDec']
        self.mag = stardata['mag']
        self.spec_type = stardata['spec_type']
        self.flags = stardata['flags']

    def set_names(self, name, name2):
        self.name = name
        self.name2 = name2
        if name and name.startswith('HD'):
            self.lname = name
            if name2:
                self.lname = '(' + name2 + ')'
        elif name2:
            lname = name2


class StarCatalog():
    def select_stars(self, fieldcentre, radius, lm_stars):
        pass
