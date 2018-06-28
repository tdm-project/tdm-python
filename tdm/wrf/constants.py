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
    'domains.geometry.j_parent_start', 'domains.geometry.e_we',
    'domains.geometry.e_sn', 'geometry.global.geog_data_res',
    'geometry.global.map_proj', 'geometry.global.truelat1',
    'geometry.global.truelat2', 'geometry.global.stand_lon',
    'domains.geometry.dx', 'domains.geometry.dy', 'base.geometry.ref_lat',
    'base.geometry.ref_lon'
]

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
    'dynamics': {
        'wrf_core': 'ARW'
    },
    'geometry': {
        'global': {
            'map_proj': 'lambert',
            'geog_data_res': 'default',
        },
    },
    'conversions': {
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
    },
    'running': {
        'debug': {
            'level': 0,
        },
        'input': {
            'restart': False,
            'domains': {
                'base': {
                    'from_file': True
                },
            },
        },
        'history': {
            'conf': {
                'outname': "/WPSRUN/wrfout_d<domain>_<date>.nc",
            },
            'domains': {
                'base': {
                    'frames_per_outfile': 1
                },
            },
        },
    },
    'physics': {
        'domains': {
            'base': {
                'mp_physics': 8,
                'ra_lw_physics': 4,
                'ra_sw_physics': 4,
                'radt': 20,
                'sf_sfclay_physics': 5,
                'sf_surface_physics': 3,
                'bl_pbl_physics': 5,
                'bldt': 0,
                'cu_physics': 3,
                'cu_diag': 1,
                'cudt': 0,
                'cu_rad_feedback': True,
            }
        },
        'swint_opt': 1,
        'convtrans_avglen_m': 20,
        'ishallow': 1,
        'surface_input_source': 1,
        'num_soil_layers': 9,
        'num_land_cat': 21,
        'maxiens': 1,
        'maxens': 3,
        'maxens2': 3,
        'maxens3': 16,
        'ensdim': 144,
        'mp_zero_out': 2,
        'mp_zero_out_thresh': 1.e-12,
        'usemonalb': True,
        'mosaic_lu': 1,
        'mosaic_soil': 1,
        'seaice_threshold': 271.4,
        'do_radar_ref': 1,
    },
}
