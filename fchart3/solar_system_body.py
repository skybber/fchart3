#    fchart3 draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-2024 fchart authors
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

from enum import Enum


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


class SolarSystemBodyObject:
    def __init__(self, solar_system_body, ra, dec, north_pole_pa, angular_radius, mag, phase, distance, ring_tilt):
        self.solar_system_body = solar_system_body
        self.ra = ra
        self.dec = dec
        self.north_pole_pa = north_pole_pa
        self.angular_radius = angular_radius
        self.mag = mag
        self.phase = phase
        self.distance = distance
        self.ring_tilt = ring_tilt


class PlanetMoonObject:
    def __init__(self, planet, moon_name, ra, dec, mag, color, distance):
        self.planet = planet
        self.moon_name = moon_name
        self.ra = ra
        self.dec = dec
        self.mag = mag
        self.color = color
        self.distance = distance
