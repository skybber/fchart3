from math import pi, sin, cos
import string

import cairo

from fchart.graphics_interface import INCH, DPI, DPMM, POINT, GraphicsInterface, paper_A
from fchart.fonts import *

class CairoDrawing(GraphicsInterface):

    def __init__(self, filename, width, height, font_metrics):
        """
        width (horizontal) and height (vertical) in mm
        font_metrics is an object of type fonts.FontMetrics
        """
        GraphicsInterface.__init__(self, width, height)

        self.surface = None
        self.context = None
        self.font_metrics = font_metrics
        self.set_filename(filename)
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)


    def new(self):
        self.surface = cairo.PDFSurface(self.gi_filename, 595, 842) # A4, in points
        self.surface.set_device_scale(DPMM, DPMM)
        self.surface.set_device_offset(self.gi_origin_x*DPMM + (210-self.gi_width)*DPMM/2, self.gi_origin_y*DPMM + 20)
        self.context = cairo.Context(self.surface)
        self.set_font('Times-Roman', 12*POINT)
        self.set_linewidth(10)

    def save(self):
        GraphicsInterface.save(self)
        self.context.save()

    def restore(self):
        GraphicsInterface.restore(self)
        self.context.restore()

    def set_font(self, font='Times-Roman', fontsize=12*POINT):
        GraphicsInterface.set_font(self, font, fontsize)
        self.context.set_font_size(self.gi_fontsize)
        self.context.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self,linewidth)
        self.context.set_line_width(linewidth)


    def set_pen_gray(self, whiteness):
        GraphicsInterface.set_pen_gray(self, whiteness)


    def set_fill_gray(self, whiteness):
        GraphicsInterface.set_fill_gray(self, whiteness)


    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)


    def set_dashed_line(self, on, off, start=0.0):
        GraphicsInterface.set_dashed_line(self, on, off, start)


    def line(self, x1,y1,x2,y2):
        self.context.set_source_rgb(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2])
        self.context.move_to(x1,-y1)
        self.context.line_to(x2,-y2)
        self.context.set_dash(self.gi_dash_style[0], self.gi_dash_style[1])
        self.context.stroke()


    def circle(self, x,y,r, mode='P'):
        """
        Draw a circle with centre at (x,y) and radius r. 'mode'
        determines how it  is drawn:
        'P': only draw border with pen
        'F': only fill interior
        'PF': fill interior with fill gray value and draw border with
        pen gray value
        """
        self.moveto(x+r, y)
        self.context.arc(x, -y, r, 0, 2.0*pi)
        if mode == 'P':
            self.context.set_source_rgb(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2])
            self.context.set_dash(self.gi_dash_style[0], self.gi_dash_style[1])
            self.context.stroke()
        elif mode == 'F':
            self.context.set_source_rgb(self.gi_fill_gray,self.gi_fill_gray,self.gi_fill_gray)
            self.context.fill()
        else:
            self.context.set_source_rgb(self.gi_fill_gray,self.gi_fill_gray,self.gi_fill_gray)
            self.context.fill_preserve()
            self.context.set_source_rgb(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2])
            self.context.stroke()


    def ellipse(self,x,y,rlong,rshort, posangle, mode='P'):
        """
        Draw an ellipse with centre at (x,y) and long radius rlong and
        short radius rshort. position_angle is the angle between the
        long axis and the positive x-axis in radians. 'mode'
        determines how it is drawn:
        'P': only draw border with pen
        'F': only fill interior
        'PF': fill interior with fill gray value and draw border with
        pen gray value
        """
        self.context.save()
        scale = rshort/rlong
        self.context.translate(x, -y)
        self.context.rotate(-posangle)
        self.context.scale(1, scale)
        self.moveto(rlong, 0)
        self.context.arc(0, 0, rlong, 0, 2.0*pi)
        self.context.restore()
        if mode == 'P':
            self.context.set_source_rgb(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2])
            self.context.set_dash(self.gi_dash_style[0], self.gi_dash_style[1])
            self.context.stroke()
        elif mode == 'F':
            self.context.set_source_rgb(self.gi_fill_gray,self.gi_fill_gray,self.gi_fill_gray)
            self.context.fill()
        else:
            self.context.set_source_rgb(self.gi_fill_gray,self.gi_fill_gray,self.gi_fill_gray)
            self.context.fill_preserve()
            self.context.set_source_rgb(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2])
            self.context.stroke()

    def text(self, text):
        self.context.show_text(text)

    def text_superscript(self, text):
        self.context.show_text(text)


    def text_right(self, x, y, text):
        self.moveto(x, y)
        self.context.set_source_rgb(0, 0, 0)
        self.context.show_text(text)


    def text_left(self, x, y, text):
        xbearing, ybearing, width, height, dx, dy = self.context.text_extents(text)
        self.moveto(x-width, y)
        self.context.set_source_rgb(0, 0, 0)
        self.context.show_text(text)


    def text_centred(self, x, y, text):
        xbearing, ybearing, width, height, dx, dy = self.context.text_extents(text)
        self.moveto(x-width/2, y - height/2)
        self.context.set_source_rgb(0, 0, 0)
        self.context.show_text(text)


    def moveto(self, x, y):
        self.context.move_to(x,-y)


    def translate(self, dx, dy):
        self.context.translate(dx, -dy)
        pass


    def rotate(self, angle):
        self.context.rotate(-angle)
        pass


    def clip_path(self, path):
        (x,y) = path[0]
        self.context.move_to(x,-y)
        for (x,y) in path[1:]:
            self.context.line_to(x,-y)
        self.context.close_path()
        self.context.clip()

    def clip_circle(self, x, y, r):
        self.context.arc(-x, -y, r, 0, 2.0*pi)
        self.context.clip()

    def reset_clip(self):
        self.context.reset_clip()


    def finish(self):
        self.surface.show_page()

