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

import os
import sys
import struct
import glob
import math
import numpy as np
from time import time

from fchart3.htm.htm import HTM
from fchart3.astrocalc import *
from fchart3.vector_math import *
from fchart3.star_catalog import *
from fchart3.geodesic_binfile_reader import *
from fchart3.geodesic_grid import *
from fchart3.htm_grid import *

NORTH = (0.0, 0.0, 1.0)

htm_meshes = {}
htm_grid = None
trixel_levels = None

"""
STAR1_DT:
              _______________
    0    hip |               |
    1        |               |
    2        |_______________|
    3   cIds |_______________|
    4     x0 |               |
    5        |               |
    6        |               |
    7        |_______________|
    8     x1 |               |
    9        |               |
    10       |               |
    11       |_______________|
    12    bV |_______________|
    13   mag |_______________|
    14 spInt |               |
    15       |_______________|
    16   dx0 |               |
    17       |               |
    18       |               |
    19       |_______________|
    20   dx1 |               |
    21       |               |
    22       |               |
    23       |_______________|
    24   plx |               |
    25       |               |
    26       |               |
    27       |_______________|

    componentIds         8
    hip                  24

    int32 x0            32
    int32 x1            32

    uint8 bV            8
    uint8 mag           8
    uint16 spInt        16

    int32 dx0,dx1,plx   32
"""

STAR1_DT = np.dtype([('hip', np.uint8, (3,)),
                     ('cIds', np.uint8),
                     ('x0', np.int32),
                     ('x1', np.int32),
                     ('bv', np.uint8),
                     ('mag', np.uint8),
                     ('spInt', np.uint16),
                     ('dx0', np.int32),
                     ('dx1', np.int32),
                     ('plx', np.int32),
                    ])

"""
STAR2_DT
              _______________
    0     x0 |               |
    1        |_______        |
    2     x1 |       |_______|
    3        |               |
    4        |_______________|
    5    dx0 |___            |
    6    dx1 |   |___________|
    7        |_______        |
    8     bV |_______|_______|
    9    mag |_________|_____| bV

    int x0          :20
    int x1          :20
    int dx0         :14
    int dx1         :14
    unsigned int bV :7
    unsigned int mag:5
"""
STAR2_DT = np.dtype([('x01', np.uint8, (5,)),
                     ('dx01', np.uint8, (3,)),
                     ('bvdx1', np.uint8),
                     ('magbv', np.uint8),
                    ])


"""
STAR3_DT
              _______________
    0     x0 |               |
    1        |___________    |
    2     x1 |           |___|
    3        |_______        |
    4     bV |_______|_______|
    5    mag |_________|_____| bV

    int x0               :18
    int x1               :18
    unsigned int bV      :7
    unsigned int mag     :5
"""
STAR3_DT = np.dtype([('x01', np.uint8, (4,)),
                     ('bvx1', np.uint8),
                     ('magbv', np.uint8),
                    ])


HTM_STARDATA_DT = np.dtype([('hip', np.uint8, (3,)),
                            ('cIds', np.uint8),
                            ('ra', np.int32),
                            ('dec', np.int32),
                            ('dRa', np.int32),
                            ('dDec', np.int32),
                            ('bv', np.uint8),
                            ('mag', np.int16),
                            ('spInt', np.uint16),
                            ('plx', np.int32),
                        ])


HTM_DEEP_STARDATA_DT = np.dtype([('ra', np.int32),
                          ('dec', np.int32),
                          ('dRa', np.int16),
                          ('dDec', np.int16),
                          ('B', np.int16),
                          ('V', np.int16),
                        ])


ZONE_STARDATA_DT = np.dtype([('ra', np.float64),
                             ('dec', np.float64),
                             ('mag', np.float64),
                             ('bvind', np.uint8),
                             ('bsc', np.dtype(object))
                           ])


EQUILATERAL_TRIANGLE_CENTER_SIDE_DIST = math.sqrt(3)/6
TRIANGLE_CENTER_FACTOR = math.sqrt(0.5**2 + EQUILATERAL_TRIANGLE_CENTER_SIDE_DIST**2)


use_precalc_star_position_scale = False
use_precalc_triangle_size = False

def set_use_precalc_star_position_scale(val):
    global use_precalc_star_position_scale
    use_precalc_star_position_scale = val


def set_use_precalc_triangle_size(val):
    global use_precalc_triangle_size
    use_precalc_triangle_size = val


