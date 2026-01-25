#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2026 fchart3 authors
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

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SolarSystemBody(Enum):
    MERCURY = (1, "Mercury")
    VENUS   = (2, "Venus")
    EARTH   = (3, "Earth")
    MARS    = (4, "Mars")
    JUPITER = (5, "Jupiter")
    SATURN  = (6, "Saturn")
    URANUS  = (7, "Uranus")
    NEPTUNE = (8, "Neptune")
    PLUTO   = (9, "Pluto")
    SUN     = (10, "Sun")
    MOON    = (11, "Moon")

    def __init__(self, value, label):
        self.label = label

    @staticmethod
    def get_by_name(name: str):
        for body in SolarSystemBody:
            if body.label.lower() == name.lower():
                return body
        raise ValueError(f"No solar system body found with name: {name}")


@dataclass(slots=True)
class SolarSystemBodyObject:
    solar_system_body: SolarSystemBody
    ra: float
    dec: float
    north_pole_pa: float
    angular_radius: float
    mag: float
    phase: float
    distance: float
    ring_tilt: Optional[float] = None  # English comment: None for bodies without rings.


@dataclass(slots=True)
class PlanetMoonObject:
    planet: SolarSystemBody
    moon_name: str
    ra: float
    dec: float
    mag: float
    color: str
    distance: float
