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

from .widget_base import WidgetBase


class WidgetOrientation(WidgetBase):

    def __init__(self, engine, alloc_space_spec, legend_fontsize, legend_linewidth, mirror_x, mirror_y, color=(0, 0, 0)):
        super().__init__(engine=engine, alloc_space_spec=alloc_space_spec, legend_linewidth=legend_linewidth)
        self.legend_fontsize = legend_fontsize
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y
        self.color = color

        self.width = self.legend_fontsize * 4.0
        self.height = self.legend_fontsize * 4.0

    def draw(self, gfx, ctx, left, top, fill_background):
        # Draw orientation indication
        dl = self.legend_fontsize
        x = left + dl + 0.35 * self.legend_fontsize
        y = top - dl - self.legend_fontsize * 1.3
        y_axis_caption = 'S' if self.mirror_y else 'N'
        gfx.text_centred(x, y + dl + 0.65*self.legend_fontsize, y_axis_caption)
        x_axis_caption = 'E' if self.mirror_x else 'W'
        gfx.text_right(x+dl+self.legend_fontsize/6.0, y-self.legend_fontsize/4.0, x_axis_caption)
        gfx.set_solid_line()
        gfx.set_pen_rgb(self.color)
        gfx.line(x-dl, y, x+dl, y)
        gfx.line(x, y-dl, x, y+dl)
        self.draw_bounding_rect(gfx)
