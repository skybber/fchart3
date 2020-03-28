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
    '2STAR': STARS,
    'ASTER': STARS,
}

CATALOG_SPECS0 = { 'Sh2-' }
CATALOGS_SPEC2 = ['vdB-Ha' ]
DEFAULT_SHOWING_CATALOGUES = ['M', 'NGC', 'IC', 'Abell', 'HCG', 'Cr', 'PK', 'Stock', 'UGC', 'Mel', 'PGC', 'PNG']

def parse_catalog_name(dso_name):
    i = 0
    name_len = len(dso_name)
    while i < name_len:
        if not dso_name[i].isalpha():
            break
        i += 1
    else:
        return None, dso_name

    if dso_name[i].isdigit(): # handle catalog names in format X[0..9][-_]*+
        if i < name_len - 1:
            if dso_name[i+1] == '-' or dso_name[i+1] == '_':
                if i==1 and dso_name[0] == 'M': # special handling for minkowski
                    return 'Mi', dso_name[1:]
                for prefix in CATALOG_SPECS0:
                    if dso_name.startswith(prefix):
                        return dso_name[:len(prefix)-1],dso_name[len(prefix):]
                return dso_name[:i],dso_name[i:]
    if not dso_name[i].isdigit():
        for prefix in CATALOGS_SPEC2:
            if dso_name.startswith(prefix):
                return dso_name[:len(prefix)],dso_name[len(prefix):]
        # print('Unknown {}'.format(dso_name))
        return None, dso_name
    return dso_name[:i], dso_name[i:]

def _parse_hnsky_line(line, show_catalogs):
    object = DeepskyObject()
    items = line.split(',')

    object.ra = 2.0 * np.pi * float(items[0])/864000.0
    object.dec = np.pi * float(items[1])/(324000.0 * 2.0)
    str_mag = items[2].strip()
    if str_mag:
        object.mag = float(str_mag)/10.0

    names = items[3].split('/')

    has_cat = False
    visible = False
    for n in names:
        cat, name = parse_catalog_name(n)
        if cat:
            visible =  visible or cat in show_catalogs
            if not has_cat:
                object.cat = cat
                object.name = name
                object.all_names = [name]
                has_cat = True
            else:
                object.synonyms.append((cat, name))

            if cat == 'M' and name.isdigit():
                object.messier = int(name)

    object.visible = visible

    types = items[4].split('/')

    obj_type = types[0].strip()
    indx = obj_type.find('[')
    if indx == -1:
        indx = obj_type.find(';')
    if indx > 0:
        obj_type = obj_type[:indx]

    object.type = dso_type_map.get(obj_type, UNKNOWN)

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

def import_hnsky_deepsky(filename, show_catalogs):# or 'IC'
    """
    Reads data from HNKSKY's deep_sky.hnd. Returns a list
    of DeepskyObjects()
    """
    hnd_file = open(filename, 'r', encoding='ISO-8859-1')
    lines   = hnd_file.readlines()[2:]
    hnd_file.close()

    all_show_catalogs = set()
    all_show_catalogs.update(DEFAULT_SHOWING_CATALOGUES)
    if show_catalogs:
        all_show_catalogs.update(show_catalogs)

    dso_list = []
    if not show_catalogs:
        show_catalogs = []
    for line in lines:
        dso_list.append(_parse_hnsky_line(line, all_show_catalogs))

    return dso_list

if __name__=='__main__':
    print(__file__)

    dso_list_single = import_hnsky_deepsky('data/catalogs/deep_sky.hnd')

    print(len(dso_list_single))

    deeplist = dso_list_single
