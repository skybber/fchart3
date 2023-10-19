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
    'CL+NB': OC,
    'NB':  N,
    'DN&HII': N,
    'pA*': UNKNOWN,     # Post-AGB Star (proto-PN)
    'C*': UNKNOWN,      # Carbon Star
    'CV*': UNKNOWN,     # Cataclysmic Variable Star
    'RNe': N,           # Reflection Nebula
    'NL*': UNKNOWN,     # Nova-like Star
    'HII': N
}

CATALOG_SPECS0 = { 'Sh2-' }
CATALOGS_SPEC2 = ['vdB-Ha' ]
DEFAULT_SHOWING_CATALOGUES = ['M', 'NGC', 'IC', 'Abell', 'HCG', 'Cr', 'PK', 'Stock', 'UGC', 'Mel', 'PGC', 'PNG']


def _denormalize_pk_name(name):
    denorm = ''
    compress = True
    outp = False
    for i in range(0, len(name)):
        c = name[i]
        if compress and c == '0':
            continue
        if not c.isdigit():
            if not outp:
                denorm += '0'
            compress = True
            outp = False
        else:
            outp = True
            compress = False
        denorm += c
    return denorm


def parse_catalog_name(dso_name):
    if dso_name.startswith('PN_'):
        dso_name = dso_name[3:]

    if dso_name.startswith('A66_'):
        dso_name = 'Abell' + dso_name[4:]

    if dso_name.startswith('PK_'):
        dso_name = 'PK' + _denormalize_pk_name(dso_name[3:])

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
                if i == 1 and dso_name[0] == 'M': # special handling for minkowski
                    return 'Mi', dso_name[1:]
                for prefix in CATALOG_SPECS0:
                    if dso_name.startswith(prefix):
                        return dso_name[:len(prefix)-1], dso_name[len(prefix):]
                return dso_name[:i], dso_name[i:]
    if not dso_name[i].isdigit():
        for prefix in CATALOGS_SPEC2:
            if dso_name.startswith(prefix):
                return dso_name[:len(prefix)], dso_name[len(prefix):]
        return None, dso_name
    return dso_name[:i], dso_name[i:]


def _parse_hnsky_line(line, show_catalogs, all_dsos):
    object = DeepskyObject()
    items = line.split(',')

    object.ra = 2.0 * np.pi * float(items[0])/864000.0
    object.dec = np.pi * float(items[1])/(324000.0 * 2.0)

    types = items[4].split('/')

    obj_type = types[0].strip()
    indx = obj_type.find('[')
    if indx == -1:
        indx = obj_type.find(';')
    if indx > 0:
        obj_type = obj_type[:indx]

    object.type = dso_type_map.get(obj_type, UNKNOWN)

    str_mag = items[2].strip()

    if str_mag:
        object.mag = float(str_mag)/10.0
    elif obj_type in ('PN', 'GX'):
        object.mag = 15.0
    else:
        object.mag = 100.0

    names = items[3].split('/')

    has_cat = False
    visible = False
    for n in names:
        cat, name = parse_catalog_name(n)
        if cat:
            visible = visible or cat in show_catalogs
            all_dsos[n] = object
            if not has_cat:
                object.cat = cat
                object.name = name
                object.all_names = [name]
                has_cat = True
            else:
                if cat == 'Abell' and (object.cat == 'PK' or object.cat == 'Sh2-') or \
                   cat == 'UGC' and object.cat == 'PGC':
                    object.all_names = [name]
                    object.name, name = name, object.name
                    object.cat, cat = cat, object.cat

                object.synonyms.append((cat, name))

            if cat == 'M' and name.isdigit():
                object.messier = int(name)

    object.visible = visible

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
            object.rshort = object.rlong
    else:
        object.rshort = object.rlong

    str_pos_angle = items[8].strip() if len(items) > 8 else None

    if str_pos_angle:
        try:
            object.position_angle = float(str_pos_angle)*np.pi/180.0
        except (ValueError, TypeError):
            object.position_angle = None

    return object