STAR3_DT = np.dtype([('x01', np.uint8, (4,)),
                     ('bvx1', np.uint8),
                     ('magbv', np.uint8),
                    ])

NORTH = (0.0, 0.0, 1.0)


class ZoneData:
    def __init__(self):
        self.center = None
        self.axis0 = None
        self.axis1 = None


    def get_J2000_pos(self, star_X0, star_X1):
        return (self.axis0 * star_X0) + (star_X1 * self.axis1) + self.center


class GeodesicStarCatalogComponent:

    def __init__(self, file_name):
        self._data_reader = None
        self._file_name = file_name
        self._file_opened = False
        self._nr_of_zones = 0
        self._star_blocks = None
        self._zone_data_ar = None
        self._star_position_scale = 0.0
        self._triangle_size = 0.0


    @property
    def file_name(self):
        return self._file_name


    @property
    def mag_min_mag(self):
        return self._data_reader.mag_min_mag


    @property
    def level(self):
        return self._data_reader.level


    @property
    def nr_of_stars(self):
        return self._data_reader.nr_of_stars


    @property
    def star_position_scale(self):
        return self._star_position_scale


    @property
    def triangle_size(self):
        return self._triangle_size


    @property
    def nr_of_zones(self):
        return self._nr_of_zones

    @property
    def star_position_scale(self):
        return self._star_position_scale

    def get_mag_table(self):
        return self._data_reader.get_mag_table()


    def load_data_file(self):
        self._data_reader = GeodesicBinFileReader()
        self._data_reader.open_file(self._file_name)
        if not self._data_reader.file:
            print("Failed to open star catalog {}, disabling it.".format(self._file_name))
            return False
        try:
            self._data_reader.read_header()
        except Exception as e:
            print("Header read error for deep star catalog {}, disabling it!".format(self._file_name))
            return False

        self._nr_of_zones = GeodesicGrid.nr_of_zones(self._data_reader.level)
        self._star_blocks = [None] * self._nr_of_zones
        self._zone_data_ar = [ZoneData() for _ in range(self._nr_of_zones)]
        self._file_opened = True
        return self._file_opened


    def init_tringle(self, index, c0, c1, c2):
        global use_precalc_star_position_scale
        z = self._zone_data_ar[index]
        z.center = vector_norm_add3(c0, c1, c2)
        z.axis0 = vector_norm_cross(NORTH, z.center)
        z.axis1 = vector_cross(z.center, z.axis0)

        if not use_precalc_triangle_size:
            d1 = vector_length(vector_sub(c0, c1))
            d2 = vector_length(vector_sub(c1, c2))
            d3 = vector_length(vector_sub(c2, c0))
            dmax = max(d1, d2, d3)
            if dmax > self._triangle_size:
                self._triangle_size = dmax

        if not use_precalc_star_position_scale:
            # Initialize star_position_scale. This scale is used to multiply stars position
            # encoded as integers so that it optimize precision over the triangle.
            # It has to be computed for each triangle because the relative orientation of the 2 axis is different for each triangle.
            mu0 = vector_dot(vector_sub(c0,z.center), z.axis0)
            mu1 = vector_dot(vector_sub(c0,z.center), z.axis1)
            f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
            h = abs(mu0)*f
            if self._star_position_scale < h:
                self._star_position_scale = h
            h = abs(mu1)*f
            if self._star_position_scale < h:
                self._star_position_scale = h

            mu0 = vector_dot(vector_sub(c1,z.center), z.axis0)
            mu1 = vector_dot(vector_sub(c1,z.center), z.axis1)
            f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
            h = abs(mu0)*f
            if self._star_position_scale < h:
                self._star_position_scale = h
            h = abs(mu1)*f
            if self._star_position_scale < h:
                self._star_position_scale = h

            mu0 = vector_dot(vector_sub(c2,z.center), z.axis0)
            mu1 = vector_dot(vector_sub(c2,z.center), z.axis1)
            f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
            h = abs(mu0)*f
            if self._star_position_scale < h:
                self._star_position_scale = h
            h = abs(mu1)*f
            if self._star_position_scale < h:
                self._star_position_scale = h


    def scale_axis(self):
        if self._data_reader.file_type == 0:
            star_max_pos_val = 0x7FFFFFFF
        elif self._data_reader.file_type == 1:
            star_max_pos_val = (1<<19)-1
        else:
            star_max_pos_val = (1<<17)-1

        self._star_position_scale /= star_max_pos_val

        for z in self._zone_data_ar:
            z.axis0 = np.array(vector_scal_dot(self._star_position_scale, z.axis0))
            z.axis1 = np.array(vector_scal_dot(self._star_position_scale, z.axis1))


    def _get_data_format(self):
        if self._data_reader.file_type == 0:
            return STAR1_DT
        if self._data_reader.file_type == 1:
            return STAR2_DT
        return STAR3_DT


    def _convert_zone_stars(self, zone_stars, zone_data, bsc_hip_map):
        mag_table = self._data_reader.get_mag_table()
        if self._data_reader.file_type == 0:
            return _convert_stars1_helper(zone_stars, zone_data, mag_table, bsc_hip_map)
        elif self._data_reader.file_type == 1:
            return _convert_stars2_helper(zone_stars, zone_data, mag_table)
        else:
            return _convert_stars3_helper(zone_stars, zone_data, mag_table)


    def get_raw_zone_stars(self, zone, bsc_hip_map=None):
        """ Used for conversion from geodesic2htm
        """
        if not self._file_opened:
            return None
        records = self._data_reader.get_record_count(zone)
        if records > 0:
            data_file = self._data_reader.file
            data_file.seek(self._data_reader.get_offset(zone))
            zone_stars = np.fromfile(data_file, self._get_data_format(), records)
        else:
            zone_stars = []

        return zone_stars


    def get_zone_data(self, zone):
        return self._zone_data_ar[zone]

    @property
    def file_type(self):
        return self._data_reader.file_type


