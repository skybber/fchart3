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

from .base_renderer import BaseRenderer


class ArrowRenderer(BaseRenderer):
    def draw(self, ctx, state):
        if ctx.highlights is not None:
            self.draw_arrow_to_highlight(ctx)
        pass
    
    def draw_arrow_to_highlight(self, ctx):
        gfx = ctx.gfx
        clip_path = ctx.clip_path
        for hl_def in ctx.highlights:
            if hl_def.style == 'cross' and len(hl_def.data) == 1:
                break
        else:
            return

        rax, decx, object_name, label, _ = hl_def.data[0]
        x, y, z = ctx.transf.equatorial_to_xyz(rax, decx)

        if self.is_inside_clip_path(clip_path, x, y):
            return

        arrow_len = 6

        intersection = self.find_intersection(clip_path, x, y)
        if intersection is None:
            return

        x_int, y_int = intersection

        direction_x = x
        direction_y = y
        norm = math.hypot(direction_x, direction_y)
        if norm == 0:
            return

        unit_direction_x = direction_x / norm
        unit_direction_y = direction_y / norm

        arrow_length = arrow_len
        arrow_end_x = x_int - unit_direction_x * arrow_length
        arrow_end_y = y_int - unit_direction_y * arrow_length

        gfx.set_solid_line()
        gfx.set_linewidth(ctx.cfg.legend_linewidth * 3)
        gfx.set_pen_rgb(ctx.cfg.draw_color)

        gfx.line(x_int, y_int, arrow_end_x, arrow_end_y)

        arrowhead_size = 2 * arrow_len / 3
        angle = math.atan2(unit_direction_y, unit_direction_x)
        left_wing_angle = angle + math.pi / 6
        right_wing_angle = angle - math.pi / 6

        left_wing_x = x_int - arrowhead_size * math.cos(left_wing_angle)
        left_wing_y = y_int - arrowhead_size * math.sin(left_wing_angle)
        gfx.line(x_int, y_int, left_wing_x, left_wing_y)

        right_wing_x = x_int - arrowhead_size * math.cos(right_wing_angle)
        right_wing_y = y_int - arrowhead_size * math.sin(right_wing_angle)
        gfx.line(x_int, y_int, right_wing_x, right_wing_y)

        if label is not None:
            label_x = x_int + (arrow_end_x - x_int) / 2
            label_y = y_int + (arrow_end_y - y_int) / 2
            gfx.text_centred(label_x, label_y, label)

    def is_inside_clip_path(self, clip_path, x, y):
        x_coords = [point[0] for point in clip_path]
        y_coords = [point[1] for point in clip_path]

        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)

        return x_min <= x <= x_max and y_min <= y <= y_max

    def find_intersection(self, clip_path, x, y):
        edges = []
        n = len(clip_path)
        for i in range(n):
            p1 = clip_path[i]
            p2 = clip_path[(i+1) % n]
            edges.append((p1, p2))

        intersections = []
        for p1, p2 in edges:
            x0, y0 = p1
            x1, y1 = p2

            if x0 == x1:  # Vertical edge
                x_edge = x0
                if x == 0:
                    continue  # Avoid division by zero; line is vertical
                t = x_edge / x
                if t >= 0:
                    y_int = t * y
                    y_min = min(y0, y1)
                    y_max = max(y0, y1)
                    if y_min <= y_int <= y_max:
                        intersections.append((t, (x_edge, y_int)))
            elif y0 == y1:  # Horizontal edge
                y_edge = y0
                if y == 0:
                    continue  # Avoid division by zero; line is horizontal
                t = y_edge / y
                if t >= 0:
                    x_int = t * x
                    x_min = min(x0, x1)
                    x_max = max(x0, x1)
                    if x_min <= x_int <= x_max:
                        intersections.append((t, (x_int, y_edge)))

        if not intersections:
            return None

        t_min, intersection_point = min(intersections, key=lambda item: item[0])
        return intersection_point
