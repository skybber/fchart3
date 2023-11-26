# Fchart3

Fchart3 is a Python project designed to create high-quality astronomical charts using data from Stellarium, Kstars, and HnSky, including 300 million stars. It can generate both offline charts with output to PDF and online interactive charts, as demonstrated in the **CzSky** project.

![fchar3](https://github.com/skybber/fchart3/assets/2523097/7748f1fd-4751-4586-ac4c-7c2900d66568)


Online interactive version available on project **CzSky**:
- [CzSky Chart](https://www.czsky.eu/chart?ra=1.532197702857378&dec=0.06961660554646551&fsz=100&splitview=true)

## Install

Download this project and run: 

`python setup.py install`

### Run
To see command-line options, use:
`fchart3 --help`

Generate findchart for Crab Nebula:
`fchart3 M1`

Generate complex chart of M39 (m39.pdf) region:
`fchart3 -width 190 -height 270 -fieldsize 40 -limstar 9 -limdso 9 --show-nebula-outlines --show-enhanced-milky-way --font-style-bayer bold --font-style-dso italic --flamsteed-numbers-only --show-equatorial-grid --hide-map-orientation-legend --hide-map-scale-legend m39`

Generate complex chart for M39 (m39.tikz) region with output to TIKZ format.
`fchart3 -f m39.tikz -width 190 -height 270 -fieldsize 40 -limstar 9 -limdso 9 --show-nebula-outlines --show-enhanced-milky-way --font-style-bayer bold --font-style-dso italic --flamsteed-numbers-only --show-equatorial-grid --hide-map-orientation-legend --hide-map-scale-legend m39`

### Previous Projects
The sources of the original project fcharts can be found at:
* https://www.astro.rug.nl/~brentjen/fchart.html

Previous fchart sources for python2.7 can be found at:
* https://github.com/Fingel/fchart

### Data files

This repository also contains the following catalogs in the data/catalogs directory:

- `bsc5.dat` catalogue of [bright stars](http://tdc-www.harvard.edu/catalogs/bsc5.html)
- `constbnd.dat` [Catalogue of Constellation Boundary Data](http://cdsarc.u-strasbg.fr/viz-bin/Cat?VI/49#sRM2.2)
- `constellationship_western.fab` - western constellation lines from Stellarium
- `milkyway.dat` - outlined Milky Way
- `milkyway_enhanced.dat` - shaded Milky Way
- `deep_sky.hnd` - catalog of deepsky objects from Hnsky created by Han Kleijn (https://www.hnsky.org/software.htm)
- `namedstars.dat` - catalog of named stars from [kstars](https://edu.kde.org/kstars/)
- `outlines_catgen.dat` - nebulae outlines from [OpenNGC](https://github.com/mattiaverga/OpenNGC)
- `PGC.dat` - catalogue of PGC galaxies
- `PGC_updates.dat` - actualizations of PGC catalogue
- `starnames.dat` - star names from [kstars](https://edu.kde.org/kstars/)
- `stars_0_0v*.cat` - UsnoNomad catalogs from [stellarium](https://github.com/Stellarium)
- `unamedstars.dat` - catalog of unamed stars from [kstars](https://edu.kde.org/kstars/)

### Authors
* Michiel Brentjens - original author
* Austin Riba - modern fchart for python 2.7, numpy. https://github.com/Fingel/fchart
* Vladimir Dvorak - fchart3: python3 + pycairo support. Rectangular view, constellations shapes, borderlines. Support for stars up to 16mag using HTM (hierarchical triangular mesh) and USNO NOMAD catalog.
