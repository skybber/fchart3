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

class ProjectionInterface:
    def __init__(self, fieldcentre, drawingscale):
        self.drawingscale = drawingscale
        self.fieldcentre = fieldcentre

    def radec_to_xy(self, ra, dec):
        pass

    def radec_to_xyz(self, ra, dec):
        pass

    def np_radec_to_xy(self, ra, dec):
        pass

    def np_radec_to_xyz(self, ra, dec):
        pass

    def direction_ddec(self, ra, dec):
        pass
