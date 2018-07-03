SHARE_DEFAULT_FIELDS = [
    'dynamics.wrf_core', 'domains.max_dom',
    'domains.timespan.start_date',
    'domains.timespan.end_date',
    'running.input.interval_seconds',
    ('geogrid.io_form', 'io_form_geogrid'),
]

GEOGRID_DEFAULT_FIELDS = [
    'domains.parent_id',
    'domains.geometry.parent_grid_ratio',
    'domains.geometry.i_parent_start',
    'domains.geometry.j_parent_start',
    'domains.geometry.e_we',
    'domains.geometry.e_sn',
    'domains.geometry.geog_data_res',
    '@base.geometry.dx',
    '@base.geometry.dy',
    'geometry.geog_data_path',
    'geometry.opt_geogrid_tbl_path',
]

GEOMETRY_PROJECTION_FIELDS = {
    'lambert': [
        'geometry.ref_lat',
        'geometry.ref_lon',
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

FDDA_DEFAULT_FIELDS = [
]

TIME_CONTROL_DEFAULT_FIELDS = [
    'domains.timespan.start_date',
    'domains.timespan.end_date',
    'running.input.interval_seconds',
    ('domains.running.history.interval', 'history_interval'),
    ('running.history.io_form', 'io_form_history'),
    'domains.running.output.frames_per_outfile',
    'domains.running.input.input_from_file',
    'running.input.restart',
    'running.input.io_form_restart',
    'running.input.io_form_input',
    'running.input.io_form_boundary',
    ('running.debug.level', 'debug_level'),
    ('running.history.outname', 'history_outname'),
]

DOMAINS_DEFAULT_FIELDS = [
    ('running.time_step_seconds', 'time_step'),
    'running.time_step_fract_num',
    'running.time_step_fract_den',
    'domains.max_dom',
    'domains.parent_id',
    'domains.geometry.grid_id',
    'domains.geometry.e_vert',
    'domains.geometry.e_we',
    'domains.geometry.e_sn',
    'domains.geometry.i_parent_start',
    'domains.geometry.j_parent_start',
    'domains.geometry.parent_grid_ratio',
    'domains.running.parent_time_step_ratio',
    'real.num_metgrid_levels',
    'real.num_metgrid_soil_levels',
]


DEFAULTS = {
    'global': {
        'geometry': {
            'map_proj': 'lambert',
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
                'io_form_input': 2,
                'io_form_restart': 2,
                'io_form_boundary': 2,
            },
            'history': {
                'outname': "/WPSRUN/wrfout_d<domain>_<date>.nc",
                'io_form': 2,
            },
            'feedback': 0,
        },
        'geogrid': {
            'io_form': 2,
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
        'physics': {
            'swint_opt': 0,
            'convtrans_avglen_m': 20,
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
            'running': {
                'output': {
                    'frames_per_outfile': 1,
                },
                'input': {
                    'input_from_file': False,
                },
            },
            'physics': {
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
            },
        },
    },
}
