#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
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

from .graphics_interface import *

DPI_IMG = 100.0
DPMM_IMG = DPI_IMG/INCH
PONT_IMG = 1.0/DPMM_IMG

A4_WIDTH_POINTS = 594
A4_HEIGHT_POINTS = 842

SKIA_DEFAULT_FONT_SIZE = 12*POINT

_TYPEFACE_CACHE = {}


def get_cached_typeface(font_name):
    """Returns a cached skia.Typeface for the given font_name."""
    if font_name not in _TYPEFACE_CACHE:
        _TYPEFACE_CACHE[font_name] = skia.Typeface(font_name)
    return _TYPEFACE_CACHE[font_name]


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
        super().__init__((width / DPMM_IMG if pixels else width) , (height / DPMM_IMG if pixels else height))

        self.fobj = fobj
        self.format = format
        self.landscape = landscape
        self.surface = None
        self.canvas = None
        self.sfc_width = None
        self.sfc_height = None
        self.base_save_count = None
        self.tolerance = tolerance
        self.dash_cache = {}
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)
        self.jpg_quality = jpg_quality

    def new(self):
        if self.format in ['png', 'jpg']:
            self.set_point_size(PONT_IMG)
            self.sfc_width = int(self.gi_width * DPMM_IMG)
            self.sfc_height = int(self.gi_height * DPMM_IMG)
            self.surface = skia.Surface(self.sfc_width, self.sfc_height)
            self.canvas = self.surface.getCanvas()
            self.canvas.scale(DPMM_IMG, DPMM_IMG)
            self.canvas.translate(self.gi_origin_x, self.gi_origin_y)
            self.base_save_count = self.canvas.getSaveCount()
        else:
            self.document = skia.PDF.MakeDocument(self.fobj)
            if self.landscape:
                self.sfc_width, self.sfc_height = A4_HEIGHT_POINTS, A4_WIDTH_POINTS
            else:
                self.sfc_width, self.sfc_height = A4_WIDTH_POINTS, A4_HEIGHT_POINTS

            self.canvas = self.document.beginPage(self.sfc_width, self.sfc_height)
            self.canvas.scale(DPMM, DPMM)
            if self.landscape:
                self.canvas.translate(self.gi_origin_x * DPMM + 15 * DPMM,
                                      self.gi_origin_y * DPMM + (210 - self.gi_height) * DPMM / 2)
            else:
                self.canvas.translate(self.gi_origin_x * DPMM + (210 - self.gi_width) * DPMM / 2,
                                      self.gi_origin_y * DPMM + 15 * DPMM)

            self.base_save_count = self.canvas.getSaveCount()

        self.paint_default = skia.Paint(AntiAlias=True)
        self.paint_dash = skia.Paint(AntiAlias=True)
        self.paint_text = skia.Paint(AntiAlias=True)
        self.font_default = None
        self.path = None

    def clear(self):
        return
        if self.gi_background_rgb:
            self.canvas.clear(skia.Color4f(self.gi_background_rgb[0], self.gi_background_rgb[1], self.gi_background_rgb[2], 1.0))

    def save(self):
        super().save()
        self.canvas.save()

    def restore(self):
        super().restore()
        self.canvas.restore()

    def _to_skia_fontstyle(self, style_flags):
        bold = (style_flags & FontStyle.BOLD) != 0
        italic = (style_flags & FontStyle.ITALIC) != 0
        if bold and italic:
            return skia.FontStyle.BoldItalic()
        if bold:
            return skia.FontStyle.Bold()
        if italic:
            return skia.FontStyle.Italic()
        return skia.FontStyle.Normal()

    def set_font(self, font='Arial', font_size=SKIA_DEFAULT_FONT_SIZE, font_style=FontStyle.NORMAL):
        old_size = self.gi_font_size
        super().set_font(font, font_size, font_style)
        if self.font_default is None or old_size != font_size:
            try:
                tf = skia.Typeface.MakeFromName(self.gi_font, self._to_skia_fontstyle(self.gi_font_style))
                if tf is None:  # fallback
                    tf = skia.Typeface('NotoSans-Regular')
            except Exception:
                tf = skia.Typeface('NotoSans-Regular')
            self.font_default = skia.Font(tf, self.gi_font_size)

    def set_linewidth(self, linewidth):
        super().set_linewidth(linewidth)
        self.paint_default.setStrokeWidth(linewidth)
        self.paint_dash.setStrokeWidth(linewidth)

    def set_solid_line(self):
        super().set_solid_line()

    def set_dashed_line(self, on, off, start=0.0):
        super().set_dashed_line(on, off, start)

    def line(self, x1, y1, x2, y2):
        paint = self._get_paint()
        paint.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2]))
        paint.setStyle(skia.Paint.kStroke_Style)
        self.canvas.drawLine((x1,-y1), (x2,-y2), paint)

    def rectangle(self, x, y, width, height, mode=DrawMode.BORDER):
        paint = self._get_paint()
        self._set_color_and_stroke_style(paint, mode)
        rect = skia.Rect.MakeXYWH(x, -y, width, height)
        self.canvas.drawRect(rect, paint)

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

    def polygons_indexed(self, x, y, polygons, mode=DrawMode.BORDER):
        path = skia.Path()
        for poly in polygons:
            if not poly:
                continue
            path.moveTo(x[poly[0]], -y[poly[0]])
            for i in poly[1:]:
                path.lineTo(x[i], -y[i])
        path.close()

        if mode == DrawMode.BORDER:
            paint = self._get_paint()
            paint.setStyle(skia.Paint.kStroke_Style)
            paint.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2], 1.0))
            self.canvas.drawPath(path, paint)
        elif mode == DrawMode.FILL:
            paint = self._get_paint()
            paint.setStyle(skia.Paint.kFill_Style)
            paint.setColor4f(skia.Color4f(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2], 1.0))
            self.canvas.drawPath(path, paint)
        else:
            fill = skia.Paint(AntiAlias=True)
            fill.setStyle(skia.Paint.kFill_Style)
            fill.setColor4f(skia.Color4f(self.gi_fill_rgb[0], self.gi_fill_rgb[1], self.gi_fill_rgb[2], 1.0))
            self.canvas.drawPath(path, fill)
            stroke = self._get_paint()
            stroke.setStyle(skia.Paint.kStroke_Style)
            stroke.setColor4f(skia.Color4f(self.gi_pen_rgb[0], self.gi_pen_rgb[1], self.gi_pen_rgb[2], 1.0))
            self.canvas.drawPath(path, stroke)

    def polyline(self, vertices):
        path = skia.Path()
        path.moveTo(vertices[0][0], -vertices[0][1])
        for v in vertices[1:]:
            path.lineTo(v[0], -v[1])
        self._set_color_and_stroke_style(self.paint_default, DrawMode.BORDER)
        self.canvas.drawPath(path, self.paint_default)

    def ellipse(self,x,y,rlong,rshort, posangle, mode=DrawMode.BORDER):
        self.canvas.save()
        paint = self._get_paint()
        self._set_color_and_stroke_style(paint, mode)
        self.canvas.translate(x, -y)
        self.canvas.rotate(-180.0 * posangle / pi)
        rect = skia.Rect.MakeLTRB(-rlong, -rshort, rlong, rshort)
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

    def move_to(self, x, y):
        if self.path is None:
            self.begin_path()
        self.path.moveTo(x, -y)

    def clip_path(self, path):
        p = skia.Path()
        p.moveTo(path[0][0], -path[0][1])
        for x, y in path[1:]:
            p.lineTo(x, -y)
        p.close()
        self.canvas.clipPath(p, doAntiAlias=True)

    def begin_path(self):
        self.path = skia.Path()

    def arc_to(self, x, y, r, angle1, angle2):
        if self.path is None:
            self.begin_path()
        start_deg = angle1 * 180.0 / pi
        sweep_deg = (angle2 - angle1) * 180.0 / pi
        oval = skia.Rect.MakeLTRB(x - r, -(y + r), x + r, -(y - r))
        self.path.addArc(oval, start_deg, sweep_deg)

    def elliptic_arc_to(self, x, y, rx, ry, angle1, angle2):
        if self.path is None:
            self.begin_path()
        start_deg = angle1 * 180.0 / pi
        sweep_deg = (angle2 - angle1) * 180.0 / pi
        oval = skia.Rect.MakeLTRB(x - rx, -(y + rx), x + rx, -(y - rx))
        tmp = skia.Path()
        tmp.addArc(oval, start_deg, sweep_deg)
        m = skia.Matrix()
        m.setScale(1.0, ry / float(rx), x, -y)
        tmp.transform(m)
        self.path.addPath(tmp)

    def line_to(self, x, y):
        if self.path is None:
            self.begin_path()
        self.path.lineTo(x, -y)

    def complete_path(self, mode=DrawMode.BORDER):
        if self.path is None:
            return
        paint = self._get_paint()
        if mode == DrawMode.BORDER:
            paint.setStyle(skia.Paint.kStroke_Style)
            paint.setColor4f(skia.Color4f(*self.gi_pen_rgb, 1.0))
            self.canvas.drawPath(self.path, paint)
        elif mode == DrawMode.FILL:
            paint.setStyle(skia.Paint.kFill_Style)
            paint.setColor4f(skia.Color4f(*self.gi_fill_rgb, 1.0))
            self.canvas.drawPath(self.path, paint)
        else:
            fill = skia.Paint(AntiAlias=True)
            fill.setStyle(skia.Paint.kFill_Style)
            fill.setColor4f(skia.Color4f(*self.gi_fill_rgb, 1.0))
            self.canvas.drawPath(self.path, fill)
            stroke = self._get_paint()
            stroke.setStyle(skia.Paint.kStroke_Style)
            stroke.setColor4f(skia.Color4f(*self.gi_pen_rgb, 1.0))
            self.canvas.drawPath(self.path, stroke)
        self.path = None

    def reset_clip(self):
        self.canvas.restoreToCount(self.base_save_count)
        if self.format in ['png', 'jpg']:
            self.canvas.scale(DPMM_IMG, DPMM_IMG)
            self.canvas.translate(self.gi_origin_x, self.gi_origin_y)
        else:
            self.canvas.scale(DPMM, DPMM)
            if self.landscape:
                self.canvas.translate(self.gi_origin_x * DPMM + 15 * DPMM,
                                      self.gi_origin_y * DPMM + (210 - self.gi_height) * DPMM / 2)
            else:
                self.canvas.translate(self.gi_origin_x * DPMM + (210 - self.gi_width) * DPMM / 2,
                                      self.gi_origin_y * DPMM + 15 * DPMM)
        self.base_save_count = self.canvas.getSaveCount()

    def finish(self):
        if self.format in ['png', 'jpg']:
            image = self.surface.makeImageSnapshot()
            fmt = skia.kPNG if self.format == 'png' else skia.kJPEG
            data = image.encodeToData(fmt, self.jpg_quality if self.format == 'jpg' else 100)
            if hasattr(self.fobj, 'write'):
                self.fobj.write(bytes(data))
            else:
                with open(self.fobj, 'wb') as fw:
                    fw.write(bytes(data))
        else:
            self.document.endPage()
            self.document.close()

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
        (on, off), phase = self.gi_dash_style
        key = (float(on), float(off), float(phase))
        pe = self.dash_cache.get(key)
        if pe is None:
            pe = skia.DashPathEffect.Make([on, off], phase)
            self.dash_cache[key] = pe
        self.paint_dash.setPathEffect(pe)
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
