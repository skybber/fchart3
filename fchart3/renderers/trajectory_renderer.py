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

from .base_renderer import BaseRenderer, SQRT2


class TrajectoryRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.trajectory:
            self.draw_trajectory(ctx, ctx.trajectory)

    def draw_trajectory(self, ctx, trajectory):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_pen_rgb(cfg.dso_color)
        gfx.set_solid_line()

        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()

        x1 = y1 = z1 = None
        labels = []

        for i, (ra2, dec2, label2) in enumerate(trajectory):
            x2, y2, z2 = ctx.transf.equatorial_to_xyz(ra2, dec2)

            if i > 0 and (nzopt or (z1 > 0 and z2 > 0)):
                gfx.set_linewidth(cfg.constellation_linewidth)
                gfx.line(x1, y1, x2, y2)
                if label2:
                    self.draw_trajectory_tick(gfx, cfg, x1, y1, x2, y2)
                if i == 1:
                    self.draw_trajectory_tick(gfx, cfg, x2, y2, x1, y1)

            nx = ny = None
            if x1 is not None:
                dx, dy = (x2 - x1), (y2 - y1)
                n = math.hypot(dx, dy)
                if n > 0:
                    nx, ny = dx / n, dy / n

            if label2 is not None:
                labels.append((x2, y2, z2, nx, ny, label2))

            x1, y1, z1 = x2, y2, z2

        sum_x, sum_y = (0, 0)
        for _, _, _, nx, ny, _ in labels:
            if nx is not None:
                sum_x += nx
                sum_y += ny
        # label_pos:
        #   1
        # 4 + 2
        #   3
        if sum_x != 0 or sum_y != 0:
            sum_x = sum_x / (len(labels) - 1)
            sum_y = sum_y / (len(labels) - 1)
            cmp = 0.8
            if sum_x > cmp or sum_x < -cmp:
                label_pos = 1
            else:
                label_pos = 2
        else:
            label_pos = 0

        r = ctx.min_radius * 1.2 / SQRT2
        gfx.set_font(gfx.gi_font, fh)
        for x, y, z, nx, ny, label in labels:
            if not (nzopt or z > 0):
                continue
            if label_pos == 1:
                gfx.text_centred(x, y + r + fh, label)
            elif label_pos == 2:
                gfx.text_right(x + r + fh / 4.0, y - fh / 2.0, label)
            else:
                gfx.text_centred(x, y - r - fh / 2.0, label)

    def draw_trajectory_tick(self, gfx, cfg, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        dr = math.hypot(dx, dy)
        if dr <= 0:
            return

        lw = cfg.constellation_linewidth
        tlen = max(2.5 * lw, 0.6)
        ddx = dx / dr
        ddy = dy / dr

        px = -ddy
        py = ddx

        gfx.set_linewidth(1.5 * lw)
        gfx.line(x2 - px * tlen, y2 - py * tlen, x2 + px * tlen, y2 + py * tlen)