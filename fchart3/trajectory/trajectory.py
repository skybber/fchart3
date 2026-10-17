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

import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union

from .types import TrajectoryPoint


def _get_trajectory_time_delta(dt_from: datetime, dt_to: datetime):
    delta = dt_to - dt_from
    if delta.days > 120:
        return timedelta(days=10), 0
    if delta.days > 30:
        return timedelta(days=5), 0
    if delta.days > 4:
        return timedelta(days=1), 0
    if delta.days > 2:
        return timedelta(hours=12), 12
    if delta.days > 1:
        return timedelta(hours=6), 6
    return timedelta(hours=3), 3


# Upper bound for labeled points of one trajectory (protects against a tiny custom step).
MAX_TRAJECTORY_LABELS = 400


def _format_trajectory_label(cur: datetime, prev: Optional[datetime]) -> str:
    new_month = prev is None or prev.month != cur.month
    day = cur.strftime("%d.%m.") if new_month else cur.strftime("%d")
    if cur.hour == 0 and cur.minute == 0:
        return day
    time_str = cur.strftime("%H:%M")
    # A time on the first point or on a new day would be ambiguous without the day.
    if prev is None or prev.date() != cur.date():
        sep = " " if new_month else ". "
        return day + sep + time_str
    return time_str


@dataclass(frozen=True)
class RefinableTrajectory:
    """
    Labeled trajectory points that can be densified once the chart projection is known.

    times[i] is the time of points[i]; position_at(dt) returns (ra, dec) in radians.
    """
    points: List[TrajectoryPoint]
    times: List[datetime]
    position_at: Callable[[datetime], Tuple[float, float]]


def _point_segment_distance(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    d2 = dx * dx + dy * dy
    if d2 <= 0.0:
        return math.hypot(px - ax, py - ay)
    u = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
    return math.hypot(px - (ax + u * dx), py - (ay + u * dy))


def refine_trajectory(
    trajectory: RefinableTrajectory,
    project: Callable[[float, float], Optional[Tuple[float, float]]],
    tolerance: float,
    max_depth: int = 12,
    max_evaluations: int = 2000,
) -> List[TrajectoryPoint]:
    """
    Return trajectory points with unlabeled points (label=None) added so the polyline drawn
    on the chart follows the true path.

    project(ra, dec) maps to chart coordinates, or returns None for a hidden point.
    An interval is split while a projected check point at 1/4, 1/2 or 3/4 of its time span lies
    farther than `tolerance` (chart units) from the projected segment between its ends.
    Three check points catch loops and S-shapes that a single midpoint can miss.
    Intervals with mixed visibility are split down to max_depth, and hidden points are kept so
    the renderer breaks the line there. max_evaluations caps new position computations for
    the whole trajectory. When splitting stops at either limit, the check points already computed
    for the interval are kept.
    """
    points, times = trajectory.points, trajectory.times
    if tolerance <= 0.0 or len(times) < 2:
        return list(points)

    cache = {dt: (pt.ra, pt.dec, project(pt.ra, pt.dec)) for dt, pt in zip(times, points)}
    evaluations = 0
    out: List[TrajectoryPoint] = []

    def position(dt):
        """Cached position, or None when it is not known and the evaluation budget is used up."""
        nonlocal evaluations
        pos = cache.get(dt)
        if pos is None and evaluations < max_evaluations:
            evaluations += 1
            ra, dec = trajectory.position_at(dt)
            pos = (ra, dec, project(ra, dec))
            cache[dt] = pos
        return pos

    def add_line_point(dt):
        ra, dec, _ = cache[dt]
        out.append(TrajectoryPoint(ra=ra, dec=dec, label=None, sun_ra=None, sun_dec=None))

    def refine(t0, t1, depth):
        # Halving (not span*k/4) gives children exactly the cached check times of their parent.
        tm = t0 + (t1 - t0) / 2
        check_times = (t0 + (tm - t0) / 2, tm, tm + (t1 - tm) / 2)
        checks = [position(t) for t in check_times]

        if all(c is not None for c in checks):
            a = cache[t0][2]
            b = cache[t1][2]
            projected = [c[2] for c in checks]
            visible = [p is not None for p in (a, b, *projected)]
            if not any(visible):
                return
            if all(visible) and all(
                    _point_segment_distance(q[0], q[1], a[0], a[1], b[0], b[1]) <= tolerance for q in projected):
                return
            if depth < max_depth:
                refine(t0, tm, depth + 1)
                add_line_point(tm)
                refine(tm, t1, depth + 1)
                return

        # Stopped by depth or budget: keep the check points already known, in time order,
        # so hidden ones still break the drawn line.
        for t in check_times:
            if t in cache:
                add_line_point(t)

    out.append(points[0])
    for i in range(1, len(points)):
        refine(times[i - 1], times[i], 0)
        out.append(points[i])
    return out


def build_trajectory(
    *,
    dt_from: datetime,
    dt_to: datetime,
    ts,
    earth,
    body,
    is_comet: bool,
    sun=None,
    refinable: bool = False,
    step: Optional[timedelta] = None,
) -> Union[List[TrajectoryPoint], RefinableTrajectory, None]:
    """
    Labeled points are placed every `step`; without it the step is chosen from the range length.

    With refinable=True the result is a RefinableTrajectory that also ends exactly at dt_to and
    is densified by refine_trajectory() once the chart projection is known.
    """
    if dt_from is None or dt_to is None or dt_from >= dt_to:
        return None

    if (dt_to - dt_from).days > 365:
        dt_to = dt_from + timedelta(days=365)

    if step is None:
        step, _ = _get_trajectory_time_delta(dt_from, dt_to)
    elif step.total_seconds() <= 0:
        raise ValueError("Trajectory step must be positive.")
    elif (dt_to - dt_from) / step > MAX_TRAJECTORY_LABELS:
        raise ValueError(f"Trajectory step {step} gives more than {MAX_TRAJECTORY_LABELS} labeled points.")

    def position_at(dt: datetime):
        ra, dec, _ = earth.at(ts.from_datetime(dt)).observe(body).radec()
        return float(ra.radians), float(dec.radians)

    points: List[TrajectoryPoint] = []
    times: List[datetime] = []

    cur = dt_from
    prev = None

    while cur <= dt_to:
        ra_rad, dec_rad = position_at(cur)

        label = _format_trajectory_label(cur, prev)
        prev = cur

        sun_ra = None
        sun_dec = None

        if is_comet and sun is not None:
            try:
                sun_obs = earth.at(ts.from_datetime(cur)).observe(sun)
                sun_ra_ang, sun_dec_ang, _ = sun_obs.radec()
                sun_ra = float(sun_ra_ang.radians)
                sun_dec = float(sun_dec_ang.radians)
            except Exception:
                sun_ra = None
                sun_dec = None

        points.append(TrajectoryPoint(
            ra=ra_rad,
            dec=dec_rad,
            label=label,
            sun_ra=sun_ra,
            sun_dec=sun_dec,
        ))
        times.append(cur)

        cur += step

    if not refinable:
        return points

    if times[-1] < dt_to:
        ra_rad, dec_rad = position_at(dt_to)
        points.append(TrajectoryPoint(ra=ra_rad, dec=dec_rad, label=None, sun_ra=None, sun_dec=None))
        times.append(dt_to)

    return RefinableTrajectory(points, times, position_at)
