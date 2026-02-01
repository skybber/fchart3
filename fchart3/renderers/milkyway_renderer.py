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

from time import time

import numpy as np

from .base_renderer import BaseRenderer
from ..graphics import DrawMode
from ..i18n import install_translator

_ = install_translator()


class MilkyWayRenderer(BaseRenderer):
    def draw(self, ctx, state):
        cfg = ctx.cfg
        if cfg.show_simple_milky_way:
            self.draw_milky_way(ctx, ctx.used_catalogs.milky_way)
        elif cfg.show_enhanced_milky_way_10k:
            self.draw_enhanced_milky_way(ctx, ctx.used_catalogs.enhanced_milky_way_10k, cfg.use_optimized_mw)
        elif cfg.show_enhanced_milky_way_30k:
            self.draw_enhanced_milky_way(ctx, ctx.used_catalogs.enhanced_milky_way_30k, cfg.use_optimized_mw)

    def draw_milky_way(self, ctx, milky_way_lines):
        gfx = ctx.gfx
        cfg = ctx.cfg

        x, y, z = ctx.transf.np_equatorial_to_xyz(milky_way_lines[:, 0], milky_way_lines[:, 1])

        gfx.set_pen_rgb(cfg.milky_way_color)
        gfx.set_fill_rgb(cfg.milky_way_color)
        gfx.set_linewidth(cfg.milky_way_linewidth)

        polygon = []

        def flush(draw_mode):
            nonlocal polygon
            if len(polygon) > 2 and any(p[2] > 0 for p in polygon):
                gfx.polygon([[p[0], p[1]] for p in polygon], draw_mode)

        for i in range(len(x)):
            if milky_way_lines[i][2] == 0:
                flush(DrawMode.BOTH)
                polygon = []
            polygon.append([x[i].item(), y[i].item(), z[i].item()])

        flush(DrawMode.FILL)

    def draw_enhanced_milky_way(self, ctx, enhanced_milky_way, use_optimized_mw):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.antialias_off()

        tm = time()

        mw_points = enhanced_milky_way.mw_points

        x, y, z = ctx.transf.np_equatorial_to_xyz(mw_points[:, 0], mw_points[:, 1])

        gfx.set_linewidth(0)
        fd = cfg.enhanced_milky_way_fade

        if use_optimized_mw:
            selected_polygons = enhanced_milky_way.select_opti_polygons(ctx.center_equatorial, ctx.field_size)
        else:
            selected_polygons = enhanced_milky_way.select_polygons(ctx.center_equatorial, ctx.field_size)

        fr_x1, fr_y1, fr_x2, fr_y2 = ctx.field_rect_mm

        total_polygons = 0
        zopt = ctx.transf.is_zoptim()
        polygons = []
        poly_buckets = [[] for _ in range(256)]
        rgb_buckets = [None for _ in range(256)]

        for polygon_index in selected_polygons:
            if use_optimized_mw:
                polygon, rgb = enhanced_milky_way.mw_opti_polygons[polygon_index]
            else:
                polygon, rgb = enhanced_milky_way.mw_polygons[polygon_index]

            if zopt and np.min(z[polygon]) < 0:
                continue

            px, py = x[polygon], y[polygon]
            if (px.max() < fr_x1) or (px.min() > fr_x2) or (py.max() < fr_y1) or (py.min() > fr_y2):
                continue

            polygons.append(polygon)
            total_polygons += 1

            r_f = fd[0] + rgb[0] * fd[1]
            g_f = fd[2] + rgb[1] * fd[3]
            b_f = fd[4] + rgb[2] * fd[5]

            brightness = max(r_f, g_f, b_f)
            bucket_index = int(round(brightness * 255))

            if bucket_index < 0:
                bucket_index = 0
            elif bucket_index > 255:
                bucket_index = 255

            poly_buckets[bucket_index].append(polygon)
            if rgb_buckets[bucket_index] is None:
                rgb_buckets[bucket_index] = [r_f, g_f, b_f]
            else:
                rgb_buckets[bucket_index][0] += r_f
                rgb_buckets[bucket_index][1] += g_f
                rgb_buckets[bucket_index][2] += b_f

        for i in range(256):
            bucket_polygons = poly_buckets[i]

            if not bucket_polygons:
                continue
            r = rgb_buckets[i][0] / len(bucket_polygons)
            g = rgb_buckets[i][1] / len(bucket_polygons)
            b = rgb_buckets[i][2] / len(bucket_polygons)
            gfx.set_fill_rgb((r, g, b))
            gfx.polygons_indexed(x, y, bucket_polygons, DrawMode.FILL)

        gfx.antialias_on()
        tmp = str(time()-tm)
        print(_("Enhanced milky way draw within {} s. Total polygons={}".format(tmp, total_polygons)), flush=True)
