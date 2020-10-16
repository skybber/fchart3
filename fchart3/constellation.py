#    fchart3 draws beautiful deepsky charts in vector formats
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

class BscStar:
    def __init__(self):
        """
        This class has the following fields:
        - name           name of star
        - greek          assigned letter of greek alphabet
        - constellation  three letter constellation abbreviation, e.g. AND
        - ra             right ascension in radians (J2000)
        - dec            declination in radians (J2000)
        - mag            magnitude
        """
        self.number = None
        self.greek = ''
        self.constellation=''
        self.ra=-1.0
        self.dec=0.0
        self.mag=-100.0


class Constellation:
    def __init__(self):
        """
        This class has the following fields:
        - name           name of star
        - lines          constellation lines as list of tuples of bsc5 star numbers
        """
        self.name = ''
        self.lines = []
        self.stars = []
        self.boundaries = []
        self.boundaries1 = [] # Serpens is divided to 2 areas

class ConstellationCatalog:
    def __init__(self, bsc5_filename='', constell_filename='', boundaries_filename='', cross_id_file=''):
        self.bright_stars = import_bsc5(bsc5_filename)
        self.constellations = import_constellation(constell_filename, boundaries_filename, cross_id_file, self)

def _parse_bsc5_line(line):
    star = BscStar()

    star.number = int(line[:4].strip())
    star.name = line[4:14].strip()
    star.constellation = line[11:14].upper()
    star.constell_number = line[4:7].strip().upper()

    star.greek = line[7:10].strip().lower()
    if star.name.startswith('NOVA'):
        star.greek = ''
    if line[75:77].strip() != '':
        star.ra = float(line[75:77])*np.pi/12.0 + float(line[77:79])*np.pi/(12.0*60.0) + float(line[79:83])*np.pi/(12*60.0*60)
        star.dec = float(line[83]+'1')*(float(line[84:86])*np.pi/180.0 + float(line[86:88])*np.pi/(180.0*60) + float(line[88:90])*np.pi/(180.0*60*60))
        star.mag = float(line[102]+'1') * float(line[103:107])
    return star


def import_bsc5(filename):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    bsc_star_list = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        bsc_star = _parse_bsc5_line(line)
        if bsc_star:
            bsc_star_list.append(bsc_star)
    return bsc_star_list


def _parse_constellation_line(line, const_catalog, cross_id_map):
    constell = Constellation()
    constell_items = line.split()
    constell.name = constell_items[0].upper()
    stars = constell_items[2:]
    for i in range(2, len(constell_items), 2):
        star_id1 = int(constell_items[i]) 
        star_id2 = int(constell_items[i+1]) 
        if not star_id1 in cross_id_map:
            print('Skipping constallation={} line. No HR for HIP={}'.format(constell.name, star_id1), flush=True)
            continue
        if not star_id2 in cross_id_map:
            print('Skipping constallation={} line. No HR for HIP={}'.format(constell.name, star_id2), flush=True)
            continue
        constell.lines.append((cross_id_map[star_id1], cross_id_map[star_id2]))
    return constell


def import_constellation(filename, boundaries_filename, cross_id_file, const_catalog):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    constellation_list = []

    cross_id_map = {}
    
    with open(cross_id_file, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            ids = line.split()
            cross_id_map[int(ids[0])] = int(ids[-1])
                
    with open(filename, 'r') as f:
        lines = f.readlines()

    cons_map = {}

    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        constell = _parse_constellation_line(line, const_catalog, cross_id_map)
        constellation_list.append(constell)
        cons_map[constell.name.upper()] = constell

    bf = open(boundaries_filename, 'r')
    bnd_lines = bf.readlines()
    bf.close()

    for line in bnd_lines:
        spl = line.strip().split()
        if len(spl) == 3:
            sra, sdec, cons1, cons2 = spl[0], spl[1], spl[2], None
        else:
            sra, sdec, cons1, cons2 = spl[0], spl[1], spl[2], spl[3]
            cons2 = cons2.upper()
        ra = float(sra)*np.pi/12.0
        dec = float(sdec)*np.pi/180.0
        cons = cons1.upper()

        if cons.startswith('SER'):
            if cons.endswith('1'):
                cons_map[cons[:-1]].boundaries.append((ra, dec, cons2))
            else:
                cons_map[cons[:-1]].boundaries1.append((ra, dec, cons2))
        else:
            cons_map[cons].boundaries.append((ra, dec, cons2))

    return constellation_list

