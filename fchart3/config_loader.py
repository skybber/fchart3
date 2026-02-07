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

from .configuration import *
from .graphics import FontStyle

# NOTE: Keep comments in English (user preference).

FLOAT_ITEMS = [
    'fieldsize',
    'limit_stars',
    'limit_deepsky',

    # linewidths
    'constellation_linewidth',
    'constellation_border_linewidth',
    'open_cluster_linewidth',
    'galaxy_cluster_linewidth',
    'nebula_linewidth',
    'dso_linewidth',
    'legend_linewidth',
    'grid_linewidth',
    'horizon_linewidth',
    'highlight_linewidth',
    'milky_way_linewidth',
    'telrad_linewidth',
    'eyepiece_linewidth',

    # spacing / font sizes / scales
    'font_size',
    'legend_font_scale',
    'ext_label_font_scale',
    'bayer_label_font_scale',
    'flamsteed_label_font_scale',
    'outlined_dso_label_font_scale',
    'highlight_label_font_scale',
    'grid_font_scale',
    'cardinal_directions_font_scale',

    # misc numeric
    'star_mag_shift',

    # planetary radius scales
    'moon_r_scale',
    'mercury_r_scale',
    'venus_r_scale',
    'mars_r_scale',
    'jupiter_r_scale',
    'saturn_r_scale',
    'uranus_r_scale',
    'neptune_r_scale',
    'pluto_r_scale',

    # comet tail
    'comet_tail_length',
    'comet_tail_half_angle_deg',
    'comet_tail_side_scale',

]

# Integers in EngineConfiguration
INT_ITEMS = [
    'constellation_linespace',
    'picker_radius',
]

# Optional floats in EngineConfiguration
OPTIONAL_FLOAT_ITEMS = [
    'eyepiece_fov',
    'observer_lat_deg',
    'observer_lon_deg',
    'comet_els_expiration_hrs',
]

RGB_ITEMS = [
    # core colors
    'background_color',
    'draw_color',
    'label_color',

    # constellation / grid / map decorations
    'constellation_lines_color',
    'constellation_border_color',
    'constellation_hl_border_color',
    'grid_color',
    'horizon_color',
    'milky_way_color',
    'cardinal_directions_color',

    # deep-sky / highlight
    'dso_color',
    'highlight_color',
    'nebula_color',
    'galaxy_color',
    'star_cluster_color',
    'galaxy_cluster_color',

    # overlays / tools
    'telrad_color',
    'eyepiece_color',
    'picker_color',
    'comet_highlight_color',
    'comet_tail_color',

    # bodies
    'sun_color',
    'moon_color',
    'mercury_color',
    'venus_color',
    'earth_color',
    'mars_color',
    'jupiter_color',
    'saturn_color',
    'uranus_color',
    'neptune_color',
    'pluto_color',
]

BOOLEAN_ITEMS = [
    # rendering / modes
    'light_mode',
    'no_margin',
    'use_optimized_mw',
    'fov_telrad',

    # show toggles
    'show_star_labels',
    'show_star_circles',
    'show_star_mag',

    'show_flamsteed',
    'flamsteed_numbers_only',

    'show_mag_scale_legend',
    'show_map_scale_legend',
    'show_numeric_map_scale_legend',
    'show_orientation_legend',
    'show_dso_legend',
    'show_coords_legend',

    'show_field_border',
    'show_equatorial_grid',
    'show_horizontal_grid',

    'show_constellation_shapes',
    'show_constellation_borders',

    'show_deepsky',
    'show_dso_mag',
    'dso_dynamic_brightness',

    'show_simple_milky_way',
    'show_enhanced_milky_way_10k',
    'show_enhanced_milky_way_30k',
    'show_nebula_outlines',

    'show_solar_system',
    'show_horizon',
    'clip_to_horizon',

    'show_picker',

    # star rendering options
    'star_colors',
    'show_comet_tail',
]

STRING_ITEMS = [
    'font',
    'output_dir',
    'highlight_style',
]

# Optional strings in EngineConfiguration
OPTIONAL_STRING_ITEMS = [
    'stellarium_skyculture_json',
    'stellarium_landscape_dir',
]

