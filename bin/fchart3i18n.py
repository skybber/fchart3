#!/usr/bin/python

#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2020 fchart authors
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

import argparse
import textwrap

from time import time

import os
import sys
import numpy as np

import fchart3

from fchart3.config_loader import ConfigurationLoader
from fchart3.astrocalc import hms2rad, dms2rad, rad2hms, rad2dms
from fchart3.skymap_engine import SkymapEngine, EN, NL, ES,FR
from fchart3.used_catalogs import UsedCatalogs
from fchart3.configuration import EngineConfiguration
from fchart3.graphics_cairo import CairoDrawing
from fchart3.graphics_tikz import TikZDrawing
from fchart3.graphics_interface import FontStyle

import gettext
_ = gettext.gettext

#################################################################


def print_version(version):
    print(-(f"""fchart3 version {version} (c) fchart3 authors 2005-2023\n
fchart3 comes with ABSOLUTELY NO WARRANTY. It is distributed under the
GNU General Public License (GPL) version 2. For details see the LICENSE
file distributed with the software. This is free software, and you are
welcome to redistribute it under certain conditions as specified in the
LICENSE file."""))


class RuntimeSettings:
    def __init__(self):
        self.extra_positions_list = []
        self.fieldcentre = (-1, -1)
        self.parse_commandline()

    def parse_commandline(self):
        argumentparser = argparse.ArgumentParser(description='fchart',
              formatter_class=argparse.RawTextHelpFormatter,
              epilog=textwrap.dedent('''\
                    Sourcenames:
                       Valid sourcenames are for example:
                       - NGC891, NgC891, n891 or 891 for NGC objects
                       - IC1396, i1396, iC1396, I1396 for IC objects
                       - m110, M3 for Messier objects
                       - \"9:35:00.8,-34:15:33,SomeCaption\" for other positions

                       There is one special sourcename, which is \"allmessier\". When this name
                       is encountered, fchart dumps maps of all messier objects to the output
                       directory.
                    ''')
              )

        argumentparser.add_argument('-o', '--output-dir', dest='output_dir', nargs='?', action='store', default='./',
                                    help='Specify the output directory (default: current directory)')

        argumentparser.add_argument('-f', '--output-file', dest='output_file', nargs='?', action='store',
                                    help='Specify the output file name. (default: name of DSO object). ' +\
                                         'The image format is defined by the file extension. ' +\
                                         'Supported formats/extensions are pdf, png, and svg.')

        argumentparser.add_argument('-config', '--config-file', dest='config_file', nargs='?', action='store',
                                    help='Specify name of the configuration file ndistributed with fchart3 or path to custom config file. (default=default)')

        argumentparser.add_argument('--extra-data-dir', dest='extra_data_dir', nargs='?', action='store',
                                    help='Path to extra data directory containing Stellarium star catalogues.')

        argumentparser.add_argument('-limdso', dest='limit_magnitude_deepsky', nargs='?', action='store', default=12.0, type=float,
                                    help='Limiting magnitude for deep sky objects (default: 12.0)')
        argumentparser.add_argument('-limstar', dest='limit_magnitude_stars', nargs='?', action='store', default=12.0, type=float,
                                    help='Limiting magnitude for stars. (Default: 12.0)')
        argumentparser.add_argument('-width', dest='width', nargs='?', action='store', default=180.0, type=float,
                            help='Width of the drawing area in millimeters.')
        argumentparser.add_argument('-height', dest='height', nargs='?', action='store', default=270.0, type=float,
                                    help='Height of the drawing area in millimeters.')
        argumentparser.add_argument('-fieldsize', dest='fieldsize', nargs='?', action='store', default=7.0, type=float,
                                    help='Diameter of the field of view in degrees (default: 7.0)')

        argumentparser.add_argument('-fmessier', '--force-messier', dest='force_messier', action='store_true',
                                    help='Select all Messier objects, regardless of the limiting magnitude for deep sky objects.')
        argumentparser.add_argument('-fasterism', '--force-asterisms', dest='force_asterisms', action='store_true',
                                    help='Force plotting of asterisms on the map. By default, only "Messier" asterisms are plotted,' + \
                                         ' while all others are ignored. The default setting helps clean up maps, especially in the Virgo cluster region.')
        argumentparser.add_argument('-funknown', '--force-unknown', dest='force_unknown', action='store_true',
                                    help='By default, objects in external galaxies are plotted only if their magnitude is known and is lower than ' + \
                                         'the limiting magnitude for deep sky objects. If this option is given, objects in external galaxies ' + \
                                         'of which the magnitude is unknown will also be plotted. This option may clutter some galaxies like M 101 ' + \
                                         'and NGC 4559.')

        argumentparser.add_argument('-lang', '--language', dest='language', nargs='?', action='store', default='en',
                                    help='Specify the language for the maps, options: \'en\', \'nl\', \'es\' (default: en)')

        argumentparser.add_argument('-sc', '--show-catalogs', dest='show_catalogs', nargs='?', action='store',
                                    help='Comma separated list of additional catalogs to be show on the map. (e.g. LBN).')

        argumentparser.add_argument('-x', '--add-cross', dest='cross_marks', nargs='?', action='append',
                                    help='Add a cross to the map at a specified position. The format of the argument for this option is: ' + \
                                         '\"rah:ram:ras,+/-decd:decm:decs,label,labelposition\". For example: -x\"20:35:25.4,+60:07:17.7,SN,t\" for ' + \
                                         'the supernova sn2004et in NGC 6946. The label position can be \'t\' for top, \'b\' for bottom, \'l\' for ' + \
                                         'left, or \'r\' for right. The label and label position may be omitted.')

        argumentparser.add_argument('-capt', '--caption', dest='caption', nargs='?', action='store', default='',
                                    help='Force a specific caption for the maps. All maps will have the same caption.')

        argumentparser.add_argument('--hide-star-labels', dest='show_star_labels', action='store_false', default=None,
                                    help='Hide star labels.')

        argumentparser.add_argument('--hide-flamsteed', dest='show_flamsteed', action='store_false', default=None,
                                    help='Hide Flamsteed designations.')

        argumentparser.add_argument('--hide-mag-scale-legend', dest='show_mag_scale_legend', action='store_false', default=None,
                                    help='Hide magnitude scale legend.')

        argumentparser.add_argument('--hide-map-scale-legend', dest='show_map_scale_legend', action='store_false', default=None,
                                    help='Hide map scale legend.')

        argumentparser.add_argument('--hide-map-orientation-legend', dest='show_orientation_legend', default=None,
                                    action='store_false',
                                    help='Hide orientation legend.')

        argumentparser.add_argument('--show-dso-legend', dest='show_dso_legend', action='store_true', default=None,
                                    help='Show deep-sky object legend.')

        argumentparser.add_argument('--show-coords-legend', dest='show_coords_legend', action='store_true', default=None,
                                    help='Show coordinates legend.')

        argumentparser.add_argument('--hide-field-border', dest='show_field_border', action='store_false', default=None,
                                    help='Hide the field border.')

        argumentparser.add_argument('--show-equatorial-grid', dest='show_equatorial_grid', action='store_true', default=None,
                                    help='Show equatorial grid.')

        argumentparser.add_argument('--hide-constellation-shapes', dest='show_constellation_shapes', action='store_false', default=None,
                                    help='Hide constellation shapes.')

        argumentparser.add_argument('--hide-constellation-borders', dest='show_constellation_borders', action='store_false', default=None,
                                    help='Hide constellation borders.')

        argumentparser.add_argument('--show-simple-milky-way', dest='show_simple_milky_way', action='store_true', default=None,
                                    help='Show a simplified representation of the Milky Way with outlines.')

        argumentparser.add_argument('--show-enhanced-milky-way', dest='show_enhanced_milky_way', action='store_true', default=None,
                                    help='Display a realistic representation of the Milky Way with shading and details.')

        argumentparser.add_argument('--hide-deepsky', dest='show_deepsky', action='store_false', default=None,
                                    help='Hide deep sky objects.')

        argumentparser.add_argument('--show-nebula-outlines', dest='show_nebula_outlines', action='store_true', default=None,
                                    help='Show nebula outlines.')

        argumentparser.add_argument('-telrad', '--FOV-telrad', dest='fov_telrad', action='store_true', default=None,
                                    help='Show telrad circles at the field of view.')

        argumentparser.add_argument('-mx', '--mirror-x', dest='mirror_x', action='store_true', default=None,
                                    help='Mirror in the x-axis.')
        argumentparser.add_argument('-my', '--mirror-y', dest='mirror_y', action='store_true', default=None,
                                    help='Mirror in the y-axis.')

        argumentparser.add_argument('--star-colors', dest='star_colors', action='store_true', default=None, help='Color stars according to spectral type.')
        argumentparser.add_argument('--color-background', dest='background_color', action='store', default=None, help='Background color. (default: white)')
        argumentparser.add_argument('--color-draw', dest='draw_color', action='store', default=None, help='Drawing color for stars. (default: black)')
        argumentparser.add_argument('--color-label', dest='label_color', action='store', default=None, help='Label color. (default: black)')
        argumentparser.add_argument('--color-constellation-lines', dest='constellation_lines_color', action='store', default=None, help='Constellation lines color.')
        argumentparser.add_argument('--color-constellation-border', dest='constellation_border_color', action='store', default=None, help='Constellation border color.')
        argumentparser.add_argument('--color-deepsky', dest='dso_color', action='store', default=None, help='Unclassified deep sky object color.')
        argumentparser.add_argument('--color-nebula', dest='nebula_color', action='store', default=None, help='Nebula color.')
        argumentparser.add_argument('--color-galaxy', dest='galaxy_color', action='store', default=None, help='Galaxy color.')
        argumentparser.add_argument('--color-star-cluster', dest='star_cluster_color', action='store', default=None, help='Star cluster color.')
        argumentparser.add_argument('--color-galaxy-cluster', dest='galaxy_cluster_color', action='store', default=None, help='Galaxy cluster color.')
        argumentparser.add_argument('--color-milky-way', dest='milky_way_color', action='store', default=None, help='Milky Way color.')
        argumentparser.add_argument('--color-grid', dest='grid_color', action='store', default=None, help='Grid color.')
        argumentparser.add_argument('--color-telrad', dest='telrad_color', action='store', default=None, help='telrad color.')

        argumentparser.add_argument('--linewidth-constellation', dest='constellation_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Constellation line width (default: 0.5)')
        argumentparser.add_argument('--linewidth-constellation-border', dest='constellation_border_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Constellation border line width (default: 0.5)')
        argumentparser.add_argument('--linewidth-nebula', dest='nebula_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of nebulae (default: 0.3)')
        argumentparser.add_argument('--linewidth-open-cluster', dest='open_cluster_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of open clusters (default: 0.3)')
        argumentparser.add_argument('--linewidth-galaxy-cluster', dest='galaxy_cluster_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of galaxy clusters (default: 0.2)')
        argumentparser.add_argument('--linewidth-deepsky', dest='dso_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of deep sky objects (default: 0.2)')
        argumentparser.add_argument('--linewidth-milky-way', dest='milky_way_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of the Milky Way (default: 0.2)')
        argumentparser.add_argument('--linewidth-legend', dest='legend_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of the legend (default: 0.2)')
        argumentparser.add_argument('--linewidth-grid', dest='grid_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Line width of the equatorial grid (default: 0.1)')
        argumentparser.add_argument('--linewidth-telrad', dest='telrad_linewidth', nargs='?', action='store', type=float, default=None,
                                    help='Telrad line width (default: 0.3)')

        argumentparser.add_argument('--constellation-line-space', dest='constellation_linespace', nargs='?', action='store', type=float, default=None,
                                    help='Space between star and constellation shape line. (Default: 1.5)')

        argumentparser.add_argument('--no-margin', dest='no_margin', action='store_true', default=False,
                                    help='Do not draw the chart margin line.')

        argumentparser.add_argument('--font', dest='font', action='store', default='Arial', help='Font (Arial)')

        argumentparser.add_argument('--font-size', dest='font_size', type=float, default=3.0, help='Font size')

        argumentparser.add_argument('--bayer-font-scale', dest='bayer_label_font_scale', nargs='?', action='store', type=float, default=None,
                                    help='Bayer designation font scale. (Default: 1.2)')
        argumentparser.add_argument('--font-style-bayer', dest='font_style_bayer', default=None, help='Bayer designation font style. [italic, bold]')
        argumentparser.add_argument('--flamsteed-font-scale', dest='flamsteed_label_font_scale', nargs='?', action='store', default=None, type=float,
                                    help='Flamsteed designation font scale. (Default: 0.9)')
        argumentparser.add_argument('--font-style-flamsteed', dest='font_style_flamsteed', default=None, help='Flamsteed designation font style. [italic, bold]')
        argumentparser.add_argument('--flamsteed-numbers-only', dest='flamsteed_numbers_only', action='store_true', default=None,
                                    help='Show Flamsteed designations without constellation prefix.')
        argumentparser.add_argument('--font-style-dso', dest='font_style_dso', default=None, help='DSO labels font style. [italic, bold]')

        argumentparser.add_argument('--legend_font_scale', dest='legend_font_scale', type=float, default=None,
                                    help='Scale of the font used in the legend relative to the chart font size.')

        argumentparser.add_argument('-v', '--version', action='store_true', default=None, help='Display version information and exit.')

        argumentparser.add_argument('sourcelist', nargs='*')

        self.parser = argumentparser.parse_args()

        if len(self.parser.sourcelist) == 0:
            argumentparser.print_help()
            sys.exit(1)

        if self.parser.language.upper() == 'NL':
            self.language = NL
        elif self.parser.language.upper() == 'EN':
            self.language = EN
        elif self.parser.language.upper() == 'ES':
            self.language = ES
        elif self.parser.language.upper() == 'FR':
            self.language = FR    
        else:
            print(_('Unsupported language {}'.format(self.parser.language)))
            sys.exit(-1)

        if self.parser.version:
            print_version("0.9.0")
            sys.exit(1)

        if self.parser.cross_marks:
            for mark in self.parser.cross_marks:
                data = mark.split(',')
                if len(data) >= 2:
                    ra_str, dec_str = data[0:2]
                    label_str = ''
                    label_pos = 'r'
                    ra_str = ra_str.lstrip().rstrip()
                    dec_str = dec_str.lstrip().rstrip()
                    if len(data) >= 3:
                        label_str = data[2].lstrip().rstrip()

                    if len(data) >= 4:
                        label_pos = data[3].rstrip().lstrip()

                    rasplit = ra_str.split(':')
                    decsplit = dec_str.split(':')

                    rah, ram, ras = 0.0, 0.0, 0.0
                    rah= float(rasplit[0])
                    if len(rasplit) >= 2:
                        ram = float(rasplit[1])
                    if len(rasplit) >= 3:
                        ras = float(rasplit[2])

                    decd, decm, decs, sign = 0.0, 0.0, 0.0, 1
                    decd= abs(float(decsplit[0]))
                    if decsplit[0][0] == '-':
                        sign = -1
                    if len(decsplit) >= 2:
                        decm = float(decsplit[1])
                    if len(decsplit) >= 3:
                        decs = float(decsplit[2])
                    rax, decx = hms2rad(rah, ram, ras), dms2rad(decd, decm, decs, sign)
                    self.extra_positions_list.append([rax,decx,label_str,label_pos])
                else:
                    print(_('option -x needs three part argument, separated by comma\'s: -x "ra,dec,label"'))
                    sys.exit(-1)


