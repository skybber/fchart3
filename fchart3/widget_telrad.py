#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2021 fchart authors
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

class WidgetTelrad:

    def __init__(self, drawingscale, linewidth):
        self.drawingscale = drawingscale
        self.linewidth = linewidth

    def draw(self, graphics):
        graphics.save()
        for tr in [15, 60, 120]:
            r = tr*np.pi/(180.0*60.0)*self.drawingscale
            graphics.set_pen_rgb((0.5,0,0))
            graphics.set_linewidth(self.linewidth)
            graphics.circle(0,0,r)
        graphics.restore()
