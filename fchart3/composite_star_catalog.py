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

from collections import namedtuple
import os
import sys
import struct
import numpy as np
from time import time

from .htm_binfile_reader import *
from .htm.htm import HTM
from .astrocalc import *

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

class StarObject:
    def __init__(self):
        self.ra = None
        self.dec = None
        self.dRa = None
        self.dDec = None
        self.parallax = None
        self.HD = None
        self.mag = None
        self.bv_index = None
        self.spec_type = None
        self.flags = None
        self.name = None
        self.name2 = None
        self.lname = None

    def init(self, stardata):
        self.ra = stardata['ra']
        self.dec = stardata['dec']
        self.dRa = stardata['dRa']
        self.dDec = stardata['dDec']
        self.parallax = stardata['parallax']
        self.HD = stardata['HD']
        self.mag = stardata['mag']
        self.bv_index = stardata['bv_index']
        self.spec_type = stardata['spec_type']
        self.flags = stardata['flags']

    def set_names(self, name, name2):
        self.name = name
        self.name2 = name2
        if name and name.startswith('HD'):
            self.lname = name
            if name2:
                self.lname = '(' + name2 + ')'
        elif name2:
            lname = name2


class StarCatalogComponent:

    def __init__(self, file_name, trig_mag, static_stars):
        self.file_name = file_name
        self.file_opened = False
        self.star_blocks = None
        self.sky_mesh = None
        self.trig_mag = trig_mag
        self._open_data_file()
        self.static_stars = static_stars
        if self.file_opened and static_stars:
            self._load_static_stars()


    def _open_data_file(self):
        self.data_reader = HtmBinFileReader()
        self.data_reader.open_file(self.file_name)
        if not self.data_reader.file:
            print("Failed to open deep star catalog {}, disabling it.".format(self.file_name))
            return False
        try:
            self.data_reader.read_header()
        except Exception as e:
            print("Header read error for deep star catalog {}, disabling it!".format(self.file_name))
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

        self.htm_level = struct.unpack('b', data_file.read(1))[0]

        self.sky_mesh = _get_htm_mesh(self.htm_level)

        data_file.read(2) # unused
        self.file_opened = True
        self.star_blocks = np.empty(self.sky_mesh.size(), dtype=object)

        return self.file_opened


    def is_deepstar_format(self):
        return self.data_reader.guess_record_size == 16


    def _get_data_format(self):
        if self.data_reader.guess_record_size == 32:
            return STARDATA_DT
        return DEEP_STARDATA_DT


    def _load_static_stars(self):
        record_size = self.data_reader.guess_record_size

        if record_size != 16 and record_size != 32:
            print("Cannot understand catalog file {}".format(self.file_name))
            return False

        data_file = self.data_reader.file
        byteswap = self.data_reader.byteswap

        data_format = self._get_data_format()
        for trixel in range(self.sky_mesh.size()):
            records = self.data_reader.get_record_count(trixel)
            if records > 0:
                trixel_stars = np.fromfile(data_file, data_format, records)
                if byteswap:
                    trixel_stars.byteswap
                self.star_blocks[trixel] = trixel_stars
            else:
                self.star_blocks[trixel] = []

        return True


    def get_sky_mesh(self):
        return self.sky_mesh


    def get_trixel_stars(self, trixel):
        if not self.file_opened:
            return None
        trixel_stars = self.star_blocks[trixel]
        if trixel_stars is None:
            records = self.data_reader.get_record_count(trixel)
            if records > 0:
                data_file = self.data_reader.file
                data_file.seek(self.data_reader.get_offset(trixel))
                trixel_stars = np.fromfile(data_file, self._get_data_format(), records)
                if self.data_reader.byteswap:
                    trixel_stars.byteswap
            else:
                trixel_stars = []
            self.star_blocks[trixel] = trixel_stars

        return trixel_stars


    def free_mem(self):
        if not self.file_opened or self.static_stars:
            return
        for i in range(len(self.star_blocks)):
            self.star_blocks[i] = None