#############################################################
#                                                           #
#                      MAIN  PROGRAM                        #
#                                                           #
#############################################################

def _convert_color(color):
    if color.startswith('#'):
        color = color[1:]
    try:
        r, g, b = [int(color[i:i+2], 16) / 255.0 for i in range(0, len(color), 2)]
    except ValueError:
        print( _('Invalid color format {}'.format(color)))
        sys.exit()
    return r, g, b

def _convert_font_style(font_style):
    if font_style == 'italic':
        return FontStyle.ITALIC
    if font_style == 'bold':
        return FontStyle.BOLD
    return FontStyle.NORMAL

def _create_engine_configuration(config_file = None):
    config = EngineConfiguration()

    # 1. sets defaults
    config.light_mode = True
    config.legend_only = False
    config.show_star_labels = True
    config.show_flamsteed = True
    config.show_mag_scale_legend = False
    config.show_map_scale_legend = False
    config.show_orientation_legend = False
    config.show_dso_legend = False
    config.show_coords_legend = False
    config.show_field_border = False
    config.show_equatorial_grid = False
    config.show_constellation_shapes = True
    config.show_constellation_borders = True
    config.show_deepsky = True
    config.show_simple_milky_way = False
    config.show_enhanced_milky_way = False
    config.show_nebula_outlines = False
    config.flamsteed_numbers_only = False

    # 2. load default config
    default_config_loader = ConfigurationLoader(fchart3.get_data('default.conf'))
    default_config_loader.load_config(config)

    # 2. load custom config
    if config_file:
        config_loader = ConfigurationLoader(config_file)
        config_loader.load_config(config)


    # 3. override from command line
    if settings.parser.show_star_labels is not None:
        config.show_star_labels = settings.parser.show_star_labels
    if settings.parser.show_flamsteed is not None:
        config.show_flamsteed = settings.parser.show_flamsteed
    if settings.parser.show_mag_scale_legend is not None:
        config.show_mag_scale_legend = settings.parser.show_mag_scale_legend
    if settings.parser.show_map_scale_legend is not None:
        config.show_map_scale_legend = settings.parser.show_map_scale_legend
    if settings.parser.show_orientation_legend is not None:
        config.show_orientation_legend = settings.parser.show_orientation_legend
    if settings.parser.show_dso_legend is not None:
        config.show_dso_legend = settings.parser.show_dso_legend
    if settings.parser.show_coords_legend is not None:
        config.show_coords_legend = settings.parser.show_coords_legend
    if settings.parser.show_field_border is not None:
        config.show_field_border = settings.parser.show_field_border
    if settings.parser.show_equatorial_grid is not None:
        config.show_equatorial_grid = settings.parser.show_equatorial_grid
    if settings.parser.show_constellation_shapes is not None:
        config.show_constellation_shapes = settings.parser.show_constellation_shapes
    if settings.parser.show_constellation_borders is not None:
        config.show_constellation_borders = settings.parser.show_constellation_borders
    if settings.parser.show_simple_milky_way is not None:
        config.show_simple_milky_way = settings.parser.show_simple_milky_way
    if settings.parser.show_enhanced_milky_way is not None:
        config.show_enhanced_milky_way = settings.parser.show_enhanced_milky_way
    if settings.parser.show_deepsky is not None:
        config.show_deepsky = settings.parser.show_deepsky
    if settings.parser.show_nebula_outlines is not None:
        config.show_nebula_outlines = settings.parser.show_nebula_outlines

    if settings.parser.fov_telrad is not None:
        config.fov_telrad = settings.parser.fov_telrad

    if settings.parser.mirror_x is not None:
        config.mirror_x = settings.parser.mirror_x
    if settings.parser.mirror_y is not None:
        config.mirror_y = settings.parser.mirror_y

    if settings.parser.star_colors is not None:
        config.star_colors = settings.parser.star_colors

    if settings.parser.background_color is not None:
        config.background_color = _convert_color(settings.parser.background_color)
    if settings.parser.draw_color is not None:
        config.draw_color = _convert_color(settings.parser.draw_color)
    if settings.parser.label_color is not None:
        config.label_color = _convert_color(settings.parser.label_color)
    if settings.parser.constellation_lines_color is not None:
        config.constellation_lines_color = _convert_color(settings.parser.constellation_lines_color)
    if settings.parser.constellation_border_color is not None:
        config.constellation_border_color = _convert_color(settings.parser.constellation_border_color)
    if settings.parser.dso_color is not None:
        config.dso_color = _convert_color(settings.parser.dso_color)
    if settings.parser.nebula_color is not None:
        config.nebula_color = _convert_color(settings.parser.nebula_color)
    if settings.parser.galaxy_color is not None:
        config.galaxy_color = _convert_color(settings.parser.galaxy_color)
    if settings.parser.star_cluster_color is not None:
        config.star_cluster_color = _convert_color(settings.parser.star_cluster_color)
    if settings.parser.galaxy_cluster_color is not None:
        config.galaxy_cluster_color = _convert_color(settings.parser.galaxy_cluster_color)
    if settings.parser.milky_way_color is not None:
        config.milky_way_color = _convert_color(settings.parser.milky_way_color)
    if settings.parser.grid_color is not None:
        config.grid_color = _convert_color(settings.parser.grid_color)
    if settings.parser.telrad_color is not None:
        config.telrad_color = _convert_color(settings.parser.telrad_color)
    if settings.parser.constellation_linewidth is not None:
        config.constellation_linewidth = settings.parser.constellation_linewidth
    if settings.parser.constellation_linespace is not None:
        config.constellation_linespace = settings.parser.constellation_linespace
    if settings.parser.constellation_border_linewidth is not None:
        config.constellation_border_linewidth = settings.parser.constellation_border_linewidth
    if settings.parser.nebula_linewidth is not None:
        config.nebula_linewidth = settings.parser.nebula_linewidth
    if settings.parser.open_cluster_linewidth is not None:
        config.open_cluster_linewidth = settings.parser.open_cluster_linewidth
    if settings.parser.galaxy_cluster_linewidth is not None:
        config.galaxy_cluster_linewidth = settings.parser.galaxy_cluster_linewidth
    if settings.parser.dso_linewidth is not None:
        config.dso_linewidth = settings.parser.dso_linewidth
    if settings.parser.milky_way_linewidth is not None:
        config.milky_way_linewidth = settings.parser.milky_way_linewidth
    if settings.parser.legend_linewidth is not None:
        config.legend_linewidth = settings.parser.legend_linewidth
    if settings.parser.grid_linewidth is not None:
        config.grid_linewidth = settings.parser.grid_linewidth
    if settings.parser.telrad_linewidth is not None:
        config.telrad_linewidth = settings.parser.telrad_linewidth
    if settings.parser.no_margin is not None:
        config.no_margin = settings.parser.no_margin
    if settings.parser.font is not None:
        config.font = settings.parser.font
    if settings.parser.font_size is not None:
        config.font_size = settings.parser.font_size
    if settings.parser.legend_font_scale is not None:
        config.legend_font_scale = settings.parser.legend_font_scale
    if settings.parser.bayer_label_font_scale is not None:
        config.bayer_label_font_scale = settings.parser.bayer_label_font_scale
    if settings.parser.font_style_bayer is not None:
        config.bayer_label_font_style = _convert_font_style(settings.parser.font_style_bayer)
    if settings.parser.font_style_flamsteed is not None:
        config.flamsteed_label_font_style = _convert_font_style(settings.parser.font_style_flamsteed)
    if settings.parser.font_style_dso is not None:
        config.dso_label_font_style = _convert_font_style(settings.parser.font_style_dso)
    if settings.parser.flamsteed_numbers_only is not None:
        config.flamsteed_numbers_only = settings.parser.flamsteed_numbers_only

    if config.show_enhanced_milky_way:
        mw_scale_fac = 3.0

        bg_r, bg_g, bg_b = config.background_color[0], config.background_color[1], config.background_color[2]

        config.enhanced_milky_way_fade = (bg_r, (config.milky_way_color[0] - bg_r) * mw_scale_fac,
                                          bg_g, (config.milky_way_color[1] - bg_g) * mw_scale_fac,
                                          bg_b, (config.milky_way_color[2] - bg_b) * mw_scale_fac)

        config.milky_way_color = (bg_r + (config.milky_way_color[0]-bg_r),
                                  bg_g + (config.milky_way_color[1]-bg_g),
                                  bg_b + (config.milky_way_color[2]-bg_b))

    return config


