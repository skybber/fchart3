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

class WidgetBase:
    def __init__(self, sky_map_engine, alloc_space_spec):
        self.engine = sky_map_engine
        self.alloc_space_spec = alloc_space_spec
        self.x, self.y = None, None
        self.width, self.height = None, None

    def get_rect(self):
        return self.x, self.y, self.width, self.height

    def allocate_space(self, space_widget_allocator):
        self.x, self.y = space_widget_allocator.alloc_space(self.width, self.height, self.alloc_space_spec)

    def draw_bounding_rect(self, graphics):
        graphics.set_linewidth(self.legend_linewidth)
        if 'bottom' in self.alloc_space_spec:
            graphics.line(self.x, self.y, self.x+self.width, self.y)
        if 'top' in self.alloc_space_spec:
            graphics.line(self.x, self.y-self.height, self.x+self.width, self.y-self.height)
        if 'left' in self.alloc_space_spec:
            graphics.line(self.x+self.width, self.y, self.x+self.width, self.y-self.height)
        if 'right' in self.alloc_space_spec:
            graphics.line(self.x, self.y, self.x, self.y-self.height)