class CompositeStarCatalog:

    def __init__(self, data_dir, usno_nomad=None):
        self.sky_mesh = None
        self.star_index = None
        self.star_blocks = None
        self.stars_loaded = False
        self.faint_magnitude = 0.0
        self.nstars = 0
        self.deepstar_catalogs = []
        self._load_static_data(os.path.join(data_dir, 'namedstars.dat'), os.path.join(data_dir, 'starnames.dat'))
        self._load_deepstar_catalogs(data_dir, usno_nomad)


    def get_sky_mesh(self):
        return self.sky_mesh


    def get_trixel_stars(self, trixel):
        return self.star_blocks[trixel]


    def is_deepstar_format(self):
        return False


    def _load_deepstar_catalogs(self, data_dir, usno_nomad):
        if not self._add_deepstar_catalog_if_exists(data_dir, 'unnamedstars.dat', -5.0, True):
            return 0
        if not self._add_deepstar_catalog_if_exists(data_dir, 'tycho2.dat', 8.0):
            if not self._add_deepstar_catalog_if_exists(data_dir, 'deepstars.dat', 8.0):
                return 1
        if not usno_nomad:
            usno_nomad = 'USNO-NOMAD-1e8.dat'
        if not self._add_deepstar_catalog_if_exists(data_dir, usno_nomad, 11.0):
            return 2
        return 3


    def _add_deepstar_catalog_if_exists(self, data_dir, file_name, trig_mag, static_stars=False):
        full_path = os.path.join(data_dir, file_name)
        if os.path.isfile(full_path):
            dsc = StarCatalogComponent(full_path, trig_mag, static_stars)
            self.deepstar_catalogs.append(dsc)
            return True
        return False


    def _load_static_data(self, namedstars_filename, starnames_filename):

        data_reader = HtmBinFileReader()
        name_reader = HtmBinFileReader()

        data_file = data_reader.open_file(namedstars_filename)
        if data_file is None:
            print("Could not open data file " + namedstars_filename)
            return False

        name_file = name_reader.open_file(starnames_filename)
        if name_file is None:
            print("Could not open data file " + starnames_filename)
            return False

        try:
            data_reader.read_header()
        except Exception as e:
            print("Reading {} failed: {}".format(namedstars_filename, str(e)))
            return False

        try:
            name_reader.read_header()
        except Exception as e:
            print("Reading {} failed: {}".format(starnames_filename, str(e)))
            return False

        byteswap = False
        named = False
        gnamed = False
        self.nstars = 0

        name_file.seek(name_reader.data_offset)
        byteswap = data_reader.byteswap

        data_file.seek(data_reader.data_offset)

        ret = 0

        faintmag = struct.unpack('h', data_file.read(2))[0]

        if byteswap:
            faintmag = swap16(faintmag)

        htm_level = struct.unpack('b', data_file.read(1))[0]
        data_file.read(2) # unused

        if faintmag / 100.0 > self.faint_magnitude:
            self.faint_magnitude = faintmag / 100.0

        self.sky_mesh = _get_htm_mesh(htm_level)
        self.star_index = np.empty(self.sky_mesh.size(), dtype=object)
        self.star_blocks = np.empty(self.sky_mesh.size(), dtype=object)

        starname_size = struct.calcsize(STARNAME_FMT)

        for trixel in range(self.sky_mesh.size()):
            trixel_size = data_reader.get_record_count(trixel)
            if trixel_size == 0:
                continue
            trixel_stars = np.fromfile(data_file, STARDATA_DT, trixel_size)
            if byteswap:
                trixel_stars.byteswap
            self.star_blocks[trixel] = trixel_stars

            for stardata in trixel_stars:
                name = None
                gname = None

                # Named Star - Read the nameFile
                visible_name = ''
                if stardata['flags'] & 0x01:
                    star_name = StarName._make(struct.unpack(STARNAME_FMT, name_file.read(starname_size)))

                    name = star_name.long_name.decode("ascii")
                    gname = star_name.bayer_name.decode("ascii")

                    if gname and gname[0] != '.':
                        visible_name = gname
                else:
                    print("ERROR: Named star file contains unnamed stars! Expect trouble.")

                # Create the new StarObject
                star = StarObject()
                star.init(stardata)

                if stardata['HD']:
                    if not name:
                        name  = "HD {}".format(stardata['HD'])

                star.set_names(name, visible_name)
                self.nstars += 1

                if not self.star_index[trixel]:
                    self.star_index[trixel] = [star]
                else:
                    self.star_index[trixel].append(star)

        data_reader.close_file()
        name_reader.close_file()

        self.stars_loaded = True
        return True


    def _select_stars_from_mash(self, catalog, fieldcentre, radius, lm_stars):
        sky_mesh = catalog.get_sky_mesh()
        intersecting_trixels = sky_mesh.intersect(RAD2DEG * fieldcentre[0], RAD2DEG * fieldcentre[1], RAD2DEG * radius)
        mesh_stars = np.array([], dtype=np.float64).reshape(0, 3)
        mesh_size = sky_mesh.size()
        mask = 1 << (sky_mesh.get_depth() * 2 + 3)

        for trixel in intersecting_trixels:
            trixel_stars = catalog.get_trixel_stars(trixel ^ mask)
            if not trixel_stars is None and len(trixel_stars) > 0:
                ra = trixel_stars['ra'] / (12.0*1000000.0) * np.pi
                dec = trixel_stars['dec'] / (180.0*100000.0) * np.pi
                if catalog.is_deepstar_format():
