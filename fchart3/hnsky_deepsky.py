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

from .deepsky_object import *

dso_type_map = {
    'GX': G,
    'BN': N,
    'DN': N,
    'PN': PN,
    'OC': OC,
    'GC': GC,
    'STARS': STARS,
    'QUASR': QSO,
    'GALCL': GALCL,
}

extra_catalogs = ['vdB-Ha']

def parse_catalog_name(name):
    i = 0
    name_len = len(name)
    while i < name_len:
        if not name[i].isalpha():
            break
        i += 1
    else:
        return None, name
    if name[i].isdigit():
        if i < name_len - 1:
            if name[i+1] in ('-'):
                i += 2
    if not name[i].isdigit():
        for prefix in extra_catalogs:
            if name.startswith(prefix):
                return name[:len(prefix)],name[len(prefix):]
        # print('Unknown {}'.format(name))
        return None, name
    return name[:i], name[i:]


def _parse_hnsky_line(line):
    object = DeepskyObject()
    items = line.split(',')

    object.ra = 2.0 * np.pi * float(items[0])/864000.0
    object.dec = np.pi * float(items[1])/(324000.0 * 2.0)
    str_mag = items[2].strip()
    object.mag = float(items[2])/10.0 if str_mag else 100.0

    names = items[3].split('/')

    if not object.mag:
        print(items[3])

    has_cat = False
    for n in names:
        cat, name = parse_catalog_name(n)
        if cat:
            if not has_cat:
                object.cat = cat
                object.name = name
                has_cat = True
            if cat == 'M':
                object.messier = int(name)

    # if len(names) > 1:
    #    object.all_names.extend(names)

    types = items[4].split('/')

    object.type = dso_type_map.get(types[0], UNKNOWN)

    str_length = items[6].strip() if len(items) > 6 else None

    if str_length:
        try:
            object.rlong = float(str_length)/600.0*np.pi/180.0/2.0
        except (ValueError, TypeError):
            object.rlong = None

    str_width = items[7].strip() if len(items) > 7 else None

    if str_width:
        try:
            object.rshort = float(str_width)/600.0*np.pi/180.0/2.0
        except (ValueError, TypeError):
            object.rshort = None

    str_pos_angle = items[8].strip() if len(items) > 8 else None

    if str_pos_angle:
        try:
            object.position_angle = float(str_pos_angle)*np.pi/180.0
        except (ValueError, TypeError):
            object.position_angle = None

    return object

def import_hnsky_deepsky(filename):# or 'IC'
    """
    Reads data from HNKSKY's deep_sky.hnd. Returns a list
    of DeepskyObjects()
    """
    hnd_file = open(filename, 'r', encoding='ISO-8859-1')
    lines   = hnd_file.readlines()[2:]
    hnd_file.close()

    dso_list_single = []
    dso_list_multiple = []

    for line in lines:
        dso = _parse_hnsky_line(line)

        dso_list_single.append(dso)

    return dso_list_single, dso_list_multiple

if __name__=='__main__':
    print(__file__)

    dso_list_single, dso_list_multiple = import_hnsky_deepsky('data/catalogs/deep_sky.hnd')

    print(len(dso_list_single))

    deeplist = dso_list_single

