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

import numpy as np


def import_milky_way(filename):
    milkyway_file = open(filename, 'r')
    lines = milkyway_file.readlines()
    milkyway_file.close()

    mw_lines = None

    for line in lines:
        items = line.split()
        ra = np.pi * float(items[1]) / 12.0
        dec = np.pi * float(items[2]) / 180

        if items[0] == 'M':
            if mw_lines is None:
                mw_lines = np.array([[ra, dec, 0]])
            else:
                mw_lines = np.append(mw_lines, [[ra, dec, 0]], axis=0)
        elif items[0] == 'S':
            mw_lines = np.append(mw_lines, [[ra, dec, 1]], axis=0)
        else:
            mw_lines = np.append(mw_lines, [[ra, dec, 2]], axis=0)

    return mw_lines
