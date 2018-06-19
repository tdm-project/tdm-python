from distutils.core import setup

setup(
    name='tdm',
    version='0.0',
    description='tdm modules and tools',
    author='ALfred E. Neumann',
    author_email='aen@gmail.com',
    packages=['tdm', 'tdm.gfs'],
    scripts=['bin/gfs_fetch'],      
)
