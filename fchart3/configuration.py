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

from enum import Enum
from dataclasses import dataclass
from typing import TypeAlias, Optional

from .projections import ProjectionType
from .graphics import FontStyle
from .base_types import Color

DEFAULT_OUTPUT_DIR = './'
DEFAULT_LIMIT_STARS = 12.0
DEFAULT_LIMIT_DEEPSKY = 12.0
DEFAULT_FIELDSIZE = 7.0

DEFAULT_CONSTELLATION_LINEWIDTH = 0.3
DEFAULT_CONSTELLATION_LINE_SPACE = 2.0
DEFAULT_CONSTELLATION_BORDER_LINEWIDTH = 0.2
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_GALAXY_CLUSTER_LINEWIDTH = 0.2
DEFAULT_NEBULA_LINEWIDTH = 0.1
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

DEFAULT_HIGHLIGHT_STYLE = 'cross'

class WidgetMode(Enum):
    NORMAL = 1
    WIDGET_ONLY = 2
    ALLOC_SPACE_ONLY = 3


class CoordSystem(Enum):
    EQUATORIAL = "equatorial"
    HORIZONTAL = "horizontal"

# - FadePattern is a sequence of floats (your default has 6 values).
FadePattern: TypeAlias = tuple[float, ...]


@dataclass(slots=True)
class EngineConfiguration:
    # Basic rendering / limits
    fieldsize: float = DEFAULT_FIELDSIZE
    limit_stars: float = DEFAULT_LIMIT_STARS
    limit_deepsky: float = DEFAULT_LIMIT_DEEPSKY
    output_dir: str = DEFAULT_OUTPUT_DIR

    # Colors
    background_color: Color = DEFAULT_BACKGROUND_COLOR
    draw_color: Color = DEFAULT_DRAW_COLOR
    label_color: Color = DEFAULT_LABEL_COLOR
    grid_color: Color = DEFAULT_GRID_COLOR
    horizon_color: Color = DEFAULT_HORIZONT_COLOR

    constellation_lines_color: Color = DEFAULT_CONSTELLATION_LINES_COLOR
    constellation_border_color: Color = DEFAULT_CONSTELLATION_BORDER_COLOR
    constellation_hl_border_color: Color = DEFAULT_CONSTELLATION_HL_BORDER_COLOR

    milky_way_color: Color = DEFAULT_MILKY_WAY_COLOR
    dso_color: Color = DEFAULT_DSO_COLOR
    highlight_color: Color = DEFAULT_DSO_HIGHLIGHT_COLOR

    telrad_color: Color = DEFAULT_TELRAD_COLOR
    eyepiece_color: Color = DEFAULT_EYEPIECE_COLOR
    picker_color: Color = DEFAULT_PICKER_COLOR
    cardinal_directions_color: Color = DEFAULT_CARDINAL_DIRECTIONS_COLOR

    # Fonts
    font: str = DEFAULT_FONT
    font_size: float = DEFAULT_FONT_SIZE

    legend_font_scale: float = DEFAULT_LEGEND_FONT_SCALE
    ext_label_font_scale: float = DEFAULT_EXT_LABEL_FONT_SCALE
    bayer_label_font_scale: float = DEFAULT_BAYER_LABEL_FONT_SCALE
    flamsteed_label_font_scale: float = DEFAULT_FLAMSTEED_LABEL_FONT_SCALE
    outlined_dso_label_font_scale: float = DEFAULT_OUTLINED_DSO_LABEL_FONT_SCALE
    highlight_label_font_scale: float = DEFAULT_HIGHLIGHT_LABEL_FONT_SCALE
    grid_font_scale: float = DEFAULT_GRID_FONT_SCALE
    cardinal_directions_font_scale: float = DEFAULT_CARDINAL_DIRECTIONS_FONT_SCALE

    bayer_label_font_style: FontStyle = FontStyle.NORMAL
    flamsteed_label_font_style: FontStyle = FontStyle.NORMAL
    dso_label_font_style: FontStyle = FontStyle.NORMAL

    # Line widths / spacing
    constellation_linewidth: float = DEFAULT_CONSTELLATION_LINEWIDTH
    constellation_linespace: int = DEFAULT_CONSTELLATION_LINE_SPACE
    constellation_border_linewidth: float = DEFAULT_CONSTELLATION_BORDER_LINEWIDTH

    open_cluster_linewidth: float = DEFAULT_OPEN_CLUSTER_LINEWIDTH
    galaxy_cluster_linewidth: float = DEFAULT_GALAXY_CLUSTER_LINEWIDTH
    nebula_linewidth: float = DEFAULT_NEBULA_LINEWIDTH
    dso_linewidth: float = DEFAULT_DSO_LINEWIDTH

    legend_linewidth: float = DEFAULT_LEGEND_LINEWIDTH
    grid_linewidth: float = DEFAULT_GRID_LINEWIDTH
    horizon_linewidth: float = DEFAULT_HORIZONT_LINEWIDTH
    highlight_linewidth: float = DEFAULT_HIGHLIGHT_LINEWIDTH
    highlight_style: str = DEFAULT_HIGHLIGHT_STYLE
    milky_way_linewidth: float = DEFAULT_MILKY_WAY_LINEWIDTH
    telrad_linewidth: float = DEFAULT_TELRAD_LINEWIDTH
    picker_linewidth: float = DEFAULT_PICKER_LINEWIDTH
    eyepiece_linewidth: float = DEFAULT_EYEPIECE_LINEWIDTH

    # Milky Way / DSO behavior
    enhanced_milky_way_fade: FadePattern = DEFAULT_ENHANCED_MILKY_WAY_FADE
    dso_dynamic_brightness: bool = False
    use_optimized_mw: bool = False

    # Eyepiece / picker
    eyepiece_fov: Optional[float] = None
    picker_radius: int = -1  # < 0 means picker is not active

    # Feature toggles
    light_mode: bool = False
    fov_telrad: bool = False
    flamsteed_numbers_only: bool = False
    no_margin: bool = False

    show_constellation_borders: bool = True
    show_constellation_shapes: bool = True
    show_coords_legend: bool = False
    show_deepsky: bool = True
    show_dso_legend: bool = False
    show_dso_mag: bool = False
    show_enhanced_milky_way_10k: bool = False
    show_enhanced_milky_way_30k: bool = False
    show_equatorial_grid: bool = False
    show_horizontal_grid: bool = False
    show_field_border: bool = False
    show_flamsteed: bool = True
    show_horizon: bool = False
    clip_to_horizon: bool = False
    show_mag_scale_legend: bool = False
    show_map_scale_legend: bool = False
    show_nebula_outlines: bool = True
    show_numeric_map_scale_legend: bool = False
    show_orientation_legend: bool = False
    show_picker: bool = False
    show_simple_milky_way: bool = False
    show_star_circles: bool = True
    show_star_labels: bool = True
    show_star_mag: bool = False
    show_solar_system: bool = False
    star_colors: bool = False

    # DSO category colors (you used DEFAULT_DSO_COLOR for these)
    galaxy_cluster_color: Color = DEFAULT_DSO_COLOR
    galaxy_color: Color = DEFAULT_DSO_COLOR
    nebula_color: Color = DEFAULT_DSO_COLOR
    star_cluster_color: Color = DEFAULT_DSO_COLOR

    # Star magnitude shift
    star_mag_shift: float = 0.0

    # Solar system colors + radius scales
    mercury_color: Color = DEFAULT_MERCURY_COLOR
    venus_color: Color = DEFAULT_VENUS_COLOR
    earth_color: Color = DEFAULT_EARTH_COLOR
    mars_color: Color = DEFAULT_MARS_COLOR
    jupiter_color: Color = DEFAULT_JUPITER_COLOR
    saturn_color: Color = DEFAULT_SATURN_COLOR
    uranus_color: Color = DEFAULT_URANUS_COLOR
    neptune_color: Color = DEFAULT_NEPTUNE_COLOR
    pluto_color: Color = DEFAULT_PLUTO_COLOR
    sun_color: Color = DEFAULT_SUN_COLOR
    moon_color: Color = DEFAULT_MOON_COLOR

    mercury_r_scale: float = DEFAULT_MERCURY_R_SCALE
    venus_r_scale: float = DEFAULT_VENUS_R_SCALE
    mars_r_scale: float = DEFAULT_MARS_R_SCALE
    jupiter_r_scale: float = DEFAULT_JUPITER_R_SCALE
    saturn_r_scale: float = DEFAULT_SATURN_R_SCALE
    uranus_r_scale: float = DEFAULT_URANUS_R_SCALE
    neptune_r_scale: float = DEFAULT_NEPTUNE_R_SCALE
    pluto_r_scale: float = DEFAULT_PLUTO_R_SCALE
    moon_r_scale: float = float(DEFAULT_MOON_R_SCALE)  # ensure float consistency

    # Modes / observer / coordinate system
    widget_mode: WidgetMode = WidgetMode.NORMAL
    observer_lat_deg: Optional[float] = None
    observer_lon_deg: Optional[float] = None
    coord_system: CoordSystem = CoordSystem.EQUATORIAL
    projection: ProjectionType = ProjectionType.STEREOGRAPHIC

    # Stellarium integration
    stellarium_skyculture_json: Optional[str] = None
    stellarium_landscape_dir: Optional[str] = None

    # Comet elements cache expiration in hours (0 or None = never expire)
    comet_els_expiration_hrs: Optional[float] = 0.0
