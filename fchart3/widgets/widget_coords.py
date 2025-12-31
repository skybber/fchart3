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

import numpy as np

from .widget_base import WidgetBase


class WidgetCoords(WidgetBase):

    def __init__(self, sky_map_engine, alloc_space_spec, legend_fontsize, legend_linewidth, color=(0, 0, 0)):
        super().__init__(sky_map_engine=sky_map_engine, alloc_space_spec=alloc_space_spec, legend_linewidth=legend_linewidth)
        self.color = color
        text = "x" + self.get_text(23, 59, 59, "-", 89, 59, 59, )

        sky_map_engine.gfx.set_font(sky_map_engine.gfx.gi_font, legend_fontsize)
        w = sky_map_engine.gfx.text_width(text)
        self.width = w + legend_fontsize * 0.5
        self.height = legend_fontsize * 1.5

    def draw(self, gfx, ctx, ra, dec, fill_background):
        """
        left,bottom are coordinates of the lower left corner of the textbox
        """
        ra_h = int(ra*12/np.pi)
        ra_m = int((ra*12/np.pi -ra_h)*60)
        ra_s = int(((ra*12/np.pi -ra_h)*60 - ra_m)*60+0.5)
        if ra_s == 60:
            ra_m += 1
            ra_s = 0
        if ra_m == 60:
            ra_h += 1
            ra_m = 0
        if ra_h == 24:
            ra_h = 0

        dec_sign = '+'
        if dec < 0.0:
            dec_sign = '-'
        dec_d = int(abs(dec)*180/np.pi)
        dec_m = int((abs(dec)*180/np.pi-dec_d)*60)
        dec_s = int(((abs(dec)*180/np.pi-dec_d)*60 -dec_m)*60 + 0.5)

        if dec_s == 60:
            dec_m += 1
            dec_s = 0
        if dec_m == 60:
            dec_m = 0

        text = self.get_text(ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s)
        padding = gfx.gi_font_size * 0.35
        gfx.text_right(self.x + padding, self.y - self.height + padding, text)
        self.draw_bounding_rect(gfx)

    def get_text(self, ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s):
        language = self.engine.language
        text = str(ra_h).rjust(2) + language['h'] + str(ra_m) + language['m'] + str(ra_s) + language['s'] + ' ' + dec_sign + str(dec_d) + '°' + str(dec_m) + '\'' + str(dec_s) + '"'
        return text
