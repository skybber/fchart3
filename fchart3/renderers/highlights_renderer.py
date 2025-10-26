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


from .base_renderer import BaseRenderer


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
                    gfx.set_pen_rgb(hl_def.color)
                    gfx.set_linewidth(hl_def.line_width)
                    if hl_def.style == 'cross':
                        r = cfg.font_size * 2
                        gfx.line(x - r, y, x - r / 2, y)
                        gfx.line(x + r, y, x + r / 2, y)
                        gfx.line(x, y + r, x, y + r / 2)
                        gfx.line(x, y - r, x, y - r / 2)
                    elif hl_def.style == 'circle':
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
