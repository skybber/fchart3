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

DEFAULT_CONSTELLATION_LINEWIDTH = 0.3
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_DSO_LINEWIDTH = 0.2
DEFAULT_LEGEND_LINEWIDTH = 0.2

DEFAULT_BACKGROUND_COLOR = (1.0, 1.0, 1.0)
DEFAULT_DRAW_COLOR = (0.0, 0.0, 0.0)
DEFAULT_LABEL_COLOR = (0.0, 0.0, 0.0)
DEFAULT_CONSTELLATION_LINES_COLOR = (0.2, 0.7, 1.0)
DEFAULT_CONSTELLATION_BORDER_COLOR = (0.95, 0.90, 0.1)
DEFAULT_DSO_COLOR = (1.0, 1.0, 1.0)
DEFAULT_FONT_SIZE = 2.6
DEFAULT_FONT = 'Arial' 

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
        self._mirror_x = False
        self._mirror_y = False
        self._background_color = DEFAULT_BACKGROUND_COLOR
        self._draw_color = DEFAULT_DRAW_COLOR
        self._label_color = DEFAULT_LABEL_COLOR
        self._constellation_lines_color = DEFAULT_CONSTELLATION_LINES_COLOR
        self._constellation_border_color = DEFAULT_CONSTELLATION_BORDER_COLOR
        self._dso_color = DEFAULT_DSO_COLOR
        self._nebula_color = DEFAULT_DSO_COLOR
        self._galaxy_color = DEFAULT_DSO_COLOR
        self._star_cluster_color = DEFAULT_DSO_COLOR
        self._constellation_linewidth = DEFAULT_CONSTELLATION_LINEWIDTH
        self._open_cluster_linewidth = DEFAULT_OPEN_CLUSTER_LINEWIDTH
        self._dso_linewidth = DEFAULT_DSO_LINEWIDTH
        self._legend_linewidth = DEFAULT_LEGEND_LINEWIDTH
        self._no_margin = False
        self._font = DEFAULT_FONT
        self._font_size = DEFAULT_FONT_SIZE

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
    def mirror_x(self):
        return self._mirror_x

    @mirror_x.setter
    def mirror_x(self, value):
        self._mirror_x = value

    @property
    def mirror_y(self):
        return self._mirror_y

    @mirror_y.setter
    def mirror_y(self, value):
        self._mirror_y = value
        
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
    def constellation_linewidth(self):
        return self._constellation_linewidth

    @constellation_linewidth.setter
    def constellation_linewidth(self, value):
        self._constellation_linewidth = value

    @property
    def open_cluster_linewidth(self):
        return self._open_cluster_linewidth

    @open_cluster_linewidth.setter
    def open_cluster_linewidth(self, value):
        self._open_cluster_linewidth = value

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
