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

from fchart3.deepsky_object import *
import numpy as np
import sys
import string
import copy

def parse_catalog_name(cnstr, ignore_err):
    if cnstr.startswith('Sh2-'):
        cnsplit = cnstr.split('-')
    else:
        cnsplit = cnstr.split()

    if len(cnsplit) == 1:
        cat = cnsplit[0][0]
        name = cnsplit[0][1:]
    elif len(cnsplit) == 2:
        cat,name = cnsplit
    elif len(cnsplit) == 3:
        cat = ''
        name = cnsplit[0][0]+cnsplit[1][0]+cnsplit[2][0]
        if name not in ['LMC', 'SMC']:
            cat = cnsplit[0]
            name = cnsplit[1]+cnsplit[2]
    else:
        if not ignore_err:
            print('ERROR: '+str(cnsplit))
            sys.exit(1)
        cat, name = None, None
    return (cat, name)

def parse_saguaro_line(line):
    object = DeepskyObject()
    strs = line.replace('","', '~').split('~')
    strs[0] = strs[0].split('"')[1]
    strs[-1] = strs[-1].split('"')[0]

    cat, name = parse_catalog_name(strs[0].strip(), False)
    altern = strs[1].strip()
    if altern:
        cat1, name1 = parse_catalog_name(altern, True)
    else:
        cat1, name1 = None, None

    typestr = strs[2].strip()
    typenum = UNKNOWN

    if typestr in ['GALXY']:
        typenum = G
    elif typestr in ['BRTNB','DRKNB', 'GX+DN', 'LMCDN', 'SMCDN']:
        typenum = N
    elif typestr in ['PLNNB']:
        typenum = PN
    elif typestr in ['CL+NB', 'LMCOC', 'LMCCN', 'OPNCL',
                     'SMCOC', 'SMCCN', 'G+C+N']:
        typenum = OC
    elif typestr in ['GLOCL', 'GX+GC', 'LMCGC', 'SMCGC']:
        typenum = GC
    elif typestr in ['ASTER', '#STAR']:
        typenum = STARS
    elif typestr in ['SNREM']:
        typenum = SNR
    elif typestr in ['QUASR']:
        typenum = QSO
    elif typestr in ['GALCL']:
        typenum = GALCL
    else:
        typenum = NOTFOUND

    object.cat = cat.strip()
    if object.cat == 'Sh2-':
        object.cat ='Sh2'
        print("##### Adding:" + name.strip().upper())

    object.name = name.strip().upper()
    object.all_names = [object.name]
    object.type = typenum
    object.constellation = strs[3]
    rhs,rms = strs[4].split()
    object.ra = float(rhs)*np.pi/12 + float(rms)*np.pi/(12*60.0)
    sign = float(strs[5][0]+'1')
    dds, dms = strs[5][1:].split()
    object.dec =sign*(float(dds)*np.pi/180.0 + float(dms)*np.pi/(180*60))
    object.mag = float(strs[6][:-1])

    rlongstr  = strs[10].strip()
    rlong = -1
    if rlongstr != '':
        if not rlongstr[0].isalnum():
            rlongstr = rlongstr[1:]
        unit = rlongstr[-1]
        try:
            rlong = float(rlongstr[:-1])*np.pi/180.0
        except ValueError:
            txt = ''
            for ch in rlongstr[:-1]:
                if ch.isalnum() or ch.isspace():
                    txt += ch
                else:
                    break
            rlong = float(txt)*np.pi/180.0
        if unit.lower() == 'm':
            rlong /= 60.0
        if unit.lower() == 's':
            rlong /= 3600.0

    rshortstr = strs[11].strip()
    rshort = -1
    if rshortstr != '':
        if not rshortstr[0].isalnum():
            rshortstr = rlongstr[1:]
        unit = rshortstr[-1]
        rshort = float(rshortstr[:-1])*np.pi/180.0
        if unit.lower() == 'm':
            rshort /= 60.0
        if unit.lower() == 's':
            rshort /= 3600.0
    pastr     = strs[12].strip()
    pa = 90*np.pi/180.0
    if pastr != '':
        pa = float(pastr)*np.pi/180.0
    object.rlong  = rlong
    object.rshort = rshort
    object.pa     = pa
    object1 = None
    if cat1 and cat1 in ['Abell', 'UGC']:
        object1 = copy.deepcopy(object)
        object1.cat = cat1.strip()
        object1.name = name1.strip().upper()
        object1.all_names = [object1.name]
        if cat1 == 'Abell':
            object, object1 = object1, object
        object1.master_object = object

    return (object, object1)


def import_saguaro(filename):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    deeplist = []

    sf = open(filename, 'r')
    lines = sf.readlines()
    sf.close()

    for line in lines[1:]:
        object, object1 = parse_saguaro_line(line)
        if object.cat != 'NGC' and object.cat != 'IC' and not(object.cat == 'Winnecke' and object.name == '4'):
            deeplist.append(object)
        if object1:
            deeplist.append(object1)
    return deeplist


if __name__ == '__main__':
    fname = '../data/catalogs/sac.txt'
    print(str(len(import_saguaro(fname)))+' objects in SAC list')
