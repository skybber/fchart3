#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
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

from .astro.astrocalc import *
from .astro.np_astrocalc import *
from .geodesic_binfile_reader import *
from .geodesic_grid import *
from .vector_math import vector_length, vector_sub

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
STAR1_GAIA_DT:
              _______________
    0  gaia_id|               |
    1         |               |
    2         |               |
    3         |               |
    4         |               |
    5         |               |
    6         |               |
    7         |_______________|
    8       x0|               |
    9         |               |
    10        |               |
    11        |_______________|
    12      x1|               |
    13        |               |
    14        |               |
    15        |_______________|
    16      x2|               |
    17        |               |
    18        |               |
    19        |_______________|
    20     dx0|               |
    21        |               |
    22        |               |
    23        |_______________|
    24     dx1|               |
    25        |               |
    26        |               |
    27        |_______________|
    28     dx2|               |
    29        |               |
    30        |               |
    31        |_______________|
    32     b_v|_______________|
    34    vmag|_______________|
    36     plx|_______________|
    38 plx_err|_______________|
    40      rv|_______________|
    42   spInt|_______________|
    44 objtype|_______________|
    45     hip|               |
    46        |               |
    47        |_______________|
"""

STAR1_GAIA_DT = np.dtype([
    ("gaia_id",  np.int64),
    ("x0",       np.int32),
    ("x1",       np.int32),
    ("x2",       np.int32),
    ("dx0",      np.int32),
    ("dx1",      np.int32),
    ("dx2",      np.int32),
    ("b_v",      np.int16),
    ("vmag",     np.int16),
    ("plx",      np.uint16),
    ("plx_err",  np.uint16),
    ("rv",       np.int16),
    ("spInt",    np.uint16),
    ("objtype",  np.uint8),
    ("hip",      np.uint8, (3,)),
])

"""
STAR2_GAIA_DT:
              _______________
    0  gaia_id|               |
    1         |               |
    2         |               |
    3         |               |
    4         |               |
    5         |               |
    6         |               |
    7         |_______________|
    8       x0|               |
    9         |               |
    10        |               |
    11        |_______________|
    12      x1|               |
    13        |               |
    14        |               |
    15        |_______________|
    16     dx0|               |
    17        |               |
    18        |               |
    19        |_______________|
    20     dx1|               |
    21        |               |
    22        |               |
    23        |_______________|
    24     b_v|_______________|
    26    vmag|_______________|
    28     plx|_______________|
    30 plx_err|_______________|
"""

STAR2_GAIA_DT = np.dtype([
    ("gaia_id", np.int64),
    ("x0",      np.int32),
    ("x1",      np.int32),
    ("dx0",     np.int32),
    ("dx1",     np.int32),
    ("b_v",     np.int16),
    ("vmag",    np.int16),
    ("plx",     np.uint16),
    ("plx_err", np.uint16),
])

"""
STAR3_GAIA_DT
              _______________
    0  gaia_id|               |
    1         |               |
    2         |               |
    3         |               |
    4         |               |
    5         |               |
    6         |               |
    7         |_______________|
    8      x0 |               |
    9         |               |
    10        |_______________|
    11     x1 |               |
    12        |               |
    13        |_______________|
    14     b_v|_______________|
    15    vmag|_______________|
