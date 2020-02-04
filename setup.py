from setuptools import setup
from distutils.core import Extension
import platform
from glob import glob

packages = ['fchart3']
ext_modules = []
try:
    import numpy
    include_dirs=[numpy.get_include()]
    have_numpy=True
except:
    have_numpy=False
    ext_modules=[]
    include_dirs=[]

    stdout.write('Numpy not found:  Not building C extensions\n')
    time.sleep(5)

if platform.system()=='Darwin':
    extra_compile_args=['-arch','i386','-arch','x86_64']
    extra_link_args=['-arch','i386','-arch','x86_64']
else:
    extra_compile_args=[]
    extra_link_args=[]

if have_numpy:
    include_dirs += ['fchart3/htm','fchart3/htm/htm_src','fchart3/htm/include']
    htm_sources = glob('fchart3/htm/htm_src/*.cpp')
    htm_sources += ['fchart3/htm/htmc.cc','fchart3/htm/htmc_wrap.cc']
    htm_module = Extension('fchart3.htm._htmc',
                           extra_compile_args=extra_compile_args,
                           extra_link_args=extra_link_args,
                           sources=htm_sources)

    ext_modules.append(htm_module)
    packages.append('fchart3.htm')

setup(
    name='fchart3',
    version='0.5',
    description='Collection of Python scripts to make beautiful deepsky finder charts in various formats',
    keywords='fchart3 starchart star charts finder chart astronomy map',
    url='https://github.com/skybber/fchart3',
    author='Michiel Brentjens <brentjens@astron.nl>, Austin Riba <root@austinriba.com>, Vladimir Dvorak<lada.dvorak7@gmail.com',
    author_email='root@austinriba.com, lada.dvorak7@gmail.com',
    license='GPLv2',
    packages=packages,
    include_package_data=True,
    install_requires=['numpy'],
    scripts=['bin/fchart3'],
    package_data={'fchart3': ['data/catalogs/index.dat',
                'data/catalogs/revngc.txt',
                'data/catalogs/revic.txt',
                'data/catalogs/sac.txt',
                'data/catalogs/vic.txt',
                'data/catalogs/bsc5.dat',
                'data/catalogs/ConstellationLines.dat',
                'data/catalogs/constbnd.dat',
                'data/catalogs/constbnd.txt',
                'data/catalogs/namedstars.dat',
                'data/catalogs/starnames.dat',
                'data/catalogs/unnamedstars.dat',
                'data/catalogs/deepstars.dat',
                'data/label_positions.txt',
                ]},
    ext_modules=ext_modules,
    include_dirs=include_dirs,
)
