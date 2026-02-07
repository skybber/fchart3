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


import math

from .base_renderer import BaseRenderer
from ..graphics.graphics_interface import DrawMode


class HighlightsRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.highlights is not None:
            self.draw_highlights(ctx, state)

    def draw_highlights(self, ctx, state):
        gfx = ctx.gfx
        cfg = ctx.cfg
        fn = gfx.gi_default_font_size
        highlight_fh = cfg.highlight_label_font_scale * fn
        nzopt = not ctx.transf.is_zoptim()

        for hl_def in ctx.highlights:
            for rax, decx, object_name, label, hl_mag in hl_def.data:
                x, y, z = ctx.transf.equatorial_to_xyz(rax, decx)
                if nzopt or z >= 0:
                    gfx.set_linewidth(hl_def.line_width)
                    if hl_def.style == 'cross':
                        gfx.set_pen_rgb(hl_def.color)
                        r = cfg.font_size * 2
                        gfx.line(x - r, y, x - r / 2, y)
                        gfx.line(x + r, y, x + r / 2, y)
                        gfx.line(x, y + r, x, y + r / 2)
                        gfx.line(x, y - r, x, y - r / 2)
                    elif hl_def.style == 'circle':
                        gfx.set_pen_rgb(hl_def.color)
                        r = cfg.font_size
                        gfx.circle(x, y, r)
                        if label:
                            gfx.set_font(gfx.gi_font, highlight_fh, cfg.dso_label_font_style)
                            self.draw_circular_object_label(ctx, x, y, r, label, fh=highlight_fh)
                            if hl_mag is not None:
                                label_mag = '{:.1f}m'.format(hl_mag)
                                gfx.set_font(gfx.gi_font, highlight_fh * 0.8, cfg.dso_label_font_style)
                                self.draw_circular_object_label(ctx, x, y - 0.9 * highlight_fh, r, label_mag, -1, highlight_fh)

                        self.collect_visible_object(ctx, state, x, y, r, object_name)
                    elif hl_def.style == 'comet':
                        payload = hl_mag if isinstance(hl_mag, dict) else {}
                        tail_pa = payload.get('tail_pa') if isinstance(payload, dict) else None
                        mag = payload.get('mag') if isinstance(payload, dict) else (hl_mag if isinstance(hl_mag, (int, float)) else None)

                        gfx.set_pen_rgb(hl_def.color)
                        gfx.set_fill_rgb(hl_def.color)
                        r = cfg.font_size
                        gfx.circle(x, y, r * 0.3, mode=DrawMode.FILL)
                        self._draw_comet_tail(ctx, rax, decx, tail_pa)

                        if label:
                            gfx.set_font(gfx.gi_font, highlight_fh, cfg.dso_label_font_style)
                            self.draw_circular_object_label(ctx, x, y, r, label, fh=highlight_fh)
                            if mag is not None:
                                label_mag = '{:.1f}m'.format(mag)
                                gfx.set_font(gfx.gi_font, highlight_fh * 0.8, cfg.dso_label_font_style)
                                self.draw_circular_object_label(ctx, x, y - 0.9 * highlight_fh, r, label_mag, -1, highlight_fh)

                        self.collect_visible_object(ctx, state, x, y, r, object_name)

    def _draw_comet_tail(self, ctx, ra, dec, tail_pa):
        cfg = ctx.cfg
        gfx = ctx.gfx

        if tail_pa is None:
            return

        if ctx.drawing_scale is None or ctx.drawing_scale <= 0:
            return

        L_ang_rad = cfg.comet_tail_length / ctx.drawing_scale
        if L_ang_rad <= 0:
            return

        half_angle = math.radians(cfg.comet_tail_half_angle_deg)
        side_scale = cfg.comet_tail_side_scale

        gfx.set_linewidth(cfg.constellation_linewidth)

        directions = [
            (tail_pa, 1.0),
            (tail_pa + half_angle, side_scale),
            (tail_pa - half_angle, side_scale),
        ]

        x0, y0, z0 = ctx.transf.equatorial_to_xyz(ra, dec)
        nzopt = not ctx.transf.is_zoptim()
        if not (nzopt or z0 > 0):
            return

        for pa, scale in directions:
            ra2, dec2 = self._destination_radec(ra, dec, pa, L_ang_rad * scale)
            x2, y2, z2 = ctx.transf.equatorial_to_xyz(ra2, dec2)
            if nzopt or (z0 > 0 and z2 > 0):
                gfx.line(x0, y0, x2, y2)

    def _destination_radec(self, ra1, dec1, pa, dist):
        sin_dec1 = math.sin(dec1)
        cos_dec1 = math.cos(dec1)
        sin_dist = math.sin(dist)
        cos_dist = math.cos(dist)

        dec2 = math.asin(sin_dec1 * cos_dist + cos_dec1 * sin_dist * math.cos(pa))
        dra = math.atan2(
            math.sin(pa) * sin_dist * cos_dec1,
            cos_dist - sin_dec1 * math.sin(dec2),
        )
        ra2 = (ra1 + dra) % (2 * math.pi)
        return ra2, dec2
