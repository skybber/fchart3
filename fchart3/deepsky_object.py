#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
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

from .astrocalc import rad2hms_t, rad2dms_t

#   0: unknown
#   1: galaxy
#   2: Galactic nebula
#   3: planetary nebula
#   4: open cluster
#   5: globular cluster
#   6: part of galaxy (star cloud, HII region)
#   7: already elsewhere in NGC or IC
#   8: IC object already in NGC
#   9: Star(s)
#  10: Not found
#  11: SNR
#  12: QSO, quasar
#  13: GALCL, galaxy cluster

UNKNOWN = 0
G = 1
N = 2
PN = 3
OC = 4
GC = 5
PG = 6
ALREADY_LISTED_1 = 7
ALREADY_LISTED_2 = 8
STARS = 9
NOTFOUND = 10
SNR = 11
QSO = 12
GALCL = 13


TYPENAME = ['Unknown', 'G', 'N', 'PN', 'OC', 'GC', 'PG', 'xxx', 'xxx', 'AST', 'xxx', 'SNR', 'QSO', 'GALCL']


class DeepskyObject:
    __slots__ = (
        'cat', 'name', 'all_names', 'synonyms', 'type', 'ra', 'dec', 'x', 'y', 'z',
        'mag', 'rlong', 'rshort', 'position_angle', 'messier', 'master_object', 'visible', 'outlines'
    )

    _DEFAULT_CAT = 'NGC'
    _PA_DEFAULT = np.pi * 0.5
    _EMPTY_TUPLE = ()

    def __init__(self):
        """
        This class has the following fields:

        - cat            name of catalog ('NGC', 'IC', 'MEL',...). Not 'M'.
                         If the object is also in the Messier list, the
                         messier field is larger than 0
        - name           primary name of object in that catalog ('891',
                         '3683A',...)
        - all_names      all names of the object in this catalog.
        - synonyms       all object synonyms
        - type           integer indicating the type of the object. There
                         are constants defined in this module to help
                         interpret this field:
                         UNKNOWN         = 0      unknown type
                         G               = 1      galaxy
                         N               = 2      diffuse nebula
                         PN              = 3      planetary nebula
                         OC              = 4      open cluster
                         GC              = 5      globular cluster
                         PG              = 6      part of other galaxy
                         ALREADY_LISTED_1= 7      already in catalog
                         ALREADY_LISTED_2= 8      already in catalog
                         STARS           = 9      asterism
                         NOTFOUND        =10      not found in reality/error
                         SNR             =11      supernova remnant
        - ra             right ascension in radians (J2000)
        - dec            declination in radians (J2000)
        - mag            magnitude
        - rlong          long dimension of object in radians (-1 if unknown)
        - rshort         short dimension of object in radians (-1 if unknown)
        - position_angle position angle (N through E) in radians
                         (default: 0.5np.pi)
        - messier        number in messier list (default: -1)
        - visible        True if object is visible on the map
        """
        self.cat = self._DEFAULT_CAT
        self.name = ''
        self.all_names = self._EMPTY_TUPLE
        self.synonyms = self._EMPTY_TUPLE

        self.type = UNKNOWN
        self.ra = -1.0
        self.dec = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.mag = -100.0
        self.rlong = -1.0
        self.rshort = -1.0
        self.position_angle = self._PA_DEFAULT
        self.messier = -1
        self.master_object = None
        self.visible = True
        self.outlines = None

    def add_name(self, n: str):
        if self.all_names is self._EMPTY_TUPLE:
            self.all_names = [n]
        else:
            self.all_names.append(n)

    def add_synonym(self, cat_name_tuple):
        if self.synonyms is self._EMPTY_TUPLE:
            self.synonyms = [cat_name_tuple]
        else:
            self.synonyms.append(cat_name_tuple)

    def set_names_sorted(self):
        if not self.all_names:
            self.all_names = self._EMPTY_TUPLE
        elif isinstance(self.all_names, list):
            self.all_names.sort()
            self.all_names = tuple(self.all_names)

    def label(self):
        if self.messier > 0:
            label = f'M {self.messier}'
        elif self.cat == 'NGC':
            if isinstance(self.all_names, list):
                names = sorted(self.all_names)
            else:
                names = self.all_names
            label = '-'.join(names)
        elif self.cat == 'Abell':
            label = self.cat + ' ' + self.name
        elif self.cat == 'Sh2':
            if isinstance(self.all_names, list):
                names = sorted(self.all_names)
            else:
                names = self.all_names
            label = self.cat + '-' + '-'.join(names)
        else:
            if isinstance(self.all_names, list):
                names = sorted(self.all_names)
            else:
                names = self.all_names
            label = self.cat + ' ' + '-'.join(names)
        return label

    def primary_label(self):
        if self.messier > 0:
            label = f'M {self.messier}'
        elif self.cat == 'Sh2':
            label = f'Sh2-{self.name}'
        else:
            label = f'{self.cat} {self.name}'
        return label

    def __str__(self):
        s = ''
        rah, ram, ras, sign_ra = rad2hms_t(self.ra)
        decd, decm, decs, sign_dec = rad2dms_t(self.dec)

        cat = 'M' if self.messier > 0 else self.cat
        name = str(self.messier) if self.messier > 0 else self.name

        s += cat.ljust(8)+' '+name.rjust(8)
        s += '  '
        s += str(rah).rjust(3)+str(ram).rjust(3)+str(int(ras+0.5)).rjust(3)
        s += '  '
        s += ('+' if sign_dec >= 0 else '-')
        s += str(decd).rjust(2)+str(decm).rjust(3)+str(int(decs+0.5)).rjust(3)
        if self.mag > -90:
            s += ' '+str(self.mag).rjust(6)+' '
        else:
            s += '        '
        if self.rlong > 0.0:
            s += str(int(self.rlong*180*60/np.pi*10+0.5)/10.0).rjust(6)
        else:
            s += '      '
        if self.rshort > 0.0:
            s += str(int(self.rshort*180*60/np.pi*10+0.5)/10.0).rjust(6)
        else:
            s += '      '

        s += ' '+TYPENAME[self.type].ljust(8)
        return s


class UnknownNebula:
    def __init__(self):
        """
        This class represents uncatalogied nubula
        """
        self.outlines = [ None, None, None ]
        self.ra_min, self.ra_max, self.dec_min, self.dec_max = (None, None, None, None)

    def add_outlines(self, level, outlines):
        for ra in outlines[0]:
            if self.ra_min is None or ra < self.ra_min:
                self.ra_min = ra
            if self.ra_max is None or ra > self.ra_max:
                self.ra_max = ra
        for dec in outlines[1]:
            if self.dec_min is None or dec < self.dec_min:
                self.dec_min = dec
            if self.dec_max is None or dec > self.dec_max:
                self.dec_max = dec

        if self.outlines[level] is None:
            self.outlines[level] = []

        self.outlines[level].append(outlines)


def cmp_ra(x, y):
    r = 0
    if x.ra > y.ra:
        r = 1
    if x.ra < y.ra:
        r = -1
    return r


def cmp_dec(x, y):
    r = 0
    if x.dec > y.dec:
        r = 1
    if x.dec < y.dec:
        r = -1
    return r


def cmp_name(x,y):
    xn = x.label()
    yn = y.label()
    r = 0
    if xn > yn:
        r = 1
    if xn < yn:
        r = -1
    return r


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
