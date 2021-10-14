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

from collections import namedtuple
import os
import sys
import struct
import numpy as np
from time import time

from .htm_binfile_reader import *
from .htm.htm import HTM
from .astrocalc import *
from .star_catalog import *

SPEC_TYPE_2_RGB = {
    'O5': (155/255, 176/255, 255/255),
    'O6': (162/255, 184/255, 255/255),
    'O7': (157/255, 177/255, 255/255),
    'O8': (157/255, 177/255, 255/255),
    'O9': (154/255, 178/255, 255/255),
    'O9.5': (164/255, 186/255, 255/255),
    'B0': (156/255, 178/255, 255/255),
    'B0.5': (167/255, 188/255, 255/255),
    'B1': (160/255, 182/255, 255/255),
    'B2': (160/255, 180/255, 255/255),
    'B3': (165/255, 185/255, 255/255),
    'B4': (164/255, 184/255, 255/255),
    'B5': (170/255, 191/255, 255/255),
    'B6': (172/255, 189/255, 255/255),
    'B7': (173/255, 191/255, 255/255),
    'B8': (177/255, 195/255, 255/255),
    'B9': (181/255, 198/255, 255/255),
    'A0': (185/255, 201/255, 255/255),
    'A1': (181/255, 199/255, 255/255),
    'A2': (187/255, 203/255, 255/255),
    'A3': (191/255, 207/255, 255/255),
    'A4': (191/255, 207/255, 255/255),
    'A5': (202/255, 215/255, 255/255),
    'A6': (199/255, 212/255, 255/255),
    'A7': (200/255, 213/255, 255/255),
    'A8': (213/255, 222/255, 255/255),
    'A9': (219/255, 224/255, 255/255),
    'F0': (224/255, 229/255, 255/255),
    'F1': (224/255, 229/255, 255/255),
    'F2': (236/255, 239/255, 255/255),
    'F3': (236/255, 239/255, 255/255),
    'F4': (224/255, 226/255, 255/255),
    'F5': (248/255, 247/255, 255/255),
    'F6': (244/255, 241/255, 255/255),
    'F7': (246/255, 243/255, 255/255),
    'F8': (255/255, 247/255, 252/255),
    'F9': (255/255, 247/255, 252/255),
    'G0': (255/255, 248/255, 252/255),
    'G1': (255/255, 247/255, 248/255),
    'G2': (255/255, 245/255, 242/255),
    'G3': (255/255, 245/255, 242/255),
    'G4': (255/255, 241/255, 229/255),
    'G5': (255/255, 244/255, 234/255),
    'G6': (255/255, 244/255, 235/255),
    'G7': (255/255, 244/255, 235/255),
    'G8': (255/255, 237/255, 222/255),
    'G9': (255/255, 239/255, 221/255),
    'K0': (255/255, 238/255, 221/255),
    'K1': (255/255, 224/255, 188/255),
    'K2': (255/255, 227/255, 196/255),
    'K3': (255/255, 222/255, 195/255),
    'K4': (255/255, 216/255, 181/255),
    'K5': (255/255, 210/255, 161/255),
    'K6': (255/255, 210/255, 161/255),
    'K7': (255/255, 199/255, 142/255),
    'K8': (255/255, 209/255, 174/255),
    'K9': (255/255, 209/255, 174/255),
    'M0': (255/255, 195/255, 139/255),
    'M1': (255/255, 204/255, 142/255),
    'M2': (255/255, 196/255, 131/255),
    'M3': (255/255, 206/255, 129/255),
    'M4': (255/255, 201/255, 127/255),
    'M5': (255/255, 204/255, 111/255),
    'M6': (255/255, 195/255, 112/255),
    'M7': (255/255, 195/255, 112/255),
    'M8': (255/255, 198/255, 109/255),
    'M9': (255/255, 198/255, 109/255),
    'C0': (255/255, 244/255, 235/255),
    'C1': (255/255, 237/255, 222/255),
    'C2': (255/255, 238/255, 221/255),
    'C3': (255/255, 227/255, 196/255),
    'C4': (255/255, 216/255, 181/255),
    'C5': (255/255, 195/255, 139/255),
    'C6': (255/255, 196/255, 131/255),
    'C7': (255/255, 201/255, 127/255),
    'N9': (255/255, 120/255, 60/255),
}

StarData = namedtuple('StarData' , 'ra dec dRa dDec parallax HD mag bv_index spec_type flags')

STARDATA_DT = np.dtype([('ra', np.int32),
                          ('dec', np.int32),
                          ('dRa', np.int32),
                          ('dDec', np.int32),
                          ('parallax', np.int32),
                          ('HD', np.int32),
                          ('mag', np.int16),
                          ('bv_index', np.int16),
                          ('spec_type', np.int8, (2,)),
                          ('flags', np.int8),
                          ('padding', np.int8),
                        ])