class GeodesicStarCatalog(StarCatalog):
    """
    Star catalog composed of GeodesicStarCatalogComponent. Each component represents
    one level of Geodesic tree.
    """
    def __init__(self, data_dir, bsc_hip_map):
        self._cat_components = []
        for i in range(9):
            cat_comp = self._load_gsc_component(data_dir, 'stars_{}_*.cat'.format(i))
            if not cat_comp:
                break
            if cat_comp.level != i:
                print("File {} has invalid catalog level.".format(self._file_name))
                break
            print('{} stars readed from {}'.format(cat_comp.nr_of_stars, os.path.split(cat_comp.file_name)[1]))
            self._cat_components.append(cat_comp)

        if i == 8:
            self._max_geodesic_grid_level = 8
        else:
            self._max_geodesic_grid_level = i-1 if i > 0 else 0

        self._geodesic_grid = GeodesicGrid(self._max_geodesic_grid_level)
        self._geodesic_grid.visit_triangles(self._max_geodesic_grid_level, self.init_tringle)

        for cat_comp in self._cat_components:
            print('Level={} scale={} triangle_size={}'.format(cat_comp.level, cat_comp.star_position_scale, cat_comp.triangle_size))
            cat_comp.scale_axis()

        self.search_result = GeodesicSearchResult(self._max_geodesic_grid_level)


    def _load_gsc_component(self, data_dir, file_regex):
        files = glob.glob(os.path.join(data_dir, file_regex))
        if len(files) > 0:
            cat_comp = GeodesicStarCatalogComponent(files[0])
            if cat_comp.load_data_file():
                return cat_comp
        return None


    @property
    def max_geodesic_grid_level(self):
        return self._max_geodesic_grid_level


    def cat_component(self, lev):
        return self._cat_components[lev]


    def init_tringle(self, lev, index, c0, c1, c2):
        self._cat_components[lev].init_tringle(index, c0, c1, c2)


class TrixelData:
    def __init__(self):
        self.center = None
        self.axis0 = None
        self.axis1 = None

    def get_J2000_pos(self, star_X0, star_X1):
        return (self.axis0 * star_X0) + (star_X1 * self.axis1) + self.center