"""

STAR3_GAIA_DT = np.dtype([
    ("gaia_id", np.int64),
    ("x0",      np.uint8, (3,)),
    ("x1",      np.uint8, (3,)),
    ("b_v",     np.uint8),
    ("vmag",    np.uint8),
])



RECT_ZONE_STARDATA_DT = np.dtype([('x', np.float32),
                                  ('y', np.float32),
                                  ('z', np.float32),
                                  ('mag', np.float32),
                                  ('bvind', np.uint8),
                                  ('hip', np.uint32)
                                  ])

D3_ZONE_STARDATA_DT = np.dtype([('x', np.float32),
                                ('y', np.float32),
                                ('z', np.float32),
                                ('mag', np.float32),
                                ('bvind', np.uint8),
                                ('hip', np.uint32)
                                ])

EQUILATERAL_TRIANGLE_CENTER_SIDE_DIST = math.sqrt(3)/6
TRIANGLE_CENTER_FACTOR = math.sqrt(0.5**2 + EQUILATERAL_TRIANGLE_CENTER_SIDE_DIST**2)

MAS2RAD = 4.8481368110953594e-9


def _convert_stars1_v3_helper(stars1_v3):
    dim = stars1_v3.shape[0]

    zone_stars = np.empty(dim, dtype=RECT_ZONE_STARDATA_DT)

    zone_stars['x'] = stars1_v3['x0'] / 2e9
    zone_stars['y'] = stars1_v3['x1'] / 2e9
    zone_stars['z'] = stars1_v3['x2'] / 2e9
    zone_stars['mag'] = stars1_v3['vmag'] / 1000.0

    bv_tmp = (stars1_v3['b_v'] / 1000.0 + 0.5) * 31.75
    np.clip(bv_tmp, 0, 127, out=bv_tmp)  # in-place clip
    zone_stars['bvind'] = bv_tmp.astype(np.uint8)
    zone_stars['hip'] = np.zeros(dim, dtype=np.uint32)

    hip_col = stars1_v3['hip']
    for i in range(dim):
        combined_hip = hip_col[i][0] | (hip_col[i][1].astype(np.uint32) << 8) | (hip_col[i][2].astype(np.uint32) << 16)
        hip = combined_hip >> 5
        if hip != 0:
            zone_stars[i]['hip'] = hip

    return zone_stars


def _convert_stars2_v3_helper(stars2_v3):
    dim = len(stars2_v3)

    ra_rad = stars2_v3['x0'] * MAS2RAD
    dec_rad = stars2_v3['x1'] * MAS2RAD

    x, y, z = np_sphere_to_rect(ra_rad, dec_rad)

    zone_stars = np.empty(dim, dtype=RECT_ZONE_STARDATA_DT)

    zone_stars['x'] = x
    zone_stars['y'] = y
    zone_stars['z'] = z

    zone_stars['mag'] = stars2_v3['vmag'] / 1000.0

    bv_tmp = (stars2_v3['b_v'] / 1000.0 + 0.5) * 31.75
    np.clip(bv_tmp, 0, 127, out=bv_tmp)
    zone_stars['bvind'] = bv_tmp.astype(np.uint8)

    zone_stars['hip'] = np.zeros(dim, dtype=np.uint32)

    return zone_stars


def _convert_stars3_v3_helper(stars3_v3):
    dim = len(stars3_v3)

    x0_arr = (
            stars3_v3['x0'][:, 0].astype(np.uint32)
            | (stars3_v3['x0'][:, 1].astype(np.uint32) << 8)
            | (stars3_v3['x0'][:, 2].astype(np.uint32) << 16)
    )
    x1_arr = (
            stars3_v3['x1'][:, 0].astype(np.uint32)
            | (stars3_v3['x1'][:, 1].astype(np.uint32) << 8)
            | (stars3_v3['x1'][:, 2].astype(np.uint32) << 16)
    )

    ra_rad = x0_arr * 100.0 * MAS2RAD
    dec_rad = (x1_arr - (90.0 * 36000.0)) * 100.0 * MAS2RAD

    x, y, z = np_sphere_to_rect(ra_rad, dec_rad)

    vmag_milli = stars3_v3['vmag'] * 20 + 16000
    float_mag = vmag_milli / 1000.0

    bv_tmp = (stars3_v3['b_v'] * 0.025 - 1 + 0.5) * 31.75
    np.clip(bv_tmp, 0, 127, out=bv_tmp)
    bv_index = bv_tmp.astype(np.uint8)

    zone_stars = np.empty(dim, dtype=RECT_ZONE_STARDATA_DT)

    zone_stars['x'] = x
    zone_stars['y'] = y
    zone_stars['z'] = z
    zone_stars['mag'] = float_mag
    zone_stars['bvind'] = bv_index
    zone_stars['hip'] = np.zeros(dim, dtype=np.uint32)

    return zone_stars


class GeodesicGaiaBinFileReader(GeodesicBinFileReader):
    def __init__(self):
        super().__init__(True)

    def get_star_rec_size(self):
        if self.file_type == 2:
            return 16   # Star2
        if self.file_type == 1:
            return 32   # Star1
        return 48       # Star0


class GeodesicStarGaiaCatalogComponent:
    def __init__(self, file_name):
        self._data_reader = None
        self.file_name = file_name
        self._file_opened = False
        self._nr_of_zones = 0
        self._star_blocks = None
        self.star_position_scale = 0.0
        self.triangle_size = 0.0

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
        self._data_reader = GeodesicGaiaBinFileReader()
        self._data_reader.open_file(self.file_name)
        if not self._data_reader.file:
            print("Failed to open star catalog {}, disabling it.".format(self.file_name))
            return False
        try:
            self._data_reader.read_header()
        except Exception as e:
            print("Header read error for deep star catalog {}, disabling it!".format(self.file_name))
            return False

        self._nr_of_zones = GeodesicGrid.nr_of_zones(self._data_reader.level) + 1
        self._star_blocks = [None] * self._nr_of_zones
        self._file_opened = True
        return self._file_opened

    def init_triangle(self, index, c0, c1, c2):
        d1 = vector_length(vector_sub(c0, c1))
        d2 = vector_length(vector_sub(c1, c2))
        d3 = vector_length(vector_sub(c2, c0))
        dmax = max(d1, d2, d3)
        if dmax > self.triangle_size:
            self.triangle_size = dmax

    def _get_data_format(self):
        if self._data_reader.file_type == 0:
            return STAR1_GAIA_DT
        if self._data_reader.file_type == 1:
            return STAR2_GAIA_DT
        return STAR3_GAIA_DT

    def _convert_zone_stars(self, zone_stars):
        if self._data_reader.file_type == 0:
            return _convert_stars1_v3_helper(zone_stars)
        elif self._data_reader.file_type == 1:
            return _convert_stars2_v3_helper(zone_stars)
        else:
            return _convert_stars3_v3_helper(zone_stars)

    def load_static_stars(self):
        for zone in range(self._nr_of_zones):
            self.get_zone_stars(zone)

    def get_zone_stars(self, zone):
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
                    zone_stars.byteswap(inplace=True)

                zone_stars = self._convert_zone_stars(zone_stars)
            else:
                zone_stars = []

            self._star_blocks[zone] = zone_stars

        return zone_stars

    def free_mem(self):
        if not self._file_opened:
            return
        for i in range(len(self._star_blocks)):
            self._star_blocks[i] = None


class GeodesicStarGaiaCatalog():
    """
    Star catalog composed of GeodesicStarGaiaCatalogComponent. Each component represents one level of Geodesic tree.
    """
    # @profile
    def __init__(self, data_dir, extra_data_dir):
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

        self.search_result = GeodesicSearchResult(self._max_geodesic_grid_level)

        if len(self._cat_components) > 0:
            self._cat_components[0].load_static_stars()

        # print("#################### Geodesic star catalog within {} s".format(str(time()-tm)), flush=True)

    def _load_gsc_component(self, data_dir, file_regex):
        files = glob.glob(os.path.join(data_dir, file_regex))
        if len(files) > 0:
            cat_comp = GeodesicStarGaiaCatalogComponent(files[0])
            if cat_comp.load_data_file():
                return cat_comp
        return None

    def _select_stars_from_zones(self, iterator, lev, lm_stars, field_rect3, cos_radius):
        stars = []
        zone = iterator.next()
        while zone != -1:
            zone_stars = self._cat_components[lev].get_zone_stars(zone)
            # print('Level={} Zone={} Len={}'.format(lev, zone, len(zone_stars)))
            selected_zone_stars = self._select_stars_from_zone(zone_stars, lm_stars, field_rect3, cos_radius)
            if selected_zone_stars is not None:
                stars.append(selected_zone_stars)
            zone = iterator.next()
        return stars

    def _select_stars_from_zone(self, zone_stars, lm_stars, field_rect3, cos_radius):
        if len(zone_stars) > 0:
            mag = zone_stars['mag']
            scal_dot = zone_stars['x'] * field_rect3[0] + zone_stars['y'] * field_rect3[1] + zone_stars['z'] * field_rect3[2]
            zone_stars = zone_stars[np.logical_and(mag <= lm_stars, scal_dot > cos_radius)]
            if len(zone_stars) > 0:
                return zone_stars
        return None

    @property
    def max_geodesic_grid_level(self):
        return self._max_geodesic_grid_level

    def init_triangle(self, lev, index, c0, c1, c2):
        self._cat_components[lev].init_triangle(index, c0, c1, c2)

    def select_stars(self, field_center, radius, lm_stars, precession_matrix):
        """
        Return an array containing of items [[ra, dec, mag], [ra, dec, mag]...]
        for all stars in the field centered around field center with given radius,
        field center and radius.
        """
        tmp_arr = []

        max_search_level = -1
        for cat_comp in self._cat_components:
            if cat_comp.level > 0 and cat_comp.mag_min_mag > lm_stars:
                break
            max_search_level += 1

        if max_search_level >= 0:
            field_rect3 = sphere_to_rect(field_center[0], field_center[1])

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
                    tmp_arr.extend(stars)

                # print('Border iterator')
                border_iterator = GeodesicSearchBorderIterator(self.search_result, lev)
                stars = self._select_stars_from_zones(border_iterator, lev, lm_stars, field_rect3, cos_radius)
                if len(stars) > 0:
                    tmp_arr.extend(stars)

                glob_zone_stars = self._cat_components[lev].get_zone_stars(GeodesicGrid.nr_of_zones(lev))
                sel_glob_zone_stars = self._select_stars_from_zone(glob_zone_stars, lm_stars, field_rect3, cos_radius)
                if sel_glob_zone_stars is not None:
                    tmp_arr.append(sel_glob_zone_stars)

        rect_stars = np.concatenate(tmp_arr, axis=0) if len(tmp_arr) > 0 else None

        if rect_stars is None or len(rect_stars) == 0:
            return None

        if precession_matrix is not None:
            mat_rect_stars = np.column_stack((rect_stars['x'], rect_stars['y'], rect_stars['z']))
            mat_rect_stars = np.matmul(mat_rect_stars, precession_matrix)
        else:
            mat_rect_stars = np.column_stack((rect_stars['x'], rect_stars['y'], rect_stars['z']))

        eq_stars = np.core.records.fromarrays(
            [
                mat_rect_stars[:, 0],  # x
                mat_rect_stars[:, 1],  # y
                mat_rect_stars[:, 2],  # z
                rect_stars['mag'],
                rect_stars['bvind'],
                rect_stars['hip'],
            ],
            dtype=D3_ZONE_STARDATA_DT)

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
    cat = GeodesicStarGaiaCatalog(data_dir, None)
    print("Loaded in : " + str(time()-tm) + "ms")
    print("Done")
