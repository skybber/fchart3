# fchart3
Michiel Brentjens' fchart - astronomical finder charts now working with numpy and python3.x

![star chart](https://github.com/skybber/fchart3/blob/assets/M103.svg)

fchart3 is a set of python3 scripts and a command line utility to create star maps/finder charts.

Install:

Download this project and

`python setup.py install`

Run: `fchart3 --help` to show commandline options.

The original source of this code can be found here:
* https://www.astro.rug.nl/~brentjen/fchart.html

However it relies on numarray which has been deprecated in favor of numpy.

Previous fchart sources for python2.7 can be found here:
* https://github.com/Fingel/fchart

This repository contains updated sourcecode so that the code may run with numpy.

This repository also contains following catalogs in the data/catalogs directory:

- `bsc5.dat` catalogue of [bright stars](http://tdc-www.harvard.edu/catalogs/bsc5.html)
- `constbnd.dat` [Catalogue of Constellation Boundary Data](http://cdsarc.u-strasbg.fr/viz-bin/Cat?VI/49#sRM2.2)
- `ConstellationLines.dat` - constellation lines from [bsc](http://tdc-www.harvard.edu/catalogs/bsc5.html)
- `deep_sky.hnd` - catalog of deepsky objects from Hnsky created by Han Kleijn (https://www.hnsky.org/software.htm)
- `deepstars.dat` - tycho2 catalog from [kstars](https://edu.kde.org/kstars/)
- `namedstars.dat` - catalog of named stars from [kstars](https://edu.kde.org/kstars/)
- `starnames.dat` - star names from [kstars](https://edu.kde.org/kstars/)
- `unamedstars.dat` - catalog of unamed stars from [kstars](https://edu.kde.org/kstars/)

DSO catalogs replaced now by catalog from hnsky:
- `revic.dat` - [Revised IC Catalogue](http://www.klima-luft.de/steinicke/ngcic/rev2000/Explan.htm)
- `revngc.txt` - [Revised New General Catalogue](http://www.klima-luft.de/steinicke/ngcic/rev2000/Explan.htm)
- `sac.txt` - [Saguaro Astronomy Club Database](https://www.saguaroastro.org/sac-downloads/)

Authors
=======
* Michiel Brentjens - original author
* Austin Riba - modern fchart for python 2.7, numpy. https://github.com/Fingel/fchart
* Vladimir Dvorak - fchart3: python3 + pycairo support. Rectangular view, constellations shapes, borderlines. Support for stars up to 16mag using HTM (hierarchical triangular mesh) and USNO NOMAD catalog.