class TrixelLev:

    def __init__(self, depth):
        self.trixel_data = [ TrixelData() for _ in range(HtmGrid.nr_of_triangles(depth))]
        self._triangle_size = 0.0
        self._star_position_scale = 0.0

    def init_trixel(self, index, c0, c1, c2):
        z = self.trixel_data[index]
        z.center = vector_norm_add3(c0, c1, c2)
        z.axis0 = vector_norm_cross(NORTH, z.center)
        z.axis1 = vector_cross(z.center, z.axis0)

        d1 = vector_length(vector_sub(c0, c1))
        d2 = vector_length(vector_sub(c1, c2))
        d3 = vector_length(vector_sub(c2, c0))
        dmax = max(d1, d2, d3)
        if dmax > self._triangle_size:
            self._triangle_size = dmax

        # Initialize star_position_scale. This scale is used to multiply stars position
        # encoded as integers so that it optimize precision over the triangle.
        # It has to be computed for each triangle because the relative orientation of the 2 axis is different for each triangle.
        mu0 = vector_dot(vector_sub(c0,z.center), z.axis0)
        mu1 = vector_dot(vector_sub(c0,z.center), z.axis1)
        f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
        h = abs(mu0)*f
        if self._star_position_scale < h:
            self._star_position_scale = h
        h = abs(mu1)*f
        if self._star_position_scale < h:
            self._star_position_scale = h

        mu0 = vector_dot(vector_sub(c1,z.center), z.axis0)
        mu1 = vector_dot(vector_sub(c1,z.center), z.axis1)
        f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
        h = abs(mu0)*f
        if self._star_position_scale < h:
            self._star_position_scale = h
        h = abs(mu1)*f
        if self._star_position_scale < h:
            self._star_position_scale = h

        mu0 = vector_dot(vector_sub(c2,z.center), z.axis0)
        mu1 = vector_dot(vector_sub(c2,z.center), z.axis1)
        f = 1.0/math.sqrt(1.0-mu0*mu0-mu1*mu1)
        h = abs(mu0)*f
        if self._star_position_scale < h:
            self._star_position_scale = h
        h = abs(mu1)*f
        if self._star_position_scale < h:
            self._star_position_scale = h


def get_radec_stars1(stars1, zone_data):
    dim = len(stars1)

    rectJ2000 = zone_data.get_J2000_pos(stars1['x0'].reshape(dim, 1), stars1['x1'].reshape(dim, 1))
    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    return ra[:,0], dec[:,0], stars1['mag']


def get_radec_stars2(stars2, zone_data):
    dim = len(stars2)

    ix01 = stars2['x01']

    x0 = (ix01[:,0].astype(np.uint32) | ix01[:,1].astype(np.uint32)<<8 | (ix01[:,2] & 0xF).astype(np.uint32)<<16) << 12
    x0 = x0.astype(np.int32) >> 12

    x1 = (ix01[:,2]>>4 | ix01[:,3].astype(np.uint32)<<4 | ix01[:,4].astype(np.uint32)<<12) << 12
    x1 = x1.astype(np.int32) >> 12

    rectJ2000 = zone_data.get_J2000_pos(x0.reshape(dim, 1), x1.reshape(dim, 1))

    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    return ra[:,0], dec[:,0], stars2['magbv']>>3


def get_radec_stars3(stars3, zone_data):
    dim = len(stars3)

    ix01 = stars3['x01']
    ibvx1 = stars3['bvx1']

    x0 = (ix01[:,0] | ix01[:,1].astype(np.uint32)<<8 | (ix01[:,2] & 0x3).astype(np.uint32)<<16) << 14
    x0 = x0.astype(np.int32) >> 14

    x1 = (ix01[:,2]>>2 | ix01[:,3].astype(np.uint32)<<6 | (ibvx1&0xf).astype(np.uint32)<<14) << 14
    x1 = x1.astype(np.int32) >> 14

    rectJ2000 = zone_data.get_J2000_pos(x0.reshape(dim, 1), x1.reshape(dim, 1))
    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    return ra[:,0], dec[:,0], stars3['magbv']>>3


def convert_stars1(stars1, zone_data, mag_table, star_position_scale):
    dim = len(stars1)

    rectJ2000 = zone_data.get_J2000_pos(stars1['x0'].reshape(dim, 1), stars1['x1'].reshape(dim, 1))
    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    mf = (np.pi/180.)*(0.0001/3600.0) / star_position_scale

    # seems like weird idea to convert stellarium format to equatorial
    drectJ2000 = zone_data.get_J2000_pos(stars1['x0'].reshape(dim, 1)+stars1['dx0'].reshape(dim, 1) * mf, stars1['x1'].reshape(dim, 1)+stars1['dx1'].reshape(dim, 1) * mf)
    year_mov_ra, year_mov_dec = rect_to_sphere(drectJ2000[:,[0]], drectJ2000[:,[1]], drectJ2000[:,[2]])

    d_ra = ra - year_mov_ra
    d_dec = dec - year_mov_dec

    htm_stars1 = np.core.records.fromarrays( \
        [ \
            stars1['hip'],
            stars1['cIds'],
            ra[:,0] * 1000000.0,
            dec[:,0] * 1000000.0,
            d_ra[:,0] * 1000000.0 * 10,
            d_dec[:,0] * 100000.0 * 10,
            stars1['bv'],
            mag_table[stars1['mag']]*100,
            stars1['spInt'],
            stars1['plx'],
        ], \
        dtype=HTM_STARDATA_DT)


    return htm_stars1


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def _get_htm_mesh(level):
    mesh = htm_meshes.get(level)
    if not mesh:
        mesh = HTM(level)
        htm_meshes[level] = mesh
    return mesh

