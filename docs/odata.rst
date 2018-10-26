Batch download
=============

Batch download is supported as CKAN registered datafile in known data formats
(e.g., netcdf4 (CF 1.7 conventions)).

Random Access
=============

.. code-block::
   /tdm/odata/product/meteo/<simtype>/<simuid>/description.json
   /tdm/odata/product/meteo/<simtype>/<simuid>/<timestamp>/<georect>/<field>

Description contains an API id

where `field` is the specific field, e.g., pressure 


.. code-block::
   /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/description.json
   /tdm/odata/product/radar/<radarid>/<acquid>/<processingid>/<timestamp>/<georect>/<field>


where field is, e.g.,  'rainfall_rate'.

   


