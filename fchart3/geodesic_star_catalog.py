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

import glob

from .astrocalc import *
from .np_astrocalc import *
from .star_catalog import *
from .geodesic_binfile_reader import *
from .geodesic_grid import *

# from memory_profiler import profile


COLOR_TABLE = (
    (0.602745,0.713725,1.000000),
    (0.604902,0.715294,1.000000),
    (0.607059,0.716863,1.000000),
    (0.609215,0.718431,1.000000),
    (0.611372,0.720000,1.000000),
    (0.613529,0.721569,1.000000),
    (0.635490,0.737255,1.000000),
    (0.651059,0.749673,1.000000),
    (0.666627,0.762092,1.000000),
    (0.682196,0.774510,1.000000),
    (0.697764,0.786929,1.000000),
    (0.713333,0.799347,1.000000),
    (0.730306,0.811242,1.000000),
    (0.747278,0.823138,1.000000),
    (0.764251,0.835033,1.000000),
    (0.781223,0.846929,1.000000),
    (0.798196,0.858824,1.000000),
    (0.812282,0.868236,1.000000),
    (0.826368,0.877647,1.000000),
    (0.840455,0.887059,1.000000),
    (0.854541,0.896470,1.000000),
    (0.868627,0.905882,1.000000),
    (0.884627,0.916862,1.000000),
    (0.900627,0.927843,1.000000),
    (0.916627,0.938823,1.000000),
    (0.932627,0.949804,1.000000),
    (0.948627,0.960784,1.000000),
    (0.964444,0.972549,1.000000),
    (0.980261,0.984313,1.000000),
    (0.996078,0.996078,1.000000),
    (1.000000,1.000000,1.000000),
    (1.000000,0.999643,0.999287),
    (1.000000,0.999287,0.998574),
    (1.000000,0.998930,0.997861),
    (1.000000,0.998574,0.997148),
    (1.000000,0.998217,0.996435),
    (1.000000,0.997861,0.995722),
    (1.000000,0.997504,0.995009),
    (1.000000,0.997148,0.994296),
    (1.000000,0.996791,0.993583),
    (1.000000,0.996435,0.992870),
    (1.000000,0.996078,0.992157),
    (1.000000,0.991140,0.981554),
    (1.000000,0.986201,0.970951),
    (1.000000,0.981263,0.960349),
    (1.000000,0.976325,0.949746),
    (1.000000,0.971387,0.939143),
    (1.000000,0.966448,0.928540),
    (1.000000,0.961510,0.917938),
    (1.000000,0.956572,0.907335),
    (1.000000,0.951634,0.896732),
    (1.000000,0.946695,0.886129),
    (1.000000,0.941757,0.875526),
    (1.000000,0.936819,0.864924),
    (1.000000,0.931881,0.854321),
    (1.000000,0.926942,0.843718),
    (1.000000,0.922004,0.833115),
    (1.000000,0.917066,0.822513),
    (1.000000,0.912128,0.811910),
    (1.000000,0.907189,0.801307),
    (1.000000,0.902251,0.790704),
    (1.000000,0.897313,0.780101),
    (1.000000,0.892375,0.769499),
    (1.000000,0.887436,0.758896),
    (1.000000,0.882498,0.748293),
    (1.000000,0.877560,0.737690),
    (1.000000,0.872622,0.727088),
    (1.000000,0.867683,0.716485),
    (1.000000,0.862745,0.705882),
    (1.000000,0.858617,0.695975),
    (1.000000,0.854490,0.686068),
    (1.000000,0.850362,0.676161),
    (1.000000,0.846234,0.666254),
    (1.000000,0.842107,0.656346),
    (1.000000,0.837979,0.646439),
    (1.000000,0.833851,0.636532),
    (1.000000,0.829724,0.626625),
    (1.000000,0.825596,0.616718),
    (1.000000,0.821468,0.606811),
    (1.000000,0.817340,0.596904),
    (1.000000,0.813213,0.586997),
    (1.000000,0.809085,0.577090),
    (1.000000,0.804957,0.567183),
    (1.000000,0.800830,0.557275),
    (1.000000,0.796702,0.547368),
    (1.000000,0.792574,0.537461),
    (1.000000,0.788447,0.527554),
    (1.000000,0.784319,0.517647),
    (1.000000,0.784025,0.520882),
    (1.000000,0.783731,0.524118),
    (1.000000,0.783436,0.527353),
    (1.000000,0.783142,0.530588),
    (1.000000,0.782848,0.533824),
    (1.000000,0.782554,0.537059),
    (1.000000,0.782259,0.540294),
    (1.000000,0.781965,0.543529),
    (1.000000,0.781671,0.546765),
    (1.000000,0.781377,0.550000),
    (1.000000,0.781082,0.553235),
    (1.000000,0.780788,0.556471),
    (1.000000,0.780494,0.559706),
    (1.000000,0.780200,0.562941),
    (1.000000,0.779905,0.566177),
    (1.000000,0.779611,0.569412),
    (1.000000,0.779317,0.572647),
    (1.000000,0.779023,0.575882),
    (1.000000,0.778728,0.579118),
    (1.000000,0.778434,0.582353),
    (1.000000,0.778140,0.585588),
    (1.000000,0.777846,0.588824),
    (1.000000,0.777551,0.592059),
    (1.000000,0.777257,0.595294),
    (1.000000,0.776963,0.598530),
    (1.000000,0.776669,0.601765),
    (1.000000,0.776374,0.605000),
    (1.000000,0.776080,0.608235),
    (1.000000,0.775786,0.611471),
    (1.000000,0.775492,0.614706),
    (1.000000,0.775197,0.617941),
    (1.000000,0.774903,0.621177),
    (1.000000,0.774609,0.624412),
    (1.000000,0.774315,0.627647),
    (1.000000,0.774020,0.630883),
    (1.000000,0.773726,0.634118),
    (1.000000,0.773432,0.637353),
    (1.000000,0.773138,0.640588),
    (1.000000,0.772843,0.643824),
    (1.000000,0.772549,0.647059),
)

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


