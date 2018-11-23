Events
======

At the highest level, an **event** is any time interval where something
"interesting" happened (e.g., "April 2017 thunderstorm"). Each event maps to a
CKAN dataset, containing multiple resources related to it. Datasets can be
annotated with multiple tags to help search. Currently, we consider two main
resource types: batch download and random access.

Batch Download
==============

Batch download is supported as `CKAN <https://ckan.org>`_ registered
data files in known data formats, e.g., `NetCDF4, CF 1.7 conventions
<http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html>`_.

E.g.::

    /tdm/datasets/radar/events/low_res/2018-04-30_16:00:00.nc

Random Access
=============

This allows to access individual dimensions and/or timestamps. For instance,
satisfy queries such as "pressure values in georect XYZ at
2018-04-30_16:49:01". In this case, CKAN will not index each individual item,
but rather a machine-readable (e.g., JSON) description that points to each
item in the event.

In the case of weather simulations, the CKAN resource will be::

    /tdm/odata/product/meteo/<simtype>/<simuid>/description.json

The JSON file will, in turn, reference several URLs like::

   /tdm/odata/product/meteo/<simtype>/<simuid>/<timestamp>/<georect>/<field>


Where ``field`` is a specific attribute (such as "pressure") and
``description.json`` contains an API version number.

In the case of radar data, the CKAN resource will be::

    /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/description.json

And the JSON references URLs like::

    /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/<timestamp>/<georect>/<field>

Where ``field`` is, e.g., "rainfall_rate".
