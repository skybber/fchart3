# Fchart3

Fchart3 is a Python project for creating high-quality astronomical finder charts and maps.  
It uses data from Stellarium, KStars, HNSky and Gaia-based deep star catalogues (≈300 million stars up to ~16–17 mag).

It can generate:

- **Offline charts** with output to PDF or TikZ.
- **Online interactive charts** – the same engine is used in the [**CzSky**](https://www.czsky.eu) project.

![fchar3](https://github.com/skybber/fchart3/assets/2523097/7748f1fd-4751-4586-ac4c-7c2900d66568)


Online interactive version (CzSky)
----------------------------------

Interactive web charts using the fchart3 engine are available in the [**CzSky**](https://www.czsky.eu) project:

- [CzSky Chart](https://www.czsky.eu/chart?ra=1.532197702857378&dec=0.06961660554646551&fsz=100&splitview=true)


## Features

- Deep-sky finder charts based on Gaia-derived star catalogues (hundreds of millions of stars).
- Deepsky catalogue with hundreds of thousands objects (from HnSky)
- Rendering of planets (including the Sun and Moon) and planetary moons, with:
  - Realistic planetary radii and phases.
  - Saturn’s rings with current orientation.
  - Optional moon magnitudes and optimised label placement.
- Horizontal (alt-az) and equatorial coordinate support, including:
  - Horizon and horizontal grid.
  - Optional equatorial grid in horizontal view.
  - Cardinal direction markers (N, E, S, W).
- Enhanced Milky Way rendering (outlined and shaded, including high-resolution variants).
- Flexible configuration of magnitude limits, fonts, labels and map legends.
- Output to **PDF** and **TikZ** for high-quality printing and LaTeX integration.
- Used as the map engine of the CzSky online star atlas.


## Install

The recommended way is to install from the Git repository into a virtual environment:

```bash
git clone https://github.com/skybber/fchart3.git
cd fchart3

# (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# install fchart3
pip install .
````

> On some systems you may need development packages for Cairo and other libraries (e.g. `libcairo` and `libicu` on Linux) before installing.

## Run

To see command-line options:

```bash
fchart3 --help
```

Generate a simple finder chart for the Crab Nebula:

```bash
fchart3 M1
```

Generate a complex chart of the M39 region (`m39.pdf`):

```bash
fchart3 -width 190 -height 270 -fieldsize 40 -limstar 9 -limdso 9 \
  --show-nebula-outlines --show-enhanced-milky-way \
  --font-style-bayer bold --font-style-dso italic \
  --flamsteed-numbers-only --show-equatorial-grid \
  --hide-map-orientation-legend --hide-map-scale-legend \
  m39
```

Generate a complex chart for the M39 region with output to **TikZ** (`m39.tikz`):

```bash
fchart3 -f m39.tikz -width 190 -height 270 -fieldsize 40 -limstar 9 -limdso 9 \
  --show-nebula-outlines --show-enhanced-milky-way \
  --font-style-bayer bold --font-style-dso italic \
  --flamsteed-numbers-only --show-equatorial-grid \
  --hide-map-orientation-legend --hide-map-scale-legend \
  m39
```

## Data files

This repository also contains the following catalogues in the `data/catalogs` directory:

* `bsc5.dat` – catalogue of [bright stars](http://tdc-www.harvard.edu/catalogs/bsc5.html)
* `constbnd.dat` – [Catalogue of Constellation Boundary Data](http://cdsarc.u-strasbg.fr/viz-bin/Cat?VI/49#sRM2.2)
* `constellationship_western.fab` – western constellation lines from Stellarium
* `milkyway.dat` – outlined Milky Way
* `milkyway_enhanced.dat` – shaded / enhanced Milky Way
* `deep_sky.hnd` – catalogue of deep-sky objects from HNSky, created by Han Kleijn ([https://www.hnsky.org/software.htm](https://www.hnsky.org/software.htm))
* `namedstars.dat` – catalogue of named stars from [KStars](https://edu.kde.org/kstars/)
* `outlines_catgen.dat` – nebula outlines from [OpenNGC](https://github.com/mattiaverga/OpenNGC)
* `PGC.dat` – catalogue of PGC galaxies
* `PGC_updates.dat` – updates to the PGC catalogue
* `starnames.dat` – star names from [KStars](https://edu.kde.org/kstars/)
* `stars_0_0v*.cat` – Gaia-based deep star catalogues from [Stellarium](https://github.com/Stellarium)
* `unamedstars.dat` – catalogue of unnamed stars from [KStars](https://edu.kde.org/kstars/)

## Authors

* **Vladimir Dvorak** – fchart3
* **Michiel Brentjens** – original author of fchart.
* **Austin Riba** – modern fchart for Python 2.7 + NumPy: [https://github.com/Fingel/fchart](https://github.com/Fingel/fchart)
