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


class WidgetPicker:

    def __init__(self, picker_radius, picker_linewidth, picker_color):
        self.picker_radius = picker_radius
        self.picker_linewidth = picker_linewidth
        self.picker_color = picker_color

    def draw(self, graphics):
        graphics.set_solid_line()
        graphics.set_pen_rgb(self.picker_color)
        graphics.set_linewidth(self.picker_linewidth)
        r = self.picker_radius
        x = r / 3.0
        graphics.line(-r, -r, -r+x, -r)
        graphics.line(-r, -r, -r, -r+x)
        graphics.line(r, -r, r-x, -r)
        graphics.line(r, -r, r, -r+x)
        graphics.line(-r, r, -r+x, r)
        graphics.line(-r, r, -r, r-x)
        graphics.line(r, r, r-x, r)
        graphics.line(r, r, r, r-x)
