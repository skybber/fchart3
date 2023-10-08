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

from .graphics_interface import FontStyle


DEFAULT_CONSTELLATION_LINEWIDTH = 0.3
DEFAULT_CONSTELLATION_LINE_SPACE = 3
DEFAULT_CONSTELLATION_BORDER_LINEWIDTH = 0.2
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_GALAXY_CLUSTER_LINEWIDTH = 0.2
DEFAULT_NEBULA_LINEWIDTH = 0.3
DEFAULT_DSO_LINEWIDTH = 0.2
DEFAULT_LEGEND_LINEWIDTH = 0.2
DEFAULT_GRID_LINEWIDTH = 0.2
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


class EngineConfiguration:
    def __init__(self):
        self._legend_only = False
        self._show_star_labels = True
        self._show_flamsteed = True
        self._show_mag_scale_legend = False
        self._show_map_scale_legend = False
        self._show_orientation_legend = False
        self._show_dso_legend = False
        self._show_coords_legend = False
        self._show_field_border = False
        self._show_equatorial_grid = False
        self._show_constellation_shapes = True
        self._show_constellation_borders = True
        self._show_star_circles = True
        self._show_deepsky = True
        self._show_simple_milky_way = False
        self._show_enhanced_milky_way = False
        self._show_nebula_outlines = False
        self._show_picker = False
        self._show_dso_mag = False
        self._show_star_mag = False
        self._fov_telrad = False
        self._eyepiece_fov = None
        self._star_colors = False
        self._light_mode = False
        self._background_color = DEFAULT_BACKGROUND_COLOR
        self._draw_color = DEFAULT_DRAW_COLOR
        self._label_color = DEFAULT_LABEL_COLOR
        self._constellation_lines_color = DEFAULT_CONSTELLATION_LINES_COLOR
        self._constellation_border_color = DEFAULT_CONSTELLATION_BORDER_COLOR
        self._constellation_hl_border_color = DEFAULT_CONSTELLATION_HL_BORDER_COLOR
        self._dso_color = DEFAULT_DSO_COLOR
        self._nebula_color = DEFAULT_DSO_COLOR
        self._galaxy_color = DEFAULT_DSO_COLOR
        self._star_cluster_color = DEFAULT_DSO_COLOR
        self._galaxy_cluster_color = DEFAULT_DSO_COLOR
        self._grid_color = DEFAULT_GRID_COLOR
        self._constellation_linewidth = DEFAULT_CONSTELLATION_LINEWIDTH
        self._constellation_border_linewidth = DEFAULT_CONSTELLATION_BORDER_LINEWIDTH
        self._constellation_linespace = DEFAULT_CONSTELLATION_LINE_SPACE
        self._open_cluster_linewidth = DEFAULT_OPEN_CLUSTER_LINEWIDTH
        self._galaxy_cluster_linewidth = DEFAULT_GALAXY_CLUSTER_LINEWIDTH
        self._nebula_linewidth = DEFAULT_NEBULA_LINEWIDTH
        self._dso_linewidth = DEFAULT_DSO_LINEWIDTH
        self._legend_linewidth = DEFAULT_LEGEND_LINEWIDTH
        self._grid_linewidth = DEFAULT_GRID_LINEWIDTH
        self._no_margin = False
        self._font = DEFAULT_FONT
        self._font_size = DEFAULT_FONT_SIZE
        self._highlight_color = DEFAULT_DSO_HIGHLIGHT_COLOR
        self._highlight_linewidth = DEFAULT_HIGHLIGHT_LINEWIDTH
        self._dso_dynamic_brightness = False
        self._legend_font_scale = DEFAULT_LEGEND_FONT_SCALE
        self._milky_way_color = DEFAULT_MILKY_WAY_COLOR
        self._milky_way_linewidth = DEFAULT_MILKY_WAY_LINEWIDTH
        self._enhanced_milky_way_fade = DEFAULT_ENHANCED_MILKY_WAY_FADE
        self._telrad_linewidth = DEFAULT_TELRAD_LINEWIDTH
        self._telrad_color = DEFAULT_TELRAD_COLOR
        self._eyepiece_linewidth = DEFAULT_EYEPIECE_LINEWIDTH
        self._eyepiece_color = DEFAULT_EYEPIECE_COLOR
        self._picker_radius = -1  # < 0 means picker is not active
        self._picker_linewidth = DEFAULT_PICKER_LINEWIDTH
        self._picker_color = DEFAULT_PICKER_COLOR
        self._ext_label_font_scale = DEFAULT_EXT_LABEL_FONT_SCALE
        self._bayer_label_font_scale = DEFAULT_BAYER_LABEL_FONT_SCALE
        self._bayer_label_font_style = FontStyle.NORMAL
        self._flamsteed_label_font_scale = DEFAULT_FLAMSTEED_LABEL_FONT_SCALE
        self._flamsteed_label_font_style = FontStyle.NORMAL
        self._dso_label_font_style = FontStyle.NORMAL
        self._outlined_dso_label_font_scale = DEFAULT_OUTLINED_DSO_LABEL_FONT_SCALE
        self._highlight_label_font_scale = DEFAULT_HIGHLIGHT_LABEL_FONT_SCALE
        self._star_mag_shift = 0
        self._flamsteed_numbers_only = False

    @property
    def legend_only(self):
        return self._legend_only

    @legend_only.setter
    def legend_only(self, value):
        self._legend_only = value

    @property
    def show_star_labels(self):
        return self._show_star_labels

    @show_star_labels.setter
    def show_star_labels(self, value):
        self._show_star_labels = value

    @property
    def show_flamsteed(self):
        return self._show_flamsteed

    @show_flamsteed.setter
    def show_flamsteed(self, value):
        self._show_flamsteed = value

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
    def show_orientation_legend(self):
        return self._show_orientation_legend

    @show_orientation_legend.setter
    def show_orientation_legend(self, value):
        self._show_orientation_legend = value

    @property
    def show_dso_legend(self):
        return self._show_dso_legend

    @show_dso_legend.setter
    def show_dso_legend(self, value):
        self._show_dso_legend = value

    @property
    def show_coords_legend(self):
        return self._show_coords_legend

    @show_coords_legend.setter
    def show_coords_legend(self, value):
        self._show_coords_legend = value

    @property
    def show_field_border(self):
        return self._show_field_border

    @show_field_border.setter
    def show_field_border(self, value):
        self._show_field_border = value

    @property
    def show_equatorial_grid(self):
        return self._show_equatorial_grid

    @show_equatorial_grid.setter
    def show_equatorial_grid(self, value):
        self._show_equatorial_grid = value

    @property
    def show_constellation_shapes(self):
        return self._show_constellation_shapes

    @show_constellation_shapes.setter
    def show_constellation_shapes(self, value):
        self._show_constellation_shapes = value

    @property
    def show_constellation_borders(self):
        return self._show_constellation_borders

    @show_constellation_borders.setter
    def show_constellation_borders(self, value):
        self._show_constellation_borders = value

    @property
    def show_star_circles(self):
        return self._show_star_circles

    @show_star_circles.setter
    def show_star_circles(self, value):
        self._show_star_circles = value

    @property
    def show_deepsky(self):
        return self._show_deepsky

    @show_deepsky.setter
    def show_deepsky(self, value):
        self._show_deepsky = value
    @property
    def show_simple_milky_way(self):
        return self._show_simple_milky_way

    @show_simple_milky_way.setter
    def show_simple_milky_way(self, value):
        self._show_simple_milky_way = value

    @property
    def show_enhanced_milky_way(self):
        return self._show_enhanced_milky_way

    @show_enhanced_milky_way.setter
    def show_enhanced_milky_way(self, value):
        self._show_enhanced_milky_way = value

    @property
    def show_nebula_outlines(self):
        return self._show_nebula_outlines

    @show_nebula_outlines.setter
    def show_nebula_outlines(self, value):
        self._show_nebula_outlines = value

    @property
    def show_picker(self):
        return self._show_picker

    @show_picker.setter
    def show_picker(self, value):
        self._show_picker = value

    @property
    def show_dso_mag(self):
        return self._show_dso_mag

    @show_dso_mag.setter
    def show_dso_mag(self, value):
        self._show_dso_mag = value

    @property
    def show_star_mag(self):
        return self._show_star_mag

    @show_star_mag.setter
    def show_star_mag(self, value):
        self._show_star_mag = value

    @property
    def fov_telrad(self):
        return self._fov_telrad

    @fov_telrad.setter
    def fov_telrad(self, value):
        self._fov_telrad = value

    @property
    def eyepiece_fov(self):
        return self._eyepiece_fov

    @eyepiece_fov.setter
    def eyepiece_fov(self, value):
        self._eyepiece_fov = value

    @property
    def star_colors(self):
        return self._star_colors

    @star_colors.setter
    def star_colors(self, value):
        self._star_colors = value

    @property
    def light_mode(self):
        return self._light_mode

    @light_mode.setter
    def light_mode(self, value):
        self._light_mode = value

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        self._background_color = value

    @property
    def draw_color(self):
        return self._draw_color

    @draw_color.setter
    def draw_color(self, value):
        self._draw_color = value

    @property
    def label_color(self):
        return self._label_color

    @label_color.setter
    def label_color(self, value):
        self._label_color = value

    @property
    def constellation_lines_color(self):
        return self._constellation_lines_color

    @constellation_lines_color.setter
    def constellation_lines_color(self, value):
        self._constellation_lines_color = value

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
    def dso_color(self):
        return self._dso_color

    @dso_color.setter
    def dso_color(self, value):
        self._dso_color = value

    @property
    def nebula_color(self):
        return self._nebula_color

    @nebula_color.setter
    def nebula_color(self, value):
        self._nebula_color = value

    @property
    def galaxy_color(self):
        return self._galaxy_color

    @galaxy_color.setter
    def galaxy_color(self, value):
        self._galaxy_color = value

    @property
    def star_cluster_color(self):
        return self._star_cluster_color

    @star_cluster_color.setter
    def star_cluster_color(self, value):
        self._star_cluster_color = value

    @property
    def galaxy_cluster_color(self):
        return self._galaxy_cluster_color

    @galaxy_cluster_color.setter
    def galaxy_cluster_color(self, value):
        self._galaxy_cluster_color = value

    @property
    def grid_color(self):
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        self._grid_color = value

    @property
    def constellation_linewidth(self):
        return self._constellation_linewidth

    @constellation_linewidth.setter
    def constellation_linewidth(self, value):
        self._constellation_linewidth = value

    @property
    def constellation_linespace(self):
        return self._constellation_linespace

    @constellation_linespace.setter
    def constellation_linespace(self, value):
        self._constellation_linespace = value

    @property
    def open_cluster_linewidth(self):
        return self._open_cluster_linewidth

    @open_cluster_linewidth.setter
    def open_cluster_linewidth(self, value):
        self._open_cluster_linewidth = value

    @property
    def galaxy_cluster_linewidth(self):
        return self._galaxy_cluster_linewidth

    @galaxy_cluster_linewidth.setter
    def galaxy_cluster_linewidth(self, value):
        self._galaxy_cluster_linewidth = value

    @property
    def nebula_linewidth(self):
        return self._nebula_linewidth

    @nebula_linewidth.setter
    def nebula_linewidth(self, value):
        self._nebula_linewidth = value

    @property
    def dso_linewidth(self):
        return self._dso_linewidth

    @dso_linewidth.setter
    def dso_linewidth(self, value):
        self._dso_linewidth = value

    @property
    def legend_linewidth(self):
        return self._legend_linewidth

    @legend_linewidth.setter
    def legend_linewidth(self, value):
        self._legend_linewidth = value

    @property
    def grid_linewidth(self):
        return self._grid_linewidth

    @grid_linewidth.setter
    def grid_linewidth(self, value):
        self._grid_linewidth = value

    @property
    def no_margin(self):
        return self._no_margin

    @no_margin.setter
    def no_margin(self, value):
        self._no_margin = value

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
    def highlight_color(self):
        return self._highlight_color

    @highlight_color.setter
    def highlight_color(self, value):
        self._highlight_color = value

    @property
    def highlight_linewidth(self):
        return self._highlight_linewidth

    @highlight_linewidth.setter
    def highlight_linewidth(self, value):
        self._highlight_linewidth = value

    @property
    def dso_dynamic_brightness(self):
        return self._dso_dynamic_brightness

    @dso_dynamic_brightness.setter
    def dso_dynamic_brightness(self, value):
        self._dso_dynamic_brightness = value

    @property
    def legend_font_scale(self):
        return self._legend_font_scale

    @legend_font_scale.setter
    def legend_font_scale(self, value):
        self._legend_font_scale = value

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
    def enhanced_milky_way_fade(self):
        return self._enhanced_milky_way_fade

    @enhanced_milky_way_fade.setter
    def enhanced_milky_way_fade(self, value):
        self._enhanced_milky_way_fade = value

    @property
    def telrad_linewidth(self):
        return self._telrad_linewidth

    @telrad_linewidth.setter
    def telrad_linewidth(self, value):
        self._telrad_linewidth = value

    @property
    def telrad_color(self):
        return self._telrad_color

    @telrad_color.setter
    def telrad_color(self, value):
        self._telrad_color = value

    @property
    def eyepiece_linewidth(self):
        return self._eyepiece_linewidth

    @eyepiece_linewidth.setter
    def eyepiece_linewidth(self, value):
        self._eyepiece_linewidth = value

    @property
    def eyepiece_color(self):
        return self._eyepiece_color

    @eyepiece_color.setter
    def eyepiece_color(self, value):
        self._eyepiece_color = value

    @property
    def picker_radius(self):
        return self._picker_radius

    @picker_radius.setter
    def picker_radius(self, value):
        self._picker_radius = value

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
    def ext_label_font_scale(self):
        return self._ext_label_font_scale

    @ext_label_font_scale.setter
    def ext_label_font_scale(self, value):
        self._ext_label_font_scale = value

    @property
    def star_mag_shift(self):
        return self._star_mag_shift

    @star_mag_shift.setter
    def star_mag_shift(self, value):
        self._star_mag_shift = value

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
    def dso_label_font_style(self):
        return self._dso_label_font_style

    @dso_label_font_style.setter
    def dso_label_font_style(self, value):
        self._dso_label_font_style = value

    @property
    def outlined_dso_label_font_scale(self):
        return self._outlined_dso_label_font_scale

    @outlined_dso_label_font_scale.setter
    def outlined_dso_label_font_scale(self, value):
        self._outlined_dso_label_font_scale = value

    @property
    def highlight_label_font_scale(self):
        return self._highlight_label_font_scale

    @highlight_label_font_scale.setter
    def highlight_label_font_scale(self, value):
        self._highlight_label_font_scale = value

    @property
    def flamsteed_numbers_only(self):
        return self._flamsteed_numbers_only

    @flamsteed_numbers_only.setter
    def flamsteed_numbers_only(self, value):
        self._flamsteed_numbers_only = value
