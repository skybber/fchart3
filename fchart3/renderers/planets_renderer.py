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

from ..astrocalc import angular_distance, pos_angle
from ..solar_system_body import SolarSystemBody
from ..graphics import DrawMode

from .base_renderer import BaseRenderer


class PlanetsRenderer(BaseRenderer):
    def draw(self, ctx, state):
        planet_moon_positions = None
        if ctx.planet_moons:
            planet_moon_positions = self.calc_planet_moons_positions(ctx, state)
            self.draw_planet_moons(ctx, state, planet_moon_positions, False)

        if ctx.solsys_bodies:
            self.draw_solar_system_bodies(ctx, state)

        if ctx.planet_moons:
            self.draw_planet_moons(ctx, state, planet_moon_positions, True)

    def draw_planet_moons(self, ctx, state, planet_moon_positions, in_front):
        solsys_bodies = ctx.solsys_bodies
        planet_moons = ctx.planet_moons
        
        if not in_front and not ctx.solsys_bodies:
            return
        
        gfx = ctx.gfx

        nzopt = not ctx.transf.is_zoptim()
        gfx.set_font(gfx.gi_font, 0.8 * gfx.gi_default_font_size)

        planet_map = {sl_body.solar_system_body: sl_body for sl_body in solsys_bodies} if solsys_bodies else {}

        for pl_moon_index, pl_moon in enumerate(planet_moons):
            planet = planet_map.get(pl_moon.planet)

            if planet is not None:
                if in_front:
                    if pl_moon.distance >= planet.distance:
                        continue
                else:
                    if pl_moon.distance <= planet.distance:
                        continue

            x, y, z = planet_moon_positions[pl_moon_index]

            if nzopt or z >= 0:
                r = self.magnitude_to_radius(ctx, pl_moon.mag)
                gfx.set_fill_rgb(pl_moon.color)
                gfx.circle(x, y, r, DrawMode.FILL)
                pl_moon_ang_dist = angular_distance((pl_moon.ra, pl_moon.dec), (planet.ra, planet.dec))
                r_lab = r if r > 0.8 else 0.8

                if pl_moon_ang_dist > 0.02 * ctx.field_size:
                    gfx.set_pen_rgb(ctx.cfg.label_color)
                    label_length = gfx.text_width(pl_moon.moon_name)
                    labelpos_list = self.planet_labelpos(ctx, x, y, r_lab, label_length, 0.75, False)
                    labelpos = self.find_min_labelpos(state, labelpos_list, label_length, favour_index=2)

                    self.draw_planet_label(ctx, x, y, r_lab, pl_moon.moon_name, labelpos, 0.75)
                    if state.picked_planet_moon == pl_moon:
                        ext_label = '{:.2f}'.format(pl_moon.mag)
                        self.draw_planet_label(ctx, x, y, r_lab, ext_label, self.to_ext_labelpos(labelpos), 0.75)

                self.collect_visible_object(ctx, state, x, y, r_lab, pl_moon.moon_name)

    def draw_solar_system_bodies(self, ctx, state):
        solsys_bodies = ctx.solsys_bodies
        gfx = ctx.gfx

        nzopt = not ctx.transf.is_zoptim()

        sun = next(b for b in solsys_bodies if b.solar_system_body == SolarSystemBody.SUN)

        gfx.set_font(gfx.gi_font, gfx.gi_default_font_size)

        for ssb_obj in solsys_bodies:
            rax = ssb_obj.ra
            decx = ssb_obj.dec
            solar_system_body = ssb_obj.solar_system_body

            x, y, z = ctx.transf.equatorial_to_xyz(rax, decx)

            if nzopt or z >= 0:
                color_attr = solar_system_body.name.lower() + '_color'
                color = getattr(ctx.cfg, color_attr)

                if solar_system_body in (SolarSystemBody.SUN, SolarSystemBody.MOON):
                    fix_r = round(1.75 * ctx.min_radius, 2)
                else:
                    r_scale_attr = solar_system_body.name.lower() + '_r_scale'
                    r_scale_conf = getattr(ctx.cfg, r_scale_attr)
                    fix_r = round(1.2 * r_scale_conf * ctx.min_radius, 2)

                cur_r = ssb_obj.angular_radius * ctx.drawing_scale
                r = max(fix_r, cur_r)

                if ssb_obj.solar_system_body == SolarSystemBody.SATURN:
                    self.draw_ring(ctx, x, y, cur_r, color, ssb_obj.ring_tilt, ssb_obj.north_pole_pa, False)

                if ssb_obj.solar_system_body == SolarSystemBody.MOON:
                    body_r_scale = ctx.cfg.moon_r_scale
                else:
                    body_r_scale = 1.0

                if solar_system_body in [SolarSystemBody.MOON,
                                         SolarSystemBody.MERCURY,
                                         SolarSystemBody.VENUS,
                                         SolarSystemBody.MARS]:
                    self.draw_phase(ctx, x, y, r, ssb_obj, sun, color, body_r_scale)
                else:
                    gfx.set_fill_rgb(color)
                    gfx.circle(x, y, r, DrawMode.FILL)

                if ssb_obj.solar_system_body == SolarSystemBody.SATURN:
                    self.draw_ring(ctx, x, y, cur_r, color, ssb_obj.ring_tilt, ssb_obj.north_pole_pa, True)
                    r_scale = 1.1
                else:
                    r_scale = body_r_scale

                label = solar_system_body.label
                if ssb_obj.solar_system_body == SolarSystemBody.MOON and body_r_scale != 1.0:
                    label += 'x{:.1f}'.format(body_r_scale)

                gfx.set_pen_rgb(ctx.cfg.label_color)

                label_length = gfx.text_width(label)
                scaled_r = r * r_scale
                labelpos_list = self.planet_labelpos(ctx, x, y, scaled_r, label_length, 1.0, True)
                labelpos = self.find_min_labelpos(state, labelpos_list, label_length, favour_index=0)
                self.draw_planet_label(ctx, x, y, r, label, labelpos, 1.0)

                if solar_system_body not in [SolarSystemBody.MOON, SolarSystemBody.SUN]:
                    self.collect_visible_object(ctx, state, x, y, scaled_r, solar_system_body.label.lower())

    def draw_phase(self, ctx, x, y, r, ssb_obj, sun, color, body_r_scale):
        gfx = ctx.gfx
        dk = 0.1
        gfx.set_fill_rgb((color[0] * dk, color[1] * dk, color[2] * dk,))
        gfx.circle(x, y, r * body_r_scale, DrawMode.FILL)

        illuminated_frac = (1 + math.cos(ssb_obj.phase)) / 2

        if illuminated_frac < 0.01:
            return

        sun_angle = pos_angle(ssb_obj.ra, ssb_obj.dec, sun.ra, sun.dec) - math.pi/2

        if sun_angle < 0:
            sun_angle += 2 * math.pi


        gfx.set_fill_rgb(color)
        gfx.save()

        gfx.translate(x, y)
        gfx.rotate(sun_angle)

        gfx.begin_path()

        scaled_r = r * body_r_scale
        gfx.move_to(0, scaled_r)

        rshort = (1 - 2 * illuminated_frac) * scaled_r

        gfx.arc_to(0, 0, scaled_r, -math.pi / 2, math.pi / 2)

        if illuminated_frac < 0.5:
            gfx.elliptic_arc_to(0, 0, rshort, scaled_r, math.pi/2, -math.pi/2)
        else:
            gfx.elliptic_arc_to(0, 0, -rshort, scaled_r, math.pi/2, 3*math.pi/2)

        gfx.complete_path(DrawMode.FILL)
        gfx.restore()

    def draw_ring(self, ctx, x, y, cur_r, color, ring_tilt, north_pole_pa, is_front):
        gfx = ctx.gfx
        inner_1 = 1.53 * cur_r
        inner_2 = 1.95 * cur_r

        outer_1 = 2.04 * cur_r
        outer_2 = 2.28 * cur_r

        r_scale = math.sin(ring_tilt)

        ring_r = min(color[0] * 1.1, 1.0)
        ring_g = min(color[1] * 1.2, 1.0)
        ring_b = min(color[2] * 1.3, 1.0)
        gfx.set_fill_rgb((ring_r, ring_g, ring_b,))

        gfx.save()

        gfx.translate(x, y)

        if north_pole_pa is not None:
            if ctx.mirror_y:
                north_pole_pa = -north_pole_pa
            if ctx.mirror_x:
                north_pole_pa = math.pi - north_pole_pa
            gfx.rotate(north_pole_pa)
        else:
            gfx.rotate(0.0)

        gfx.begin_path()

        ang_orient = 1.0 if is_front else -1.0

        gfx.move_to(inner_1, 0)
        gfx.elliptic_arc_to(0, 0, inner_1, inner_1*r_scale, 0, ang_orient * math.pi)
        gfx.line_to(-inner_2, 0)
        gfx.elliptic_arc_to(0, 0, inner_2, inner_2*r_scale, ang_orient * math.pi, 0)
        gfx.line_to(inner_1, 0)
        gfx.complete_path(DrawMode.FILL)

        gfx.begin_path()
        gfx.move_to(outer_1, 0)
        gfx.elliptic_arc_to(0, 0, outer_1, outer_1*r_scale, 0, ang_orient * math.pi)
        gfx.line_to(-outer_2, 0)
        gfx.elliptic_arc_to(0, 0, outer_2, outer_2*r_scale, ang_orient * math.pi, 0)
        gfx.line_to(outer_1, 0)
        gfx.complete_path(DrawMode.FILL)

        gfx.restore()

    def draw_planet_label(self, ctx, x, y, r, label, labelpos, font_scale):
        gfx = ctx.gfx
        fh = gfx.gi_default_font_size * font_scale
        arg = 1.0-2*fh/(3.0*r)
        arg = max(-1.0, min(1.0, arg))
        a = math.acos(arg)

        if labelpos == 0:
            gfx.text_centred(x, y + r + 0.75 * fh, label)
        elif labelpos == 1:
            gfx.text_centred(x, y - r - 0.75 * fh, label)
        elif labelpos == 2:
            gfx.text_right(x+math.sin(a)*r+fh/6.0, y-r, label)
        elif labelpos == 3:
            gfx.text_left(x-math.sin(a)*r-fh/6.0, y-r, label)
        elif labelpos == 4:
            gfx.text_right(x+math.sin(a)*r+fh/6.0, y+r-2*fh/3.0, label)
        elif labelpos == 5:
            gfx.text_left(x-math.sin(a)*r-fh/6.0, y+r-2*fh/3.0, label)

    def planet_labelpos(self, ctx, x, y, radius, label_length, font_scale, top_down_only):
        gfx = ctx.gfx
        fh = gfx.gi_default_font_size * font_scale
        r = radius if radius > 0 else ctx.drawing_width/40.0

        arg = 1.0-2*fh/(3.0*r)

        if (arg < 1.0) and (arg > -1.0):
            a = math.acos(arg)
        else:
            a = 0.5*math.pi

        label_pos_list = []

        y3 = y + r + 0.75 * fh
        label_pos_list.append(((x-label_length/2, y3), (x, y3), (x+label_length/2, y3)))
        y4 = y - r - 0.75 * fh
        label_pos_list.append(((x-label_length/2, y4), (x, y4), (x+label_length/2, y4)))

        if not top_down_only:
            x1 = x+math.sin(a)*r+fh/6.0
            x2 = x-math.sin(a)*r-fh/6.0 - label_length
            y1 = y-r+fh/3.0
            y2 = y+r-fh/3.0

            label_pos_list.append(((x1, y1), (x1 + label_length / 2.0, y1), (x1 + label_length, y1)))
            label_pos_list.append(((x2, y1), (x2 + label_length / 2.0, y1), (x2 + label_length, y1)))
            label_pos_list.append(((x1, y2), (x1 + label_length / 2.0, y2), (x1 + label_length, y2)))
            label_pos_list.append(((x2, y2), (x2 + label_length / 2.0, y2), (x2 + label_length, y2)))

        return label_pos_list

    def calc_planet_moons_positions(self, ctx, state):
        result = []
        pick_r = ctx.cfg.picker_radius if ctx.cfg.picker_radius > 0 else 0
        pick_min_r = pick_r ** 2
        for pl_moon in ctx.planet_moons:
            x, y, z = ctx.transf.equatorial_to_xyz(pl_moon.ra, pl_moon.dec)
            result.append([x, y, z])
            r = x ** 2 + y ** 2
            if r < pick_min_r:
                state.picked_planet_moon = pl_moon
                pick_min_r = r
        return result


