#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2024 fchart authors
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

SQRT2 = math.sqrt(2)

MAG_SCALE_X = [0, 1,   2,   3,   4,    5,    25]
MAG_SCALE_Y = [0, 1.8, 3.3, 4.7, 6,  7.2,  18.0]


def interp_magnitude_to_radius(lm_stars, star_mag_r_shift, magnitude):
    mag_d = lm_stars - np.clip(magnitude, a_min=None, a_max=lm_stars)
    mag_s = np.interp(mag_d, MAG_SCALE_X, MAG_SCALE_Y)
    radius = 0.1 * 1.33 ** mag_s + star_mag_r_shift
    return radius


class BaseRenderer:
    def draw(self, ctx, state):
        pass

    def magnitude_to_radius(self, ctx, magnitude):
        return interp_magnitude_to_radius(ctx.lm_stars, ctx.star_mag_r_shift, magnitude)

    def draw_circular_object_label(self, ctx, x, y, r, label, labelpos=-1, fh=None, set_pen=True):
        gfx = ctx.gfx
        if fh is None:
            fh = gfx.gi_default_font_size
        if label:
            if set_pen:
                gfx.set_pen_rgb(ctx.cfg.label_color)
            arg = 1.0-2*fh/(3.0*r)
            if (arg < 1.0) and (arg > -1.0):
                a = math.acos(arg)
            else:
                a = 0.5*math.pi
            if labelpos == 0 or labelpos == -1:
                gfx.text_right(x+math.sin(a)*r+fh/6.0, y-r, label)
            elif labelpos == 1:
                gfx.text_left(x-math.sin(a)*r-fh/6.0, y-r, label)
            elif labelpos == 2:
                gfx.text_right(x+math.sin(a)*r+fh/6.0, y+r-2*fh/3.0, label)
            elif labelpos == 3:
                gfx.text_left(x-math.sin(a)*r-fh/6.0, y+r-2*fh/3.0, label)

    def circular_object_labelpos(self, ctx, x, y, radius=-1.0, label_length=0.0):
        fh = ctx.gfx.gi_default_font_size
        r = radius if radius > 0 else ctx.drawing_width/40.0

        arg = 1.0-2*fh/(3.0*r)

        if (arg < 1.0) and (arg > -1.0):
            a = math.acos(arg)
        else:
            a = 0.5*math.pi

        label_pos_list = []
        x1 = x+math.sin(a)*r+fh/6.0
        x2 = x-math.sin(a)*r-fh/6.0 - label_length
        y1 = y-r+fh/3.0
        y2 = y+r-fh/3.0

        label_pos_list.append(((x1, y1), (x1 + label_length / 2.0, y1), (x1 + label_length, y1)))
        label_pos_list.append(((x2, y1), (x2 + label_length / 2.0, y1), (x2 + label_length, y1)))
        label_pos_list.append(((x1, y2), (x1 + label_length / 2.0, y2), (x1 + label_length, y2)))
        label_pos_list.append(((x2, y2), (x2 + label_length / 2.0, y2), (x2 + label_length, y2)))

        return label_pos_list

    def find_min_labelpos(self, state, labelpos_list, label_length, favour_right=False, favour_index=-1):
        pot = float('inf')
        result = 0

        for labelpos_index, (pos1, pos2, pos3) in enumerate(labelpos_list):
            x2, y2 = pos2
            pot1 = state.label_potential.compute_potential(x2, y2)
            if favour_index == labelpos_index:
                pot1 *= 0.6
            if pot1 < pot:
                pot = pot1
                result = labelpos_index

        lx, ly = labelpos_list[result][1]
        state.label_potential.add_position(lx, ly, label_length)
        return result
    
    def set_label_font(self, ctx, extended, style=None, scale=1.0):
        gfx = ctx.gfx
        if extended:
            fh = ctx.cfg.ext_label_font_scale * gfx.gi_default_font_size
        else:
            fh = gfx.gi_default_font_size * scale
        gfx.set_font(gfx.gi_font, fh, style or ctx.cfg.dso_label_font_style)
        return fh

    def to_ext_labelpos(self, labelpos):
        if labelpos == 0:
            return 1
        if labelpos == 1:
            return 0
        if labelpos == 2:
            return 3
        if labelpos == 3:
            return 2
        return 1

    def collect_visible_object(self, ctx, state, x, y, r, label):
        gfx = ctx.gfx
        if state.visible_objects_collector is not None:
            xs1, ys1 = x - r, y - r
            xs2, ys2 = x + r, y + r
            if gfx.on_screen(xs1, ys1) or gfx.on_screen(xs2, ys2):
                xp1, yp1 = gfx.to_pixel(xs1, ys1)
                xp2, yp2 = gfx.to_pixel(xs2, ys2)
                xp1, yp1, xp2, yp2 = self.align_rect_coords(xp1, yp1, xp2, yp2)
                state.visible_objects_collector.append([r, label.replace(' ', ''), xp1, yp1, xp2, yp2])
                return True
        return False

    def align_rect_coords(self, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return x1, y1, x2, y2

