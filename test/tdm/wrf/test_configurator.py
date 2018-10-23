import unittest
import yaml
from tdm.wrf import configurator, configuration_checker


def flatten_flat(assigned):
    f = []
    for k, v in assigned.items():
        if isinstance(v, dict):
            for k1, v1 in flatten_flat(v):
                f.append((k + '.' + k1, v1))
        else:
            f.append((k, v))
    return f


def flatten_global(assigned):
    return flatten_flat(assigned['global'])


def flatten_domains(assigned):
    domains = assigned['domains']
    f = []
    for dn in domains:
        f = f + [('@{}.{}'.format(dn, k), v)
                 for k, v in flatten_flat(domains[dn])]
    return f


class test_configurator(unittest.TestCase):

    def setUp(self):
        with open('minimal.yaml') as f:
            assigned = yaml.load(f.read())
        self.assigned = assigned
        self.c = configurator.make(assigned)

    def check_minimal(self):
        c = self.c
        assigned = self.assigned
        for i, d in enumerate(c.domains_sequence):
            self.assertEqual(i + 1, c.domains[d].id)
        for k, v in flatten_global(assigned):
            self.assertEqual(c[k], v)
        for kd, v in flatten_domains(assigned):
            dn, k = kd[1:].split('.', 1)
            if k.find('parent') == -1:
                self.assertEqual(c.domains[dn][k], v)
        test_vals = {'geogrid.io_form': 2,
                     'running.input.restart': False,
                     'physics.ishallow': 0}
        for k, v in test_vals.items():
            self.assertEqual(v, c[k])

    def check_update(self):
        c = self.c
        updates = [('@base.geometry.e_we', 131),
                   ('@dom1.geometry.e_we', 202),
                   ('@dom2.timespan.start.year', 2019),
                   ('@dom2.timespan.start.month', 6),
                   ('geometry.truelat1', 43),
                   ('physics.num_soil_layers', 4),
                   ('physics.num_land_cat', 22),
                   ('foobar.foo.bar', 'this is a string')]
        c.update(dict(updates))
        for kd, v in updates:
            if kd.startswith('@'):
                dn, k = kd[1:].split('.', 1)
                if k != 'parent':
                    self.assertEqual(c.domains[dn][k], v)
            else:
                self.assertEqual(c[kd], v)

    def check_time_step(self):
        c = self.c
        v = 44.1902
        iv, iv_f_n, iv_f_d = 44, 951, 5000
        c.update({'global.running.time_step': v})
        self.assertEqual(c['global.running.time_step_seconds'], iv)
        self.assertEqual(c['global.running.time_step_fract_num'], iv_f_n)
        self.assertEqual(c['global.running.time_step_fract_den'], iv_f_d)
        v = 44
        iv, iv_f_n, iv_f_d = 44, 0, 1
        c.update({'global.running.time_step': v})
        self.assertEqual(c['global.running.time_step_seconds'], iv)
        self.assertEqual(c['global.running.time_step_fract_num'], iv_f_n)
        self.assertEqual(c['global.running.time_step_fract_den'], iv_f_d)

    def check_checker(self):
        c = self.c
        cc = configuration_checker(c)
        self.assertTrue(cc.check())
        updates = [('@dom2.geometry.e_we', 19),
                   ('@dom2.geometry.parent_grid_ratio', 7)]
        c.update(dict(updates))
        cc = configuration_checker(c)
        self.assertFalse(cc.check())

    def check_generation(self):
        c = self.c
        c.generate_share()
        c.generate_geogrid()
        c.generate_ungrib()
        c.generate_metgrid()
        c.generate_time_control()
        c.generate_domains()
        c.generate_physics()
        c.generate_fdda()
        c.generate_dynamics()
        c.generate_bdy_control()
        c.generate_grib2()
        c.generate_namelist_quilt()

    def check_domains(self):
        c = self.c
        for dn, dv in c.domains.items():
            self.assertEqual(dn, dv.name)
        self.assertAlmostEqual(c.domains['base'].get_offset_wrt_base(),
                               (0.0, 0.0))
        self.assertAlmostEqual(c.domains['base'].get_extension(),
                               (1200000, 2400000))
        self.assertAlmostEqual(c.domains['dom1'].get_offset_wrt_base(),
                               (288000.0, 600000.0))
        self.assertAlmostEqual(c.domains['dom1'].get_extension(),
                               (360000.0, 720000.0))


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(test_configurator('check_minimal'))
    suite_.addTest(test_configurator('check_update'))
    suite_.addTest(test_configurator('check_time_step'))
    suite_.addTest(test_configurator('check_generation'))
    suite_.addTest(test_configurator('check_domains'))
    suite_.addTest(test_configurator('check_checker'))
    return suite_


if __name__ == '__main__':
    _RUNNER = unittest.TextTestRunner(verbosity=2)
    _RUNNER.run((suite()))
