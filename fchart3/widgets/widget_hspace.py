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

from ..graphics import DrawMode


class WidgetHSpace:
    def __init__(self, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        self.legend_fontsize = legend_fontsize
        self.legend_linewidth = legend_linewidth
        self.color = color
        self.height = 2.2 * self.legend_fontsize

    def draw(self, gfx, left, right, bottom, fill_background):
        gfx.set_solid_line()
        gfx.set_pen_rgb(self.color)
        gfx.set_linewidth(self.legend_linewidth)

        if fill_background and gfx.gi_background_rgb:
            gfx.save()
            gfx.set_fill_background()
            gfx.rectangle(left, bottom+self.height, right-left, self.height, DrawMode.FILL)
            gfx.restore()

        gfx.line(left, bottom+self.height, right, bottom+self.height)
