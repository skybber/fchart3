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

from enum import Enum

INCH = 25.4
DPI = 72.0
DPMM = DPI/INCH
POINT = 1.0/DPMM


class DrawMode(Enum):
    """
    BORDER - only draw border with pen
    FILL   - only fill interior
    BOTH   - fill interior with fill rgb value and draw border with gray
    """
    BORDER = 1
    FILL = 2
    BOTH = 3

class FontStyle(Enum):
    NORMAL = 0
    ITALIC = 1
    BOLD = 2
    ITALIC_BOLD = 3

def paper_A(n):
    """
    Returns (width, height) of ISO An paper in mm
    """
    w = (2.0**-n/2.0**0.5)**0.5
    h = w*2**0.5
    return (int(1000*w+0.5), int(1000*h+0.5))


class GraphicsInterface:
    """
    A GraphicsInterface has many data members and methods. The default unit is the mm

    gi_width       width of drawing in mm
    gi_height      height of drawing in mm
    gi_linewidth   width of the pen line in mm
    gi_font        name of the default font
    gi_font_size    height of the font in mm
    gi_origin_x    horizontal position of the user coordinate system relative
                   to the bottom left corner of the drawing.
    gi_origin_y    vertical position of the user coordinate system relative
                   to the bottom left corner of the drawing.
    gi_stack       graphics state stack.
    """
    def __init__(self, width, height):
        """
        width and height in mm
        """
        # length of point in mm
        self.gi_width = float(width)
        self.gi_height = float(height)
        self.gi_pen_rgb = (0.0, 0.0, 0.0)
        self.gi_fill_rgb = (0.0, 0.0, 0.0)
        self.gi_linewidth = 0.1
        self.gi_dash_style = None
        self.gi_origin_x = self.gi_width/2.0
        self.gi_origin_y = self.gi_height/2.0
        self.gi_font = 'Times-Roman'
        self.gi_font_style = 0
        self.set_point_size(POINT)
        self.pointsize = None
        self.gi_font_size = None
        self.gi_default_font_size = None

        self.gi_fobj = ''
        self.gi_stack = []
        self.gi_background_rgb = None

    def set_point_size(self, pointsize):
        self.pointsize = pointsize
        self.gi_font_size = 12*self.pointsize

    def get_default_fontsize(self):
        return 12*self.pointsize

    def save(self):
        """
        Save graphics state to stack. This method should be extended, not overriden.
        """
        self.gi_stack.append((self.gi_linewidth,
                              self.gi_dash_style,
                              self.gi_font,
                              self.gi_font_size,
                              self.gi_font_style,
                              self.gi_fill_rgb,
                              self.gi_pen_rgb))

    def restore(self):
        """
        Save graphics state to stack. This method should be extended, not overriden.
        """
        (self.gi_linewidth,
         self.gi_dash_style,
         self.gi_font,
         self.gi_font_size,
         self.gi_font_style,
         self.gi_fill_rgb,
         self.gi_pen_rgb) = self.gi_stack.pop()

    def new(self):
        """
        Erase all graphics, but keep graphics state (font, fontsize, linewidth&style , width, height, origin as they are.
        """
        pass

    def set_dimensions(self, width, height):
        """
        Sets gi_width and gi_height
        """
        self.gi_width  = width
        self.gi_height = height
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)

    def set_origin(self, origin_x, origin_y):
        """
        Sets gi_origin_x and gi_origin_y
        """
        self.gi_origin_x = origin_x
        if abs(self.gi_origin_x) < 1e-5:
            self.gi_origin_x = 0.0
        self.gi_origin_y = origin_y
        if abs(self.gi_origin_y) < 1e-5:
            self.gi_origin_y = 0.0

    def set_linewidth(self, linewidth):
        """
        Sets gi_linewidth. Derived classes should extend, not override this method.
        """
        self.gi_linewidth = linewidth

    def set_pen_rgb(self, pen_rgb):
        """
        Sets gi_pen_rgb. Derived classes should extend, not override this method.
        """
        self.gi_pen_rgb = pen_rgb

    def set_fill_rgb(self, fill_rgb):
        """
        Sets gi_fill_rgb. Derived classes should extend, not override this method.
        """
        self.gi_fill_rgb = fill_rgb

    def set_fill_background(self):
        """
        Sets gi_fill_rgb. to g_background
        """
        self.gi_fill_rgb = self.gi_background_rgb

    def set_solid_line(self):
        """
        From now on, all lines should be drawn solid. Extend this method.
        """
        self.gi_dash_style = None

    def set_dashed_line(self, on, off, start=0.0):
        """
        From now on, all lines should be drawn dashed. \"on\" mm on followed by
        \"off\" mm off. The dash pattern starts \"start\" mm from the beginning of
        the \"on\" pattern. Extend this method
        """
        self.gi_dash_style = ([on, off], start)

    def set_font(self, font='Times-Roman', font_size=None, font_style=FontStyle.NORMAL):
        """
        \"font\" is the fontname (a string)
        \"fontsize\" the fontsize in mm.
        \"font_style\" the fonr style

        This method must be extended by derived classes, not overriden. It sets
        gi_font and gi_font_size. In order to set a 12 point Helvetica font, use:
        GI.set_font('Helvetica', 12*POINT)
        """
        if font_size is None:
            font_size = self.get_default_fontsize()
        self.gi_font = font
        self.gi_font_size = font_size
        self.gi_font_style = font_style

    def set_default_font_size(self, default_font_size):
        self.gi_default_font_size = default_font_size

    def translate(self, dx, dy):
        """
        Shift origin of coordinate system (dx,dy) mm with respect to
        self.gi_origin_{x,y}
        """
        pass

    def rotate(self, angle):
        """
        Rotate coordinates angle radians around current origin.
        """
        pass

    def line(self, x1, y1, x2, y2):
        """
        Draw a line from (x1,y1) to (x2,y2) using the current pen gray value, linestyle
        and linewidth.
        """
        pass

    def rectangle(self, x, y, width, height, mode=DrawMode.BORDER):
        """
        Draw a rectangle with left upper corner in (x,y) and widt/height
        pen gray value
        """
        pass

    def circle(self, x, y, r, mode=DrawMode.BORDER):
        """
        Draw a circle with centre at (x,y) and radius r.
        """
        pass

    def polygon(self, vertices, mode=DrawMode.BORDER):
        """
        Draw a poligon with specified vertices
        """
        pass

    def polyline(self, vertices):
        """
        Draw a polyline with specified vertices
        """
        pass

    def ellipse(self, x, y, rlong, rshort, position_angle, mode=DrawMode.BORDER):
        """
        Draw an ellipse with centre at (x,y) and long radius rlong and
        short radius rshort. position_angle is the angle between the
        long axis and the positive x-axis in radians.
        """
        pass

    def text_right(self, x, y, text):
        """
        x, y is the bottom left corner of text
        """
        pass

    def text_left(self, x, y, text):
        """
        x, y is the bottom right corner of text
        """
        pass

    def text_centred(self, x, y, text):
        """
        Draw text centred at (x,y)
        """
        pass

    def text_width(self, text):
        """
        Text width in current font
        """
        pass

    def finish(self):
        """
        Finalize the drawing (Store to disk, memory, whatever).
        """
        pass

    def clip_path(self, path):
        """
        Clip path
        """
        pass

    def reset_clip(self):
        """
        Clip rectangle
        """
        pass

    def clear(self):
        """
        Fill by background color
        """
        pass

    def set_background_rgb(self, background_rgb):
        """
        Set if is transparent
        """
        self.gi_background_rgb = background_rgb

    def on_screen(self, x, y):
        """
        True if point is on screen
        """
        return True

    def to_pixel(self, x, y):
        """
        Convert x, y to pixel position
        """
        return x, y

    def antialias_on(self):
        pass

    def antialias_off(self):
        pass

    def cohen_sutherland_encode(self, x, y):
        code = 0
        if x < -self.gi_width/2:
            code |= 1
        if x > self.gi_width/2:
            code |= 2
        if y > self.gi_height/2:
            code |= 4
        if y < -self.gi_height/2:
            code |= 8
        return code
