#!/usr/bin/python

#    fchart draws beautiful deepsky charts in vector formats
#    fchart3 CLI enhancements: horizontal coordinate input parsing
#    Copyright (C) 2005-2025 fchart authors
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

"""
Generate a multi-page full-sky atlas by calling fchart3 repeatedly.
- Default tiling is equatorial (RA/Dec) like TriAtlas.
- Produces one PDF (or SVG/PNG) per tile; optionally merges them into one PDF.

Notes:
- fchart3 CLI accepts "RA,Dec,Caption" as a source position (RA in hours, Dec in degrees).
- We call fchart3 once per tile to keep filenames unique and predictable.
"""

import argparse
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass(frozen=True)
class Tile:
    ra_hours: float   # 0..24
    dec_deg: float    # -90..+90
    name: str         # caption + filename stem


def wrap_ra_hours(h: float) -> float:
    """Wrap RA hours into [0, 24)."""
    h = h % 24.0
    if h < 0:
        h += 24.0
    return h


def h2hms(h: float) -> str:
    """Format RA hours as sexagesimal 'HH:MM:SS.s' string for fchart3."""
    h = wrap_ra_hours(h)
    hh = int(h)
    mm_f = (h - hh) * 60.0
    mm = int(mm_f)
    ss = (mm_f - mm) * 60.0
    return f"{hh:02d}:{mm:02d}:{ss:04.1f}"


def d2dms(d: float) -> str:
    """Format degrees as sexagesimal '±DD:MM:SS.s'."""
    sign = "+" if d >= 0 else "-"
    d = abs(d)
    dd = int(d)
    mm_f = (d - dd) * 60.0
    mm = int(mm_f)
    ss = (mm_f - mm) * 60.0
    return f"{sign}{dd:02d}:{mm:02d}:{ss:04.1f}"


def build_equatorial_tiles(field_deg: float, overlap: float) -> List[Tile]:
    """
    Build a full-sky tiling using declination bands.

    Fix: ensure we always include the last band at dec_max (otherwise the pole cap
    can be missed when step_dec does not land exactly on dec_max).
    """
    if not (0.0 <= overlap < 1.0):
        raise ValueError("overlap must be in [0, 1).")

    step_dec = field_deg * (1.0 - overlap)
    if step_dec <= 0:
        raise ValueError("field_deg*(1-overlap) must be > 0.")

    r_rad = math.radians(field_deg / 2.0)

    dec_min = -90.0 + field_deg / 2.0
    dec_max = +90.0 - field_deg / 2.0

    # --- Build declination band centers robustly ---
    decs: List[float] = []
    dec = dec_min
    while dec <= dec_max + 1e-9:
        decs.append(dec)
        dec += step_dec

    # Ensure the last band hits dec_max (important for full coverage).
    if not decs:
        decs = [0.0]
    if abs(decs[-1] - dec_max) > 1e-6:
        # If we overshot, replace; if we undershot, append.
        if decs[-1] > dec_max:
            decs[-1] = dec_max
        else:
            decs.append(dec_max)

    tiles: List[Tile] = []
    band_idx = 0

    for dec in decs:
        dec_rad = math.radians(dec)
        sin_dec = math.sin(dec_rad)
        cos_dec = math.cos(dec_rad)

        if abs(cos_dec) < 1e-6:
            n_ra = 1
        else:
            cos_r = math.cos(r_rad)
            denom = (cos_dec * cos_dec)
            arg = (cos_r - (sin_dec * sin_dec)) / denom
            arg = max(-1.0, min(1.0, arg))

            delta_alpha_rad = math.acos(arg)
            width_ra_deg = 2.0 * math.degrees(delta_alpha_rad)

            step_ra_deg = width_ra_deg * (1.0 - overlap)
            step_ra_h = step_ra_deg / 15.0

            n_ra = max(1, int(math.ceil(24.0 / step_ra_h)))

        step_ra_h = 24.0 / n_ra

        for i in range(n_ra):
            ra = i * step_ra_h
            name = (
                f"tile_{band_idx:02d}_{i:03d}_"
                f"RA{h2hms(ra).replace(':','')}_"
                f"DEC{d2dms(dec).replace(':','')}"
            )
            tiles.append(Tile(ra_hours=ra, dec_deg=dec, name=name))

        band_idx += 1

    return tiles


