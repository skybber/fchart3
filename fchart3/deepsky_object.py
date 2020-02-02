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

import numpy as np

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

UNKNOWN=0
G=1
N=2
PN=3
OC=4
GC=5
PG=6
ALREADY_LISTED_1=7
ALREADY_LISTED_2=8
STARS=9
NOTFOUND=10
SNR=11
QSO=12
GALCL=13


TYPENAME=['Unknown',
          'G', 'N', 'PN', 'OC', 'GC', 'PG', 'xxx', 'xxx', 'AST', 'xxx', 'SNR', 'QSO', 'GALCL']

class DeepskyObject:
    def __init__(self, catalog='NGC'):
        """
        This class has the following fields:

        - cat            name of catalog ('NGC', 'IC', 'MEL',...). Not 'M'.
                         If the object is also in the Messier list, the
                         messier field is larger than 0
        - name           primary name of object in that catalog ('891',
                         '3683A',...)
        - all_names      all names of the object in this catalog.
        - component      number of component if source consists of multiple
                         components (default: 0)
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
        - constellation  three letter constellation abbreviation, e.g. AND
        - ra             right ascension in radians (J2000)
        - dec            declination in radians (J2000)
        - mag            magnitude
        - rlong          long dimension of object in radians (-1 if unknown)
        - rshort         short dimension of object in radians (-1 if unknown)
        - position_angle position angle (N through E) in radians
                         (default: 0.5np.pi)
        - messier        number in messier list (default: -1)
        """
        self.cat    = catalog.upper().rstrip().lstrip()
        self.name = ''
        self.all_names = []
        self.component = 0
        self.type   = UNKNOWN
        self.constellation=''
        self.ra=-1.0
        self.dec=0.0
        self.mag=-100.0
        self.rlong=-1.0
        self.rshort=-1.0
        self.position_angle=90.0*np.pi/180.0
        self.messier=-1
        self.master_object = None


    def __str__(self):
        s = ''
        rah, ram, ras,sign = rad2hms_t(self.ra)
        decd, decm, decs,sign = rad2dms_t(self.dec)

        cat  = self.cat
        name = self.name
        if self.messier > 0:
            cat = 'M'
            name = str(self.messier)

        s += cat.ljust(8)+' '+name.rjust(8)+' '+self.constellation
        s +='  '
        s += str(rah).rjust(3)+str(ram).rjust(3)+str(int(ras+0.5)).rjust(3)
        s += '  '
        if sign >= 0:
            s += '+'
        else:
            s += '-'
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


def cmp_ra(x,y):
    r = 0
    if x.ra > y.ra:
        r = 1
    if x.ra < y.ra:
        r = -1
    return r


def cmp_dec(x,y):
    r = 0
    if x.dec > y.dec:
        r = 1
    if x.dec < y.dec:
        r = -1
    return r

def cmp_name(x,y):
    xn = (x.cat+x.name).upper()
    yn = (y.cat+y.name).upper()
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

__all__ = ['DeepskyObject','UNKNOWN',
           'G', 'N', 'PN', 'OC','GC', 'PG',
           'ALREADY_LISTED_1', 'ALREADY_LISTED_2', 'STARS',
           'NOTFOUND', 'SNR', 'QSO','GALCL','cmp_ra', 'cmp_dec', 'cmp_name', 'cmp_to_key']
