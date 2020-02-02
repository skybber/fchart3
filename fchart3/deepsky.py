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

import fchart3

from .deepsky_catalog import *
from .deepsky_object import *
from .saguaro import *
from .vic import *
from .revngc import *
from .astrocalc import *


def get_deepsky_list(data_dir=os.path.join(fchart3.get_catalogs_dir())):
    deeplist = []

    m24 = DeepskyObject()
    m24.cat ='IC'
    m24.name ='4715'
    m24.messier = 24
    m24.type = STARS
    m24.ra = hms2rad(18,16.9)
    m24.dec = dms2rad(18,29,0,-1)
    m24.mag = 3.1
    m24.rlong = 95*pi/(180.0*60)
    m24.rshort=35*pi/(180.0*60)
    m24.constellation='SGR'
    deeplist.append(m24)

    m40 = DeepskyObject()
    m40.cat = 'Winnecke'
    m40.name = '4'
    m40.messier=40
    m40.type=STARS
    m40.ra = hms2rad(12,22,16)
    m40.dec= dms2rad(58,0o5, 4)
    m40.mag=9.0
    m40.rlong=1.0*pi/(180*60.0)
    m40.constellation='UMA'
    deeplist.append(m40)

    m45 = DeepskyObject()
    m45.cat = 'Mel'
    m45.name = '22'
    m45.messier=45
    m45.type=OC
    m45.ra= hms2rad(3,47.0)
    m45.dec=dms2rad(24,7)
    m45.mag=1.4
    m45.rlong=110*pi/(180*60.0*2.0)
    m45.constellation='TAU'
    deeplist.append(m45)

    print('Reading NGC...')
    ngclist, ngclist_multiple = import_revised_ngcic(os.path.join(data_dir,'revngc.txt'), 'NGC')
    print('Reading IC...')
    iclist, iclist_multiple  = import_revised_ngcic(os.path.join(data_dir,'revic.txt'), 'IC')
    print('Reading SAC...')
    saclist = import_saguaro(os.path.join(data_dir, 'sac.txt'))
    print('Reading VIC...')
    viclist = import_vic(os.path.join(data_dir, 'vic.txt'))

    print('Sorting Sac...')
    saclist.sort(key=cmp_to_key(cmp_name))

    ngcstart = 0
    ngcend   = 0
    icstart = 0
    icend   = 0
    index = 0
    print("searching index_start")
    while index < len(saclist):
        if saclist[index].cat == 'IC':
            icstart = index
            index += 1
            while saclist[index].cat == 'IC':
                index += 1
            icend = index
        if saclist[index].cat == 'NGC':
            ngcstart = index
            index += 1
            while saclist[index].cat == 'NGC':
                index += 1
            ngcend = index
        if ngcstart*ngcend*icstart*icend != 0:
            break
        index += 1
    print("done")
    deeplist += saclist[0:icstart]

    deeplist += saclist[ngcend:]+ngclist +ngclist_multiple +iclist+iclist_multiple+viclist
    deeplist.sort(key=cmp_to_key(cmp_name))
    return deeplist


def get_deepsky_catalog(data_dir=os.path.join(fchart3.get_catalogs_dir())):
    l = get_deepsky_list(data_dir)
    print(len(l))
    dc = DeepskyCatalog(l)
    return dc


import fchart3.deepsky_object

__all__=['get_deepsky_list', 'get_deepsky_catalog', 'DeepskyCatalog']+fchart3.deepsky_object.__all__
