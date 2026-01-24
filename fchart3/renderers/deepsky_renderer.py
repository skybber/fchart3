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

import numpy as np
import math

from ..astro.np_astrocalc import np_rect_to_sphere
from ..deepsky_object import DsoType

from .base_renderer import BaseRenderer, SQRT2


class DeepskyRenderer(BaseRenderer):
    def draw(self, ctx, state):
        gfx = ctx.gfx
        cfg = ctx.cfg
        if not cfg.show_deepsky or ctx.used_catalogs.deepsky_catalog is None:
            return

        deepsky_list = ctx.used_catalogs.deepsky_catalog.select_deepsky(ctx.center_equatorial, ctx.field_size, ctx.lm_deepsky)

        filtered_showing_dsos = []

        dso_hide_filter_set = {dso for dso in ctx.dso_hide_filter} if ctx.dso_hide_filter else {}

        if ctx.showing_dsos:
            for dso in ctx.showing_dsos:
                if dso not in deepsky_list:
                    filtered_showing_dsos.append(dso)
                if dso in dso_hide_filter_set:
                    dso_hide_filter_set.remove(dso)

        if ctx.dso_highlights:
            for dso_highlight in ctx.dso_highlights:
                for dso in dso_highlight.dsos:
                    if dso not in deepsky_list and dso not in filtered_showing_dsos:
                        filtered_showing_dsos.append(dso)
                    if dso in dso_hide_filter_set:
                        dso_hide_filter_set.remove(dso)

        deepsky_list.sort(key=lambda x: x.mag)
        deepsky_list_ext = []

        self.calc_deepsky_list_ext(ctx, deepsky_list_ext, deepsky_list)
        self.calc_deepsky_list_ext(ctx, deepsky_list_ext, filtered_showing_dsos)

        state.label_potential.add_deepsky_list(deepsky_list_ext)

        # print('Drawing objects...')
        pick_r = cfg.picker_radius if cfg.picker_radius > 0 else 0
        if pick_r > 0:
            pick_min_r = pick_r**2
            for dso, x, y, rlong in deepsky_list_ext:
                if abs(x) < pick_r and abs(y) < pick_r:
                    r = x*x + y*y
                    if r < pick_min_r:
                        state.picked_dso = dso
                        pick_min_r = r

        for dso, x, y, rlong in deepsky_list_ext:
            if dso in dso_hide_filter_set:
                continue

            label = dso.label()
            primary_label = dso.primary_label()

            if cfg.show_dso_mag and dso.mag is not None and dso.mag != -100 and dso.mag < 30:
                label_mag = f'{dso.mag:.1f}'
            else:
                label_mag = None

            if ctx.dso_highlights:
                for dso_highlight in ctx.dso_highlights:
                    if dso in dso_highlight.dsos:
                        self.draw_dso_highlight(ctx, state, x, y, rlong, label, dso_highlight, state.visible_objects_collector)
                        break

            rlong = dso.rlong if dso.rlong is not None else ctx.min_radius
            rshort = dso.rshort if dso.rshort is not None else ctx.min_radius
            if rlong == 0:
                rlong = rshort
            elif rshort == 0:
                rshort = rlong
            rlong = rlong*ctx.drawing_scale
            rshort = rshort*ctx.drawing_scale
            posangle = dso.position_angle+ctx.transf.direction_dtheta(dso.ra, dso.dec)+0.5*np.pi

            if rlong <= ctx.min_radius:
                rshort *= ctx.min_radius/rlong
                rlong = ctx.min_radius

            label_ext = None
            if dso == state.picked_dso and dso.mag < 30.0:
                label_mag = f'{dso.mag:.2f}m'

            label_length = gfx.text_width(label)

            if dso.type == DsoType.G:
                labelpos_list = self.galaxy_labelpos(ctx, x, y, rlong, rshort, posangle, label_length)
            elif dso.type == DsoType.N:
                labelpos_list = self.diffuse_nebula_labelpos(ctx, x, y, 2.0*rlong, 2.0*rshort, posangle, label_length)
            elif dso.type in [DsoType.PN, DsoType.OC, DsoType.GC, DsoType.SNR, DsoType.GALCL]:
                labelpos_list = self.circular_object_labelpos(ctx, x, y, rlong, label_length)
            elif dso.type == DsoType.STARS:
                labelpos_list = self.asterism_labelpos(ctx, x, y, rlong, label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(ctx, x, y, rlong, label_length)

            labelpos = self.find_min_labelpos(state, labelpos_list, label_length)

            if dso.type == DsoType.G:
                self.galaxy(ctx, x, y, rlong, rshort, posangle, dso.mag, label, label_mag, label_ext, labelpos)
            elif dso.type == DsoType.N:
                has_outlines = False
                if cfg.show_nebula_outlines and dso.outlines is not None and rlong > ctx.min_radius:
                    has_outlines = self.draw_dso_outlines(ctx, dso, x, y, rlong, rshort, posangle, label, label_ext, labelpos)
                if not has_outlines:
                    self.diffuse_nebula(ctx, x, y, 2.0*rlong, 2.0*rshort, posangle, label, label_mag, label_ext, labelpos)
            elif dso.type == DsoType.PN:
                self.planetary_nebula(ctx, x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == DsoType.OC:
                if cfg.show_nebula_outlines and dso.outlines is not None:
                    self.draw_dso_outlines(ctx, dso, x, y, rlong, rshort)
                self.open_cluster(ctx, x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == DsoType.GC:
                self.globular_cluster(ctx, x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == DsoType.STARS:
                self.asterism(ctx, x, y, rlong, label, label_ext, labelpos)
            elif dso.type == DsoType.SNR:
                self.supernova_remnant(ctx, x, y, rlong, label, label_ext, labelpos)
            elif dso.type == DsoType.GALCL:
                self.galaxy_cluster(ctx, x, y, rlong, label, label_ext, labelpos)
            else:
                self.unknown_object(ctx, x, y, rlong, label, label_ext, labelpos)

            if self.collect_visible_object(ctx, state, x, y, rlong, primary_label):
                if state.picked_dso == dso:
                    pick_xp1, pick_yp1 = gfx.to_pixel(-pick_r, -pick_r)
                    pick_xp2, pick_yp2 = gfx.to_pixel(pick_r, pick_r)
                    pick_xp1, pick_yp1, pick_xp2, pick_yp2 = self.align_rect_coords(pick_xp1, pick_yp1, pick_xp2, pick_yp2)
                    state.visible_objects_collector.append([rlong, primary_label.replace(' ', ''), pick_xp1, pick_yp1, pick_xp2, pick_yp2])

    def calc_deepsky_list_ext(self, ctx, deepsky_list_ext, dso_list):
        if ctx.precession_matrix is not None:
            mat_rect_dso = np.empty([len(dso_list), 3])
            for i, dso in enumerate(dso_list):
               mat_rect_dso[i] = [dso.x, dso.y, dso.z]
            mat_rect_dso = np.matmul(mat_rect_dso, ctx.precession_matrix)
            ra_ar, dec_ar = np_rect_to_sphere(mat_rect_dso[:,[0]], mat_rect_dso[:,[1]], mat_rect_dso[:,[2]])
        else:
            ra_ar = np.array([dso.ra for dso in dso_list])
            dec_ar = np.array([dso.dec for dso in dso_list])

        x, y, z = ctx.transf.np_equatorial_to_xyz(ra_ar, dec_ar)
        nzopt = not ctx.transf.is_zoptim()

        for i, dso in enumerate(dso_list):
            if nzopt or z[i] > 0:
                if dso.rlong is None:
                    rlong = ctx.min_radius
                else:
                    rlong = dso.rlong*ctx.drawing_scale
                    if rlong < ctx.min_radius:
                        rlong = ctx.min_radius
                deepsky_list_ext.append((dso, x[i], y[i], rlong))

    def draw_dso_outlines(self, ctx, dso, x, y, rlong, rshort, posangle=None, label=None, label_ext=None,  labelpos=None):
        lev_shift = 0
        has_outlines = False
        draw_label = True
        for outl_lev in range(2, -1, -1):
            outlines_ar = dso.outlines[outl_lev]
            if outlines_ar:
                has_outlines = True
                for outlines in outlines_ar:
                    x_outl, y_outl = ctx.transf.np_equatorial_to_xy(outlines[0], outlines[1])
                    self.diffuse_nebula_outlines(ctx, x, y, x_outl, y_outl, outl_lev+lev_shift, 2.0*rlong, 2.0*rshort, posangle,
                                                 label, label_ext, draw_label, labelpos)
                    draw_label = False
            else:
                lev_shift += 1
        return has_outlines

    def open_cluster(self, ctx, x, y, radius, label, label_mag, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0

        gfx.set_pen_rgb(cfg.star_cluster_color)
        gfx.set_linewidth(cfg.open_cluster_linewidth)
        gfx.set_dashed_line(0.6, 0.4)

        gfx.circle(x, y, r)
        label_fh = self.set_label_font(ctx, label_ext)

        self.draw_circular_object_label(ctx, x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(ctx, x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)
        if not label_ext and label_mag:
            gfx.set_font(gfx.gi_font, label_fh*0.8, cfg.dso_label_font_style)
            self.draw_circular_object_label(ctx, x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def galaxy_cluster(self, ctx, x, y, radius, label, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0

        gfx.set_pen_rgb(cfg.galaxy_cluster_color)
        gfx.set_linewidth(cfg.galaxy_cluster_linewidth)
        gfx.set_dashed_line(0.5, 2.0)

        gfx.circle(x, y, r)
        label_fh = self.set_label_font(ctx, label_ext)

        self.draw_circular_object_label(ctx, x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(ctx, x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

    def asterism(self, ctx, x, y, radius, label, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0
        d = r / SQRT2

        gfx.set_pen_rgb(cfg.star_cluster_color)
        gfx.set_linewidth(cfg.open_cluster_linewidth)
        gfx.set_dashed_line(0.6, 0.4)

        diff = gfx.gi_linewidth / (2 * SQRT2)

        gfx.line(x-diff, y+d+diff, x+d+diff, y-diff)
        gfx.line(x+d, y, x, y-d)
        gfx.line(x+diff, y-d-diff, x-d-diff, y+diff)
        gfx.line(x-d, y, x, y+d)

        label_fh = self.set_label_font(ctx, label_ext)

        if label:
            gfx.set_pen_rgb(cfg.label_color)
            self.draw_asterism_label(ctx, x, y, label, labelpos, d, label_fh)

        if label_ext:
            gfx.set_pen_rgb(cfg.label_color)
            self.draw_asterism_label(ctx, x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)

    def draw_asterism_label(self, ctx, x, y, label, labelpos, d, fh):
        gfx = ctx.gfx
        cfg = ctx.cfg

        if labelpos == 0 or labelpos == -1:
            gfx.text_centred(x, y-d-2*fh/3.0, label)
        elif labelpos == 1:
            gfx.text_centred(x, y+d+fh/3.0, label)
        elif labelpos == 2:
            gfx.text_left(x-d-fh/6.0, y-fh/3.0, label)
        elif labelpos == 3:
            gfx.text_right(x+d+fh/6.0, y-fh/3.0, label)

    def asterism_labelpos(self, ctx, x, y, radius=-1, label_length=0.0):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0
        d = r / SQRT2
        fh = gfx.gi_default_font_size
        label_pos_list = []
        yy = y - d - 2*fh/3.0
        label_pos_list.append(((x - label_length / 2.0, yy), (x, yy), (x + label_length, yy)))

        yy = y + d + 2*fh/3.0
        label_pos_list.append(((x - label_length / 2.0, yy), (x, yy), (x + label_length, yy)))

        xx = x - d - fh/6.0
        yy = y
        label_pos_list.append(((xx - label_length, yy), (xx - label_length / 2.0, yy), (xx, yy)))

        xx = x + d + fh/6.0
        yy = y
        label_pos_list.append(((xx, yy), (xx + label_length / 2.0, yy), (xx + label_length, yy)))

        return label_pos_list

    def draw_galaxy_label(self, ctx, x, y, label, labelpos, rlong, rshort, fh):
        gfx = ctx.gfx
        cfg = ctx.cfg

        if labelpos == 0 or labelpos == -1:
            gfx.text_centred(0, -rshort-0.5*fh, label)
        elif labelpos == 1:
            gfx.text_centred(0, +rshort+0.5*fh, label)
        elif labelpos == 2:
            gfx.text_right(rlong+fh/6.0, -fh/3.0, label)
        elif labelpos == 3:
            gfx.text_left(-rlong-fh/6.0, -fh/3.0, label)

    def galaxy(self, ctx, x, y, rlong, rshort, posangle, mag, label, label_mag, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = ctx.drawing_width/40.0
            rs = rl/2.0
        if (rlong > 0.0) and (rshort < 0.0):
            rl = rlong
            rs = rlong/2.0

        gfx.save()

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        if cfg.dso_dynamic_brightness and (mag is not None) and ctx.lm_deepsky >= 10.0 and label_ext is None:
            fac = ctx.lm_deepsky - 8.0
            if fac > 5:
                fac = 5.0
            diff_mag = ctx.lm_deepsky - mag
            if diff_mag < 0:
                diff_mag = 0
            if diff_mag > 5:
                diff_mag = 5
            dso_intensity = 1.0 if diff_mag > fac else 0.5 + 0.5 * diff_mag / fac
        else:
            dso_intensity = 1.0

        gfx.set_pen_rgb((cfg.galaxy_color[0]*dso_intensity,
                                   cfg.galaxy_color[1]*dso_intensity,
                                   cfg.galaxy_color[2]*dso_intensity))

        p = posangle
        if posangle >= 0.5*math.pi:
            p += math.pi
        if posangle < -0.5*math.pi:
            p -= math.pi

        ctx.mirroring_gfx.ellipse(x, y, rl, rs, p)

        if label or label_ext:
            ctx.mirroring_gfx.translate(x, y)
            ctx.mirroring_gfx.rotate(p)
            gfx.set_pen_rgb((cfg.label_color[0]*dso_intensity,
                                       cfg.label_color[1]*dso_intensity,
                                       cfg.label_color[2]*dso_intensity))
            label_fh = self.set_label_font(ctx, label_ext)
            if label:
                self.draw_galaxy_label(ctx, x, y, label, labelpos, rlong, rshort, label_fh)
            if label_ext:
                self.draw_galaxy_label(ctx, x, y, label_ext, self.to_ext_labelpos(labelpos), rlong, rshort, label_fh)
            if not label_ext and label_mag:
                ctx.mirroring_gfx.translate(0, -label_fh*0.9)
                gfx.set_font(gfx.gi_font, label_fh*0.8, cfg.dso_label_font_style)
                self.draw_galaxy_label(ctx, x, y, label_mag, labelpos, rlong, rshort, label_fh)

        gfx.restore()

    def galaxy_labelpos(self, ctx, x, y, rlong=-1, rshort=-1, posangle=0.0, label_length=0.0):
        gfx = ctx.gfx
        cfg = ctx.cfg

        p = posangle
        if posangle >= 0.5*math.pi:
            p += math.pi
        if posangle < -0.5*math.pi:
            p -= math.pi

        fh = gfx.gi_default_font_size
        label_pos_list = []

        sp = math.sin(p)
        cp = math.cos(p)

        hl = label_length/2.0

        d = -rshort-0.5*fh
        xc = x + d*sp
        yc = y - d*cp
        xs = xc - hl*cp
        ys = yc - hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs, ys], [xc, yc], [xe, ye]])

        xc = x - d*sp
        yc = y + d*cp
        xs = xc - hl*cp
        ys = yc - hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs, ys], [xc, yc], [xe, ye]])

        d = rlong+fh/6.0
        xs = x + d*cp
        ys = y + d*sp
        xc = xs + hl*cp
        yc = ys + hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs, ys], [xc, yc], [xe, ye]])

        xe = x - d*cp
        ye = y - d*sp
        xc = xe - hl*cp
        yc = ye - hl*sp
        xs = xc - hl*cp
        ys = yc - hl*sp
        label_pos_list.append([[xs, ys], [xc, yc], [xe, ye]])
        return label_pos_list

    def globular_cluster(self, ctx, x, y, radius, label, label_mag, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.star_cluster_color)

        gfx.circle(x, y, r)
        gfx.line(x-r, y, x+r, y)
        gfx.line(x, y-r, x, y+r)

        label_fh = self.set_label_font(ctx, label_ext)

        self.draw_circular_object_label(ctx, x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(ctx, x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

        if not label_ext and label_mag:
            gfx.set_font(gfx.gi_font, label_fh*0.8, cfg.dso_label_font_style)
            self.draw_circular_object_label(ctx, x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def diffuse_nebula(self, ctx, x, y, width, height, posangle, label, label_mag, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_linewidth(cfg.nebula_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.nebula_color)

        d = 0.5*width
        if width < 0.0:
            d = ctx.drawing_width/40.0
        d1 = d+gfx.gi_linewidth/2.0

        gfx.line(x-d1, y+d, x+d1, y+d)
        gfx.line(x+d, y+d, x+d, y-d)
        gfx.line(x+d1, y-d, x-d1, y-d)
        gfx.line(x-d, y-d, x-d, y+d)

        label_fh = self.set_label_font(ctx, label_ext)

        gfx.set_pen_rgb(cfg.label_color)
        if label:
            self.draw_diffuse_nebula_label(ctx, x, y, label, labelpos, d, label_fh)
        if label_ext:
            self.draw_diffuse_nebula_label(ctx, x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)
        if not label_ext and label_mag:
            gfx.set_font(gfx.gi_font, label_fh*0.8, cfg.dso_label_font_style)
            self.draw_diffuse_nebula_label(ctx, x, y-0.9*label_fh, label_mag, labelpos, d, label_fh)

    def draw_diffuse_nebula_label(self, ctx, x, y, label, labelpos, d, fh):
        gfx = ctx.gfx

        if labelpos == 0 or labelpos == -1:
            gfx.text_centred(x, y-d-fh/2.0, label)
        elif labelpos == 1:
            gfx.text_centred(x, y+d+fh/2.0, label)
        elif labelpos == 2:
            gfx.text_left(x-d-fh/6.0, y-fh/3.0, label)
        elif labelpos == 3:
            gfx.text_right(x+d+fh/6.0, y-fh/3.0, label)

    def diffuse_nebula_outlines(self, ctx, x, y, x_outl, y_outl, outl_lev, width, height, posangle, label, label_ext,
                                draw_label, labelpos=''):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_linewidth(cfg.nebula_linewidth)
        gfx.set_solid_line()

        if cfg.light_mode:
            frac = 4 - 1.5 * outl_lev  # no logic, look nice in light mode
            pen_r = 1.0 - ((1.0 - cfg.nebula_color[0]) / frac)
            pen_g = 1.0 - ((1.0 - cfg.nebula_color[1]) / frac)
            pen_b = 1.0 - ((1.0 - cfg.nebula_color[2]) / frac)
        else:
            frac = 4 - 1.5 * outl_lev  # no logic, look nice in dark mode
            pen_r = cfg.nebula_color[0] / frac
            pen_g = cfg.nebula_color[1] / frac
            pen_b = cfg.nebula_color[2] / frac

        gfx.set_pen_rgb((pen_r, pen_g, pen_b))

        d = 0.5*width
        if width < 0.0:
            d = ctx.drawing_width/40.0

        for i in range(len(x_outl)-1):
            gfx.line(x_outl[i].item(), y_outl[i].item(), x_outl[i+1].item(), y_outl[i+1].item())
        gfx.line(x_outl[len(x_outl)-1].item(), y_outl[len(x_outl)-1].item(), x_outl[0].item(), y_outl[0].item())

        if draw_label:
            label_fh = self.set_label_font(ctx, label_ext, scale=cfg.outlined_dso_label_font_scale)
            gfx.set_pen_rgb(cfg.label_color)
            if label:
                self.draw_diffuse_nebula_label(ctx, x, y, label, labelpos, d, label_fh)
            if label_ext:
                self.draw_diffuse_nebula_label(ctx, x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)

    def diffuse_nebula_labelpos(self, ctx, x, y, width=-1.0, height=-1.0, posangle=0.0, label_length=0.0):
        gfx = ctx.gfx

        d = 0.5*width
        if width < 0.0:
            d = ctx.drawing_width/40.0
        fh = gfx.gi_default_font_size

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y - d - fh/2.0
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        ys = y + d + fh/2.0
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        return label_pos_list

    def planetary_nebula(self, ctx,  x, y, radius, label, label_mag, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.nebula_color)

        gfx.circle(x, y, 0.75*r)
        gfx.line(x-0.75*r, y, x-1.5*r, y)
        gfx.line(x+0.75*r, y, x+1.5*r, y)
        gfx.line(x, y+0.75*r, x, y+1.5*r)
        gfx.line(x, y-0.75*r, x, y-1.5*r)

        label_fh = self.set_label_font(ctx, label_ext)

        self.draw_circular_object_label(ctx, x, y, r, label, labelpos, label_fh)

        if label_ext:
            self.draw_circular_object_label(ctx, x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)
        if not label_ext and label_mag:
            gfx.set_font(gfx.gi_font, label_fh*0.8, cfg.dso_label_font_style)
            self.draw_circular_object_label(ctx, x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def supernova_remnant(self, ctx, x, y, radius, label, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius if radius > 0 else ctx.drawing_width/40.0

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.nebula_color)

        gfx.circle(x, y, r-gfx.gi_linewidth/2.0)

        label_fh = self.set_label_font(ctx, label_ext, style=cfg.dso_label_font_style)

        self.draw_circular_object_label(ctx, x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(ctx, x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

    def unknown_object(self, ctx, x, y, radius, label, label_ext, labelpos):
        gfx = ctx.gfx
        cfg = ctx.cfg

        r = radius
        if radius <= 0.0:
            r = ctx.drawing_width/40.0

        r /= SQRT2

        gfx.set_linewidth(cfg.dso_linewidth)
        gfx.set_solid_line()
        gfx.set_pen_rgb(cfg.dso_color)

        gfx.line(x-r, y+r, x+r, y-r)
        gfx.line(x+r, y+r, x-r, y-r)

        fh = gfx.gi_default_font_size

        if label != '':
            gfx.set_pen_rgb(cfg.label_color)
            if labelpos == 0:
                gfx.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos == 1:
                gfx.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                gfx.text_centred(x, y + r + fh/2.0, label)
            else:
                gfx.text_centred(x, y - r - fh/2.0, label)

    def unknown_object_labelpos(self, ctx, x, y, radius=-1, label_length=0.0):
        gfx = ctx.gfx

        r = radius
        if radius <= 0.0:
            r = ctx.drawing_width/40.0
        fh = gfx.gi_default_font_size
        r /= SQRT2
        label_pos_list = []
        xs = x + r + fh/6.0
        ys = y
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        xs = x - r - fh/6.0 - label_length
        ys = y
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        xs = x - label_length/2.0
        ys = y + r + fh/2.0
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        xs = x - label_length/2.0
        ys = y - r - fh/2.0
        label_pos_list.append(((xs, ys), (xs + label_length / 2.0, ys), (xs + label_length, ys)))

        return label_pos_list

    def draw_dso_highlight(self, ctx, state, x, y, rlong, dso_name, dso_highligth, visible_objects_collector):
        gfx = ctx.gfx
        cfg = ctx.cfg

        gfx.set_pen_rgb(dso_highligth.color)
        gfx.set_linewidth(dso_highligth.line_width)
        if dso_highligth.dash and len(dso_highligth.dash) == 2:
            gfx.set_dashed_line(dso_highligth.dash[0], dso_highligth.dash[1])
        else:
            gfx.set_solid_line()

        r = cfg.font_size
        gfx.circle(x, y, r)
        self.collect_visible_object(ctx, state, x, y, r, dso_name)
