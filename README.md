# Fchart3

Fchart3 is a project designed to create high quality astronomical charts. It is written in Python using data from Stellarium, Kstars and HnSky, including 300 million stars. It can be used to create both offline charts with output to PDF or online interactive charts as can be seen in the case of project **CzSky**.

![star chart](https://github.com/skybber/fchart3/blob/assets/Orion.png)

Online interactive version is available on project **CzSky**:

* https://www.czsky.eu/chart?ra=1.532197702857378&dec=0.06961660554646551&fsz=100&splitview=true

Install:

Download this project and

`python setup.py install`

Run: `fchart3 --help` to show commandline options.

The sources of original project fcharts can be found at:
* https://www.astro.rug.nl/~brentjen/fchart.html

However it relies on numarray which has been deprecated in favor of numpy.

Previous fchart sources for python2.7 can be found at:
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
- `stars_0_0v*.cat` - UsnoNomad catalogs from [stellarium](https://github.com/Stellarium)
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
