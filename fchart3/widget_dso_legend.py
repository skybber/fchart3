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

from . import deepsky_object as deepsky


class WidgetDsoLegend:

    def __init__(self, language, drawingwidth, legend_margin, color=(0, 0, 0)):
        self.language = language
        self.drawingwidth = drawingwidth
        self.legend_margin = legend_margin
        self.color = color

    def draw_dso_legend(self, sky_map_engine, graphics, legend_only):
        fh = graphics.gi_font_size
        # Draw list of symbols
        legendx  = 0.48*self.drawingwidth
        legendy  = 0.49*self.drawingwidth
        legendinc= fh

        r = fh/3.0
        text_offset = -2.5*r

        toplabels=[('OCL', len(self.language['OCL'])),
                   ('AST', len(self.language['AST'])),
                   ('G', len(self.language['G'])),
                   ('GCL', len(self.language['GCL']))]
        bottomlabels=[('SNR', len(self.language['SNR'])),
                      ('N',len(self.language['N'])),
                      ('PN', len(self.language['PN'])),
                      ('PG',len(self.language['PG']))]

        def labsort(x,y):
            r = 0
            if x[1] < y[1]:
                r = -1
            if x[1] > y[1]:
                r = 1
            return r

        toplabels.sort(key = deepsky.cmp_to_key(labsort))
        toplabels.reverse()
        tl = []
        for lab in toplabels:
            tl.append(lab[0])

        bottomlabels.sort(key = deepsky.cmp_to_key(labsort))
        bottomlabels.reverse()
        bl = []
        for lab in bottomlabels:
            bl.append(lab[0])

        sky_map_engine.open_cluster(legendx, legendy - (tl.index('OCL') + 1)*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, legendy - (tl.index('OCL') + 1)*legendinc - fh/3.0, self.language['OCL'])

        sky_map_engine.asterism(legendx, legendy - (tl.index('AST') + 1)*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, legendy - (tl.index('AST') + 1)*legendinc - fh/3.0, self.language['AST'])

        sky_map_engine.galaxy(legendx, legendy - (tl.index('G') + 1)*legendinc, r, -1, 0.0, 7.0, '', '', '')
        graphics.text_left(legendx + text_offset, legendy - (tl.index('G') + 1)*legendinc - fh/3.0, self.language['G'])

        sky_map_engine.globular_cluster(legendx, legendy  - (tl.index('GCL') +1 )*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, legendy - (tl.index('GCL') + 1)*legendinc - fh/3.0, self.language['GCL'])

        legendy = self.legend_margin*self.drawingwidth

        sky_map_engine.supernova_remnant(legendx, -legendy + bl.index('SNR')*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, -legendy + bl.index('SNR')*legendinc - fh/3.0, self.language['SNR'])

        sky_map_engine.planetary_nebula(legendx, -legendy + bl.index('PN')*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, -legendy+bl.index('PN')*legendinc -  fh/3.0, self.language['PN'])

        sky_map_engine.diffuse_nebula(legendx, -legendy + bl.index('N')*legendinc, r, -1, 0.0, '', '', '')
        graphics.text_left(legendx + text_offset, -legendy + bl.index('N')*legendinc - fh/3.0, self.language['N'])

        sky_map_engine.unknown_object(legendx, -legendy + bl.index('PG')*legendinc, r, '', '', '')
        graphics.text_left(legendx + text_offset, -legendy + bl.index('PG')*legendinc - fh/3.0, self.language['PG'])
