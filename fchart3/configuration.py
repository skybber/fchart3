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

from .graphics import FontStyle

from enum import Enum

DEFAULT_OUTPUT_DIR = './'
DEFAULT_LIMIT_STARS = 12.0
DEFAULT_LIMIT_DEEPSKY = 12.0
DEFAULT_FIELDSIZE = 7.0

DEFAULT_CONSTELLATION_LINEWIDTH = 0.3
DEFAULT_CONSTELLATION_LINE_SPACE = 3
DEFAULT_CONSTELLATION_BORDER_LINEWIDTH = 0.2
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_GALAXY_CLUSTER_LINEWIDTH = 0.2
DEFAULT_NEBULA_LINEWIDTH = 0.3
DEFAULT_DSO_LINEWIDTH = 0.2
DEFAULT_LEGEND_LINEWIDTH = 0.2
DEFAULT_GRID_LINEWIDTH = 0.2
DEFAULT_HORIZONT_LINEWIDTH = 1.0
DEFAULT_HIGHLIGHT_LINEWIDTH = 0.3
DEFAULT_MILKY_WAY_LINEWIDTH = 0.2
DEFAULT_TELRAD_LINEWIDTH = 0.3
DEFAULT_PICKER_LINEWIDTH = 0.4
DEFAULT_EYEPIECE_LINEWIDTH = 0.3

DEFAULT_ENHANCED_MILKY_WAY_FADE = (0.0, 0.4, 0.0, 0.4, 0.0, 0.4)

DEFAULT_BACKGROUND_COLOR = (1.0, 1.0, 1.0)
DEFAULT_DRAW_COLOR = (0.0, 0.0, 0.0)
DEFAULT_LABEL_COLOR = (0.0, 0.0, 0.0)
DEFAULT_CONSTELLATION_LINES_COLOR = (0.2, 0.7, 1.0)
DEFAULT_CONSTELLATION_BORDER_COLOR = (0.95, 0.90, 0.1)
DEFAULT_CONSTELLATION_HL_BORDER_COLOR = (1.0, 0.95, 0.5)
DEFAULT_MILKY_WAY_COLOR = (0.1, 0.1, 0.1)
DEFAULT_DSO_COLOR = (1.0, 1.0, 1.0)
DEFAULT_DSO_HIGHLIGHT_COLOR = (0.1, 0.2, 0.4)
DEFAULT_GRID_COLOR = (0.25, 0.31, 0.375)
DEFAULT_HORIZONT_COLOR = (0.31, 0.31, 0.25)
DEFAULT_TELRAD_COLOR = (0.5, 0.0, 0.0)
DEFAULT_EYEPIECE_COLOR = (0.5, 0.3, 0.0)
DEFAULT_PICKER_COLOR = (0.5, 0.5, 0.0)
DEFAULT_FONT_SIZE = 2.6
DEFAULT_FONT = 'Arial'
DEFAULT_LEGEND_FONT_SCALE = 1.75
DEFAULT_EXT_LABEL_FONT_SCALE = 1.2
DEFAULT_BAYER_LABEL_FONT_SCALE = 1.2
DEFAULT_FLAMSTEED_LABEL_FONT_SCALE = 0.9
DEFAULT_OUTLINED_DSO_LABEL_FONT_SCALE = 1.1
DEFAULT_HIGHLIGHT_LABEL_FONT_SCALE = 1.0
DEFAULT_GRID_FONT_SCALE = 1.1
DEFAULT_CARDINAL_DIRECTIONS_FONT_SCALE = 1.3
DEFAULT_CARDINAL_DIRECTIONS_COLOR = (0.8, 0.2, 0.102)

