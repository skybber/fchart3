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
from ..graphics import DrawMode


class WidgetNumericMapScale(WidgetBase):

    def __init__(self, engine, alloc_space_spec, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        super().__init__(engine=engine, alloc_space_spec=alloc_space_spec, legend_linewidth=legend_linewidth)
        self.legend_fontsize = legend_fontsize
        self.alloc_space_spec = alloc_space_spec
        self.color = color
        self.x, self.y = None, None
        self.width, self.height = 6 * self.legend_fontsize, 2.2 * self.legend_fontsize

    def draw(self, gfx, ctx, fill_background, label):
        if self.x is None or self.y is None:
            return
        fh = self.legend_fontsize

        gfx.set_solid_line()
        gfx.set_pen_rgb(self.color)
        gfx.set_linewidth(0)

        if fill_background and gfx.gi_background_rgb:
            gfx.save()
            gfx.set_fill_background()
            gfx.rectangle(self.x, self.y, self.width, self.height, DrawMode.FILL)
            gfx.restore()

        old_fontsize = gfx.gi_font_size
        gfx.set_font(gfx.gi_font, fh)
        x = self.x + 0.8 * fh
        y = self.y - self.height + (self.height - 0.66*fh) / 2
        gfx.text_right(x, y, label)

        gfx.set_font(gfx.gi_font, old_fontsize)

        self.draw_bounding_rect(gfx)