DEEP_STARDATA_DT = np.dtype([('ra', np.int32),
                          ('dec', np.int32),
                          ('dRa', np.int16),
                          ('dDec', np.int16),
                          ('B', np.int16),
                          ('V', np.int16),
                        ])

TRIXEL_STARDATA_DT = np.dtype([('ra', np.float64),
                            ('dec', np.float64),
                            ('mag', np.float64),
                            ('spec_type', np.int8, (2,)),
                            ('bsc', np.dtype(object))
                          ])


StarName = namedtuple('StarName', 'bayer_name long_name')
STARNAME_FMT = '8s32s'
RAD2DEG = 180.0/np.pi

htm_meshes = {}


def _get_htm_mesh(level):
    mesh = htm_meshes.get(level)
    if not mesh:
        mesh = HTM(level)
        htm_meshes[level] = mesh
    return mesh


def _convert_trixels_stars_helper(trixel_stars, bsc_hd_map):
    dim = len(trixel_stars)
    trixel_star_data = np.core.records.fromarrays( \
        [ \
            trixel_stars['ra'] / (12.0*1000000.0) * np.pi,
            trixel_stars['dec'] / (180.0*100000.0) * np.pi,
            trixel_stars['mag']/100.0,
            trixel_stars['spec_type'],
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=TRIXEL_STARDATA_DT)

    if bsc_hd_map:
        for i in range(dim):
            hd = trixel_stars[i]['HD']
            if hd != 0:
                bsc_star = bsc_hd_map.get(hd)
                if bsc_star:
                    trixel_star_data[i]['bsc'] = bsc_star

    return trixel_star_data



def _convert_trixels_deep_stars_helper(trixel_stars):
    use_b = np.logical_and(trixel_stars['V'] == 30000, trixel_stars['B'] != 30000)
    mag = use_b * (trixel_stars['B'] - 1600) / 1000.0 + np.logical_not(use_b) * trixel_stars['V'] / 1000.0

    bv_index = (trixel_stars['B'] - trixel_stars['V']) / 1000.0;

    spec_type_base = np.where(np.logical_and(trixel_stars['V'] != 30000, trixel_stars['B'] != 30000),
                   np.where(bv_index <= 0.325, ord('A'),
                   np.where(bv_index <= 0.575, ord('F'),
                   np.where(bv_index <= 0.975, ord('G'),
                   np.where(bv_index <= 1.6, ord('K'), ord('M'))))), ord('?'))

    dim = len(spec_type_base)
    spec_type = np.zeros((dim,2))
    spec_type[:,:-1] = spec_type_base.reshape(dim, 1)

    return np.core.records.fromarrays( \
        [ \
            trixel_stars['ra'] / (12.0*1000000.0) * np.pi,
            trixel_stars['dec'] / (180.0*100000.0) * np.pi,
            mag,
            spec_type,
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=TRIXEL_STARDATA_DT)


class HtmStarCatalogComponent:

    def __init__(self, file_name, trig_mag, static_stars, bsc_hd_map):
        self._file_name = file_name
        self._file_opened = False
        self._star_blocks = None
        self._sky_mesh = None
        self._trig_mag = trig_mag
        self._open_data_file()
        self._static_stars = static_stars
        if self._file_opened and static_stars:
            self._load_static_stars(bsc_hd_map)

    def _open_data_file(self):
        self.data_reader = HtmBinFileReader()
        self.data_reader.open_file(self._file_name)
        if not self.data_reader.file:
            print("Failed to open deep star catalog {}, disabling it.".format(self._file_name))
            return False
        try:
            self.data_reader.read_header()
        except Exception as e:
            print("Header read error for deep star catalog {}, disabling it!".format(self._file_name))
            return False

        data_file = self.data_reader.file
        byteswap = self.data_reader.byteswap
        faintmag = struct.unpack('h', data_file.read(2))[0]

        if byteswap:
            faintmag = swap16(faintmag)

        if self.data_reader.guess_record_size == 16:
            self.faint_magnitude = faintmag / 1000.0
        else:
            self.faint_magnitude = faintmag / 100.0

        htm_level = struct.unpack('b', data_file.read(1))[0]
        self._sky_mesh = _get_htm_mesh(htm_level)

        data_file.read(2) # unused
        self._star_blocks = [None] * self._sky_mesh.size()

        self._file_opened = True
        return self._file_opened

    def is_deepstar_format(self):
        return self.data_reader.guess_record_size == 16

    def _get_data_format(self):
        if self.data_reader.guess_record_size == 32:
            return STARDATA_DT
        return DEEP_STARDATA_DT

    def _convert_trixels_stars(self, trixel_stars, bsc_hd_map):
        if self.data_reader.guess_record_size == 32:
            return _convert_trixels_stars_helper(trixel_stars, bsc_hd_map)
        return _convert_trixels_deep_stars_helper(trixel_stars)

    def _load_static_stars(self, bsc_hd_map):
        for trixel in range(self._sky_mesh.size()):
            self.get_trixel_stars(trixel, bsc_hd_map)
        return True

    def get_sky_mesh(self):
        return self._sky_mesh

    def get_trixel_stars(self, trixel, bsc_hd_map=None):
        if not self._file_opened:
            return None
        trixel_stars = self._star_blocks[trixel]
        if trixel_stars is None:
            records = self.data_reader.get_record_count(trixel)
            if records > 0:
                data_file = self.data_reader.file
                data_file.seek(self.data_reader.get_offset(trixel))
                trixel_stars = np.fromfile(data_file, self._get_data_format(), records)
                if self.data_reader.byteswap:
                    trixel_stars.byteswap
                trixel_stars = self._convert_trixels_stars(trixel_stars, bsc_hd_map)
            else:
                trixel_stars = []
            self._star_blocks[trixel] = trixel_stars

        return trixel_stars

    def get_trig_mag(self):
        return self._trig_mag

    def free_mem(self):
        if not self._file_opened or self._static_stars:
            return
        for i in range(len(self._star_blocks)):
            self._star_blocks[i] = None


class HtmStarCatalog(StarCatalog):
    '''
    Star catalog composed of HtmStarCatalogComponent. Each component represents one level of HTM tree
    '''
    def __init__(self, data_dir, bsc_hd_map, usno_nomad=None):
        self._deepstar_catalogs = []
        self._load_deepstar_catalogs(data_dir, bsc_hd_map, usno_nomad)

    def _load_deepstar_catalogs(self, data_dir, bsc_hd_map, usno_nomad):
        if not self._add_deepstar_catalog_if_exists(data_dir, 'namedstars.dat', -5.0, bsc_hd_map, static_stars=True):
            return 0
        if not self._add_deepstar_catalog_if_exists(data_dir, 'unnamedstars.dat', -5.0, bsc_hd_map, static_stars=True):
            return 1
        if not self._add_deepstar_catalog_if_exists(data_dir, 'deepstars.dat', 8.0, None):
            return 2
        if not usno_nomad:
            usno_nomad = 'USNO-NOMAD-1e8.dat'
        if not self._add_deepstar_catalog_if_exists(data_dir, usno_nomad, 11.0, None):
            return 3
        return 4

    def _add_deepstar_catalog_if_exists(self, data_dir, file_name, trig_mag, bsc_hd_map, static_stars=False):
        full_path = os.path.join(data_dir, file_name)
        if os.path.isfile(full_path):
            dsc = HtmStarCatalogComponent(full_path, trig_mag, static_stars, bsc_hd_map)
            self._deepstar_catalogs.append(dsc)
            return True
        return False

    def _select_stars_from_mesh(self, catalog, fieldcentre, radius, lm_stars):
        sky_mesh = catalog.get_sky_mesh()
        intersecting_trixels = sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        stars = []
        mask = 1 << (sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_stars = catalog.get_trixel_stars(trixel ^ mask)
            if not trixel_stars is None and len(trixel_stars) > 0:
                mag = trixel_stars['mag']
                trixel_stars = trixel_stars[mag <= lm_stars]
                stars.append(trixel_stars)
        return stars

    def select_stars(self, fieldcentre, radius, lm_stars, rect_coords=False):
        """
        Return an array containing of items [[ra, dec, mag], [ra, dec, mag]...]
        for all stars in the field centered around fieldcentre with iven radius,
        fieldcentre and radius.
        """
        tmp_arr = []

        for cat in self._deepstar_catalogs:
            if cat.get_trig_mag() < lm_stars:
                stars = self._select_stars_from_mesh(cat, fieldcentre, radius, lm_stars)
                if len(stars) > 0:
                    tmp_arr += stars

        selected_stars = np.concatenate(tmp_arr, axis=0)

        return selected_stars

    def get_star_color(self, star):
        spec_type = star['spec_type']
        subtype = spec_type[1]//10
        if subtype > 9:
            subtype = 9
        return SPEC_TYPE_2_RGB.get(chr(spec_type[0]) + str(subtype), (1.0, 1.0, 1.0))

    def free_mem(self):
        for dsc in self._deepstar_catalogs:
            dsc.free_mem()


if __name__ == '__main__':
    data_dir='./data/catalogs/'
    tm = time()
    cat = HtmStarCatalog(data_dir)
    print("Loaded in : " + str(time()-tm) + "ms")
    print("Done")
