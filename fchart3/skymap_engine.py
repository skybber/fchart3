#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2023 fchart authors
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


import gettext
import os

uilanguage=os.environ.get('fchart3lang')
try:
    lang = gettext.translation( 'messages',localedir='locale', languages=[uilanguage])
    lang.install()
    _ = lang.gettext
except:                  
    _ = gettext.gettext


from time import time

from .label_potential import *
from .np_astrocalc import *
from .constellation import *
from .mirroring_graphics import *
from .configuration import *
from . import deepsky_object as deepsky

from .graphics_interface import DrawMode

from .projection import ProjectionType
from .projection_orthographic import ProjectionOrthographic
from .projection_stereographic import ProjectionStereographic

from .space_widget_allocator import SpaceWidgetAllocator
from .widget_mag_scale import WidgetMagnitudeScale
from .widget_map_scale import WidgetMapScale
from .widget_orientation import WidgetOrientation
from .widget_coords import WidgetCoords
from .widget_dso_legend import WidgetDsoLegend
from .widget_telrad import WidgetTelrad
from .widget_eyepiece import WidgetEyepiece
from .widget_picker import WidgetPicker

from .precession import compute_precession_matrix



LABELi18N = {
    'h': _('h'),
    'm':_('m'),
    's':_('s'),
    'G':_('Galaxy'),
    'OCL':_('Open cluster'),
    'GCL':_('Globular cluster'),
    'AST':_('Asterism'),
    'PN':_('Planetary nebula'),
    'N': _('Diffuse nebula'),
    'SNR':_('Supernova remnant'),
    'PG':_('Part of galaxy')
}

