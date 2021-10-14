#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2021 fchart authors
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

import string
import numpy as np
import math

from time import time

from .label_potential import *
from .astrocalc import *
from .np_astrocalc import *
from .constellation import *
from .mirroring_graphics import *
from .configuration import *
from . import deepsky_object as deepsky

from .graphics_interface import DrawMode

from .widget_mag_scale import WidgetMagnitudeScale
from .widget_map_scale import WidgetMapScale
from .widget_orientation import WidgetOrientation
from .widget_coords import WidgetCoords
from .widget_dso_legend import WidgetDsoLegend
from .widget_telrad import WidgetTelrad


NL = {
    'h':'u',
    'm':'m',
    's':'s',
    'G':'Sterrenstelsel',
    'OCL':'Open sterrenhoop',
    'GCL':'Bolhoop',
    'AST':'Groepje sterren',
    'PN': 'Planetaire nevel',
    'N': 'Diffuse emissienevel',
    'SNR':'Supernovarest',
    'PG':'Deel van sterrenstelsel'
}


EN = {
    'h':'h',
    'm':'m',
    's':'s',
    'G':'Galaxy',
    'OCL':'Open cluster',
    'GCL':'Globular cluster',
    'AST':'Asterism',
    'PN': 'Planetary nebula',
    'N': 'Diffuse nebula',
    'SNR':'Supernova remnant',
    'PG':'Part of galaxy'
}

STAR_LABELS = {
    "alp":"α",
    "bet":"β",
    "gam":"γ",
    "del":"δ",
    "eps":"ε",
    "zet":"ζ",
    "eta":"η",
    "the":"θ",
    "iot":"ι",
    "kap":"κ",
    "lam":"λ",
    "mu":"μ",
    "nu":"ν",
    "xi":"ξ",
    "omi":"ο",
    "pi":"π",
    "rho":"ρ",
    "sig":"σ/ς",
    "tau":"τ",
    "ups":"υ",
    "phi":"φ",
    "chi":"χ",
    "psi":"ψ",
    "ome":"ω"
}

STARS_IN_SCALE = 7
LEGEND_MARGIN = 0.47
BASE_SCALE = 0.98
GRID_DENSITY = 4

RA_GRID_SCALE = [1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 3*60]
DEC_GRID_SCALE = [1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 45*60, 60*60]

MAG_SCALE_X = [0, 1,   2,   3,   4,    5,    25]
MAG_SCALE_Y = [0, 1.8, 3.3, 4.7, 6,  7.2,  18.0]

#====================>>>  SkymapEngine  <<<====================

