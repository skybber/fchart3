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

from .label_potential import *
from .constellation import *
from .configuration import *

from .graphics import *
from .projections import *
from .precession import compute_precession_matrix
from .viewport_transformer import ViewportTransformer

from .space_widget_allocator import SpaceWidgetAllocator

from .renderers import *
from .widgets import *

from .utils.types import RenderContext, RenderState

uilanguage = os.environ.get('fchart3lang')
try:
    if uilanguage:
        lang = gettext.translation('messages', localedir='locale', languages=[uilanguage])
        lang.install()
        _ = lang.gettext
    else:
        _ = gettext.gettext
except (FileNotFoundError, OSError) as e:
    _ = gettext.gettext


LABELi18N = {
    'h': _('h'),
    'm': _('m'),
    's': _('s'),
    'G': _('Galaxy'),
    'OCL': _('Open cluster'),
    'GCL': _('Globular cluster'),
    'AST': _('Asterism'),
    'PN': _('Planetary nebula'),
    'N': _('Diffuse nebula'),
    'SNR': _('Supernova remnant'),
    'PG': _('Part of galaxy')
}


STARS_IN_SCALE = 10
LEGEND_MARGIN = 0.47
BASE_SCALE = 0.98


class SkymapEngine:
    def __init__(self, graphics, language=LABELi18N, lm_stars=13.8, lm_deepsky=12.5, caption=''):
        self.create_renderers()
        self.gfx = graphics
        self.cfg = EngineConfiguration()
        self.transf = None

        self.caption = caption
        self.language = language
        self.drawing_width = self.gfx.gi_width
        self.drawing_height = self.gfx.gi_height
        self.min_radius = 1.0  # of deepsky symbols (mm)

        self.lm_stars = lm_stars
        self.lm_deepsky = lm_deepsky
        self.star_mag_r_shift = 0

        self.is_equatorial = False
        self.center_celestial = None
        self.center_equatorial = None
        self.field_radius = None
        self.field_size = None
        self.field_label = None
        self.scene_scale = None
        self.drawing_scale = None
        self.legend_fontscale = None
        self.mirror_x = False
        self.mirror_y = False

        self.space_widget_allocator = None
        self.widgets = None

        self.norm_field_radius = None

    def set_field(self, phi, theta, field_radius, field_label=None, mirror_x=False, mirror_y=False, projection_type=ProjectionType.STEREOGRAPHIC):
        self.field_radius = field_radius
        self.center_celestial = (phi, theta)
        self.center_equatorial = (phi, theta)
        self.field_label = field_label if field_label is not None else 'FoV:' + str(field_radius)

        wh = max(self.drawing_width, self.drawing_height)

        self.field_size = field_radius * math.hypot(self.drawing_width, self.drawing_height) / wh

        if self.cfg.no_margin:
            self.scene_scale = (wh - self.cfg.legend_linewidth) / wh
        else:
            self.scene_scale = BASE_SCALE

        self.drawing_scale = self.scene_scale*wh/2.0/math.sin(field_radius)
        self.legend_fontscale = min(self.cfg.legend_font_scale, wh/100.0)
        self.set_caption(self.caption)

        if projection_type == ProjectionType.ORTHOGRAPHIC:
            proj = ProjectionOrthographic()
        else:
            proj = ProjectionStereographic()

        self.transf = ViewportTransformer(proj)
        self.transf.set_celestial_center(0, 0)
        self.transf.set_scale(1.0, 1.0)
        self.norm_field_radius, _ = self.transf.equatorial_to_xy(field_radius, 0)
        self.drawing_scale = self.scene_scale*wh / 2.0 / abs(self.norm_field_radius)
        self.transf.set_celestial_center(self.center_celestial[0], self.center_celestial[1])
        mulx = -1 if mirror_x else 1
        muly = -1 if mirror_y else 1
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y
        self.transf.set_scale(self.drawing_scale*mulx, self.drawing_scale*muly)

    def set_observer(self, lst, lat, is_equatorial):
        self.is_equatorial = is_equatorial
        if not is_equatorial:
            self.transf.set_observer(lst, lat)
            c_ra, c_dec = self.transf.get_equatorial_center()
            self.center_equatorial = (c_ra, c_dec)
        self.transf.set_grid_observer(lst, lat)

    def set_configuration(self, config):
        self.cfg = config

    def get_field_radius_mm(self):
        return self.drawing_scale * self.norm_field_radius

    def get_field_rect_mm(self):
        x = self.scene_scale * self.drawing_width / 2.0
        y = self.scene_scale * self.drawing_height / 2.0
        return -x, -y, x, y

    def set_language(self, language):
        self.language = language

    def set_caption(self, caption):
        self.caption = caption

    def make_map(self, used_catalogs, jd=None, solsys_bodies=None, planet_moons=None, showing_dsos=None, dso_highlights=None, highlights=None,
                 dso_hide_filter=None, extra_positions=None, hl_constellation=None, trajectory=None, visible_objects=None, transparent=False):

        self.create_widgets()

        self.gfx.set_background_rgb(self.cfg.background_color)

        self.gfx.new()

        if not transparent:
            self.gfx.clear()

        self.gfx.set_pen_rgb(self.cfg.draw_color)
        self.gfx.set_fill_rgb(self.cfg.draw_color)
        self.gfx.set_font(font=self.cfg.font, font_size=self.cfg.font_size)
        self.gfx.set_default_font_size(self.cfg.font_size)
        self.gfx.set_linewidth(self.cfg.legend_linewidth)

        if self.cfg.widget_mode != WidgetMode.WIDGET_ONLY:
            clip_path = self.space_widget_allocator.get_border_path()
            if self.cfg.widget_mode == WidgetMode.ALLOC_SPACE_ONLY:
                x1, y1, x2, y2 = self.get_field_rect_mm()
                self.gfx.clip_path([(x2,y2), (x2, y1), (x1, y1), (x1, y2)])
            else:
                self.gfx.clip_path(clip_path)

            precession_matrix = np.linalg.inv(compute_precession_matrix(jd)) if jd is not None else None

            mirroring_gfx = self.gfx
            if self.mirror_x or self.mirror_y:
                mirroring_gfx = MirroringGraphics(self.gfx, self.mirror_x, self.mirror_y)

            self.star_mag_r_shift = 0
            if self.cfg.star_mag_shift > 0:
                self.star_mag_r_shift = self.magnitude_to_radius(self.lm_stars - self.cfg.star_mag_shift) - self.magnitude_to_radius(self.lm_stars)

            ctx = RenderContext(
                gfx=self.gfx,
                mirroring_gfx=mirroring_gfx,
                cfg=self.cfg,
                transf=self.transf,
                drawing_width=self.drawing_width,
                drawing_height=self.drawing_height,
                min_radius=self.min_radius,
                scene_scale=self.scene_scale,
                drawing_scale=self.drawing_scale,
                field_rect_mm=self.get_field_rect_mm(),
                clip_path=clip_path,
                is_equatorial=self.is_equatorial,
                center_equatorial=self.center_equatorial,
                center_celestial=self.center_celestial,
                field_radius=self.field_radius,
                field_size=self.field_size,
                mirror_x=self.mirror_x,
                mirror_y=self.mirror_y,
                lm_stars=self.lm_stars,
                lm_deepsky=self.lm_deepsky,
                star_mag_r_shift=self.star_mag_r_shift,
                used_catalogs=used_catalogs,
                jd=jd,
                precession_matrix=precession_matrix,
                showing_dsos=showing_dsos,
                dso_hide_filter=dso_hide_filter,
                dso_highlights=dso_highlights,
                highlights=highlights,
                hl_constellation=hl_constellation,
                extra_positions=extra_positions,
                solsys_bodies=solsys_bodies,
                planet_moons=planet_moons,
                trajectory=trajectory,
            )

            visible_objects_collector = [] if visible_objects is not None else None

            state = RenderState(
                label_potential=LabelPotential(self.get_field_radius_mm()),
                visible_objects_collector=visible_objects_collector,
                picked_dso=None,
                picked_star=None,
                picked_planet_moon=None,
            )

            self.renderers["milkyway"].draw(ctx, state)
            self.renderers["grid"].draw(ctx, state)
            self.renderers["highlights"].draw(ctx, state)
            self.renderers["constellations"].draw(ctx, state)
            self.renderers["nebulae_outlines"].draw(ctx, state)
            self.renderers["stars"].draw(ctx, state)
            self.renderers["deepsky"].draw(ctx, state)
            self.renderers["planets"].draw(ctx, state)

            self.renderers["extras"].draw(ctx, state)

            if state.picked_dso is None and state.picked_planet_moon is None and state.picked_star is not None:
                self.renderers["stars"].draw_picked_star(ctx, state)

            self.renderers["trajectory"].draw(ctx, state)
            self.renderers["arrow"].draw(ctx, state)
            if not self.is_equatorial:
                self.renderers["horizon"].draw(ctx, state)


            self.gfx.reset_clip()

            if visible_objects is not None and state.visible_objects_collector is not None:
                state.visible_objects_collector.sort(key=lambda x: x[0])
                for obj in state.visible_objects_collector:
                    visible_objects.extend([obj[1], obj[2], obj[3], obj[4], obj[5]])

        self.draw_caption()
        self.draw_widgets()
        self.draw_field_border()
        self.gfx.finish()

    def magnitude_to_radius(self, magnitude):
        return interp_magnitude_to_radius(self.lm_stars, self.star_mag_r_shift, magnitude)

    def draw_caption(self):
        if self.caption != '':
            font_size = self.get_legend_font_size()
            self.gfx.set_font(self.gfx.gi_font, 2.0*font_size)
            self.gfx.text_centred(0, self.drawing_width/2.0*BASE_SCALE + font_size, self.caption)

    def draw_field_border(self):
        if self.cfg.show_field_border:
            self.gfx.set_linewidth(self.cfg.legend_linewidth)
            x1, y1, x2, y2 = self.get_field_rect_mm()
            self.gfx.line(x1, y1, x1, y2)
            self.gfx.line(x1, y2, x2, y2)
            self.gfx.line(x2, y2, x2, y1)
            self.gfx.line(x2, y1, x1, y1)

    def get_legend_font_size(self):
        return self.cfg.font_size * self.legend_fontscale

    def draw_widgets(self):
        if self.cfg.widget_mode == WidgetMode.ALLOC_SPACE_ONLY:
            return
        font_size = self.get_legend_font_size()
        self.gfx.set_font(self.gfx.gi_font, font_size=font_size)

        x1, y1, x2, y2 = self.get_field_rect_mm()

        fill_background = self.cfg.widget_mode in [WidgetMode.WIDGET_ONLY, WidgetMode.NORMAL]

        if self.cfg.fov_telrad:
            self.widgets["telrad"].draw(self.gfx)
        if self.cfg.eyepiece_fov is not None:
            self.widgets["eyepiece"].draw(self.gfx)
        if self.cfg.show_picker and self.cfg.picker_radius > 0:
            self.widgets["picker"].draw(self.gfx)
        if self.cfg.show_mag_scale_legend:
            self.widgets["mag_scale"].draw(self.gfx, fill_background)
        if self.cfg.show_map_scale_legend:
            self.widgets["map_scale"].draw(self.gfx, fill_background)
        if self.cfg.show_numeric_map_scale_legend:
            self.widgets["numeric_map_scale"].draw(self.gfx, fill_background, self.field_label)
        if self.cfg.show_orientation_legend:
            self.widgets["orientation"].draw(self.gfx, x1, y2, fill_background)
        if self.cfg.show_coords_legend:
            self.widgets["coords"].draw(self.gfx, left=x2-font_size/2, bottom=y2-font_size, ra=self.center_equatorial[0], dec=self.center_equatorial[1], fill_background=fill_background)
        if self.cfg.show_dso_legend:
            self.widgets["dso_legend"].draw_dso_legend(self, self.gfx, fill_background)

    def create_renderers(self):
        self.renderers = {}
        self.renderers["arrow"] = ArrowRenderer()
        self.renderers["constellations"] = ConstellationsRenderer()
        self.renderers["deepsky"] = DeepskyRenderer()
        self.renderers["grid"] = GridRenderer()
        self.renderers["extras"] = ExtrasRenderer()
        self.renderers["highlights"] = HighlightsRenderer()
        self.renderers["horizon"] = HorizonRenderer()
        self.renderers["milkyway"] = MilkyWayRenderer()
        self.renderers["nebulae_outlines"] = NebulaeOutlinesRenderer()
        self.renderers["stars"] = StarsRenderer()
        self.renderers["planets"] = PlanetsRenderer()
        self.renderers["trajectory"] = TrajectoryRenderer()

    def create_widgets(self):
        left, bottom, right, top = self.get_field_rect_mm()
        self.space_widget_allocator = SpaceWidgetAllocator(left, bottom, right, top)

        self.widgets = {}

        self.widgets["mag_scale"] = WidgetMagnitudeScale(sky_map_engine=self,
                                                         alloc_space_spec='bottom,left',
                                                         legend_fontsize=self.get_legend_font_size(),
                                                         stars_in_scale=STARS_IN_SCALE,
                                                         lm_stars=self.lm_stars,
                                                         legend_linewidth=self.cfg.legend_linewidth,
                                                         vertical=False,
                                                         color=self.cfg.draw_color
                                                         )

        self.widgets["map_scale"] = WidgetMapScale(sky_map_engine=self,
                                                   alloc_space_spec='bottom,right',
                                                   drawingscale=self.drawing_scale,
                                                   maxlength=self.drawing_width / 3.0,
                                                   legend_fontsize=self.get_legend_font_size(),
                                                   legend_linewidth=self.cfg.legend_linewidth,
                                                   color=self.cfg.draw_color)

        self.widgets["numeric_map_scale"] = WidgetNumericMapScale(sky_map_engine=self,
                                                                  alloc_space_spec='bottom,left',
                                                                  legend_fontsize=self.get_legend_font_size(),
                                                                  legend_linewidth=self.cfg.legend_linewidth,
                                                                  color=self.cfg.draw_color)

        self.widgets["orientation"] = WidgetOrientation(legend_fontsize=self.get_legend_font_size(),
                                                        mirror_x=self.mirror_x,
                                                        mirror_y=self.mirror_y,
                                                        color=self.cfg.draw_color)

        self.widgets["coords"] = WidgetCoords(self.language, color=self.cfg.draw_color)
        self.widgets["dso_legend"] = WidgetDsoLegend(self.language, self.drawing_width, LEGEND_MARGIN, color=self.cfg.draw_color)
        self.widgets["telrad"] = WidgetTelrad(self.drawing_scale, self.cfg.telrad_linewidth, self.cfg.telrad_color)
        self.widgets["eyepiece"] = WidgetEyepiece(self.drawing_scale, self.cfg.eyepiece_fov, self.cfg.eyepiece_linewidth, self.cfg.eyepiece_color)
        self.widgets["picker"] = WidgetPicker(self.cfg.picker_radius, self.cfg.picker_linewidth, self.cfg.picker_color)

        if self.cfg.show_mag_scale_legend:
            self.widgets["mag_scale"].allocate_space(self.space_widget_allocator)
        if self.cfg.show_map_scale_legend:
            self.widgets["map_scale"].allocate_space(self.space_widget_allocator)
        if self.cfg.show_numeric_map_scale_legend:
            self.widgets["numeric_map_scale"].allocate_space(self.space_widget_allocator)
