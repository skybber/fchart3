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

from .widget_base import WidgetBase
from .graphics_interface import DrawMode


class WidgetNumericMapScale(WidgetBase):

    def __init__(self, sky_map_engine, alloc_space_spec, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        super().__init__(sky_map_engine=sky_map_engine, alloc_space_spec=alloc_space_spec)
        self.legend_fontsize = legend_fontsize
        self.legend_linewidth = legend_linewidth
        self.alloc_space_spec = alloc_space_spec
        self.color = color
        self.x, self.y = None, None
        self.width, self.height = 6 * self.legend_fontsize, 2.2 * self.legend_fontsize

    def draw(self, graphics, fill_background, label):
        fh = self.legend_fontsize

        graphics.set_solid_line()
        graphics.set_pen_rgb(self.color)
        graphics.set_linewidth(0)

        if fill_background and graphics.gi_background_rgb:
            graphics.save()
            graphics.set_fill_background()
            graphics.rectangle(self.x, self.y, self.width, self.height, DrawMode.FILL)
            graphics.restore()

        old_fontsize = graphics.gi_font_size
        graphics.set_font(graphics.gi_font, fh)
        x = self.x + 0.8 * fh
        y = self.y - self.height + (self.height - 0.66*fh) / 2
        graphics.text_right(x, y, label)

        graphics.set_font(graphics.gi_font, old_fontsize)

        self.draw_bounding_rect(graphics)
