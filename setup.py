from distutils.core import setup

setup(
    name='tdm',
    version='0.0',
    description='tdm modules and tools',
    author='ALfred E. Neumann',
    author_email='aen@gmail.com',
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
