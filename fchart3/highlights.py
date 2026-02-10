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

from dataclasses import dataclass
from typing import Optional, Tuple, Literal, List, Any, Sequence, Set

from .base_types import Color

DashPattern = Optional[Tuple[float, float]]  # e.g. (0.6, 1.2) or None
HighlightStyle = Literal['cross', 'circle', 'comet']
DsoHighlightStyle = Literal['cross', 'circle']

# Data row used by HighlightDefinition in your codebase:
# [ra, dec, dso_name, extra_label, payload]
HighlightRow = List[Any]  # keep tolerant, see strict version below


@dataclass(slots=True, eq=False)
class HighlightDefinition:
    """
    style        'cross' | 'circle'
    line_width   line width
    color        (r, g, b) floats in [0..1]
    data         sequence of highlight rows: [ra, dec, dso_name, extra_label, payload]
    size         symbol size multiplier (>0), 1.0 = default
    """
    style: HighlightStyle
    line_width: float
    color: Color
    data: Sequence[HighlightRow]
    size: float = 1.0


@dataclass(slots=True, eq=False)
class DsoHighlightDefinition:
    """
    dsos         set of DeepskyObject to be highlighted
    line_width   line width
    color        (r, g, b)
    dash         dash pattern (on, off) or None for solid
    style        'cross' | 'circle'
    size         symbol size multiplier (>0), 1.0 = default
    """
    dsos: Set["DeepskyObject"]
    line_width: float
    color: Color
    dash: DashPattern
    style: DsoHighlightStyle = 'circle'
    size: float = 1.0
