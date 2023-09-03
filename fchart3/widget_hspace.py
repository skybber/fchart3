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

import numpy as np

from .graphics_interface import DrawMode

class WidgetHSpace:
    def __init__(self, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        self.legend_fontsize = legend_fontsize
        self.legend_linewidth = legend_linewidth
        self.color = color
        self.height = 2.2 * self.legend_fontsize

    def draw(self, graphics, left, right, bottom, legend_only):
        graphics.set_solid_line()
        graphics.set_pen_rgb(self.color)
        graphics.set_linewidth(self.legend_linewidth)

        if legend_only and graphics.gi_background_rgb:
            graphics.save()
            graphics.set_fill_background()
            graphics.rectangle(left, bottom+self.height, right-left, self.height, DrawMode.FILL)
            graphics.restore()

        graphics.line(left, bottom+self.height, right, bottom+self.height)
