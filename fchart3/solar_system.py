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

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from skyfield.api import load, Topos
from skyfield.magnitudelib import planetary_magnitude

import fchart3

UTC = timezone.utc

skyfield_ts = load.timescale()

# Remote SPK kernels for major moons (same as in czsky helper)
MAR099S_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/mar099s.bsp"
JUP365_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/jup365.bsp"
JUP347_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/jup347.bsp"
SAT_441_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/sat441.bsp"
URA111_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/ura111.bsp"
NEP097_BSP = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/nep097.bsp"

# de421 body keys used by Skyfield
BODY_KEY_DICT = {
    "mercury": "mercury",
    "venus": "venus",
    "mars": "mars",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter",
}

PLANET_DATA = {
    "sun": [696340],
    "moon": [1737.1],
    "mercury": [2439.7, 87.97, 115.88],
    "venus": [6051.8, 224.70, 583.92],
    "mars": [3389.5, 686.98, 779.94],
    "jupiter": [69911, 4332.59, 398.88],
    "saturn": [58232, 10759.22, 378.09],
    "uranus": [25362, 30687.15, 369.66],
    "neptune": [24622, 60190.03, 367.49],
    "pluto": [1188.3, 90560.0, 366.73],
}

PLANET_NORTH_POLE = {
    "saturn": [math.radians(40.589), math.radians(83.537)],
}

PLANET_MOONS_DATA = {
    fchart3.SolarSystemBody.MARS: {
        MAR099S_BSP: {
            "Phobos": [11.8, (1.0, 0.919, 0.806)],
            "Deimos": [12.89, (1.0, 0.93, 0.832)],
        },
    },
    fchart3.SolarSystemBody.JUPITER: {
        JUP365_BSP: {
            "Io": [-1.68, (1.0, 0.885, 0.598)],
            "Europa": [-1.41, (1.0, 0.968, 0.887)],
            "Ganymede": [-2.09, (1.0, 0.962, 0.871)],
            "Callisto": [-1.05, (1.0, 0.979, 0.897)],
            "Amalthea": [7.4, (1.0, 0.627, 0.492)],
        },
        JUP347_BSP: {
            "Himalia": [8.14, (1.0, 0.9, 0.75)],
        },
    },
    fchart3.SolarSystemBody.SATURN: {
        SAT_441_BSP: {
            "Titan": [-1.28, (1.0, 0.807, 0.453)],
            "Rhea": [0.1, (1.0, 0.981, 0.942)],
            "Iapetus": [1.5, (1.0, 0.973, 0.948)],
            "Enceladus": [2.1, (1.0, 0.998, 0.991)],
            "Mimas": [3.3, (1.0, 0.983, 0.972)],
            "Tethys": [0.6, (0.999, 1.0, 0.999)],
            "Dione": [0.8, (1.0, 0.98, 0.966)],
            "Phoebe": [6.89, (1.0, 0.9, 0.75)],
            "Hyperion": [4.63, (1.0, 0.914, 0.835)],
        },
    },
    fchart3.SolarSystemBody.URANUS: {
        URA111_BSP: {
            "Titania": [1.02, (1.0, 0.875, 0.779)],
            "Oberon": [1.23, (1.0, 0.875, 0.798)],
            "Umbriel": [2.1, (1.0, 0.956, 0.956)],
            "Ariel": [1.45, (1.0, 0.849, 0.731)],
            "Miranda": [3.6, (1.0, 0.902, 0.871)],
        },
    },
    fchart3.SolarSystemBody.NEPTUNE: {
        NEP097_BSP: {
            "Triton": [-1.24, (0.961, 1.0, 0.819)],
        },
    },
}

AU_TO_KM = 149597870.7

# Saturn pole vector (as in czsky helper)
SATURN_POLE = np.array([0.08547883, 0.07323576, 0.99364475])


def _get_de421():
    # Skyfield caches download locally; subsequent calls are fast.
    return load("de421.bsp")


def get_north_pole_pa(ra: float, dec: float, obj_ra: float, obj_dec: float) -> float:
    """Calculate North position angle, return in [0, 2*pi)."""
    d1 = dec
    a1 = ra
    a5 = obj_ra
    d5 = obj_dec

    sp = math.cos(d1) * math.sin(a1 - a5)
    cp = math.sin(d1) * math.cos(d5)
    cp -= math.cos(d1) * math.sin(d5) * math.cos(a1 - a5)

    pa = math.atan2(sp, cp) % (2.0 * math.pi)
    return pa


