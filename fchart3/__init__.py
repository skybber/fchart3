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

__doc__ = """
The modules saguaro and revngc are meant for the import of deepsky data

skymap_engine contains the SkymapEngine class that draws maps of the sky,
given a StarCatalog and DeepskyCatalog. eps and pdf provide classes to
create eps and pdf files respectively. These classes are subclassed
from GraphicsInterface.

astrocalc provides coordinate conversions etc.
"""

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_data(path):
    return os.path.join(_ROOT, 'data', path)

def get_catalogs_dir():
    return os.path.join(get_data('catalogs'))

from fchart3.skymap_engine import *
from fchart3.configuration import *
from fchart3.used_catalogs import *
from fchart3.cairo import *
from fchart3.graphics_interface import *

