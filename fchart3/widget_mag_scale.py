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


class WidgetMagnitudeScale(WidgetBase):

    def __init__(self, sky_map_engine, alloc_space_spec, legend_fontsize, stars_in_scale, lm_stars, legend_linewidth, vertical=True, color=(0, 0, 0)):
        WidgetBase.__init__(self, sky_map_engine=sky_map_engine, alloc_space_spec=alloc_space_spec)
        self.legend_fontsize = legend_fontsize
        self.stars_in_scale = stars_in_scale
        self.lm_stars = lm_stars
        self.legend_linewidth = legend_linewidth
        self.alloc_space_spec = alloc_space_spec
        self.vertical = vertical
        self.color = color
        if vertical:
            if int(self.lm_stars) < 10:
                self.width = 2.2 * self.legend_fontsize
            else:
                self.width = 2.7 * self.legend_fontsize
            self.height = (self.stars_in_scale + 0.6) * self.legend_fontsize
        else:
            self.height = 2.2 * self.legend_fontsize
            self.width = (self.stars_in_scale + 0.6) * self.legend_fontsize


    def draw(self, graphics, legend_only):
        fh = self.legend_fontsize
        mags_in_scale = int(self.lm_stars) - np.arange(self.stars_in_scale)

        graphics.set_solid_line()
        graphics.set_pen_rgb(self.color)
        graphics.set_linewidth(0)

        if legend_only and graphics.gi_background_rgb:
            graphics.save()
            graphics.set_fill_background()
            graphics.rectangle(self.x, self.y, self.width, self.height, DrawMode.FILL)
            graphics.restore()

        legendr = self.engine.magnitude_to_radius(mags_in_scale)

        if self.vertical:
            graphics.set_font(graphics.gi_font, fh * 0.8)
            legendy = self.y - self.height + np.arange(self.stars_in_scale)*fh + 0.5*fh

            for i in range(len(legendy)):
                self.engine.no_mirror_star(self.x+0.6*fh, legendy[i] + 0.33 * fh, legendr[i])
                graphics.text_right(self.x+1.2*fh, legendy[i], str(mags_in_scale[i]))
        else:
            graphics.set_font(graphics.gi_font, fh * 0.66)
            legendx = self.x + np.arange(self.stars_in_scale)*fh + 0.5*fh
            for i in range(self.stars_in_scale):
                self.engine.no_mirror_star(legendx[i] + 0.6 * fh, self.y-self.height + 0.66*fh, legendr[-i-1])
                graphics.text_centred(legendx[i] + 0.6 * fh, self.y-self.height + 1.6*fh, str(mags_in_scale[-i-1]))

        self.draw_bounding_rect(graphics)
