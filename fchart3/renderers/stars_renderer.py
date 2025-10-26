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

import numpy as np

from fchart3.graphics_interface import DrawMode

from .base_renderer import BaseRenderer

STAR_LABELS = {
    "alp": "α",
    "bet": "β",
    "gam": "γ",
    "del": "δ",
    "eps": "ε",
    "zet": "ζ",
    "eta": "η",
    "the": "θ",
    "iot": "ι",
    "kap": "κ",
    "lam": "λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "omi": "ο",
    "pi": "π",
    "rho": "ρ",
    "sig": "σ/ς",
    "tau": "τ",
    "ups": "υ",
    "phi": "φ",
    "chi": "χ",
    "psi": "ψ",
    "ome": "ω"
}


class StarsRenderer(BaseRenderer):
    def draw(self, ctx, state):
        # Select and draw stars
        # print('Drawing stars...')

        if ctx.used_catalogs.star_catalog is not None:
            self.draw_stars(ctx, state, ctx.used_catalogs.star_catalog, ctx.used_catalogs.bsc_hip_map)

    def draw_stars(self, ctx, state, star_catalog, bsc_hip_map):
        gfx = ctx.gfx
        cfg = ctx.cfg

        pick_r = cfg.picker_radius if cfg.picker_radius > 0 else 0
        selection = star_catalog.select_stars(ctx.center_equatorial, ctx.field_size, ctx.lm_stars, ctx.precession_matrix)
        if selection is None or len(selection) == 0:
            print('No stars found.')
            return

        # print("Stars selection {} ms".format(str(time()-tm)), flush=True)
        print('{} stars in map.'.format(selection.shape[0]))
        var = str(round(max(selection['mag']), 2))
        print(f'Faintest star : {var}')

        # tm = time()
        points_3d = np.column_stack([selection['x'],
                                     selection['y'],
                                     selection['z']])
        x, y, _ = ctx.transf.np_unit3d_to_xy(points_3d)

        # print("Stars view positioning {} ms".format(str(time()-tm)), flush=True)

        mag = selection['mag']
        hip = selection['hip']

        indices = np.argsort(mag)
        magsorted = mag[indices]
        rsorted = self.magnitude_to_radius(ctx, magsorted)

        if not cfg.star_colors:
            # gfx.set_pen_rgb((cfg.draw_color[0]/3, cfg.draw_color[0]/3, cfg.draw_color[0]/3))
            gfx.set_fill_rgb(cfg.draw_color)

        gfx.set_linewidth(0)

        star_labels = []
        star_mag_defs = []
        pick_min_r = pick_r**2
        x1, y1, x2, y2 = ctx.field_rect_mm
        for i, index in enumerate(indices):
            xx, yy, rr = (x[index].item(), y[index].item(), rsorted[i].item(),)
            if (xx < x1-rr) or (xx > x2+rr) or (yy < y1-rr) or (yy > y2+rr):
                continue
            star_color = star_catalog.get_star_color(selection[index])
            if cfg.show_star_circles:
                self.star(ctx, xx, yy, rr, star_color)

            if pick_r > 0 and abs(xx) < pick_r and abs(yy) < pick_r:
                r = xx**2 + yy**2
                if r < pick_min_r:
                    bsc_star = bsc_hip_map.get(hip[index]) if hip[index] > 0 else None
                    state.picked_star = (xx, yy, rr, mag[index], bsc_star)
                    pick_min_r = r
            elif cfg.show_star_mag:
                star_mag_defs.append((xx, yy, rr, mag[index], star_color))
            elif cfg.show_star_labels:
                if hip[index] > 0:
                    bsc_star = bsc_hip_map.get(hip[index])
                    if bsc_star is not None:
                        if isinstance(bsc_star, str):
                            slabel = bsc_star
                        else:
                            slabel = bsc_star.greek
                            if slabel:
                                slabel = STAR_LABELS[slabel] + bsc_star.greek_no
                            elif cfg.show_flamsteed:
                                slabel = bsc_star.flamsteed
                                if slabel and cfg.flamsteed_numbers_only:
                                    slabel = slabel.split()[0]
                        if slabel:
                            label_length = gfx.text_width(slabel)
                            labelpos_list = self.circular_object_labelpos(ctx, xx, yy, rr, label_length)

                            labelpos = self.find_min_labelpos(state, labelpos_list, label_length, 0)

                            star_labels.append((xx, yy, rr, labelpos, bsc_star))

        if len(star_mag_defs) > 0:
            gfx.set_font(gfx.gi_font, 0.8*gfx.gi_default_font_size)
            for x, y, r, mag, star_color in star_mag_defs:
                diff_mag = ctx.lm_stars - mag
                if diff_mag < 0:
                    diff_mag = 0
                if diff_mag > 5:
                    diff_mag = 5
                star_intensity = 0.4 + 0.6 * diff_mag / 5

                gfx.set_pen_rgb((cfg.label_color[0] * star_intensity,
                                           cfg.label_color[1] * star_intensity,
                                           cfg.label_color[2] * star_intensity))

                self.draw_circular_object_label(ctx, x, y, r, str(mag), set_pen=False)

        if len(star_labels) > 0:
            self.draw_stars_labels(ctx, star_labels)

    def draw_stars_labels(self, ctx, star_labels):
        gfx = ctx.gfx
        cfg = ctx.cfg
        fn = gfx.gi_default_font_size
        printed = {}
        bayer_fh = cfg.bayer_label_font_scale * fn
        flamsteed_fh = cfg.flamsteed_label_font_scale * fn
        for x, y, r, labelpos, star in star_labels:
            if isinstance(star, str):
                gfx.set_font(gfx.gi_font, 0.9*fn)
                self.draw_circular_object_label(ctx, x, y, r, star, labelpos)
            else:
                slabel = star.greek
                if not slabel:
                    is_greek = False
                    if cfg.show_flamsteed:
                        slabel = star.flamsteed
                        if slabel and cfg.flamsteed_numbers_only:
                            slabel = slabel.split()[0]
                else:
                    is_greek = True
                    slabel = STAR_LABELS.get(slabel) + star.greek_no
                if slabel:
                    printed_labels = printed.setdefault(star.constellation, set())
                    if slabel not in printed_labels:
                        printed_labels.add(slabel)
                        if is_greek:
                            gfx.set_font(gfx.gi_font, bayer_fh, cfg.bayer_label_font_style)
                        else:
                            gfx.set_font(gfx.gi_font, flamsteed_fh, cfg.flamsteed_label_font_style)
                        self.draw_circular_object_label(ctx, x, y, r, slabel, labelpos)

    def star(self, ctx, x, y, radius, star_color):
        if ctx.cfg.star_colors and star_color:
            ctx.gfx.set_fill_rgb(star_color)
        r = round(radius, 2)
        ctx.gfx.circle(x, y, r, DrawMode.FILL)

    def draw_picked_star(self, ctx, state):
        gfx = ctx.gfx
        if state.picked_star is not None:
            x, y, r, mag, bsc_star = state.picked_star
            gfx.set_font(gfx.gi_font, 0.9*gfx.gi_default_font_size)
            label = str(mag)
            if bsc_star is not None:
                if bsc_star.greek:
                    label += '(' + STAR_LABELS[bsc_star.greek] + bsc_star.greek_no + ' ' + bsc_star.constellation.capitalize() + ')'
                elif bsc_star.flamsteed:
                    label += '(' + str(bsc_star.flamsteed) + ')'
                elif bsc_star.HD is not None:
                    label += '(HD' + str(bsc_star.HD) + ')'
            self.draw_circular_object_label(ctx, x, y, r, label)