RECT_ZONE_STARDATA_DT = np.dtype([('x', np.float32),
                                  ('y', np.float32),
                                  ('z', np.float32),
                                  ('mag', np.float32),
                                  ('bvind', np.uint8),
                                  ('bsc', np.dtype(object))
                                  ])


EQ_ZONE_STARDATA_DT = np.dtype([('ra', np.float32),
                                ('dec', np.float32),
                                ('mag', np.float32),
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


def _convert_stars1_helper(stars1, zone_data, mag_table, bsc_hip_map):
    dim = len(stars1)

    rectJ2000 = get_J2000_pos(zone_data, stars1['x0'].reshape(dim, 1), stars1['x1'].reshape(dim, 1))

    zone_stars = np.core.records.fromarrays( \
        [ \
            rectJ2000[:,0],
            rectJ2000[:,1],
            rectJ2000[:,2],
            mag_table[stars1['mag']],
            stars1['bv'],
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=RECT_ZONE_STARDATA_DT)

    if bsc_hip_map:
        hip_col = stars1['hip']
        for i in range(dim):
            hip = hip_col[i][0] | hip_col[i][1].astype(np.uint32)<<8  | hip_col[i][2].astype(np.uint32)<<16
            if hip != 0:
                bsc_star = bsc_hip_map.get(hip)
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

    rectJ2000 = get_J2000_pos(zone_data, x0.reshape(dim, 1), x1.reshape(dim, 1))

    zone_stars = np.core.records.fromarrays( \
        [ \
            rectJ2000[:,0],
            rectJ2000[:,1],
            rectJ2000[:,2],
            mag_table[stars2['magbv']>>3],
            stars2['bvdx1']>>4 | (stars2['magbv']&0x7)<<4,
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=RECT_ZONE_STARDATA_DT)

    return zone_stars


def _convert_stars3_helper(stars3, zone_data, mag_table):
    dim = len(stars3)

    ix01 = stars3['x01']
    ibvx1 = stars3['bvx1']

    x0 = (ix01[:,0] | ix01[:,1].astype(np.uint32)<<8 | (ix01[:,2] & 0x3).astype(np.uint32)<<16) << 14
    x0 = x0.astype(np.int32) >> 14

    x1 = (ix01[:,2]>>2 | ix01[:,3].astype(np.uint32)<<6 | (ibvx1&0xf).astype(np.uint32)<<14) << 14
    x1 = x1.astype(np.int32) >> 14

    rectJ2000 = get_J2000_pos(zone_data, x0.reshape(dim, 1), x1.reshape(dim, 1))

    zone_stars = np.core.records.fromarrays( \
        [ \
            rectJ2000[:,0],
            rectJ2000[:,1],
            rectJ2000[:,2],
            mag_table[stars3['magbv']>>3],
            (stars3['magbv']&0x7)<<4 | stars3['bvx1']>>4,
            np.empty(dim, np.dtype(object)),
        ], \
        dtype=RECT_ZONE_STARDATA_DT)

    return zone_stars


STAR3_DT = np.dtype([('x01', np.uint8, (4,)),
                     ('bvx1', np.uint8),
                     ('magbv', np.uint8),
                    ])

NORTH = (0.0, 0.0, 1.0)

class ZoneData:
    __slots__ = 'center', 'axis0', 'axis1'

ZoneDataNp = np.dtype([('center', (np.float32, 3)),
                       ('axis0', (np.float32, 3)),
                       ('axis1', (np.float32, 3))])

def get_J2000_pos(zone_data, star_X0, star_X1):
    return (zone_data['axis0'] * star_X0) + (star_X1 * zone_data['axis1']) + zone_data['center']


class GeodesicStarCatalogComponent:

    def __init__(self, file_name):
        self._data_reader = None
        self.file_name = file_name
        self._file_opened = False
        self._nr_of_zones = 0
        self._star_blocks = None
        self._zone_data_ar = None
        self.star_position_scale = 0.0
        self.triangle_size = 0.0

    def to_np_arrays(self):
        self._zone_data_ar = np.array([(zd.center, zd.axis0, zd.axis1) for zd in self._zone_data_ar], dtype=ZoneDataNp)

    @property
    def level(self):
        return self._data_reader.level

    @property
    def mag_min_mag(self):
        return self._data_reader.mag_min_mag

    @property
    def nr_of_stars(self):
        return self._data_reader.nr_of_stars

    def load_data_file(self):
        self._data_reader = GeodesicBinFileReader()
        self._data_reader.open_file(self.file_name)
        if not self._data_reader.file:
            print("Failed to open star catalog {}, disabling it.".format(self.file_name))
            return False
        try:
            self._data_reader.read_header()
        except Exception as e:
            print("Header read error for deep star catalog {}, disabling it!".format(self.file_name))
            return False

        self._nr_of_zones = GeodesicGrid.nr_of_zones(self._data_reader.level)
        self._star_blocks = [None] * self._nr_of_zones
        self._zone_data_ar = [ZoneData() for _ in range(self._nr_of_zones)]
        self._file_opened = True
        return self._file_opened

    def init_triangle(self, index, c0, c1, c2):
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
            if dmax > self.triangle_size:
                self.triangle_size = dmax

        if not use_precalc_star_position_scale:
            # Initialize star_position_scale. This scale is used to multiply stars position
            # encoded as integers so that it optimize precision over the triangle.
            # It has to be computed for each triangle because the relative orientation of the 2 axis is different for each triangle.
            sc0 = vector_sub(c0,z.center)
            mu0 = vector_dot(sc0, z.axis0)
            mu1 = vector_dot(sc0, z.axis1)
            f = 1.0-mu0*mu0-mu1*mu1
            h = mu0*mu0/f
            if self.star_position_scale < h:
                self.star_position_scale = h
            h = mu1*mu1/f
            if self.star_position_scale < h:
                self.star_position_scale = h

            sc1 = vector_sub(c1,z.center)
            mu0 = vector_dot(sc1, z.axis0)
            mu1 = vector_dot(sc1, z.axis1)
            f = 1.0-mu0*mu0-mu1*mu1
            h = mu0*mu0/f
            if self.star_position_scale < h:
                self.star_position_scale = h
            h = mu1*mu1/f
            if self.star_position_scale < h:
                self.star_position_scale = h

            sc2 = vector_sub(c2,z.center)
            mu0 = vector_dot(sc2, z.axis0)
            mu1 = vector_dot(sc2, z.axis1)
            f = 1.0-mu0*mu0-mu1*mu1
            h = mu0*mu0/f
            if self.star_position_scale < h:
                self.star_position_scale = h
            h = mu1*mu1/f
            if self.star_position_scale < h:
                self.star_position_scale = h

    def scale_axis(self):
        if self._data_reader.file_type == 0:
            star_max_pos_val = 0x7FFFFFFF
        elif self._data_reader.file_type == 1:
            star_max_pos_val = (1 << 19)-1
        else:
            star_max_pos_val = (1 << 17)-1

        self.star_position_scale = math.sqrt(self.star_position_scale) / star_max_pos_val

        for z in self._zone_data_ar:
            z.axis0 = np.array(vector_scal_dot(self.star_position_scale, z.axis0))
            z.axis1 = np.array(vector_scal_dot(self.star_position_scale, z.axis1))

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

    def load_static_stars(self, bsc_hip_map):
        for zone in range(self._nr_of_zones):
            self.get_zone_stars(zone, bsc_hip_map=bsc_hip_map)

    def get_zone_stars(self, zone, bsc_hip_map=None):
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

                zone_stars = self._convert_zone_stars(zone_stars, self._zone_data_ar[zone], bsc_hip_map)
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
    Star catalog composed of GeodesicStarCatalogComponent. Each component represents one level of Geodesic tree.
    """
    # @profile
    def __init__(self, data_dir, extra_data_dir, bsc_hip_map):
        # tm = time()
        self._cat_components = []
        max_file_num = 8
        for i in range(max_file_num+1):
            cat_file_name_regexp = 'stars_{}_*.cat'
            cat_comp = self._load_gsc_component(data_dir, cat_file_name_regexp.format(i))
            if not cat_comp:
                if extra_data_dir:
                    cat_comp = self._load_gsc_component(extra_data_dir, cat_file_name_regexp.format(i))
                if not cat_comp:
                    break
            if cat_comp.level != i:
                print("File {} has invalid catalog level.".format(self.file_name))
                break
            print('{} stars read from {}'.format(cat_comp.nr_of_stars, os.path.split(cat_comp.file_name)[1]))
            self._cat_components.append(cat_comp)

        self._max_geodesic_grid_level = self._cat_components[-1].level
        self._geodesic_grid = GeodesicGrid(self._max_geodesic_grid_level)
        self._geodesic_grid.visit_triangles(self._max_geodesic_grid_level, self.init_triangle)

        for cat_comp in self._cat_components:
            cat_comp.scale_axis()
            cat_comp.to_np_arrays()

        self.search_result = GeodesicSearchResult(self._max_geodesic_grid_level)

        if len(self._cat_components) > 0:
            self._cat_components[0].load_static_stars(bsc_hip_map)

        self._geodesic_grid.to_np_arrays()

        # print("#################### Geodesic star catalog within {} s".format(str(time()-tm)), flush=True)

    def _load_gsc_component(self, data_dir, file_regex):
        files = glob.glob(os.path.join(data_dir, file_regex))
        if len(files) > 0:
            cat_comp = GeodesicStarCatalogComponent(files[0])
            if cat_comp.load_data_file():
                return cat_comp
        return None

    def _select_stars_from_zones(self, iterator, lev, lm_stars, field_rect3, cos_radius):
        stars = []
        zone = iterator.next()
        while zone != -1:
            zone_stars = self._cat_components[lev].get_zone_stars(zone)
            # print('Level={} Zone={} Len={}'.format(lev, zone, len(zone_stars)))
            if len(zone_stars) > 0:
                mag = zone_stars['mag']
                scal_dot = zone_stars['x']*field_rect3[0] + zone_stars['y']*field_rect3[1] + zone_stars['z']*field_rect3[2]
                zone_stars = zone_stars[np.logical_and(mag <= lm_stars, scal_dot > cos_radius)]
                if len(zone_stars) > 0:
                    stars.append(zone_stars)
            zone = iterator.next()
        return stars

    @property
    def max_geodesic_grid_level(self):
        return self._max_geodesic_grid_level

    def init_triangle(self, lev, index, c0, c1, c2):
        self._cat_components[lev].init_triangle(index, c0, c1, c2)

    def select_stars(self, fieldcentre, radius, lm_stars, precession_matrix):
        """
        Return an array containing of items [[ra, dec, mag], [ra, dec, mag]...]
        for all stars in the field centered around field centre with given radius,
        field centre and radius.
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
            # print('Radius: {}'.format(radius/np.pi*180.0))
            cos_radius = math.cos(radius)
            for lev in range(max_search_level+1):
                radius_inner = radius
                # use asin() since it is chord on sphere
                triangle_radius = 2 * math.asin(TRIANGLE_CENTER_FACTOR * self._cat_components[lev].triangle_size)
                radius_outer = triangle_radius + radius
                lev_spherical_caps.append(SphericalCap(field_rect3, math.cos(radius_inner), math.cos(radius_outer)))

            self.search_result.reset()
            self._geodesic_grid.search_zones(lev_spherical_caps, self.search_result, max_search_level)

            for lev in range(max_search_level + 1):
                # print('Inside iterator')
                inside_iterator = GeodesicSearchInsideIterator(self.search_result, lev)
                stars = self._select_stars_from_zones(inside_iterator, lev, lm_stars, field_rect3, cos_radius)
                if len(stars) > 0:
                    tmp_arr += stars

                # print('Border iterator')
                border_iterator = GeodesicSearchBorderIterator(self.search_result, lev)
                stars = self._select_stars_from_zones(border_iterator, lev, lm_stars, field_rect3, cos_radius)
                if len(stars) > 0:
                    tmp_arr += stars

        rect_stars = np.concatenate(tmp_arr, axis=0) if len(tmp_arr) > 0 else None

        if rect_stars is None or len(rect_stars) == 0:
            return None

        if precession_matrix is not None:
            mat_rect_stars = np.column_stack((rect_stars['x'], rect_stars['y'], rect_stars['z']))
            mat_rect_stars = np.matmul(mat_rect_stars, precession_matrix)
            ra, dec = np_rect_to_sphere(mat_rect_stars[:,[0]], mat_rect_stars[:,[1]], mat_rect_stars[:,[2]])
        else:
            dim = len(rect_stars)
            ra, dec = np_rect_to_sphere(rect_stars['x'].reshape(dim, 1), rect_stars['y'].reshape(dim, 1), rect_stars['z'].reshape(dim, 1))

        eq_stars = np.core.records.fromarrays(
            [
                ra[:, 0],
                dec[:, 0],
                rect_stars['mag'],
                rect_stars['bvind'],
                rect_stars['bsc'],
            ],
            dtype=EQ_ZONE_STARDATA_DT)

        return eq_stars

    def free_mem(self):
        for cat_comp in self._cat_components:
            if cat_comp.level > 0:
                cat_comp.free_mem()

    def get_star_color(self, star):
        return COLOR_TABLE[star['bvind']]


if __name__ == '__main__':
    data_dir='./data/catalogs/'
    tm = time()
    cat = GeodesicStarCatalog(data_dir, None)
    print("Loaded in : " + str(time()-tm) + "ms")
    print("Done")