def import_hnsky_deepsky(filename, show_catalogs, all_dsos):
    """
    Reads data from HNKSKY's deep_sky.hnd. Returns a list
    of DeepskyObjects()
    """
    hnd_file = open(filename, 'r', encoding='ISO-8859-1')
    lines = hnd_file.readlines()[2:]
    hnd_file.close()

    all_show_catalogs = set()
    all_show_catalogs.update(DEFAULT_SHOWING_CATALOGUES)
    if show_catalogs:
        all_show_catalogs.update(show_catalogs)

    dso_list = []
    for line in lines:
        dso_list.append(_parse_hnsky_line(line, all_show_catalogs, all_dsos))

    return dso_list


def _parse_hnsky_supplement_line(line, all_dsos):
    object = DeepskyObject()
    items = line.split(',')

    object.ra = np.pi * float(items[0])/12.0
    if items[1].strip():
        object.ra += np.pi * float(items[1]) / (12.0 * 60.0)
    if items[2].strip():
        object.ra += np.pi * float(items[2]) / (12.0 * 60.0 * 60)
    object.dec = np.pi * float(items[3]) / 180.0
    mul_dec = 1 if object.dec >= 0 else -1
    if items[4].strip():
        object.dec += mul_dec * np.pi * float(items[4]) / (180.0 * 60)
    if items[5].strip():
        object.dec += mul_dec * np.pi * float(items[5]) / (180.0 * 60 * 60)

    str_mag = items[6].strip()

    if str_mag:
        object.mag = float(str_mag) / 10.0
    else:
        object.mag = 100.0

    names = items[7].split('/')

    has_cat = False
    visible = False
    for n in names:
        if n.startswith('['): # skip bibcodes
            continue
        cat, name = parse_catalog_name(n)
        if cat:
            visible = True
            all_dsos[n] = object
            if not has_cat:
                object.cat = cat
                object.name = name
                object.all_names = [name]
                has_cat = True
            else:
                if cat == 'Abell' and (object.cat == 'PK' or object.cat == 'Sh2-') or \
                        cat == 'UGC' and object.cat == 'PGC':
                    object.all_names = [name]
                    object.name, name = name, object.name
                    object.cat, cat = cat, object.cat

                object.synonyms.append((cat, name))

            if cat == 'M' and name.isdigit():
                object.messier = int(name)

    object.visible = visible

    types = items[8].split('/')

    obj_type = types[0].strip()
    indx = obj_type.find('[')
    if indx == -1:
        indx = obj_type.find(';')
    if indx > 0:
        obj_type = obj_type[:indx]

    object.type = dso_type_map.get(obj_type, UNKNOWN)


    str_length = items[10].strip() if len(items) > 10 else None

    if str_length:
        try:
            object.rlong = float(str_length)/600.0*np.pi/180.0/2.0
        except (ValueError, TypeError):
            object.rlong = None

    str_width = items[11].strip() if len(items) > 11 else None

    if str_width:
        try:
            object.rshort = float(str_width)/600.0*np.pi/180.0/2.0
        except (ValueError, TypeError):
            object.rshort = object.rlong
    else:
        object.rshort = object.rlong

    str_pos_angle = items[12].strip() if len(items) > 12 else None

    if str_pos_angle:
        try:
            object.position_angle = float(str_pos_angle)*np.pi/180.0
        except (ValueError, TypeError):
            object.position_angle = None

    return object

def import_hnsky_supplement(filename, all_dsos):
    """
    Reads data from HNKSKY's supplement file. Returns a list
    of DeepskyObjects()
    """
    supl_file = open(filename, 'r', encoding='ISO-8859-1')
    lines = supl_file.readlines()
    supl_file.close()

    dso_list = []
    for line in lines:
        if line.strip() and not line.startswith(';'):
            dso_list.append(_parse_hnsky_supplement_line(line, all_dsos))

    return dso_list