class SkymapEngine:

    def __init__(self, graphics, language=EN, ra=0.0, dec=0.0, fieldradius=-1.0, lm_stars=13.8, lm_deepsky=12.5, caption=''):
        """
        Width is width of the map including the legend in mm.
        """
        self.graphics = graphics
        self.config = EngineConfiguration()

        self.caption = ''
        self.language = language
        self.drawingwidth = self.graphics.gi_width
        self.drawingheight = self.graphics.gi_height
        self.min_radius   = 1.0 # of deepsky symbols (mm)

        self.lm_stars     = lm_stars
        self.lm_deepsky   = lm_deepsky

        self.set_caption(caption)
        self.set_field(ra, dec, fieldradius)


    def set_field(self, ra, dec, fieldradius):
        """
        Provide the RA, DEC, and radius of the map in radians. This method
        sets a new drawingscale and legend_fontscale
        """
        self.fieldcentre         = (ra,dec)
        self.fc_sincos_dec       = (math.sin(dec), math.cos(dec))

        self.fieldradius         = fieldradius

        wh = max(self.drawingwidth, self.drawingheight)

        self.fieldsize           = fieldradius * math.sqrt(self.drawingwidth**2 + self.drawingheight**2) / wh

        if self.config.no_margin:
            self.scene_scale = (wh - self.config.legend_linewidth) / wh
        else:
            self.scene_scale = BASE_SCALE

        self.drawingscale    = self.scene_scale*wh/2.0/math.sin(fieldradius)

        self.legend_fontscale    = min(self.config.legend_font_scale, wh/100.0)

        self.set_caption(self.caption)


    def set_configuration(self, config):
        self.config = config


    def get_field_radius_mm(self):
        return self.drawingscale * math.sin(self.fieldradius)

    def get_field_rect_mm(self):
        x = self.scene_scale * self.drawingwidth / 2.0
        y = self.scene_scale * self.drawingheight / 2.0
        return (-x, -y, x, y)

    def set_language(self, language):
        """
        Set the language of the legend.
        """
        self.language = language


    def set_caption(self, caption):
        self.caption = caption
        if caption != '':
            self.graphics.set_dimensions(self.drawingwidth,self.drawingheight + self.legend_fontscale*self.graphics.gi_fontsize*2.0)


    def draw_caption(self):
        if self.caption != '':
            old_size = self.graphics.gi_fontsize
            font_size = self.get_legend_font_size()
            self.graphics.set_font(self.graphics.gi_font, 2.0*font_size)
            self.graphics.text_centred(0, self.drawingwidth/2.0*BASE_SCALE + font_size, self.caption)
            self.graphics.set_font(self.graphics.gi_font, old_size)


    def draw_field_border(self):
        """
        Draw a circle representing the edge of the field of view.
        """
        if self.config.show_field_border:
            self.graphics.set_linewidth(self.config.legend_linewidth)
            x1, y1, x2, y2 = self.get_field_rect_mm()
            self.graphics.line(x1, y1, x1, y2)
            self.graphics.line(x1, y2, x2, y2)
            self.graphics.line(x2, y2, x2, y1)
            self.graphics.line(x2, y1, x1, y1)


    def get_legend_font_size(self):
        return self.config.font_size * self.legend_fontscale


    def draw_widgets(self):
        # Set the fontsize for the entire legend
        fontsize = self.get_legend_font_size()
        self.graphics.set_font(self.graphics.gi_font, fontsize=fontsize)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        if self.config.fov_telrad:
            self.w_telrad.draw(self.graphics)
        if self.config.show_mag_scale_legend:
            self.w_mag_scale.draw(self.graphics, x1, y1, self.config.legend_only)
        if self.config.show_map_scale_legend:
            self.w_map_scale.draw(self.graphics, x2, y1, self.config.legend_only)
        if self.config.show_orientation_legend:
            self.w_orientation.draw(self.graphics, x1, y2, self.config.legend_only)
        if self.config.show_coords_legend:
            self.w_coords.draw(self.graphics, left=x2-fontsize/2, bottom=y2-fontsize, ra=self.fieldcentre[0], dec=self.fieldcentre[1], legend_only=self.config.legend_only)
        if self.config.show_dso_legend:
            self.w_dso_legend.draw_dso_legend(self, self.graphics, self.config.legend_only)


    def draw_deepsky_objects(self, deepsky_catalog, showing_dsos, hl_showing_dsos, dso_hide_filter):
        # Draw deep sky
        print('Drawing deepsky...')

        if self.config.show_deepsky:
            deepsky_list = deepsky_catalog.select_deepsky(self.fieldcentre, self.fieldsize, self.lm_deepsky)
        else:
            deepsky_list = []

        last_selected = len(deepsky_list)
        filtered_showing_dsos = []

        if dso_hide_filter:
            dso_hide_filter_set = { dso for dso in dso_hide_filter }
        else:
            dso_hide_filter_set = {}

        if showing_dsos:
            for dso in showing_dsos:
                if not dso in deepsky_list:
                    filtered_showing_dsos.append(dso)
                if dso in dso_hide_filter_set:
                    dso_hide_filter_set.remove(dso)

        deepsky_list.sort(key = lambda x: x.mag)
        deepsky_list_mm = []

        # calc for deepsky objects from selection
        for object in deepsky_list:
            x, y  =  radec_to_xy(object.ra, object.dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            if object.type == deepsky.GALCL:
                rlong = self.min_radius
            elif object.rlong is None:
                rlong = self.min_radius
            else:
                rlong  = object.rlong*self.drawingscale
                if rlong < self.min_radius:
                    rlong = self.min_radius
            deepsky_list_mm.append((object, x, y, rlong))

        # calc for deepsky objects from showing dsos
        for object in filtered_showing_dsos:
            if angular_distance((object.ra, object.dec), self.fieldcentre) < self.fieldsize:
                x, y, z  = radec_to_xyz(object.ra, object.dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
                if z > 0:
                    rlong  = object.rlong*self.drawingscale
                    if object.type == deepsky.GALCL:
                        rlong = self.min_radius
                    if rlong < self.min_radius:
                        rlong = self.min_radius
                    deepsky_list_mm.append((object, x, y, rlong))

        label_potential = LabelPotential(self.get_field_radius_mm(), deepsky_list_mm)

        print('Drawing objects...')
        for i in range(len(deepsky_list_mm)):
            object, x, y, rlong  = deepsky_list_mm[i]

            if object in dso_hide_filter_set:
                continue

            label = object.label()

            if hl_showing_dsos and object in showing_dsos:
                self.draw_dso_hightlight(x, y, rlong, label)

            rlong = object.rlong if object.rlong is not None else self.min_radius
            rshort = object.rshort if object.rshort is not None else self.min_radius
            rlong  = rlong*self.drawingscale
            rshort = rshort*self.drawingscale
            posangle=object.position_angle+direction_ddec((object.ra, object.dec), self.fieldcentre, self.fc_sincos_dec)+0.5*np.pi

            if rlong <= self.min_radius:
                rshort *= self.min_radius/rlong
                rlong = self.min_radius

            if object.type == deepsky.GALCL:
                rlong /= 3.0

            label_length = self.graphics.text_width(label)
            labelpos = -1

            labelpos_list =[]
            if object.type == deepsky.G:
                labelpos_list = self.galaxy_labelpos(x, y, rlong, rshort, posangle, label_length)
            elif object.type == deepsky.N:
                labelpos_list = self.diffuse_nebula_labelpos(x, y, 2.0*rlong, 2.0*rshort, posangle, label_length)
            elif object.type in [deepsky.PN,deepsky.OC,deepsky.GC,deepsky.SNR]:
                labelpos_list = self.circular_object_labelpos(x, y, rlong, label_length)
            elif object.type == deepsky.STARS:
                labelpos_list = self.asterism_labelpos(x, y, rlong, label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(x, y, rlong, label_length)

            pot = 1e+30
            for labelpos_index in range(len(labelpos_list)):
                [[x1,y1],[x2,y2],[x3,y3]] = labelpos_list[labelpos_index]
                pot1 = label_potential.compute_potential(x2,y2)
                #label_potential.compute_potential(x1,y1),
                #label_potential.compute_potential(x3,y3)])
                if pot1 < pot:
                    pot = pot1
                    labelpos = labelpos_index

            [xx, yy] = labelpos_list[labelpos][1]
            label_potential.add_position(xx, yy, label_length)

            if object.type == deepsky.G:
                self.galaxy(x, y, rlong, rshort, posangle, object.mag, label, labelpos)
            elif object.type == deepsky.N:
                has_outlines = False
                if object.outlines is not None:
                    has_outlines = self.draw_object_outlines(object, x, y, rlong, rshort, posangle, label, labelpos)
                if not has_outlines:
                    self.diffuse_nebula(x, y, 2.0*rlong, 2.0*rshort, posangle, label, labelpos)
            elif object.type == deepsky.PN:
                self.planetary_nebula(x, y, rlong, label, labelpos)
            elif object.type == deepsky.OC:
                has_outlines = False
                if object.outlines is not None:
                    has_outlines = self.draw_object_outlines(object, x, y, rlong, rshort)
                    if has_outlines:
                        print('Outlines {}'.format(object.name))
                self.open_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.GC:
                self.globular_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.STARS:
                self.asterism(x, y, rlong, label, labelpos)
            elif object.type == deepsky.SNR:
                self.supernova_remnant(x, y, rlong, label, labelpos)
            else:
                self.unknown_object(x, y, rlong, label, labelpos)

            if self.visible_objects is not None:
                xs1, ys1 = x-rlong, y-rlong
                xs2, ys2 = x+rlong, y+rlong
                if self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2):
                    xp1, yp1 = self.graphics.to_pixel(xs1, ys1)
                    xp2, yp2 = self.graphics.to_pixel(xs2, ys2)
                    self.visible_objects_in_map.append([rlong, label.replace(' ', ''), xp1, yp1, xp2, yp2])

    def draw_object_outlines(self, object, x, y, rlong, rshort, posangle=None, label=None, labelpos=None):
        lev_shift = 0
        for outl_lev in range(2, -1, -1):
            outlines_ar = object.outlines[outl_lev]
            if outlines_ar:
                has_outlines = True
                for outlines in outlines_ar:
                    x_outl, y_outl = np_radec_to_xy(outlines[0], outlines[1], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
                    self.diffuse_nebula_outlines(x, y, x_outl, y_outl, outl_lev+lev_shift, 2.0*rlong, 2.0*rshort, posangle, label, labelpos)
            else:
                lev_shift += 1
        return has_outlines

    def draw_unknown_nebula(self, unknown_nebulas):
        for uneb in unknown_nebulas:
            ra = (uneb.ra_min + uneb.ra_max) / 2.0
            dec = (uneb.dec_min + uneb.dec_max) / 2.0
            x, y, z = radec_to_xyz(ra, dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            if z <=0:
                continue
            for outl_lev in range(3):
                outlines = uneb.outlines[outl_lev]
                if not outlines:
                    continue
                for outl in outlines:
                    if z > 0:
                        x_outl, y_outl = np_radec_to_xy(outl[0], outl[1], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
                        self.unknown_diffuse_nebula_outlines(x_outl, y_outl, outl_lev)


    def draw_milky_way(self, milky_way_lines):

        self.graphics.save()

        x, y, z = np_radec_to_xyz(milky_way_lines[:,0], milky_way_lines[:,1], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)

        self.graphics.set_pen_rgb(self.config.milky_way_color)
        self.graphics.set_fill_rgb(self.config.milky_way_color)
        self.graphics.set_linewidth(self.config.milky_way_linewidth)

        polygon = None
        for i in range(len(x)-1):
            if milky_way_lines[i][2] == 0:
                if polygon is not None and len(polygon) > 2:
                    self.graphics.polygon(polygon, DrawMode.BOTH)
                x1, y1, z1 = x[i].item(), y[i].item(), z[i].item()
                polygon = None
                if z1 > 0:
                    polygon = [[x1, y1]]
            else:
                x1, y1, z1 = x[i].item(), y[i].item(), z[i].item()
                if z1 > 0:
                    if polygon is None:
                        polygon = []
                    polygon.append([x1, y1])

        if polygon is not None and len(polygon) > 2:
            self.graphics.polygon(polygon, DrawMode.FILL)

        self.graphics.restore()


    def draw_extra_objects(self,extra_positions):
        # Draw extra objects
        print('Drawing extra objects...')
        for object in extra_positions:
            rax,decx,label,labelpos = object
            if angular_distance((rax,decx),self.fieldcentre) < self.fieldsize:
                x, y =  radec_to_xy(rax, decx, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
                self.unknown_object(x,y,self.min_radius,label,labelpos)

    def draw_highlights(self, highlights):
        # Draw highlighted objects
        print('Drawing highlighted objects...')

        self.graphics.save()

        for hl_def in highlights:
            self.graphics.set_pen_rgb(hl_def.color)
            self.graphics.set_linewidth(self.config.dso_linewidth * hl_def.line_width)
            for dso_name, rax, decx in hl_def.data:
                if angular_distance((rax,decx), self.fieldcentre) < self.fieldsize:
                    x, y =  radec_to_xy(rax, decx, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
                    if hl_def.style == 'cross':
                        r = self.config.font_size * 2
                        self.mirroring_graphics.line(x-r, y, x-r/2, y)
                        self.mirroring_graphics.line(x+r, y, x+r/2, y)
                        self.mirroring_graphics.line(x, y+r, x, y+r/2)
                        self.mirroring_graphics.line(x, y-r, x, y-r/2)
                    elif hl_def.style == 'circle':
                        r = self.config.font_size
                        self.mirroring_graphics.circle(x,y,r)
                        if dso_name and self.visible_objects is not None:
                            xs1, ys1 = x-r, y-r
                            xs2, ys2 = x+r, y+r
                            if self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2):
                                xp1, yp1 = self.graphics.to_pixel(xs1, ys1)
                                xp2, yp2 = self.graphics.to_pixel(xs2, ys2)
                                self.visible_objects_in_map.append([r, dso_name.replace(' ', ''), xp1, yp1, xp2, yp2])

        self.graphics.restore()


    def draw_dso_hightlight(self, x, y, rlong, dso_name):
        self.graphics.save()

        self.graphics.set_pen_rgb(self.config.dso_highlight_color)
        self.graphics.set_linewidth(self.config.dso_highlight_linewidth)

        r = self.config.font_size
        self.mirroring_graphics.circle(x,y,r)
        xs1, ys1 = x-r, y-r
        xs2, ys2 = x+r, y+r
        if self.visible_objects_in_map is not None and (self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2)):
            xp1, yp1 = self.graphics.to_pixel(xs1, ys1)
            xp2, yp2 = self.graphics.to_pixel(xs2, ys2)
            self.visible_objects_in_map.append([r, dso_name.replace(' ', ''), xp1, yp1, xp2, yp2])

        self.graphics.restore()


    def draw_trajectory(self,trajectory):
        # Draw extra objects
        print('Drawing trajectory...')
        self.graphics.save()
        self.graphics.set_pen_rgb(self.config.dso_color)

        fh = self.graphics.gi_fontsize
        label1 = ''
        x1 = None
        y1 = None
        z1 = None
        r = self.min_radius * 1.2 / 2**0.5

        for i in range(0, len(trajectory)):
            rax2, decx2, label2 = trajectory[i]
            x2, y2, z2 =  radec_to_xyz(rax2,decx2, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)

            if i > 0:
                self.graphics.set_linewidth(self.config.constellation_linewidth)
                if z1 > 0 and z2 > 0:
                    self.mirroring_graphics.line(x1, y1, x2, y2)
                    self.draw_trajectory_tick(x1, y1, x2, y2)
                    if i == 1:
                        self.draw_trajectory_tick(x2, y2, x1, y1)

            self.mirroring_graphics.text_centred(x2, y2 - r - fh/2.0, label2)

            x1,y1,z1 = (x2, y2, z2)
            label1 = label2

        self.graphics.restore()


    def draw_trajectory_tick(self, x1, y1, x2, y2):
        dx = x2-x1
        dy = y2-y1
        dr = math.sqrt(dx * dx + dy*dy)
        ddx = dx * 1.0 / dr
        ddy = dy * 1.0 / dr
        self.graphics.set_linewidth(1.5*self.config.constellation_linewidth)
        self.mirroring_graphics.line(x2-ddy, y2+ddx, x2+ddy, y2-ddx)



    def magnitude_to_radius(self, magnitude):
        #radius = 0.13*1.35**(int(self.lm_stars)-magnitude)
        mag_d = self.lm_stars - np.clip(magnitude, a_min=None, a_max=self.lm_stars)
        mag_s = np.interp(mag_d, MAG_SCALE_X, MAG_SCALE_Y)
        radius = 0.1 * 1.33 ** (mag_s)
        return radius


    def draw_stars(self, star_catalog):
        # Select and draw stars
        print('Drawing stars...')

        # tm = time()
        selection = star_catalog.select_stars(self.fieldcentre, self.fieldsize, self.lm_stars)
        if selection is None or len(selection) == 0:
            print('No stars found.')
            return

        # print("Stars selection {} ms".format(str(time()-tm)), flush=True)
        print('{} stars in map.'.format(selection.shape[0]))
        print('Faintest star: ' + str(round(max(selection['mag']), 2)))

        # tm = time()
        x, y = np_radec_to_xy(selection['ra'], selection['dec'], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)

        # print("Stars view positioning {} ms".format(str(time()-tm)), flush=True)

        mag = selection['mag']

        indices   = np.argsort(mag)
        magsorted = mag[indices]
        rsorted = self.magnitude_to_radius(magsorted)

        if not self.config.star_colors:
            # self.graphics.set_pen_rgb((self.config.draw_color[0]/3, self.config.draw_color[0]/3, self.config.draw_color[0]/3))
            self.graphics.set_fill_rgb(self.config.draw_color)

        self.graphics.set_linewidth(0)

        named_star_list = []
        x1, y1, x2, y2 = self.get_field_rect_mm()
        for i in range(len(indices)):
            index = indices[i]
            xx, yy, rr = (x[index].item(), y[index].item(), rsorted[i].item(),)
            if xx >= x1-rr and xx <= x2+rr and yy >= y1-rr and yy <= y2+rr:
                self.star(xx, yy, rr, star_catalog.get_star_color(selection[index]))
                bsc_star = selection[index]['bsc']
                if not bsc_star is None:
                    named_star_list.append((xx, yy, rr, bsc_star,))

        self.draw_stars_labels(named_star_list)


    def draw_stars_labels(self, star_list):
        if not self.config.show_star_labels:
            return

        fn = self.graphics.gi_fontsize

        printed = {}
        for x, y, r, star in star_list:

            slabel = star.greek
            if not slabel and self.config.show_flamsteed:
                slabel = star.flamsteed
            if not slabel:
                continue

            printed_labels = printed.get(star.constellation)

            if printed_labels is None:
                printed_labels = set()
                printed[star.constellation] = printed_labels
            elif slabel in printed_labels:
                continue

            printed_labels.add(slabel)

            if slabel in STAR_LABELS:
                self.graphics.set_font(self.graphics.gi_font, 1.3*fn)
                slabel = STAR_LABELS.get(slabel)
            else:
                self.graphics.set_font(self.graphics.gi_font, 0.9*fn)

            self.draw_circular_object_label(x, y, r, slabel)

        self.graphics.set_font(self.graphics.gi_font, fn)


    def draw_constellations(self, constell_catalog, hl_constellation):
        print('Drawing constellations...')
        if self.config.show_constellation_borders:
            self.draw_constellation_boundaries(constell_catalog, hl_constellation)
        if self.config.show_constellation_shapes:
            self.draw_constellation_shapes(constell_catalog)


    def draw_grid_equatorial(self):
        print('Drawing equatorial grid...')
        self.graphics.save()
        self.graphics.set_linewidth(self.config.grid_linewidth)
        self.graphics.set_pen_rgb(self.config.grid_color)

        self.draw_grid_ra()
        self.draw_grid_dec()

        self.graphics.restore()


    def grid_dec_label(self, dec_minutes, label_fmt):
        deg = abs(int(dec_minutes/60))
        minutes = abs(dec_minutes) - deg * 60
        if dec_minutes > 0:
            prefix = '+'
        elif dec_minutes < 0:
            prefix = '-'
        else:
            prefix = ''
        return  prefix + label_fmt.format(deg, minutes)


    def grid_ra_label(self, ra_minutes, label_fmt):
        return label_fmt.format(ra_minutes//60, ra_minutes % 60)


    def draw_grid_ra(self):
        prev_steps, prev_grid_minutes = (None, None)
        for grid_minutes in DEC_GRID_SCALE:
            steps = self.fieldradius / (np.pi * grid_minutes / (180 * 60))
            if steps < GRID_DENSITY:
                if not prev_steps is None:
                    if prev_steps-GRID_DENSITY < GRID_DENSITY-steps:
                        grid_minutes = prev_grid_minutes
                break
            prev_steps, prev_grid_minutes = (steps, grid_minutes)

        dec_min = self.fieldcentre[1] - self.fieldradius
        dec_max = self.fieldcentre[1] + self.fieldradius

        label_fmt = '{}°' if grid_minutes >= 60 else '{}°{:02d}\''

        dec_minutes = -90*60 + grid_minutes

        while dec_minutes < 90*60:
            dec = np.pi * dec_minutes / (180*60)
            if dec > dec_min and dec < dec_max:
                self.draw_grid_ra_line(dec, dec_minutes, label_fmt)
            dec_minutes += grid_minutes



    def draw_grid_ra_line(self, dec, dec_minutes, label_fmt):
        dra = self.fieldradius / 10
        x11, y11, z11 = (None, None, None)
        agg_ra = 0
        while True:
            x12, y12, z12 = radec_to_xyz(self.fieldcentre[0] + agg_ra, dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            x22, y22, z22 = radec_to_xyz(self.fieldcentre[0] - agg_ra, dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            if not x11 is None and z11 > 0 and z12 > 0:
                self.mirroring_graphics.line(x11, y11, x12, y12)
                self.mirroring_graphics.line(x21, y21, x22, y22)
            agg_ra = agg_ra + dra
            if agg_ra > np.pi:
                break
            if x12 < -self.drawingwidth/2:
                y = (y12-y11) * (self.drawingwidth/2 + x11) / (x11 - x12) + y11
                label = self.grid_dec_label(dec_minutes, label_fmt)
                self.graphics.save()
                self.mirroring_graphics.translate(-self.drawingwidth/2,y)
                text_ang = math.atan2(y11-y12, x11-x12)
                self.mirroring_graphics.rotate(text_ang)
                fh =  self.graphics.gi_fontsize
                if dec >= 0:
                    self.graphics.text_right(2*fh/3, +fh/3, label)
                else:
                    self.graphics.text_right(2*fh/3, -fh, label)
                self.graphics.restore()
                break
            x11,y11,z11 = (x12, y12, z12)
            x21,y21,z21 = (x22, y22, z22)


    def draw_grid_dec(self):
        prev_steps, prev_grid_minutes = (None, None)
        fc_cos = math.cos(self.fieldcentre[1])
        for grid_minutes in RA_GRID_SCALE:
            steps = self.fieldradius / (fc_cos * (np.pi * grid_minutes / (12 * 60)))
            if steps < GRID_DENSITY:
                if not prev_steps is None:
                    if prev_steps-GRID_DENSITY < GRID_DENSITY-steps:
                        grid_minutes = prev_grid_minutes
                break
            prev_steps, prev_grid_minutes = (steps, grid_minutes)

        max_visible_dec = self.fieldcentre[1]+self.fieldradius if self.fieldcentre[1]>0 else self.fieldcentre[1]-self.fieldradius;
        if max_visible_dec >= np.pi/2 or max_visible_dec <= -np.pi/2:
            ra_size = 2*np.pi
        else:
            ra_size = self.fieldradius / math.cos(max_visible_dec)
            if ra_size > 2*np.pi:
                ra_size = 2*np.pi

        label_fmt = '{}h' if grid_minutes >= 60 else '{}h{:02d}m'

        ra_minutes = 0

        while ra_minutes <= 24*60:
            ra = np.pi * ra_minutes / (12*60)
            if abs(self.fieldcentre[0]-ra) < ra_size or abs(2*np.pi+self.fieldcentre[0]-ra) < ra_size:
                self.draw_grid_dec_line(ra, ra_minutes, label_fmt)
            ra_minutes += grid_minutes


    def draw_grid_dec_line(self, ra, ra_minutes, label_fmt):
        ddec = self.fieldradius / 10
        x11, y11, z11 = (None, None, None)
        x21, y21, z21 = (None, None, None)
        agg_dec = 0
        while True:
            x12, y12, z12 = radec_to_xyz(ra, self.fieldcentre[1] + agg_dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            x22, y22, z22 = radec_to_xyz(ra, self.fieldcentre[1] - agg_dec, self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
            if not x11 is None:
                if z11 > 0 and z12 > 0:
                    self.mirroring_graphics.line(x11, y11, x12, y12)
                if z21 > 0 and z22 > 0:
                    self.mirroring_graphics.line(x21, y21, x22, y22)
            agg_dec = agg_dec + ddec
            if agg_dec > np.pi/2:
                break
            if y12 > self.drawingheight/2 and y22 < -self.drawingheight/2:
                label = self.grid_ra_label(ra_minutes, label_fmt)
                self.graphics.save()
                if self.fieldcentre[1] <= 0:
                    x = (x12-x11) * (self.drawingheight/2 - y11) / (y12 - y11) + x11
                    self.mirroring_graphics.translate(x, self.drawingheight/2)
                    text_ang = math.atan2(y11-y12, x11-x12)
                else:
                    x = (x22-x21) * (-self.drawingheight/2 - y21) / (y22 - y21) + x21
                    self.mirroring_graphics.translate(x, -self.drawingheight/2)
                    text_ang = math.atan2(y21-y22, x21-x22)
                self.mirroring_graphics.rotate(text_ang)
                fh =  self.graphics.gi_fontsize
                self.graphics.text_right(2*fh/3, fh/3, label)
                self.graphics.restore()
                break
            x11,y11,z11 = (x12, y12, z12)
            x21,y21,z21 = (x22, y22, z22)


    def draw_constellation_shapes(self, constell_catalog):
        self.graphics.save()
        self.graphics.set_linewidth(self.config.constellation_linewidth)
        self.graphics.set_pen_rgb(self.config.constellation_lines_color)

        x1, y1, z1 = np_radec_to_xyz(constell_catalog.all_constell_lines[:,0], constell_catalog.all_constell_lines[:,1], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)
        x2, y2, z2 = np_radec_to_xyz(constell_catalog.all_constell_lines[:,2], constell_catalog.all_constell_lines[:,3], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)

        for i in range(len(x1)):
            if z1[i] > 0 and z2[i] > 0:
                if self.config.constellation_linespace > 0:
                    dx = x2[i] - x1[i]
                    dy = y2[i] - y1[i]
                    dr = math.sqrt(dx * dx + dy*dy)
                    ddx = dx * self.config.constellation_linespace / dr
                    ddy = dy * self.config.constellation_linespace / dr
                    self.mirroring_graphics.line(x1[i] + ddx, y1[i] + ddy, x2[i] - ddx, y2[i] - ddy)
                else:
                    self.mirroring_graphics.line(x1[i], y1[i], x2[i], y2[i])

        self.graphics.restore()


    def draw_constellation_boundaries(self, constell_catalog, hl_constellation):
        self.graphics.save()
        self.graphics.set_dashed_line(1.2, 1.2)

        x, y, z = np_radec_to_xyz(constell_catalog.boundaries_points[:,0], constell_catalog.boundaries_points[:,1], self.fieldcentre, self.drawingscale, self.fc_sincos_dec)

        hl_constellation = hl_constellation.upper() if hl_constellation else None

        for index1, index2, cons1, cons2 in constell_catalog.boundaries_lines:
            if z[index1] > 0 and z[index2] > 0:
                if hl_constellation and (hl_constellation == cons1 or hl_constellation == cons2):
                    self.graphics.set_pen_rgb(self.config.constellation_hl_border_color)
                    self.graphics.set_linewidth(self.config.constellation_linewidth * 1.75)
                else:
                    self.graphics.set_pen_rgb(self.config.constellation_border_color)
                    self.graphics.set_linewidth(self.config.constellation_linewidth)

                self.mirroring_graphics.line(x[index1], y[index1], x[index2], y[index2])

        self.graphics.restore()


    def make_map(self, used_catalogs, showing_dsos=None, hl_showing_dsos=False, highlights=None, dso_hide_filter=None, extra_positions=None, hl_constellation=None,
                 trajectory=[], visible_objects=None):
        """ Creates map using given graphics, params and config

        used_catalogs - UsedCatalogs data structure
        showing_dso - DSO forced to be shown even if they don't pass the filter
        hl_showing_dsos - True if showing dso will be highlighted
        highlights - list of DSOs that will be marked
        dso_hide_filter - list of DSO to be hidden, except showing_dso
        extra_positons
        hl_constellation - constellation name that will be highlighted
        trajectory - defined by list of points (ra, dec) points
        visible_objects - output array containing list of object visible on the map
        """

        self.visible_objects = visible_objects
        self.visible_objects_in_map = [] if visible_objects is not None else None

        if self.config.mirror_x or self.config.mirror_y:
            self.mirroring_graphics = MirroringGraphics(self.graphics, self.config.mirror_x, self.config.mirror_y)
        else:
            self.mirroring_graphics = self.graphics

        self.create_widgets()

        self.graphics.set_background_rgb(self.config.background_color)

        self.graphics.new()

        if not self.config.legend_only:
            self.graphics.clear()

        self.graphics.set_pen_rgb(self.config.draw_color)
        self.graphics.set_fill_rgb(self.config.draw_color)
        self.graphics.set_font(font=self.config.font, fontsize=self.config.font_size)
        self.graphics.set_linewidth(self.config.legend_linewidth)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        w_mags_width, w_mags_heigth = self.w_mag_scale.get_size()
        w_maps_width, w_maps_height = self.w_map_scale.get_size()

        if not self.config.legend_only:

            if self.config.show_milky_way:
                # tm = time()
                self.draw_milky_way(used_catalogs.milky_way_lines)
                # print("Milky way within {} ms".format(str(time()-tm)), flush=True)

            if self.config.show_map_scale_legend or self.config.show_mag_scale_legend:
                clip_path = [(x2,y2)]

                if self.config.show_map_scale_legend:
                    clip_path.extend([(x2,y1+w_maps_height),
                                     (x2-w_maps_width, y1+w_maps_height),
                                     (x2-w_maps_width, y1)])
                else:
                    clip_path.append((x2,y1))

                if self.config.show_mag_scale_legend:
                    clip_path.extend([(x1 + w_mags_width, y1),
                                     (x1 + w_mags_width, y1 + w_mags_heigth),
                                     (x1, y1 + w_mags_heigth)])
                else:
                    clip_path.append((x1, y1))

                clip_path.append((x1, y2))

                self.graphics.clip_path(clip_path)

            if self.config.show_equatorial_grid:
                # tm = time()
                self.draw_grid_equatorial()
                # print("Equatorial grid within {} ms".format(str(time()-tm)), flush=True)

            if highlights:
                self.draw_highlights(highlights)

            if used_catalogs.constellcatalog is not None:
                # tm = time()
                self.draw_constellations(used_catalogs.constellcatalog, hl_constellation)
                # print("constellations within {} ms".format(str(time()-tm)), flush=True)

            if used_catalogs.unknown_nebulas is not None:
                self.draw_unknown_nebula(used_catalogs.unknown_nebulas)

            if used_catalogs.deepskycatalog is not None:
                # tm = time()
                self.draw_deepsky_objects(used_catalogs.deepskycatalog, showing_dsos, hl_showing_dsos, dso_hide_filter)
                # print("DSO within {} ms".format(str(time()-tm)), flush=True)

            if extra_positions:
                self.draw_extra_objects(extra_positions)

            if trajectory:
                self.draw_trajectory(trajectory)

            if used_catalogs.starcatalog is not None:
                # tm = time()
                self.draw_stars(used_catalogs.starcatalog)
                # print("Stars within {} ms".format(str(time()-tm)), flush=True)

            self.graphics.reset_clip()

        print('Drawing legend')
        self.draw_caption()

        print('Drawing widgets')
        self.draw_widgets()

        # Draw border of field-of-view
        self.draw_field_border()

        # tm = time()
        self.graphics.finish()
        # print("Rest {} ms".format(str(time()-tm)), flush=True)

        if self.visible_objects_in_map is not None:
            self.visible_objects_in_map.sort(key=lambda x: x[0])
            for obj in self.visible_objects_in_map:
                self.visible_objects.extend([obj[1], obj[2], obj[3], obj[4], obj[5]])

    def create_widgets(self):
        self.w_mag_scale = WidgetMagnitudeScale(self,
                                          legend_fontsize=self.get_legend_font_size(),
                                          stars_in_scale=STARS_IN_SCALE,
                                          lm_stars=self.lm_stars,
                                          legend_linewidth=self.config.legend_linewidth)

        self.w_map_scale = WidgetMapScale(drawingscale=self.drawingscale,
                                    maxlength=self.drawingwidth/3.0,
                                    legend_fontsize=self.get_legend_font_size(),
                                    legend_linewidth=self.config.legend_linewidth)

        self.w_orientation = WidgetOrientation(legend_fontsize=self.get_legend_font_size(),
                                               mirror_x=self.config.mirror_x,
                                               mirror_y=self.config.mirror_y
                                               )

        self.w_coords = WidgetCoords(self.language)

        self.w_dso_legend = WidgetDsoLegend(self.language, self.drawingwidth, LEGEND_MARGIN)

        self.w_telrad = WidgetTelrad(self.drawingscale, self.config.constellation_linewidth)


    def star(self, x, y, radius, star_color):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_rgb and set_fill_rgb
        """
        if self.config.star_colors and star_color:
            self.graphics.set_fill_rgb(star_color)

        r = round(radius, 2)
        self.mirroring_graphics.circle(x, y, r, DrawMode.FILL)


    def no_mirror_star(self, x, y, radius):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_rgb and set_fill_rgb
        """
        r = int((radius + self.graphics.gi_linewidth/2.0)*100.0 + 0.5)/100.0
        self.graphics.circle(x, y, r,DrawMode.BOTH)


    def open_cluster(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        self.graphics.save()

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        self.mirroring_graphics.circle(x,y,r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def asterism(self,x,y,radius=-1, label='', labelpos=-1):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2=2**0.5
        d = r/2.0*w2

        self.graphics.save()

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        diff = self.graphics.gi_linewidth/2.0/w2

        self.mirroring_graphics.line(x-diff, y+d+diff, x+d+diff,y-diff)
        self.mirroring_graphics.line(x+d, y, x,y-d)
        self.mirroring_graphics.line(x+diff, y-d-diff, x-d-diff,y+diff)
        self.mirroring_graphics.line(x-d, y, x,y+d)

        fh =  self.graphics.gi_fontsize
        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-2*fh/3.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def asterism_labelpos(self,x,y,radius=-1,label_length=0.0):
        """
        x,y,radius, label_length in mm
        returns [[start, centre, end],()]
        """
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2 = 2**0.5
        d = r/2.0*w2
        fh =  self.graphics.gi_fontsize
        label_pos_list = []
        yy = y-d-2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        yy = y+d+2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        xx = x-d-fh/6.0
        yy = y
        label_pos_list.append([[xx-label_length,yy],[xx-label_length/2.0,yy],[xx,yy]])
        xx = x+d+fh/6.0
        yy = y
        label_pos_list.append([[xx,yy],[xx+label_length/2.0,yy],[xx+label_length,yy]])
        return label_pos_list


    def galaxy(self, x, y, rlong=-1, rshort=-1, posangle=0.0, mag=None, label='', labelpos=-1):
        """
        If rlong != -1 and rshort == -1 =>   rshort <- rlong
        if rlong < 0.0 => standard galaxy
        labelpos can be 0,1,2,3
        """
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        if self.config.dso_dynamic_brightness and (mag is not None) and self.lm_deepsky >= 10.0:
            fac = self.lm_deepsky - 8.0
            if fac > 5:
                fac = 5.0
            diff_mag = self.lm_deepsky - mag
            if diff_mag < 0:
                diff_mag = 0
            if diff_mag > 5:
                diff_mag = 5
            dso_intensity = 1.0 if diff_mag > fac else 0.5 + 0.5 * diff_mag / fac;
        else:
            dso_intensity = 1.0

        self.graphics.set_pen_rgb((self.config.galaxy_color[0]*dso_intensity,
                                   self.config.galaxy_color[1]*dso_intensity,
                                   self.config.galaxy_color[2]*dso_intensity))

        p = posangle
        if posangle >= 0.5*np.pi:
            p += np.pi
        if posangle < -0.5*np.pi:
            p -= np.pi

        fh = self.graphics.gi_fontsize
        self.mirroring_graphics.ellipse(x,y,rl, rs, p)

        if label != '':
            self.graphics.save()
            self.mirroring_graphics.translate(x,y)
            self.mirroring_graphics.rotate(p)
            self.mirroring_graphics.set_pen_rgb((self.config.label_color[0]*dso_intensity,
                                                 self.config.label_color[1]*dso_intensity,
                                                 self.config.label_color[2]*dso_intensity))

            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(0, -rshort-0.5*fh, label)
            elif labelpos == 1:
                self.graphics.text_centred(0, +rshort+0.5*fh, label)
            elif labelpos == 2:
                self.graphics.text_right(rlong+fh/6.0, -fh/3.0, label)
            elif labelpos == 3:
                self.graphics.text_left(-rlong-fh/6.0, -fh/3.0, label)
            self.graphics.restore()

        self.graphics.restore()


    def galaxy_labelpos(self,x,y,rlong=-1,rshort=-1,posangle=0.0,label_length=0.0):
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        p = posangle
        if posangle >= 0.5*np.pi:
            p += np.pi
        if posangle < -0.5*np.pi:
            p -= np.pi

        fh = self.graphics.gi_fontsize
        label_pos_list = []

        sp = math.sin(p)
        cp = math.cos(p)

        hl = label_length/2.0

        d = -rshort-0.5*fh
        xc = x + d*sp
        yc = y - d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xc = x - d*sp
        yc = y + d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        d  = rlong+fh/6.0
        xs = x + d*cp
        ys = y + d*sp
        xc = xs + hl*cp
        yc = ys + hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xe = x - d*cp
        ye = y - d*sp
        xc = xe - hl*cp
        yc = ye - hl*sp
        xs = xc - hl*cp
        ys = yc - hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        return label_pos_list


    def draw_circular_object_label(self, x, y, r, label, labelpos=-1):
        fh = self.graphics.gi_fontsize
        if label:
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            arg = 1.0-2*fh/(3.0*r)
            if arg < 1.0 and arg > -1.0:
                a = math.acos(arg)
            else:
                a = 0.5*np.pi
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_right(x+math.sin(a)*r+fh/6.0, y-r, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_left(x-math.sin(a)*r-fh/6.0, y-r, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_right(x+math.sin(a)*r+fh/6.0, y+r-2*fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_left(x-math.sin(a)*r-fh/6.0, y+r-2*fh/3.0, label)


    def circular_object_labelpos(self, x, y, radius=-1.0, label_length=0.0):
        fh = self.graphics.gi_fontsize
        r = radius

        if radius <= 0.0:
            r = self.drawingwidth/40.0

        arg = 1.0-2*fh/(3.0*r)

        if arg < 1.0 and arg > -1.0:
            a = math.acos(arg)
        else:
            a = 0.5*np.pi

        label_pos_list = []
        xs = x+math.sin(a)*r+fh/6.0
        ys = y-r+fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        xs = x-math.sin(a)*r-fh/6.0 - label_length
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+math.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+math.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list



    def globular_cluster(self, x,y,radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.star_cluster_color)

        self.mirroring_graphics.circle(x,y,r)
        self.mirroring_graphics.line(x-r, y, x+r, y)
        self.mirroring_graphics.line(x, y-r, x, y+r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def diffuse_nebula(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label='',labelpos=''):
        self.graphics.save()

        self.graphics.set_linewidth(self.config.nebula_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        d1 = d+self.graphics.gi_linewidth/2.0

        self.mirroring_graphics.line(x-d1, y+d, x+d1, y+d)
        self.mirroring_graphics.line(x+d, y+d, x+d, y-d)
        self.mirroring_graphics.line(x+d1, y-d, x-d1, y-d)
        self.mirroring_graphics.line(x-d, y-d, x-d, y+d)

        fh = self.graphics.gi_fontsize
        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-fh/2.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/2.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()

    def diffuse_nebula_outlines(self, x, y, x_outl, y_outl, outl_lev, width=-1.0, height=-1.0, posangle=0.0, label='', labelpos=''):
        self.graphics.save()

        self.graphics.set_linewidth(self.config.nebula_linewidth)


        if self.config.light_mode:
            frac = 4 - 1.5 * outl_lev # no logic, look nice in light mode
            pen_r = 1.0 - ((1.0 - self.config.nebula_color[0]) / frac)
            pen_g = 1.0 - ((1.0 - self.config.nebula_color[1]) / frac)
            pen_b = 1.0 - ((1.0 - self.config.nebula_color[2]) / frac)
        else:
            frac = 4 - 1.5 * outl_lev # no logic, look nice in dark mode
            pen_r = self.config.nebula_color[0] / frac
            pen_g = self.config.nebula_color[1] / frac
            pen_b = self.config.nebula_color[2] / frac

        self.graphics.set_pen_rgb((pen_r, pen_g, pen_b))

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0

        for i in range(len(x_outl)-1):
            self.mirroring_graphics.line(x_outl[i].item(), y_outl[i].item(), x_outl[i+1].item(), y_outl[i+1].item())
        self.mirroring_graphics.line(x_outl[len(x_outl)-1].item(), y_outl[len(x_outl)-1].item(), x_outl[0].item(), y_outl[0].item())

        fh = self.graphics.gi_fontsize
        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-fh/2.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/2.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def unknown_diffuse_nebula_outlines(self, x_outl, y_outl, outl_lev):
        self.graphics.save()

        self.graphics.set_linewidth(self.config.nebula_linewidth)


        if self.config.light_mode:
            frac = 4 - 1.5 * outl_lev # no logic, look nice in light mode
            pen_r = 1.0 - ((1.0 - self.config.nebula_color[0]) / frac)
            pen_g = 1.0 - ((1.0 - self.config.nebula_color[1]) / frac)
            pen_b = 1.0 - ((1.0 - self.config.nebula_color[2]) / frac)
        else:
            frac = 4 - 1.5 * outl_lev # no logic, look nice in dark mode
            pen_r = self.config.nebula_color[0] / frac
            pen_g = self.config.nebula_color[1] / frac
            pen_b = self.config.nebula_color[2] / frac

        self.graphics.set_pen_rgb((pen_r, pen_g, pen_b))

        for i in range(len(x_outl)-1):
            self.mirroring_graphics.line(x_outl[i].item(), y_outl[i].item(), x_outl[i+1].item(), y_outl[i+1].item())
        self.mirroring_graphics.line(x_outl[len(x_outl)-1].item(), y_outl[len(x_outl)-1].item(), x_outl[0].item(), y_outl[0].item())

        self.graphics.restore()

    def diffuse_nebula_labelpos(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label_length=0.0):

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y-d-fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        ys = y+d+fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


    def planetary_nebula(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/60.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x,y,0.75*r)
        self.mirroring_graphics.line(x-0.75*r, y, x-1.5*r, y)
        self.mirroring_graphics.line(x+0.75*r, y, x+1.5*r, y)
        self.mirroring_graphics.line(x, y+0.75*r, x, y+1.5*r)
        self.mirroring_graphics.line(x, y-0.75*r, x, y-1.5*r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def supernova_remnant(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x,y,r-self.graphics.gi_linewidth/2.0)
        #self.graphics.circle(x,y,r*0.85)
        #self.graphics.circle(x,y,r*0.7)
        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()

    def unknown_object(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        r /= 2**0.5
        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_pen_rgb(self.config.dso_color)

        self.mirroring_graphics.line(x-r, y+r, x+r, y-r)
        self.mirroring_graphics.line(x+r, y+r, x-r, y-r)

        fh = self.graphics.gi_fontsize

        if label != '':
            self.mirroring_graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0:
                self.mirroring_graphics.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos ==1:
                self.mirroring_graphics.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_centred(x, y + r + fh/2.0, label)
            else:
                self.mirroring_graphics.text_centred(x, y - r - fh/2.0, label)
        self.graphics.restore()


    def unknown_object_labelpos(self, x, y, radius=-1, label_length=0.0):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize
        r/=2**0.5
        label_pos_list = []
        xs = x + r +fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - r -fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y + r +fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y - r -fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


if __name__ == '__main__':
    from . import graphics_cairo
    from . import composite_star_catalog as sc

    data_dir='./data/catalogs/'

    stars = sc.CompositeStarCatalog(data_dir)

    width = 200
    cairo = cairo.CairoDrawing(width, width, 'radec00.pdf',)

    sm = SkymapEngine(cairo)
    sm.set_caption('Probeersel')
    sm.set_field(1.5,1, 0.05)
    sm.make_map(stars)
    cairo.close()

