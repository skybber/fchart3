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

from .widget_base import WidgetBase
from .graphics_interface import DrawMode


class WidgetMapScale(WidgetBase):

    def __init__(self, sky_map_engine, alloc_space_spec, drawingscale, maxlength, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        WidgetBase.__init__(self, sky_map_engine=sky_map_engine, alloc_space_spec=alloc_space_spec)
        self.drawingscale = drawingscale
        self.maxlength = maxlength
        self.legend_fontsize = legend_fontsize
        self.legend_linewidth = legend_linewidth
        self.alloc_space_spec = alloc_space_spec
        self.color = color
        self.x, self.y = None, None
        self._initialize()

    def _initialize(self):
        # Determine a suitable scale ruler
        allowed_ruler = np.array([1, 5, 10, 30, 60, 120, 300.0, 600.0, 1200.0]) # arcminutes
        allowed_labels = ['1\'', '5\'', '10\'', '30\'', '1°', '2°', '5°', '10°', '20°']

        ruler_mm = allowed_ruler*np.pi/(180.0*60.0)*self.drawingscale
        self.ruler_label = ''
        self.ruler_length = 0.0

        for i in range(len(allowed_ruler)):
            if ruler_mm[-(i+1)] <= self.maxlength:
                self.ruler_label = allowed_labels[-(i+1)]
                self.ruler_length = ruler_mm[-(i+1)]
                break

        fh = self.legend_fontsize * 0.66
        self.width, self.height = self.ruler_length + 2*fh, 2.2 * self.legend_fontsize

    def draw(self, graphics, legend_only):
        fh = self.legend_fontsize * 0.66

        x = self.x + self.width - fh
        y = self.y - self.height + fh + fh/2

        graphics.set_solid_line()
        graphics.set_pen_rgb(self.color)
        graphics.set_linewidth(self.legend_linewidth)

        lw = graphics.gi_linewidth

        if legend_only and graphics.gi_background_rgb:
            graphics.save()
            graphics.set_fill_background()
            graphics.rectangle(self.x, self.y, self.width, self.height, DrawMode.FILL)
            graphics.restore()

        graphics.line(x, y, x - self.ruler_length, y)
        graphics.line(x - lw/2.0, y - 0.5*fh,
                      x - lw/2.0, y + 0.5*fh)
        graphics.line(x - self.ruler_length + lw/2.0, y - 0.5*fh,
                      x - self.ruler_length + lw/2.0, y + 0.5*fh)
        old_fontsize = graphics.gi_font_size
        graphics.set_font(graphics.gi_font, fh)
        graphics.text_centred(x - self.ruler_length/2.0, y + graphics.gi_font_size*2/3.0, self.ruler_label)

        graphics.set_font(graphics.gi_font, old_fontsize)

        self.draw_bounding_rect(graphics)
