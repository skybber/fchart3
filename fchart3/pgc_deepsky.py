#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2021 fchart authors
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

from .deepsky_object import *
from .hnsky_deepsky import parse_catalog_name, dso_type_map


def import_pgc_deepsky(filename, show_catalogs, all_dsos):
    sf = open(filename, 'r')
    lines = sf.readlines()
    sf.close()

    dso_list = []

    for line in lines:

        if len(line[6:37].strip()) == 0:
            continue

        pgc_num = int(line[0:5])

        alt_names = [
            line[77:93].strip().replace(' ', ''),
            line[93:109].strip().replace(' ', ''),
            line[109:125].strip().replace(' ', ''),
            line[125:141].strip().replace(' ', '')
        ]

        pgc_name = 'PGC{}'.format(pgc_num)
        pgc_dso = all_dsos.get(pgc_name)

        if not pgc_dso:
            for name in alt_names:
                pgc_dso = all_dsos.get(name)
                if pgc_dso:
                    break

        if pgc_dso is None:
            for ugc_name in alt_names:
                if ugc_name.startswith('UGC') and not ugc_name.startswith('UGCA') and not ugc_name == 'UGC':
                    break
            else:
                ugc_name = None

            pgc_dso = DeepskyObject()
            pgc_dso.ra = float(line[6:8])*np.pi/12.0 + float(line[8:10])*np.pi/(12.0*60.0) + float(line[10:14])*np.pi/(12*60.0*60)
            pgc_dso.dec = float(line[14]+'1')*(float(line[15:17])*np.pi/180.0 + float(line[17:19])*np.pi/(180.0*60) + float(line[19:21])*np.pi/(180.0*60*60))
            pgc_dso.type = dso_type_map.get('GX', UNKNOWN)

            try:
                pgc_dso.mag = float(line[59:63])
            except ValueError:
                pgc_dso.mag = 100.0

            try:
                pgc_dso.rlong = float(line[43:49])/60.0*np.pi/180.0/2.0
            except ValueError:
                pgc_dso.rlong = 15.0/60.0/60.0*np.pi/180.0/2.0

            try:
                pgc_dso.rshort = float(line[51:56])/60.0*np.pi/180.0/2.0
            except ValueError:
                pgc_dso.rshort = pgc_dso.rlong

            try:
                pgc_dso.position_angle = int(line[73:76])*np.pi/180.0
            except ValueError:
                pgc_dso.position_angle = 0.0

            all_dsos[pgc_name] = pgc_dso
            pgc_dso.cat, pgc_dso.name = parse_catalog_name(pgc_name)

            if ugc_name:
                pgc_dso.cat, pgc_dso.name = parse_catalog_name(ugc_name)
                pgc_dso.synonyms.append((pgc_dso.cat, pgc_dso.name))
                all_dsos[ugc_name] = pgc_dso

            pgc_dso.all_names = [pgc_dso.name]

            pgc_dso.visible = True

            dso_list.append(pgc_dso)

    return dso_list