def create_solar_system_body_obj(
        eph,
        body_enum: "fchart3.SolarSystemBody",
        t=None,
        observer_lat: Optional[float] = None,
        observer_lon: Optional[float] = None,
        observer_elevation: float = 0.0,
):
    """Create fchart3.SolarSystemBodyObject for a given enum at time t."""
    if body_enum == fchart3.SolarSystemBody.EARTH:
        return None

    if t is None:
        ts = skyfield_ts
        t = ts.now()

    body_name = body_enum.name.lower()

    if body_name in ("sun", "moon"):
        body = eph[body_name]
    else:
        body = eph[BODY_KEY_DICT[body_name]]

    if (observer_lat is not None) and (observer_lon is not None):
        location = Topos(
            latitude_degrees=observer_lat,
            longitude_degrees=observer_lon,
            elevation_m=observer_elevation,
        )
        observer = (eph["earth"] + location).at(t)
    else:
        observer = eph["earth"].at(t)

    astrometric = observer.observe(body)
    ra_ang, dec_ang, distance = astrometric.radec()

    ra = ra_ang.radians
    dec = dec_ang.radians
    distance_km = distance.au * AU_TO_KM

    physical_radius_km = PLANET_DATA.get(body_name, [None])[0]
    if physical_radius_km and distance_km > physical_radius_km:
        angular_radius = math.asin(physical_radius_km / distance_km)
    else:
        angular_radius = 0.0

    if body_enum != fchart3.SolarSystemBody.SUN:
        phase_angle = astrometric.phase_angle(eph["sun"]).radians
    else:
        phase_angle = None

    if body_enum == fchart3.SolarSystemBody.SATURN:
        r_se = body.at(t).observe(eph["earth"]).position.au
        r_se_unit = r_se / np.linalg.norm(r_se)
        ring_tilt = float(np.arcsin(np.dot(r_se_unit, SATURN_POLE)))
    else:
        ring_tilt = None

    north_pole = PLANET_NORTH_POLE.get(body_name)
    if north_pole:
        north_pole_pa = get_north_pole_pa(north_pole[0], north_pole[1], ra, dec)
    else:
        north_pole_pa = None

    # Magnitude handling (same as your helper)
    if body_enum == fchart3.SolarSystemBody.SUN:
        mag = -26.7
    elif body_enum == fchart3.SolarSystemBody.MOON:
        mag = -12.0
    elif body_enum == fchart3.SolarSystemBody.PLUTO:
        mag = 14.5
    else:
        mag = float(planetary_magnitude(astrometric))

    return fchart3.SolarSystemBodyObject(
        body_enum,
        ra,
        dec,
        north_pole_pa,
        angular_radius,
        mag,
        phase_angle,
        distance_km,
        ring_tilt,
    )


def _create_planet_moon_obj(eph, planet_enum, moon_name: str, abs_mag: float, color, t=None):
    """Create fchart3.PlanetMoonObject."""
    if t is None:
        ts = skyfield_ts
        t = ts.now()

    pl_moon = eph[moon_name.lower()]
    earth = eph["earth"].at(t)
    sun = eph["sun"].at(t)

    astrometric_from_earth = earth.observe(pl_moon)
    ra_ang, dec_ang, distance = astrometric_from_earth.radec()

    astrometric_from_sun = sun.observe(pl_moon)
    distance_sun_au = astrometric_from_sun.distance().au

    distance_earth_au = distance.au
    distance_earth_km = distance_earth_au * AU_TO_KM

    mag = abs_mag + 5.0 * math.log10(distance_sun_au * distance_earth_au)

    return fchart3.PlanetMoonObject(
        planet_enum,
        moon_name,
        ra_ang.radians,
        dec_ang.radians,
        float(mag),
        color,
        float(distance_earth_km),
    )


def get_solsys_bodies(dt: datetime, observer_lat, observer_lon, observer_elevation):
    """Cached load of all solar system bodies (except Earth)."""
    ts = skyfield_ts
    t = ts.from_datetime(dt.astimezone(UTC))
    eph = _get_de421()

    bodies = []
    for body_enum in fchart3.SolarSystemBody:
        if body_enum in (fchart3.SolarSystemBody.EARTH,):
            continue
        bodies.append(
            create_solar_system_body_obj(
                eph,
                body_enum,
                t,
                observer_lat=observer_lat,
                observer_lon=observer_lon,
                observer_elevation=observer_elevation,
            )
        )
    # Filter None (Earth)
    return [b for b in bodies if b is not None]


def get_planet_moons(dt: datetime, maglim: float):
    """Cached load of planet moons down to magnitude limit."""
    ts = skyfield_ts
    t = ts.from_datetime(dt.astimezone(UTC))

    pl_moons = []
    for planet_enum, url_moons in PLANET_MOONS_DATA.items():
        for eph_url, moons in url_moons.items():
            eph = load(eph_url)
            for moon_name, (abs_mag, color) in moons.items():
                pl_moons.append(_create_planet_moon_obj(eph, planet_enum, moon_name, abs_mag, color, t))

    return [m for m in pl_moons if m.mag <= maglim]