FONT_STYLE_ITEMS = [
    'bayer_label_font_style',
    'flamsteed_label_font_style',
    'dso_label_font_style',
]

FONT_STYLE_CONVERSION = {
    'normal': FontStyle.NORMAL,
    'italic': FontStyle.ITALIC,
    'bold': FontStyle.BOLD,
}

TUPLE_FLOAT_ITEMS = [
    'enhanced_milky_way_fade',
]

# Enum-backed items
ENUM_ITEMS = [
    'coord_system',
    'widget_mode',
    'projection',
]


class ConfigurationLoader:
    def __init__(self, config_file):
        self.config_file = config_file

    def parse_color(self, color_str):
        """
        Parse color from 'RRGGBB' or '#RRGGBB' to (r, g, b) floats in [0..1].
        """
        s = color_str.strip()
        if s.startswith('#'):
            s = s[1:]
        if len(s) != 6:
            raise ValueError(f"Invalid color '{color_str}'. Expected RRGGBB or #RRGGBB.")
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        return r, g, b

    def parse_bool(self, value_str):
        """
        Parse common boolean strings.
        """
        v = value_str.strip().lower()
        return v in ('true', '1', 'yes', 'y', 'on')

    def parse_float_tuple(self, value_str):
        """
        Parse comma-separated floats into a tuple, e.g. "0.0,0.4,0.0,0.4,0.0,0.4".
        """
        parts = [p.strip() for p in value_str.split(',') if p.strip() != '']
        return tuple(float(p) for p in parts)

    def parse_optional_float(self, value_str):
        """
        Parse float or None (empty/'none'/'null').
        """
        v = value_str.strip().lower()
        if v in ('', 'none', 'null'):
            return None
        return float(value_str)

    def parse_optional_string(self, value_str):
        """
        Parse string or None (empty/'none'/'null').
        """
        v = value_str.strip()
        if v.lower() in ('', 'none', 'null'):
            return None
        return v

    def parse_int(self, value_str):
        """
        Parse integer. Accepts floats like "3.0" but stores as int.
        """
        v = value_str.strip()
        if v.lower() in ('', 'none', 'null'):
            raise ValueError("Expected int, got empty/none/null.")
        return int(float(v))

    def set_enum(self, config, key, value_str):
        """
        Set Enum value from string. Tries both raw and lowercased value.
        """
        raw = value_str.strip()
        low = raw.lower()

        enum_type = type(getattr(config, key))
        # Try direct (in case Enum expects exact casing)
        try:
            setattr(config, key, enum_type(raw))
            return
        except Exception:
            pass

        # Try lowercased (common for config files)
        try:
            setattr(config, key, enum_type(low))
            return
        except Exception:
            pass

        # If still not valid, ignore silently (keeps default).

    def load_config(self, config):
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if not hasattr(config, key):
                continue

            try:
                if key in FLOAT_ITEMS:
                    setattr(config, key, float(value))

                elif key in OPTIONAL_FLOAT_ITEMS:
                    setattr(config, key, self.parse_optional_float(value))

                elif key in INT_ITEMS:
                    setattr(config, key, self.parse_int(value))

                elif key in RGB_ITEMS:
                    setattr(config, key, self.parse_color(value))

                elif key in BOOLEAN_ITEMS:
                    setattr(config, key, self.parse_bool(value))

                elif key in FONT_STYLE_ITEMS:
                    setattr(config, key, FONT_STYLE_CONVERSION.get(value.strip().lower(), FontStyle.NORMAL))

                elif key in STRING_ITEMS:
                    setattr(config, key, value)

                elif key in OPTIONAL_STRING_ITEMS:
                    setattr(config, key, self.parse_optional_string(value))

                elif key in TUPLE_FLOAT_ITEMS:
                    setattr(config, key, self.parse_float_tuple(value))

                elif key in ENUM_ITEMS:
                    self.set_enum(config, key, value)

            except Exception:
                # Silently ignore invalid lines to keep loader tolerant.
                continue

        return True
