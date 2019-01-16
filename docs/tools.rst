Grib2 files collection to a single CF file
==========================================

example usage of grib2cf::

   docker run --mount type=bind,src=${PWD},dst=/mnt/data \
              --rm -it crs4/tdm-tools \
              tdm grib2cf moloch 2018050103 -d /mnt/data/data -O /mnt/data
