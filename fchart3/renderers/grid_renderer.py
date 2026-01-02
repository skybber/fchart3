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
from .. import CoordSystem

MIN_GRID_DENSITY = 4
RA_GRID_SCALE = [0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 3*60]
DEC_GRID_SCALE = [1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 45*60, 60*60]
EPS = 1e-9


class GridRenderer(BaseRenderer):
    def draw(self, ctx, state):
        cfg = ctx.cfg
        if cfg.show_equatorial_grid:
            self.draw_grid_equatorial(ctx)

        if cfg.show_horizontal_grid:
            self.draw_grid_horizontal(ctx)

    def draw_grid_equatorial(self, ctx):
        if not ctx.center_equatorial:
            return
        def to_xyz(ra, dec):
            return ctx.transf.equatorial_to_xyz(ra, dec)

        self.draw_grid_generic(
            ctx=ctx,
            to_xyz=to_xyz,
            center_u=ctx.center_equatorial[0],
            center_v=ctx.center_equatorial[1],
            u_scale_list=[m for m in RA_GRID_SCALE],
            v_scale_list=[m for m in DEC_GRID_SCALE],
            u_label_fmt_fn=self.grid_ra_label,
            v_label_fmt_fn=self.grid_dec_label,
            cos_of_v=math.cos,
            u_period=2 * math.pi,
            v_min=-math.pi / 2, v_max=+math.pi / 2,
            v_label_edge='left',
            u_label_edges='auto',
            u_arcmin_per_unit=15.0,
            u_total_minutes=24 * 60,
            is_eq_grid=True
        )

    def draw_grid_horizontal(self, ctx):
        ra_c, dec_c = ctx.center_equatorial
        az_c, alt_c = ctx.transf.grid_equatorial_to_horizontal(ra_c, dec_c)
        if ctx.cfg.coord_system == CoordSystem.EQUATORIAL:
            def to_xyz(az, alt):
                ra, dec = ctx.transf.grid_horizontal_to_equatorial(az, alt)
                return ctx.transf.equatorial_to_xyz(ra, dec)
        else:
            def to_xyz(az, alt):
                return ctx.transf.horizontal_to_xyz(az, alt)

        AZ_GRID_SCALE = [1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 2*60, 5*60, 10*60, 15*60, 30*60, 45*60, 60*60]

        self.draw_grid_generic(
            ctx=ctx,
            to_xyz=to_xyz,
            center_u=az_c,
            center_v=alt_c,
            u_scale_list=AZ_GRID_SCALE,
            v_scale_list=DEC_GRID_SCALE,
            u_label_fmt_fn=self.grid_az_label,
            v_label_fmt_fn=self.grid_alt_label,
            cos_of_v=math.cos,
            u_period=2 * math.pi,
            v_min=-math.pi / 2, v_max=+math.pi / 2,
            v_label_edge='left',
            u_label_edges='auto',
            is_eq_grid=False
        )

    def draw_grid_generic(self,
                          ctx,
                          to_xyz,
                          center_u, center_v,
                          u_scale_list, v_scale_list,
                          u_label_fmt_fn, v_label_fmt_fn,
                          cos_of_v,
                          u_period=2 * math.pi,
                          v_min=-math.pi / 2, v_max=+math.pi / 2,
                          v_label_edge='left',
                          u_label_edges='auto',
                          u_arcmin_per_unit=1.0,
                          u_total_minutes=360 * 60,
                          is_eq_grid=True
                          ):
        gfx = ctx.gfx

        gfx.save()
        gfx.set_linewidth(ctx.cfg.grid_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(ctx.cfg.grid_color)

        prev_steps, prev_v_minutes = (None, None)
        for v_minutes in v_scale_list:
            steps = ctx.field_radius / (math.pi * v_minutes / (180 * 60))
            if steps < MIN_GRID_DENSITY:
                if prev_steps is not None and (prev_steps - MIN_GRID_DENSITY) < (MIN_GRID_DENSITY - steps):
                    v_minutes = prev_v_minutes
                break
            prev_steps, prev_v_minutes = (steps, v_minutes)

        v_label_fmt = '{}°' if v_minutes >= 60 else '{}°{:02d}\''

        v_min_vis = center_v - ctx.field_radius
        v_max_vis = center_v + ctx.field_radius

        v_minutes_cur = int(round(v_min * 180 * 60 / math.pi)) + v_minutes
        while v_minutes_cur < int(round(v_max * 180 * 60 / math.pi)):
            v = math.pi * v_minutes_cur / (180 * 60)
            if (v > v_min_vis) and (v < v_max_vis):
                self.draw_single_parallel(ctx, to_xyz, center_u, v, v_minutes_cur, v_label_fmt, v_label_fmt_fn, v_label_edge)
            v_minutes_cur += v_minutes

        prev_steps, prev_u_minutes = (None, None)
        fc_cos = cos_of_v(center_v)
        for u_minutes in u_scale_list:
            du_rad = math.pi * (u_minutes * u_arcmin_per_unit) / (180.0 * 60.0)
            steps = ctx.field_radius / max(EPS, (fc_cos * du_rad))
            if steps < MIN_GRID_DENSITY:
                if prev_steps is not None and (prev_steps - MIN_GRID_DENSITY) < (MIN_GRID_DENSITY - steps):
                    u_minutes = prev_u_minutes
                break
            prev_steps, prev_u_minutes = (steps, u_minutes)

        max_visible_v = center_v + ctx.field_radius if center_v > 0 else center_v - ctx.field_radius
        if max_visible_v >= math.pi/2 or max_visible_v <= -math.pi/2:
            u_size = u_period
        else:
            u_size = ctx.field_radius / max(EPS, cos_of_v(max_visible_v))
            if u_size > u_period:
                u_size = u_period

        if is_eq_grid:
            if u_minutes >= 60:
                u_label_fmt = 'H'
            elif u_minutes >= 1:
                u_label_fmt = 'HM'
            else:
                u_label_fmt = 'HMS'
        else:
            u_label_fmt = '{}°' if u_minutes >= 60 else '{}°{:02d}\''

        u_minutes_cur = 0

        while u_minutes_cur < u_total_minutes:
            u = (math.pi * (u_minutes_cur * u_arcmin_per_unit) / (180.0 * 60.0)) % u_period
            du = ((u - center_u + u_period / 2.0) % u_period) - u_period / 2.0
            if abs(du) <= u_size + 1e-6:
                self.draw_single_meridian(ctx, to_xyz, u, u_minutes_cur, u_label_fmt, u_label_fmt_fn, u_label_edges, center_v)
            u_minutes_cur += u_minutes

        gfx.restore()

    def draw_single_parallel(self, ctx, to_xyz, center_u, v, v_minutes, label_fmt, label_fmt_fn, label_edge):
        gfx = ctx.gfx
        du = ctx.field_radius / 10.0
        x11 = y11 = z11 = None
        x21 = y21 = z21 = None
        agg_u = 0.0
        nzopt = not ctx.transf.is_zoptim()

        iter_count = 0
        while agg_u <= math.pi and iter_count < 1000:
            x12, y12, z12 = to_xyz(center_u + agg_u, v)
            x22, y22, z22 = to_xyz(center_u - agg_u, v)

            if x11 is not None and (nzopt or (z11 > 0 and z12 > 0)):
                gfx.line(x11, y11, x12, y12)
                gfx.line(x21, y21, x22, y22)

            agg_u += du
            iter_count += 1

            if y11 is not None and x12 < -ctx.drawing_width / 2:
                y = (y12 - y11) * (ctx.drawing_width / 2 + x11) / (x11 - x12) + y11
                label = label_fmt_fn(v_minutes, label_fmt)
                gfx.save()
                ctx.mirroring_gfx.translate(-ctx.drawing_width / 2, y)
                text_ang = math.atan2(y11 - y12, x11 - x12)
                if ctx.mirror_y:
                    text_ang = -text_ang
                ctx.mirroring_gfx.rotate(text_ang)
                fh = gfx.gi_default_font_size
                if v >= 0:
                    gfx.text_right(2 * fh / 3, +fh / 3, label)
                else:
                    gfx.text_right(2 * fh / 3, -fh, label)
                gfx.restore()
                break

            x11, y11, z11 = (x12, y12, z12)
            x21, y21, z21 = (x22, y22, z22)

    def draw_single_meridian(self, ctx, to_xyz, u, u_minutes, label_fmt, label_fmt_fn, label_edges, center_v):
        gfx = ctx.gfx
        dv = ctx.field_radius / 10.0
        x11, y11, z11 = to_xyz(u, center_v)
        x21, y21, z21 = x11, y11, z11
        v11 = v21 = center_v
        nzopt = not ctx.transf.is_zoptim()

        x12 = y12 = z12 = None
        x22 = y22 = z22 = None

        while True:
            v12 = v11 + dv
            if v12 >= math.pi/2 and v11 <= math.pi/2:
                v12 = math.pi/2
            if v12 <= math.pi/2:
                x12, y12, z12 = to_xyz(u, v12)
                if nzopt or (z11 > 0 and z12 > 0):
                    gfx.line(x11, y11, x12, y12)

            v22 = v21 - dv
            if v22 <= -math.pi/2 and v21 >= -math.pi/2:
                v22 = -math.pi/2
            if v22 >= -math.pi/2:
                x22, y22, z22 = to_xyz(u, v22)
                if nzopt or (z21 > 0 and z22 > 0):
                    gfx.line(x21, y21, x22, y22)

            if v12 >= math.pi/2 and v22 <= -math.pi/2:
                break

            v11, v21 = v12, v22

            if y12 is not None and y22 is not None and y12 > ctx.drawing_height/2 and y22 < -ctx.drawing_height/2:
                label = label_fmt_fn(u_minutes, label_fmt)
                gfx.save()
                fh = gfx.gi_default_font_size
                top = (label_edges == 'top') or (label_edges == 'auto' and center_v > 0)
                if not top:
                    x = (x12 - x11) * (ctx.drawing_height / 2 - y11) / (y12 - y11) + x11
                    ctx.mirroring_gfx.translate(x, ctx.drawing_height / 2)
                    text_ang = math.atan2(y11 - y12, x11 - x12)
                else:
                    x = (x22 - x21) * (-ctx.drawing_height / 2 - y21) / (y22 - y21) + x21
                    ctx.mirroring_gfx.translate(x, -ctx.drawing_height / 2)
                    text_ang = math.atan2(y21 - y22, x21 - x22)
                if ctx.mirror_x:
                    text_ang = -text_ang
                ctx.mirroring_gfx.rotate(text_ang)
                if ctx.mirror_x:
                    gfx.text_left(-2 * fh / 3, fh / 3, label)
                else:
                    gfx.text_right(2 * fh / 3, fh / 3, label)

                gfx.restore()
                break
            if y12 is not None:
                x11, y11, z11 = (x12, y12, z12)
            if y22 is not None:
                x21, y21, z21 = (x22, y22, z22)

    def grid_alt_label(self, alt_minutes, label_fmt):
        deg = abs(int(alt_minutes/60))
        minutes = abs(alt_minutes) - deg * 60
        prefix = '+' if alt_minutes > 0 else ('-' if alt_minutes < 0 else '')
        return prefix + label_fmt.format(deg, minutes)

    def grid_az_label(self, az_minutes, label_fmt):
        az_deg = (-(az_minutes / 60)) % 360
        deg = int(az_deg)
        minutes = int(round((az_deg - deg) * 60))
        if minutes == 60:
            deg = (deg + 1) % 360
            minutes = 0
        return label_fmt.format(deg, minutes)

    def grid_ra_label(self, ra_minutes, fmt_token):
        hrs = int(ra_minutes // 60)
        mins = int(ra_minutes % 60)
        secs = int(round((ra_minutes - int(ra_minutes)) * 60))

        if secs == 60:
            secs = 0
            mins += 1
        if mins == 60:
            mins = 0
            hrs = (hrs + 1) % 24

        if fmt_token == 'H':
            return f'{hrs}h'
        elif fmt_token == 'HM':
            return f'{hrs}h{mins:02d}m'
        else:  # 'HMS'
            return f'{hrs}h{mins:02d}m{secs:02d}s'

    def grid_dec_label(self, dec_minutes, label_fmt):
        deg = abs(int(dec_minutes/60))
        minutes = abs(dec_minutes) - deg * 60
        if dec_minutes > 0:
            prefix = '+'
        elif dec_minutes < 0:
            prefix = '-'
        else:
            prefix = ''
        return prefix + label_fmt.format(deg, minutes)
