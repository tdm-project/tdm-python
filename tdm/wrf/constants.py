SHARE_DEFAULT_FIELDS = [
    'dynamics.wrf_core', 'domains.max_dom',
    'domains.timespan.start_date',
    'domains.timespan.end_date',
    'running.input.interval_seconds',
    'geogrid.io_form_geogrid'
]

GEOGRID_DEFAULT_FIELDS = [
    'domains.parent_id',
    'domains.geometry.parent_grid_ratio',
    'domains.geometry.i_parent_start',
    'domains.geometry.j_parent_start',
    'domains.geometry.e_we',
    'domains.geometry.e_sn',
    '@base.geometry.dx',
    '@base.geometry.dy',
    'geometry.geog_data_path',
    'geometry.opt_geogrid_tbl_path',
]

GEOMETRY_PROJECTION_FIELDS = {
    'lambert' : [
        'geometry.ref_lat',
        'geometry.ref_lon',
        'geometry.geog_data_res',
        'geometry.truelat1',
        'geometry.truelat2',
        'geometry.stand_lon'
    ]
}


UNGRIB_DEFAULT_FIELDS = [
    'ungrib.out_format',
    'ungrib.prefix',
]

METGRID_DEFAULT_FIELDS = [
    'metgrid.fg_name',
    'metgrid.io_form_metgrid',
    'metgrid.opt_metgrid_tbl_path',
]

DEFAULTS = {
    'global': {
        'geometry': {
            'map_proj': 'lambert',
            'geog_data_res': 'default',
            'opt_geogrid_tbl_path': '/wrf/WPS/geogrid'
        },
        'dynamics': {
            'wrf_core': 'ARW'
        },
        'running': {
            'debug': {
                'level': 0,
            },
            'input': {
                'restart': False,
            },
            'history': {
                'conf': {
                    'outname': "/WPSRUN/wrfout_d<domain>_<date>.nc",
                },
            },
        },
        'geogrid': {
            'io_form_geogrid': 2,
            'opt_output_from_geogrid_path': '.',
        },
        'ungrib': {
            'out_format': 'WPS',
            'prefix': 'FILE',
        },
        'metgrid': {
            'fg_name': 'FILE',
            'io_form_metgrid': 2,
            'opt_metgrid_tbl_path': '/wrf/WPS/metgrid',
        },
        'physics': { # all default values
            'swint_opt': 0,
            'convtrans_avglen_m': 20, # unclear if used
            'ishallow': 0,
            'surface_input_source': 3,
            'num_soil_layers': 5,
            'num_land_cat': 21,
            'maxiens': 1,
            'maxens': 3,
            'maxens2': 3,
            'maxens3': 16,
            'ensdim': 144,
            'mp_zero_out': 0,
            'usemonalb': False,
            'mosaic_lu': 0,
            'mosaic_soil': 0,
        },
    },
    'domains': {
        'base': { 
            'mp_physics': 0,  
            'ra_lw_physics': 0,
            'ra_sw_physics': 0,
            'sf_sfclay_physics': 0,
            'sf_surface_physics': 0,
            'bl_pbl_physics': 0,
            'bldt': 0,
            'cu_physics': 0,
            'cu_diag': 0,
            'cudt': 0,
            'cu_rad_feedback': False,
        }
    },
}
