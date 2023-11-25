from setuptools import setup
from distutils.core import Extension
import platform
import sys
import time
from glob import glob

packages = ['fchart3']
ext_modules = []
try:
    import numpy
    include_dirs = [numpy.get_include()]
    have_numpy = True
except:
    have_numpy = False
    ext_modules = []
    include_dirs = []

    sys.stdout.write('Numpy not found:  Not building C extensions\n')
    time.sleep(5)

if platform.system() == 'Darwin':
    extra_compile_args = ['-arch','i386','-arch','x86_64']
    extra_link_args = ['-arch','i386','-arch','x86_64']
else:
    extra_compile_args = []
    extra_link_args = []

if have_numpy:
    include_dirs += ['fchart3/htm','fchart3/htm/htm_src','fchart3/htm/include']
    htm_sources = glob('fchart3/htm/htm_src/*.cpp')
    htm_sources += ['fchart3/htm/htmc.cc','fchart3/htm/htmc_wrap.cc']
    htm_module = Extension('fchart3.htm._htmc',
                           extra_compile_args=extra_compile_args,
                           extra_link_args=extra_link_args,
                           sources=htm_sources,
                           include_dirs=include_dirs)

    ext_modules.append(htm_module)
    packages.append('fchart3.htm')

setup(
    name='fchart3',
    version='0.10.2',
    description='Collection of Python scripts to make beautiful deepsky charts in various formats',
    keywords='fchart3 starchart star charts finder chart astronomy map',
    url='https://github.com/skybber/fchart3',
    author='Michiel Brentjens <brentjens@astron.nl>, Austin Riba <root@austinriba.com>, Vladimir Dvorak<lada.dvorak7@gmail.com',
    author_email='lada.dvorak7@gmail.com',
    packages=packages,
    include_package_data=True,
    install_requires=['numpy', 'pycairo', 'Pillow', 'skia-python'],
    scripts=['bin/fchart3'],
    package_data={'fchart3': ['data/catalogs/bsc5.dat',
                              'data/catalogs/constbndJ2000.dat',
                              'data/catalogs/constellation_boundaries.dat',
                              'data/catalogs/constellationship_western.fab',
                              'data/catalogs/convert_stellarium_boundaries.txt',
                              'data/catalogs/cross-id.dat',
                              'data/catalogs/deep_sky.hnd',
                              'data/catalogs/milkyway.dat',
                              'data/catalogs/milkyway_enhanced.dat',
                              'data/catalogs/namedstars.dat',
                              'data/catalogs/outlines_catgen.dat',
                              'data/catalogs/PGC.dat',
                              'data/catalogs/PGC_update.dat',
                              'data/catalogs/starnames.dat',
                              'data/catalogs/stars_0_0v0_8.cat',
                              'data/catalogs/stars_1_0v0_8.cat',
                              'data/catalogs/stars_2_0v0_8.cat',
                              'data/catalogs/stars_3_1v0_4.cat',
                              'data/catalogs/unnamedstars.dat',
                              'data/catalogs/vic.txt',
                              'data/default.conf',
                              ]},
    ext_modules=ext_modules,
    include_dirs=include_dirs,
)
