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

FLOAT_ITEMS = ['constellation_linewidth', 'constellation_border_linewidth', 'nebula_linewidth',
               'open_cluster_linewidth', 'galaxy_cluster_linewidth', 'dso_linewidth', 'milky_way_linewidth',
               'legend_linewidth', 'grid_linewidth', 'constellation_linespace', 'font_size', 'legend_font_scale']

RGB_ITEMS = ['background_color', 'draw_color', 'label_color', 'constellation_lines_color', 'constellation_border_color',
             'constellation_hl_border_color', 'nebula_color', 'galaxy_color', 'star_cluster_color', 'galaxy_cluster_color',
             'milky_way_color', 'grid_color', 'telrad_color']

BOOLEAN_ITEMS = ['show_star_labels', 'show_flamsteed', 'show_mag_scale_legend', 'show_map_scale_legend',
                 'show_orientation_legend', 'show_dso_legend', 'show_coords_legend', 'show_field_border',
                 'show_equatorial_grid', 'show_constellation_shapes', 'show_constellation_borders',
                 'show_deepsky', 'show_simple_milky_way', 'show_enhanced_milky_way', 'show_nebula_outlines',
                 'star_colors', 'flamsteed_numbers_only']

STRING_ITEMS = ['font']

FONT_STYLE_ITEMS = ['bayer_label_font_style', 'flamsteed_label_font_style', 'dso_label_font_style']

FONT_STYLE_CONVERSION = { 'normal': FontStyle.NORMAL, 'italic': FontStyle.ITALIC, 'bold': FontStyle.BOLD }

class ConfigurationLoader:
    def __init__(self, config_file):
        self.config_file = config_file

    def parse_color(self, color_str):
        r = int(color_str[0:2], 16) / 255.0
        g = int(color_str[2:4], 16) / 255.0
        b = int(color_str[4:6], 16) / 255.0
        return r, g, b

    def parse_value(self, value_str):
        try:
            return float(value_str)
        except ValueError:
            return value_str

    def load_config(self, config):
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()

                if hasattr(config, key):
                    if key in FLOAT_ITEMS:
                        setattr(config, key, float(value))
                    elif key in RGB_ITEMS:
                        setattr(config, key, self.parse_color(value))
                    elif key in BOOLEAN_ITEMS:
                        setattr(config, key, value.lower() == 'true')
                    elif key in FONT_STYLE_ITEMS:
                        setattr(config, key, FONT_STYLE_CONVERSION.get(value, FontStyle.NORMAL))
                    elif key in STRING_ITEMS:
                        setattr(config, key, value)
        return True
