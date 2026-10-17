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

"""Apparent magnitudes of comets and minor planets (same formulas as CzSkY light curves)."""

import math
from typing import Optional, Tuple


def _finite(value) -> Optional[float]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def body_geometry(earth, sun, body, t) -> Tuple[float, float, float]:
    """Heliocentric distance r [au], geocentric distance delta [au] and phase angle [deg]."""
    earth_at = earth.at(t)
    r_vec = body.at(t).position.au - sun.at(t).position.au
    delta_vec = earth_at.observe(body).position.au
    earth_sun_vec = earth_at.observe(sun).position.au

    r = math.sqrt(sum(c * c for c in r_vec))
    delta = math.sqrt(sum(c * c for c in delta_vec))
    earth_sun = math.sqrt(sum(c * c for c in earth_sun_vec))
    cos_phase = (r * r + delta * delta - earth_sun * earth_sun) / (2.0 * r * delta)
    phase = math.degrees(math.acos(max(-1.0, min(1.0, cos_phase))))
    return r, delta, phase


def comet_magnitude(g_mag: float, k_slope: float, r: float, delta: float) -> float:
    """Total cometary magnitude m = g + 5 log(delta) + 2.5 k log(r)."""
    return g_mag + 5.0 * math.log10(delta) + 2.5 * k_slope * math.log10(r)


def hg_magnitude(h_mag: float, g_slope: Optional[float], r: float, delta: float, phase_deg: float) -> float:
    """IAU H-G magnitude system (Bowell et al. 1989)."""
    if g_slope is None or not math.isfinite(g_slope):
        g_slope = 0.15
    tan_half = math.tan(math.radians(max(0.0, min(179.9, phase_deg))) / 2.0)
    phi1 = math.exp(-3.33 * tan_half ** 0.63)
    phi2 = math.exp(-1.87 * tan_half ** 1.22)
    flux = max((1.0 - g_slope) * phi1 + g_slope * phi2, 1e-12)
    return h_mag + 5.0 * math.log10(r * delta) - 2.5 * math.log10(flux)


def comet_magnitude_function(row, ts, earth, sun, body):
    """Return dt -> magnitude for an MPC comet row, or None when g/k are unknown."""
    g = _finite(row.get("magnitude_g"))
    k = _finite(row.get("magnitude_k"))
    if g is None or k is None:
        return None

    def magnitude_at(dt):
        r, delta, _ = body_geometry(earth, sun, body, ts.from_datetime(dt))
        return comet_magnitude(g, k, r, delta)
    return magnitude_at


def minor_planet_magnitude_function(row, ts, earth, sun, body):
    """Return dt -> magnitude for an MPCORB row, or None when H is unknown."""
    h = _finite(row.get("magnitude_H"))
    if h is None:
        return None
    g = _finite(row.get("magnitude_G"))

    def magnitude_at(dt):
        r, delta, phase = body_geometry(earth, sun, body, ts.from_datetime(dt))
        return hg_magnitude(h, g, r, delta, phase)
    return magnitude_at