# TODO:
#                     if trixel_stars['V'] == 30000 and trixel_stars['B'] != 30000:
#                         mag = (trixel_stars['B'] - 1600) / 1000.0
#                     else:
#                         mag = trixel_stars['V'] / 1000.0
                    mag = trixel_stars['V'] / 1000.0
                else:
                    mag = trixel_stars['mag'] / 100.0
                mesh_stars = np.concatenate((mesh_stars, np.column_stack((ra, dec, mag))), axis=0)
        return mesh_stars


    def select_stars(self, fieldcentre, radius, lm_stars):
        """
        return an array containing [[ra, dec, mag], [ra, dec, mag]]
        etc... for all stars in the field centred around fieldcentre
        with radius 'radius'

        fieldcentre is a tuple (ra, dec) in radians. radius is also in
        radians
        """
        fieldsize = angular_distance(fieldcentre, (fieldcentre[0] - radius, fieldcentre[1] - radius))

        selected_stars = self._select_stars_from_mash(self, fieldcentre, radius, lm_stars)

        for cat in self.deepstar_catalogs:
            if cat.trig_mag < lm_stars:
                mesh_stars = self._select_stars_from_mash(cat, fieldcentre, radius, lm_stars)
                if mesh_stars.shape[0] > 0:
                    selected_stars = np.concatenate((selected_stars, mesh_stars), axis=0)

        ra = selected_stars[:,0]
        dec = selected_stars[:,1]

        ra_sep = abs(ra-fieldcentre[0])
        toosmall = ra_sep < np.pi
        norm_ra_sep = toosmall * ra_sep + np.logical_not(toosmall) * (2*np.pi-ra_sep)
        star_in_field = np.logical_and(norm_ra_sep*np.cos(dec) < radius, abs(dec-fieldcentre[1]) < radius)

        position_selection = selected_stars[star_in_field]

        # select on magnitude
        mag = position_selection[:,2]
        bright_enough = mag <= lm_stars

        selection = position_selection[bright_enough]

        return selection

    def free_mem(self):
        for dsc in self.deepstar_catalogs:
            dsc.free_mem()

if __name__ == '__main__':
    data_dir='./data/catalogs/'
    tm = time()
    cat = CompositeStarCatalog(data_dir)
    print("Loaded in : " + str(time()-tm) + "ms")
    print("Done")
