Fchart3 changelog
=================

0.12.0 (2025-01-25)
-------------------

Added
~~~~~
- New **fchart3-atlas** tool for generating multi-page sky atlases (including install/script changes).
- Support for additional map projections configurable via config and CLI (including fisheye/equidistant-style projections).
- Improvements to the all-sky workflow and new options related to horizon clipping (e.g. ``clip_to_horizon``).
- Expanded Solar System object support plus helper search utilities (stars/SS/moons) and trajectory computations.
- Comet support (MPC comet import + trajectory computation).
- Minor planet support (MPCORB file handling, trajectory computation, new CLI options).
- Stellarium **skyculture JSON** support in CLI/config, including constellation parsing.
- Optional “enhanced” Milky Way rendering (shading) and updated defaults for nebula rendering.

Changed
~~~~~~~
- CLI: legends are hidden by default.
- Major configuration refactor (simplification/unification, ``cfg`` structure, dataclasses, typed/enumerated options).
- Codebase refactoring and module/package moves (e.g. astronomy computations consolidated under ``astro``, ``solar_system`` moved under ``cli``).
- Configuration/layout tweaks for constellation-line spacing and various rendering/layout adjustments (e.g. magnitude scale widget, cardinal directions).
- Trajectory engine refactor to support **multiple trajectories** (not just a single one) and updated step computation logic.

Fixed
~~~~~
- Fixed equatorial grid rendering in horizontal-coordinate mode.
- Minor fixes/cleanup in method signatures and helpers (e.g. ``unknown_object``).
- Fixes related to Stellarium landscapes (azimuth handling, polygon horizon quirks, related edge cases).

Breaking changes / migration notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- CLI argument parsing changed in a few places (e.g. width/height flag adjustments and added short options); verify your command lines.
- Config/API refactors (``settings`` -> ``cfg``, dataclasses, enums) and module moves may require import/config updates in downstream integrations.


Changes v0.11.1 (2025-11-08)
----------------------------------


New features
~~~~~~~~~~~~

- Added support for rendering planets (including the Sun and Moon) and their moons in finder charts, with basic planetary disks integrated into the existing sky rendering.
- Planets and their moons can now be selected as chart objects; the Sun and Moon are intentionally non-selectable to avoid accidental selection.
- Added numeric field-of-view (FoV) overlay.
- Added configurable highlights, including magnitude limits.
- Added user object lists, allowing custom target sets to be used directly in chart generation.


Planets and moons
~~~~~~~~~~~~~~~~~

- Use real planetary radii for drawing relative sizes.
- Implemented planetary phase rendering, including fixes for mirrored phases and phase-angle sign errors.
- Implemented a prototype of Saturn’s rings with improved orientation and rotation.
- Added a catalog of planetary moons, including magnitude evaluation and optional display of moon magnitudes.
- Improved positioning of moon labels (increased offset from symbol and optimised label placement).


Coordinate systems and horizon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduced basic horizontal coordinates for charts, using the equatorial field centre for consistent projections.
- Added drawing of horizon and horizontal grid, including fixes to horizon rendering.
- Added optional equatorial grid in horizontal coordinates.
- Added cardinal direction markers (N, E, S, W) for better orientation.


Star catalog (Gaia)
~~~~~~~~~~~~~~~~~~~

- Migrated the deep star catalog from NOMAD to Gaia.
- Introduced matrix-based coordinate transformations for robust handling of Gaia data.
- Fixed HIP identifiers and ensured HIP fields are consistently initialised.


Milky Way and deep sky
~~~~~~~~~~~~~~~~~~~~~~

- Added 10k and 30k “enhanced” Milky Way map variants for more detailed rendering at high zoom levels.
- Optimised Milky Way rendering, including the enhanced variant and supporting data structures.
- Reduced memory usage for deep-sky object (DSO) catalogs.


Performance, memory and compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Optimised geodesic grid initialisation, including numpy-based conversions and improved memory handling.
- Added support for numpy 2.0 and updated array handling where necessary.
- Various numerical fixes in phase/position-angle and related calculations.


UI, widgets and rendering backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added configurable Moon scale in widgets.
- Improved robustness of map scale widgets (safer handling of missing coordinates).
- Skia drawing backend:
  - Initial integration of Skia-based rendering.
  - Typeface caching in SkiaDrawing to reduce overhead and improve performance.


Internal changes
~~~~~~~~~~~~~~~~

- Broader modularisation of the codebase, splitting large modules and cleaning up imports.
- General code cleanup: removal of dead code, parameter reorganisation, and minor maintenance updates.
