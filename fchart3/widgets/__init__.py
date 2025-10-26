#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2024 fchart authors
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

from .widget_mag_scale import WidgetMagnitudeScale
from .widget_map_scale import WidgetMapScale
from .widget_numeric_map_scale import WidgetNumericMapScale
from .widget_orientation import WidgetOrientation
from .widget_coords import WidgetCoords
from .widget_dso_legend import WidgetDsoLegend
from .widget_telrad import WidgetTelrad
from .widget_eyepiece import WidgetEyepiece
from .widget_picker import WidgetPicker

__all__ = [k for k in globals() if not k.startswith("_")]
