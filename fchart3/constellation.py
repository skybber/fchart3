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

import gettext
import os

uilanguage=os.environ.get('fchart3lang')

try:
    lang = gettext.translation( 'messages',localedir='locale', languages=[uilanguage])
    lang.install()
    _ = lang.gettext
except:                  
    _ = gettext.gettext


class BscStar:

    __slots__ = 'number', 'name', 'HD', 'constellation', 'constell_number', 'greek', 'greek_no', 'flamsteed', 'ra', 'dec', 'mag'

    def __init__(self):
        """
        BscStar - has the following fields:
        - number                bsc number
        - name                  name of star
        - HD                    Henry Draper Catalog Number
        - constellation         three letter constellation abbreviation, e.g. AND
        - constellation_number  number in constellation
        - greek                 assigned letter of greek alphabet
        - flamsteed             Flamsteed designation
        - ra                    right ascension in radians (J2000)
        - dec                   declination in radians (J2000)
        - mag                   magnitude
        """
        self.number = None
        self.name = ''
        self.HD = None
        self.constellation = ''
        self.constell_number = None
        self.greek = ''
        self.greek_no = ''
        self.flamsteed = ''
        self.ra = -1.0
        self.dec = 0.0
        self.mag = -100.0


class Constellation:
    def __init__(self):
        """
        Constellation - hold information about constellation
        - name           name of star
        - lines          constellation lines as list of tuples of bsc5 star numbers
        """
        self.name = ''
        self.lines = []
        self.stars = []


class ConstellationCatalog:
    """
    ConstellationCatalog - keeps constellation data

    - all_constell_lines  - np array of constellations lines (pair for each line)
    - bright stars        - list of BscStars
    - bsc_hd_map          - map HD->BscStar
    - constellations      - list od Constellations
    - boundaries_lines    - list of boundaries lines (pair of index to boundaries_points for each line)
    """
    def __init__(self, bsc5_filename='', constell_filename='', boundaries_filename='', cross_id_file=''):
        self.all_constell_lines = []
        hip2hr_cross_id_map, hd2hip_cross_id_map = self._load_cross_id_file(cross_id_file)
        self.bsc_hd_map, self.bsc_hip_map, self.bright_stars = self._import_bsc5(bsc5_filename, hd2hip_cross_id_map)
        self.constellations, self.boundaries_lines, self.boundaries_points = self._import_constellation(constell_filename, boundaries_filename, hip2hr_cross_id_map, self)
        self.all_constell_lines = np.array(self.all_constell_lines)

    def _parse_bsc5_line(self, line):
        star = BscStar()

        star.number = int(line[:4].strip())
        star.name = line[4:14].strip()
        star.constellation = line[11:14].upper()
        star.constell_number = line[4:7].strip().upper()

        star.greek = line[7:10].strip().lower()
        star.greek_no = line[10:11].strip()
        str_HD = line[25:31].strip()
        if str_HD:
            star.HD = int(str_HD)

        if star.constellation and star.constell_number:
            star.flamsteed = star.constell_number + ' ' + star.constellation.lower().capitalize()

        if star.name.startswith('NOVA'):
            star.greek = ''

        if line[75:77].strip() != '':
            star.ra = float(line[75:77])*np.pi/12.0 + float(line[77:79])*np.pi/(12.0*60.0) + float(line[79:83])*np.pi/(12*60.0*60)
            star.dec = float(line[83]+'1')*(float(line[84:86])*np.pi/180.0 + float(line[86:88])*np.pi/(180.0*60) + float(line[88:90])*np.pi/(180.0*60*60))
            star.mag = float(line[102]+'1') * float(line[103:107])

        return star

    def _import_bsc5(self, filename, hd2hip_cross_id_map):
        # Import all saguaro objects that are not NGC or IC objects, or M40
        bsc_star_list = []
        bsc_hd_map = {}
        bsc_hip_map = {}

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            bsc_star = self._parse_bsc5_line(line)
            if bsc_star:
                bsc_star_list.append(bsc_star)
                if not bsc_star.HD is None:
                    bsc_hd_map[bsc_star.HD] = bsc_star
                    if bsc_star.HD in hd2hip_cross_id_map:
                        bsc_hip_map[hd2hip_cross_id_map[bsc_star.HD]] = bsc_star
        return (bsc_hd_map, bsc_hip_map, bsc_star_list,)

    def _parse_constellation_line(self, line, const_catalog, hip2hr_cross_id_map):
        constell = Constellation()
        constell_items = line.split()
        constell.name = constell_items[0].upper()
        stars = constell_items[2:]
        for i in range(2, len(constell_items), 2):
            star_id1 = int(constell_items[i])
            star_id2 = int(constell_items[i+1])
            if not star_id1 in hip2hr_cross_id_map:
                print(_('Skipping constallation={} line. No HR for HIP={}'.format(constell.name, star_id1), flush=True))
                continue
            if not star_id2 in hip2hr_cross_id_map:
                print(_('Skipping constallation={} line. No HR for HIP={}'.format(constell.name, star_id2), flush=True))
                continue
            star1 = self.bright_stars[hip2hr_cross_id_map[star_id1]-1]
            star2 = self.bright_stars[hip2hr_cross_id_map[star_id2]-1]
            constell.lines.append([star1.ra, star1.dec, star2.ra, star2.dec])
            self.all_constell_lines.append([star1.ra, star1.dec, star2.ra, star2.dec])
        return constell

    def _load_cross_id_file(self, cross_id_file):
        hip2hr_cross_id_map = {}
        hd2hip_cross_id_map = {}

        with open(cross_id_file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                ids = line.split('\t')

                hip = int(ids[0].strip())
                str_hd = ids[3].strip()
                str_hr = ids[4].strip()

                if str_hr.isdigit():
                    hip2hr_cross_id_map[hip] = int(str_hr)
                if str_hd.isdigit():
                    hd2hip_cross_id_map[int(str_hd)] = hip
        return hip2hr_cross_id_map, hd2hip_cross_id_map

    def _import_constellation(self, filename, boundaries_filename, hip2hr_cross_id_map, const_catalog):
        # Import all saguaro objects that are not NGC or IC objects, or M40
        constellation_list = []

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            constell = self._parse_constellation_line(line, const_catalog, hip2hr_cross_id_map)
            constellation_list.append(constell)

        bf = open(boundaries_filename, 'r')
        bnd_lines = bf.readlines()
        bf.close()

        index_map = {}
        boundaries_points = []
        boundaries_lines = []
        cur_index = 0

        for line in bnd_lines:
            spl = line.strip().split()
            sra1, sdec1, sra2, sdec2, cons1, cons2 = spl[0], spl[1], spl[2], spl[3], spl[4], spl[5]

            ra1 = float(sra1)*np.pi/12.0
            dec1 = float(sdec1)*np.pi/180.0
            key1 = str(ra1) + '_' + str(dec1)

            index1 = index_map.get(key1)
            if index1 is None:
                index1 = cur_index
                index_map[key1] = index1
                boundaries_points.append([ra1, dec1])
                cur_index += 1

            ra2 = float(sra2)*np.pi/12.0
            dec2 = float(sdec2)*np.pi/180.0
            key2 = str(ra2) + '_' + str(dec2)

            index2 = index_map.get(key2)
            if index2 is None:
                index2 = cur_index
                index_map[key2] = index2
                boundaries_points.append([ra2, dec2])
                cur_index += 1

            boundaries_lines.append([index1, index2, cons1, cons2])

        return (constellation_list, boundaries_lines, np.array(boundaries_points))
