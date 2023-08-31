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

FIXING_NAMES = { 'NGC2174': 'NGC2175', 'NGC1893' : 'IC410' }


def import_outlines_catgen(filename):
    outlines_file = open(filename, 'r', encoding='ISO-8859-1')
    lines = outlines_file.readlines()
    outlines_file.close()

    outlines = ({},{},{})

    next_dso = True
    dso_name = None

    for line in lines:
        items = line.split()
        if next_dso:
            dso_name = items[4].split('_')[0]
            if dso_name in FIXING_NAMES:
                dso_name = FIXING_NAMES[dso_name]
            points = []
            idx = int(items[3]) - 1
            if not dso_name in outlines[idx]:
                outlines[idx][dso_name] = []
            outlines[idx][dso_name].append(points)
            next_dso = False
        elif int(items[2]) == 1:
            next_dso = True
        ra = np.pi * float(items[0]) / 180.0
        dec = np.pi * float(items[1]) / 180.0
        points.append((ra, dec))
    return outlines