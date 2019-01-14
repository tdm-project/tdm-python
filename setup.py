from distutils.core import setup

setup(
    name='tdm',
    version='0.0',
    url='https://github.com/tdm-project/tdm-tools',
    description='TDM Tools - http://www.tdm-project.it/en/',
    author=', '.join((
        'Simone Leo',
        'Gianluigi Zanetti',
    )),
    author_email=', '.join((
        '<simone.leo@crs4.it>',
        '<gianluigi.zanetti@crs4.it>',
    )),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Intended Audience :: Science/Research',
    ],
    packages=['tdm', 'tdm.gfs', 'tdm.gfs.noaa', 'tdm.radar', 'tdm.wrf'],
    scripts=[
        'bin/tdm_gfs_fetch',
        'bin/tdm_link_grib',
        'bin/tdm_map_to_lonlat',
        'bin/tdm_map_to_tree',
        'bin/tdm_radar_events',
        'bin/tdm_radar_nc_to_geo',
        'bin/tdm_rainfall',
        'bin/tdm_wrf_configurator',
        'bin/tdm_grib2cf',
    ],
)
