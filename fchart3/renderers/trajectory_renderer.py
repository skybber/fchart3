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

from .base_renderer import BaseRenderer, SQRT2
from ..astro.astrocalc import pos_angle


class TrajectoryRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.trajectories:
            for trajectory in ctx.trajectories:
                self.draw_trajectory(ctx, trajectory)

    def draw_trajectory(self, ctx, trajectory):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_pen_rgb(cfg.dso_color)
        gfx.set_solid_line()

        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()

        x1 = y1 = z1 = None
        labels = []
        first_tangent = None
        tail_side_sum = 0.0
        tail_side_count = 0

        for i, pt in enumerate(trajectory):
            ra2 = pt.ra
            dec2 = pt.dec
            label2 = pt.label
            x2, y2, z2 = ctx.transf.equatorial_to_xyz(ra2, dec2)

            if i > 0 and (nzopt or (z1 > 0 and z2 > 0)):
                gfx.set_linewidth(cfg.constellation_linewidth)
                gfx.line(x1, y1, x2, y2)
                if label2:
                    self.draw_trajectory_tick(gfx, cfg, x1, y1, x2, y2)
                if i == 1:
                    self.draw_trajectory_tick(gfx, cfg, x2, y2, x1, y1)

            if pt.sun_ra is not None and pt.sun_dec is not None:
                if nzopt or z2 > 0:
                    self.draw_comet_with_tail(ctx, pt)

            nx = ny = None
            if x1 is not None:
                dx, dy = (x2 - x1), (y2 - y1)
                n = math.hypot(dx, dy)
                if n > 0:
                    nx, ny = dx / n, dy / n
                    if first_tangent is None:
                        first_tangent = (nx, ny)

            if nx is not None:
                tail_vec = self._tail_screen_unit_vector(ctx, pt)
                if tail_vec is not None:
                    # Positive means "tail is on the left side of trajectory".
                    left_nx, left_ny = -ny, nx
                    tail_side = tail_vec[0] * left_nx + tail_vec[1] * left_ny
                    tail_side_sum += tail_side
                    tail_side_count += 1

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

        tail_opposite_side = self._recommended_label_side(tail_side_sum, tail_side_count)

        r = ctx.min_radius * 1.2 / SQRT2
        gfx.set_font(gfx.gi_font, fh)
        for x, y, z, nx, ny, label in labels:
            if not (nzopt or z > 0):
                continue
            if tail_opposite_side is not None:
                tangent = (nx, ny) if nx is not None else first_tangent
                if tangent is not None:
                    tx, ty = tangent
                    self._draw_label_on_trajectory_side(
                        gfx, x, y, label, tx, ty, tail_opposite_side, r, fh
                    )
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

    def draw_comet_with_tail(self, ctx, pt):
        cfg = ctx.cfg
        gfx = ctx.gfx

        if not cfg.show_comet_tail:
            return

        base_length = cfg.comet_tail_length
        if base_length <= 0:
            return

        L_ang_rad = base_length / ctx.drawing_scale
        if L_ang_rad <= 0:
            return

        pa_sun = pos_angle(pt.ra, pt.dec, pt.sun_ra, pt.sun_dec)
        pa_tail = pa_sun

        half_angle = math.radians(cfg.comet_tail_half_angle_deg)
        side_scale = cfg.comet_tail_side_scale

        gfx.set_pen_rgb(cfg.comet_tail_color)
        self.draw_tail_fan(ctx, pt.ra, pt.dec, pa_tail, L_ang_rad, base_length, half_angle, side_scale)
        gfx.set_pen_rgb(cfg.dso_color)

    def _tail_screen_unit_vector(self, ctx, pt, eps=1e-9):
        if pt.sun_ra is None or pt.sun_dec is None:
            return None

        base_length = ctx.cfg.comet_tail_length
        if base_length <= 0:
            return None

        L_ang_rad = base_length / ctx.drawing_scale
        if L_ang_rad <= 0:
            return None

        x0, y0, z0 = ctx.transf.equatorial_to_xyz(pt.ra, pt.dec)
        pa_sun = pos_angle(pt.ra, pt.dec, pt.sun_ra, pt.sun_dec)
        ra2, dec2 = self._destination_radec(pt.ra, pt.dec, pa_sun, L_ang_rad)
        x2, y2, z2 = ctx.transf.equatorial_to_xyz(ra2, dec2)

        nzopt = not ctx.transf.is_zoptim()
        if not (nzopt or (z0 > 0 and z2 > 0)):
            return None

        dx = x2 - x0
        dy = y2 - y0
        d = math.hypot(dx, dy)
        if d <= eps:
            return None

        return dx / d, dy / d

    def _recommended_label_side(self, tail_side_sum, tail_side_count, eps=1e-6):
        if tail_side_count <= 0:
            return None
        return -1 if tail_side_sum >= 0 else 1

    def _draw_label_on_trajectory_side(self, gfx, x, y, label, tx, ty, side, r, fh):
        nx = -ty * side
        ny = tx * side

        n = math.hypot(nx, ny)
        if n <= 0:
            return
        nx /= n
        ny /= n

        offset = r + fh * 0.5
        lx = x + nx * offset
        ly = y + ny * offset

        if abs(nx) >= abs(ny):
            if nx >= 0:
                gfx.text_right(lx + fh / 6.0, ly - fh / 3.0, label)
            else:
                gfx.text_left(lx - fh / 6.0, ly - fh / 3.0, label)
            return

        if ny >= 0:
            gfx.text_centred(lx, ly + fh / 3.0, label)
        else:
            gfx.text_centred(lx, ly - fh / 3.0, label)

    def draw_tail_fan(self, ctx, ra, dec, pa_tail, L_ang_rad, base_length, half_angle, side_scale):
        cfg = ctx.cfg
        gfx = ctx.gfx

        gfx.set_linewidth(cfg.constellation_linewidth)

        directions = [
            (pa_tail, 1.0),
            (pa_tail + half_angle, side_scale),
            (pa_tail - half_angle, side_scale),
        ]

        x0, y0, z0 = ctx.transf.equatorial_to_xyz(ra, dec)
        nzopt = not ctx.transf.is_zoptim()
        if not (nzopt or z0 > 0):
            return

        for pa, scale in directions:
            target_length = base_length * scale
            ra2, dec2 = self._destination_radec(ra, dec, pa, L_ang_rad * scale)
            x2, y2, z2 = ctx.transf.equatorial_to_xyz(ra2, dec2)
            if nzopt or (z0 > 0 and z2 > 0):
                endpoint = self._normalized_segment_endpoint(x0, y0, x2, y2, target_length)
                if endpoint is None:
                    continue
                x2n, y2n = endpoint
                gfx.line(x0, y0, x2n, y2n)

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

    def _normalized_segment_endpoint(self, x0, y0, x2, y2, target_length, eps=1e-9):
        if target_length <= 0:
            return None

        dx = x2 - x0
        dy = y2 - y0
        d = math.hypot(dx, dy)
        if d <= eps:
            return None

        scale = target_length / d
        return x0 + dx * scale, y0 + dy * scale
