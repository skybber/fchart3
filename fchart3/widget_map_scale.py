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

class WidgetMapScale:

    def __init__(self, drawingwidth, drawingscale, maxlength, legend_fontsize, legend_linewidth):
        self.drawingwidth = drawingwidth
        self.drawingscale = drawingscale
        self.maxlength = maxlength
        self.legend_fontsize = legend_fontsize
        self.legend_linewidth = legend_linewidth
        self._initialize()

    def _initialize(self):
        # Determine a suitable scale ruler
        allowed_ruler = array([1, 5, 10, 30, 60, 120, 300.0]) # arcminutes
        allowed_labels = ['1\'', '5\'', '10\'', '30\'', '1°', '2°', '5°']

        ruler_mm = allowed_ruler*pi/(180.0*60.0)*self.drawingscale
        self.ruler_label = ''
        self.ruler_length = 0.0

        for i in range(len(allowed_ruler)):
            if ruler_mm[-(i+1)] <= self.maxlength:
                self.ruler_label = allowed_labels[-(i+1)]
                self.ruler_length = ruler_mm[-(i+1)]
                break

        fh = self.legend_fontsize * 0.5
        self.width, self.height = self.ruler_length + 2*fh, fh*3

    def get_size(self):
        return (self.width, self.height)


    def draw(self, graphics, right, bottom):
        """
        x,y are the coordinates of the leftmost point of the horizontal line.
        This is excluding the vertical end bars. maxlength is the maximum
        length of the ruler line excluding the endbars.
        """
        fh = self.legend_fontsize * 0.5

        x = right - fh
        y = bottom + fh + fh/2

        graphics.set_linewidth(self.legend_linewidth)

        lw = graphics.gi_linewidth

        graphics.line(x, y, x - self.ruler_length, y)
        graphics.line(x - lw/2.0, y - 0.01*self.drawingwidth,
                      x - lw/2.0, y + 0.01*self.drawingwidth)
        graphics.line(x - self.ruler_length + lw/2.0, y - 0.01*self.drawingwidth,
                      x - self.ruler_length + lw/2.0, y + 0.01*self.drawingwidth)
        old_fontsize = graphics.gi_fontsize
        graphics.set_font(graphics.gi_font, fh)
        graphics.text_centred(x - self.ruler_length/2.0, y + graphics.gi_fontsize*2/3.0, self.ruler_label)

        graphics.set_font(graphics.gi_font, old_fontsize)

        graphics.line(right-self.width, bottom+self.height, right, bottom+self.height)
        graphics.line(right-self.width, bottom+self.height, right-self.width, bottom)

