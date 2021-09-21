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

from collections import namedtuple

import os
import sys
import struct
import glob
import math
import numpy as np
from time import time

from .astrocalc import *
from .vector_math import *
from .star_catalog import *
from .geodesic_binfile_reader import *
from .geodesic_grid import *

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


ZONE_STARDATA_DT = np.dtype([('ra', np.float64),
                             ('dec', np.float64),
                             ('mag', np.float64),
                             ('bvind', np.uint8),
                             ('bsc', np.dtype(object))
                           ])

use_precalc_star_position_scale = False
use_precalc_triangle_size = False


def set_use_precalc_star_position_scale(val):
    global use_precalc_star_position_scale
    use_precalc_star_position_scale = val


def set_use_precalc_triangle_size(val):
    global use_precalc_triangle_size
    use_precalc_triangle_size = val


def _convert_stars1_helper(stars1, zone_data, mag_table, bsc_map):
    dim = len(stars1)

    rectJ2000 = zone_data.get_J2000_pos(stars1['x0'].reshape(dim, 1), stars1['x1'].reshape(dim, 1))
    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    zone_stars = np.core.records.fromarrays( \
        [ \
            ra[:,0],
            dec[:,0],
            mag_table[stars1['mag']],
            stars1['bv'],
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=ZONE_STARDATA_DT)

    if bsc_map:
        for i in range(dim):
            hip = stars1[i]['hip'][0] | stars1[i]['hip'][2]<<8  | stars1[i]['hip'][2]<<16
            if hip != 0:
                bsc_star = bsc_map.get(hip)
                if bsc_star:
                    zone_stars[i]['bsc'] = bsc_star

    return zone_stars


def _convert_stars2_helper(stars2, zone_data, mag_table):
    dim = len(stars2)

    ix01 = stars2['x01']

    x0 = (ix01[:,0].astype(np.uint32) | ix01[:,1].astype(np.uint32)<<8 | (ix01[:,2] & 0xF).astype(np.uint32)<<16) << 12
    x0 = x0.astype(np.int32) >> 12

    x1 = (ix01[:,2]>>4 | ix01[:,3].astype(np.uint32)<<4 | ix01[:,4].astype(np.uint32)<<12) << 12
    x1 = x1.astype(np.int32) >> 12

    rectJ2000 = zone_data.get_J2000_pos(x0.reshape(dim, 1), x1.reshape(dim, 1))


    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])


    zone_stars = np.core.records.fromarrays( \
        [ \
            ra[:,0],
            dec[:,0],
            mag_table[stars2['magbv']>>3],
            stars2['bvdx1']>>4 | (stars2['magbv']&0x7)<<4,
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=ZONE_STARDATA_DT)

    return zone_stars


def _convert_stars3_helper(stars3, zone_data, mag_table):
    dim = len(stars3)

    ix01 = stars3['x01']
    ibvx1 = stars3['bvx1']

    x0 = (ix01[:,0] | ix01[:,1].astype(np.uint32)<<8 | (ix01[:,2] & 0x3).astype(np.uint32)<<16) << 14
    x0 = x0.astype(np.int32) >> 14

    x1 = (ix01[:,2]>>2 | ix01[:,3].astype(np.uint32)<<6 | (ibvx1&0xf).astype(np.uint32)<<14) << 14
    x1 = x1.astype(np.int32) >> 14

    rectJ2000 = zone_data.get_J2000_pos(x0.reshape(dim, 1), x1.reshape(dim, 1))
    ra, dec = rect_to_sphere(rectJ2000[:,[0]], rectJ2000[:,[1]], rectJ2000[:,[2]])

    zone_stars = np.core.records.fromarrays( \
        [ \
            ra[:,0],
            dec[:,0],
            mag_table[stars3['magbv']>>3],
            (stars3['magbv']&0x7)<<4 | stars3['bvx1']>>4,
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=ZONE_STARDATA_DT)

    return zone_stars

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


    def _convert_zone_stars(self, zone_stars, zone_data, bsc_map):
        mag_table = self._data_reader.get_mag_table()
        if self._data_reader.file_type == 0:
            return _convert_stars1_helper(zone_stars, zone_data, mag_table, bsc_map)
        elif self._data_reader.file_type == 1:
            return _convert_stars2_helper(zone_stars, zone_data, mag_table)
        else:
            return _convert_stars3_helper(zone_stars, zone_data, mag_table)


    def get_zone_stars(self, zone, bsc_map=None):
        if not self._file_opened:
            return None
        zone_stars = self._star_blocks[zone]
        if zone_stars is None:
            records = self._data_reader.get_record_count(zone)
            if records > 0:
                data_file = self._data_reader.file
                data_file.seek(self._data_reader.get_offset(zone))
                zone_stars = np.fromfile(data_file, self._get_data_format(), records)

                if self._data_reader.byteswap:
                    zone_stars.byteswap

                zone_stars = self._convert_zone_stars(zone_stars, self._zone_data_ar[zone], bsc_map)
            else:
                zone_stars = []

            self._star_blocks[zone] = zone_stars

        return zone_stars


    def free_mem(self):
        if not self._file_opened:
            return
        for i in range(len(self._star_blocks)):
            self._star_blocks[i] = None


class GeodesicStarCatalog(StarCatalog):
    """
    Star catalog composed of GeodesicStarCatalogComponent. Each component represents
    one level of Geodesic tree.
    """
    def __init__(self, data_dir, bsc_map):
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

        self.max_geodesic_grid_level = i-1 if i > 0 else 0

        self._geodesic_grid = GeodesicGrid(self.max_geodesic_grid_level)
        self._geodesic_grid.visit_triangles(self.max_geodesic_grid_level, self.init_tringle)

        for cat_comp in self._cat_components:
            print('Level={} scale={} triangle_size={}'.format(cat_comp.level, cat_comp.star_position_scale, cat_comp.triangle_size))
            cat_comp.scale_axis()

        self.search_result = GeodesicSearchResult(self.max_geodesic_grid_level)

    def _load_gsc_component(self, data_dir, file_regex):
        files = glob.glob(os.path.join(data_dir, file_regex))
        if len(files) > 0:
            cat_comp = GeodesicStarCatalogComponent(files[0])
            if cat_comp.load_data_file():
                return cat_comp
        return None


    def _select_stars_from_zones(self, iterator, lev, lm_stars):
        stars = None
        zone = iterator.next()
        while zone != -1:
            zone_stars = self._cat_components[lev].get_zone_stars(zone)
            # print('Level={} Zone={} Len={}'.format(lev, zone, len(zone_stars)))
            if len(zone_stars) > 0:
                mag = zone_stars['mag']
                zone_stars = zone_stars[mag <= lm_stars]
                if len(zone_stars) > 0:
                    if stars is None:
                        stars= zone_stars
                    else:
                        stars = np.append(stars, zone_stars)
            zone = iterator.next()
        return stars


    def init_tringle(self, lev, index, c0, c1, c2):
        self._cat_components[lev].init_tringle(index, c0, c1, c2)


    def select_stars(self, fieldcentre, radius, lm_stars):
        """
        Return an array containing of items [[ra, dec, mag], [ra, dec, mag]...]
        for all stars in the field centered around fieldcentre with iven radius,
        fieldcentre and radius.
        """
        tmp_arr = []

        max_search_level = -1
        for cat_comp in self._cat_components:
            if cat_comp.level > 0 and cat_comp.mag_min_mag > lm_stars:
                break
            max_search_level += 1

        if max_search_level >= 0:
            field_rect3 = sphere_to_rect(fieldcentre[0], fieldcentre[1])

            lev_spherical_caps = []
            print('Radius: {}'.format(radius/np.pi*180.0))
            for lev in range(max_search_level+1):
                radius_inner = radius / 2.0
                radius_outer = self._cat_components[lev].triangle_size + radius / 2.0
                lev_spherical_caps.append(SphericalCap(field_rect3, math.cos(radius_inner), math.cos(radius_outer)))

            self.search_result.reset()
            self._geodesic_grid.search_zones(lev_spherical_caps, self.search_result, max_search_level)

            for lev in range(max_search_level):
                print('Inside iterator')
                inside_iterator = GeodesicSearchInsideIterator(self.search_result, lev)
                stars = self._select_stars_from_zones(inside_iterator, lev, lm_stars)
                if stars is not None and stars.shape[0] > 0:
                    tmp_arr.append(stars)

                print('Border iterator')
                border_iterator = GeodesicSearchBorderIterator(self.search_result, lev)
                stars = self._select_stars_from_zones(border_iterator, lev, lm_stars)
                if stars is not None and stars.shape[0] > 0:
                    tmp_arr.append(stars)

        return np.concatenate(tmp_arr, axis=0) if len(tmp_arr) > 0 else None


    def free_mem(self):
        for cat_comp in self._cat_components:
            cat_comp.free_mem()


    def get_star_color(self, star):
        return None


if __name__ == '__main__':
    data_dir='./data/catalogs/'
    tm = time()
    cat = GeodesicStarCatalog(data_dir, none)
    print("Loaded in : " + str(time()-tm) + "ms")
    print("Done")
