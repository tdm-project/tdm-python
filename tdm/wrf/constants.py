SHARE_DEFAULT_FIELDS = [
    'dynamics.wrf_core', 'domains.max_dom',
    'domains.timespans.start_date',
    'domains.timespans.end_date',
    'running.input.interval_seconds',
    'conversions.geogrid.io_form_geogrid'
]

GEOGRID_DEFAULT_FIELDS = [
    'domains.geometry.parent_id',
    'domains.geometry.parent_grid_ratio',
    'domains.geometry.i_parent_start',
    'domains.geometry.j_parent_start',
    'domains.geometry.e_we',
    'domains.geometry.e_sn',
    'domains.geometry.dx',
    'domains.geometry.dy',    
]

GEOMETRY_PROJECTION_FIELDS = {
    'lambert' : [
        'geometry.global.ref_lat',
        'geometry.global.ref_lon',
        'geometry.global.geog_data_res',
        'geometry.global.truelat1',
        'geometry.global.truelat2',
        'geometry.global.stand_lon',
    ]
}


UNGRIB_DEFAULT_FIELDS = [
    'conversions.ungrib.out_format',
    'conversions.ungrib.prefix',
]

METGRID_DEFAULT_FIELDS = [
    'conversions.metgrid.fg_name',
    'conversions.metgrid.io_form_metgrid',
    'conversions.metgrid.opt_metgrid_tbl_path',
]

DEFAULTS = {
    'global': {
        'geometry': {
            'map_proj': 'lambert',
            'geog_data_res': 'default',
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
