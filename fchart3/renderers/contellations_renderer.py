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

import math

import numpy as np

from ..np_astrocalc import np_sphere_to_rect, np_rect_to_sphere
from .base_renderer import BaseRenderer


class ConstellationsRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.used_catalogs.constell_catalog is not None:
            if ctx.cfg.show_constellation_borders:
                self.draw_constellations_boundaries(ctx, ctx.used_catalogs.constell_catalog)
            if ctx.cfg.show_constellation_shapes:
                self.draw_constellations_shapes(ctx, ctx.used_catalogs.constell_catalog)

    def draw_constellations_shapes(self, ctx, constell_catalog):
        gfx = ctx.gfx
        cfg = ctx.cfg
        gfx.set_linewidth(cfg.constellation_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.constellation_lines_color)

        if ctx.precession_matrix is not None:
            points = constell_catalog.all_constell_lines
            xr1, yr1, zr1 = np_sphere_to_rect(points[:,0], points[:,1])
            constell_lines_rect1 = np.column_stack((xr1, yr1, zr1))
            xr2, yr2, zr2 = np_sphere_to_rect(points[:,2], points[:,3])
            constell_lines_rect2 = np.column_stack((xr2, yr2, zr2))
            prec_rect1 = np.matmul(constell_lines_rect1, ctx.precession_matrix)
            ra1, dec1 = np_rect_to_sphere(prec_rect1[:,[0]], prec_rect1[:,[1]], prec_rect1[:,[2]])
            prec_rect2 = np.matmul(constell_lines_rect2, ctx.precession_matrix)
            ra2, dec2 = np_rect_to_sphere(prec_rect2[:,[0]], prec_rect2[:,[1]], prec_rect2[:,[2]])
            constell_lines = np.column_stack((ra1, dec1, ra2, dec2))
        else:
            constell_lines = constell_catalog.all_constell_lines

        x1, y1, z1 = ctx.transf.np_equatorial_to_xyz(constell_lines[:, 0], constell_lines[:, 1])
        x2, y2, z2 = ctx.transf.np_equatorial_to_xyz(constell_lines[:, 2], constell_lines[:, 3])

        nzopt = not ctx.transf.is_zoptim()

        for i in range(len(x1)):
            if not (nzopt or (z1[i] > 0 and z2[i] > 0)):
                continue
            c1 = gfx.cohen_sutherland_encode(x1[i], y1[i])
            c2 = gfx.cohen_sutherland_encode(x2[i], y2[i])
            if (c1 & c2) != 0:
                continue
            if nzopt and z1[i] < 0 and z2[i] < 0:
                c = c1 | c2
                if (c & 0b1100 == 0b1100) or (c & 0b0011 == 0b0011):
                    continue

            if cfg.constellation_linespace > 0:
                dx = x2[i] - x1[i]
                dy = y2[i] - y1[i]
                dr = math.hypot(dx, dy)
                if dr == 0:
                    continue
                ddx = dx * cfg.constellation_linespace / dr
                ddy = dy * cfg.constellation_linespace / dr
                gfx.line(x1[i] + ddx, y1[i] + ddy, x2[i] - ddx, y2[i] - ddy)
            else:
                gfx.line(x1[i], y1[i], x2[i], y2[i])

    def draw_constellations_boundaries(self, ctx, constell_catalog):
        gfx = ctx.gfx
        cfg = ctx.cfg
        gfx.set_dashed_line(0.6, 1.2)

        if ctx.precession_matrix is not None:
            points = constell_catalog.boundaries_points
            xr, yr, zr = np_sphere_to_rect(points[:,0], points[:,1])
            constell_bound_rect = np.column_stack((xr, yr, zr))
            prec_rect = np.matmul(constell_bound_rect, ctx.precession_matrix)
            ra, dec = np_rect_to_sphere(prec_rect[:,[0]], prec_rect[:,[1]], prec_rect[:,[2]])
            constell_boundaries = np.column_stack((ra, dec))
        else:
            constell_boundaries = constell_catalog.boundaries_points

        x, y, z = ctx.transf.np_equatorial_to_xyz(constell_boundaries[:,0], constell_boundaries[:,1])

        hl_constellation = ctx.hl_constellation.upper() if ctx.hl_constellation else None

        wh_min = 2.5 # 2.5mm min interp distance
        flat_dec = math.pi*75/180 # boundaries can be linearized above 75 deg
        flat_rac_interp = math.pi*7/180 # some "magic" angle 7 deg.
        max_angle2 = (1 / 180 * math.pi)

        nzopt = not ctx.transf.is_zoptim()

        for index1, index2, cons1, cons2 in constell_catalog.boundaries_lines:
            if nzopt or (z[index1] > 0 and z[index2] > 0):
                if hl_constellation and (hl_constellation == cons1 or hl_constellation == cons2):
                    gfx.set_pen_rgb(cfg.constellation_hl_border_color)
                    gfx.set_linewidth(cfg.constellation_linewidth * 1.75)
                else:
                    gfx.set_pen_rgb(cfg.constellation_border_color)
                    gfx.set_linewidth(cfg.constellation_border_linewidth)

                x_start, y_start, z_start = x[index1], y[index1], z[index1]
                x_end, y_end, z_end = x[index2], y[index2], z[index2]

                ra_start, dec_start = constell_boundaries[index1]
                ra_end, dec_end = constell_boundaries[index2]

                d_ra = ((ra_end - ra_start + math.pi) % (2 * math.pi)) - math.pi
                d_dec = (dec_end - dec_start)

                interpolate = True
                if (abs(dec_start) > flat_dec or abs(dec_end) > flat_dec) and abs(d_ra) < flat_rac_interp:
                    interpolate = False

                if interpolate:
                    divisions = self.calc_boundary_divisions(ctx, 1, 1, wh_min, max_angle2, x_start, y_start, z_start, x_end, y_end, z_end, ra_start, dec_start, ra_end, dec_end)
                else:
                    divisions = 1

                if divisions == 0:
                    continue

                if divisions == 1:
                    gfx.line(x_start, y_start, x_end, y_end)
                else:
                    dd_ra = d_ra / divisions
                    dd_dec = d_dec / divisions
                    vertices = [(x_start, y_start)]
                    ra1, dec1 = ra_start, dec_start

                    for i in range(divisions-1):
                        dec2 = dec1 + dd_dec
                        ra2 = ra1 + dd_ra
                        x2, y2 = ctx.transf.equatorial_to_xy(ra2, dec2)
                        vertices.append((x2, y2))
                        ra1, dec1 = ra2, dec2
                    vertices.append((x_end, y_end))
                    gfx.polyline(vertices)

    def calc_boundary_divisions(self, ctx, level, divs, wh_min, max_angle2, x1, y1, z1, x2, y2, z2, ra1, dec1, ra2, dec2):
        gfx = ctx.gfx
        if abs(x2-x1) < wh_min and abs(y2-y1) < wh_min:
            # gfx.text_centred((x1+x2)/2, (y1+y2)/2, '{:.1f}'.format(max(abs(x2-x1), abs(y2-y1))))
            return divs

        if level > 12:
            return divs

        ra_center = ((ra1 + ra2) / 2.0) if abs(ra2 - ra1) <= math.pi else (math.pi + (ra1 + ra2) / 2.0)
        dec_center = (dec1 + dec2) / 2.0

        xc, yc = ctx.transf.equatorial_to_xy(ra_center, dec_center)

        if level == 1:
            c1 = gfx.cohen_sutherland_encode(x1, y1)
            c2 = gfx.cohen_sutherland_encode(xc, yc)
            c3 = gfx.cohen_sutherland_encode(x2, y2)
            if (c1 & c2) != 0 and (c2 & c3) != 0:
                return 0
            nzopt = not ctx.transf.is_zoptim()
            if nzopt and z1 < 0 and z2 < 0 and ctx.field_radius > math.pi/4:
                c1 = gfx.cohen_sutherland_encode(x1, y1)
                c2 = gfx.cohen_sutherland_encode(x2, y2)
                c = c1 | c2
                if (c & 0b1100 == 0b1100) or (c & 0b0011 == 0b0011):
                    return 0

        vx1, vy1 = xc - x1, yc - y1
        vx2, vy2 = x2 - xc, y2 - yc
        n1 = math.hypot(vx1, vy1)
        n2 = math.hypot(vx2, vy2)
        if n1 == 0 or n2 == 0:
            return divs

        cross = (vx1 * vy2 - vy1 * vx2) / (n1 * n2)
        if abs(cross) < max_angle2:
            return divs

        return self.calc_boundary_divisions(ctx, level+1, divs * 2, wh_min, max_angle2, x1, y1, 1, xc, yc, 1, ra1, dec1, ra_center, dec_center)
