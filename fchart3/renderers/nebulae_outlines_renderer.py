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


class NebulaeOutlinesRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.used_catalogs.unknown_nebulae is not None:
            self.draw_unknown_nebulae(ctx, ctx.used_catalogs.unknown_nebulae)

    def draw_unknown_nebulae(self, ctx, unknown_nebulae):
        zopt = ctx.transf.is_zoptim()
        for uneb in unknown_nebulae:
            ra = (uneb.ra_min + uneb.ra_max) / 2.0
            dec = (uneb.dec_min + uneb.dec_max) / 2.0
            x, y, z = ctx.transf.equatorial_to_xyz(ra, dec)
            if zopt and z <= 0:
                continue
            for outl_lev in range(3):
                outlines = uneb.outlines[outl_lev]
                if not outlines:
                    continue
                for outl in outlines:
                    if not zopt or z > 0:
                        x_outl, y_outl = ctx.transf.np_equatorial_to_xy(outl[0], outl[1])
                        self.nebula_outlines(ctx, x_outl, y_outl, outl_lev)

    def nebula_outlines(self, ctx, x_outl, y_outl, outl_lev):
        gfx = ctx.gfx
        gfx.set_linewidth(ctx.cfg.nebula_linewidth)
        gfx.set_solid_line()

        if ctx.cfg.light_mode:
            frac = 4 - 1.5 * outl_lev  # no logic, look nice in light mode
            pen_r = 1.0 - ((1.0 - ctx.cfg.nebula_color[0]) / frac)
            pen_g = 1.0 - ((1.0 - ctx.cfg.nebula_color[1]) / frac)
            pen_b = 1.0 - ((1.0 - ctx.cfg.nebula_color[2]) / frac)
        else:
            frac = 4 - 1.5 * outl_lev # no logic, look nice in dark mode
            pen_r = ctx.cfg.nebula_color[0] / frac
            pen_g = ctx.cfg.nebula_color[1] / frac
            pen_b = ctx.cfg.nebula_color[2] / frac

        gfx.set_pen_rgb((pen_r, pen_g, pen_b))

        for i in range(len(x_outl)-1):
            gfx.line(x_outl[i].item(), y_outl[i].item(), x_outl[i+1].item(), y_outl[i+1].item())
        gfx.line(x_outl[len(x_outl)-1].item(), y_outl[len(x_outl)-1].item(), x_outl[0].item(), y_outl[0].item())
