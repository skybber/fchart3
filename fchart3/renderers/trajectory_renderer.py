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


def _segment_hits_box(ax, ay, bx, by, u0, u1, v0, v1) -> bool:
    """Liang-Barsky test: does segment a-b intersect the axis-aligned box [u0,u1] x [v0,v1]?"""
    t0, t1 = 0.0, 1.0
    dx, dy = bx - ax, by - ay
    for p, q in ((-dx, ax - u0), (dx, u1 - ax), (-dy, ay - v0), (dy, v1 - ay)):
        if p == 0.0:
            if q < 0.0:
                return False
        else:
            t = q / p
            if p < 0.0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def _box_corners(box):
    """Corners of a label box (px, py, nx, ny, u0, u1, half_h): u along (nx, ny), v across it."""
    px, py, nx, ny, u0, u1, half_h = box
    tx, ty = ny, -nx
    return [(px + nx * u + tx * v, py + ny * u + ty * v)
            for u, v in ((u0, -half_h), (u1, -half_h), (u1, half_h), (u0, half_h))]


def _convex_overlap(p, q) -> bool:
    """Separating axis test for two convex polygons (touching does not count)."""
    for poly in (p, q):
        for k in range(len(poly)):
            x1, y1 = poly[k]
            x2, y2 = poly[(k + 1) % len(poly)]
            ax, ay = y1 - y2, x2 - x1
            pa = [ax * x + ay * y for x, y in p]
            qa = [ax * x + ay * y for x, y in q]
            if max(pa) <= min(qa) or max(qa) <= min(pa):
                return False
    return True


class _Obstacles:
    """What trajectory labels avoid: drawn trajectory segments and already placed labels."""

    def __init__(self, segments=None):
        self.segments = list(segments or [])
        self.boxes = []

    def hits(self, box) -> int:
        px, py, nx, ny, u0, u1, half_h = box
        tx, ty = ny, -nx
        count = 0
        for ax, ay, bx, by in self.segments:
            au = (ax - px) * nx + (ay - py) * ny
            av = (ax - px) * tx + (ay - py) * ty
            bu = (bx - px) * nx + (by - py) * ny
            bv = (bx - px) * tx + (by - py) * ty
            if _segment_hits_box(au, av, bu, bv, u0, u1, -half_h, half_h):
                count += 1
        corners = _box_corners(box)
        count += sum(1 for other in self.boxes if _convex_overlap(corners, other))
        return count

    def add_box(self, box):
        self.boxes.append(_box_corners(box))

    def best_box(self, candidates):
        """First candidate box without collisions, else the one with the fewest."""
        best = None
        for box in candidates:
            hits = self.hits(box)
            if hits == 0:
                return box
            if best is None or hits < best[0]:
                best = (hits, box)
        return best[1] if best else None


class _TextWriter:
    """Draws horizontal text through gfx and registers its box as an obstacle, for every label style."""

    def __init__(self, gfx, obstacles):
        self.gfx = gfx
        self.obstacles = obstacles
        self.fh = gfx.gi_default_font_size

    def _register(self, left, cy, text):
        self.obstacles.add_box((left, cy, 1.0, 0.0, 0.0, self.gfx.text_width(text), self.fh * 0.45))

    def text_right(self, x, y, text):
        self.gfx.text_right(x, y, text)
        self._register(x, y + self.fh / 3.0, text)

    def text_left(self, x, y, text):
        self.gfx.text_left(x, y, text)
        self._register(x - self.gfx.text_width(text), y + self.fh / 3.0, text)

    def text_centred(self, x, y, text):
        self.gfx.text_centred(x, y, text)
        self._register(x - self.gfx.text_width(text) / 2.0, y, text)

    def text_in_box(self, box, text):
        """Draw text into a horizontal box (left x, centre y, 1, 0, 0, width, half_h)."""
        self.text_right(box[0], box[1] - self.fh / 3.0, text)


class TrajectoryRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if not ctx.trajectories:
            return
        # Accept TrajectoryDrawing (points + name) as well as a plain list of points.
        items = [(getattr(t, "points", t), getattr(t, "name", None)) for t in ctx.trajectories]
        show_names = len(items) > 1
        projected = [self._project(ctx, points) for points, _ in items]

        # Labels avoid all trajectory lines and the labels placed before them.
        obstacles = _Obstacles()
        for proj in projected:
            obstacles.segments.extend(self._visible_segments(ctx, proj))

        for (points, name), proj in zip(items, projected):
            self.draw_trajectory(ctx, points, name=name if show_names else None,
                                 projected=proj, obstacles=obstacles)

    def _project(self, ctx, points):
        return [ctx.transf.equatorial_to_xyz(pt.ra, pt.dec) for pt in points]

    def _visible_segments(self, ctx, proj):
        nzopt = not ctx.transf.is_zoptim()
        return [(x1, y1, x2, y2)
                for (x1, y1, z1), (x2, y2, z2) in zip(proj, proj[1:])
                if nzopt or (z1 > 0 and z2 > 0)]

    def _label_text(self, cfg, pt):
        if cfg.show_trajectory_mag and pt.mag is not None:
            return f"{pt.label} {pt.mag:.1f}m"
        return pt.label

    def draw_trajectory(self, ctx, trajectory, name=None, projected=None, obstacles=None):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_pen_rgb(cfg.dso_color)
        gfx.set_solid_line()

        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()

        if projected is None:
            projected = self._project(ctx, trajectory)
        if obstacles is None:
            obstacles = _Obstacles(self._visible_segments(ctx, projected))
        normal_style = cfg.trajectory_label_style != "side"
        writer = _TextWriter(gfx, obstacles)

        x1 = y1 = z1 = None
        labels = []
        first_tangent = None
        tail_side_sum = 0.0
        tail_side_count = 0

        for i, pt in enumerate(trajectory):
            label2 = pt.label
            x2, y2, z2 = projected[i]

            if i > 0 and (nzopt or (z1 > 0 and z2 > 0)):
                gfx.set_linewidth(cfg.trajectory_linewidth)
                gfx.line(x1, y1, x2, y2)
                if normal_style:
                    if label2:
                        self._draw_tick_along_tangent(ctx, projected, i)
                    if i == 1:
                        self._draw_tick_along_tangent(ctx, projected, 0)
                else:
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
                labels.append((i, x2, y2, z2, nx, ny, self._label_text(cfg, pt)))

            x1, y1, z1 = x2, y2, z2

        tail_opposite_side = self._recommended_label_side(tail_side_sum, tail_side_count)

        gfx.set_font(gfx.gi_font, fh)
        if normal_style:
            self._draw_normal_labels(ctx, projected, labels, tail_opposite_side, obstacles, writer)
        else:
            self._draw_side_labels(ctx, labels, first_tangent, tail_opposite_side, writer)

        if name:
            self._draw_name_label(ctx, projected, name, obstacles, writer)

    def _draw_side_labels(self, ctx, labels, first_tangent, tail_opposite_side, writer):
        """Horizontal labels beside the points (original placement, boxes registered as obstacles)."""
        gfx = ctx.gfx
        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()

        sum_x, sum_y = (0, 0)
        for _, _, _, _, nx, ny, _ in labels:
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
        for _, x, y, z, nx, ny, label in labels:
            if not (nzopt or z > 0):
                continue
            if tail_opposite_side is not None:
                tangent = (nx, ny) if nx is not None else first_tangent
                if tangent is not None:
                    tx, ty = tangent
                    self._draw_label_on_trajectory_side(
                        writer, x, y, label, tx, ty, tail_opposite_side, r, fh
                    )
                    continue

            if label_pos == 1:
                writer.text_centred(x, y + r + fh, label)
            elif label_pos == 2:
                writer.text_right(x + r + fh / 4.0, y - fh / 2.0, label)
            else:
                writer.text_centred(x, y - r - fh / 2.0, label)

    def _tangent_at(self, ctx, projected, i):
        """
        Unit screen tangent at point i, shared by its tick and label: central difference of the visible
        neighbours, else a usable one-sided direction (e.g. at a turning point), else a fixed fallback.
        """
        nzopt = not ctx.transf.is_zoptim()

        def visible(k):
            return 0 <= k < len(projected) and (nzopt or projected[k][2] > 0)

        def unit(a, b):
            dx = projected[b][0] - projected[a][0]
            dy = projected[b][1] - projected[a][1]
            d = math.hypot(dx, dy)
            return (dx / d, dy / d) if d > 1e-12 else None

        prev_ok, next_ok = visible(i - 1), visible(i + 1)
        candidates = []
        if prev_ok and next_ok:
            candidates.append((i - 1, i + 1))
        if prev_ok:
            candidates.append((i - 1, i))
        if next_ok:
            candidates.append((i, i + 1))
        for a, b in candidates:
            t = unit(a, b)
            if t is not None:
                return t
        # No usable direction (single point, hidden neighbours): normal then points sideways.
        return 0.0, -1.0

    def _draw_tick_along_tangent(self, ctx, projected, i):
        """Tick at point i perpendicular to the same tangent its label uses."""
        x, y, _ = projected[i]
        tx, ty = self._tangent_at(ctx, projected, i)
        self.draw_trajectory_tick(ctx.gfx, ctx.cfg, x - tx, y - ty, x, y)

    def _draw_normal_labels(self, ctx, projected, labels, tail_opposite_side, obstacles, writer):
        """
        Labels in the direction perpendicular to the trajectory, on the side free of lines.
        Text is horizontal by default; with cfg.trajectory_label_rotate it is rotated along the normal.
        """
        gfx = ctx.gfx
        cfg = ctx.cfg
        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()

        tlen = max(2.5 * cfg.constellation_linewidth, 0.6)
        d0 = tlen + fh * 0.25
        half_h = fh * 0.45
        preferred = tail_opposite_side if tail_opposite_side is not None else 1
        rotate = cfg.trajectory_label_rotate

        for i, x, y, z, _, _, label in labels:
            if not (nzopt or z > 0):
                continue
            tx, ty = self._tangent_at(ctx, projected, i)
            width = gfx.text_width(label)

            candidates = []
            for side in (preferred, -preferred):
                nx, ny = -ty * side, tx * side
                if rotate:
                    candidates.append((x, y, nx, ny, d0, d0 + width, half_h))
                else:
                    candidates.append(self._horizontal_box_along_normal(x, y, nx, ny, d0, width, half_h))
            box = obstacles.best_box(candidates)

            if rotate:
                self._draw_rotated_label(gfx, x, y, box[2], box[3], d0, label, fh)
                obstacles.add_box(box)
            else:
                writer.text_in_box(box, label)

    @staticmethod
    def _horizontal_box_along_normal(x, y, nx, ny, d0, width, half_h):
        """
        Box of horizontal text pushed out along normal (nx, ny) so its nearest edge is d0 from (x, y).
        Returned in the label box form (left x, centre y, 1, 0, 0, width, half_h).
        """
        reach = width / 2.0 * abs(nx) + half_h * abs(ny)
        cx = x + nx * (d0 + reach)
        cy = y + ny * (d0 + reach)
        return (cx - width / 2.0, cy, 1.0, 0.0, 0.0, width, half_h)

    def _draw_rotated_label(self, gfx, x, y, nx, ny, d0, label, fh):
        """Draw text along direction (nx, ny) starting d0 from (x, y), never upside down."""
        angle = math.atan2(ny, nx)
        gfx.save()
        gfx.translate(x, y)
        if nx >= 0:
            gfx.rotate(angle)
            gfx.text_right(d0, -fh / 3.0, label)
        else:
            gfx.rotate(angle + math.pi)
            gfx.text_left(-d0, -fh / 3.0, label)
        gfx.restore()

    def _draw_name_label(self, ctx, projected, name, obstacles, writer):
        """Object name near the start point: behind it along the line, else the first free spot."""
        gfx = ctx.gfx
        fh = gfx.gi_default_font_size
        nzopt = not ctx.transf.is_zoptim()
        if not projected or not (nzopt or projected[0][2] > 0):
            return
        x, y, _ = projected[0]
        width = gfx.text_width(name)
        half_h = fh * 0.45
        d0 = fh * 0.6
        step = fh * 1.1

        # Candidate (left x, centre y) of horizontal text, preferred first: behind the start along the
        # line, rows shifted up/down (nearby parallel tracks), around the point, further rows.
        bx, by = (-c for c in self._tangent_at(ctx, projected, 0))
        ax, ay = x + bx * d0, y + by * d0
        left = ax if bx >= 0 else ax - width
        positions = [(left, ay + k * step) for k in (0, 1, -1)]
        positions += [(x + d0, y), (x - d0 - width, y), (x - width / 2.0, y + step), (x - width / 2.0, y - step)]
        positions += [(left, ay + k * step) for k in (2, -2, 3, -3)]

        box = obstacles.best_box([(px, py, 1.0, 0.0, 0.0, width, half_h) for px, py in positions])
        writer.text_in_box(box, name)

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
        # gfx: anything with text_right/text_left/text_centred (a _TextWriter registers the box)
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

        gfx.set_linewidth(cfg.trajectory_linewidth)

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
