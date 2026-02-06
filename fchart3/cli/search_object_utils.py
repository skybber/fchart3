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

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from skyfield.api import load
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from .solar_system import get_solsys_bodies, get_planet_moons
from ..trajectory import build_trajectory
from ..i18n import install_translator

_ = install_translator()

skyfield_ts = load.timescale()


class TargetType(str, Enum):
    MOON = "moon"
    STAR = "star"
    SOLAR_SYSTEM = "solar_system"
    PLANET_MOON = "planet_moon"
    MINOR_PLANET = "minor_planet"  # new


@dataclass(frozen=True)
class ResolvedTarget:
    """Resolved target with equatorial coordinates in radians."""
    target_type: TargetType
    name: str
    ra_rad: float
    dec_rad: float
    caption: str = ""


def _strip_accents(s: str) -> str:
    """Normalize unicode and strip accents (useful for Czech names)."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _norm(s: str) -> str:
    """Casefold + remove accents + trim."""
    return _strip_accents(s).casefold().strip()


def _norm_compact(s: str) -> str:
    """Compact normalization for tolerant matching (remove whitespace and separators)."""
    s = _norm(s)
    return re.sub(r"[\s\.\-_]+", "", s)


# Bayer token support (minimal, extend as needed)
_GREEK_SYMBOL_TO_NAME = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa",
    "λ": "lambda", "μ": "mu", "ν": "nu", "ξ": "xi", "ο": "omicron",
    "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "υ": "upsilon",
    "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
}
_CZ_GREEK_NAME_TO_NAME = {
    "alfa": "alpha",
    "beta": "beta",
    "gama": "gamma",
    "delta": "delta",
    "epsilon": "epsilon",
    "eta": "eta",
    "teta": "theta",
    "theta": "theta",
    "omega": "omega",
}


def _normalize_bayer_token(tok: str) -> Optional[str]:
    """Return canonical bayer token name (alpha/beta/...) or None."""
    t = tok.strip()
    if not t:
        return None
    if t in _GREEK_SYMBOL_TO_NAME:
        return _GREEK_SYMBOL_TO_NAME[t]
    k = _norm(t)
    if k in _CZ_GREEK_NAME_TO_NAME:
        return _CZ_GREEK_NAME_TO_NAME[k]
    if k in set(_GREEK_SYMBOL_TO_NAME.values()):
        return k
    return None


def _bsc_to_search_labels(bsc_star: Any) -> Dict[str, str]:
    """
    Build possible textual labels for a BSC star object.
    Returns dict[normalized_key] = pretty_label
    """
    labels: Dict[str, str] = {}

    greek = getattr(bsc_star, "greek", None)  # e.g. "alp"
    greek_no = getattr(bsc_star, "greek_no", "") or ""  # e.g. "1"
    flam = getattr(bsc_star, "flamsteed", None)  # e.g. "58 Ori"
    con = getattr(bsc_star, "constellation", None)  # e.g. "ori"
    hd = getattr(bsc_star, "HD", None)

    con_code = None
    if con:
        con_code = str(con).strip().upper()

    # Flamsteed: stored as "58 Ori"
    if flam:
        flam_s = str(flam).strip()
        labels[_norm(flam_s)] = flam_s
        labels[_norm_compact(flam_s)] = flam_s

        # Also accept "58Ori" (no space)
        m = re.match(r"^\s*([0-9]+)\s*([A-Za-z]{3})\s*$", flam_s.replace(" ", ""))
        if m:
            labels[_norm(f"{m.group(1)} {m.group(2).upper()}")] = flam_s
            labels[_norm_compact(f"{m.group(1)}{m.group(2).upper()}")] = flam_s

    # Bayer: accept "alp ORI", plus expand alp->alpha (common subset)
    if greek and con_code:
        greek = str(greek).strip().casefold()
        labels[_norm(f"{greek}{greek_no} {con_code}")] = f"{greek}{greek_no} {con_code}"
        labels[_norm_compact(f"{greek}{greek_no}{con_code}")] = f"{greek}{greek_no} {con_code}"
        # Also accept without greek_no (e.g. user types "alp ORI")
        labels[_norm(f"{greek} {con_code}")] = f"{greek} {con_code}"
        labels[_norm_compact(f"{greek}{con_code}")] = f"{greek} {con_code}"

        three_to_full = {
            "alp": "alpha", "bet": "beta", "gam": "gamma", "del": "delta", "eps": "epsilon",
            "zet": "zeta", "eta": "eta", "the": "theta", "iot": "iota", "kap": "kappa",
            "lam": "lambda", "mu": "mu", "nu": "nu", "ksi": "xi", "omi": "omicron",
            "pi": "pi", "rho": "rho", "sig": "sigma", "tau": "tau", "ups": "upsilon",
            "phi": "phi", "chi": "chi", "psi": "psi", "ome": "omega",
        }
        full = three_to_full.get(greek)
        if full:
            labels[_norm(f"{full} {con_code}")] = f"{full} {con_code}"
            labels[_norm_compact(f"{full}{con_code}")] = f"{full} {con_code}"

            # Greek symbol variants (α ORI, β ORI, ...)
            full_to_sym = {v: k for k, v in _GREEK_SYMBOL_TO_NAME.items()}
            sym = full_to_sym.get(full)
            if sym:
                labels[_norm(f"{sym} {con_code}")] = f"{sym} {con_code}"
                labels[_norm_compact(f"{sym}{con_code}")] = f"{sym} {con_code}"

    # HD ids
    if hd is not None:
        try:
            hd_i = int(hd)
            labels[_norm(f"HD {hd_i}")] = f"HD {hd_i}"
            labels[_norm_compact(f"HD{hd_i}")] = f"HD {hd_i}"
        except Exception:
            pass

    return labels


def build_star_index(bsc_hip_map: Dict[int, Any]) -> Dict[str, int]:
    """Build query_key -> HIP index using the bsc_hip_map."""
    idx: Dict[str, int] = {}
    for hip, bsc_star in (bsc_hip_map or {}).items():
        if hip is None or hip <= 0:
            continue

        # Sometimes bsc_hip_map can store a pre-formatted label string.
        if isinstance(bsc_star, str):
            idx.setdefault(_norm(bsc_star), hip)
            idx.setdefault(_norm_compact(bsc_star), hip)
            continue

        for k in _bsc_to_search_labels(bsc_star).keys():
            idx.setdefault(k, hip)

    return idx


def _star_record_by_hip(star_catalog: Any, hip: int) -> Optional[Any]:
    """
    Retrieve star record for HIP, trying multiple possible catalog APIs.
    We keep this defensive because star_catalog implementations vary.
    """
    # Dedicated method
    if hasattr(star_catalog, "get_star_by_hip"):
        try:
            return star_catalog.get_star_by_hip(hip)
        except Exception:
            pass

    # Numpy structured arrays inside known attributes
    for attr in ("stars", "data", "catalog", "star_data"):
        if hasattr(star_catalog, attr):
            arr = getattr(star_catalog, attr)
            try:
                if hasattr(arr, "dtype") and arr.dtype.names and "hip" in arr.dtype.names:
                    hits = arr[arr["hip"] == hip]
                    if hits is not None and len(hits) > 0:
                        return hits[0]
            except Exception:
                continue

    # Iterable fallback
    try:
        for rec in star_catalog:
            if getattr(rec, "hip", None) == hip:
                return rec
    except Exception:
        pass

    return None


def resolve_star(query: str, star_catalog: Any, bsc_hip_map: Dict[int, Any], cache: Dict[str, Any]) -> Optional[ResolvedTarget]:
    """
    Resolve star using the same sources as StarsRenderer:
      - star_catalog for coordinates (ra/dec or x/y/z)
      - bsc_hip_map for names (greek/flamsteed/HD/constellation)

    cache is caller-provided so we can reuse the star index across queries.
    """
    if not query or star_catalog is None or bsc_hip_map is None:
        return None

    q_norm = _norm(query)
    q_comp = _norm_compact(query)

    idx = cache.get("star_index")
    if idx is None:
        idx = build_star_index(bsc_hip_map)
        cache["star_index"] = idx

    # Explicit HIP query: "HIP 12345"
    m = re.match(r"^\s*HIP\s*([0-9]+)\s*$", query.strip(), re.IGNORECASE)
    if m:
        hip = int(m.group(1))
        bsc_star = bsc_hip_map.get(hip)
        if bsc_star is None:
            return None
        return ResolvedTarget(TargetType.STAR, name=f"HIP {hip}", ra_rad=bsc_star.ra, dec_rad=bsc_star.dec, caption=f"HIP {hip}")
    hip = idx.get(q_norm) or idx.get(q_comp)

    # Bayer patterns: "alpha Ori", "alfa Ori", "α Ori"
    if not hip:
        words = query.strip().split()
        if len(words) == 2:
            b = _normalize_bayer_token(words[0])
            con = words[1].upper()
            if b:
                hip = idx.get(_norm(f"{b} {con}")) or idx.get(_norm_compact(f"{b}{con}"))

    # Flamsteed compact: "58Ori"
    if not hip:
        m2 = re.match(r"^\s*([0-9]+)\s*([A-Za-z]{3})\s*$", query.strip().replace(" ", ""))
        if m2:
            key1 = _norm(f"{m2.group(1)} {m2.group(2).upper()}")
            key2 = _norm_compact(f"{m2.group(1)}{m2.group(2).upper()}")
            hip = idx.get(key1) or idx.get(key2)

    # HD: "HD48915" / "HD 48915"
    if not hip:
        m3 = re.match(r"^\s*HD\s*([0-9]+)\s*$", query.strip(), re.IGNORECASE)
        if m3:
            key = _norm(f"HD {int(m3.group(1))}")
            hip = idx.get(key) or idx.get(_norm_compact(key))

    if not hip:
        return None

    bsc_star = bsc_hip_map.get(hip)
    if bsc_star is None:
        return None

    ra = bsc_star.ra
    dec = bsc_star.dec

    # Prefer nicer caption from BSC info
    bsc = bsc_hip_map.get(int(hip))
    if isinstance(bsc, str):
        caption = bsc
    elif bsc is not None:
        flam = bsc.flamsteed
        if flam:
            caption = str(flam)
        else:
            caption = f"HIP {hip}"
    else:
        caption = f"HIP {hip}"

    return ResolvedTarget(TargetType.STAR, name=caption, ra_rad=ra, dec_rad=dec, caption=caption)


_SOLAR_ALIASES = {
    _norm("sun"): "sun",
    _norm("moon"): "moon",
    _norm("mercury"): "mercury",
    _norm("merkur"): "mercury",
    _norm("venus"): "venus",
    _norm("mars"): "mars",
    _norm("jupiter"): "jupiter",
    _norm("saturn"): "saturn",
    _norm("uranus"): "uranus",
    _norm("neptune"): "neptune",
    _norm("neptun"): "neptune",
    _norm("pluto"): "pluto",
}


def resolve_solar_system(
        query: str,
        *,
        dt_utc: Optional[datetime],
        observer_lat_deg: Optional[float],
        observer_lon_deg: Optional[float],
) -> Optional[ResolvedTarget]:
    """
    Resolve Sun/Moon/planets by localized aliases using get_solsys_bodies().
    Note: if observer lat/lon are not provided, we fall back to (0,0).
    """
    if not query:
        return None
    if dt_utc is None:
        dt_utc = datetime.now(timezone.utc)

    key = _norm(query)
    canonical = _SOLAR_ALIASES.get(key, key)

    lat = observer_lat_deg if observer_lat_deg is not None else 0.0
    lon = observer_lon_deg if observer_lon_deg is not None else 0.0

    try:
        bodies = get_solsys_bodies(dt_utc, observer_lat=lat, observer_lon=lon, observer_elevation=0.0)
    except Exception:
        return None

    for b in bodies or []:
        bname = b.solar_system_body.label
        if not bname:
            continue
        if _norm(str(bname)) == canonical:
            ra = b.ra
            dec = b.dec
            if ra is None or dec is None:
                continue
            return ResolvedTarget(
                TargetType.SOLAR_SYSTEM,
                name=str(bname),
                ra_rad=float(ra),
                dec_rad=float(dec),
                caption=str(bname),
            )

    return None


def resolve_planet_moon(query: str, *, dt_utc: Optional[datetime], maglim: float = 12.0) -> Optional[ResolvedTarget]:
    """Resolve a planet moon by name using get_planet_moons()."""
    if not query:
        return None
    if dt_utc is None:
        dt_utc = datetime.now(timezone.utc)

    key = _norm(query)

    try:
        moons = get_planet_moons(dt_utc, maglim=maglim)
    except Exception:
        return None

    for m in moons or []:
        if _norm(str(m.moon_name)) == key:
            ra = m.ra
            dec = m.dec
            if ra is None or dec is None:
                continue
            return ResolvedTarget(
                TargetType.PLANET_MOON,
                name=str(m.moon_name),
                ra_rad=float(ra),
                dec_rad=float(dec),
                caption=str(m.moon_name),
            )

    return None


def _load_mpc_comets_df(mpc_comets_file: str | None):
    """
    Load MPC comets dataframe using Skyfield.
    If mpc_comets_file is provided, load from local file.
    Otherwise try Skyfield's default MPC comets source (network).
    """
    if mpc_comets_file:
        try:
            with open(mpc_comets_file, "rb") as f:
                return mpc.load_comets_dataframe(f)
        except Exception as e:
            print(_(f"Failed to load MPC comets from file '{mpc_comets_file}': {e}"))
            return None

    # Network fallback (if available in user's environment)
    try:
        # Skyfield exposes a URL constant in mpc; if not present, this will fail and we handle it.
        comet_url = mpc.COMET_URL
        return mpc.load_comets_dataframe(comet_url)
    except Exception as e:
        print(_(f"Failed to load MPC comets from network source: {e}"))
        print(_(
            "Tip: provide a local MPC comets file via --mpc-comets-file."
        ))
        return None


def _find_mpc_comet_row(comet_id: str, df):
    """
    Find a comet row in MPC comets dataframe.
    We try:
      - exact match on 'designation' (case-insensitive)
      - contains match on 'designation' (case-insensitive)
      - exact match on index (case-insensitive) if index looks usable
    Returns a pandas Series-like row or None.
    """
    if df is None:
        return None
    q = comet_id.strip()
    if not q:
        return None

    q_cf = q.casefold()

    # 'designation' column is the usual one in Skyfield MPC frames
    if "designation" in df.columns:
        try:
            col = df["designation"].astype(str)
            exact = df[col.str.casefold() == q_cf]
            if len(exact) > 0:
                return exact.iloc[0]
            partial = df[col.str.casefold().str.contains(q_cf, na=False)]
            if len(partial) > 0:
                return partial.iloc[0]
        except Exception:
            pass

    # Index fallback
    try:
        idx = df.index.astype(str)
        exact_i = df[idx.str.casefold() == q_cf]
        if len(exact_i) > 0:
            return exact_i.iloc[0]
    except Exception:
        pass

    return None




def resolve_comet(source: str, *, dt_utc: datetime, traj_from: datetime, traj_to: datetime, mpc_comets_file: str | None, cfg=None):
    """
    Resolve comet by MPC designation, return:
      (name, ra_rad, dec_rad, trajectory_list)
    """
    if dt_utc is None:
        return None

    df = _load_mpc_comets_df(mpc_comets_file)
    if df is None:
        return None

    row = _find_mpc_comet_row(source, df)
    if row is None:
        return None

    try:
        eph = load("de421.bsp")
        sun = eph["sun"]
        earth = eph["earth"]
        # Same approach as czsky: heliocentric orbit body relative to Sun
        body = sun + mpc.comet_orbit(row, skyfield_ts, GM_SUN)
    except Exception as e:
        print(_(f"Failed to build comet orbit for '{source}': {e}"))
        return None

    # Current position at dt_utc
    try:
        t_now = skyfield_ts.from_datetime(dt_utc)
        ra_ang, dec_ang, _ = earth.at(t_now).observe(body).radec()
        ra_rad = float(ra_ang.radians)
        dec_rad = float(dec_ang.radians)
    except Exception as e:
        print(_(f"Failed to compute comet RA/Dec for '{source}': {e}"))
        return None

    # Trajectory
    try:
        traj = build_trajectory(
            dt_from=traj_from,
            dt_to=traj_to,
            ts=skyfield_ts,
            earth=earth,
            body=body,
            is_comet=True,
            sun=sun,
        )
    except Exception as e:
        print(_(f"Failed to compute comet trajectory for '{source}': {e}"))
        traj = None

    # Prefer designation field if present
    comet_name = source
    try:
        if "designation" in row.index:
            comet_name = str(row["designation"])
    except Exception:
        pass
    trajectories = [traj] if traj is not None else None
    return comet_name, ra_rad, dec_rad, trajectories


def _load_mpc_minor_planets_df(mpc_minor_planets_file: str | None):
    """
    Load MPCORB dataframe using Skyfield.
    Requires a local file (recommended: MPCORB.9999.DAT).
    """
    if not mpc_minor_planets_file:
        return None
    try:
        with open(mpc_minor_planets_file, "rb") as f:
            # Skyfield API name differs by version; try both.
            if hasattr(mpc, "load_mpcorb_dataframe"):
                return mpc.load_mpcorb_dataframe(f)
            if hasattr(mpc, "load_mpcorb"):
                # Fallback: some older versions expose load_mpcorb(); may not be dataframe.
                return mpc.load_mpcorb(f)
    except Exception as e:
        print(_(f"Failed to load MPC minor planets from file '{mpc_minor_planets_file}': {e}"))
        return None
    return None


def _find_mpc_minor_planet_row(query: str, df):
    """
    Find a minor planet row in MPCORB dataframe.
    Supports:
      - numeric designation (e.g. "1", "433") -> df.iloc[n-1] (works well for MPCORB.9999.DAT)
      - name/designation partial match if columns exist.
    """
    if df is None or not query:
        return None

    q = query.strip()
    if not q:
        return None

    # Numeric designation (common use-case; also avoids name ambiguity).
    if q.isdigit():
        n = int(q)
        try:
            if 1 <= n <= len(df):
                return df.iloc[n - 1]
        except Exception:
            pass

    q_cf = q.casefold()

    # Try columns that often exist in MPCORB dataframes.
    for colname in ("name", "designation", "packed_designation"):
        if hasattr(df, "columns") and colname in df.columns:
            try:
                col = df[colname].astype(str)
                exact = df[col.str.casefold() == q_cf]
                if len(exact) > 0:
                    return exact.iloc[0]
                partial = df[col.str.casefold().str.contains(q_cf, na=False)]
                if len(partial) > 0:
                    return partial.iloc[0]
            except Exception:
                continue

    # Index fallback
    try:
        idx = df.index.astype(str)
        exact_i = df[idx.str.casefold() == q_cf]
        if len(exact_i) > 0:
            return exact_i.iloc[0]
    except Exception:
        pass

    return None


def resolve_minor_planet(
    source: str,
    dt_utc: datetime,
    traj_from: Optional[datetime],
    traj_to: Optional[datetime],
    mpc_minor_planets_file: str | None,
    cfg=None,
):
    """
    Resolve minor planet from MPCORB, return:
      (name, ra_rad, dec_rad, trajectories)
    trajectories is a list of trajectory-lists (same as comets).
    """
    if dt_utc is None:
        return None

    df = _load_mpc_minor_planets_df(mpc_minor_planets_file)
    if df is None:
        return None

    row = _find_mpc_minor_planet_row(source, df)
    if row is None:
        return None

    try:
        eph = load("de421.bsp")
        sun = eph["sun"]
        earth = eph["earth"]
        ts = skyfield_ts

        # MPCORB orbit relative to the Sun, same approach as czsky.
        body = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
    except Exception as e:
        print(_(f"Failed to build minor planet orbit for '{source}': {e}"))
        return None

    # Position at dt_utc
    try:
        t_now = skyfield_ts.from_datetime(dt_utc)
        ra_ang, dec_ang, _ = earth.at(t_now).observe(body).radec()
        ra_rad = float(ra_ang.radians)
        dec_rad = float(dec_ang.radians)
    except Exception as e:
        print(_(f"Failed to compute minor planet RA/Dec for '{source}': {e}"))
        return None

    # Trajectory
    traj = None
    if traj_from is not None and traj_to is not None:
        try:
            traj = build_trajectory(
                dt_from=traj_from,
                dt_to=traj_to,
                ts=skyfield_ts,
                earth=earth,
                body=body,
                is_comet=False,
                sun=None,
            )
        except Exception as e:
            print(_(f"Failed to compute minor planet trajectory for '{source}': {e}"))
            traj = None

    # Name: try to pick something user-friendly if available
    mp_name = source
    try:
        for k in ("name", "designation"):
            if hasattr(row, "index") and k in row.index:
                v = str(row[k]).strip()
                if v and v.lower() != "nan":
                    mp_name = v
                    break
    except Exception:
        pass

    trajectories = [traj] if traj is not None else None
    return mp_name, ra_rad, dec_rad, trajectories