DEFAULT_MERCURY_COLOR = (0.5, 0.5, 0.5)
DEFAULT_VENUS_COLOR   = (0.9, 0.8, 0.6)
DEFAULT_EARTH_COLOR   = (0.2, 0.6, 1.0)
DEFAULT_MARS_COLOR    = (0.8, 0.4, 0.1)
DEFAULT_JUPITER_COLOR = (0.9, 0.6, 0.5)
DEFAULT_SATURN_COLOR  = (0.9, 0.8, 0.5)
DEFAULT_URANUS_COLOR  = (0.6, 0.8, 1.0)
DEFAULT_NEPTUNE_COLOR = (0.3, 0.5, 0.9)
DEFAULT_PLUTO_COLOR   = (0.7, 0.6, 0.5)
DEFAULT_SUN_COLOR     = (1.0, 1.0, 0.0)
DEFAULT_MOON_COLOR    = (0.8, 0.8, 0.8)

DEFAULT_MOON_R_SCALE    = 1
DEFAULT_MERCURY_R_SCALE = 1.0
DEFAULT_VENUS_R_SCALE   = 1.0
DEFAULT_MARS_R_SCALE    = 1.0
DEFAULT_JUPITER_R_SCALE = 1.0
DEFAULT_SATURN_R_SCALE  = 1.0
DEFAULT_URANUS_R_SCALE  = 0.6
DEFAULT_NEPTUNE_R_SCALE = 0.6
DEFAULT_PLUTO_R_SCALE   = 0.6


class WidgetMode(Enum):
    NORMAL = 1
    WIDGET_ONLY = 2
    ALLOC_SPACE_ONLY = 3


class CoordSystem(Enum):
    EQUATORIAL = "equatorial"
    HORIZONTAL = "horizontal"