def run_fchart3_for_tile(
        fchart3_bin: str,
        out_dir: Path,
        tile: Tile,
        *,
        config_file: str | None,
        width_mm: float,
        height_mm: float,
        field_deg: float,
        projection: str,
        language: str,
        limit_star: float | None,
        limit_dso: float | None,
        extra_args: List[str],
        output_ext: str,
) -> None:
    """
    Call fchart3 once for a single tile.
    We do NOT pass -f/--output-file because that would override all outputs.
    Instead we use the caption as filename stem (your CLI does that for position sources).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build the position source string (RA hours, Dec degrees, Caption).
    source = f"{h2hms(tile.ra_hours)},{d2dms(tile.dec_deg)},{tile.name}"

    cmd = [
        fchart3_bin,
        "-o", str(out_dir),
        "-W", str(width_mm),
        "-H", str(height_mm),
        "-fov", str(field_deg),
        "--projection", projection,
        "-l", language,
        # Typical atlas defaults (optional; comment out if you want):
        # "--show-coords-legend",
        # "--show-map-orientation-legend",
        # "--show-equatorial-grid",
        # "--hide-star-labels",
    ]

    if config_file:
        cmd += ["-c", config_file]
    if limit_star is not None:
        cmd += ["-ls", str(limit_star)]
    if limit_dso is not None:
        cmd += ["-ld", str(limit_dso)]

    # You can pass extra raw CLI args (e.g. ["--show-equatorial-grid"]).
    cmd += extra_args

    # Enforce desired format by letting fchart3 append .pdf by default.
    # If you want svg/png, you can pass "--output-file" per call, but we rely on stem naming.
    # So we post-rename if needed OR simply keep PDF and convert externally.
    #
    # Your CLI chooses format by filename extension; for position sources it does `filename += '.pdf'`.
    # Therefore: easiest is to generate PDF always, and optionally convert later.
    if output_ext.lower() not in ("pdf",):
        # Keep it simple: generate PDF, then external convert step (not implemented here).
        pass

    cmd.append(source)

    subprocess.run(cmd, check=True)


def merge_pdfs(out_dir: Path, merged_name: str) -> None:
    """
    Merge PDF pages into one file using a best-effort external tool:
    - pdfunite (poppler-utils) OR
    - qpdf
    - gs (Ghostscript)

    If none exists, we just leave separate PDFs.
    """
    pdfs = sorted(out_dir.glob("*.pdf"))
    if not pdfs:
        return

    target = out_dir / merged_name

    # Try pdfunite
    pdfunite = shutil.which("pdfunite")
    if pdfunite:
        subprocess.run([pdfunite, *map(str, pdfs), str(target)], check=True)
        return

    # Try qpdf
    qpdf = shutil.which("qpdf")
    if qpdf:
        subprocess.run([qpdf, "--empty", "--pages", *map(str, pdfs), "--", str(target)], check=True)
        return

    # Try Ghostscript
    gs = shutil.which("gs")
    if gs:
        subprocess.run(
            [
                gs, "-dBATCH", "-dNOPAUSE", "-q",
                "-sDEVICE=pdfwrite",
                f"-sOutputFile={target}",
                *map(str, pdfs),
            ],
            check=True,
        )
        return

    print("No PDF merge tool found (pdfunite/qpdf/gs). Leaving individual PDFs.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a multi-page full-sky atlas via fchart3.")
    ap.add_argument("--fchart3", default="fchart3", help="Path to fchart3 executable.")
    ap.add_argument("--out", default="./atlas_out", help="Output directory.")
    ap.add_argument("--config", default=None, help="fchart3 config file name or path (passed to -c).")

    ap.add_argument("--width-mm", type=float, default=180.0, help="Page width in mm.")
    ap.add_argument("--height-mm", type=float, default=270.0, help="Page height in mm.")
    ap.add_argument("--field-deg", type=float, default=45.0, help="Field of view diameter in degrees.")
    ap.add_argument("--overlap", type=float, default=0.20, help="Tile overlap fraction (0..1).")

    ap.add_argument("--projection", default="stereographic", choices=["stereographic", "orthographic", "equidistant"])
    ap.add_argument("--language", default="en", help="Map language (passed to -l).")

    ap.add_argument("--limit-star", type=float, default=9, help="Limiting magnitude for stars (-ls).")
    ap.add_argument("--limit-dso", type=float, default=9, help="Limiting magnitude for DSO (-ld).")

    ap.add_argument("--merge", action="store_true", help="Merge produced PDFs into one atlas.pdf (requires pdfunite/qpdf/gs).")
    ap.add_argument("--merged-name", default="atlas.pdf", help="Merged PDF filename.")
    ap.add_argument("--extra-arg", action="append", default=[], help="Extra fchart3 CLI arg (repeatable). Example: --extra-arg --show-equatorial-grid")
    ap.add_argument(
        "--show-enhanced-milky-way",
        dest="show_enhanced_milky_way",
        action="store_true",
        default=False,
        help="Enable enhanced Milky Way shading on each generated page (passes --show-enhanced-milky-way to fchart3)."
    )
    args = ap.parse_args()

    out_dir = Path(args.out).expanduser().resolve()

    # Build tiles
    tiles = build_equatorial_tiles(args.field_deg, args.overlap)
    print(f"Tiles: {len(tiles)}")
    # Build fchart3 args that should be applied to every page.
    extra_args = list(args.extra_arg) if args.extra_arg else []

    if args.show_enhanced_milky_way:
        extra_args.append("--show-enhanced-milky-way")

    # Generate pages
    for idx, t in enumerate(tiles, start=1):
        print(f"[{idx}/{len(tiles)}] {t.name}  RA={h2hms(t.ra_hours)}  Dec={d2dms(t.dec_deg)}")
        run_fchart3_for_tile(
            args.fchart3,
            out_dir,
            t,
            config_file=args.config,
            width_mm=args.width_mm,
            height_mm=args.height_mm,
            field_deg=args.field_deg,
            projection=args.projection,
            language=args.language,
            limit_star=args.limit_star,
            limit_dso=args.limit_dso,
            extra_args=extra_args,
            output_ext="pdf",
        )

    # Optional merge
    if args.merge:
        merge_pdfs(out_dir, args.merged_name)
        print(f"Merged: {out_dir / args.merged_name}")


if __name__ == "__main__":
    main()
