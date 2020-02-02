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

DEFAULT_CONSTELLATION_LINEWIDTH = 0.5
DEFAULT_STAR_BORDER_LINEWIDTH = 0.06
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_DSO_LINEWIDTH = 0.2
DEFAULT_LEGEND_LINEWIDTH = 0.2

class EngineConfiguration:
    def __init__(self):
        self._show_dso_legend = False
        self._invert_colors = False
        self._mirror_x = False
        self._mirror_y = False
        self._constellation_linewidth = DEFAULT_CONSTELLATION_LINEWIDTH
        self._star_border_linewidth = DEFAULT_STAR_BORDER_LINEWIDTH
        self._open_cluster_linewidth = DEFAULT_OPEN_CLUSTER_LINEWIDTH
        self._dso_linewidth = DEFAULT_DSO_LINEWIDTH
        self._legend_linewidth = DEFAULT_LEGEND_LINEWIDTH
        self._night_mode = False

    @property
    def show_dso_legend(self):
        return self._show_dso_legend

    @show_dso_legend.setter
    def show_dso_legend(self, value):
        self._show_dso_legend = value

    @property
    def invert_colors(self):
        return self._invert_colors

    @invert_colors.setter
    def invert_colors(self, value):
        self._invert_colors = value

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
    def constellation_linewidth(self):
        return self._constellation_linewidth

    @constellation_linewidth.setter
    def constellation_linewidth(self, value):
        self._constellation_linewidth = value

    @property
    def star_border_linewidth(self):
        return self._star_border_linewidth

    @star_border_linewidth.setter
    def star_border_linewidth(self, value):
        self._star_border_linewidth = value

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
    def night_mode(self):
        return self._night_mode

    @night_mode.setter
    def night_mode(self, value):
        self._night_mode = value

