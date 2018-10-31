Batch Download
==============

Batch download is supported as `CKAN <https://ckan.org>`_ registered
data files in known data formats, e.g., `NetCDF4, CF 1.7 conventions
<http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html>`_.

Random Access
=============

Weather simulations::

    /tdm/odata/product/meteo/<simtype>/<simuid>/description.json
    /tdm/odata/product/meteo/<simtype>/<simuid>/<timestamp>/<georect>/<field>

Where ``field`` is a specific attribute (such as "pressure") and
``description.json`` contains an API version number.

Radar data::

    /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/description.json
    /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/<timestamp>/<georect>/<field>

Where ``field`` is, e.g., "rainfall_rate".
