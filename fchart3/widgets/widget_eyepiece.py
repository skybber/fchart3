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

import numpy as np


class WidgetEyepiece:

    def __init__(self, drawingscale, fov, linewidth, color=(0.5, 0.3, 0)):
        self.drawingscale = drawingscale
        self.linewidth = linewidth
        self.fov = fov
        self.color = color

    def draw(self, gfx, ctx):
        r = self.fov*np.pi/(2.0*180.0)*self.drawingscale
        gfx.set_solid_line()
        gfx.set_pen_rgb(self.color)
        gfx.set_linewidth(self.linewidth)
        gfx.circle(0, 0, r)
