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

import skia
from math import pi

from .graphics_interface import INCH, DPMM, POINT, GraphicsInterface, DrawMode, FontStyle

DPI_IMG = 100.0
DPMM_IMG = DPI_IMG/INCH
PONT_IMG = 1.0/DPMM_IMG

A4_WIDTH_POINTS = 594
A4_HEIGHT_POINTS = 842

SKIA_DEFAULT_FONT_SIZE = 12*POINT

class SkiaDrawing(GraphicsInterface):
    """
    A SkiaDrawing - implement Graphics interface using Skia-Python
    """

    def __init__(self, fobj, width, height, format='pdf', pixels=False, landscape=False, tolerance=None, jpg_quality=90):
        """
        :param fobj: file object
        :param width: width in mm
        :param height: height in mm
        :param format: format png/svg
        :param pixels: True if units of width/height are pixels
        :param landscape: True if orientation of page is landscape
        :param tolerance: Cairo context drawing tolerance, use it for speedup of graphics operations
        """
        GraphicsInterface.__init__(self, (width / DPMM_IMG if pixels else width) , (height / DPMM_IMG if pixels else height))

        self.fobj = fobj
        self.format = format
        self.landscape = landscape
        self.surface = None
        self.canvas = None
        self.sfc_width = None
        self.sfc_height = None
        self.tolerance = tolerance
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)

    def new(self):
        if self.format in ['png', 'jpg']:
            self.set_point_size(PONT_IMG)
            self.sfc_width = int(self.gi_width * DPMM_IMG)
            self.sfc_height = int(self.gi_height * DPMM_IMG)
            self.surface = skia.Surface(self.sfc_width, self.sfc_height)
            self.canvas = self.surface.getCanvas()
            self.canvas.scale(DPMM_IMG, DPMM_IMG)
            self.canvas.translate(self.gi_origin_x, self.gi_origin_y)
        else:
            if self.landscape:
                self.sfc_width = A4_HEIGHT_POINTS
                self.sfc_height = A4_WIDTH_POINTS
                self.document = skia.PDF.MakeDocument(self.fobj)
                self.canvas = document.page(self.sfc_width, self.sfc_height)
                self.canvas.scale(DPMM, DPMM)
                self.canvas.translate(self.gi_origin_x*DPMM + 15*DPMM, self.gi_origin_y*DPMM + (210-self.gi_height)*DPMM/2)
            else:
                self.sfc_width = A4_WIDTH_POINTS
                self.sfc_height = A4_HEIGHT_POINTS
                self.document = skia.PDF.MakeDocument(self.fobj)
                self.canvas = document.page(self.sfc_width, self.sfc_height)
                self.canvas.scale(DPMM, DPMM)
                self.canvas.translate(self.gi_origin_x*DPMM + (210-self.gi_width)*DPMM/2, self.gi_origin_y*DPMM + 15*DPMM)
        self.paint_default = skia.Paint(AntiAlias=True)
        self.paint_dash = skia.Paint(AntiAlias=True)
        self.paint_text = skia.Paint(AntiAlias=True)
        self.font_default = None

    def clear(self):
        return
        if self.gi_background_rgb:
            self.canvas.clear(skia.Color4f(self.gi_background_rgb[0], self.gi_background_rgb[1], self.gi_background_rgb[2], 1.0))

    def save(self):
        GraphicsInterface.save(self)
        self.canvas.save()

    def restore(self):
        GraphicsInterface.restore(self)
        self.canvas.restore()

    def set_font(self, font='Arial', font_size=SKIA_DEFAULT_FONT_SIZE, font_style=FontStyle.NORMAL):
        old_size = self.gi_font_size
        GraphicsInterface.set_font(self, font, font_size, font_style)
        if self.font_default is None or old_size != font_size:
            self.font_default = skia.Font(skia.Typeface('NotoSans'), font_size)

    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self, linewidth)
        self.paint_default.setStrokeWidth(linewidth)
        self.paint_dash.setStrokeWidth(linewidth)

    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)

    def set_dashed_line(self, on, off, start=0.0):
        GraphicsInterface.set_dashed_line(self, on, off, start)

    def line(self, x1,y1,x2,y2):
        paint = self._get_paint()
        paint.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        paint.setStyle(skia.Paint.kStroke_Style)
        self.canvas.drawLine((x1,-y1), (x2,-y2), paint)

    def rectangle(self,x,y,width,height, mode=DrawMode.BORDER):
        paint = self._get_paint()
        self._set_color_and_stroke_style(paint, mode)
        self.canvas.drawRect(skia.Rec(x, -y, width, height), paint)

    def circle(self, x, y, r, mode=DrawMode.BORDER):
        paint = self._get_paint()
        self._set_color_and_stroke_style(paint, mode)
        self.canvas.drawCircle(x, -y, r, paint)

    def polygon(self, vertices, mode=DrawMode.BORDER):
        path = skia.Path()
        path.moveTo(vertices[0][0], -vertices[0][1])
        for v in vertices[1:]:
            path.lineTo(v[0], -v[1])
        path.close()
        self._set_color_and_stroke_style(self.paint_default, mode)
        self.canvas.drawPath(path, self.paint_default)

    def polyline(self, vertices):
        path = skia.Path()
        path.moveTo(vertices[0][0], -vertices[0][1])
        for v in vertices[1:]:
            path.lineTo(v[0], -v[1])
        self._set_color_and_stroke_style(self.paint_default)
        self.canvas.drawPath(path, self.paint_default)

    def ellipse(self,x,y,rlong,rshort, posangle, mode=DrawMode.BORDER):
        self.canvas.save()
        paint = self._get_paint()
        paint.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        paint.setStyle(skia.Paint.kStroke_Style)
        rect = skia.Rect(-rlong, -rshort, rlong, rshort)
        self.canvas.translate(x, -y)
        self.canvas.rotate(-180.0*posangle/pi)
        self._set_color_and_stroke_style(paint, mode)
        self.canvas.drawOval(rect, paint)
        self.canvas.restore()

    def text_right(self, x, y, text):
        self.paint_text.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        self.canvas.drawString(text, x, -y, self.font_default, self.paint_text)

    def text_left(self, x, y, text):
        text_width = self.font_default.measureText(text)
        self.paint_text.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        self.canvas.drawString(text, x-text_width, -y, self.font_default, self.paint_text)

    def text_centred(self, x, y, text):
        text_width = self.font_default.measureText(text)
        self.paint_text.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        self.canvas.drawString(text, x-text_width/2, -y, self.font_default, self.paint_text)

    def text_width(self, text):
        return self.font_default.measureText(text)

    def translate(self, dx, dy):
        self.canvas.translate(dx, -dy)

    def rotate(self, angle):
        self.canvas.rotate(-180.0*angle/pi)

    def clip_path(self, path):
        pass

    def reset_clip(self):
        pass

    def finish(self):
        if self.format == 'png':
            image = self.surface.makeImageSnapshot()
            image.save(self.fobj, skia.kPNG)
        elif self.format == 'jpg':
            image = self.surface.makeImageSnapshot()
            image.save(self.fobj, skia.kJPEG)
        else:
            pass

    def on_screen(self, x, y):
        return x > -self.gi_width/2.0 and x < self.gi_width/2.0 and y > -self.gi_height/2.0  and y < self.gi_height/2.0

    def to_pixel(self, x, y):
        return (int(x * DPMM_IMG + self.sfc_width/2), int(y * DPMM_IMG + self.sfc_height/2))

    def antialias_on(self):
        self.paint_default.setAntiAlias(True)
        self.paint_dash.setAntiAlias(True)

    def antialias_off(self):
        self.paint_default.setAntiAlias(False)
        self.paint_dash.setAntiAlias(False)

    def _get_paint(self):
        if self.gi_dash_style is None:
            return self.paint_default
        self.paint_dash.setPathEffect(skia.DashPathEffect.Make(self.gi_dash_style[0], self.gi_dash_style[1]))
        return self.paint_dash

    def _set_color_and_stroke_style(self, paint, mode):
        if mode == DrawMode.BORDER:
            paint.setStyle(skia.Paint.kStroke_Style)
            paint.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        elif mode == DrawMode.FILL:
            paint.setStyle(skia.Paint.kFill_Style)
            paint.setColor4f(skia.Color4f(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2]))
        else:
            paint.setStyle(skia.Paint.kStrokeAndFill_Style)
            paint.setColor4f(skia.Color4f(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2]))
