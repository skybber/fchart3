#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2025 fchart3 authors
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

from dataclasses import dataclass, field
from typing import Optional, Tuple, Any
import numpy as np

from ..horizon_landscape import StellariumLandscape

Coord = Tuple[float, float]
Rect = Tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class RenderContext:
    gfx: Any
    mirroring_gfx: Any
    cfg: Any
    transf: Any
    drawing_width: float
    drawing_height: float
    min_radius: float
    scene_scale: float
    drawing_scale: float
    field_rect_mm: Rect
    clip_path: Any
    center_equatorial: Coord
    center_celestial: Coord
    field_radius: float
    field_size: float
    mirror_x: bool
    mirror_y: bool
    lm_stars: float
    lm_deepsky: float
    star_mag_r_shift: float
    used_catalogs: Any
    jd: Optional[float] = None
    precession_matrix: Optional[np.ndarray] = None
    showing_dsos: Any = None
    dso_hide_filter: Any = None
    dso_highlights: Any = None
    highlights: Any = None
    hl_constellation: Any = None
    extra_positions: Any = None
    solsys_bodies: Any = None
    planet_moons: Any = None
    trajectory: Any = None
    landscape: StellariumLandscape = None


@dataclass(slots=True)
class RenderState:
    label_potential: Any
    visible_objects_collector: Any
    picked_dso: Optional[Any] = None
    picked_star: Optional[Any] = None
    picked_planet_moon: Optional[Any] = None
    cache: dict = field(default_factory=dict)
