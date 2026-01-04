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

from .base_renderer import BaseRenderer, SQRT2


class ExtrasRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.extra_positions is not None:
            self.draw_extra_positions(ctx, ctx.extra_positions)

    def draw_extra_positions(self, ctx, extra_positions):
        nzopt = not ctx.transf.is_zoptim()
        for rax, decx, label, labelpos in extra_positions:
            x, y, z = ctx.transf.equatorial_to_xyz(rax, decx)
            if nzopt or z >= 0:
                self.unknown_object(ctx, x, y, ctx.min_radius, label, labelpos)
                
    def unknown_object(self, ctx, x, y, radius, label, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0.0 else ctx.drawing_width / 40.0
        r /= SQRT2

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.dso_color)

        gfx.line(x-r, y+r, x+r, y-r)
        gfx.line(x+r, y+r, x-r, y-r)

        fh = gfx.gi_default_font_size

        if label:
            gfx.set_pen_rgb(cfg.label_color)
            if labelpos == 0:
                gfx.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos == 1:
                gfx.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                gfx.text_centred(x, y + r + fh/2.0, label)
            else:
                gfx.text_centred(x, y - r - fh/2.0, label)
