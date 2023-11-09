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
import gettext
import os

uilanguage=os.environ.get('fchart3lang')
try:
    lang = gettext.translation( 'messages',localedir='locale', languages=[uilanguage])
    lang.install()
    _ = lang.gettext
except:                  
    _ = gettext.gettext


from .deepsky_object import *
from numpy import *
import csv


def _vic2int(s):
    s.lstrip('0')
    if len(s) == 0:
        return 0
    return int(s)


def import_vic(filename):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    deeplist = []

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        row_id = 0
        for row in reader:
            row_id += 1
            object = DeepskyObject()
            object.cat = 'VIC'
            object.name = str(row_id)
            object.all_names = [object.name]
            object.type = STARS
            rhs,rms,rss = row['RA'].split(',')
            object.ra = pi * (float(rhs) + float(rms)/60.0) / 12.0
            dds, dms, dss = row['Dec'].split(',')
            object.dec = pi*(float(dds) + float(dms)/60.0) / 180.0
            object.mag = _vic2int(row['mag']) / 10
            deeplist.append(object)
    return deeplist


if __name__ == '__main__':
    fname = '../data/catalogs/vic.txt'
    nb=len(import_vic(fname))
    #print(str(len(import_vic(fname)))+' objects in VIC catalogue')
    print( _(f'{nb} objects in VIC catalogue') )
