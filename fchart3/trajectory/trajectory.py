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

from datetime import datetime, timedelta
from typing import Optional, List

from .types import TrajectoryPoint


def _get_trajectory_time_delta(dt_from: datetime, dt_to: datetime):
    delta = dt_to - dt_from
    if delta.days > 120:
        return timedelta(days=30), 0
    if delta.days > 30:
        return timedelta(days=7), 0
    if delta.days > 4:
        return timedelta(days=1), 0
    if delta.days > 2:
        return timedelta(hours=12), 12
    if delta.days > 1:
        return timedelta(hours=6), 6
    return timedelta(hours=3), 3


def _format_trajectory_label(cur: datetime, prev_month: Optional[int]) -> str:
    if prev_month is None or prev_month != cur.month:
        return cur.strftime("%d.%m.") if (cur.hour == 0) else cur.strftime("%H:00")
    return cur.strftime("%d") if (cur.hour == 0) else cur.strftime("%H:00")


def build_trajectory(
    *,
    dt_from: datetime,
    dt_to: datetime,
    ts,
    earth,
    body,
    is_comet: bool,
    sun=None,
) -> Optional[List[TrajectoryPoint]]:
    if dt_from is None or dt_to is None or dt_from >= dt_to:
        return None

    if (dt_to - dt_from).days > 365:
        dt_to = dt_from + timedelta(days=365)

    step, _ = _get_trajectory_time_delta(dt_from, dt_to)
    points: List[TrajectoryPoint] = []

    cur = dt_from
    prev_month = None

    while cur <= dt_to:
        t = ts.from_datetime(cur)
        obs = earth.at(t).observe(body)
        ra, dec, _ = obs.radec()

        label = _format_trajectory_label(cur, prev_month)
        prev_month = cur.month

        sun_ra = None
        sun_dec = None

        if is_comet and sun is not None:
            try:
                sun_obs = earth.at(t).observe(sun)
                sun_ra_ang, sun_dec_ang, _ = sun_obs.radec()
                sun_ra = float(sun_ra_ang.radians)
                sun_dec = float(sun_dec_ang.radians)
            except Exception:
                sun_ra = None
                sun_dec = None

        pt = TrajectoryPoint(
            ra=float(ra.radians),
            dec=float(dec.radians),
            label=label,
            sun_ra=sun_ra,
            sun_dec=sun_dec,
        )
        points.append(pt)

        cur += step

    return points
