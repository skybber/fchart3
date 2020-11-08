#    fchart3 draws beautiful deepsky charts in vector formats
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

import numpy as np

from .graphics_interface import DrawMode

class WidgetMagnitudeScale:

    def __init__(self, sky_map_engine, legend_fontsize, stars_in_scale, lm_stars, legend_linewidth):
        self.engine = sky_map_engine
        self.legend_fontsize = legend_fontsize
        self.stars_in_scale = stars_in_scale
        self.lm_stars = lm_stars
        self.legend_linewidth = legend_linewidth
        if int(self.lm_stars) < 10:
            self.width = 2.2 * self.legend_fontsize
        else:
            self.width = 2.7 * self.legend_fontsize
        self.height = (self.stars_in_scale + 0.6) * self.legend_fontsize

    def get_size(self):
        return (self.width, self.height)


    def draw(self, graphics, left, bottom, legend_only):
        """
        Draws a vertical magnitude scale with at most \"stars_in_scale\" stars down
        to magnitude -1
        """
        fh = self.legend_fontsize
        mags_in_scale = int(self.lm_stars) - np.arange(self.stars_in_scale)

        legendy = bottom + np.arange(self.stars_in_scale)*fh + 0.5*fh
        legendr = self.engine.magnitude_to_radius(mags_in_scale)

        graphics.set_linewidth(0)

        if legend_only and graphics.gi_background_rgb:
            graphics.save()
            graphics.set_fill_background()
            graphics.rectangle(left, bottom+self.height, self.width, self.height, DrawMode.FILL)
            graphics.restore()

        for i in range(len(legendy)):
            if mags_in_scale[i] >= -1:
                self.engine.no_mirror_star(left+0.6*fh, legendy[i] + 0.33 * fh, legendr[i])
                graphics.text_right(left+1.2*fh, legendy[i], str(mags_in_scale[i]))
        graphics.set_linewidth(self.legend_linewidth)
        graphics.line(left, bottom+self.height, left+self.width, bottom+self.height)
        graphics.line(left+self.width, bottom+self.height, left+self.width, bottom)