if __name__ == '__main__':
    tm = time()

    data_dir = os.path.join(fchart3.get_catalogs_dir())

    # Create default settings and parse commandline
    settings = RuntimeSettings()

    print_version()

    # Create output space if necessary
    if not os.path.exists(settings.parser.output_dir):
        #print('Creating directory '+settings.parser.output_dir)
        print(_('Creating directory {}'.format(settings.parser.output_dir)))
        os.mkdir(settings.parser.output_dir)

    show_catalogs = settings.parser.show_catalogs.split(',') if settings.parser.show_catalogs else None

    config_file = None
    if settings.parser.config_file:
        installed_config_file = fchart3.get_data(settings.parser.config_file)
        if not installed_config_file.endswith('.conf'):
            installed_config_file += '.conf'
        if os.path.isfile(installed_config_file):
            config_file = installed_config_file
        elif os.path.isfile(settings.parser.config_file):
            config_file = settings.parser.config_file

        if config_file is None:
            print( _('Config file {} not found!\n'.format(settings.parser.config_file)))
            exit(-1)

    used_catalogs = UsedCatalogs(data_dir,
                                 extra_data_dir=settings.parser.extra_data_dir,
                                 limit_magnitude_deepsky=settings.parser.limit_magnitude_deepsky,
                                 force_messier=settings.parser.force_messier,
                                 force_asterisms=settings.parser.force_asterisms,
                                 force_unknown=settings.parser.force_unknown,
                                 show_catalogs=show_catalogs,
                                 )

    # Final report before mapmaking
    nb_reduced_deeplist= len(used_catalogs.reduced_deeplist)
    nb_used_catalogs   = len(used_catalogs.deeplist)
    print(' {0}/{1} deepsky objects after magnitude/messier selection.'.format(nb_reduced_deeplist,nb_used_catalogs))

    print('Making maps with: ')
    if config_file:
        print( _('   Config file    : {}'.format(config_file)))
    print(_('   Output dir     : {}'.format(settings.parser.output_dir)))
    print(_('   Deep sky limit : {}'.format(settings.parser.limit_magnitude_deepsky))
    print(_('   Stellar limit  : {}'.format(settings.parser.limit_magnitude_stars)))
    print(_('   Fieldsize      : {}  degrees'.format(settings.parser.fieldsize)))
    print(_('   Paper width    : {}  mm'.format(settings.parser.width))))
    print(_('   Paper height   : {}  mm'.format(settings.parser.height)))
    print(_('   Force Messier  : {}'.format(settings.parser.force_messier)))
    print(_('   Force asterisms: {}'.format(settings.parser.force_asterisms)))
    print(_('   Force pg       : {}'.format(settings.parser.force_unknown)))
    print(_('   Extra points   : {}'.format(len(settings.extra_positions_list))))
    print(_('   Show dso legend: {}'.format(settings.parser.show_dso_legend)))

    if settings.parser.extra_data_dir:
        print(_('   Extra data directory: {}'.format(settings.parser.extra_data_dir)))


    for object in settings.extra_positions_list:
        rax,decx,label,labelpos = object
        #print(label,':', rad2hms(rax), rad2dms(decx))
        print(_('{0}: rad2hms({1}), rad2dms({2})'.format(label, rax, decx)))

    # For all sources...
    for source in settings.parser.sourcelist:
        filename = ''
        # Parse sourcename
        if source.upper().rstrip().lstrip() == 'ALLMESSIER':
            print(_('alles'))
            for object in used_catalogs.messierlist:
                print('')
                print(_('M{}'.format(object.messier)))
                ra  = object.ra
                dec = object.dec
                artist = None
                filename = settings.parser.output_dir + os.sep + 'm' + str(object.messier).rjust(3).replace(' ','0')
                filename += '.pdf'
                artist = CairoDrawing(filename, settings.parser.width, settings.parser.height, format='pdf')
                engine = SkymapEngine(artist, settings.language, lm_stars = settings.parser.limit_magnitude_stars)
                engine.set_configuration(_create_engine_configuration(config_file))
                engine.set_field(ra, dec, settings.parser.fieldsize*np.pi/180.0/2.0)
                engine.set_caption('M '+str(object.messier))
                engine.set_showing_dso(object)
                engine.set_active_constellation(object.constellation)
                engine.make_map(used_catalogs, settings.extra_positions_list)
        else:
            showing_dso = None
            if ':' in source:
                data = source.split(',')
                if len(data) >= 3:
                    ra_str, dec_str = data[0:2]
                    caption_str = ''
                    label_pos = 'r'
                    ra_str = ra_str.lstrip().rstrip()
                    dec_str = dec_str.lstrip().rstrip()
                    if len(data) >= 3:
                        label_str = data[2].lstrip().rstrip()

                    if len(data) >= 4:
                        label_pos = data[3].rstrip().lstrip()

                    rasplit = ra_str.split(':')
                    decsplit = dec_str.split(':')

                    rah, ram, ras = 0.0, 0.0, 0.0
                    rah= float(rasplit[0])
                    if len(rasplit) >= 2:
                        ram = float(rasplit[1])
                    if len(rasplit) >= 3:
                        ras = float(rasplit[2])

                    decd, decm, decs, sign = 0.0, 0.0, 0.0, 1
                    decd = abs(float(decsplit[0]))
                    if decsplit[0][0] == '-':
                        sign = -1
                    if len(decsplit) >= 2:
                        decm = float(decsplit[1])
                    if len(decsplit) >= 3:
                        decs = float(decsplit[2])
                    ra, dec = hms2rad(rah, ram, ras), dms2rad(decd, decm, decs, sign)
                    cat = ''
                    name = ','.join(data[2:])
                    filename = settings.parser.output_dir + os.sep + name.replace(' ','-').replace('/', '-').replace(',', '')
                else:
                    print(_('Position specification needs three part argument, separated by commas: "ra,dec,caption"'))
                    sys.exit(-1)

            else:# : in source
                showing_dso, cat, name = used_catalogs.lookup_dso(source)
                if showing_dso:
                    ra = showing_dso.ra
                    dec = showing_dso.dec
                else:
                    ra = 1
                    dec = 0

            print('')
            print(cat, name)

            if ra >= 0.0:
                artist = None
                if settings.parser.output_file:
                    filename = settings.parser.output_file
                else:
                    if filename == '':
                        filename = settings.parser.output_dir + os.sep + source
                    filename += '.pdf'
                if filename.endswith('.png'):
                    output_format = 'png'
                elif filename.endswith('.svg'):
                    output_format = 'svg'
                elif filename.endswith('.tikz'):
                    output_format = 'tikz'
                else:
                    output_format = 'pdf'
                if output_format == 'tikz':
                    artist = TikZDrawing(filename,
                                         settings.parser.width,
                                         settings.parser.height,
                                         output_format)
                else:
                    artist = CairoDrawing(filename,
                                          settings.parser.width,
                                          settings.parser.height,
                                          output_format)
                engine = SkymapEngine(artist, settings.language,
                                      lm_stars=settings.parser.limit_magnitude_stars,
                                      lm_deepsky=settings.parser.limit_magnitude_deepsky)
                engine.set_configuration(_create_engine_configuration(config_file))
                engine.set_field(ra, dec, settings.parser.fieldsize*np.pi/180.0/2.0)
                caption = cat + ' ' + name

                if settings.parser.caption != False:
                    caption = settings.parser.caption
                if caption != '':
                    engine.set_caption(caption)

                showing_dsos = None
                if showing_dso:
                    if showing_dso.master_object:
                        showing_dso = showing_dso.master_object
                    showing_dsos = [showing_dso]
                    engine.set_active_constellation(showing_dso.constellation)
                tmp =   time()-tm
                print(_("Started in : {} ms".format(tmp)))
                engine.make_map(used_catalogs, showing_dsos=showing_dsos, extra_positions=settings.extra_positions_list)
            else:
                print(_('object not found, try appending an A or a B'))
    tmp =   time()-tm
    print(_("Chart generated in : {} ms ".format(tmp)))