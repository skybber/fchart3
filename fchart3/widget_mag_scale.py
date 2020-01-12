#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
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

from numpy import *

LEGEND_MARGIN = 0.96

class WidgetMagnitudeScale:

    def __init__(self, sky_map_engine, field_radius_mm, legend_fontsize, stars_in_scale, lm_stars, star_border_linewidth, legend_linewidth):
        self.engine = sky_map_engine
        self.field_radius_mm = field_radius_mm
        self.margin = field_radius_mm*LEGEND_MARGIN
        self.legend_fontsize =legend_fontsize
        self.stars_in_scale = stars_in_scale
        self.lm_stars = lm_stars
        self.star_border_linewidth = star_border_linewidth
        self.legend_linewidth = legend_linewidth
        self.width = (self.field_radius_mm - self.margin) + 2.3 * self.legend_fontsize
        self.height = (self.field_radius_mm - self.margin) + (self.stars_in_scale - 0.2) * self.legend_fontsize

    def get_size(self):
        return (self.width, self.height)


    def draw(self, graphics, left, bottom):
        """
        Draws a vertical magnitude scale with at most \"stars_in_scale\" stars down
        to magnitude -1
        """
        fh = self.legend_fontsize
        mags_in_scale = int(self.lm_stars) - arange(self.stars_in_scale)

        legendx = -self.margin
        legendy = -self.margin + arange(self.stars_in_scale)*fh

        legendr = self.engine.magnitude_to_radius(mags_in_scale)
        graphics.set_linewidth(self.star_border_linewidth)

        for i in range(len(legendy)):
            if mags_in_scale[i] >= -1:
                self.engine.star(legendx, legendy[i], legendr[i], False)
                graphics.text_right(legendx + fh*0.75, legendy[i] - fh/3.0, str(mags_in_scale[i]))
        graphics.set_linewidth(self.legend_linewidth)
        graphics.line(left, bottom+self.height, left+self.width, bottom+self.height)
        graphics.line(left+self.width, bottom+self.height, left+self.width, bottom)

