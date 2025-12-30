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

from .. import deepsky_object as deepsky


class WidgetDsoLegend:

    def __init__(self, dso_renderer, language, drawing_width, legend_margin, color=(0, 0, 0)):
        self.dso_renderer = dso_renderer
        self.language = language
        self.drawing_width = drawing_width
        self.legend_margin = legend_margin
        self.color = color

    def draw_dso_legend(self, graphics, ctx, erase_background):
        fh = graphics.gi_font_size
        # Draw list of symbols
        legendx = 0.48*self.drawing_width
        legendy = 0.49*self.drawing_width
        legendinc = fh

        r = fh/3.0
        text_offset = -2.5*r

        toplabels = [('OCL', len(self.language['OCL'])),
                     ('AST', len(self.language['AST'])),
                     ('G', len(self.language['G'])),
                     ('GCL', len(self.language['GCL']))]
        bottomlabels = [('SNR', len(self.language['SNR'])),
                        ('N', len(self.language['N'])),
                        ('PN', len(self.language['PN'])),
                        ('PG', len(self.language['PG']))]

        def labsort(x,y):
            r = 0
            if x[1] < y[1]:
                r = -1
            if x[1] > y[1]:
                r = 1
            return r

        toplabels.sort(key=deepsky.cmp_to_key(labsort))
        toplabels.reverse()
        tl = []
        for lab in toplabels:
            tl.append(lab[0])

        bottomlabels.sort(key=deepsky.cmp_to_key(labsort))
        bottomlabels.reverse()
        bl = []
        for lab in bottomlabels:
            bl.append(lab[0])

        self.dso_renderer.open_cluster(ctx, legendx, legendy - (tl.index('OCL') + 1)*legendinc, r, '', '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, legendy - (tl.index('OCL') + 1)*legendinc - fh/3.0, self.language['OCL'])

        self.dso_renderer.asterism(ctx, legendx, legendy - (tl.index('AST') + 1)*legendinc, r, '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, legendy - (tl.index('AST') + 1)*legendinc - fh/3.0, self.language['AST'])

        self.dso_renderer.galaxy(ctx, legendx, legendy - (tl.index('G') + 1)*legendinc, r, -1, 0.0, 7.0, '', '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, legendy - (tl.index('G') + 1)*legendinc - fh/3.0, self.language['G'])

        self.dso_renderer.globular_cluster(ctx, legendx, legendy - (tl.index('GCL') + 1)*legendinc, r, '', '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, legendy - (tl.index('GCL') + 1)*legendinc - fh/3.0, self.language['GCL'])

        legendy = self.legend_margin*self.drawing_width

        self.dso_renderer.supernova_remnant(ctx, legendx, -legendy + bl.index('SNR')*legendinc, r, '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, -legendy + bl.index('SNR')*legendinc - fh/3.0, self.language['SNR'])

        self.dso_renderer.planetary_nebula(ctx, legendx, -legendy + bl.index('PN')*legendinc, r, '', '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, -legendy+bl.index('PN')*legendinc - fh/3.0, self.language['PN'])

        self.dso_renderer.diffuse_nebula(ctx, legendx, -legendy + bl.index('N')*legendinc, r, -1, 0.0, '', '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, -legendy + bl.index('N')*legendinc - fh/3.0, self.language['N'])

        self.dso_renderer.unknown_object(ctx, legendx, -legendy + bl.index('PG')*legendinc, r, '', '', labelpos=1)
        graphics.set_pen_rgb(self.color)
        graphics.text_left(legendx + text_offset, -legendy + bl.index('PG')*legendinc - fh/3.0, self.language['PG'])