FR = {
    'h':'h',
    'm':'m',
    's':'s',
    'G':'Galaxie',
    'OCL':'Cluster Ouvert',
    'GCL':'Cluster Globulaire',
    'AST':'Astérisme',
    'PN': 'Nébuleuse Planétaire',
    'N': 'Nébuleuse Diffuse',
    'SNR':'Rémanent de Supernova',
    'PG':'Partie de Galaxie'
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

STARS_IN_SCALE = 10
LEGEND_MARGIN = 0.47
BASE_SCALE = 0.98
GRID_DENSITY = 4

RA_GRID_SCALE = [0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 3*60]
DEC_GRID_SCALE = [1, 2, 3, 5, 10, 15, 20, 30, 60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 45*60, 60*60]

MAG_SCALE_X = [0, 1,   2,   3,   4,    5,    25]
MAG_SCALE_Y = [0, 1.8, 3.3, 4.7, 6,  7.2,  18.0]

constell_lines_rect1 = None
constell_lines_rect2 = None
constell_bound_rect = None

class SkymapEngine:
    def __init__(self, graphics, language=LABELi18N, lm_stars=13.8, lm_deepsky=12.5, caption=''):
        """
        Width is width of the map including the legend in mm.
        """
        self.graphics = graphics
        self.config = EngineConfiguration()

        self.caption = caption
        self.language = language
        self.drawingwidth = self.graphics.gi_width
        self.drawingheight = self.graphics.gi_height
        self.min_radius = 1.0  # of deepsky symbols (mm)

        self.lm_stars = lm_stars
        self.lm_deepsky = lm_deepsky

        self.fieldcentre = None
        self.fieldradius = None
        self.fieldsize = None
        self.scene_scale = None
        self.drawing_scale = None
        self.legend_fontscale = None
        self.mirror_x = None
        self.mirror_y = None

        self.space_widget_allocator = None
        self.w_mag_scale = None
        self.w_map_scale = None
        self.w_orientation = None
        self.w_coords = None
        self.w_dso_legend = None
        self.w_telrad = None
        self.w_eyepiece = None
        self.w_picker = None
        self.mirroring_graphics = None
        self.picked_dso = None
        self.picked_star = None
        self.star_mag_r_shift = 0
        self.projection = None
        self.norm_field_radius = None


    def set_field(self, ra, dec, fieldradius, mirror_x=False, mirror_y=False, projection_type=ProjectionType.STEREOGRAPHIC):
        self.fieldradius = fieldradius
        self.fieldcentre = (ra, dec)

        wh = max(self.drawingwidth, self.drawingheight)

        self.fieldsize = fieldradius * math.sqrt(self.drawingwidth**2 + self.drawingheight**2) / wh

        if self.config.no_margin:
            self.scene_scale = (wh - self.config.legend_linewidth) / wh
        else:
            self.scene_scale = BASE_SCALE

        self.drawing_scale = self.scene_scale*wh/2.0/math.sin(fieldradius)
        self.legend_fontscale = min(self.config.legend_font_scale, wh/100.0)
        self.set_caption(self.caption)

        self.projection = self._create_projection(projection_type)
        self.projection.set_fieldcentre((0, 0))
        self.projection.set_scale(1.0, 1.0)
        self.norm_field_radius, _ = self.projection.radec_to_xy(fieldradius, 0)
        self.drawing_scale = self.scene_scale*wh / 2.0 / abs(self.norm_field_radius)
        self.projection.set_fieldcentre(self.fieldcentre)
        mulx = -1 if mirror_x else 1
        muly = -1 if mirror_y else 1
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y
        self.projection.set_scale(self.drawing_scale*mulx, self.drawing_scale*muly)

    def _create_projection(self, projection_type):
        if projection_type == ProjectionType.ORTHOGRAPHIC:
            return ProjectionOrthographic()
        if projection_type == ProjectionType.STEREOGRAPHIC:
            return ProjectionStereographic()
        return None

    def set_configuration(self, config):
        self.config = config
        self.star_mag_r_shift = 0
        if self.config.star_mag_shift > 0:
            self.star_mag_r_shift = self.magnitude_to_radius(self.lm_stars-self.config.star_mag_shift) - self.magnitude_to_radius(self.lm_stars)

    def get_field_radius_mm(self):
        return self.drawing_scale * self.norm_field_radius

    def get_field_rect_mm(self):
        x = self.scene_scale * self.drawingwidth / 2.0
        y = self.scene_scale * self.drawingheight / 2.0
        return -x, -y, x, y

    def set_language(self, language):
        """
        Set the language for the legend.
        """
        self.language = language

    def set_caption(self, caption):
        self.caption = caption
        if caption != '':
            self.graphics.set_dimensions(self.drawingwidth,self.drawingheight + self.legend_fontscale*self.graphics.gi_default_font_size*2.0)

    def make_map(self, used_catalogs, jd=None, showing_dsos=None, dso_highlights=None, highlights=None, dso_hide_filter=None,
                 extra_positions=None, hl_constellation=None, trajectory=[], visible_objects=None, use_optimized_mw=False,
                 transparent=False):
        """ Creates map using given graphics, params and config
        used_catalogs - UsedCatalogs data structure
        jd - julian date
        showing_dso - DSO forced to be shown even if they don't pass the filter
        dso_highlights - list of DsoHighlightDefinition that will be marked
        highlights - list of HighlightDefinitions that will be marked
        dso_hide_filter - list of DSO to be hidden, except showing_dso
        extra_positions - extra positions to be drawn
        hl_constellation - constellation name that will be highlighted
        trajectory - defined by list of points (ra, dec) points
        visible_objects - output array containing list of object visible on the map
        use_optimized_mw - use optimized milky way
        transparent - make chart transparent
        """
        visible_dso_collector = [] if visible_objects is not None else None
        self.picked_dso = None
        self.picked_star = None

        if self.mirror_x or self.mirror_y:
            self.mirroring_graphics = MirroringGraphics(self.graphics, self.mirror_x, self.mirror_y)
        else:
            self.mirroring_graphics = self.graphics

        self.create_widgets()

        self.graphics.set_background_rgb(self.config.background_color)

        self.graphics.new()

        if not transparent:
            self.graphics.clear()

        self.graphics.set_pen_rgb(self.config.draw_color)
        self.graphics.set_fill_rgb(self.config.draw_color)
        self.graphics.set_font(font=self.config.font, font_size=self.config.font_size)
        self.graphics.set_default_font_size(self.config.font_size)
        self.graphics.set_linewidth(self.config.legend_linewidth)


        if jd is not None:
            precession_matrix = np.linalg.inv(compute_precession_matrix(jd))
        else:
            precession_matrix = None

        if not self.config.legend_only:

            self.label_potential = LabelPotential(self.get_field_radius_mm())
            self.picked_star = None

            clip_path = self.space_widget_allocator.get_border_path()
            self.graphics.clip_path(clip_path)

            if self.config.show_simple_milky_way:
                self.draw_milky_way(used_catalogs.milky_way)
            elif self.config.show_enhanced_milky_way:
                self.draw_enhanced_milky_way(used_catalogs.enhanced_milky_way, use_optimized_mw)

            if self.config.show_equatorial_grid:
                # tm = time()
                self.draw_grid_equatorial()
                # print("Equatorial grid within {} s".format(str(time()-tm)), flush=True)

            if highlights:
                self.draw_highlights(highlights, visible_dso_collector)

            if used_catalogs.constellcatalog is not None:
                # tm = time()
                self.draw_constellations(used_catalogs.constellcatalog, jd, precession_matrix, hl_constellation)
                # print("constellations within {} s".format(str(time()-tm)), flush=True)

            if used_catalogs.unknown_nebulas is not None:
                self.draw_unknown_nebula(used_catalogs.unknown_nebulas)

            if used_catalogs.starcatalog is not None:
                # tm = time()
                self.draw_stars(used_catalogs.starcatalog, precession_matrix)
                # print("Stars within {} s".format(str(time()-tm)), flush=True)

            if used_catalogs.deepskycatalog is not None:
                # tm = time()
                self.draw_deepsky_objects(used_catalogs.deepskycatalog, precession_matrix, showing_dsos, dso_highlights, dso_hide_filter, visible_dso_collector)
                # print("DSO within {} s".format(str(time()-tm)), flush=True)

            if self.picked_dso is None and self.picked_star is not None:
                self.draw_picked_star()

            if extra_positions:
                self.draw_extra_objects(extra_positions)

            if trajectory:
                self.draw_trajectory(trajectory)

            self.graphics.reset_clip()

        # print('Drawing legend')
        self.draw_caption()

        # print('Drawing widgets')
        self.draw_widgets()

        # Draw border of field-of-view
        self.draw_field_border()

        # tm = time()
        self.graphics.finish()
        # print("Rest {} ms".format(str(time()-tm)), flush=True)

        if visible_dso_collector is not None:
            visible_dso_collector.sort(key=lambda x: x[0])
            for obj in visible_dso_collector:
                visible_objects.extend([obj[1], obj[2], obj[3], obj[4], obj[5]])

    def draw_caption(self):
        if self.caption != '':
            font_size = self.get_legend_font_size()
            self.graphics.set_font(self.graphics.gi_font, 2.0*font_size)
            self.graphics.text_centred(0, self.drawingwidth/2.0*BASE_SCALE + font_size, self.caption)

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
        # Set the font_size for the entire legend
        font_size = self.get_legend_font_size()
        self.graphics.set_font(self.graphics.gi_font, font_size=font_size)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        if self.config.fov_telrad:
            self.w_telrad.draw(self.graphics)
        if self.config.eyepiece_fov is not None:
            self.w_eyepiece.draw(self.graphics)
        if self.config.show_picker and self.config.picker_radius > 0:
            self.w_picker.draw(self.graphics)
        if self.config.show_mag_scale_legend:
            self.w_mag_scale.draw(self.graphics, self.config.legend_only)
        if self.config.show_map_scale_legend:
            self.w_map_scale.draw(self.graphics, self.config.legend_only)
        if self.config.show_orientation_legend:
            self.w_orientation.draw(self.graphics, x1, y2, self.config.legend_only)
        if self.config.show_coords_legend:
            self.w_coords.draw(self.graphics, left=x2-font_size/2, bottom=y2-font_size, ra=self.fieldcentre[0], dec=self.fieldcentre[1], legend_only=self.config.legend_only)
        if self.config.show_dso_legend:
            self.w_dso_legend.draw_dso_legend(self, self.graphics, self.config.legend_only)

    def draw_deepsky_objects(self, deepsky_catalog, precession_matrix, showing_dsos, dso_highlights, dso_hide_filter, visible_dso_collector):
        if not self.config.show_deepsky:
            return

        # Draw deep sky
        # print('Drawing deepsky...')

        deepsky_list = deepsky_catalog.select_deepsky(self.fieldcentre, self.fieldsize, self.lm_deepsky)

        filtered_showing_dsos = []

        dso_hide_filter_set = { dso for dso in dso_hide_filter }  if dso_hide_filter else {}

        if showing_dsos:
            for dso in showing_dsos:
                if dso not in deepsky_list:
                    filtered_showing_dsos.append(dso)
                if dso in dso_hide_filter_set:
                    dso_hide_filter_set.remove(dso)

        if dso_highlights:
            for dso_highlight in dso_highlights:
                for dso in dso_highlight.dsos:
                    if dso not in deepsky_list and dso not in filtered_showing_dsos:
                        filtered_showing_dsos.append(dso)
                    if dso in dso_hide_filter_set:
                        dso_hide_filter_set.remove(dso)

        deepsky_list.sort(key=lambda x: x.mag)
        deepsky_list_ext = []

        self.calc_deepsky_list_ext(precession_matrix, deepsky_list_ext, deepsky_list)
        self.calc_deepsky_list_ext(precession_matrix, deepsky_list_ext, filtered_showing_dsos)

        self.label_potential.add_deepsky_list(deepsky_list_ext)

        # print('Drawing objects...')
        pick_r = self.config.picker_radius if self.config.picker_radius > 0 else 0
        if pick_r > 0:
            pick_min_r = pick_r**2
            for dso, x, y, rlong in deepsky_list_ext:
                if pick_r > 0 and abs(x) < pick_r and abs(y) < pick_r:
                    r = x*x + y*y
                    if r < pick_min_r:
                        self.picked_dso = dso
                        pick_min_r = r

        for dso, x, y, rlong in deepsky_list_ext:
            if dso in dso_hide_filter_set:
                continue

            label = dso.label()
            if self.config.show_dso_mag and dso.mag is not None and dso.mag != -100:
                label_mag = '{:.1f}'.format(dso.mag)
            else:
                label_mag = None

            if dso_highlights:
                for dso_highlight in dso_highlights:
                    if dso in dso_highlight.dsos:
                        self.draw_dso_hightlight(x, y, rlong, label, dso_highlight, visible_dso_collector)
                        break

            rlong = dso.rlong if dso.rlong is not None else self.min_radius
            rshort = dso.rshort if dso.rshort is not None else self.min_radius
            rlong = rlong*self.drawing_scale
            rshort = rshort*self.drawing_scale
            posangle = dso.position_angle+self.projection.direction_ddec(dso.ra, dso.dec)+0.5*np.pi

            if rlong <= self.min_radius:
                rshort *= self.min_radius/rlong
                rlong = self.min_radius

            label_ext = None
            if dso == self.picked_dso and dso.mag < 100.0:
                label_ext = '{:.2f}m'.format(dso.mag)

            label_length = self.graphics.text_width(label)
            labelpos = -1

            if dso.type == deepsky.G:
                labelpos_list = self.galaxy_labelpos(x, y, rlong, rshort, posangle, label_length)
            elif dso.type == deepsky.N:
                labelpos_list = self.diffuse_nebula_labelpos(x, y, 2.0*rlong, 2.0*rshort, posangle, label_length)
            elif dso.type in [deepsky.PN, deepsky.OC, deepsky.GC, deepsky.SNR, deepsky.GALCL]:
                labelpos_list = self.circular_object_labelpos(x, y, rlong, label_length)
            elif dso.type == deepsky.STARS:
                labelpos_list = self.asterism_labelpos(x, y, rlong, label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(x, y, rlong, label_length)

            pot = 1e+30
            for labelpos_index in range(len(labelpos_list)):
                [[x1, y1], [x2, y2], [x3, y3]] = labelpos_list[labelpos_index]
                pot1 = self.label_potential.compute_potential(x2, y2)
                # self.label_potential.compute_potential(x1,y1),
                # self.label_potential.compute_potential(x3,y3)])
                if pot1 < pot:
                    pot = pot1
                    labelpos = labelpos_index

            [xx, yy] = labelpos_list[labelpos][1]
            self.label_potential.add_position(xx, yy, label_length)

            if dso.type == deepsky.G:
                self.galaxy(x, y, rlong, rshort, posangle, dso.mag, label, label_mag, label_ext, labelpos)
            elif dso.type == deepsky.N:
                has_outlines = False
                if self.config.show_nebula_outlines and dso.outlines is not None and rlong > self.min_radius:
                    has_outlines = self.draw_dso_outlines(dso, x, y, rlong, rshort, posangle, label, label_ext, labelpos)
                if not has_outlines:
                    self.diffuse_nebula(x, y, 2.0*rlong, 2.0*rshort, posangle, label, label_mag, label_ext, labelpos)
            elif dso.type == deepsky.PN:
                self.planetary_nebula(x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == deepsky.OC:
                if self.config.show_nebula_outlines and dso.outlines is not None:
                    has_outlines = self.draw_dso_outlines(dso, x, y, rlong, rshort)
                self.open_cluster(x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == deepsky.GC:
                self.globular_cluster(x, y, rlong, label, label_mag, label_ext, labelpos)
            elif dso.type == deepsky.STARS:
                self.asterism(x, y, rlong, label, label_ext, labelpos)
            elif dso.type == deepsky.SNR:
                self.supernova_remnant(x, y, rlong, label, label_ext, labelpos)
            elif dso.type == deepsky.GALCL:
                self.galaxy_cluster(x, y, rlong, label, label_ext, labelpos)
            else:
                self.unknown_object(x, y, rlong, label, label_ext, labelpos)

            if visible_dso_collector is not None:
                xs1, ys1 = x-rlong, y-rlong
                xs2, ys2 = x+rlong, y+rlong
                if self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2):
                    xp1, yp1 = self.mirroring_graphics.to_pixel(xs1, ys1)
                    xp2, yp2 = self.mirroring_graphics.to_pixel(xs2, ys2)
                    xp1, yp1, xp2, yp2 = self.align_rect_coords(xp1, yp1, xp2, yp2)
                    visible_dso_collector.append([rlong, label.replace(' ', ''), xp1, yp1, xp2, yp2])
                    if self.picked_dso == dso:
                        pick_xp1, pick_yp1 = self.mirroring_graphics.to_pixel(-pick_r, -pick_r)
                        pick_xp2, pick_yp2 = self.mirroring_graphics.to_pixel(pick_r, pick_r)
                        pick_xp1, pick_yp1, pick_xp2, pick_yp2 = self.align_rect_coords(pick_xp1, pick_yp1, pick_xp2, pick_yp2)
                        visible_dso_collector.append([rlong, label.replace(' ', ''), pick_xp1, pick_yp1, pick_xp2, pick_yp2])

    def calc_deepsky_list_ext(self, precession_matrix, deepsky_list_ext, dso_list):
        if precession_matrix is not None:
            mat_rect_dso = np.empty([len(dso_list), 3])
            for i, dso in enumerate(dso_list):
               mat_rect_dso[i] = [dso.x, dso.y, dso.z]
            mat_rect_dso = np.matmul(mat_rect_dso, precession_matrix)
            ra_ar, dec_ar = np_rect_to_sphere(mat_rect_dso[:,[0]], mat_rect_dso[:,[1]], mat_rect_dso[:,[2]])
        else:
            ra_ar = np.empty([len(dso_list)])
            dec_ar = np.empty([len(dso_list)])
            for i, dso in enumerate(dso_list):
                ra_ar[i] = dso.ra
                dec_ar[i] = dso.dec

        x, y, z = self.projection.np_radec_to_xyz(ra_ar, dec_ar)
        nzopt = not self.projection.is_zoptim()

        for i, dso in enumerate(dso_list):
            if nzopt or z[i] > 0:
                if dso.rlong is None:
                    rlong = self.min_radius
                else:
                    rlong = dso.rlong*self.drawing_scale
                    if rlong < self.min_radius:
                        rlong = self.min_radius
                deepsky_list_ext.append((dso, x[i], y[i], rlong))


    def draw_dso_outlines(self, dso, x, y, rlong, rshort, posangle=None, label=None, label_ext=None,  labelpos=None):
        lev_shift = 0
        has_outlines = False
        draw_label = True
        for outl_lev in range(2, -1, -1):
            outlines_ar = dso.outlines[outl_lev]
            if outlines_ar:
                has_outlines = True
                for outlines in outlines_ar:
                    x_outl, y_outl = self.projection.np_radec_to_xy(outlines[0], outlines[1])
                    self.diffuse_nebula_outlines(x, y, x_outl, y_outl, outl_lev+lev_shift, 2.0*rlong, 2.0*rshort, posangle,
                                                 label, label_ext, draw_label, labelpos)
                    draw_label = False
            else:
                lev_shift += 1
        return has_outlines

    def draw_unknown_nebula(self, unknown_nebulas):
        zopt = self.projection.is_zoptim()
        for uneb in unknown_nebulas:
            ra = (uneb.ra_min + uneb.ra_max) / 2.0
            dec = (uneb.dec_min + uneb.dec_max) / 2.0
            x, y, z = self.projection.radec_to_xyz(ra, dec)
            if zopt and z <=0:
                continue
            for outl_lev in range(3):
                outlines = uneb.outlines[outl_lev]
                if not outlines:
                    continue
                for outl in outlines:
                    if not zopt or z > 0:
                        x_outl, y_outl = self.projection.np_radec_to_xy(outl[0], outl[1])
                        self.unknown_diffuse_nebula_outlines(x_outl, y_outl, outl_lev)

    def draw_milky_way(self, milky_way_lines):
        x, y, z = self.projection.np_radec_to_xyz(milky_way_lines[:, 0], milky_way_lines[:, 1])
        self.graphics.set_pen_rgb(self.config.milky_way_color)
        self.graphics.set_fill_rgb(self.config.milky_way_color)
        self.graphics.set_linewidth(self.config.milky_way_linewidth)

        nzopt = not self.projection.is_zoptim()

        polygon = None
        for i in range(len(x)-1):
            if milky_way_lines[i][2] == 0:
                if polygon is not None and len(polygon) > 2:
                    self.graphics.polygon(polygon, DrawMode.BOTH)
                x1, y1, z1 = x[i].item(), y[i].item(), z[i].item()
                polygon = None
                if nzopt or z1 > 0:
                    polygon = [[x1, y1]]
            else:
                x1, y1, z1 = x[i].item(), y[i].item(), z[i].item()
                if nzopt or z1 > 0:
                    if polygon is None:
                        polygon = []
                    polygon.append([x1, y1])

        if polygon is not None and len(polygon) > 2:
            self.graphics.polygon(polygon, DrawMode.FILL)

    def draw_enhanced_milky_way(self, enhanced_milky_way, use_optimized_mw):
        self.graphics.antialias_off()

        tm = time()

        mw_points = enhanced_milky_way.mw_points

        x, y, z = self.projection.np_radec_to_xyz(mw_points[:, 0], mw_points[:, 1])

        self.graphics.set_linewidth(0)
        fd = self.config.enhanced_milky_way_fade

        if use_optimized_mw:
            selected_polygons = enhanced_milky_way.select_opti_polygons(self.fieldcentre, self.fieldsize)
        else:
            selected_polygons = enhanced_milky_way.select_polygons(self.fieldcentre, self.fieldsize)

        fr_x1, fr_y1, fr_x2, fr_y2 = self.get_field_rect_mm()

        total_polygons = 0
        zopt = self.projection.is_zoptim()
        for polygon_index in selected_polygons:
            if use_optimized_mw:
                polygon, rgb = enhanced_milky_way.mw_opti_polygons[polygon_index]
            else:
                polygon, rgb = enhanced_milky_way.mw_polygons[polygon_index]

            if zopt and any(z[i] < 0 for i in polygon):
                continue

            xy_polygon = [(x[i], y[i]) for i in polygon]
            for xp, yp in xy_polygon:
                if (xp >= fr_x1) and (xp <= fr_x2) and (yp >= fr_y1) and (yp <= fr_y2):
                    break
            else:
                continue

            frgb = (fd[0] + rgb[0] * fd[1], fd[2] + rgb[1] * fd[3], fd[4] + rgb[2] * fd[5])
            total_polygons += 1
            self.graphics.set_fill_rgb(frgb)
            self.graphics.polygon(xy_polygon, DrawMode.FILL)

        self.graphics.antialias_on()
        tmp=str(time()-tm)
        print( _("Enhanced milky way draw within {} s. Total polygons={}".format(tmp, total_polygons)) , flush=True)

    def draw_extra_objects(self,extra_positions):
        # Draw extra objects
        # print('Drawing extra objects...')
        nzopt = not self.projection.is_zoptim()
        for rax, decx, label, labelpos in extra_positions:
            x, y, z = self.projection.radec_to_xyz(rax, decx)
            if nzopt or z >= 0:
                self.unknown_object(x, y, self.min_radius, label, labelpos)

    def draw_highlights(self, highlights, visible_dso_collector):
        # Draw highlighted objects
        # print('Drawing highlighted objects...')
        fn = self.graphics.gi_default_font_size
        highlight_fh = self.config.highlight_label_font_scale * fn
        nzopt = not self.projection.is_zoptim()

        for hl_def in highlights:
            for rax, decx, object_name, label in hl_def.data:
                x, y, z = self.projection.radec_to_xyz(rax, decx)
                if nzopt or z >= 0:
                    self.graphics.set_pen_rgb(hl_def.color)
                    self.graphics.set_linewidth(hl_def.line_width)
                    if hl_def.style == 'cross':
                        r = self.config.font_size * 2
                        self.mirroring_graphics.line(x-r, y, x-r/2, y)
                        self.mirroring_graphics.line(x+r, y, x+r/2, y)
                        self.mirroring_graphics.line(x, y+r, x, y+r/2)
                        self.mirroring_graphics.line(x, y-r, x, y-r/2)
                    elif hl_def.style == 'circle':
                        r = self.config.font_size
                        self.mirroring_graphics.circle(x, y, r)
                        if label:
                            self.draw_circular_object_label(x, y, r, label, fh=highlight_fh)
                        if object_name and visible_dso_collector is not None:
                            xs1, ys1 = x-r, y-r
                            xs2, ys2 = x+r, y+r
                            if self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2):
                                xp1, yp1 = self.mirroring_graphics.to_pixel(xs1, ys1)
                                xp2, yp2 = self.mirroring_graphics.to_pixel(xs2, ys2)
                                xp1, yp1, xp2, yp2 = self.align_rect_coords(xp1, yp1, xp2, yp2)
                                visible_dso_collector.append([r, object_name, xp1, yp1, xp2, yp2])

    def draw_dso_hightlight(self, x, y, rlong, dso_name, dso_highligth, visible_dso_collector):
        self.graphics.set_pen_rgb(dso_highligth.color)
        self.graphics.set_linewidth(dso_highligth.line_width)
        if dso_highligth.dash and len(dso_highligth.dash) == 2:
            self.graphics.set_dashed_line(dso_highligth.dash[0], dso_highligth.dash[1])
        else:
            self.graphics.set_solid_line()

        r = self.config.font_size
        self.mirroring_graphics.circle(x, y, r)
        xs1, ys1 = x-r, y-r
        xs2, ys2 = x+r, y+r
        if visible_dso_collector is not None and (self.graphics.on_screen(xs1, ys1) or self.graphics.on_screen(xs2, ys2)):
            xp1, yp1 = self.mirroring_graphics.to_pixel(xs1, ys1)
            xp2, yp2 = self.mirroring_graphics.to_pixel(xs2, ys2)
            xp1, yp1, xp2, yp2 = self.align_rect_coords(xp1, yp1, xp2, yp2)
            visible_dso_collector.append([r, dso_name.replace(' ', ''), xp1, yp1, xp2, yp2])

    def draw_trajectory(self, trajectory):
        # Draw extra objects
        # print('Drawing trajectory...')
        self.graphics.set_pen_rgb(self.config.dso_color)
        self.graphics.set_solid_line()

        fh = self.graphics.gi_default_font_size
        x1, y1, z1 = (None, None, None)
        nzopt = not self.projection.is_zoptim()

        labels = []

        for i in range(0, len(trajectory)):
            rax2, decx2, label2 = trajectory[i]
            x2, y2, z2 = self.projection.radec_to_xyz(rax2, decx2)

            if i > 0:
                self.graphics.set_linewidth(self.config.constellation_linewidth)
                if nzopt or (z1 > 0 and z2 > 0):
                    self.mirroring_graphics.line(x1, y1, x2, y2)
                    self.draw_trajectory_tick(x1, y1, x2, y2)
                    if i == 1:
                        self.draw_trajectory_tick(x2, y2, x1, y1)

            nx, ny = (None, None)
            if x1 is not None:
                n = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                if n != 0:
                    nx = (x2-x1)/n
                    ny = (y2-y1)/n

            labels.append([x2, y2, z2, nx, ny, label2])

            x1, y1, z1 = (x2, y2, z2)

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

        r = self.min_radius * 1.2 / 2**0.5
        for x, y, z, nx, ny, label in labels:
            if nzopt or z > 0:
                if label_pos == 1:
                    self.mirroring_graphics.text_centred(x, y + r + fh, label)
                elif label_pos == 2:
                    self.mirroring_graphics.text_right(x + r + fh/4, y - fh/2, label)
                else:
                    self.mirroring_graphics.text_centred(x, y - r - fh/2.0, label)

    def draw_trajectory_tick(self, x1, y1, x2, y2):
        dx = x2-x1
        dy = y2-y1
        dr = math.sqrt(dx * dx + dy*dy)
        ddx = dx * 1.0 / dr
        ddy = dy * 1.0 / dr
        self.graphics.set_linewidth(1.5*self.config.constellation_linewidth)
        self.mirroring_graphics.line(x2-ddy, y2+ddx, x2+ddy, y2-ddx)

    def magnitude_to_radius(self, magnitude):
        # radius = 0.13*1.35**(int(self.lm_stars)-magnitude)
        mag_d = self.lm_stars - np.clip(magnitude, a_min=None, a_max=self.lm_stars)
        mag_s = np.interp(mag_d, MAG_SCALE_X, MAG_SCALE_Y)
        radius = 0.1 * 1.33 ** mag_s + self.star_mag_r_shift
        return radius

    def draw_stars(self, star_catalog, precession_matrix):
        # Select and draw stars
        # print('Drawing stars...')

        pick_r = self.config.picker_radius if self.config.picker_radius > 0 else 0
        selection = star_catalog.select_stars(self.fieldcentre, self.fieldsize, self.lm_stars, precession_matrix)
        if selection is None or len(selection) == 0:
            print(_('No stars found.'))
            return

        # print("Stars selection {} ms".format(str(time()-tm)), flush=True)
        print(_('{} stars in map.'.format(selection.shape[0])))
        var=str(round(max(selection['mag']), 2))
        print(_(f'Faintest star : {var}' )) 

        # tm = time()
        x, y = self.projection.np_radec_to_xy(selection['ra'], selection['dec'])

        # print("Stars view positioning {} ms".format(str(time()-tm)), flush=True)

        mag = selection['mag']
        bsc = selection['bsc']

        indices = np.argsort(mag)
        magsorted = mag[indices]
        rsorted = self.magnitude_to_radius(magsorted)

        if not self.config.star_colors:
            # self.graphics.set_pen_rgb((self.config.draw_color[0]/3, self.config.draw_color[0]/3, self.config.draw_color[0]/3))
            self.graphics.set_fill_rgb(self.config.draw_color)

        self.graphics.set_linewidth(0)

        star_labels = []
        star_mag_defs = []
        pick_min_r = pick_r**2
        x1, y1, x2, y2 = self.get_field_rect_mm()
        for i, index in enumerate(indices):
            xx, yy, rr = (x[index].item(), y[index].item(), rsorted[i].item(),)
            if (xx < x1-rr) or (xx > x2+rr) or (yy < y1-rr) or (yy > y2+rr):
                continue
            star_color = star_catalog.get_star_color(selection[index])
            if self.config.show_star_circles:
                self.star(xx, yy, rr, star_color)

            if pick_r > 0 and abs(xx) < pick_r and abs(yy) < pick_r:
                r = xx**2 + yy**2
                if r < pick_min_r:
                    self.picked_star = (xx, yy, rr, mag[index], bsc[index])
                    pick_min_r = r
            elif self.config.show_star_mag:
                star_mag_defs.append((xx, yy, rr, mag[index], star_color))
            elif self.config.show_star_labels:
                bsc_star = selection[index]['bsc']
                if bsc_star is not None:
                    if isinstance(bsc_star, str):
                        slabel = bsc_star
                    else:
                        slabel = bsc_star.greek
                        if slabel:
                            slabel = STAR_LABELS[slabel] + bsc_star.greek_no
                        elif self.config.show_flamsteed:
                            slabel = bsc_star.flamsteed
                            if slabel and self.config.flamsteed_numbers_only:
                                slabel = slabel.split()[0]
                    if slabel:
                        label_length = self.graphics.text_width(slabel)
                        labelpos_list = self.circular_object_labelpos(xx, yy, rr, label_length)
                        pot = 1e+30
                        for labelpos_index in range(len(labelpos_list)):
                            [[lx1, ly1], [lx2, ly2], [lx3, ly3]] = labelpos_list[labelpos_index]
                            pot1 = self.label_potential.compute_potential(lx2, ly2)
                            if labelpos_index == 0:
                                pot1 *= 0.6 # favour label right
                            # self.label_potential.compute_potential(x1,y1),
                            # self.label_potential.compute_potential(x3,y3)])
                            if pot1 < pot:
                                pot = pot1
                                labelpos = labelpos_index

                        [lx, ly] = labelpos_list[labelpos][1]
                        self.label_potential.add_position(lx, ly, label_length)
                        star_labels.append((xx, yy, rr, labelpos, bsc_star))

        if len(star_mag_defs) > 0:
            self.graphics.set_font(self.graphics.gi_font, 0.8*self.graphics.gi_default_font_size)
            for x, y, r, mag, star_color in star_mag_defs:
                diff_mag = self.lm_stars - mag
                if diff_mag < 0:
                    diff_mag = 0
                if diff_mag > 5:
                    diff_mag = 5
                star_intensity = 0.4 + 0.6 * diff_mag / 5;

                self.graphics.set_pen_rgb((self.config.label_color[0] * star_intensity,
                                           self.config.label_color[1] * star_intensity,
                                           self.config.label_color[2] * star_intensity))

                self.draw_circular_object_label(x, y, r, str(mag), set_pen=False)

        if len(star_labels) > 0:
            self.draw_stars_labels(star_labels)

    def draw_picked_star(self):
        if self.picked_star is not None:
            x, y, r, mag, bsc = self.picked_star
            self.graphics.set_font(self.graphics.gi_font, 0.9*self.graphics.gi_default_font_size)
            label = str(mag)
            if bsc is not None:
                if bsc.greek:
                    label += '(' + STAR_LABELS[bsc.greek] + bsc.greek_no + ' ' + bsc.constellation.capitalize() + ')'
                elif bsc.flamsteed:
                    label += '(' + str(bsc.flamsteed) + ')'
                elif bsc.HD is not None:
                    label += '(HD' + str(bsc.HD) + ')'
            self.draw_circular_object_label(x, y, r, label)

    def draw_stars_labels(self, star_labels):
        fn = self.graphics.gi_default_font_size
        printed = {}
        bayer_fh = self.config.bayer_label_font_scale * fn
        flamsteed_fh = self.config.flamsteed_label_font_scale * fn
        for x, y, r, labelpos, star in star_labels:
            if isinstance(star, str):
                self.graphics.set_font(self.graphics.gi_font, 0.9*fn)
                self.draw_circular_object_label(x, y, r, star, labelpos)
            else:
                slabel = star.greek
                if not slabel:
                    is_greek = False
                    if self.config.show_flamsteed:
                        slabel = star.flamsteed
                        if slabel and self.config.flamsteed_numbers_only:
                            slabel = slabel.split()[0]
                else:
                    is_greek = True
                    slabel = STAR_LABELS.get(slabel) + star.greek_no
                if slabel:
                    printed_labels = printed.setdefault(star.constellation, set())
                    if slabel not in printed_labels:
                        printed_labels.add(slabel)
                        if is_greek:
                            self.graphics.set_font(self.graphics.gi_font, bayer_fh, self.config.bayer_label_font_style)
                        else:
                            self.graphics.set_font(self.graphics.gi_font, flamsteed_fh, self.config.flamsteed_label_font_style)
                        self.draw_circular_object_label(x, y, r, slabel, labelpos)

    def draw_constellations(self, constell_catalog, jd, precession_matrix, hl_constellation):
        # print('Drawing constellations...')
        if self.config.show_constellation_borders:
            self.draw_constellation_boundaries(constell_catalog, jd, precession_matrix, hl_constellation)
        if self.config.show_constellation_shapes:
            self.draw_constellation_shapes(constell_catalog, jd, precession_matrix)

    def draw_grid_equatorial(self):
        # print('Drawing equatorial grid...')
        self.graphics.save()
        self.graphics.set_linewidth(self.config.grid_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.grid_color)

        self.draw_grid_dec()
        self.draw_grid_ra()

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
        return prefix + label_fmt.format(deg, minutes)

    def grid_ra_label(self, ra_minutes, label_fmt):
        hrs = int(ra_minutes/60)
        mins = int(ra_minutes) % 60
        secs = int(ra_minutes % 1 * 60)
        return label_fmt.format(hrs, mins, secs)

    def draw_grid_dec(self):
        prev_steps, prev_grid_minutes = (None, None)
        for grid_minutes in DEC_GRID_SCALE:
            steps = self.fieldradius / (np.pi * grid_minutes / (180 * 60))
            if steps < GRID_DENSITY:
                if prev_steps is not None:
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
            if (dec > dec_min) and (dec < dec_max):
                self.draw_grid_dec_line(dec, dec_minutes, label_fmt)
            dec_minutes += grid_minutes

    def draw_grid_dec_line(self, dec, dec_minutes, label_fmt):
        dra = self.fieldradius / 10
        x11, y11, z11 = (None, None, None)
        agg_ra = 0
        nzopt = not self.projection.is_zoptim()

        while True:
            x12, y12, z12 = self.projection.radec_to_xyz(self.fieldcentre[0] + agg_ra, dec)
            x22, y22, z22 = self.projection.radec_to_xyz(self.fieldcentre[0] - agg_ra, dec)
            if x11 is not None and (nzopt or (z11 > 0 and z12 > 0)):
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
                fh = self.graphics.gi_default_font_size
                if dec >= 0:
                    self.graphics.text_right(2*fh/3, +fh/3, label)
                else:
                    self.graphics.text_right(2*fh/3, -fh, label)
                self.graphics.restore()
                break
            x11, y11, z11 = (x12, y12, z12)
            x21, y21, z21 = (x22, y22, z22)

    def draw_grid_ra(self):
        prev_steps, prev_grid_minutes = (None, None)
        fc_cos = math.cos(self.fieldcentre[1])
        for grid_minutes in RA_GRID_SCALE:
            steps = self.fieldradius / (fc_cos * (np.pi * grid_minutes / (12 * 60)))
            if steps < GRID_DENSITY:
                if prev_steps is not None:
                    if prev_steps-GRID_DENSITY < GRID_DENSITY-steps:
                        grid_minutes = prev_grid_minutes
                break
            prev_steps, prev_grid_minutes = (steps, grid_minutes)

        max_visible_dec = self.fieldcentre[1]+self.fieldradius if self.fieldcentre[1] > 0 else self.fieldcentre[1]-self.fieldradius;
        if max_visible_dec >= np.pi/2 or max_visible_dec <= -np.pi/2:
            ra_size = 2*np.pi
        else:
            ra_size = self.fieldradius / math.cos(max_visible_dec)
            if ra_size > 2*np.pi:
                ra_size = 2*np.pi

        if grid_minutes >= 60:
            label_fmt = '{}h'
        elif grid_minutes >= 1:
            label_fmt = '{}h{:02d}m'
        else:
            label_fmt = '{}h{:02d}m{:02d}s'

        ra_minutes = 0

        while ra_minutes < 24*60:
            ra = np.pi * ra_minutes / (12*60)
            if abs(self.fieldcentre[0]-ra) < ra_size or abs(self.fieldcentre[0]-2*np.pi-ra) < ra_size or abs(2*np.pi+self.fieldcentre[0]-ra) < ra_size:
                self.draw_grid_ra_line(ra, ra_minutes, label_fmt)
            ra_minutes += grid_minutes

    def draw_grid_ra_line(self, ra, ra_minutes, label_fmt):
        ddec = self.fieldradius / 10
        x11, y11, z11 = (None, None, None)
        x21, y21, z21 = (None, None, None)
        agg_dec = 0
        nzopt = not self.projection.is_zoptim()

        while True:
            x12, y12, z12 = self.projection.radec_to_xyz(ra, self.fieldcentre[1] + agg_dec)
            x22, y22, z22 = self.projection.radec_to_xyz(ra, self.fieldcentre[1] - agg_dec)
            if x11 is not None:
                if nzopt or (z11 > 0 and z12 > 0):
                    self.mirroring_graphics.line(x11, y11, x12, y12)
                if nzopt or (z21 > 0 and z22 > 0):
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
                fh = self.graphics.gi_default_font_size
                self.graphics.text_right(2*fh/3, fh/3, label)
                self.graphics.restore()
                break
            x11, y11, z11 = (x12, y12, z12)
            x21, y21, z21 = (x22, y22, z22)


    def draw_constellation_shapes(self, constell_catalog, jd, precession_matrix):
        self.graphics.set_linewidth(self.config.constellation_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.constellation_lines_color)

        global constell_lines_rect1, constell_lines_rect2

        if jd is not None:
            if constell_lines_rect1 is None:
                points = constell_catalog.all_constell_lines
                xr1, yr1, zr1 = np_sphere_to_rect(points[:,0], points[:,1])
                constell_lines_rect1 = np.column_stack((xr1, yr1, zr1))
                xr2, yr2, zr2 = np_sphere_to_rect(points[:,2], points[:,3])
                constell_lines_rect2 = np.column_stack((xr2, yr2, zr2))
            prec_rect1 = np.matmul(constell_lines_rect1, precession_matrix)
            ra1, dec1 = np_rect_to_sphere(prec_rect1[:,[0]], prec_rect1[:,[1]], prec_rect1[:,[2]])
            prec_rect2 = np.matmul(constell_lines_rect2, precession_matrix)
            ra2, dec2 = np_rect_to_sphere(prec_rect2[:,[0]], prec_rect2[:,[1]], prec_rect2[:,[2]])
            constell_lines = np.column_stack((ra1, dec1, ra2, dec2))
        else:
            constell_lines = constell_catalog.all_constell_lines

        x1, y1, z1 = self.projection.np_radec_to_xyz(constell_lines[:, 0], constell_lines[:, 1])
        x2, y2, z2 = self.projection.np_radec_to_xyz(constell_lines[:, 2], constell_lines[:, 3])

        nzopt = not self.projection.is_zoptim()

        for i in range(len(x1)):
            if nzopt or (z1[i] > 0 and z2[i] > 0):
                c1 = self.graphics.cohen_sutherland_encode(x1[i], y1[i])
                c2 = self.graphics.cohen_sutherland_encode(x2[i], y2[i])
                if (c1 | c2) != 0 and (c1 & c2) != 0:
                    continue
                if nzopt and z1[i] < 0 and z2[i] < 0:
                    c = c1 | c2
                    if (c & 0b1100 == 0b1100) or (c & 0b0011 == 0b0011):
                        continue

                if self.config.constellation_linespace > 0:
                    dx = x2[i] - x1[i]
                    dy = y2[i] - y1[i]
                    dr = math.sqrt(dx * dx + dy*dy)
                    ddx = dx * self.config.constellation_linespace / dr
                    ddy = dy * self.config.constellation_linespace / dr
                    self.mirroring_graphics.line(x1[i] + ddx, y1[i] + ddy, x2[i] - ddx, y2[i] - ddy)
                else:
                    self.mirroring_graphics.line(x1[i], y1[i], x2[i], y2[i])

    def draw_constellation_boundaries(self, constell_catalog, jd, precession_matrix, hl_constellation):
        self.graphics.set_dashed_line(0.6, 1.2)

        global constell_bound_rect

        if jd is not None:
            if constell_bound_rect is None:
                points = constell_catalog.boundaries_points
                xr, yr, zr = np_sphere_to_rect(points[:,0], points[:,1])
                constell_bound_rect = np.column_stack((xr, yr, zr))

            prec_rect = np.matmul(constell_bound_rect, precession_matrix)
            ra, dec = np_rect_to_sphere(prec_rect[:,[0]], prec_rect[:,[1]], prec_rect[:,[2]])
            constell_boundaries = np.column_stack((ra, dec))
        else:
            constell_boundaries = constell_catalog.boundaries_points

        x, y, z = self.projection.np_radec_to_xyz(constell_boundaries[:,0], constell_boundaries[:,1])

        hl_constellation = hl_constellation.upper() if hl_constellation else None

        wh_min = 2.5 # 2.5mm min interp distance
        flat_dec = np.pi*75/180 # boundaries can be linearized above 75 deg
        flat_rac_interp = np.pi*7/180 # some "magic" angle 7 deg.
        max_angle2 = (1 / 180 * np.pi)

        nzopt = not self.projection.is_zoptim()

        for index1, index2, cons1, cons2 in constell_catalog.boundaries_lines:
            if nzopt or (z[index1] > 0 and z[index2] > 0):
                if hl_constellation and (hl_constellation == cons1 or hl_constellation == cons2):
                    self.graphics.set_pen_rgb(self.config.constellation_hl_border_color)
                    self.graphics.set_linewidth(self.config.constellation_linewidth * 1.75)
                else:
                    self.graphics.set_pen_rgb(self.config.constellation_border_color)
                    self.graphics.set_linewidth(self.config.constellation_border_linewidth)

                x_start, y_start, z_start = x[index1], y[index1], z[index1]
                x_end, y_end, z_end = x[index2], y[index2], z[index2]

                ra_start, dec_start = constell_boundaries[index1]
                ra_end, dec_end = constell_boundaries[index2]

                if abs(ra_end - ra_start) > np.pi:
                    if ra_end < ra_start:
                        ra_start, ra_end = ra_end, ra_start
                        dec_start, dec_end = dec_end, dec_start
                        x_start, y_start, z_start, x_end, y_end, z_end = x_end, y_end, z_end, x_start, y_start, z_start
                    d_ra = (ra_end - (ra_start + 2 * np.pi))
                else:
                    d_ra = (ra_end - ra_start)

                d_dec = (dec_end - dec_start)

                interpolate = True
                if (abs(dec_start) > flat_dec or abs(dec_end) > flat_dec) and abs(d_ra) < flat_rac_interp:
                    interpolate = False

                if interpolate:
                    divisions = self.calc_boundary_divisions(1, 1, wh_min, max_angle2, x_start, y_start, z_start, x_end, y_end, z_end, ra_start, dec_start, ra_end, dec_end)
                else:
                    divisions = 1

                if divisions == 0:
                    continue

                if divisions == 1:
                    self.mirroring_graphics.line(x_start, y_start, x_end, y_end)
                else:
                    dd_ra = d_ra / divisions
                    dd_dec = d_dec / divisions
                    vertices = [(x_start, y_start)]
                    ra1, dec1 = ra_start, dec_start

                    for i in range(divisions-1):
                        dec2 = dec1 + dd_dec
                        ra2 = ra1 + dd_ra
                        x2, y2 = self.projection.radec_to_xy(ra2, dec2)
                        vertices.append((x2, y2))
                        ra1, dec1 = ra2, dec2
                    vertices.append((x_end, y_end))
                    self.mirroring_graphics.polyline(vertices)

    def calc_boundary_divisions(self, level, divs, wh_min, max_angle2, x1, y1, z1, x2, y2, z2, ra1, dec1, ra2, dec2):
        if abs(x2-x1) < wh_min and abs(y2-y1) < wh_min:
            # self.mirroring_graphics.text_centred((x1+x2)/2, (y1+y2)/2, '{:.1f}'.format(max(abs(x2-x1), abs(y2-y1))))
            return divs

        if abs(ra2-ra1) > np.pi:
            ra_center = np.pi + (ra1 + ra2) / 2
        else:
            ra_center = (ra1 + ra2) / 2
        dec_center = (dec1 + dec2) /2

        x_center, y_center = self.projection.radec_to_xy(ra_center, dec_center)

        if level == 1:
            c1 = self.graphics.cohen_sutherland_encode(x1, y1)
            c2 = self.graphics.cohen_sutherland_encode(x_center, y_center)
            c3 = self.graphics.cohen_sutherland_encode(x2, y2)
            if (c1 | c2) != 0 and (c1 & c2) != 0 and (c2 | c3) != 0 and (c2 & c3) != 0:
                return 0
            nzopt = not self.projection.is_zoptim()
            if nzopt and z1 < 0 and z2 < 0 and self.fieldradius > np.pi/4:
                c1 = self.graphics.cohen_sutherland_encode(x1, y1)
                c2 = self.graphics.cohen_sutherland_encode(x2, y2)
                c = c1 | c2
                if (c & 0b1100 == 0b1100) or (c & 0b0011 == 0b0011):
                    return 0

        vx1 = x_center - x1
        vy1 = y_center - y1
        vx2 = x2 - x_center
        vy2 = y2 - y_center

        vec_mul2 = (vx1 * vy2 - vy1 * vx2) / (math.sqrt(vx1**2 + vy1**2) * math.sqrt(vx2**2 + vy2**2))

        if abs(vec_mul2) < max_angle2:
            return divs

        return self.calc_boundary_divisions(level+1, divs * 2, wh_min, max_angle2, x1, y1, 1, x_center, y_center, 1, ra1, dec1, ra_center, dec_center)

    def create_widgets(self):
        left, bottom, right, top = self.get_field_rect_mm()
        self.space_widget_allocator = SpaceWidgetAllocator(left, bottom, right, top)

        self.w_mag_scale = WidgetMagnitudeScale(sky_map_engine=self,
                                                alloc_space_spec='bottom,left',
                                                legend_fontsize=self.get_legend_font_size(),
                                                stars_in_scale=STARS_IN_SCALE,
                                                lm_stars=self.lm_stars,
                                                legend_linewidth=self.config.legend_linewidth,
                                                vertical=False,
                                                color=self.config.draw_color
                                                )

        self.w_map_scale = WidgetMapScale(sky_map_engine=self,
                                          alloc_space_spec='bottom,right',
                                          drawingscale=self.drawing_scale,
                                          maxlength=self.drawingwidth/3.0,
                                          legend_fontsize=self.get_legend_font_size(),
                                          legend_linewidth=self.config.legend_linewidth,
                                          color=self.config.draw_color)

        self.w_orientation = WidgetOrientation(legend_fontsize=self.get_legend_font_size(),
                                               mirror_x=self.mirror_x,
                                               mirror_y=self.mirror_y,
                                               color=self.config.draw_color)

        self.w_coords = WidgetCoords(self.language, color=self.config.draw_color)
        self.w_dso_legend = WidgetDsoLegend(self.language, self.drawingwidth, LEGEND_MARGIN, color=self.config.draw_color)
        self.w_telrad = WidgetTelrad(self.drawing_scale, self.config.telrad_linewidth, self.config.telrad_color)
        self.w_eyepiece = WidgetEyepiece(self.drawing_scale, self.config.eyepiece_fov, self.config.eyepiece_linewidth, self.config.eyepiece_color)
        self.w_picker = WidgetPicker(self.config.picker_radius, self.config.picker_linewidth, self.config.picker_color)

        if self.config.show_mag_scale_legend:
            self.w_mag_scale.allocate_space(self.space_widget_allocator)
        if self.config.show_map_scale_legend:
            self.w_map_scale.allocate_space(self.space_widget_allocator)

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
        self.graphics.circle(x, y, r, DrawMode.FILL)

    def open_cluster(self, x, y, radius, label, label_mag, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        self.mirroring_graphics.circle(x, y, r)
        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, self.graphics.gi_default_font_size, self.config.dso_label_font_style)

        self.draw_circular_object_label(x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)
        if not label_ext and label_mag:
            self.graphics.set_font(self.graphics.gi_font, label_fh*0.8, self.config.dso_label_font_style)
            self.draw_circular_object_label(x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def galaxy_cluster(self, x, y, radius, label, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0

        self.graphics.set_pen_rgb(self.config.galaxy_cluster_color)
        self.graphics.set_linewidth(self.config.galaxy_cluster_linewidth)
        self.graphics.set_dashed_line(0.5, 2.0)

        self.mirroring_graphics.circle(x, y, r)
        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = None
            self.graphics.set_font(self.graphics.gi_font, self.graphics.gi_default_font_size, self.config.dso_label_font_style)

        self.draw_circular_object_label(x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

    def draw_asterism_label(self, x, y, label, labelpos, d, fh):
        if labelpos == 0 or labelpos == -1:
            self.mirroring_graphics.text_centred(x, y-d-2*fh/3.0, label)
        elif labelpos == 1:
            self.mirroring_graphics.text_centred(x, y+d+fh/3.0, label)
        elif labelpos == 2:
            self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
        elif labelpos == 3:
            self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)

    def asterism(self, x, y, radius, label, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0
        w2 = 2**0.5
        d = r/2.0*w2

        self.graphics.set_pen_rgb(self.config.star_cluster_color)
        self.graphics.set_linewidth(self.config.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6, 0.4)

        diff = self.graphics.gi_linewidth/2.0/w2

        self.mirroring_graphics.line(x-diff, y+d+diff, x+d+diff, y-diff)
        self.mirroring_graphics.line(x+d, y, x, y-d)
        self.mirroring_graphics.line(x+diff, y-d-diff, x-d-diff, y+diff)
        self.mirroring_graphics.line(x-d, y, x, y+d)

        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, self.graphics.gi_default_font_size, self.config.dso_label_font_style)

        if label:
            self.graphics.set_pen_rgb(self.config.label_color)
            self.draw_asterism_label(x, y, label, labelpos, d, label_fh)

        if label_ext:
            self.graphics.set_pen_rgb(self.config.label_color)
            self.draw_asterism_label(x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)

    def asterism_labelpos(self, x, y, radius=-1, label_length=0.0):
        """
        x,y,radius, label_length in mm
        returns [[start, centre, end],()]
        """
        r = radius if radius > 0 else self.drawingwidth/40.0
        w2 = 2**0.5
        d = r/2.0*w2
        fh = self.graphics.gi_default_font_size
        label_pos_list = []
        yy = y-d-2*fh/3.0
        label_pos_list.append([[x-label_length/2.0, yy], [x, yy], [x+label_length, yy]])
        yy = y+d+2*fh/3.0
        label_pos_list.append([[x-label_length/2.0, yy], [x, yy], [x+label_length, yy]])
        xx = x-d-fh/6.0
        yy = y
        label_pos_list.append([[xx-label_length, yy], [xx-label_length/2.0, yy], [xx, yy]])
        xx = x+d+fh/6.0
        yy = y
        label_pos_list.append([[xx, yy], [xx+label_length/2.0, yy], [xx+label_length, yy]])
        return label_pos_list

    def draw_galaxy_label(self, x, y, label, labelpos, rlong, rshort, fh):
        if labelpos == 0 or labelpos == -1:
            self.graphics.text_centred(0, -rshort-0.5*fh, label)
        elif labelpos == 1:
            self.graphics.text_centred(0, +rshort+0.5*fh, label)
        elif labelpos == 2:
            self.graphics.text_right(rlong+fh/6.0, -fh/3.0, label)
        elif labelpos == 3:
            self.graphics.text_left(-rlong-fh/6.0, -fh/3.0, label)

    def galaxy(self, x, y, rlong, rshort, posangle, mag, label, label_mag, label_ext, labelpos):
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
        if (rlong > 0.0) and (rshort < 0.0):
            rl = rlong
            rs = rlong/2.0

        self.graphics.save()

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_solid_line()
        if self.config.dso_dynamic_brightness and (mag is not None) and self.lm_deepsky >= 10.0 and label_ext is None:
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

        self.mirroring_graphics.ellipse(x, y, rl, rs, p)

        if label or label_ext:
            self.mirroring_graphics.translate(x, y)
            self.mirroring_graphics.rotate(p)
            self.graphics.set_pen_rgb((self.config.label_color[0]*dso_intensity,
                                       self.config.label_color[1]*dso_intensity,
                                       self.config.label_color[2]*dso_intensity))
            if label_ext:
                label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            else:
                label_fh = self.graphics.gi_default_font_size

            self.graphics.set_font(self.graphics.gi_font, label_fh, self.config.dso_label_font_style)

            if label:
                self.draw_galaxy_label(x, y, label, labelpos, rlong, rshort, label_fh)
            if label_ext:
                self.draw_galaxy_label(x, y, label_ext, self.to_ext_labelpos(labelpos), rlong, rshort, label_fh)
            if not label_ext and label_mag:
                self.mirroring_graphics.translate(0, -label_fh*0.9)
                self.graphics.set_font(self.graphics.gi_font, label_fh*0.8, self.config.dso_label_font_style)
                self.draw_galaxy_label(x, y, label_mag, labelpos, rlong, rshort, label_fh)

        self.graphics.restore()

    def galaxy_labelpos(self, x, y, rlong=-1, rshort=-1, posangle=0.0, label_length=0.0):
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if (rlong > 0.0) and (rshort < 0.0):
            rl = rlong
            rs = rlong/2.0

        p = posangle
        if posangle >= 0.5*np.pi:
            p += np.pi
        if posangle < -0.5*np.pi:
            p -= np.pi

        fh = self.graphics.gi_default_font_size
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

    def draw_circular_object_label(self, x, y, r, label, labelpos=-1, fh=None, set_pen=True):
        if fh is None:
            fh = self.graphics.gi_default_font_size
        if label:
            if set_pen:
                self.graphics.set_pen_rgb(self.config.label_color)
            arg = 1.0-2*fh/(3.0*r)
            if (arg < 1.0) and (arg > -1.0):
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
        fh = self.graphics.gi_default_font_size
        r = radius if radius > 0 else self.drawingwidth/40.0

        arg = 1.0-2*fh/(3.0*r)

        if (arg < 1.0) and (arg > -1.0):
            a = math.acos(arg)
        else:
            a = 0.5*np.pi

        label_pos_list = []
        xs = x+math.sin(a)*r+fh/6.0
        ys = y-r+fh/3.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])
        xs = x-math.sin(a)*r-fh/6.0 - label_length
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x+math.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x+math.sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])
        return label_pos_list

    def globular_cluster(self, x, y, radius, label, label_mag, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.star_cluster_color)

        self.mirroring_graphics.circle(x, y, r)
        self.mirroring_graphics.line(x-r, y, x+r, y)
        self.mirroring_graphics.line(x, y-r, x, y+r)

        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh, self.config.dso_label_font_style)

        self.draw_circular_object_label(x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

        if not label_ext and label_mag:
            self.graphics.set_font(self.graphics.gi_font, label_fh*0.8, self.config.dso_label_font_style)
            self.draw_circular_object_label(x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def diffuse_nebula(self, x, y, width, height, posangle, label, label_mag, label_ext, labelpos):
        self.graphics.set_linewidth(self.config.nebula_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.nebula_color)

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        d1 = d+self.graphics.gi_linewidth/2.0

        self.mirroring_graphics.line(x-d1, y+d, x+d1, y+d)
        self.mirroring_graphics.line(x+d, y+d, x+d, y-d)
        self.mirroring_graphics.line(x+d1, y-d, x-d1, y-d)
        self.mirroring_graphics.line(x-d, y-d, x-d, y+d)

        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, self.graphics.gi_default_font_size, self.config.dso_label_font_style)

        self.graphics.set_pen_rgb(self.config.label_color)
        if label:
            self.draw_diffuse_nebula_label(x, y, label, labelpos, d, label_fh)
        if label_ext:
            self.draw_diffuse_nebula_label(x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)
        if not label_ext and label_mag:
            self.graphics.set_font(self.graphics.gi_font, label_fh*0.8, self.config.dso_label_font_style)
            self.draw_diffuse_nebula_label(x, y-0.9*label_fh, label_mag, labelpos, d, label_fh)

    def draw_diffuse_nebula_label(self, x, y, label, labelpos, d, fh):
        if labelpos == 0 or labelpos == -1:
            self.mirroring_graphics.text_centred(x, y-d-fh/2.0, label)
        elif labelpos == 1:
            self.mirroring_graphics.text_centred(x, y+d+fh/2.0, label)
        elif labelpos == 2:
            self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
        elif labelpos == 3:
            self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)

    def diffuse_nebula_outlines(self, x, y, x_outl, y_outl, outl_lev, width, height, posangle, label, label_ext,
                                draw_label, labelpos=''):
        self.graphics.set_linewidth(self.config.nebula_linewidth)
        self.graphics.set_solid_line()

        if self.config.light_mode:
            frac = 4 - 1.5 * outl_lev  # no logic, look nice in light mode
            pen_r = 1.0 - ((1.0 - self.config.nebula_color[0]) / frac)
            pen_g = 1.0 - ((1.0 - self.config.nebula_color[1]) / frac)
            pen_b = 1.0 - ((1.0 - self.config.nebula_color[2]) / frac)
        else:
            frac = 4 - 1.5 * outl_lev  # no logic, look nice in dark mode
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

        if draw_label:
            if label_ext:
                label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            else:
                label_fh = self.graphics.gi_default_font_size * self.config.outlined_dso_label_font_scale
            self.graphics.set_font(self.graphics.gi_font, label_fh)
            self.graphics.set_pen_rgb(self.config.label_color)
            if label:
                self.draw_diffuse_nebula_label(x, y, label, labelpos, d, label_fh)
            if label_ext:
                self.draw_diffuse_nebula_label(x, y, label_ext, self.to_ext_labelpos(labelpos), d, label_fh)

    def unknown_diffuse_nebula_outlines(self, x_outl, y_outl, outl_lev):
        self.graphics.set_linewidth(self.config.nebula_linewidth)
        self.graphics.set_solid_line()

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

    def diffuse_nebula_labelpos(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label_length=0.0):
        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        fh = self.graphics.gi_default_font_size

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y-d-fh/2.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        ys = y+d+fh/2.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])
        return label_pos_list

    def planetary_nebula(self, x, y, radius, label, label_mag, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x, y, 0.75*r)
        self.mirroring_graphics.line(x-0.75*r, y, x-1.5*r, y)
        self.mirroring_graphics.line(x+0.75*r, y, x+1.5*r, y)
        self.mirroring_graphics.line(x, y+0.75*r, x, y+1.5*r)
        self.mirroring_graphics.line(x, y-0.75*r, x, y-1.5*r)

        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh, self.config.dso_label_font_style)

        self.draw_circular_object_label(x, y, r, label, labelpos, label_fh)

        if label_ext:
            self.draw_circular_object_label(x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)
        if not label_ext and label_mag:
            self.graphics.set_font(self.graphics.gi_font, label_fh*0.8, self.config.dso_label_font_style)
            self.draw_circular_object_label(x, y-0.9*label_fh, r, label_mag, labelpos, label_fh)

    def supernova_remnant(self, x, y, radius, label, label_ext, labelpos):
        r = radius if radius > 0 else self.drawingwidth/40.0

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.nebula_color)

        self.mirroring_graphics.circle(x, y, r-self.graphics.gi_linewidth/2.0)

        if label_ext:
            label_fh = self.config.ext_label_font_scale * self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, label_fh)
        else:
            label_fh = self.graphics.gi_default_font_size
            self.graphics.set_font(self.graphics.gi_font, self.graphics.gi_default_font_size, self.config.dso_label_font_style)

        self.draw_circular_object_label(x, y, r, label, labelpos, label_fh)
        if label_ext:
            self.draw_circular_object_label(x, y, r, label_ext, self.to_ext_labelpos(labelpos), label_fh)

    def unknown_object(self, x, y, radius, label, label_ext, labelpos):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        r /= 2**0.5

        self.graphics.set_linewidth(self.config.dso_linewidth)
        self.graphics.set_solid_line()
        self.graphics.set_pen_rgb(self.config.dso_color)

        self.mirroring_graphics.line(x-r, y+r, x+r, y-r)
        self.mirroring_graphics.line(x+r, y+r, x-r, y-r)

        fh = self.graphics.gi_default_font_size

        if label != '':
            self.graphics.set_pen_rgb(self.config.label_color)
            if labelpos == 0:
                self.mirroring_graphics.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos ==1:
                self.mirroring_graphics.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_centred(x, y + r + fh/2.0, label)
            else:
                self.mirroring_graphics.text_centred(x, y - r - fh/2.0, label)

    def unknown_object_labelpos(self, x, y, radius=-1, label_length=0.0):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        fh = self.graphics.gi_default_font_size
        r /= 2**0.5
        label_pos_list = []
        xs = x + r + fh/6.0
        ys = y
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x - r - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x - label_length/2.0
        ys = y + r + fh/2.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])

        xs = x - label_length/2.0
        ys = y - r - fh/2.0
        label_pos_list.append([[xs, ys], [xs+label_length/2.0, ys], [xs+label_length, ys]])
        return label_pos_list

    def align_rect_coords(self, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return x1, y1, x2, y2

