from setuptools import setup
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(here, 'README.rst')) as f:
        long_description = f.read()
else:
    with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='etv',
    version='0.1',
    description=('Earth Time-series Visualization'),
    long_description=long_description,
    author='Ryan J. Dillon',
    author_email='ryanjamesdillon@gmail.com',
    url='https://github.com/ryanjdillon/etv',
    download_url='https://github.com/ryanjdillon/etv/archive/0.1.tar.gz',
    license='MIT',
    packages=[
        'etv',
        'etv.cli',
        'etv.etv',
        'etv.etv_configuration',
        'etv.etv_configuration.templatetags',
        'etv.utils'],
    install_requires=[
        'click',
        'Django',
        'netCDF4',
        'numpy',
        'pyproj',
        'tqdm',
        'yamlord',
        ],
    entry_points = {'console_scripts': ['etv=etv.cli.cli:main']},
    include_package_data=True,
    keywords=['visualization', 'gridded', 'simulation', 'time-series',
              'earth-science'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5'],
    zip_safe=False,
    )