def init_trixel_lev(depth, index, v0, v1, v2):
    trixel_levels[depth].init_trixel(index, v0, v1, v2)

if __name__ == '__main__':
    data_dir='../data/catalogs/'
    tm = time()
    cat = GeodesicStarCatalog(data_dir, None)
    print("Loaded in : " + str(time()-tm) + "ms")

    htm_grid = HtmGrid(cat.max_geodesic_grid_level)

    trixel_levels = [None] * (cat.max_geodesic_grid_level+1)
    for i in range(len(trixel_levels)):
        trixel_levels[i] = TrixelLev(i)

    htm_grid.visit_triangles(cat.max_geodesic_grid_level, init_trixel_lev)

    for i in range(cat.max_geodesic_grid_level+1):
        cat_comp = cat.cat_component(i)
        nr_of_zones = cat_comp.nr_of_zones
        progress_suffix = 'Converting level {} / stars {} / file type {}  '.format(i, cat_comp.nr_of_stars, cat_comp.file_type)
        htm_mesh = _get_htm_mesh(i)

        trixel_stars = [[] for _ in range(htm_mesh.size())]

        mask = 1 << (htm_mesh.get_depth() * 2 + 3)

        star_idx = 0
        for zone in range(nr_of_zones):
            zone_stars = cat_comp.get_raw_zone_stars(zone)
            progress(zone, nr_of_zones, suffix=progress_suffix)
            if len(zone_stars)>0:
                zone_data = cat_comp.get_zone_data(zone)
                if cat_comp.file_type == 0:
                    ra, dec, mag = get_radec_stars1(zone_stars, zone_data)
                elif cat_comp.file_type == 1:
                    ra, dec, mag = get_radec_stars2(zone_stars, zone_data)
                else:
                    ra, dec, mag = get_radec_stars3(zone_stars, zone_data)

                conv = htm_mesh.lookup_id(ra*180.0/np.pi, dec*180.0/np.pi)

                for i in range(len(conv)):
                    trixel_stars[conv[i] ^ mask].append((mag[i], star_idx))
                    star_idx += 1
                    # print(zone_stars[i])

        sys.stdout.write('\n')
        sys.stdout.flush()

        progress_suffix = 'Sorting level {} / stars {} / file type {}  '.format(i, cat_comp.nr_of_stars, cat_comp.file_type)

        for i in range(len(trixel_stars)):
            progress(i, len(trixel_stars), suffix=progress_suffix)
            trixel_stars[i].sort(key=lambda x: x[0])

        sys.stdout.write('\n')
        sys.stdout.flush()

        progress_suffix = 'Converting level {} / stars {} / file type {}  '.format(i, cat_comp.nr_of_stars, cat_comp.file_type)

        star_id = 0
        mag_table = cat_comp.get_mag_table()
        star_position_scale = cat_comp.star_position_scale
        for zone in range(nr_of_zones):
            zone_stars = cat_comp.get_raw_zone_stars(zone)
            progress(zone, nr_of_zones, suffix=progress_suffix)
            if len(zone_stars)>0:
                conv_stars = None
                zone_data = cat_comp.get_zone_data(zone)
                if cat_comp.file_type == 0:
                    conv_stars = convert_stars1(zone_stars, zone_data, mag_table, star_position_scale)
                elif cat_comp.file_type == 1:
                    # conv_stars = convert_stars2(zone_stars, zone_data, mag_table, star_position_scale)
                    pass
                else:
                    # conv_stars = convert_stars3(zone_stars, zone_data, mag_table, star_position_scale)
                    pass
                # if conv_stars is not None:
                    # print(conv_stars)

        sys.stdout.write('\n')
        sys.stdout.flush()

        print('Htm level {} avg trixel size: {}'.format(i + 1, star_idx / len(trixel_stars)))
