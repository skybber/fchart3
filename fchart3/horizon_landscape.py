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

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import configparser
import math
from typing import Optional, Tuple, List

Rgb = Tuple[float, float, float]
PointAzAlt = Tuple[float, float]  # radians (az, alt)


@dataclass(frozen=True)
class PolygonalHorizon:
    # Points in horizontal coordinates, in radians. Order is preserved from source files.
    points: Tuple[PointAzAlt, ...]


@dataclass(frozen=True)
class StellariumLandscape:
    name: str
    author: Optional[str]
    description: Optional[str]
    landscape_type: str

    ground_color: Optional[Rgb]
    horizon_line_color: Optional[Rgb]

    # Polygon horizon (if landscape_type == "polygonal")
    polygonal_horizon: Optional[PolygonalHorizon]

    # Rotation around Z axis (azimuth rotation), in radians.
    polygonal_rotate_z: float

    # geographical coordinates. These should exist and be used.
    loc_longitude: Optional[float]
    loc_latitude: Optional[float]
    loc_altitude: Optional[int]
    loc_timezone: Optional[str]


def _parse_rgb(value: str) -> Optional[Rgb]:
    # Parse ".15,.45,.05" or "0.15, 0.45, 0.05"
    if not value:
        return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 3:
        return None
    try:
        r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError:
        return None
    return (r, g, b)


def _parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value.strip())
    except Exception:
        return default


def _read_polygon_file(path: Path) -> List[Tuple[float, float]]:
    """
    Read Stellarium polygonal horizon file.
    Each non-comment line: "<az_deg> <alt_deg>"
    Returns degrees (az_deg, alt_deg) to allow later rotation + normalization.
    """
    pts: List[Tuple[float, float]] = []
    if not path.exists():
        print(f"Stellarium horizon file {path} not found. Falling back to Zero horizon.")
        return pts

    print(f"Processing Stellarium horizon file {path}.")
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Split by whitespace
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            az_deg = float(parts[0])
            alt_deg = float(parts[1])
        except ValueError:
            continue
        pts.append((az_deg, alt_deg))
    return pts


def _deg_to_rad(d: float) -> float:
    return d * math.pi / 180.0


def _wrap_deg_360(d: float) -> float:
    # Normalize degrees to [0, 360)
    d = d % 360.0
    if d < 0:
        d += 360.0
    return d


def load_stellarium_landscape(landscape_dir: str) -> StellariumLandscape:
    """
    Load Stellarium landscape from a directory containing landscape.ini.
    Cached (LRU) so repeated redraws don't re-parse files.
    """
    print(f"Loading Stellarium landscape {landscape_dir}.")

    base = Path(landscape_dir)
    ini_path = base / "landscape.ini"

    cp = configparser.ConfigParser(interpolation=None)
    cp.read(ini_path, encoding="utf-8")

    sec = "landscape"
    name = cp.get(sec, "name", fallback=base.name)
    author = cp.get(sec, "author", fallback=None)
    description = cp.get(sec, "description", fallback=None)
    landscape_type = cp.get(sec, "type", fallback="").strip().lower()

    ground_color = _parse_rgb(cp.get(sec, "ground_color", fallback=""))
    horizon_line_color = _parse_rgb(cp.get(sec, "horizon_line_color", fallback=""))

    # Stellarium uses polygonal_angle_rotatez for polygon rotation (degrees).
    # Keep support for a generic angle_rotatez as well (some landscapes may use variants).
    rotate_deg = _parse_float(cp.get(sec, "polygonal_angle_rotatez", fallback="0.0"), default=0.0)
    if rotate_deg == 0.0:
        rotate_deg = _parse_float(cp.get(sec, "angle_rotatez", fallback="0.0"), default=0.0)
    rotate_rad = _deg_to_rad(rotate_deg)

    polygonal_horizon: Optional[PolygonalHorizon] = None

    if landscape_type == "polygonal" or cp.get(sec, "polygonal_horizon_list", fallback=None) is not None:
        # polygonal_horizon_list can be "file.txt" or "a.txt, b.txt" etc.
        horizon_list_raw = cp.get(sec, "polygonal_horizon_list", fallback="").strip()
        print(f"polygonal_horizon_list: {horizon_list_raw}")
        files: List[str] = []
        if horizon_list_raw:
            # Split by comma first, then by whitespace
            for chunk in horizon_list_raw.split(","):
                chunk = chunk.strip()
                if not chunk:
                    continue
                for token in chunk.split():
                    token = token.strip()
                    if token:
                        files.append(token)

        all_pts_deg: List[Tuple[float, float]] = []
        for fn in files:
            all_pts_deg.extend(_read_polygon_file(base / fn))

        # Apply rotation and convert to radians
        pts_rad: List[PointAzAlt] = []
        for az_deg, alt_deg in all_pts_deg:
            az_rot = _wrap_deg_360(az_deg + rotate_deg)
            pts_rad.append((_deg_to_rad(az_rot), _deg_to_rad(alt_deg)))

        if len(pts_rad) >= 2:
            polygonal_horizon = PolygonalHorizon(points=tuple(pts_rad))

    sec = "location"
    loc_longitude = _parse_stel_angle(cp.get(sec, "longitude", fallback=None))
    loc_latitude = _parse_stel_angle(cp.get(sec, "latitude", fallback=None))
    loc_altitude = int(cp.get(sec, "altitude", fallback=None))
    loc_timezone = cp.get(sec, "timezone", fallback="").strip().lower()

    return StellariumLandscape(
        name=name,
        author=author,
        description=description,
        landscape_type=landscape_type,
        ground_color=ground_color,
        horizon_line_color=horizon_line_color,
        polygonal_horizon=polygonal_horizon,
        polygonal_rotate_z=rotate_rad,
        loc_longitude=loc_longitude,
        loc_latitude=loc_latitude,
        loc_altitude=loc_altitude,
        loc_timezone=loc_timezone
    )


def _parse_stel_angle(angle: str) -> float:
    """Parse an angle given in any of Stellarium's ways to write angles to config files
    This can be a regular float, or a string like "+1d23'45"
    """
    import re
    if 'd' in angle:
        r = re.compile(r'-?\d+')  # Not the best RE, but it should suffice
        comp = r.findall(angle)
        d: int = int(comp[0])
        m: float = math.copysign(float(comp[1]), d)
        s: float = 0.0
        if len(comp) > 2:
            s = math.copysign(float(comp[2]), d)
        return round((s / 60.0 + m) / 60.0 + d, 5)
    else:
        return round(float(angle), 5)
