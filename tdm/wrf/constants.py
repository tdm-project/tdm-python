OPS_TABLE = {
    'wrf_core' : 'ARW', # hardwired lambda _: _.get('physics.wrf_core')
    'max_dom' : lambda _: len(_.domains),
    'start_date' : lambda _: [x.start_date for x in _.domains],
    'end_date' : lambda _: [x.start_date for x in _.domains],
}

DEFAULTS = {
    'dynamics': {
        'wrf_core' : 'ARW'
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
            'level' : 0,
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
        'maxens2':3,
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