class EngineConfiguration:
    def __init__(self):
        self._fieldsize = DEFAULT_FIELDSIZE
        self._limit_stars = DEFAULT_LIMIT_STARS
        self._limit_deepsky = DEFAULT_LIMIT_DEEPSKY
        self._output_dir = DEFAULT_OUTPUT_DIR
        self._background_color = DEFAULT_BACKGROUND_COLOR
        self._bayer_label_font_scale = DEFAULT_BAYER_LABEL_FONT_SCALE
        self._bayer_label_font_style = FontStyle.NORMAL
        self._cardinal_directions_color = DEFAULT_CARDINAL_DIRECTIONS_COLOR
        self._cardinal_directions_font_scale = DEFAULT_CARDINAL_DIRECTIONS_FONT_SCALE
        self._constellation_border_color = DEFAULT_CONSTELLATION_BORDER_COLOR
        self._constellation_border_linewidth = DEFAULT_CONSTELLATION_BORDER_LINEWIDTH
        self._constellation_hl_border_color = DEFAULT_CONSTELLATION_HL_BORDER_COLOR
        self._constellation_lines_color = DEFAULT_CONSTELLATION_LINES_COLOR
        self._constellation_linespace = DEFAULT_CONSTELLATION_LINE_SPACE
        self._constellation_linewidth = DEFAULT_CONSTELLATION_LINEWIDTH
        self._draw_color = DEFAULT_DRAW_COLOR
        self._dso_color = DEFAULT_DSO_COLOR
        self._dso_dynamic_brightness = False
        self._dso_label_font_style = FontStyle.NORMAL
        self._dso_linewidth = DEFAULT_DSO_LINEWIDTH
        self._earth_color = DEFAULT_EARTH_COLOR
        self._enhanced_milky_way_fade = DEFAULT_ENHANCED_MILKY_WAY_FADE
        self._ext_label_font_scale = DEFAULT_EXT_LABEL_FONT_SCALE
        self._eyepiece_color = DEFAULT_EYEPIECE_COLOR
        self._eyepiece_fov = None
        self._eyepiece_linewidth = DEFAULT_EYEPIECE_LINEWIDTH
        self._flamsteed_label_font_scale = DEFAULT_FLAMSTEED_LABEL_FONT_SCALE
        self._flamsteed_label_font_style = FontStyle.NORMAL
        self._flamsteed_numbers_only = False
        self._font = DEFAULT_FONT
        self._font_size = DEFAULT_FONT_SIZE
        self._fov_telrad = False
        self._galaxy_cluster_color = DEFAULT_DSO_COLOR
        self._galaxy_cluster_linewidth = DEFAULT_GALAXY_CLUSTER_LINEWIDTH
        self._galaxy_color = DEFAULT_DSO_COLOR
        self._grid_color = DEFAULT_GRID_COLOR
        self._grid_linewidth = DEFAULT_GRID_LINEWIDTH
        self._highlight_color = DEFAULT_DSO_HIGHLIGHT_COLOR
        self._highlight_label_font_scale = DEFAULT_HIGHLIGHT_LABEL_FONT_SCALE
        self._grid_font_scale = DEFAULT_GRID_FONT_SCALE
        self._highlight_linewidth = DEFAULT_HIGHLIGHT_LINEWIDTH
        self._horizon_color = DEFAULT_HORIZONT_COLOR
        self._horizon_linewidth = DEFAULT_HORIZONT_LINEWIDTH
        self._jupiter_color = DEFAULT_JUPITER_COLOR
        self._jupiter_r_scale = DEFAULT_JUPITER_R_SCALE
        self._label_color = DEFAULT_LABEL_COLOR
        self._legend_font_scale = DEFAULT_LEGEND_FONT_SCALE
        self._legend_linewidth = DEFAULT_LEGEND_LINEWIDTH
        self._light_mode = False
        self._mars_color = DEFAULT_MARS_COLOR
        self._mars_r_scale = DEFAULT_MARS_R_SCALE
        self._mercury_color = DEFAULT_MERCURY_COLOR
        self._mercury_r_scale = DEFAULT_MERCURY_R_SCALE
        self._milky_way_color = DEFAULT_MILKY_WAY_COLOR
        self._milky_way_linewidth = DEFAULT_MILKY_WAY_LINEWIDTH
        self._moon_color = DEFAULT_MOON_COLOR
        self._moon_r_scale = DEFAULT_MOON_R_SCALE
        self._nebula_color = DEFAULT_DSO_COLOR
        self._nebula_linewidth = DEFAULT_NEBULA_LINEWIDTH
        self._neptune_color = DEFAULT_NEPTUNE_COLOR
        self._neptune_r_scale = DEFAULT_NEPTUNE_R_SCALE
        self._no_margin = False
        self._open_cluster_linewidth = DEFAULT_OPEN_CLUSTER_LINEWIDTH
        self._outlined_dso_label_font_scale = DEFAULT_OUTLINED_DSO_LABEL_FONT_SCALE
        self._picker_color = DEFAULT_PICKER_COLOR
        self._picker_linewidth = DEFAULT_PICKER_LINEWIDTH
        self._picker_radius = -1  # < 0 means picker is not active
        self._pluto_color = DEFAULT_PLUTO_COLOR
        self._pluto_r_scale = DEFAULT_PLUTO_R_SCALE
        self._saturn_color = DEFAULT_SATURN_COLOR
        self._saturn_r_scale = DEFAULT_SATURN_R_SCALE
        self._show_constellation_borders = True
        self._show_constellation_shapes = True
        self._show_coords_legend = False
        self._show_deepsky = True
        self._show_dso_legend = False
        self._show_dso_mag = False
        self._show_enhanced_milky_way_10k = False
        self._show_enhanced_milky_way_30k = False
        self._use_optimized_mw = False
        self._show_equatorial_grid = False
        self._show_horizontal_grid = False
        self._show_field_border = False
        self._show_flamsteed = True
        self._show_horizon = False
        self._show_mag_scale_legend = False
        self._show_map_scale_legend = False
        self._show_nebula_outlines = False
        self._show_numeric_map_scale_legend = False
        self._show_orientation_legend = False
        self._show_picker = False
        self._show_simple_milky_way = False
        self._show_star_circles = True
        self._show_star_labels = True
        self._show_star_mag = False
        self._show_solar_system = False
        self._star_cluster_color = DEFAULT_DSO_COLOR
        self._star_colors = False
        self._star_mag_shift = 0
        self._sun_color = DEFAULT_SUN_COLOR
        self._telrad_color = DEFAULT_TELRAD_COLOR
        self._telrad_linewidth = DEFAULT_TELRAD_LINEWIDTH
        self._uranus_color = DEFAULT_URANUS_COLOR
        self._uranus_r_scale = DEFAULT_URANUS_R_SCALE
        self._venus_color = DEFAULT_VENUS_COLOR
        self._venus_r_scale = DEFAULT_VENUS_R_SCALE
        self._widget_mode = WidgetMode.NORMAL
        self._observer_lat_deg = None
        self._observer_lon_deg = None
        self._coord_system = CoordSystem.EQUATORIAL
        self._stellarium_landscape_dir = None

    @ property
    def fieldsize(self):
        return self._fieldsize
    @ fieldsize.setter
    def fieldsize(self, value):
        self._fieldsize = value

    @ property
    def limit_stars(self):
        return self._limit_stars
    @ limit_stars.setter
    def limit_stars(self, value):
        self._limit_stars = value

    @ property
    def limit_deepsky(self):
        return self._limit_deepsky
    @ limit_deepsky.setter
    def limit_deepsky(self, value):
        self._limit_deepsky = value
    @ property
    def output_dir(self):
        return self._output_dir
    @ output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        self._background_color = value

    @property
    def bayer_label_font_scale(self):
        return self._bayer_label_font_scale

    @bayer_label_font_scale.setter
    def bayer_label_font_scale(self, value):
        self._bayer_label_font_scale = value

    @property
    def bayer_label_font_style(self):
        return self._bayer_label_font_style

    @bayer_label_font_style.setter
    def bayer_label_font_style(self, value):
        self._bayer_label_font_style = value

    @property
    def cardinal_directions_color(self):
        return self._cardinal_directions_color

    @cardinal_directions_color.setter
    def cardinal_directions_color(self, value):
        self._cardinal_directions_color = value

    @property
    def cardinal_directions_font_scale(self):
        return self._cardinal_directions_font_scale

    @cardinal_directions_font_scale.setter
    def cardinal_directions_font_scale(self, value):
        self._cardinal_directions_font_scale = value

    @property
    def constellation_border_color(self):
        return self._constellation_border_color

    @constellation_border_color.setter
    def constellation_border_color(self, value):
        self._constellation_border_color = value

    @property
    def constellation_border_linewidth(self):
        return self._constellation_border_linewidth

    @constellation_border_linewidth.setter
    def constellation_border_linewidth(self, value):
        self._constellation_border_linewidth = value

    @property
    def constellation_hl_border_color(self):
        return self._constellation_hl_border_color

    @constellation_hl_border_color.setter
    def constellation_hl_border_color(self, value):
        self._constellation_hl_border_color = value

    @property
    def constellation_lines_color(self):
        return self._constellation_lines_color

    @constellation_lines_color.setter
    def constellation_lines_color(self, value):
        self._constellation_lines_color = value

    @property
    def constellation_linespace(self):
        return self._constellation_linespace

    @constellation_linespace.setter
    def constellation_linespace(self, value):
        self._constellation_linespace = value

    @property
    def constellation_linewidth(self):
        return self._constellation_linewidth

    @constellation_linewidth.setter
    def constellation_linewidth(self, value):
        self._constellation_linewidth = value

    @property
    def draw_color(self):
        return self._draw_color

    @draw_color.setter
    def draw_color(self, value):
        self._draw_color = value

    @property
    def dso_color(self):
        return self._dso_color

    @dso_color.setter
    def dso_color(self, value):
        self._dso_color = value

    @property
    def dso_dynamic_brightness(self):
        return self._dso_dynamic_brightness

    @dso_dynamic_brightness.setter
    def dso_dynamic_brightness(self, value):
        self._dso_dynamic_brightness = value

    @property
    def dso_label_font_style(self):
        return self._dso_label_font_style

    @dso_label_font_style.setter
    def dso_label_font_style(self, value):
        self._dso_label_font_style = value

    @property
    def dso_linewidth(self):
        return self._dso_linewidth

    @dso_linewidth.setter
    def dso_linewidth(self, value):
        self._dso_linewidth = value

    @property
    def earth_color(self):
        return self._earth_color

    @earth_color.setter
    def earth_color(self, value):
        self._earth_color = value

    @property
    def enhanced_milky_way_fade(self):
        return self._enhanced_milky_way_fade

    @enhanced_milky_way_fade.setter
    def enhanced_milky_way_fade(self, value):
        self._enhanced_milky_way_fade = value

    @property
    def ext_label_font_scale(self):
        return self._ext_label_font_scale

    @ext_label_font_scale.setter
    def ext_label_font_scale(self, value):
        self._ext_label_font_scale = value

    @property
    def eyepiece_color(self):
        return self._eyepiece_color

    @eyepiece_color.setter
    def eyepiece_color(self, value):
        self._eyepiece_color = value

    @property
    def eyepiece_fov(self):
        return self._eyepiece_fov

    @eyepiece_fov.setter
    def eyepiece_fov(self, value):
        self._eyepiece_fov = value

    @property
    def eyepiece_linewidth(self):
        return self._eyepiece_linewidth

    @eyepiece_linewidth.setter
    def eyepiece_linewidth(self, value):
        self._eyepiece_linewidth = value

    @property
    def flamsteed_label_font_scale(self):
        return self._flamsteed_label_font_scale

    @flamsteed_label_font_scale.setter
    def flamsteed_label_font_scale(self, value):
        self._flamsteed_label_font_scale = value

    @property
    def flamsteed_label_font_style(self):
        return self._flamsteed_label_font_style

    @flamsteed_label_font_style.setter
    def flamsteed_label_font_style(self, value):
        self._flamsteed_label_font_style = value

    @property
    def flamsteed_numbers_only(self):
        return self._flamsteed_numbers_only

    @flamsteed_numbers_only.setter
    def flamsteed_numbers_only(self, value):
        self._flamsteed_numbers_only = value

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value

    @property
    def fov_telrad(self):
        return self._fov_telrad

    @fov_telrad.setter
    def fov_telrad(self, value):
        self._fov_telrad = value

    @property
    def galaxy_cluster_color(self):
        return self._galaxy_cluster_color

    @galaxy_cluster_color.setter
    def galaxy_cluster_color(self, value):
        self._galaxy_cluster_color = value

    @property
    def galaxy_cluster_linewidth(self):
        return self._galaxy_cluster_linewidth

    @galaxy_cluster_linewidth.setter
    def galaxy_cluster_linewidth(self, value):
        self._galaxy_cluster_linewidth = value

    @property
    def galaxy_color(self):
        return self._galaxy_color

    @galaxy_color.setter
    def galaxy_color(self, value):
        self._galaxy_color = value

    @property
    def grid_color(self):
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        self._grid_color = value

    @property
    def grid_linewidth(self):
        return self._grid_linewidth

    @grid_linewidth.setter
    def grid_linewidth(self, value):
        self._grid_linewidth = value

    @property
    def highlight_color(self):
        return self._highlight_color

    @highlight_color.setter
    def highlight_color(self, value):
        self._highlight_color = value

    @property
    def highlight_label_font_scale(self):
        return self._highlight_label_font_scale

    @highlight_label_font_scale.setter
    def highlight_label_font_scale(self, value):
        self._highlight_label_font_scale = value

    @property
    def grid_font_scale(self):
        return self._grid_font_scale

    @grid_font_scale.setter
    def grid_font_scale(self, value):
        self._grid_font_scale = value

    @property
    def highlight_linewidth(self):
        return self._highlight_linewidth

    @highlight_linewidth.setter
    def highlight_linewidth(self, value):
        self._highlight_linewidth = value

    @property
    def horizon_color(self):
        return self._horizon_color

    @horizon_color.setter
    def horizon_color(self, value):
        self._horizon_color = value

    @property
    def horizon_linewidth(self):
        return self._horizon_linewidth

    @horizon_linewidth.setter
    def horizon_linewidth(self, value):
        self._horizon_linewidth = value

    @property
    def jupiter_color(self):
        return self._jupiter_color

    @jupiter_color.setter
    def jupiter_color(self, value):
        self._jupiter_color = value

    @property
    def jupiter_r_scale(self):
        return self._jupiter_r_scale

    @jupiter_r_scale.setter
    def jupiter_r_scale(self, value):
        self._jupiter_r_scale = value

    @property
    def label_color(self):
        return self._label_color

    @label_color.setter
    def label_color(self, value):
        self._label_color = value

    @property
    def legend_font_scale(self):
        return self._legend_font_scale

    @legend_font_scale.setter
    def legend_font_scale(self, value):
        self._legend_font_scale = value

    @property
    def legend_linewidth(self):
        return self._legend_linewidth

    @legend_linewidth.setter
    def legend_linewidth(self, value):
        self._legend_linewidth = value

    @property
    def light_mode(self):
        return self._light_mode

    @light_mode.setter
    def light_mode(self, value):
        self._light_mode = value

    @property
    def mars_color(self):
        return self._mars_color

    @mars_color.setter
    def mars_color(self, value):
        self._mars_color = value

    @property
    def mars_r_scale(self):
        return self._mars_r_scale

    @mars_r_scale.setter
    def mars_r_scale(self, value):
        self._mars_r_scale = value

    @property
    def mercury_color(self):
        return self._mercury_color

    @mercury_color.setter
    def mercury_color(self, value):
        self._mercury_color = value

    @property
    def mercury_r_scale(self):
        return self._mercury_r_scale

    @mercury_r_scale.setter
    def mercury_r_scale(self, value):
        self._mercury_r_scale = value

    @property
    def milky_way_color(self):
        return self._milky_way_color

    @milky_way_color.setter
    def milky_way_color(self, value):
        self._milky_way_color = value

    @property
    def milky_way_linewidth(self):
        return self._milky_way_linewidth

    @milky_way_linewidth.setter
    def milky_way_linewidth(self, value):
        self._milky_way_linewidth = value

    @property
    def moon_color(self):
        return self._moon_color

    @moon_color.setter
    def moon_color(self, value):
        self._moon_color = value

    @property
    def moon_r_scale(self):
        return self._moon_r_scale

    @moon_r_scale.setter
    def moon_r_scale(self, value):
        self._moon_r_scale = value

    @property
    def nebula_color(self):
        return self._nebula_color

    @nebula_color.setter
    def nebula_color(self, value):
        self._nebula_color = value

    @property
    def nebula_linewidth(self):
        return self._nebula_linewidth

    @nebula_linewidth.setter
    def nebula_linewidth(self, value):
        self._nebula_linewidth = value

    @property
    def neptune_color(self):
        return self._neptune_color

    @neptune_color.setter
    def neptune_color(self, value):
        self._neptune_color = value

    @property
    def neptune_r_scale(self):
        return self._neptune_r_scale

    @neptune_r_scale.setter
    def neptune_r_scale(self, value):
        self._neptune_r_scale = value

    @property
    def no_margin(self):
        return self._no_margin

    @no_margin.setter
    def no_margin(self, value):
        self._no_margin = value

    @property
    def open_cluster_linewidth(self):
        return self._open_cluster_linewidth

    @open_cluster_linewidth.setter
    def open_cluster_linewidth(self, value):
        self._open_cluster_linewidth = value

    @property
    def outlined_dso_label_font_scale(self):
        return self._outlined_dso_label_font_scale

    @outlined_dso_label_font_scale.setter
    def outlined_dso_label_font_scale(self, value):
        self._outlined_dso_label_font_scale = value

    @property
    def picker_color(self):
        return self._picker_color

    @picker_color.setter
    def picker_color(self, value):
        self._picker_color = value

    @property
    def picker_linewidth(self):
        return self._picker_linewidth

    @picker_linewidth.setter
    def picker_linewidth(self, value):
        self._picker_linewidth = value

    @property
    def picker_radius(self):
        return self._picker_radius

    @picker_radius.setter
    def picker_radius(self, value):
        self._picker_radius = value

    @property
    def pluto_color(self):
        return self._pluto_color

    @pluto_color.setter
    def pluto_color(self, value):
        self._pluto_color = value

    @property
    def pluto_r_scale(self):
        return self._pluto_r_scale

    @pluto_r_scale.setter
    def pluto_r_scale(self, value):
        self._pluto_r_scale = value

    @property
    def saturn_color(self):
        return self._saturn_color

    @saturn_color.setter
    def saturn_color(self, value):
        self._saturn_color = value

    @property
    def saturn_r_scale(self):
        return self._saturn_r_scale

    @saturn_r_scale.setter
    def saturn_r_scale(self, value):
        self._saturn_r_scale = value

    @property
    def show_constellation_borders(self):
        return self._show_constellation_borders

    @show_constellation_borders.setter
    def show_constellation_borders(self, value):
        self._show_constellation_borders = value

    @property
    def show_constellation_shapes(self):
        return self._show_constellation_shapes

    @show_constellation_shapes.setter
    def show_constellation_shapes(self, value):
        self._show_constellation_shapes = value

    @property
    def show_coords_legend(self):
        return self._show_coords_legend

    @show_coords_legend.setter
    def show_coords_legend(self, value):
        self._show_coords_legend = value

    @property
    def show_deepsky(self):
        return self._show_deepsky

    @show_deepsky.setter
    def show_deepsky(self, value):
        self._show_deepsky = value

    @property
    def show_dso_legend(self):
        return self._show_dso_legend

    @show_dso_legend.setter
    def show_dso_legend(self, value):
        self._show_dso_legend = value

    @property
    def show_dso_mag(self):
        return self._show_dso_mag

    @show_dso_mag.setter
    def show_dso_mag(self, value):
        self._show_dso_mag = value

    @property
    def show_enhanced_milky_way_10k(self):
        return self._show_enhanced_milky_way_10k

    @show_enhanced_milky_way_10k.setter
    def show_enhanced_milky_way_10k(self, value):
        self._show_enhanced_milky_way_10k = value

    @property
    def show_enhanced_milky_way_30k(self):
        return self._show_enhanced_milky_way_30k

    @show_enhanced_milky_way_30k.setter
    def show_enhanced_milky_way_30k(self, value):
        self._show_enhanced_milky_way_30k = value

    @property
    def use_optimized_mw(self):
        return self._use_optimized_mw

    @use_optimized_mw.setter
    def use_optimized_mw(self, value):
        self._use_optimized_mw = value

    @property
    def show_equatorial_grid(self):
        return self._show_equatorial_grid

    @show_equatorial_grid.setter
    def show_equatorial_grid(self, value):
        self._show_equatorial_grid = value

    @property
    def show_horizontal_grid(self):
        return self._show_horizontal_grid

    @show_horizontal_grid.setter
    def show_horizontal_grid(self, value):
        self._show_horizontal_grid = value

    @property
    def show_field_border(self):
        return self._show_field_border

    @show_field_border.setter
    def show_field_border(self, value):
        self._show_field_border = value

    @property
    def show_flamsteed(self):
        return self._show_flamsteed

    @show_flamsteed.setter
    def show_flamsteed(self, value):
        self._show_flamsteed = value

    @property
    def show_horizon(self):
        return self._show_horizon

    @show_horizon.setter
    def show_horizon(self, value):
        self._show_horizon = value

    @property
    def show_mag_scale_legend(self):
        return self._show_mag_scale_legend

    @show_mag_scale_legend.setter
    def show_mag_scale_legend(self, value):
        self._show_mag_scale_legend = value

    @property
    def show_map_scale_legend(self):
        return self._show_map_scale_legend

    @show_map_scale_legend.setter
    def show_map_scale_legend(self, value):
        self._show_map_scale_legend = value

    @property
    def show_nebula_outlines(self):
        return self._show_nebula_outlines

    @show_nebula_outlines.setter
    def show_nebula_outlines(self, value):
        self._show_nebula_outlines = value

    @property
    def show_numeric_map_scale_legend(self):
        return self._show_numeric_map_scale_legend

    @show_numeric_map_scale_legend.setter
    def show_numeric_map_scale_legend(self, value):
        self._show_numeric_map_scale_legend = value

    @property
    def show_orientation_legend(self):
        return self._show_orientation_legend

    @show_orientation_legend.setter
    def show_orientation_legend(self, value):
        self._show_orientation_legend = value

    @property
    def show_picker(self):
        return self._show_picker

    @show_picker.setter
    def show_picker(self, value):
        self._show_picker = value

    @property
    def show_simple_milky_way(self):
        return self._show_simple_milky_way

    @show_simple_milky_way.setter
    def show_simple_milky_way(self, value):
        self._show_simple_milky_way = value

    @property
    def show_star_circles(self):
        return self._show_star_circles

    @show_star_circles.setter
    def show_star_circles(self, value):
        self._show_star_circles = value

    @property
    def show_star_labels(self):
        return self._show_star_labels

    @show_star_labels.setter
    def show_star_labels(self, value):
        self._show_star_labels = value

    @property
    def show_star_mag(self):
        return self._show_star_mag

    @show_star_mag.setter
    def show_star_mag(self, value):
        self._show_star_mag = value

    @property
    def show_solar_system(self):
        return self._show_solar_system

    @show_solar_system.setter
    def show_solar_system(self, value):
        self._show_solar_system = value

    @property
    def star_cluster_color(self):
        return self._star_cluster_color

    @star_cluster_color.setter
    def star_cluster_color(self, value):
        self._star_cluster_color = value

    @property
    def star_colors(self):
        return self._star_colors

    @star_colors.setter
    def star_colors(self, value):
        self._star_colors = value

    @property
    def star_mag_shift(self):
        return self._star_mag_shift

    @star_mag_shift.setter
    def star_mag_shift(self, value):
        self._star_mag_shift = value

    @property
    def sun_color(self):
        return self._sun_color

    @sun_color.setter
    def sun_color(self, value):
        self._sun_color = value

    @property
    def telrad_color(self):
        return self._telrad_color

    @telrad_color.setter
    def telrad_color(self, value):
        self._telrad_color = value

    @property
    def telrad_linewidth(self):
        return self._telrad_linewidth

    @telrad_linewidth.setter
    def telrad_linewidth(self, value):
        self._telrad_linewidth = value

    @property
    def uranus_color(self):
        return self._uranus_color

    @uranus_color.setter
    def uranus_color(self, value):
        self._uranus_color = value

    @property
    def uranus_r_scale(self):
        return self._uranus_r_scale

    @uranus_r_scale.setter
    def uranus_r_scale(self, value):
        self._uranus_r_scale = value

    @property
    def venus_color(self):
        return self._venus_color

    @venus_color.setter
    def venus_color(self, value):
        self._venus_color = value

    @property
    def venus_r_scale(self):
        return self._venus_r_scale

    @venus_r_scale.setter
    def venus_r_scale(self, value):
        self._venus_r_scale = value

    @property
    def widget_mode(self):
        return self._widget_mode

    @widget_mode.setter
    def widget_mode(self, value):
        self._widget_mode = value

    @property
    def observer_lat_deg(self):
        return self._observer_lat_deg

    @observer_lat_deg.setter
    def observer_lat_deg(self, value):
        self._observer_lat_deg = value

    @property
    def observer_lon_deg(self):
        return self._observer_lon_deg

    @observer_lon_deg.setter
    def observer_lon_deg(self, value):
        self._observer_lon_deg = value

    @property
    def coord_system(self):
        return self._coord_system

    @coord_system.setter
    def coord_system(self, value):
        self._coord_system = value

    @property
    def stellarium_landscape_dir(self):
        return self._stellarium_landscape_dir

    @stellarium_landscape_dir.setter
    def stellarium_landscape_dir(self, value):
        self._stellarium_landscape_dir = value
