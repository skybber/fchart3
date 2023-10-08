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

from math import pi

from .graphics_interface import DrawMode


class MirroringGraphics:
    """
    A Graphics used for mirroring in X and Y axises
    """
    def __init__(self, graphics, mirror_x, mirror_y):
        self.graphics = graphics
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y

    def translate(self, dx, dy):
        self.graphics.translate(dx, dy)

    def rotate(self, angle):
        if self.mirror_x:
            angle = -angle + pi
        if self.mirror_y:
            angle = -angle
        self.graphics.rotate(angle)

    def line(self, x1, y1, x2, y2):
        self.graphics.line(x1, y1, x2, y2)

    def polyline(self, vertices):
        self.graphics.polyline(vertices)

    def circle(self, x, y, r, mode=DrawMode.BORDER):
        self.graphics.circle(x, y, r, mode)

    def ellipse(self, x, y, rlong, rshort, position_angle, mode=DrawMode.BORDER):
        if self.mirror_x:
            position_angle = -position_angle + pi
        if self.mirror_y:
            position_angle = -position_angle
        self.graphics.ellipse(x, y, rlong, rshort, position_angle, mode)

    def text(self, text):
        self.graphics.text(text)

    def text_right(self, x, y, text):
        self.graphics.text_right(x, y, text)

    def text_left(self, x, y, text):
        self.graphics.text_left(x, y, text)

    def text_centred(self, x, y, text):
        self.graphics.text_centred(x, y, text)

    def set_pen_rgb(self, pen_rgb):
        """
        Sets gi_pen_rgb. Derived classes should extend, not override this method.
        """
        self.graphics.set_pen_rgb(pen_rgb)

    def to_pixel(self, x, y):
        """
        Convert x,y to pixel
        """
        return self.graphics.to_pixel(x, y)
